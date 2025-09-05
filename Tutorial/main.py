import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from matplotlib.patches import Polygon

# 设置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号

class EnhancedInteractivePolarCloud:
    def __init__(self):
        # 参数设置
        self.num_points = 50  # 点云数量
        self.base_radius = 8  # 基础半径
        self.noise_level = 0.3  # 噪声水平
        self.original_center = np.array([5, 3])  # 初始中心
        self.current_center = self.original_center.copy()  # 当前中心（可拖动）
        
        # 生成圆形分布的极坐标点云
        self.original_polar = self.generate_circular_polar_points()
        
        # 转换为全局直角坐标
        self.global_cartesian = self.polar_to_global_cartesian(self.original_polar)
        
        # 初始化最近点和约束相关参数
        self.closest_point = None
        self.closest_dist = 0
        self.constraint_visible = False  # 约束可见性属性
        
        # 创建图形
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig.subplots_adjust(bottom=0.1)  # 留出底部空间放按钮
        self.fig.suptitle('带约束的极坐标点云可视化', fontsize=16)
        
        # 添加按钮
        self.add_buttons()
        
        # 初始化图形元素
        self.setup_plot_elements()
        
        # 连接事件处理
        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.dragging = False
        
        plt.show()
    
    def generate_circular_polar_points(self):
        """生成圆形分布的极坐标点云（带少量噪声）"""
        angles = np.linspace(0, 2*np.pi, self.num_points, endpoint=False)
        radii = self.base_radius + np.random.normal(0, self.noise_level, self.num_points)
        radii = np.maximum(0.1, radii)
        return np.column_stack((radii, angles))
    
    def polar_to_global_cartesian(self, polar_points):
        """将极坐标点转换为全局直角坐标"""
        radii, angles = polar_points[:, 0], polar_points[:, 1]
        x = self.original_center[0] + radii * np.cos(angles)
        y = self.original_center[1] + radii * np.sin(angles)
        return np.column_stack((x, y))
    
    def update_polar_from_center(self):
        """根据当前中心更新极坐标表示"""
        rel_x = self.global_cartesian[:, 0] - self.current_center[0]
        rel_y = self.global_cartesian[:, 1] - self.current_center[1]
        
        radii = np.sqrt(rel_x**2 + rel_y**2)
        angles = np.arctan2(rel_y, rel_x)
        
        # 找到最近点
        self.closest_dist = np.min(radii)
        self.closest_point = self.global_cartesian[np.argmin(radii)]
        
        return np.column_stack((radii, angles))
    
    def setup_plot_elements(self):
        """设置绘图元素"""
        # 极坐标连接线
        self.lines, = self.ax.plot([], [], 'gray', linestyle='--', alpha=0.6)
        
        # 点云
        self.points, = self.ax.plot([], [], 'bo', markersize=6)
        
        # 最近点标记
        self.closest_marker, = self.ax.plot([], [], 'g', markersize=8, marker='d')
        
        # 半空间约束可视化
        self.constraint_line, = self.ax.plot([], [], 'r-', linewidth=2)
        # 初始化多边形为一个退化的多边形（避免空坐标错误）
        self.halfspace_patch = Polygon([[0,0],[0,0],[0,0],[0,0]], facecolor='pink', alpha=0.2)
        self.ax.add_patch(self.halfspace_patch)
        
        # 中心点
        self.center_marker, = self.ax.plot([], [], 'r', markersize=10, marker='*')
        
        # 信息文本
        self.info_text = self.ax.text(0.05, 0.95, '', transform=self.ax.transAxes,
                                      verticalalignment='top', 
                                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 更新绘图数据
        self.update_plot()
        
        # 设置坐标轴
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.axis('equal')
        self.ax.grid(True)
        self.ax.set_title('拖动红色中心点观察变化（绿色为最近点）')
    
    def add_buttons(self):
        """添加交互按钮"""
        # 重置按钮
        ax_reset = plt.axes([0.65, 0.02, 0.15, 0.05])
        self.btn_reset = widgets.Button(ax_reset, '重置中心')
        self.btn_reset.on_clicked(self.reset_center)
        
        # 半空间约束开关按钮
        ax_constraint = plt.axes([0.45, 0.02, 0.15, 0.05])
        self.btn_constraint = widgets.Button(ax_constraint, '显示约束')
        self.btn_constraint.on_clicked(self.toggle_constraint)
    
    def toggle_constraint(self, event):
        """切换半空间约束显示状态"""
        self.constraint_visible = not self.constraint_visible
        self.btn_constraint.label.set_text('隐藏约束' if self.constraint_visible else '显示约束')
        self.update_plot()
    
    def update_halfspace_constraint(self):
        """更新半空间约束可视化"""
        if not self.constraint_visible or self.closest_point is None:
            # 使用退化多边形（四个相同的点）替代空列表，避免shape错误
            self.constraint_line.set_data([], [])
            self.halfspace_patch.set_xy([[0,0], [0,0], [0,0], [0,0]])
            return
        
        # 计算约束线（垂直于中心点到最近点的连线）
        dx = self.current_center[0] - self.closest_point[0]
        dy = self.current_center[1] - self.closest_point[1]
        
        # 法向量归一化
        norm = np.sqrt(dx**2 + dy**2)
        if norm < 1e-6:
            self.constraint_line.set_data([], [])
            self.halfspace_patch.set_xy([[0,0], [0,0], [0,0], [0,0]])
            return
            
        dx_norm = dx / norm
        dy_norm = dy / norm
        
        # 约束线方向向量（垂直于法向量）
        perp_dx = -dy_norm
        perp_dy = dx_norm
        
        # 生成约束线的两个端点（延长线）
        extend = self.base_radius * 0.8
        p1 = self.closest_point + np.array([perp_dx * extend, perp_dy * extend])
        p2 = self.closest_point - np.array([perp_dx * extend, perp_dy * extend])
        
        # 生成半空间多边形
        p3 = p2 + np.array([dx_norm * extend, dy_norm * extend])
        p4 = p1 + np.array([dx_norm * extend, dy_norm * extend])
        
        # 更新约束线和半空间区域
        self.constraint_line.set_data([p1[0], p2[0]], [p1[1], p2[1]])
        self.halfspace_patch.set_xy([p1, p2, p3, p4])
    
    def update_plot(self):
        """更新绘图内容"""
        # 更新极坐标信息（同时找到最近点）
        self.update_polar_from_center()
        
        # 更新点的位置
        self.points.set_data(self.global_cartesian[:, 0], self.global_cartesian[:, 1])
        
        # 更新中心点
        self.center_marker.set_data([self.current_center[0]], [self.current_center[1]])
        
        # 更新最近点
        self.closest_marker.set_data([self.closest_point[0]], [self.closest_point[1]])
        
        # 更新极坐标连接线
        if len(self.global_cartesian) > 0:
            x = np.hstack([
                np.repeat(self.current_center[0], self.num_points),
                self.global_cartesian[:, 0],
                np.full(self.num_points, np.nan)
            ]).reshape(3, -1).ravel('F')
            
            y = np.hstack([
                np.repeat(self.current_center[1], self.num_points),
                self.global_cartesian[:, 1],
                np.full(self.num_points, np.nan)
            ]).reshape(3, -1).ravel('F')
            
            self.lines.set_data(x, y)
        
        # 更新半空间约束
        self.update_halfspace_constraint()
        
        # 更新信息文本
        self.info_text.set_text(
            f'中心坐标: ({self.current_center[0]:.1f}, {self.current_center[1]:.1f})\n'
            f'最近点距离: {self.closest_dist:.2f}\n'
            f'最近点坐标: ({self.closest_point[0]:.1f}, {self.closest_point[1]:.1f})'
        )
        
        # 调整坐标轴范围
        all_x = np.append(self.global_cartesian[:, 0], self.current_center[0])
        all_y = np.append(self.global_cartesian[:, 1], self.current_center[1])
        padding = self.base_radius * 0.2
        self.ax.set_xlim(all_x.min() - padding, all_x.max() + padding)
        self.ax.set_ylim(all_y.min() - padding, all_y.max() + padding)
        
        # 刷新画布
        self.fig.canvas.draw_idle()
    
    def on_press(self, event):
        """鼠标按下事件"""
        if event.inaxes != self.ax:
            return
        
        # 检查是否点击了中心点
        dx = event.xdata - self.current_center[0]
        dy = event.ydata - self.current_center[1]
        if np.sqrt(dx**2 + dy**2) < 0.5:  # 点击范围
            self.dragging = True
    
    def on_release(self, event):
        """鼠标释放事件"""
        self.dragging = False
    
    def on_motion(self, event):
        """鼠标移动事件"""
        if self.dragging and event.inaxes == self.ax:
            # 更新中心点位置
            self.current_center = np.array([event.xdata, event.ydata])
            self.update_plot()
    
    def reset_center(self, event):
        """重置中心点到初始位置"""
        self.current_center = self.original_center.copy()
        self.update_plot()

if __name__ == "__main__":
    # 创建并显示交互式可视化
    app = EnhancedInteractivePolarCloud()
