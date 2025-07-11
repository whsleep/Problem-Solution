import casadi as ca
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# 定义问题参数
start_pose = np.array([0, 0])
end_pose = np.array([2, 2])
obs_pose = np.array([[0.5, 0.75], [1.5, 1.25]])
safe_dis = 0.4
size = 3
lambda_1 = 500  # 安全距离约束权重
lambda_2 = 300  # 相邻路径点距离约束权重

# 计算起始点的直线距离
l = np.linalg.norm(end_pose - start_pose)
l_min = l / size
l_max = 1.2 * l / size
l_mid = (l_min + l_max)/2.0

# 定义决策变量
X = ca.SX.sym('X', size * 2)
trajectory = ca.reshape(X, size, 2)

# 将 start_pose 和 end_pose 转换为 Casadi 二维矩阵
start_pose_ca = ca.DM(start_pose).T.reshape((1, 2))
end_pose_ca = ca.DM(end_pose).T.reshape((1, 2))

# 垂直拼接
full_trajectory = ca.vertcat(start_pose_ca, trajectory, end_pose_ca)

# 1. 路径长度项
path_length_terms = []
for i in range(1, size + 2):
    dx = full_trajectory[i, 0] - full_trajectory[i - 1, 0]
    dy = full_trajectory[i, 1] - full_trajectory[i - 1, 1]
    path_length_terms.append(dx**2 + dy**2)
path_length_terms_sx = ca.vertcat(*path_length_terms)

# 2. 安全距离约束项
safety_terms = []
for i in range(size + 2):
    point = full_trajectory[i, :]
    min_dist_to_obs = ca.fmin(*[ca.norm_2(point - ca.DM(obs).T.reshape((1, 2))) for obs in obs_pose])
    safety_violation = ca.fmax(0, safe_dis - min_dist_to_obs)
    safety_terms.append(safety_violation**2)
safety_terms_sx = ca.vertcat(*safety_terms)

# 3. 相邻路径点距离约束项
adjacent_distance_terms = []
for i in range(size + 1):
    dist = ca.norm_2(full_trajectory[i + 1, :] - full_trajectory[i, :])
    violation = ca.fmax(0, ca.fabs(l_min - dist) - l_mid)
    adjacent_distance_terms.append(violation**2)
adjacent_distance_terms_sx = ca.vertcat(*adjacent_distance_terms)

# 定义目标函数
objective = ca.sum1(path_length_terms_sx) + lambda_1 * ca.sum1(safety_terms_sx) 
# objective = ca.sum1(path_length_terms_sx) + lambda_1 * ca.sum1(safety_terms_sx) + lambda_2 * ca.sum1(adjacent_distance_terms_sx)


# 定义 NLP 问题
nlp = {'x': X, 'f': objective}

# 创建求解器
solver = ca.nlpsol('solver', 'ipopt', nlp)

# 生成线性插值的初始猜测
def generate_linear_initial_guess():
    initial_guess = np.zeros((size, 2))
    for i in range(size):
        ratio = (i + 1) / (size + 1)
        point = start_pose + ratio * (end_pose - start_pose)
        initial_guess[i] = point
    return initial_guess

# 可视化轨迹
def visualize_trajectory(result, initial_guess):
    """可视化轨迹规划结果（支持多个障碍物）"""
    # 提取优化后的轨迹点
    trajectory = result['x'].full().reshape(-1, 2)  # 注意Casadi结果需用.full()转换为numpy数组
    full_trajectory = np.vstack((start_pose, trajectory, end_pose))
    
    # 提取初始猜测轨迹
    initial_trajectory = initial_guess.reshape(-1, 2)
    initial_full = np.vstack((start_pose, initial_trajectory, end_pose))
    
    # 创建图形
    plt.figure(figsize=(12, 10))
    
    # 绘制初始猜测轨迹（灰色虚线）
    plt.plot(initial_full[:, 0], initial_full[:, 1], 'o--', color='gray', alpha=0.5, label='Initial Guess (Linear)')
    
    # 绘制优化后的轨迹
    plt.plot(full_trajectory[:, 0], full_trajectory[:, 1], 'o-', color='blue', label='Optimized Trajectory')
    
    # 绘制起点和终点
    plt.plot(start_pose[0], start_pose[1], 'go', markersize=12, label='Start')
    plt.plot(end_pose[0], end_pose[1], 'ro', markersize=12, label='End')
    
    # 绘制所有障碍物及其安全区域
    for obs in obs_pose:
        # 安全区域（虚线圆）
        circle = Circle(obs, safe_dis, color='r', fill=False, linestyle='--')
        plt.gca().add_patch(circle)
        # 障碍物本身（黑色方块）
        plt.plot(obs[0], obs[1], 'ks', markersize=12, label='Obstacle' if obs is obs_pose[0] else "")
    
    # 添加标签和图例
    plt.grid(True)
    plt.axis('equal')
    plt.xlabel('X Coordinate', fontsize=12)
    plt.ylabel('Y Coordinate', fontsize=12)
    plt.title(f'Trajectory Planning with Obstacles (Inserted Points: {size}, Safety Distance: {safe_dis}m)', fontsize=14)
    plt.legend(fontsize=12)
    
    # 计算并显示优化结果指标
    final_cost = float(result['f'])  # 转换为浮点数显示
    
    # 修改这里，使用正确的返回状态键
    plt.text(0.05, 0.90, f'Final Cost: {final_cost:.6f}', transform=plt.gca().transAxes, fontsize=12)
    
    plt.show()

# 主程序执行
if __name__ == '__main__':
    initial_guess = generate_linear_initial_guess()
    initial_guess_flat = initial_guess.flatten()
    
    # 求解 NLP 问题
    result = solver(x0=initial_guess_flat)
    
    # 可视化结果
    visualize_trajectory(result, initial_guess_flat)