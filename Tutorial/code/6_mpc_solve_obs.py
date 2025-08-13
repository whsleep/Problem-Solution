import irsim
import time
import casadi as ca
import numpy as np

class TrajectoryOptimizer:
    def __init__(self, T=0.1, N=100, v_max=0.8, omega_max=1.0, obstacles=None):
        """
        轨迹优化器初始化(单次求解完整轨迹)
        :param T: 采样时间
        :param N: 总步数(状态序列长度为N+1,控制序列长度为N)
        :param v_max: 最大线速度
        :param omega_max: 最大角速度
        :param obstacles: 障碍物列表，每个障碍物为字典{'x': x, 'y': y, 'r': 半径, 'safety_dist': 安全距离}
                          例如: [{'x':1.0, 'y':1.0, 'r':0.3, 'safety_dist':0.2}]
        """
        # 控制器参数
        self.T = T
        self.N = N  # 控制序列长度
        self.v_max = v_max
        self.omega_max = omega_max
        self.n_states = 3  # x, y, theta
        self.n_controls = 2  # v, omega
        
        # 障碍物参数（默认无障碍物，可外部传入）
        self.obstacles = obstacles if obstacles is not None else []
        
        # 初始化求解器
        self._build_kinematic_model()
        self._build_optimizer()
        
    def _build_kinematic_model(self):
        """构建车辆运动学模型"""
        x = ca.SX.sym('x')
        y = ca.SX.sym('y')
        theta = ca.SX.sym('theta')
        states = ca.vertcat(x, y, theta)
        
        v = ca.SX.sym('v')
        omega = ca.SX.sym('omega')
        controls = ca.vertcat(v, omega)
        
        # 连续时间运动学方程
        rhs = ca.vertcat(
            v * ca.cos(theta),
            v * ca.sin(theta),
            omega
        )
        
        # 状态转移函数
        self.f = ca.Function('f', [states, controls], [rhs])
        
    def _build_optimizer(self):
        """构建轨迹优化求解器（含障碍约束）"""
        # 优化变量
        U = ca.SX.sym('U', self.n_controls, self.N)  # 控制序列（长度2xN）
        X = ca.SX.sym('X', self.n_states, self.N+1)  # 状态序列（长度3xN+1）
        P = ca.SX.sym('P', 2*self.n_states)          # 参数: [初始状态, 目标状态]（6x1）
        
        # 代价函数权重
        self.Q = np.diag([20.0, 20.0, 100.0])  # 状态权重（x,y,theta）
        self.R = np.diag([1.0, 1.0])         # 控制权重（v,omega）
        self.Qf = np.diag([20.0, 20.0, 100.0]) # 终端状态权重
        
        # 构建目标函数和约束
        obj = 0
        g = []  # 约束列表（后续逐步添加）
        
        # 1. 初始状态约束（X[:,0] = 初始状态）
        g.append(X[:, 0] - P[:self.n_states])
        
        # 2. 终端状态约束（X[:,N] = 目标状态）
        g.append(X[:, -1] - P[self.n_states:])
        
        # 3. 运动学约束（欧拉离散）
        for i in range(self.N):
            x_b = (X[:, i+1] - X[:, i]) / self.T - self.f(X[:, i], U[:, i])
            g.append(x_b)
        
        # 4. 障碍约束（车辆与障碍物的距离 ≥ 安全距离）
        # 车辆自身半径（假设为0.2m，可根据实际情况调整）
        self.robot_radius = 0.2
        for obs in self.obstacles:
            obs_x = obs['x']
            obs_y = obs['y']
            obs_r = obs['r']
            safety_dist = obs['safety_dist']
            # 最小安全距离 = 障碍物半径 + 车辆半径 + 额外安全距离
            min_distance = obs_r + self.robot_radius + safety_dist
            # 对每个状态点添加距离约束
            for i in range(self.N+1):
                # 车辆中心(x,y)与障碍物中心的欧氏距离
                dist = ca.sqrt((X[0, i] - obs_x)**2 + (X[1, i] - obs_y)** 2)
                # 约束：距离 ≥ 最小安全距离（dist - min_distance ≥ 0）
                g.append(dist - min_distance)
        
        # 构建目标函数
        for i in range(self.N):
            # 阶段代价（状态跟踪 + 控制平滑）
            state_error = X[:, i] - P[self.n_states:]
            obj += ca.mtimes([state_error.T, self.Q, state_error])
            obj += ca.mtimes([U[:, i].T, self.R, U[:, i]])
        # 终端代价
        final_error = X[:, -1] - P[self.n_states:]
        obj += ca.mtimes([final_error.T, self.Qf, final_error])
        
        # 优化变量向量（控制序列 + 状态序列）
        opt_vars = ca.vertcat(
            ca.reshape(U, -1, 1),
            ca.reshape(X, -1, 1)
        )
        
        # 构建NLP问题
        nlp_prob = {
            'f': obj,
            'x': opt_vars,
            'p': P,
            'g': ca.vertcat(*g)
        }
        
        # 求解器配置（增加迭代次数以处理更多约束）
        opts = {
            'ipopt': {
                'max_iter': 10000,  # 障碍约束增加后需更多迭代
                'print_level': 3,
                'acceptable_tol': 1e-6,
                'acceptable_obj_change_tol': 1e-6,
                'tol': 1e-6
            },
            'print_time': 1
        }
        
        self.solver = ca.nlpsol('solver', 'ipopt', nlp_prob, opts)
        
        # 约束上下界设置
        # 计算约束总数量：初始状态(3) + 终端状态(3) + 运动学约束(N*3) + 障碍约束(障碍物数量*(N+1))
        n_initial = self.n_states
        n_terminal = self.n_states
        n_kinematic = self.N * self.n_states
        n_obstacle = len(self.obstacles) * (self.N + 1)
        total_constraints = n_initial + n_terminal + n_kinematic + n_obstacle
        
        self.lbg = []
        self.ubg = []
        
        # 初始状态约束（等于初始值）
        self.lbg.extend([0.0] * n_initial)
        self.ubg.extend([0.0] * n_initial)
        
        # 终端状态约束（等于目标值）
        self.lbg.extend([0.0] * n_terminal)
        self.ubg.extend([0.0] * n_terminal)
        
        # 运动学约束（等于0）
        self.lbg.extend([0.0] * n_kinematic)
        self.ubg.extend([0.0] * n_kinematic)
        
        # 障碍约束（距离 ≥ 最小安全距离 → dist - min_distance ≥ 0）
        self.lbg.extend([0.0] * n_obstacle)
        self.ubg.extend([np.inf] * n_obstacle)
        
        # 控制输入约束（v和omega的上下限）
        self.lbx = []
        self.ubx = []
        for _ in range(self.N):
            self.lbx.extend([-self.v_max, -self.omega_max])  # v的范围, omega的范围
            self.ubx.extend([self.v_max, self.omega_max])
        
        # 状态变量约束（x,y无硬限制，theta无限制）
        for _ in range(self.N + 1):
            self.lbx.extend([-np.inf, -np.inf, -np.inf])  # x, y, theta的下界
            self.ubx.extend([np.inf, np.inf, np.inf])      # x, y, theta的上界
    
    def solve(self, x0, xs):
        """
        单次求解完整轨迹
        :param x0: 初始状态 [x, y, theta]
        :param xs: 目标状态 [x, y, theta]
        :return: 状态轨迹、控制序列、时间序列
        """
        # 构建参数向量（初始状态 + 目标状态）
        c_p = np.concatenate((x0, xs)).flatten()
        
        # 优化变量初始猜测（改进初始猜测以提高求解效率）
        u_init = np.zeros((self.n_controls, self.N))
        x_init = np.zeros((self.n_states, self.N+1))
        # 线性初始猜测（从起点到终点的直线插值）
        for i in range(self.N+1):
            alpha = i / self.N
            x_init[:, i] = x0.flatten() * (1 - alpha) + xs.flatten() * alpha
        init_opt = np.concatenate((u_init.flatten(), x_init.flatten()))
        
        # 求解NLP
        start_time = time.time()
        res = self.solver(
            x0=init_opt,
            p=c_p,
            lbg=self.lbg,
            ubg=self.ubg,
            lbx=self.lbx,
            ubx=self.ubx
        )
        total_time = time.time() - start_time
        
        # 检查求解是否成功
        if not self.solver.stats()['success']:
            print("求解失败! 可能原因：约束冲突（如轨迹与障碍物重叠）或求解器未收敛。")
            return None, None, None
        
        # 提取优化结果
        opt_result = res['x'].full().flatten()
        u_opt = opt_result[:self.n_controls*self.N].reshape(self.N, self.n_controls)
        x_opt = opt_result[self.n_controls*self.N:].reshape(self.N+1, self.n_states)
        
        # 生成时间序列
        t_opt = np.linspace(0, self.N*self.T, self.N+1)
        
        # 求解总结
        print(f"求解完成: 总步数 = {self.N}, 总耗时 = {total_time:.4f}s")
        
        return x_opt, u_opt, t_opt


if __name__ == '__main__':
    try:
        # 定义障碍物（可修改位置、半径和安全距离）
        obstacles = [
            {'x': 1.0, 'y': 0.8, 'r': 0.3, 'safety_dist': 0.2},  # 障碍物1：中心(1.0,0.8)，半径0.3m，安全距离0.2m
            {'x': 1.5, 'y': 1.5, 'r': 0.2, 'safety_dist': 0.1}   # 障碍物2：中心(1.5,1.5)，半径0.2m，安全距离0.1m
        ]
        
        # 创建轨迹优化器实例（含障碍约束）
        optimizer = TrajectoryOptimizer(
            T=0.1, 
            N=200, 
            v_max=0.8, 
            omega_max=1.0,
            obstacles=obstacles  # 传入障碍物参数
        )
        
        # 初始状态和目标状态
        x0 = np.array([0.0, 0.0, -np.pi]).reshape(-1, 1)  # [x, y, theta]：起点(0,0)，朝向-π（向左）
        xs = np.array([2.0, 2.0, np.pi/2]).reshape(-1, 1)   # 目标状态(2,2)，朝向π/2（向上）
        
        # 单次求解完整轨迹（含避障）
        x_trajectory, u_controls, t_sequence = optimizer.solve(x0, xs)

        if x_trajectory is not None and u_controls is not None:
            # 仿真执行求解出的控制序列
            env = irsim.make('robot_world.yaml', save_ani=True, display=True, full=False)
            # 确保不超过可用的控制输入数量
            steps = min(len(u_controls), 200)
            for i in range(steps):
                env.step(action_id=0, action=u_controls[i])
                env.render()
                if env.done():
                    break
            env.end(ani_name='mpc_nlp_with_obstacle', ending_time=steps*0.1)
            
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
