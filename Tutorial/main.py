import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. 构造一条示例路径（可替换为自己的路径）
# -------------------------------------------------
p = np.array([
    [0.0, 0.0],
    [2.0, 0.5],
    [4.0, 2.0],
    [5.0, 4.0],
    [4.0, 6.0],
    [2.0, 7.0],
    [0.0, 7.5]
])

# -------------------------------------------------
# 2. 计算每个 g_i 对应的包裹器圆心
# -------------------------------------------------
r = 0.8  # 包裹器半径

centers = []
for i in range(len(p) - 1):
    g_i      = p[i]
    g_ip1    = p[i + 1]
    vec      = g_ip1 - g_i
    d        = np.linalg.norm(vec) + 1e-9  # 避免除零
    l_goal   = vec / d                     # 单位向量
    w        = g_i - r * l_goal            # 圆心
    centers.append(w)

centers = np.array(centers)

# -------------------------------------------------
# 3. 可视化
# -------------------------------------------------
plt.figure(figsize=(6, 4))
plt.plot(p[:, 0], p[:, 1], 'o-', label='path p')
for c in centers:
    circle = plt.Circle(c, r, color='orange', fill=False, ls='--')
    plt.gca().add_patch(circle)
plt.plot(centers[:, 0], centers[:, 1], 'rx', label='wrapper centers')
plt.axis('equal')
plt.legend()
plt.title('Local Goal Wrapper Demo')
plt.show()