import numpy as np
import matplotlib.pyplot as plt
import math

def bernstein(n, k, t):
    """
    计算n阶伯恩斯坦多项式B_{n,k}(t)
    B_{n,k}(t) = C(n,k) * (1-t)^(n-k) * t^k
    其中C(n,k)是二项式系数n!/(k!(n-k)!)
    """
    # 计算二项式系数C(n,k)
    binomial = math.factorial(n) / (math.factorial(k) * math.factorial(n - k))
    # 计算伯恩斯坦多项式值
    return binomial * ((1 - t) ** (n - k)) * (t ** k)

def bezier_curve(control_points, num_points=100):
    """
    计算n阶贝塞尔曲线，n = 控制点数量 - 1
    公式：S(t) = Σ B_{n,k}(t) * P_k，其中k从0到n
    """
    n = len(control_points) - 1  # 曲线阶数
    t_values = np.linspace(0, 1, num_points)  # t从0到1均匀取值
    curve = []
    
    for t in t_values:
        point = np.zeros(2)  # 初始化曲线点坐标
        for k in range(n + 1):
            # 累加计算：每个控制点乘以对应的伯恩斯坦多项式权重
            point += bernstein(n, k, t) * control_points[k]
        curve.append(point)
    
    return np.array(curve)

# 示例：四阶贝塞尔曲线（5个控制点）
control_points_3rd = np.array([
    [0.0, 0.0],
    [0.2, 1.0],
    [0.8, 0.0],
    [1.0, 1.0],
    [1.5, 0.7]
])
curve_3rd = bezier_curve(control_points_3rd)
plt.figure(figsize=(8, 6))
plt.plot(control_points_3rd[:, 0], control_points_3rd[:, 1], 'r--')
plt.scatter(control_points_3rd[:, 0], control_points_3rd[:, 1], c='red', s=100)
plt.plot(curve_3rd[:, 0], curve_3rd[:, 1], 'b-', linewidth=2)
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.grid(True)
plt.axis('equal')
plt.show()
