import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Circle

def bernstein(n, k, t):
    """计算n阶伯恩斯坦多项式B_{n,k}(t)"""
    if k < 0 or k > n:
        return 0
    # 计算二项式系数C(n,k)
    binomial = math.comb(n, k)  # 使用math.comb更高效
    # 计算伯恩斯坦多项式值
    return binomial * ((1 - t) ** (n - k)) * (t ** k)

def bezier_curve(control_points, num_points=100):
    """计算n阶贝塞尔曲线，n = 控制点数量 - 1"""
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

class InteractiveBezier:
    def __init__(self, control_points):
        self.control_points = np.array(control_points)
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)  # 贝塞尔曲线
        self.control_line, = self.ax.plot([], [], 'r--')      # 控制点连接线
        self.control_points_scatter = self.ax.scatter([], [], c='red', s=100, 
                                                     picker=5)  # 控制点，picker用于交互
        
        # 记录当前被拖动的点的索引
        self.dragging_point = None
        
        # 设置坐标轴
        self.ax.set_xlim(-0.5, 2.0)
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # 连接事件处理函数
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        # 初始化绘图
        self.update_plot()
    
    def update_plot(self):
        """更新图形显示"""
        # 更新控制点
        self.control_points_scatter.set_offsets(self.control_points)
        # 更新控制点连接线
        self.control_line.set_data(self.control_points[:, 0], self.control_points[:, 1])
        # 计算并更新贝塞尔曲线
        curve = bezier_curve(self.control_points)
        self.line.set_data(curve[:, 0], curve[:, 1])
        # 刷新画布
        self.fig.canvas.draw_idle()
    
    def on_press(self, event):
        """鼠标按下事件处理"""
        # 忽略不在坐标轴内的点击
        if event.inaxes != self.ax:
            return
        
        # 检查是否点击了控制点
        contains, index = self.control_points_scatter.contains(event)
        if contains:
            self.dragging_point = index['ind'][0]  # 记录被选中的点的索引
    
    def on_release(self, event):
        """鼠标释放事件处理"""
        self.dragging_point = None  # 重置拖动状态
    
    def on_motion(self, event):
        """鼠标移动事件处理"""
        # 如果没有拖动任何点或鼠标不在坐标轴内，则返回
        if self.dragging_point is None or event.inaxes != self.ax:
            return
        
        # 更新被拖动的控制点坐标
        self.control_points[self.dragging_point] = [event.xdata, event.ydata]
        # 更新图形
        self.update_plot()
    
    def show(self):
        """显示图形"""
        plt.show()

# 示例：五阶贝塞尔曲线（6个控制点）
if __name__ == "__main__":
    control_points = np.array([
        [0.0, 0.0],
        [0.2, 1.0],
        [0.8, 0.0],
        [1.0, 1.0],
        [1.5, 0.7],
        [2.0, 0.2]  # 增加一个控制点
    ])
    
    # 创建并显示交互式贝塞尔曲线
    interactive_bezier = InteractiveBezier(control_points)
    interactive_bezier.show()
