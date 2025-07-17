import casadi as ca
import numpy as np
import matplotlib.pyplot as plt

class PathPlannerSolver:
    """路径规划求解器（支持障碍约束自适应、轨迹点数量自动调整）"""
    
    def __init__(self, x0, xf, obstacles, n=None, safe_distance=0.30, 
                 v_max=1.0, omega_max=1.0, r_min=0.5, a_max=2.0, epsilon=1e-2,
                 w_p=1.0, w_t=0.5, w_kin=2.0, w_r=2.0, T_min=0.05, T_max=0.3):
        """
        初始化路径规划求解器
        
        参数:
            x0: 起点坐标和姿态 [x, y, theta]
            xf: 终点坐标和姿态 [x, y, theta]
            obstacles: 障碍物坐标数组，形状为 (m, 2)，空数组表示无障碍
            n: 中间点数(None时自动计算)
            ... 其他参数同前 ...
        """
        self.x0 = np.array(x0)
        self.xf = np.array(xf)
        self.obstacles = np.array(obstacles)
        self.safe_distance = safe_distance
        self.v_max = v_max
        self.omega_max = omega_max
        self.r_min = r_min
        self.a_max = a_max
        self.epsilon = epsilon
        self.w_p = w_p
        self.w_t = w_t
        self.w_kin = w_kin
        self.w_r = w_r
        self.T_min = T_min
        self.T_max = T_max
        
        # 自动计算轨迹点数量n（若未指定）
        self.n = self._auto_calculate_n() if n is None else n
        self.n = max(5, self.n)  # 确保最少5个中间点
        
        # 求解结果
        self.trajectory = None
        self.solver_result = None
        self.cost = None
    
    def _auto_calculate_n(self):
        """根据起点终点距离、最大速度和障碍数量自动计算中间点数n"""
        # 1. 计算起点到终点的直线距离
        pos0 = self.x0[:2]
        posf = self.xf[:2]
        dist_total = np.linalg.norm(posf - pos0)
        
        # 若起点终点重合，返回最小点数
        if dist_total < 1e-6:
            return 5
        
        # 2. 估算每个时间步的最大移动距离（基于平均时间步）
        T_avg = (self.T_min + self.T_max) / 2  # 平均时间步
        max_step_dist = self.v_max * T_avg     # 每步最大移动距离
        
        # 3. 基础点数：总距离 / 每步最大距离（减1是因为总点数为n+2）
        base_n = int(dist_total / max_step_dist) - 1
        base_n = max(1, base_n)  # 至少1个中间点
        
        # 4. 根据障碍数量调整：障碍越多，需要的点数越多
        num_obstacles = len(self.obstacles)
        obstacle_factor = 1.0 + 0.5 * num_obstacles  # 每个障碍增加50%点数
        adjusted_n = int(base_n * obstacle_factor)
        
        return adjusted_n
    
    def solve(self, x0=None, xf=None, obstacles=None):
        """
        求解路径规划问题，支持同时更新起点、终点与障碍物。
        只要任意一个参数不为 None,就会触发 n 的重新计算。
        
        参数:
            x0 : 新起点 [x, y, theta],None 表示沿用旧值
            xf : 新终点 [x, y, theta],None 表示沿用旧值
            obstacles : 新障碍物数组 shape (m,2),None 表示沿用旧值
        返回:
            trajectory : 优化后的轨迹 (n+2, 3)
        """
        # 1. 按需更新起点/终点
        if x0 is not None:
            self.x0 = np.array(x0)
        if xf is not None:
            self.xf = np.array(xf)
        if obstacles is not None:
            self.obstacles = np.array(obstacles)

        # 2. 只要起点、终点、障碍物任一发生变化，就重新计算 n
        #    _auto_calculate_n 内部会读取最新的 self.x0, self.xf, self.obstacles
        if any(arg is not None for arg in (x0, xf, obstacles)):
            self.n = max(5, self._auto_calculate_n())

        # 3. 构建并求解
        res = self._build_and_solve(self.obstacles)

        # 4. 提取结果
        self.solver_result = res
        self.trajectory = self._extract_trajectory(res)
        self.cost = float(res['f'])
        return self.trajectory
    
    def _build_and_solve(self, obs_now):
        """构建优化问题并求解（支持无障碍时忽略障碍约束）"""
        # 变量定义（n+2个轨迹点，n+1个时间步）
        x = ca.SX.sym('x', self.n + 2)
        y = ca.SX.sym('y', self.n + 2)
        theta = ca.SX.sym('theta', self.n + 2)
        dt = ca.SX.sym('dt', self.n + 1)
        z = ca.vertcat(x, y, theta, dt)
        
        # 目标函数
        f = 0
        for i in range(self.n + 1):
            dx = x[i+1] - x[i]
            dy = y[i+1] - y[i]
            f += self.w_p * (dx**2 + dy**2)  # 路径平滑性
            f += self.w_t * dt[i]**2          # 时间惩罚
        
        # 约束条件
        g_eq = []    # 等式约束
        g_ineq = []  # 不等式约束
        
        # 1. 边界姿态约束（起点和终点固定）
        g_eq.extend([
            x[0] - self.x0[0],    y[0] - self.x0[1],    theta[0] - self.x0[2],
            x[-1] - self.xf[0],   y[-1] - self.xf[1],   theta[-1] - self.xf[2]
        ])
        
        # 2. 避障约束（所有轨迹点，包括起点和终点；无障碍时自动忽略）
        if len(obs_now) > 0:  # 仅当有障碍物时添加约束
            for i in range(self.n + 2):  # 遍历所有轨迹点（0到n+1）
                for (ox, oy) in obs_now:
                    # 计算轨迹点到障碍物的距离
                    dist = ca.sqrt((x[i] - ox)**2 + (y[i] - oy)** 2)
                    # 约束：距离 >= 安全距离（即安全距离 - 距离 <= 0）
                    g_ineq.append(self.safe_distance - dist)
        
        # 3. 运动学约束（速度、角速度、加速度、转弯半径）
        for i in range(self.n + 1):
            # 位移计算
            dx = x[i+1] - x[i]
            dy = y[i+1] - y[i]
            dist_step = ca.sqrt(dx**2 + dy**2)
            
            # 线速度约束：|v| <= v_max
            v = dist_step / (dt[i] + self.epsilon)
            g_ineq.extend([v - self.v_max, -v - self.v_max])
            
            # 角速度约束：|omega| <= omega_max
            dth = ca.atan2(ca.sin(theta[i+1]-theta[i]),
                          ca.cos(theta[i+1]-theta[i]))  # 角度差（[-pi, pi]）
            omega = dth / (dt[i] + self.epsilon)
            g_ineq.extend([omega - self.omega_max, -omega - self.omega_max])
            
            # 转弯半径软约束（惩罚小于最小半径的情况）
            radius = v / (ca.fabs(omega) + self.epsilon)
            f += self.w_r * ca.fmax(0, self.r_min - radius)**2
            
            # 加速度约束（除最后一个时间步）
            if i < self.n:
                dx2 = x[i+2] - x[i+1]
                dy2 = y[i+2] - y[i+1]
                dist_step2 = ca.sqrt(dx2**2 + dy2**2)
                v2 = dist_step2 / (dt[i+1] + self.epsilon)
                acc = (v2 - v) / (0.5*(dt[i] + dt[i+1]) + self.epsilon)
                g_ineq.extend([acc - self.a_max, -acc - self.a_max])
        
        # 4. 非完整约束（惩罚运动方向与姿态偏离）
        for i in range(self.n + 1):
            dx = x[i+1] - x[i]
            dy = y[i+1] - y[i]
            li = ca.vertcat(ca.cos(theta[i]), ca.sin(theta[i]))
            li1 = ca.vertcat(ca.cos(theta[i+1]), ca.sin(theta[i+1]))
            cross = (li[0] + li1[0]) * dy - (li[1] + li1[1]) * dx
            f += self.w_kin * cross**2
        
        # 约束边界设置
        g = ca.vertcat(*g_eq, *g_ineq)
        lbg = [0]*len(g_eq) + [-ca.inf]*len(g_ineq)
        ubg = [0]*len(g_eq) + [0]*len(g_ineq)
        
        # 变量上下界
        lbx = -np.inf * np.ones(z.shape[0])
        ubx = np.inf * np.ones(z.shape[0])
        
        # 固定起点和终点的位置与姿态
        fix_idx = [
            0, self.n+1,                # x的起点和终点索引
            self.n+2, 2*self.n+3,       # y的起点和终点索引
            2*self.n+4, 3*self.n+5      # theta的起点和终点索引
        ]
        lbx[fix_idx] = ubx[fix_idx] = [
            self.x0[0], self.xf[0],
            self.x0[1], self.xf[1],
            self.x0[2], self.xf[2]
        ]
        
        # 时间步上下界
        dt_start_idx = 3 * (self.n + 2)
        lbx[dt_start_idx:] = self.T_min
        ubx[dt_start_idx:] = self.T_max
        
        # 初始猜测值
        z0 = np.zeros(z.shape[0])
        z0[:self.n+2] = np.linspace(self.x0[0], self.xf[0], self.n+2)
        z0[self.n+2:2*self.n+4] = np.linspace(self.x0[1], self.xf[1], self.n+2)
        z0[2*self.n+4:3*self.n+6] = np.linspace(self.x0[2], self.xf[2], self.n+2)
        z0[3*self.n+6:] = np.ones(self.n+1) * ((self.T_min + self.T_max)/2)
        
        # 求解NLP
        nlp = {'x': z, 'f': f, 'g': g}
        opts = {'ipopt.print_level': 0, 'print_time': 1}
        solver = ca.nlpsol('solver', 'ipopt', nlp, opts)
        res = solver(x0=z0, lbg=lbg, ubg=ubg, lbx=lbx, ubx=ubx)
        return res
    
    def _extract_trajectory(self, res):
        """从求解结果中提取轨迹"""
        x = res['x'][:self.n+2].full().flatten()
        y = res['x'][self.n+2:2*self.n+4].full().flatten()
        th = res['x'][2*self.n+4:3*self.n+6].full().flatten()
        return np.column_stack((x, y, th))
    
    def get_trajectory(self):
        return self.trajectory
    
    def get_cost(self):
        return self.cost


# 可视化工具（保持与求解器分离）
class PathVisualizer:
    def __init__(self, planner_solver):
        self.planner = planner_solver
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self._init_plot_elements()
        self._setup_interactive_events()
    
    def _init_plot_elements(self):
        self.ax.set_aspect('equal')
        x_min = min(self.planner.x0[0], self.planner.xf[0]) - 0.2
        x_max = max(self.planner.x0[0], self.planner.xf[0]) + 0.2
        y_min = min(self.planner.x0[1], self.planner.xf[1]) - 0.2
        y_max = max(self.planner.x0[1], self.planner.xf[1]) + 0.2
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        
        self.pt_radius = 0.06
        self.head_scale = 0.4
        
        # 轨迹点圆圈
        self.circles = [plt.Circle((0,0), self.pt_radius, color='tab:red', alpha=0.2) 
                       for _ in range(self.planner.n + 2)]
        for c in self.circles:
            self.ax.add_patch(c)
        self.circles[0].set_color('tab:blue')
        self.circles[-1].set_color('tab:green')
        
        # 姿态箭头
        self.arrows = [self.ax.arrow(0,0,0,0, head_width=self.head_scale*self.pt_radius, 
                                    fc='k', ec='k') for _ in range(self.planner.n + 2)]
        
        # 障碍物与安全区域
        self.obs_scat = self.ax.scatter(
            self.planner.obstacles[:,0], self.planner.obstacles[:,1],
            s=300, c='k', picker=True
        )
        self.safe_circs = [plt.Circle(o, self.planner.safe_distance, color='k', alpha=0.1)
                         for o in self.planner.obstacles]
        for c in self.safe_circs:
            self.ax.add_patch(c)
        
        self.drag_idx = None
    
    def _setup_interactive_events(self):
        self.fig.canvas.mpl_connect('pick_event', self._on_pick)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self._on_release)
    
    def _on_pick(self, event):
        if event.artist == self.obs_scat:
            self.drag_idx = event.ind[0]
    
    def _on_motion(self, event):
        if self.drag_idx is None or event.xdata is None:
            return
        self.planner.obstacles[self.drag_idx] = [event.xdata, event.ydata]
        self.obs_scat.set_offsets(self.planner.obstacles)
        for c, o in zip(self.safe_circs, self.planner.obstacles):
            c.center = o
        self.fig.canvas.draw_idle()
    
    def _on_release(self, event):
        if self.drag_idx is None:
            return
        new_traj = self.planner.solve()
        print(f"障碍物更新后，新代价 = {self.planner.get_cost():.4f}")
        self.update_plot(new_traj)
        self.drag_idx = None
    
    def update_plot(self, trajectory=None):
        traj = trajectory if trajectory is not None else self.planner.get_trajectory()
        if traj is None:
            return
        for k, (xi, yi, thi) in enumerate(traj):
            self.circles[k].center = (xi, yi)
            self.arrows[k].remove()
            dx = self.pt_radius * np.cos(thi)
            dy = self.pt_radius * np.sin(thi)
            self.arrows[k] = self.ax.arrow(
                xi, yi, dx, dy, head_width=self.head_scale*self.pt_radius,
                fc='k', ec='k'
            )
        self.fig.canvas.draw_idle()
    
    def show(self):
        initial_traj = self.planner.solve()
        print(f"初始求解完成，n={self.planner.n}，代价={self.planner.get_cost():.4f}")
        self.update_plot(initial_traj)
        plt.show()


# 使用示例
if __name__ == "__main__":
    # 示例1：有障碍物（n自动计算）
    x0 = [0.0, 0.0, -np.pi]
    xf = [2.0, 2.0, np.pi/3]
    obstacles = np.array([[0.5, 0.75], [1.5, 1.25]])  # 2个障碍物
    planner = PathPlannerSolver(x0, xf, obstacles)  # 不指定n，自动计算
    visualizer = PathVisualizer(planner)
    visualizer.show()
    
    # 示例2：无障碍物（自动忽略障碍约束）
    # x0 = [0.0, 0.0, 0.0]
    # xf = [3.0, 1.0, np.pi/2]
    # obstacles = np.array([])  # 无障碍
    # planner = PathPlannerSolver(x0, xf, obstacles)
    # visualizer = PathVisualizer(planner)
    # visualizer.show()
