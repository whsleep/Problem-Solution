import irsim
import sys
import numpy as np
from collections import namedtuple

# 构造环境
env = irsim.make("path_track.yaml", save_ani=False, display=True)

# 从csv提取参考路径
ref_path = np.genfromtxt('./ovalpath.csv', delimiter=',', skip_header=1)
xyz_matrix = ref_path[:, 0:3]
formatted_path_list = []
for waypoint in xyz_matrix:
    column_vector = waypoint.reshape((3, 1))
    formatted_path_list.append(column_vector)
env.draw_trajectory(formatted_path_list, traj_type='-k') # plot path


class LQRLateralController():
    def __init__(
            self,
            wheel_base: float = 2.5, # [m] wheel_base
            Q: np.ndarray = np.diag([1.0, 1.0]), # weight matrix for state variables
            R: np.ndarray = np.diag([1.0]), # weight matrix for control inputs
            ref_path: np.ndarray = np.array([[0.0, 0.0, 0.0, 1.0], [10.0, 0.0, 0.0, 1.0]]),
    ) -> None:
        """initialize lqr controller for path-tracking"""
        # 轴距
        self.l = wheel_base # [m] wheel base

        # 权重矩阵
        self.Q = Q # weight matrix for state variables
        self.R = R # weight matrix for control inputs

        # 获取参考路径
        self.ref_path = ref_path
        self.prev_waypoints_idx = 0

    def calc_control_input(self, observed_x: np.ndarray,velocity: float, delta_t: float) -> float:
        """calculate control input"""

        # 当前实际位置
        x = observed_x[0]
        y = observed_x[1]
        yaw = observed_x[2]
        beta = observed_x[3]
        v = velocity

        # 获取参考点信息
        _, ref_x, ref_y, ref_yaw, _ = self._get_nearest_waypoint(x, y, update_prev_idx=True)
        if self.prev_waypoints_idx >= self.ref_path.shape[0]-1:
            print("[ERROR] Reached the end of the reference path.")
            raise IndexError

        # 计算车辆在参考路径的左侧或右侧
        ## algorithm : http://www.hptown.com/ucad/Ufb00009.htm
        x1, y1 = ref_x, ref_y
        x2, y2 = ref_x + 1.0 * np.cos(ref_yaw), ref_y + 1.0 * np.sin(ref_yaw)
        # 参考路径的方向向量
        vx, vy = x2 - x1, y2 - y1
        # 车辆位置相对于参考路径起点的向量
        wx, wy =  x - x1,  y - y1
        # 叉乘判断车辆位置，主要根据 sin(theta)正负判断
        s = vx * wy - vy * wx # s>0 : vehicle is on the left of the path, s<0 : vehicle is on the left of the path,

        # 计算横向偏移
        y_e = np.sign(s) * np.sqrt((ref_x-x)**2 + (ref_y-y)**2) # lateral error
        # 计算航向误差
        theta_e = yaw - ref_yaw # heading error
        # 限制范围
        theta_e = np.arctan2(np.sin(theta_e), np.cos(theta_e)) # normalize heading error to [-pi, pi]

        # define A, B matrices and solve algebraic riccati equation to get feedback gain matrix f for LQR
        A = np.array([
            [0, v],
            [0, 0],
        ])
        B = np.array([
            [0],
            [v / (self.l * (np.cos(beta))**2)],
        ])

        # 计算最优控制律
        P = self.solve_are(A, B, self.Q, self.R)
        f = np.linalg.inv(self.R) @ B.T @ P
        steer_cmd = -f @ np.array([y_e, theta_e])

        return steer_cmd[0].real # TODO : why does steer_cmd have imaginary part?

    def solve_are(self, A, B, Q, R):
        """solve algebraic riccati equation with the Arimoto-Potter algorithm
        Ref: https://qiita.com/trgkpc/items/8210927d5b035912a153
        """
        # define hamiltonian matrix
        H = np.block([[A, -B @ np.linalg.inv(R) @ B.T],
                      [-Q , -A.T]])

        # solve eigenvalue problem
        eigenvalue, w = np.linalg.eig(H)

        # define Y and Z, which are used to calculate P
        Y_, Z_ = [], []
        n = len(w[0])//2

        # sort eigenvalues
        index_array = sorted([i for i in range(2*n)],
            key = lambda x:eigenvalue[x].real)

        # choose n eigenvalues which have smaller real part
        for i in index_array[:n]:
            Y_.append(w.T[i][:n])
            Z_.append(w.T[i][n:])
        Y = np.array(Y_).T
        Z = np.array(Z_).T

        # calculate P
        if np.linalg.det(Y) != 0:
            return Z @ np.linalg.inv(Y)
        else:
            print("Warning: Y is not regular matrix. Result may be wrong!") # TODO : need to consider mathmatical meaning of this case.
            return Z @ np.linalg.pinv(Y)

    def _get_nearest_waypoint(self, x: float, y: float, update_prev_idx: bool = False):
        """search the closest waypoint to the vehicle on the reference path"""
        # 仅仅检索前方一定范围的点以节省计算时间
        SEARCH_IDX_LEN = 100 # [points] forward search range
        # 记录上次最近点的索引以加速搜索
        prev_idx = self.prev_waypoints_idx
        dx = [x - ref_x for ref_x in self.ref_path[prev_idx:(prev_idx + SEARCH_IDX_LEN), 0]]
        dy = [y - ref_y for ref_y in self.ref_path[prev_idx:(prev_idx + SEARCH_IDX_LEN), 1]]
        d = [idx ** 2 + idy ** 2 for (idx, idy) in zip(dx, dy)]
        min_d = min(d)
        # 在已有检索上递增索引
        nearest_idx = d.index(min_d) + prev_idx

        # 获取参考点信息
        ref_x = self.ref_path[nearest_idx,0]
        ref_y = self.ref_path[nearest_idx,1]
        ref_yaw = self.ref_path[nearest_idx,2]
        ref_v = self.ref_path[nearest_idx,3]

        # 更新最近点索引
        if update_prev_idx:
            self.prev_waypoints_idx = nearest_idx

        return nearest_idx, ref_x, ref_y, ref_yaw, ref_v



def main():
    CONSTANT_V = 5.0
    robot_info = env.get_robot_info()

    # 初始化LQR控制器
    lqr_lat_controller = LQRLateralController(
        wheel_base = robot_info.wheelbase, # [m] wheel base
        Q = np.diag([20.0, 30.0]), # weight matrix for state variables
        R = np.diag([15.0]), # weight matrix for control inputs
        ref_path = ref_path, # ndarray, size is <num_of_waypoints x 2>
    )

    for i in range(5000):    
        # 获取当前实际状态
        current_state = env.get_robot_state().reshape(-1)
        # 计算控制输入
        steer_input = lqr_lat_controller.calc_control_input(observed_x=current_state, velocity=CONSTANT_V ,delta_t=0.1)
        steer_input = np.clip(steer_input, -1.0, 1.0)
        action_input_list =  np.array([CONSTANT_V, steer_input])
        env.step(action=action_input_list) # step once to initialize
        env.render(show_traj=True, show_trail=True)
        if env.robot.arrive:
            env.end(ending_time=i*0.1, suffix='.gif')
            break

    
if __name__ == '__main__':
    main()