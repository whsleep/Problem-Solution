import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.widgets import Button

# 设置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

class LocalGoalWrapperVisualizer:
    def __init__(self):
        self.control_points: np.ndarray = np.array([])  # 存储控制点
        self.path: np.ndarray = np.array([])  # 存储密集平滑路径
        self.goal_index: int = 5  # 默认目标点索引
        self.radius: float = 1.0  # 默认半径
        
        # 创建图形和轴
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        self.fig.subplots_adjust(bottom=0.1, left=0.05, right=0.95, top=0.95)
        
        # 设置标题和轴标签
        self.ax.set_title("局部目标包裹器可视化")
        self.ax.set_xlabel("X 坐标")
        self.ax.set_ylabel("Y 坐标")
        
        # 创建按钮
        self.button_ax = plt.axes([0.85, 0.02, 0.1, 0.04])
        self.button = Button(self.button_ax, '重新生成路径')
        self.button.on_clicked(self.generate_random_path)
        
        # 生成初始随机路径
        self.generate_random_path()
        
        # 连接事件处理
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.fig.canvas.mpl_connect('scroll_event', self.on_mouse_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # 显示图形
        plt.show()
    
    def generate_random_path(self, event=None) -> None:
        """生成随机平滑路径"""
        try:
            self.ax.clear()
            
            # 生成随机控制点 (6-12个点)
            num_control_points = np.random.randint(6, 13)
            self.control_points = np.random.rand(num_control_points, 2) * 10
            
            # 确保控制点之间的距离不过近
            for i in range(1, len(self.control_points)):
                while np.linalg.norm(self.control_points[i] - self.control_points[i-1]) < 1.5:
                    self.control_points[i] = np.random.rand(2) * 10
            
            # 使用贝塞尔曲线生成密集平滑路径
            self.path = self.generate_bezier_curve(self.control_points, num_points=300)
            
            # 重置目标点索引
            self.goal_index = min(10, len(self.path) - 2)
            
            # 绘制路径
            self.draw_visualization()
            
        except Exception as e:
            print(f"生成路径时出错: {e}")
    
    def generate_bezier_curve(self, control_points: np.ndarray, num_points: int = 100) -> np.ndarray:
        """
        使用贝塞尔曲线生成密集平滑路径
        
        参数:
        control_points -- 控制点数组
        num_points -- 生成的路径点数量
        
        返回:
        密集平滑路径点数组
        """
        try:
            n = len(control_points) - 1
            if n < 1:
                return np.array([])
                
            t_values = np.linspace(0, 1, num_points)
            bezier_points = np.zeros((num_points, 2))
            
            for i, t in enumerate(t_values):
                point = np.zeros(2)
                for j in range(n + 1):
                    # 计算贝塞尔基函数
                    basis = self._bernstein_polynomial(n, j, t)
                    point += basis * control_points[j]
                bezier_points[i] = point
            
            return bezier_points
        except Exception as e:
            print(f"生成贝塞尔曲线时出错: {e}")
            return np.array([])
    
    def _bernstein_polynomial(self, n: int, j: int, t: float) -> float:
        """计算贝塞尔曲线的基函数"""
        try:
            return np.math.comb(n, j) * (t ** j) * ((1 - t) ** (n - j))
        except Exception as e:
            print(f"计算贝塞尔基函数时出错: {e}")
            return 0.0
    
    def draw_visualization(self) -> None:
        """绘制可视化内容"""
        try:
            self.ax.clear()
            
            # 绘制密集平滑路径
            path_line, = self.ax.plot(self.path[:, 0], self.path[:, 1], 'b-', linewidth=2, label='平滑路径')
            
            # 绘制控制点（半透明显示）
            control_points, = self.ax.plot(self.control_points[:, 0], self.control_points[:, 1], 'ro', markersize=8, alpha=0.5, label='控制点')
            
            # 确保目标点索引有效
            if self.goal_index < 0:
                self.goal_index = 0
            if self.goal_index >= len(self.path) - 1:
                self.goal_index = len(self.path) - 2
            
            # 获取当前目标点
            current_goal = self.path[self.goal_index]
            
            # 计算目标向量 l_goal
            next_point = self.path[self.goal_index + 1]
            delta = next_point - current_goal
            distance = np.linalg.norm(delta)
            
            if distance > 1e-10:
                l_goal = delta / distance
            else:
                l_goal = np.array([0, 0])
            
            # 计算包裹器圆心 (使用 g_i - r * l_goal)
            circle_center = current_goal - self.radius * l_goal
            
            # 绘制目标点（突出显示）
            goal_point, = self.ax.plot(current_goal[0], current_goal[1], 'go', markersize=12, label=f'临时目标点 g_i')
            
            # 绘制目标向量
            arrow = self.ax.arrow(
                current_goal[0], current_goal[1], 
                l_goal[0] * self.radius, l_goal[1] * self.radius, 
                head_width=0.2, head_length=0.3, fc='y', ec='y', 
                label='目标向量 l_goal'
            )
            
            # 绘制圆形包裹器（只显示边缘）
            circle = patches.Circle(circle_center, self.radius, fill=False, color='orange', linewidth=2, linestyle='-', label='圆形包裹器')
            self.ax.add_patch(circle)
            
            # 绘制圆心
            center_point, = self.ax.plot(circle_center[0], circle_center[1], 'mo', markersize=6, label='包裹器圆心')
            
            # 添加使用说明
            self.add_usage_info()
            
            # 添加图例
            self.add_legend()
            
            # 添加网格
            self.ax.grid(True)
            
            # 设置坐标轴比例相等，确保圆形显示为圆形
            self.ax.axis('equal')
            
            # 设置轴范围，确保有足够空间显示包裹器
            min_x, max_x = np.min(self.path[:, 0]), np.max(self.path[:, 0])
            min_y, max_y = np.min(self.path[:, 1]), np.max(self.path[:, 1])
            padding = max(self.radius * 1.2, 1.5)
            
            self.ax.set_xlim(min_x - padding, max_x + padding)
            self.ax.set_ylim(min_y - padding, max_y + padding)
            
            # 更新标题显示当前参数
            self.ax.set_title(f"局部目标包裹器可视化 - 半径 r = {self.radius:.2f}, 目标点索引 = {self.goal_index}")
            
            # 更新画布
            self.fig.canvas.draw_idle()
            
        except Exception as e:
            print(f"绘制可视化内容时出错: {e}")
    
    def add_usage_info(self) -> None:
        """添加使用说明文本框"""
        info_text = (
            "使用说明:\n"
            "- 点击: 选择目标点\n"
            "- 滚轮: 调整包裹器半径\n"
            "- 键盘 ↑: 增大半径\n"
            "- 键盘 ↓: 减小半径\n"
            "- 键盘 →: 目标点后移\n"
            "- 键盘 ←: 目标点前移\n"
            "- 键盘 r: 重新生成路径"
        )
        
        self.ax.text(
            0.02, 0.98, info_text, transform=self.ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=9
        )
    
    def add_legend(self) -> None:
        """添加优化的图例"""
        # 获取当前轴上的所有艺术家和标签
        handles, labels = self.ax.get_legend_handles_labels()
        
        # 创建图例，使用两列显示，调整位置和大小
        self.ax.legend(
            handles, labels,
            loc='upper right',
            bbox_to_anchor=(1.0, 1.0),
            ncol=2,
            fontsize=9,
            frameon=True,
            framealpha=0.8,
            shadow=True,
            borderpad=0.5
        )
    
    def on_mouse_click(self, event) -> None:
        """鼠标点击事件处理"""
        try:
            if event.inaxes != self.ax:
                return
            
            # 查找最近的路径点
            min_distance = float('inf')
            closest_index = -1
            
            for i, point in enumerate(self.path):
                distance = np.sqrt((event.xdata - point[0])**2 + (event.ydata - point[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_index = i
            
            # 如果点击足够接近某个点，且该点不是最后一个点，则更新目标点索引
            if min_distance < 0.5 and closest_index < len(self.path) - 1:
                self.goal_index = closest_index
                self.draw_visualization()
                
        except Exception as e:
            print(f"处理鼠标点击事件时出错: {e}")
    
    def on_mouse_scroll(self, event) -> None:
        """鼠标滚轮事件处理"""
        try:
            if event.inaxes != self.ax:
                return
            
            # 调整半径
            if event.button == 'up':
                self.radius = min(self.radius + 0.1, 5.0)  # 最大半径限制
            else:
                self.radius = max(self.radius - 0.1, 0.2)  # 最小半径限制
            
            # 重绘
            self.draw_visualization()
            
        except Exception as e:
            print(f"处理鼠标滚轮事件时出错: {e}")
    
    def on_key_press(self, event) -> None:
        """键盘按键事件处理"""
        try:
            # 检查是否按下了有效的按键
            if event.key == 'up':
                self.radius = min(self.radius + 0.1, 5.0)
            elif event.key == 'down':
                self.radius = max(self.radius - 0.1, 0.2)
            elif event.key == 'right':
                self.goal_index = min(self.goal_index + 1, len(self.path) - 2)
            elif event.key == 'left':
                self.goal_index = max(self.goal_index - 1, 0)
            elif event.key == 'r':
                self.generate_random_path()
            else:
                return  # 如果按下的不是有效按键，则不做任何处理
            
            # 重绘
            self.draw_visualization()
            
        except Exception as e:
            print(f"处理键盘事件时出错: {e}")

# 创建并运行可视化器
if __name__ == "__main__":
    visualizer = LocalGoalWrapperVisualizer()
