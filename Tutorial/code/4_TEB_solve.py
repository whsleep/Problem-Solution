import casadi as ca
import numpy as np
import matplotlib.pyplot as plt

# ---------- 用户参数 ----------
n         = 50          # 中间点数
SafeDis   = 0.30        # 安全距离
v_max     = 1.0
omega_max = 1.0
r_min     = 0.5
a_max     = 2.0
epsilon   = 1e-2

w_p = 0.5               # 路径权重
w_t = 1.0               # 时间权重

# 边界姿态
x0 = [0.0, 0.0, -np.pi]
xf = [2.0, 2.0,  np.pi/3]

# 障碍物
obstacles = np.array([[0.5, 0.75],
                      [1.5, 1.25]])

# ---------- 变量 ----------
x     = ca.SX.sym('x', n+2)      # 0..n+1
y     = ca.SX.sym('y', n+2)
theta = ca.SX.sym('theta', n+2)
dt    = ca.SX.sym('dt', n+1)

z = ca.vertcat(x, y, theta, dt)  # 拉平
nz = z.shape[0]

# ---------- 目标函数 ----------
f = 0
for i in range(n+1):
    dx = x[i+1] - x[i]
    dy = y[i+1] - y[i]
    f += w_p * (dx**2 + dy**2) + w_t * dt[i]**2

# ---------- 约束 ----------
g_eq   = []   # h(z)=0
g_ineq = []   # g(z)≤0

# 1) 边界姿态（等式）
g_eq.append(x[0]     - x0[0])
g_eq.append(y[0]     - x0[1])
g_eq.append(theta[0] - x0[2])
g_eq.append(x[-1]    - xf[0])
g_eq.append(y[-1]    - xf[1])
g_eq.append(theta[-1]- xf[2])

# 2) 避障（不等式）
for i in range(1, n+1):                 # 仅中间点
    for ox, oy in obstacles:
        dist = ca.sqrt((x[i]-ox)**2 + (y[i]-oy)**2)
        g_ineq.append(SafeDis - dist)   # ≤0

# 3) 速度、角速度、转弯半径、加速度
for i in range(n+1):
    dx   = x[i+1] - x[i]
    dy   = y[i+1] - y[i]
    dist = ca.sqrt(dx**2 + dy**2)

    v     = dist / (dt[i] + epsilon)
    dth   = ca.atan2(ca.sin(theta[i+1]-theta[i]),
                     ca.cos(theta[i+1]-theta[i]))
    omega = dth / (dt[i] + epsilon)
    radius = v / (ca.fabs(omega) + epsilon)

    # 速度、角速度、转弯半径
    g_ineq.append(v      - v_max)      # v ≤ v_max
    g_ineq.append(-v     - v_max)      # -v ≤ v_max  即 |v|≤v_max
    g_ineq.append(omega  - omega_max)
    g_ineq.append(-omega - omega_max)
    g_ineq.append(r_min  - radius)     # r ≥ r_min

    # 加速度（线）
    if i < n:
        dx2   = x[i+2] - x[i+1]
        dy2   = y[i+2] - y[i+1]
        dist2 = ca.sqrt(dx2**2 + dy2**2)
        v2    = dist2 / (dt[i+1] + epsilon)
        acc   = (v2 - v) / (0.5*(dt[i]+dt[i+1]) + epsilon)
        g_ineq.append(acc  - a_max)
        g_ineq.append(-acc - a_max)

# 4) 非完整约束（等式）
for i in range(n+1):
    dx   = x[i+1] - x[i]
    dy   = y[i+1] - y[i]
    li   = ca.vertcat(ca.cos(theta[i]),  ca.sin(theta[i]))
    li1  = ca.vertcat(ca.cos(theta[i+1]), ca.sin(theta[i+1]))
    cross = (li[0]+li1[0])*dy - (li[1]+li1[1])*dx
    g_eq.append(cross)

# 5) 时间间隔非负
for i in range(n+1):
    g_ineq.append(-dt[i])   # -dt ≤ 0  => dt ≥ 0

# ---------- 求解器 ----------
g = ca.vertcat(*g_eq, *g_ineq)
lbg = [0]*len(g_eq) + [-ca.inf]*len(g_ineq)
ubg = [0]*len(g_eq) + [0]*len(g_ineq)

# 初始猜测
z0 = np.zeros(nz)
# 位置：线性插值
z0[:n+2]   = np.linspace(x0[0], xf[0], n+2)
z0[n+2:2*n+4] = np.linspace(x0[1], xf[1], n+2)
z0[2*n+4:3*n+6] = np.linspace(x0[2], xf[2], n+2)
z0[3*n+6:] = np.ones(n+1)*0.5      # dt

nlp = {'x': z, 'f': f, 'g': g}
opts = {'ipopt.print_level': 0, 'print_time': True}
solver = ca.nlpsol('solver', 'ipopt', nlp, opts)
res = solver(x0=z0,
             lbg=lbg,
             ubg=ubg)

# ---------- 可视化 ----------
x_opt  = res['x'][:n+2].full().flatten()
y_opt  = res['x'][n+2:2*n+4].full().flatten()
theta_opt = res['x'][2*n+4:3*n+6].full().flatten()

fig, ax = plt.subplots(figsize=(6,6))
ax.set_aspect('equal')
ax.set_xlim(-0.2, 2.2); ax.set_ylim(-0.2, 2.2)

pt_radius = 0.06
head_scale = 0.4
colors = ['tab:blue'] + ['tab:red']*n + ['tab:green']

for k,(xi,yi,thi,col) in enumerate(zip(x_opt, y_opt, theta_opt, colors)):
    circle = plt.Circle((xi,yi), pt_radius, color=col, alpha=0.2)
    ax.add_patch(circle)
    dx = pt_radius*np.cos(thi)
    dy = pt_radius*np.sin(thi)
    ax.arrow(xi,yi,dx,dy, head_width=head_scale*pt_radius, fc='k', ec='k')

ax.scatter(obstacles[:,0], obstacles[:,1], c='k', s=300, label='obstacle')
for o in obstacles:
    ax.add_patch(plt.Circle(o, SafeDis, color='k', alpha=0.1))
ax.plot([x0[0],xf[0]], [x0[1],xf[1]], 'k--', alpha=0.3, label='straight')
ax.legend()
plt.tight_layout()
plt.show()