import casadi as ca
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.gridspec as gridspec


# 设置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

def trapezoidal_collocation_with_extension(N=20):
    """梯形配点法轨迹优化，扩展到N+(N-1)个点并区分显示"""
    # 1. 时间离散化
    t = np.linspace(0, 1, N)  # 原始配点时间
    h = t[1:] - t[:-1]        # 时间间隔
    n_vars = 3 * N            # 决策变量: x, v, u
    
    # 2. 构建目标函数矩阵Q (最小化控制力平方和)
    Q = np.zeros((n_vars, n_vars))
    Q[2, 2] = h[0]  # u0的权重
    Q[3*N-1, 3*N-1] = h[-1]  # u_{N-1}的权重
    for k in range(1, N-1):
        Q[3*k + 2, 3*k + 2] = h[k-1] + h[k]  # uk的权重
    
    # 3. 构建约束矩阵A和向量b
    n_constraints = 2*(N-1) + 4
    A = np.zeros((n_constraints, n_vars))
    b = np.zeros(n_constraints)
    
    # 3.1 运动学约束（梯形配点公式）
    constraint_idx = 0
    for k in range(N-1):
        # 位置约束
        A[constraint_idx, 3*k] = -1
        A[constraint_idx, 3*k + 1] = -h[k]/2
        A[constraint_idx, 3*(k+1)] = 1
        A[constraint_idx, 3*(k+1) + 1] = -h[k]/2
        constraint_idx += 1
        
        # 速度约束
        A[constraint_idx, 3*k + 1] = -1
        A[constraint_idx, 3*k + 2] = -h[k]/2
        A[constraint_idx, 3*(k+1) + 1] = 1
        A[constraint_idx, 3*(k+1) + 2] = -h[k]/2
        constraint_idx += 1
    
    # 3.2 边界约束
    A[constraint_idx, 0] = 1          # x0 = 0
    b[constraint_idx] = 0
    constraint_idx += 1
    
    A[constraint_idx, 3*(N-1)] = 1    # x_{N-1} = 1
    b[constraint_idx] = 1
    constraint_idx += 1
    
    A[constraint_idx, 1] = 1          # v0 = 0
    b[constraint_idx] = 0
    constraint_idx += 1
    
    A[constraint_idx, 3*(N-1) + 1] = 1  # v_{N-1} = 0
    b[constraint_idx] = 0
    
    # 4. 构建并求解QP问题
    z = ca.SX.sym('z', n_vars)
    cost = 0.5 * ca.dot(z, Q @ z)
    constraints = A @ z
    
    qp = {'x': z, 'f': cost, 'g': constraints}
    solver = ca.qpsol('solver', 'qpoases', qp)
    
    # 初始猜测
    x0 = np.zeros(n_vars)
    for k in range(N):
        x0[3*k] = t[k]    # 位置初始猜测
        x0[3*k + 1] = 1   # 速度初始猜测
        x0[3*k + 2] = 0   # 控制力初始猜测
    
    # 求解
    sol = solver(x0=x0, lbg=b, ubg=b)
    z_opt = sol['x'].full().flatten()
    
    # 提取原始离散点
    x_original = z_opt[::3]   # 位置
    v_original = z_opt[1::3]  # 速度
    u_original = z_opt[2::3]  # 控制力
    
    # 5. 插值函数与扩展点计算
    def linear_interpolation(k, tau):
        """控制量u的线性插值"""
        if k >= len(h):
            return u_original[k]
        return u_original[k] + tau / h[k] * (u_original[k+1] - u_original[k])
    
    def quadratic_interpolation_x(k, tau):
        """位置x的二次插值"""
        if k >= len(h):
            return x_original[k]
        return x_original[k] + v_original[k] * tau + (tau**2) / (2 * h[k]) * (v_original[k+1] - v_original[k])
    
    # 生成扩展点（原始点+插值点）
    t_extended = []
    x_extended = []
    u_extended = []
    v_extended = []
    
    # 标记哪些是原始点（True），哪些是插值点（False）
    is_original = []
    
    for k in range(N):
        # 添加原始点
        t_extended.append(t[k])
        x_extended.append(x_original[k])
        v_extended.append(v_original[k])
        u_extended.append(u_original[k])
        is_original.append(True)
        
        # 在两个原始点之间添加插值点（最后一个点除外）
        if k < N-1:
            mid_time = (t[k] + t[k+1]) / 2  # 区间中点时间
            tau = mid_time - t[k]
            
            # 计算插值点
            x_mid = quadratic_interpolation_x(k, tau)
            v_mid = v_original[k] + u_original[k] * tau + (tau**2) / (2 * h[k]) * (u_original[k+1] - u_original[k])
            u_mid = linear_interpolation(k, tau)
            
            # 添加插值点
            t_extended.append(mid_time)
            x_extended.append(x_mid)
            v_extended.append(v_mid)
            u_extended.append(u_mid)
            is_original.append(False)
    
    # 分离原始点和插值点以便单独绘制
    t_original = [t_extended[i] for i in range(len(t_extended)) if is_original[i]]
    x_original_plot = [x_extended[i] for i in range(len(x_extended)) if is_original[i]]
    u_original_plot = [u_extended[i] for i in range(len(u_extended)) if is_original[i]]
    v_original_plot = [v_extended[i] for i in range(len(v_extended)) if is_original[i]]
    
    t_interp = [t_extended[i] for i in range(len(t_extended)) if not is_original[i]]
    x_interp_plot = [x_extended[i] for i in range(len(x_extended)) if not is_original[i]]
    u_interp_plot = [u_extended[i] for i in range(len(u_extended)) if not is_original[i]]
    v_interp_plot = [v_extended[i] for i in range(len(v_extended)) if not is_original[i]]
    
    # 6. 可视化
    fig = plt.figure(figsize=(12, 9))
    gs = gridspec.GridSpec(2, 2, width_ratios=[3, 2], height_ratios=[1, 1])
    
    # 6.1 物块运动演示
    ax_block = fig.add_subplot(gs[0, 0])
    ax_block.set_xlim(-0.1, 1.1)
    ax_block.set_ylim(-0.4, 0.4)
    ax_block.set_title('物块运动（原始点与插值点）', fontsize=14)
    ax_block.set_xlabel('位置', fontsize=12)
    ax_block.grid(alpha=0.3)
    
    # 起点和终点标记
    ax_block.plot([0, 0], [-0.1, 0.1], 'k-', linewidth=2)
    ax_block.plot([1, 1], [-0.1, 0.1], 'k-', linewidth=2)
    ax_block.text(-0.05, -0.25, '起点', ha='center')
    ax_block.text(1.05, -0.25, '终点', ha='center')
    
    # 原始位置点（蓝色圆形）和插值位置点（橙色方形）
    ax_block.scatter(x_original_plot, np.zeros_like(x_original_plot), 
                    c='blue', s=60, marker='o', alpha=0.7, label='原始位置点')
    ax_block.scatter(x_interp_plot, np.zeros_like(x_interp_plot), 
                    c='orange', s=40, marker='s', alpha=0.7, label='插值位置点')
    
    # 物块和轨迹
    block = plt.Rectangle((x_extended[0]-0.05, -0.2), 0.1, 0.4, fc='dodgerblue', ec='blue')
    trail, = ax_block.plot([x_extended[0]], [0], 'r--', linewidth=1)
    time_text = ax_block.text(0.05, 0.8, f'时间: 0.00s', transform=ax_block.transAxes)
    ax_block.add_patch(block)
    ax_block.legend()
    
    # 6.2 位置-时间曲线
    ax_pos = fig.add_subplot(gs[1, 0])
    ax_pos.set_xlim(0, 1)
    ax_pos.set_ylim(-0.1, 1.1)
    ax_pos.set_title('位置-时间曲线', fontsize=14)
    ax_pos.set_xlabel('时间 (s)')
    ax_pos.set_ylabel('位置')
    ax_pos.grid(alpha=0.3)
    
    # 绘制原始点和插值点
    ax_pos.scatter(t_original, x_original_plot, 
                  c='blue', s=60, marker='o', alpha=0.7, label='原始位置点')
    ax_pos.scatter(t_interp, x_interp_plot, 
                  c='orange', s=40, marker='s', alpha=0.7, label='插值位置点')
    pos_curve, = ax_pos.plot(t_extended, x_extended, 'gray', linewidth=1.5, label='连续轨迹')
    pos_marker, = ax_pos.plot([t_extended[0]], [x_extended[0]], 'red', marker='*', markersize=10, label='当前点')
    ax_pos.legend()
    
    # 6.3 速度-时间曲线
    ax_vel = fig.add_subplot(gs[0, 1])
    max_v = max(abs(np.array(v_extended))) * 1.2
    ax_vel.set_xlim(0, 1)
    ax_vel.set_ylim(-max_v, max_v)
    ax_vel.set_title('速度-时间曲线', fontsize=14)
    ax_vel.set_xlabel('时间 (s)')
    ax_vel.set_ylabel('速度')
    ax_vel.grid(alpha=0.3)
    ax_vel.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    
    # 绘制原始点和插值点
    ax_vel.scatter(t_original, v_original_plot, 
                  c='green', s=60, marker='o', alpha=0.7, label='原始速度点')
    ax_vel.scatter(t_interp, v_interp_plot, 
                  c='purple', s=40, marker='s', alpha=0.7, label='插值速度点')
    vel_curve, = ax_vel.plot(t_extended, v_extended, 'gray', linewidth=1.5, label='连续轨迹')
    vel_marker, = ax_vel.plot([t_extended[0]], [v_extended[0]], 'red', marker='*', markersize=10, label='当前点')
    ax_vel.legend()
    
    # 6.4 控制力-时间曲线
    ax_force = fig.add_subplot(gs[1, 1])
    max_u = max(abs(np.array(u_extended))) * 1.2
    ax_force.set_xlim(0, 1)
    ax_force.set_ylim(-max_u, max_u)
    ax_force.set_title('控制力-时间曲线', fontsize=14)
    ax_force.set_xlabel('时间 (s)')
    ax_force.set_ylabel('力')
    ax_force.grid(alpha=0.3)
    ax_force.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    
    # 绘制原始点和插值点
    ax_force.scatter(t_original, u_original_plot, 
                    c='green', s=60, marker='o', alpha=0.7, label='原始控制力点')
    ax_force.scatter(t_interp, u_interp_plot, 
                    c='purple', s=40, marker='s', alpha=0.7, label='插值控制力点')
    force_curve, = ax_force.plot(t_extended, u_extended, 'gray', linewidth=1.5, label='连续轨迹')
    force_marker, = ax_force.plot([t_extended[0]], [u_extended[0]], 'red', marker='*', markersize=10, label='当前点')
    ax_force.legend()
    
    plt.tight_layout()
    
    # 动画更新函数
    def update(frame):
        # 更新物块位置
        block.set_x(x_extended[frame] - 0.05)
        # 更新轨迹
        trail.set_data(x_extended[:frame+1], np.zeros(frame+1))
        # 更新时间文本
        time_text.set_text(f'时间: {t_extended[frame]:.2f}s')
        
        # 更新当前点标记
        pos_marker.set_data([t_extended[frame]], [x_extended[frame]])
        vel_marker.set_data([t_extended[frame]], [v_extended[frame]])
        force_marker.set_data([t_extended[frame]], [u_extended[frame]])
        
        return (block, trail, time_text, pos_marker, vel_marker, force_marker)
    
    # 创建动画
    ani = FuncAnimation(
        fig, update,
        frames=len(t_extended),
        interval=100,  # 每帧间隔100ms
        blit=True,
        repeat=False
    )
    
    # 保存动画
    writer = PillowWriter(fps=10)
    ani.save('extended_trajectory_animation.gif', writer=writer)
    plt.show()

# 运行程序（N=20，扩展后为39个点）
if __name__ == "__main__":
    trapezoidal_collocation_with_extension(N=10)
