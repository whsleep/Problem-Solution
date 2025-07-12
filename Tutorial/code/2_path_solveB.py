import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import time

"""
问题参数
    起点位置, 目标点位置, 障碍序列, 安全距离, 插入路径点数量
"""
start_pose = np.array([0, 0])
end_pose = np.array([2, 2])
obs_pose = np.array([[0.5, 0.75], [1.5, 1.25]])
safe_dis = 0.3
size = 20

def compute_safety_violation(trajectory):
    """计算路径点到所有障碍的最小距离，评估安全约束违反程度"""
    min_dist = float('inf')
    for point in trajectory:
        # 计算到每个障碍物的距离，取最小值
        dist_to_obs = min(np.linalg.norm(point - obs) for obs in obs_pose)
        if dist_to_obs < min_dist:
            min_dist = dist_to_obs
    return min_dist - safe_dis  # 小于0表示存在安全约束违反

def objective_function(params, lambda_weight=100, lambda_dist=100):
    """构建最小二乘问题的目标函数，现在包含相邻路径点距离约束"""
    # 重塑参数为轨迹点(一维->二维)
    trajectory = params.reshape(-1, 2)
    
    # 构建完整轨迹（包括起点和终点）
    full_trajectory = np.vstack((start_pose, trajectory, end_pose))
    
    # 直线距离（用于计算l_min和l_max）
    total_distance = np.linalg.norm(end_pose - start_pose)
    l_min = total_distance / size
    l_max = 1.5 * total_distance / size
    l_mid = (l_min + l_max)/2.0
    
    # 1. 路径长度项（相邻点之间的欧氏距离）
    path_length_terms = []
    for i in range(1, len(full_trajectory)):
        dx = full_trajectory[i, 0] - full_trajectory[i-1, 0]
        dy = full_trajectory[i, 1] - full_trajectory[i-1, 1]
        segment_distance = np.sqrt(dx**2 + dy**2)
        path_length_terms.append(segment_distance)
    
    # 2. 安全距离约束项（对每个障碍物都计算）
    safety_terms = []
    for point in full_trajectory:
        # 计算到每个障碍物的距离，取最小距离（最危险的障碍物）
        min_dist_to_obs = min(np.linalg.norm(point - obs) for obs in obs_pose)
        # 当最小距离小于安全距离时施加惩罚
        safety_violation = max(0, safe_dis - min_dist_to_obs)
        safety_terms.append(safety_violation)
    
    # 3. 相邻路径点距离约束项
    distance_constraint_terms = []
    for i in range(1, len(full_trajectory)):
        dx = full_trajectory[i, 0] - full_trajectory[i-1, 0]
        dy = full_trajectory[i, 1] - full_trajectory[i-1, 1]
        segment_distance = np.sqrt(dx**2 + dy**2)
        
        # 计算约束违反程度
        ind_cos = l_mid - segment_distance
        
        # 添加约束项
        distance_constraint_terms.append(ind_cos)
    
    # 4. 组合所有项
    residuals = []
    residuals.extend(path_length_terms)  # 路径长度项
    residuals.extend([lambda_weight * s for s in safety_terms])  # 安全约束项（带权重）
    residuals.extend([lambda_dist * d for d in distance_constraint_terms])  # 相邻距离约束项（带权重）
    
    return np.array(residuals)

def visualize_trajectory(result, initial_guess):
    """可视化轨迹规划结果（支持多个障碍物）"""
    # 提取优化后的轨迹点
    trajectory = result.x.reshape(-1, 2)
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
    
    # 绘制相邻路径点距离
    for i in range(1, len(full_trajectory)):
        midpoint_x = (full_trajectory[i-1, 0] + full_trajectory[i, 0]) / 2
        midpoint_y = (full_trajectory[i-1, 1] + full_trajectory[i, 1]) / 2
        segment_distance = np.linalg.norm(full_trajectory[i] - full_trajectory[i-1])
        plt.text(midpoint_x, midpoint_y, f'{segment_distance:.2f}', fontsize=9, color='red')
    
    # 绘制起点和终点
    plt.plot(start_pose[0], start_pose[1], 'go', markersize=12, label='Start')
    plt.plot(end_pose[0], end_pose[1], 'ro', markersize=12, label='End')
    
    # 绘制所有障碍物及其安全区域
    for obs in obs_pose:
        # 安全区域（虚线圆）
        circle = plt.Circle(obs, safe_dis, color='r', fill=False, linestyle='--')
        plt.gca().add_patch(circle)
        # 障碍物本身（黑色方块）
        plt.plot(obs[0], obs[1], 'ks', markersize=12, label='Obstacle' if obs is obs_pose[0] else "")
    
    # 添加标签和图例
    plt.grid(True)
    plt.axis('equal')
    plt.xlabel('X Coordinate', fontsize=12)
    plt.ylabel('Y Coordinate', fontsize=12)
    plt.title(f'Trajectory Planning with Multiple Constraints (Inserted Points: {size}, Safety Distance: {safe_dis}m)', fontsize=14)
    plt.legend(fontsize=12)
    
    # 显示优化结果
    safety_violation = compute_safety_violation(full_trajectory)
    
    # 计算相邻路径点距离约束的违反程度
    distance_violation = 0
    total_distance = np.linalg.norm(end_pose - start_pose)
    l_min = total_distance / size
    l_max = 1.5 * total_distance / size
    
    for i in range(1, len(full_trajectory)):
        segment_distance = np.linalg.norm(full_trajectory[i] - full_trajectory[i-1])
        below_min = max(0, l_min - segment_distance)
        above_max = max(0, segment_distance - l_max)
        distance_violation += below_min + above_max
    
    plt.text(0.05, 0.95, f'Optimization Status: {result.message}', transform=plt.gca().transAxes, fontsize=12)
    plt.text(0.05, 0.90, f'Function Evaluations: {result.nfev}', transform=plt.gca().transAxes, fontsize=12)
    plt.text(0.05, 0.85, f'Final Cost: {result.cost:.6f}', transform=plt.gca().transAxes, fontsize=12)
    plt.text(0.05, 0.80, f'Safety Violation: {safety_violation:.6f}', transform=plt.gca().transAxes, fontsize=12)
    plt.text(0.05, 0.75, f'Distance Violation: {distance_violation:.6f}', transform=plt.gca().transAxes, fontsize=12)
    
    plt.show()

def generate_linear_initial_guess():
    """生成线性插值的初始猜测"""
    initial_guess = np.zeros((size, 2))
    # for i in range(size):
    #     ratio = (i + 1) / (size + 1)
    #     point = start_pose + ratio * (end_pose - start_pose)
    #     initial_guess[i] = point
    return initial_guess

if __name__ == '__main__':
    # 生成初始猜测（线性插值）
    initial_guess = generate_linear_initial_guess()
    initial_guess_flat = initial_guess.flatten()

    # 记录优化开始时间
    start_time = time.time()
    # 执行优化
    result = least_squares(
        objective_function,
        initial_guess_flat,
        method='trf',
        args=(5, 1),  # 分别对应lambda_weight和lambda_dist
        verbose=1,
        ftol=1e-8,
        xtol=1e-8,
        max_nfev=1000,
        bounds=(-10, 10)
    )
    # 计算优化耗时
    optimization_time = time.time() - start_time

    trajectory = result.x.reshape(-1, 2)
    full_trajectory = np.vstack((start_pose, trajectory, end_pose))
    safety_violation = compute_safety_violation(full_trajectory)
    
    print(f"Safety Violation: {safety_violation:.6f}")
    print(f"Optimization Time: {optimization_time:.4f} seconds")
    
    if result is not None:
        print("\nFinal Optimization Result:")
        print("Status:", result.message)
        print("Iterations:", result.nfev)
        print("Objective Function Value:", result.cost)
        visualize_trajectory(result, initial_guess)
    else:
        print("Optimization failed, no feasible solution found")