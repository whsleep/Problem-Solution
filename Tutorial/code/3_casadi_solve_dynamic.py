import casadi as ca
import numpy as np
import matplotlib.pyplot as plt

# ---------- 1. 问题参数 ----------
start_pose = np.array([0.0, 0.0])
end_pose   = np.array([2.0, 2.0])
obs_pose   = np.array([[0.5, 0.75],
                       [1.5, 1.25]])
safe_dis   = 0.4
n          = 50
lambda_pen = 0.5

# ---------- 2. 实时构建求解器 ----------
def build_solver(obs):       # 把当前障碍坐标传进来
    X = ca.SX.sym('X', 2 * n)
    pts = [start_pose.reshape(2, 1)]
    for k in range(n):
        pts.append(X[2*k:2*k+2])
    pts.append(end_pose.reshape(2, 1))

    obj = 0
    for i in range(1, len(pts)):
        obj += ca.norm_2(pts[i] - pts[i-1])**2
    for pt in pts:
        dists = [ca.norm_2(pt - o.reshape(2, 1)) for o in obs]
        d_min = ca.mmin(ca.vertcat(*dists))
        obj += lambda_pen * ca.fmax(0, safe_dis - d_min)**2

    nlp = {'x': X, 'f': obj}
    opts = {'ipopt.print_level': 0, 'print_time': 0}
    return ca.nlpsol('solver', 'ipopt', nlp, opts)

# ---------- 3. 初始路径 ----------
def linear_init():
    return np.tile(start_pose, (n, 1)).flatten()

def solve_now():
    solver = build_solver(obs_pose)          # 用当前障碍坐标
    res = solver(x0=linear_init(), lbx=-10, ubx=10)
    path = np.vstack([start_pose,
                      np.array(res['x']).reshape((-1, 2)),
                      end_pose])
    return path, float(res['f'])

# ---------- 4. 可视化 ----------
fig, ax = plt.subplots(figsize=(5, 5))
ax.set_aspect('equal'); ax.set_xlim(-0.2, 2.2); ax.set_ylim(-0.2, 2.2)
path_line, = ax.plot([], [], 'r-o', lw=2)
obs_scat   = ax.scatter(obs_pose[:, 0], obs_pose[:, 1],
                        s=300, c='k', picker=True)
circles = [plt.Circle(o, safe_dis, color='k', alpha=0.1) for o in obs_pose]
for c in circles: ax.add_patch(c)

def refresh_plot(path):
    path_line.set_data(path[:, 0], path[:, 1])
    obs_scat.set_offsets(obs_pose)
    for c, o in zip(circles, obs_pose):
        c.center = (o[0], o[1])
    fig.canvas.draw_idle()

full_path, cost = solve_now()
refresh_plot(full_path)
print('Initial cost =', cost)

# ---------- 5. 鼠标交互 ----------
drag_idx = None

def on_pick(event):
    global drag_idx
    if event.artist == obs_scat:
        drag_idx = event.ind[0]

def on_motion(event):
    if drag_idx is None or event.xdata is None:
        return
    obs_pose[drag_idx] = [event.xdata, event.ydata]
    refresh_plot(full_path)   # 仅移动，不立即求解

def on_release(event):
    global drag_idx
    if drag_idx is None:
        return
    full_path, cost = solve_now()
    refresh_plot(full_path)
    print('Re-solved cost =', cost)
    drag_idx = None

fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

plt.show()