import irsim
import time
import casadi as ca
import numpy as np

class TrajectoryOptimizer:
    def __init__(self, T=0.1, N=100, v_max=0.8, omega_max=1.0):
        """
        轨迹优化器初始化(单次求解完整轨迹)
        :param T: 采样时间
        :param N: 总步数(状态序列长度为N+1,控制序列长度为N)
        :param v_max: 最大线速度
        :param omega_max: 最大角速度
        """
        # 控制器参数
        self.T = T
        self.N = N  # 控制序列长度
        self.v_max = v_max
        self.omega_max = omega_max
        self.n_states = 3  # x, y, theta
        self.n_controls = 2  # v, omega
        
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
        """构建轨迹优化求解器"""
        # 优化变量
        U = ca.SX.sym('U', self.n_controls, self.N)  # 控制序列（长度N）
        X = ca.SX.sym('X', self.n_states, self.N+1)  # 状态序列（长度N+1）
        P = ca.SX.sym('P', 2*self.n_states)          # 参数: [初始状态, 目标状态]
        
        # 代价函数权重
        self.Q = np.diag([20.0, 20.0, 100.0])  # 状态权重
        self.R = np.diag([1.0, 1.0])         # 控制权重
        self.Qf = np.diag([20.0, 20.0, 100.0]) # 终端状态权重（更大以确保收敛到目标）
        
        # 构建目标函数和约束
        obj = 0
        g = [X[:, 0] - P[:self.n_states]]  # 初始状态约束
        g.append(X[:, -1] - P[self.n_states:])  # 终端状态约束（强制最后到达目标）
        
        for i in range(self.N):
            # 阶段代价
            state_error = X[:, i] - P[self.n_states:]
            obj += ca.mtimes([state_error.T, self.Q, state_error])
            obj += ca.mtimes([U[:, i].T, self.R, U[:, i]])
            
            # 运动学约束 (欧拉离散)
            x_next = X[:, i] + self.T * self.f(X[:, i], U[:, i])
            g.append(X[:, i+1] - x_next)
        
        # 终端代价
        final_error = X[:, -1] - P[self.n_states:]
        obj += ca.mtimes([final_error.T, self.Qf, final_error])
        
        # 优化变量向量
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
        
        # 求解器配置
        opts = {
            'ipopt': {
                'max_iter': 2000,
                'print_level': 3,
                'acceptable_tol': 1e-6,
                'acceptable_obj_change_tol': 1e-6
            },
            'print_time': 1
        }
        
        self.solver = ca.nlpsol('solver', 'ipopt', nlp_prob, opts)
        
        # 约束上下界
        # 初始状态和终端状态约束为硬约束（等于给定值）
        self.lbg = [0.0]*self.n_states + [0.0]*self.n_states + [0.0]*(self.N*self.n_states)
        self.ubg = [0.0]*self.n_states + [0.0]*self.n_states + [0.0]*(self.N*self.n_states)
        
        # 控制输入约束
        self.lbx = []
        self.ubx = []
        for _ in range(self.N):
            self.lbx.extend([-self.v_max, -self.omega_max])
            self.ubx.extend([self.v_max, self.omega_max])
        
        # 状态变量约束
        for _ in range(self.N + 1):
            self.lbx.extend([-np.inf, -np.inf, -np.inf])
            self.ubx.extend([np.inf, np.inf, np.inf])
    
    def solve(self, x0, xs):
        """
        单次求解完整轨迹
        :param x0: 初始状态 [x, y, theta]
        :param xs: 目标状态 [x, y, theta]
        :return: 状态轨迹、控制序列、时间序列
        """
        # 构建参数向量
        c_p = np.concatenate((x0, xs)).flatten()
        
        # 优化变量初始猜测（可以改进初始猜测以提高求解效率）
        u_init = np.zeros((self.n_controls, self.N))
        x_init = np.zeros((self.n_states, self.N+1))
        # 简单线性初始猜测
        for i in range(self.N+1):
            alpha = i / self.N
            x_init[:, i] = x0.flatten() * (1-alpha) + xs.flatten() * alpha
        init_opt = np.concatenate((u_init.flatten(), x_init.flatten()))
        
        # 求解NLP（仅调用一次）
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
        if self.solver.stats()['success'] is False:
            print("求解失败!")
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
        # 创建轨迹优化器实例（N=100表示100个控制量，101个状态）
        optimizer = TrajectoryOptimizer(T=0.1, N=200)
        
        # 初始状态和目标状态
        x0 = np.array([0.0, 0.0, -np.pi]).reshape(-1, 1)  # [x, y, theta]
        xs = np.array([2.0, 2.0, np.pi/2]).reshape(-1, 1)   # 目标状态
        
        # 单次求解完整轨迹
        x_trajectory, u_controls, t_sequence = optimizer.solve(x0, xs)

        if x_trajectory is not None and u_controls is not None:
            # 仿真执行求解出的控制序列
            env = irsim.make('robot_world.yaml')
            # 确保不超过可用的控制输入数量
            steps = min(len(u_controls), 200)
            for i in range(steps):
                env.step(action_id=0, action=u_controls[i])
                env.render()

                if env.done():
                    break

            env.end()
            
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
    