"""
interactive_ellipse_wrapper.py
Python ≥3.7
pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

# ---------------- 路径 ----------------
# 任意折线路径：可改为自己的
path = np.array([
    [0.0, 0.0],
    [2.0, 1.0],
    [4.0, 0.5],
    [6.0, 2.0],
    [8.0, 1.0]
])

# 取 g_i 为第 i 个路径点（这里固定 i=2，可改）
i = 2
g_i = path[i]
g_ip1 = path[i+1]
alpha = 1.5

# 方向向量
theta_g = np.arctan2(g_ip1[1] - g_i[1], g_ip1[0] - g_i[0])
l_vec = np.array([np.cos(theta_g), np.sin(theta_g)])

# ---------------- 图形 ----------------
fig, ax = plt.subplots(num="Interactive ellipse wrapper")
ax.set_aspect('equal')
ax.plot(path[:, 0], path[:, 1], 'ko-')
ax.plot(*g_i, 'bo', label='g_i')
# 设置坐标轴范围
plt.xlim((-5, 10))
plt.ylim((-5, 10))

# 机器人位置：可拖动
pr_plot, = ax.plot(0.5, 0.5, 'ro')
pr_point = np.array([0.5, 0.5])

# 椭圆
ellipse_patch = Ellipse((0, 0), 0, 0,
                        angle=np.degrees(theta_g),
                        fill=False, color='r', lw=2)
ax.add_patch(ellipse_patch)

def update_ellipse(pr,alpha):
    """根据当前 pr 重新计算并绘制椭圆"""
    lr = np.linalg.norm(pr - g_i)
    theta_r = np.arctan2(pr[1] - g_i[1], pr[0] - g_i[0])

    a = alpha*lr * np.cos(theta_r - theta_g)
    b = alpha*lr * np.sin(theta_r - theta_g)
    a = abs(a)
    b = abs(b)


    # 椭圆中心
    center = g_i - a * l_vec

    # 更新椭圆
    ellipse_patch.set_center(center)
    ellipse_patch.width  = abs(2*a) if abs(2*a) > 1e-3 else 1e-3
    ellipse_patch.height = abs(2*b) if abs(2*b) > 1e-3 else 1e-3
    ellipse_patch.angle  = np.degrees(theta_g)

    fig.canvas.draw_idle()

update_ellipse(pr_point,alpha)   # 首次绘制

# ---------------- 鼠标交互 ----------------
dragging = False

def on_press(event):
    global dragging
    if event.inaxes != ax:
        return
    # 检查点击是否在红点内
    if np.linalg.norm([event.xdata - pr_point[0], event.ydata - pr_point[1]]) < 0.2:
        dragging = True

def on_motion(event):
    if not dragging or event.inaxes != ax:
        return
    pr_point[0] = event.xdata
    pr_point[1] = event.ydata
    pr_plot.set_data([pr_point[0]], [pr_point[1]])
    update_ellipse(pr_point,alpha)

def on_release(event):
    global dragging
    dragging = False

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

ax.legend()
plt.show()