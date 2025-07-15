import casadi as ca
import numpy as np
import matplotlib.pyplot as plt

# ---------- 1. 参数 ----------
start   = np.array([0.0, 0.0, -np.pi])
end     = np.array([2.0, 2.0, np.pi/3])
obs     = np.array([[0.5, 0.75], [1.5, 1.25]])
n       = 50
vmax    = 1.0
wmax    = 1.5
rmin    = 0.5
safe_dis= 0.3

# ---------- 2. 决策变量 ----------
x  = ca.SX.sym('x', n)
y  = ca.SX.sym('y', n)
θ  = ca.SX.sym('θ', n)
ΔT = ca.SX.sym('ΔT', n+1)
w  = ca.vertcat(x, y, θ, ΔT)


# ---------- 3. 轨迹点列表 ----------
pts = [ca.DM(start)]
for k in range(n):
    pts.append(ca.vertcat(x[k], y[k], θ[k]))
pts.append(ca.DM(end))          # 起点/终点是常量，中间是符号变量

# ---------- 4. 辅助角度计算 ----------
def norm_angle(a):
    return ca.atan2(ca.sin(a), ca.cos(a))

# ---------- 5. 目标函数 ----------
res = []
for i in range(n+1):
    p0, p1   = pts[i][:2], pts[i+1][:2]
    th0, th1 = pts[i][2], pts[i+1][2]
    seg = ca.norm_2(p1 - p0)
    dt  = ΔT[i]

    # 1. 路径长度
    res.append(seg**2)
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

# ---------- 6. 求解 ----------
nlp = {'x': w, 'f': 0.5 * ca.dot(residuals, residuals)}
solver = ca.nlpsol('solver', 'ipopt', nlp,
                   {'ipopt.print_level': 0, 'print_time': 1})

# ---------- 7. 初值 ----------
x0 = np.hstack([
        np.linspace(start[0], end[0], n+2)[1:-1],
        np.linspace(start[1], end[1], n+2)[1:-1],
        np.linspace(start[2], end[2], n+2)[1:-1],
        np.full(n+1, 0.2)
])

# ---------- 8. 求解 ----------
res = solver(x0=x0, lbx=-10, ubx=10)
w_opt = np.array(res['x']).flatten()
print('Cost =', float(res['f']))

# ---------- 9. 可视化（圆 + 箭头长度=圆半径） ----------
x_opt  = w_opt[:n]
y_opt  = w_opt[n:2*n]
θ_opt  = w_opt[2*n:3*n]
dt_opt = w_opt[3*n:]

# 构造完整轨迹（起点 + 中间点 + 终点）
full = np.vstack([start,
                  np.column_stack([x_opt, y_opt, θ_opt]),
                  end])

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect('equal')
ax.set_xlim(-0.2, 2.2)
ax.set_ylim(-0.2, 2.2)

# 圆和箭头参数
pt_radius = 0.06          # 圆半径 = 箭头长度
head_scale = 0.4          # 箭头头部相对宽度

# 颜色区分
colors = ['tab:blue'] + ['tab:red'] * n + ['tab:green']

# 绘制每个轨迹点
for k, (x, y, th, col) in enumerate(zip(full[:,0], full[:,1], full[:,2], colors)):
    # 圆
    circle = plt.Circle((x, y), pt_radius, color=col, alpha=0.2)
    ax.add_patch(circle)
    # 箭头（长度 = 圆半径）
    dx = pt_radius * np.cos(th)
    dy = pt_radius * np.sin(th)
    ax.arrow(x, y, dx, dy,
             head_width=head_scale * pt_radius,
             fc='k', ec='k')

# 障碍与安全圆
ax.scatter(obs[:,0], obs[:,1], c='k', s=300, label='obstacle')
for o in obs:
    ax.add_patch(plt.Circle(o, safe_dis, color='k', alpha=0.1))

# 直线参考
ax.plot([start[0], end[0]], [start[1], end[1]], 'k--', alpha=0.3, label='straight')
ax.legend()
plt.tight_layout()
plt.show()