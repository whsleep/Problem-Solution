import casadi as ca
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ---------- 1. 参数 ----------
start   = np.array([0.0, 0.0, -np.pi])
end     = np.array([2.0, 2.0, np.pi/3])
obs     = np.array([[0.5, 0.75], [1.5, 1.25],[0.5, 1.75], [1.5, 0.85]])
n       = 50
vmax    = 1.0
wmax    = 1.5
rmin    = 0.5
safe_dis= 0.3

# ---------- 2. 实时求解器 ----------
def build_solver(obs_now):
    x  = ca.SX.sym('x', n)
    y  = ca.SX.sym('y', n)
    θ  = ca.SX.sym('θ', n)
    ΔT = ca.SX.sym('ΔT', n+1)
    w  = ca.vertcat(x, y, θ, ΔT)

    pts = [ca.DM(start)]
    for k in range(n):
        pts.append(ca.vertcat(x[k], y[k], θ[k]))
    pts.append(ca.DM(end))

    def norm_angle(a):
        return ca.atan2(ca.sin(a), ca.cos(a))

    res = []
    for i in range(n+1):
        p0, p1   = pts[i][:2], pts[i+1][:2]
        th0, th1 = pts[i][2], pts[i+1][2]
        seg = ca.norm_2(p1 - p0)
        dt  = ΔT[i]

        # 1. 路径长度
        res.append(seg)
        # 2. 时间
        res.append(dt)
        # 3. 安全距离（仅内部点）
        if 1 <= i <= n:
            dists = [ca.norm_2(pts[i][:2] - o) for o in obs]
            dmin  = ca.mmin(ca.vertcat(*dists))
            res.append(ca.fmax(0, safe_dis - dmin))
        # 4. 速度
        v = seg / (dt + 1e-6)
        res.append(ca.fmax(0, ca.fabs(v) - vmax))
        # 5. 角速度
        dth = norm_angle(th1 - th0)
        ω   = dth / (dt + 1e-6)
        res.append(ca.fmax(0, ca.fabs(ω) - wmax))
        # 6. 非完整运动学
        l0 = ca.vertcat(ca.cos(th0), ca.sin(th0))
        l1 = ca.vertcat(ca.cos(th1), ca.sin(th1))
        d  = p1 - p0
        cross = (l0[0]+l1[0])*d[1] - (l0[1]+l1[1])*d[0]
        res.append(10*cross)
        # 7. 转弯半径
        # 计算转弯半径（考虑速度方向）
        r = v / (ca.fabs(ω) + 1e-6)
        # 确保转弯半径的绝对值大于等于最小转弯半径
        res.append(10*ca.fmax(0, ca.fabs(r) - rmin))

    residuals = ca.vertcat(*res)
    nlp = {'x': w, 'f': 0.5 * ca.dot(residuals, residuals)}
    opts = {'ipopt.print_level': 0, 'print_time': 1}
    return ca.nlpsol('solver', 'ipopt', nlp, opts)

# ---------- 3. 初值 ----------
def init_guess():
    return np.hstack([
        np.linspace(start[0], end[0], n+2)[1:-1],
        np.linspace(start[1], end[1], n+2)[1:-1],
        np.linspace(start[2], end[2], n+2)[1:-1],
        np.full(n+1, 0.2)
    ])

def solve_now():
    sol = build_solver(obs)(x0=init_guess(), lbx=-10, ubx=10)
    w_opt = np.array(sol['x']).flatten()
    full  = np.vstack([start,
                       np.column_stack([w_opt[:n],
                                        w_opt[n:2*n],
                                        w_opt[2*n:3*n]]),
                       end])
    return full, float(sol['f'])

# ---------- 4. 可视化 ----------
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect('equal')
ax.set_xlim(-0.2, 2.2)
ax.set_ylim(-0.2, 2.2)

pt_radius = 0.06
head_scale = 0.4

circles = []
arrows  = []
for _ in range(n + 2):
    c = plt.Circle((0, 0), pt_radius, color='tab:red', alpha=0.2)
    ax.add_patch(c)
    circles.append(c)
    ar = ax.arrow(0, 0, 0, 0,
                  head_width=head_scale * pt_radius,
                  fc='k', ec='k')
    arrows.append(ar)
circles[0].set_color('tab:blue')
circles[-1].set_color('tab:green')

obs_scat = ax.scatter(obs[:, 0], obs[:, 1], s=300, c='k', picker=True)
safe_circs = [plt.Circle(o, safe_dis, color='k', alpha=0.1) for o in obs]
for c in safe_circs:
    ax.add_patch(c)

def update_plot(full):
    for k, (x, y, th) in enumerate(full):
        circles[k].center = (x, y)
        arrows[k].remove()
        dx = pt_radius * np.cos(th)
        dy = pt_radius * np.sin(th)
        arrows[k] = ax.arrow(x, y, dx, dy,
                             head_width=head_scale * pt_radius,
                             fc='k', ec='k')
    obs_scat.set_offsets(obs)
    for c, o in zip(safe_circs, obs):
        c.center = o
    fig.canvas.draw_idle()

full, cost = solve_now()
print('Initial cost =', cost)
update_plot(full)

# ---------- 5. 鼠标交互 ----------
drag_idx = None

def on_pick(event):
    global drag_idx
    if event.artist == obs_scat:
        drag_idx = event.ind[0]

def on_motion(event):
    if drag_idx is None or event.xdata is None:
        return
    obs[drag_idx] = [event.xdata, event.ydata]
    obs_scat.set_offsets(obs)
    for c, o in zip(safe_circs, obs):
        c.center = o
    fig.canvas.draw_idle()

def on_release(event):
    global drag_idx
    if drag_idx is None:
        return
    full, cost = solve_now()
    print('Re-solved cost =', cost)
    update_plot(full)
    drag_idx = None
    print(obs)

fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

plt.show()