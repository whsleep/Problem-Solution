import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# ---------- 1. 包裹器 ----------
def ellipse_wrapper(a, b, g_i, l_goal, phi):
    x_i, y_i = g_i
    cosθ, sinθ = l_goal
    x_w = x_i - a * cosθ
    y_w = y_i - a * sinθ
    rho = a * b / np.sqrt(b**2 * np.cos(phi)**2 + a**2 * np.sin(phi)**2)
    x = x_w + rho * (cosθ * np.cos(phi) - sinθ * np.sin(phi))
    y = y_w + rho * (sinθ * np.cos(phi) + cosθ * np.sin(phi))
    return x, y

# ---------- 2. 路径 ----------
np.random.seed(7)
path = np.cumsum(np.random.randn(5, 2) * 2, axis=0)

# ---------- 3. 画布 ----------
fig, ax = plt.subplots(figsize=(6, 6))
plt.subplots_adjust(bottom=0.25)
ax.set_aspect('equal')
ax.set_title('Ellipse Wrapper - Live')

# 初始参数
a_init, b_init, n_init = 1.2, 0.5, 64
phi = np.linspace(0, 2*np.pi, n_init)

# 绘制路径（不变）
ax.plot(path[:, 0], path[:, 1], 'ro-', lw=2, zorder=3)
lines = []          # 保存椭圆线对象

# ---------- 4. 更新函数 ----------
def update(val):
    # 读取滑块值
    a = a_slider.val
    b = b_slider.val
    n = int(n_slider.val)
    phi_new = np.linspace(0, 2*np.pi, n)

    # 清除旧椭圆
    for ln in lines:
        ln.remove()
    lines.clear()

    # 绘制新椭圆
    for i in range(len(path) - 1):
        g_i = tuple(path[i])
        vec = path[i+1] - path[i]
        l_goal = vec / np.linalg.norm(vec)
        xy = np.array([ellipse_wrapper(a, b, g_i, tuple(l_goal), p) for p in phi_new])
        ln, = ax.plot(xy[:, 0], xy[:, 1], lw=1)
        lines.append(ln)
    fig.canvas.draw_idle()

# ---------- 5. 滑块 ----------
ax_a   = plt.axes([0.2, 0.15, 0.5, 0.03])
ax_b   = plt.axes([0.2, 0.10, 0.5, 0.03])
ax_n   = plt.axes([0.2, 0.05, 0.5, 0.03])

a_slider = Slider(ax_a, 'a', 0.1, 3.0, valinit=a_init)
b_slider = Slider(ax_b, 'b', 0.1, 3.0, valinit=b_init)
n_slider = Slider(ax_n, 'n_pts', 8, 256, valinit=n_init, valfmt='%0.0f')

a_slider.on_changed(update)
b_slider.on_changed(update)
n_slider.on_changed(update)

# 首次绘制
update(None)
plt.show()