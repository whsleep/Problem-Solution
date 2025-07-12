import casadi as ca
import numpy as np
import matplotlib.pyplot as plt

# ---------- 1. 问题参数 ----------
start_pose = np.array([0.0, 0.0])
end_pose   = np.array([2.0, 2.0])
obs_pose   = np.array([[0.5, 0.75],
                       [1.5, 1.25]])
safe_dis   = 0.5
n          = 25         # 中间点个数
dim        = 2
lambda_pen = 0.5      # 安全距离惩罚权重

# ---------- 2. 决策变量 ----------

# 变量向量 X = [x1,y1,x2,y2,...,xn,yn]
X = ca.SX.sym('X', 2 * n)

# 辅助：把向量拆成点序列
pts = [start_pose.reshape(2, 1)]
for k in range(n):
    pts.append(X[2*k:2*k+2])
pts.append(end_pose.reshape(2, 1))

# ---------- 3. 目标函数 ----------
obj = 0
# 3.1 路径长度
for i in range(1, len(pts)):
    seg = ca.norm_2(pts[i] - pts[i-1])
    obj += seg**2                       # 原始长度

# 3.2 安全距离惩罚
for pt in pts:
    dists = [ca.norm_2(pt - obs.reshape(2, 1)) for obs in obs_pose]
    d_min = ca.mmin(ca.vertcat(*dists))
    barrier = ca.fmax(0, safe_dis - d_min)
    obj += lambda_pen * barrier**2

# ---------- 4. NLP 求解 ----------
nlp = {'x': X, 'f': obj}
opts = {'ipopt.print_level': 1, 'print_time': 1}
solver = ca.nlpsol('solver', 'ipopt', nlp, opts)

# ---------- 5. 初始猜测 ----------
def linear_init():
    t = np.linspace(0, 1, n + 2)[1:-1]  # 去掉首尾
    # path = start_pose + t[:, None] * (end_pose - start_pose)
    path = np.tile(start_pose, (n, 1)) # 全部初始化为起点
    return path.flatten()

x0 = linear_init()

# ---------- 6. 求解 ----------
res = solver(x0=x0,
             lbx=-10, ubx=10)  # 简单上下界
theta_opt = np.array(res['x']).reshape(-1, 2)

# ---------- 7. 结果 ----------
full_path = np.vstack([start_pose, theta_opt, end_pose])
print('Cost =', float(res['f']))

# ---------- 8. 可视化 ----------
plt.figure(figsize=(5, 5))
plt.plot(full_path[:, 0], full_path[:, 1], 'ro-', label='path')
plt.scatter(obs_pose[:, 0], obs_pose[:, 1],
            s=300, c='k', marker='o', label='obstacle')
for obs in obs_pose:
    circle = plt.Circle(obs, safe_dis, color='k', alpha=0.1)
    plt.gca().add_patch(circle)
plt.plot([0, 2], [0, 2], 'k--', alpha=0.3, label='straight')
plt.axis('equal'); plt.legend(); plt.tight_layout(); plt.show()