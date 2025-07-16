import casadi as ca
import numpy as np
import matplotlib.pyplot as plt

# ---------- 1. 用户参数 ----------
n         = 40          # 中间点数
SafeDis   = 0.30        # 安全距离
v_max     = 1.0
omega_max = 1.0
r_min     = 0.5
a_max     = 2.0
epsilon   = 1e-2

w_p = 1.0             # 路径权重
w_t = 0.5              # 时间权重

# 边界姿态
x0 = [0.0, 0.0, -np.pi]
xf = [2.0, 2.0,  np.pi/3]

# 障碍物（可拖拽）
obstacles = np.array([[0.5, 0.75],
                      [1.5, 1.25]])

# ---------- 2. 实时求解器 ----------
def build_solver(obs_now):
    # ---------- 变量 ----------
    x     = ca.SX.sym('x', n+2)      # 0..n+1
    y     = ca.SX.sym('y', n+2)
    theta = ca.SX.sym('theta', n+2)
    dt    = ca.SX.sym('dt', n+1)
    z = ca.vertcat(x, y, theta, dt)

    # ---------- 目标函数 ----------
    f = 0
    for i in range(n+1):
        dx = x[i+1] - x[i]
        dy = y[i+1] - y[i]
        f += w_p * (dx**2 + dy**2) + w_t * dt[i]**2

    # ---------- 约束 ----------
    g_eq   = []
    g_ineq = []

    # 1) 边界姿态
    g_eq.extend([x[0]-x0[0], y[0]-x0[1], theta[0]-x0[2],
                 x[-1]-xf[0], y[-1]-xf[1], theta[-1]-xf[2]])

    # 2) 避障
    for i in range(1, n+1):
        for ox, oy in obs_now:
            dist = ca.sqrt((x[i]-ox)**2 + (y[i]-oy)**2)
            g_ineq.append(SafeDis - dist)

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

        g_ineq.extend([v - v_max, -v - v_max,
                       omega - omega_max, -omega - omega_max,
                       r_min - radius])

        if i < n:
            dx2   = x[i+2] - x[i+1]
            dy2   = y[i+2] - y[i+1]
            dist2 = ca.sqrt(dx2**2 + dy2**2)
            v2    = dist2 / (dt[i+1] + epsilon)
            acc   = (v2 - v) / (0.5*(dt[i]+dt[i+1]) + epsilon)
            g_ineq.extend([acc - a_max, -acc - a_max])

    # 4) 非完整约束
    for i in range(n+1):
        dx   = x[i+1] - x[i]
        dy   = y[i+1] - y[i]
        li   = ca.vertcat(ca.cos(theta[i]), ca.sin(theta[i]))
        li1  = ca.vertcat(ca.cos(theta[i+1]), ca.sin(theta[i+1]))
        cross = (li[0]+li1[0])*dy - (li[1]+li1[1])*dx
        g_eq.append(cross)

    # 5) dt ≥ 0
    g_ineq.extend([-dt[i] for i in range(n+1)])

    # ---------- 求解器 ----------
    g = ca.vertcat(*g_eq, *g_ineq)
    lbg = [0]*len(g_eq) + [-ca.inf]*len(g_ineq)
    ubg = [0]*len(g_eq) + [0]*len(g_ineq)

    # 初始猜测
    z0 = np.zeros((3*(n+2)+n+1))
    z0[:n+2]   = np.linspace(x0[0], xf[0], n+2)
    z0[n+2:2*n+4] = np.linspace(x0[1], xf[1], n+2)
    z0[2*n+4:3*n+6] = np.linspace(x0[2], xf[2], n+2)
    z0[3*n+6:] = np.ones(n+1)*0.5

    nlp = {'x': z, 'f': f, 'g': g}
    opts = {'ipopt.print_level': 0, 'print_time': 1,
                'ipopt.max_iter': 5000
                    }
    solver = ca.nlpsol('solver', 'ipopt', nlp, opts)
    res = solver(x0=z0, lbg=lbg, ubg=ubg)
    return res

def extract_trajectory(res):
    x  = res['x'][:n+2].full().flatten()
    y  = res['x'][n+2:2*n+4].full().flatten()
    th = res['x'][2*n+4:3*n+6].full().flatten()
    return np.column_stack((x, y, th))

# ---------- 3. 可视化 ----------
fig, ax = plt.subplots(figsize=(6,6))
ax.set_aspect('equal')
ax.set_xlim(-0.2, 2.2); ax.set_ylim(-0.2, 2.2)

pt_radius  = 0.06
head_scale = 0.4

# 轨迹点圆圈和箭头
circles = []
arrows  = []
for _ in range(n+2):
    c = plt.Circle((0,0), pt_radius, color='tab:red', alpha=0.2)
    ax.add_patch(c); circles.append(c)
    ar = ax.arrow(0,0,0,0, head_width=head_scale*pt_radius, fc='k', ec='k')
    arrows.append(ar)
circles[0].set_color('tab:blue')
circles[-1].set_color('tab:green')

# 障碍物与安全圆
obs_scat   = ax.scatter(obstacles[:,0], obstacles[:,1], s=300, c='k', picker=True)
safe_circs = [plt.Circle(o, SafeDis, color='k', alpha=0.1) for o in obstacles]
for c in safe_circs:
    ax.add_patch(c)

def update_plot(traj):
    for k,(xi,yi,thi) in enumerate(traj):
        circles[k].center = (xi, yi)
        arrows[k].remove()
        dx = pt_radius*np.cos(thi)
        dy = pt_radius*np.sin(thi)
        arrows[k] = ax.arrow(xi, yi, dx, dy,
                             head_width=head_scale*pt_radius,
                             fc='k', ec='k')
    obs_scat.set_offsets(obstacles)
    for c,o in zip(safe_circs, obstacles):
        c.center = o
    fig.canvas.draw_idle()

# 初始绘制
res = build_solver(obstacles)
traj = extract_trajectory(res)
print('Initial cost =', float(res['f']))
update_plot(traj)

# ---------- 4. 鼠标交互 ----------
drag_idx = None

def on_pick(event):
    global drag_idx
    if event.artist == obs_scat:
        drag_idx = event.ind[0]

def on_motion(event):
    global drag_idx
    if drag_idx is None or event.xdata is None: return
    obstacles[drag_idx] = [event.xdata, event.ydata]
    obs_scat.set_offsets(obstacles)
    for c,o in zip(safe_circs, obstacles):
        c.center = o
    fig.canvas.draw_idle()

def on_release(event):
    global drag_idx
    if drag_idx is None: return
    res = build_solver(obstacles)
    traj = extract_trajectory(res)
    print('Re-solved cost =', float(res['f']))
    update_plot(traj)
    drag_idx = None

fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

plt.show()