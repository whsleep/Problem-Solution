import casadi as ca
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
import matplotlib.gridspec as gridspec


# 设置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

def explicit_qp_solver_with_visualization(N=100):
    """使用显式QP格式求解并可视化物块轨迹优化问题"""
    # 时间离散化
    t = np.linspace(0, 1, N)
    h = t[1:] - t[:-1]  # 时间间隔
    n_vars = 3 * N      # 决策变量总数: 每个配点有x, v, u三个变量
    
    # 1. 显式构建二次项系数矩阵Q
    Q = np.zeros((n_vars, n_vars))
    # 第一个u和最后一个u的系数
    Q[2, 2] = h[0]  # u0
    Q[3*N-1, 3*N-1] = h[-1]  # u_{N-1}
    # 中间u的系数
    for k in range(1, N-1):
        Q[3*k + 2, 3*k + 2] = h[k-1] + h[k]  # uk
    
    # 2. 显式构建约束矩阵A和向量b
    n_constraints = 2*(N-1) + 4  # 约束总数
    A = np.zeros((n_constraints, n_vars))
    b = np.zeros(n_constraints)
    
    # 2.1 运动学约束
    constraint_idx = 0
    for k in range(N-1):
        # x约束: x_{k+1} - x_k - h_k*(v_k + v_{k+1})/2 = 0
        A[constraint_idx, 3*k] = -1
        A[constraint_idx, 3*k + 1] = -h[k]/2
        A[constraint_idx, 3*(k+1)] = 1
        A[constraint_idx, 3*(k+1) + 1] = -h[k]/2
        constraint_idx += 1
        
        # v约束: v_{k+1} - v_k - h_k*(u_k + u_{k+1})/2 = 0
        A[constraint_idx, 3*k + 1] = -1
        A[constraint_idx, 3*k + 2] = -h[k]/2
        A[constraint_idx, 3*(k+1) + 1] = 1
        A[constraint_idx, 3*(k+1) + 2] = -h[k]/2
        constraint_idx += 1
    
    # 2.2 边界约束
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
    
    # 3. 构建QP问题 (显式矩阵形式) 3Nx1
    z = ca.SX.sym('z', n_vars)
    # 目标函数: 0.5*z^T Q z
    cost = 0.5 * ca.dot(z, Q @ z)
    # 约束: A z = b (通过设置lbg=ubg=b实现)
    constraints = A @ z
    
    # 定义QP问题结构
    qp = {
        'x': z,        # 决策变量
        'f': cost,     # 目标函数
        'g': constraints  # 约束表达式
    }
    
    # 选择求解器
    solver = ca.qpsol('solver', 'qpoases', qp)
    
    # 初始猜测值
    x0 = np.zeros(n_vars)
    for k in range(N):
        x0[3*k] = t[k]    # x初始猜测: x(t)=t
        x0[3*k + 1] = 1   # v初始猜测: v(t)=1
        x0[3*k + 2] = 0   # u初始猜测: u(t)=0
    
    # 求解QP问题 (等式约束 A z = b)
    sol = solver(x0=x0, lbg=b, ubg=b)
    z_opt = sol['x'].full().flatten()
    
    # 提取结果
    x = z_opt[::3]   # 位置
    v = z_opt[1::3]  # 速度
    u = z_opt[2::3]  # 控制力
    
    # 5. 动态可视化
    fig = plt.figure(figsize=(12, 9))
    gs = gridspec.GridSpec(2, 2, width_ratios=[3, 2], height_ratios=[1, 1])
    
    # 5.1 物块运动演示
    ax_block = fig.add_subplot(gs[0, 0])
    ax_block.set_xlim(-0.1, 1.1)
    ax_block.set_ylim(-0.4, 0.4)
    ax_block.set_title('物块运动演示 (显式QP求解)', fontsize=14)
    ax_block.set_xlabel('位置', fontsize=12)
    ax_block.grid(alpha=0.3)
    # 起点和终点标记
    ax_block.plot([0, 0], [-0.1, 0.1], 'k-', linewidth=2)
    ax_block.plot([1, 1], [-0.1, 0.1], 'k-', linewidth=2)
    ax_block.text(-0.05, -0.25, '起点', ha='center')
    ax_block.text(1.05, -0.25, '终点', ha='center')
    # 物块和轨迹
    block = plt.Rectangle((x[0]-0.05, -0.2), 0.1, 0.4, fc='dodgerblue', ec='blue')
    trail, = ax_block.plot([x[0]], [0], 'r--', linewidth=1)
    time_text = ax_block.text(0.05, 0.8, f'时间: 0.00s', transform=ax_block.transAxes)
    ax_block.add_patch(block)
    
    # 5.2 位置-时间曲线
    ax_pos = fig.add_subplot(gs[1, 0])
    ax_pos.set_xlim(0, 1)
    ax_pos.set_ylim(-0.1, 1.1)
    ax_pos.set_title('位置-时间曲线', fontsize=14)
    ax_pos.set_xlabel('时间 (s)')
    ax_pos.set_ylabel('位置')
    ax_pos.grid(alpha=0.3)
    pos_line, = ax_pos.plot(t, x, 'b-', linewidth=1.5)
    pos_marker, = ax_pos.plot([t[0]], [x[0]], 'ro', markersize=6)
    
    # 5.3 速度-时间曲线
    ax_vel = fig.add_subplot(gs[0, 1])
    max_v = max(abs(v)) * 1.2
    ax_vel.set_xlim(0, 1)
    ax_vel.set_ylim(-max_v, max_v)
    ax_vel.set_title('速度-时间曲线', fontsize=14)
    ax_vel.set_xlabel('时间 (s)')
    ax_vel.set_ylabel('速度')
    ax_vel.grid(alpha=0.3)
    ax_vel.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    vel_line, = ax_vel.plot(t, v, 'g-', linewidth=1.5)
    vel_marker, = ax_vel.plot([t[0]], [v[0]], 'ro', markersize=6)
    
    # 5.4 控制力-时间曲线
    ax_force = fig.add_subplot(gs[1, 1])
    max_u = max(abs(u)) * 1.2
    ax_force.set_xlim(0, 1)
    ax_force.set_ylim(-max_u, max_u)
    ax_force.set_title('控制力-时间曲线', fontsize=14)
    ax_force.set_xlabel('时间 (s)')
    ax_force.set_ylabel('力')
    ax_force.grid(alpha=0.3)
    ax_force.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    force_line, = ax_force.plot(t, u, 'purple', linewidth=1.5)
    force_marker, = ax_force.plot([t[0]], [u[0]], 'ro', markersize=6)
    
    plt.tight_layout()
    
    # 动画更新函数
    def update(frame):
        # 更新物块位置
        block.set_x(x[frame] - 0.05)
        # 更新轨迹
        trail.set_data(x[:frame+1], np.zeros(frame+1))
        # 更新时间文本
        time_text.set_text(f'时间: {t[frame]:.2f}s')
        # 更新各曲线标记
        pos_marker.set_data([t[frame]], [x[frame]])
        vel_marker.set_data([t[frame]], [v[frame]])
        force_marker.set_data([t[frame]], [u[frame]])
        
        return (block, trail, time_text, pos_marker, vel_marker, force_marker)
    
    # 创建动画
    ani = FuncAnimation(
        fig, update,
        frames=len(t),
        interval=50,  # 每帧间隔50ms
        blit=True,
        repeat=False
    )
    
    # 保存为GIF (无需额外依赖)
    writer = PillowWriter(fps=30)
    ani.save('block_trajectory.gif', writer=writer)
    plt.show()

# 运行程序
if __name__ == "__main__":
    explicit_qp_solver_with_visualization(N=100)
