import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import solve_banded

class CubicSpline:
    def __init__(self, P):
        """
        初始化三次样条曲线计算器
        P: 点序列{P_0, P_1, ..., P_m}，其中P_i = (x_i, y_i)
        """
        self.P = np.array(P)  # 点序列，与文档中的{P_0,P_1,...,P_m}对应
        self.m = len(self.P) - 1  # 区间数量，与文档中的m一致
        
        # 系数矩阵，与文档中的定义完全对应
        # x方向: f_i(t) = a_i t³ + b_i t² + c_i t + d_i
        self.a = None  # a_i系数
        self.b = None  # b_i系数
        self.c = None  # c_i系数
        self.d = None  # d_i系数
        
        # y方向: g_i(t) = e_i t³ + f_i t² + g_i t + h_i
        self.e = None  # e_i系数
        self.f = None  # f_i系数
        self.g = None  # g_i系数
        self.h = None  # h_i系数
        
        self.solve()  # 求解样条曲线参数
    
    def solve(self):
        """求解三次样条曲线的参数方程"""
        # 提取x和y坐标，与文档中的x_i, y_i对应
        x = self.P[:, 0]  # x_i
        y = self.P[:, 1]  # y_i
        
        # 求解x方向的系数 (a_i, b_i, c_i, d_i)
        a_x, b_x, c_x, d_x = self._solve_direction(x)
        self.a, self.b, self.c, self.d = a_x, b_x, c_x, d_x
        
        # 求解y方向的系数 (e_i, f_i, g_i, h_i)
        e_y, f_y, g_y, h_y = self._solve_direction(y)
        self.e, self.f, self.g, self.h = e_y, f_y, g_y, h_y
    
    def _solve_direction(self, points):
        """
        求解单个方向（x或y）的三次样条参数
        points: 对应x方向的{x_0, x_1, ..., x_m}或y方向的{y_0, y_1, ..., y_m}
        返回值: 对应方向的四个系数数组
        """
        m = self.m  # 区间数量[P_0,P_1], ..., [P_{m-1},P_m]
        
        # 创建三对角矩阵求解二阶导数
        ab = np.zeros((3, m + 1))
        
        # 填充矩阵（用于求解二阶导数连续条件）
        ab[1, 0] = 2.0  # 主对角线第一个元素
        ab[1, -1] = 2.0  # 主对角线最后一个元素
        
        for i in range(1, m):
            ab[0, i] = 1.0  # 上对角线
            ab[1, i] = 4.0  # 主对角线
            ab[2, i] = 1.0  # 下对角线
        
        # 右侧向量（根据二阶导数连续条件构建）
        rhs = np.zeros(m + 1)
        for i in range(1, m):
            rhs[i] = 6 * (points[i + 1] - 2 * points[i] + points[i - 1])
        
        # 自然样条边界条件：两端二阶导数为0
        # f''_0(0) = 0, f''_{m-1}(1) = 0
        rhs[0] = 0.0
        rhs[-1] = 0.0
        
        # 求解二阶导数
        M = solve_banded((1, 1), ab, rhs)
        
        # 计算每个区间的多项式系数
        a = []  # a_i系数数组
        b = []  # b_i系数数组
        c = []  # c_i系数数组
        d = []  # d_i系数数组
        
        for i in range(m):
            h = 1.0  # t在[0,1]范围内，步长为1
            
            # 根据文档中的公式计算系数
            a_i = (M[i + 1] - M[i]) / (6 * h)
            b_i = M[i] / 2
            c_i = (points[i + 1] - points[i]) / h - (M[i + 1] + 2 * M[i]) * h / 6
            d_i = points[i]
            
            a.append(a_i)
            b.append(b_i)
            c.append(c_i)
            d.append(d_i)
        
        return np.array(a), np.array(b), np.array(c), np.array(d)
    
    def evaluate(self, num_points_per_segment=100):
        """
        计算样条曲线上的点
        每个区间[P_i,P_{i+1}]内使用参数t∈[0,1]
        """
        curve_points = []
        
        for i in range(self.m):
            # 在每个区间上均匀取t值，t∈[0,1]
            t = np.linspace(0, 1, num_points_per_segment)
            
            # 根据文档中的参数方程计算x和y
            # x = f_i(t) = a_i t³ + b_i t² + c_i t + d_i
            x = self.a[i] * t**3 + self.b[i] * t**2 + self.c[i] * t + self.d[i]
            
            # y = g_i(t) = e_i t³ + f_i t² + g_i t + h_i
            y = self.e[i] * t**3 + self.f[i] * t**2 + self.g[i] * t + self.h[i]
            
            # 添加到曲线点列表
            curve_points.extend(np.column_stack((x, y)))
        
        return np.array(curve_points)

def visualize_spline(P, num_points_per_segment=100):
    """可视化三次样条曲线和控制点"""
    # 创建样条曲线
    spline = CubicSpline(P)
    curve_points = spline.evaluate(num_points_per_segment)
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制曲线和控制点
    ax.plot(curve_points[:, 0], curve_points[:, 1], 'b-', linewidth=2, label='三次样条曲线')
    ax.plot(P[:, 0], P[:, 1], 'r--', alpha=0.5, label='控制点连线')
    ax.scatter(P[:, 0], P[:, 1], c='red', s=100, label='控制点')
    
    ax.grid(True)
    ax.set_aspect('equal')
    ax.set_title('三次样条曲线')
    ax.legend()
    
    # 设置坐标轴范围
    x_min, x_max = np.min(P[:, 0]) - 1, np.max(P[:, 0]) + 1
    y_min, y_max = np.min(P[:, 1]) - 1, np.max(P[:, 1]) + 1
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    plt.show()

# 示例用法
if __name__ == "__main__":
    # 点序列{P_0, P_1, ..., P_m}
    P = np.array([
        [0, 0],    # P_0
        [2, 3],    # P_1
        [5, 2],    # P_2
        [7, 5],    # P_3
        [10, 3]    # P_4
    ])
    
    # 可视化样条曲线
    visualize_spline(P)
    