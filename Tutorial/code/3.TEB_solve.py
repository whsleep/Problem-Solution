import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.optimize import minimize

class DynamicTEBPlanner:
    def __init__(self, start_pose, end_pose, initial_obstacles, n_points=10, 
                 safe_distance=0.3, v_max=1.0, omega_max=np.pi/4, r_min=0.5):
        # 初始化参数
        self.start_pose = np.array(start_pose)
        self.end_pose = np.array(end_pose)
        self.obstacles = np.array(initial_obstacles)
        self.n_points = n_points
        self.safe_distance = safe_distance
        self.v_max = v_max
        self.omega_max = omega_max
        self.r_min = r_min
        
        # 初始化轨迹
        self.poses = None
        self.dt = None
        
        # 创建图形界面
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        
        # 障碍物拖动状态
        self.dragging = False
        self.dragged_index = -1
        self.original_position = None
        
        # 初始规划并显示
        self.optimize_trajectory()
        self.update_plot()
        
        plt.title('Dynamic Obstacle Trajectory Planning - Drag obstacles to update')
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        plt.grid(True)
        plt.axis('equal')
        plt.show()
    
    def _generate_initial_guess(self, poses=None):
        """生成初始猜测轨迹，可基于当前轨迹优化"""
        if poses is None or len(poses) != self.n_points + 2:
            # 初始猜测：线性插值
            x_vals = np.linspace(self.start_pose[0], self.end_pose[0], self.n_points + 2)
            y_vals = np.linspace(self.start_pose[1], self.end_pose[1], self.n_points + 2)
            theta_vals = np.linspace(self.start_pose[2], self.end_pose[2], self.n_points + 2)
            total_time = 5.0
            dt_vals = np.ones(self.n_points + 1) * (total_time / (self.n_points + 1))
        else:
            # 基于当前轨迹的扰动作为初始猜测，加速收敛
            x_vals = poses[:, 0]
            y_vals = poses[:, 1]
            theta_vals = poses[:, 2]
            dt_vals = np.ones(self.n_points + 1) * (sum(self.dt) / (self.n_points + 1)) if self.dt is not None else np.ones(self.n_points + 1) * 0.5
        
        x = np.zeros(3 * self.n_points + (self.n_points + 1))
        for i in range(self.n_points):
            x[3*i:3*i+3] = [x_vals[i+1], y_vals[i+1], theta_vals[i+1]]
        x[3*self.n_points:] = dt_vals
        
        return x
    
    def _extract_variables(self, x):
        """从解向量中提取轨迹点和时间间隔"""
        poses = np.zeros((self.n_points + 2, 3))
        poses[0] = self.start_pose
        poses[-1] = self.end_pose
        
        for i in range(self.n_points):
            poses[i+1] = x[3*i:3*i+3]
            
        dt = x[3*self.n_points:]
        return poses, dt
    
    def _compute_cost(self, x):
        """计算目标函数值"""
        poses, dt = self._extract_variables(x)
        total_cost = 0.0
        
        # 路径长度代价
        path_cost = 0.0
        for i in range(self.n_points + 1):
            dx = poses[i+1, 0] - poses[i, 0]
            dy = poses[i+1, 1] - poses[i, 1]
            path_cost += dx**2 + dy**2
        total_cost += path_cost
        
        # 时间代价
        time_cost = sum(dt**2)
        total_cost += time_cost
        
        # 安全距离代价
        safety_cost = 0.0
        for i in range(1, self.n_points + 1):
            min_dist = min(np.sqrt((poses[i, 0] - obs[0])** 2 + (poses[i, 1] - obs[1])**2) for obs in self.obstacles)
            safety_cost += max(0, self.safe_distance - min_dist)** 2
        total_cost += safety_cost * 300  # 增加安全代价权重
        
        # 速度和角速度代价
        vel_cost = 0.0
        omega_cost = 0.0
        radius_cost = 0.0
        
        for i in range(self.n_points + 1):
            dx = poses[i+1, 0] - poses[i, 0]
            dy = poses[i+1, 1] - poses[i, 1]
            dist = np.sqrt(dx**2 + dy**2)
            v = dist / dt[i] if dt[i] > 0 else 0.0
            vel_cost += max(0, v - self.v_max)**2
            
            d_theta = poses[i+1, 2] - poses[i, 2]
            d_theta = (d_theta + np.pi) % (2 * np.pi) - np.pi  # 归一化角度
            omega = d_theta / dt[i] if dt[i] > 0 else 0.0
            omega_cost += max(0, abs(omega) - self.omega_max)** 2
            
            if abs(omega) > 1e-6:
                r = abs(v / omega)
                radius_cost += max(0, self.r_min - r)**2 * 5  # 增加转弯半径权重
        
        total_cost += vel_cost + omega_cost + radius_cost
        
        # 运动学约束代价
        kinematic_cost = 0.0
        for i in range(self.n_points + 1):
            l_k = np.array([np.cos(poses[i, 2]), np.sin(poses[i, 2]), 0])
            l_k1 = np.array([np.cos(poses[i+1, 2]), np.sin(poses[i+1, 2]), 0])
            d_k = np.array([poses[i+1, 0] - poses[i, 0], poses[i+1, 1] - poses[i, 1], 0])
            cross_product = np.cross(l_k + l_k1, d_k)
            kinematic_cost += cross_product[2]**2 * 5  # 增加运动学约束权重
        
        total_cost += kinematic_cost*100
        
        return total_cost
    
    def optimize_trajectory(self):
        """执行轨迹优化"""
        # 基于当前轨迹生成初始猜测（加速收敛）
        initial_guess = self._generate_initial_guess(self.poses)
        
        # 设置边界约束
        bounds = []
        for _ in range(self.n_points):
            bounds.extend([(-5, 5), (-5, 5), (-np.pi, np.pi)])  # x, y, theta范围
        for _ in range(self.n_points + 1):
            bounds.append((0.1, 2.0))  # 时间间隔范围
        
        # 执行优化
        result = minimize(self._compute_cost, initial_guess, method='L-BFGS-B', bounds=bounds, options={'maxiter': 50})
        self.poses, self.dt = self._extract_variables(result.x)
    
    def update_plot(self):
        """更新绘图显示（修改了障碍物可视化部分）"""
        self.ax.clear()
        
        # 绘制轨迹
        if self.poses is not None:
            self.ax.plot(self.poses[:, 0], self.poses[:, 1], 'b-', linewidth=2, label='Optimized Trajectory')
            
            # 绘制方向箭头
            for i in range(0, len(self.poses), max(1, len(self.poses)//10)):
                x, y, theta = self.poses[i]
                self.ax.arrow(x, y, 0.15 * np.cos(theta), 0.15 * np.sin(theta),
                             head_width=0.08, head_length=0.1, fc='blue', ec='blue')
        
        # 绘制起点和终点
        self.ax.plot(self.start_pose[0], self.start_pose[1], 'go', markersize=12, label='Start')
        self.ax.plot(self.end_pose[0], self.end_pose[1], 'ro', markersize=12, label='Goal')
        
        # 绘制障碍物（带安全距离区域）- 修改部分
        for idx, obs in enumerate(self.obstacles):
            # 安全区域（红色虚线圆）
            circle = plt.Circle(obs, self.safe_distance, color='r', fill=False, linestyle='--')
            self.ax.add_patch(circle)
            # 障碍物本身（黑色方块）
            self.ax.plot(obs[0], obs[1], 'ks', markersize=12, label='Obstacle' if idx == 0 else "")
        
        self.ax.legend()
        self.ax.grid(True)
        self.ax.axis('equal')
        self.fig.canvas.draw_idle()
    
    def on_press(self, event):
        """鼠标按下事件：判断是否点击障碍物"""
        if event.inaxes != self.ax:
            return
        
        # 检查是否点击了障碍物
        for i, obs in enumerate(self.obstacles):
            dist = np.sqrt((event.xdata - obs[0])** 2 + (event.ydata - obs[1])**2)
            if dist < 0.2:  # 点击范围阈值
                self.dragging = True
                self.dragged_index = i
                self.original_position = obs.copy()
                break
    
    def on_drag(self, event):
        """鼠标拖动事件：更新障碍物位置并重新规划"""
        if not self.dragging or event.inaxes != self.ax:
            return
        
        # 更新障碍物位置
        self.obstacles[self.dragged_index] = [event.xdata, event.ydata]
        
        # 重新规划轨迹（降低优化迭代次数以提高响应速度）
        self.optimize_trajectory()
        
        # 更新显示
        self.update_plot()
    
    def on_release(self, event):
        """鼠标释放事件：结束拖动"""
        self.dragging = False
        self.dragged_index = -1

# 运行程序
if __name__ == "__main__":
    # 初始参数
    start_pose = [0, 0, -np.pi/2]
    end_pose = [2, 2, np.pi/3]
    initial_obstacles = [[0.5, 0.75], [1.5, 1.25]]
    
    # 启动动态规划UI
    app = DynamicTEBPlanner(
        start_pose=start_pose,
        end_pose=end_pose,
        initial_obstacles=initial_obstacles,
        n_points=10,  # 中间轨迹点数量
        safe_distance=0.3,
        v_max=1.0,
        omega_max=np.pi/4,
        r_min=0.5
    )