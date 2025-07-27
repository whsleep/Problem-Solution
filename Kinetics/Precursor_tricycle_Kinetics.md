# 前驱三轮底盘动力学

<img src="picture/tricycle_v1.png"  height ="400" />

状态向量为

$X=[x,y,\theta]^T$

控制输入

$u=[v_f,\gamma]^T$

其中

- $x,y$ 为全局坐标，

- $\theta$ 为车辆整体方位角

- $\gamma$ 为车辆前轮的转向角

- $v_f$ 为前轮线速度

**系统方程如下：**

$$
\begin{align}
\dot{x}&=v_fcos\gamma cos\theta\\
\dot{y}&=v_fcos\gamma sin\theta\\
\dot{\theta}&=\frac{v_f sin\gamma}{d}\\
\end{align}
$$

或者写为

$$
\begin{align}
v&=v_fcos\gamma\\
\dot{\theta}&=\frac{v_f sin\gamma}{d}\\
\end{align}
$$

$d$ 为前驱动轮与后轮轴线的垂直距离。

## 两相邻位姿间的运动学关系

<img src="picture/circle.png"  height ="400" />

给定后轮轴心相邻位姿  

$$
\mathbf{P}_1 = \begin{bmatrix} x_1 \\ y_1 \\ \theta_1 \end{bmatrix}, \quad
\mathbf{P}_2 = \begin{bmatrix} x_2 \\ y_2 \\ \theta_2 \end{bmatrix}
$$

时间间隔 $\Delta T$，且假设 $\gamma$ 恒定。

### 几何量定义
- **转向角度**：$\Delta\theta = \theta_2 - \theta_1$  

### 后轮轴心轨迹
- **弦长**：$s = \|\mathbf{P}_{2,xy}-\mathbf{P}_{1,xy}\|$  
- **转向半径**：$R = \dfrac{s}{2sin\frac{\Delta\theta}{2}}$  
- **弧长**：$L = R \cdot \Delta\theta$

### 前轮轴心轨迹
将后轮位姿平移至前轮：

$$
\mathbf{P}_i^f = \mathbf{P}_i + d\begin{bmatrix} \cos\theta_i \\ \sin\theta_i \end{bmatrix}, \quad i=1,2
$$

- **弦长**：$s^f = \|\mathbf{P}_{2,xy}^f - \mathbf{P}_{1,xy}^f\|$  
- **前轮转向半径**：$R^f = \dfrac{s^f}{2sin\frac{\Delta\theta}{2}}$  
- **前轮弧长**：$L^f = R^f \cdot \Delta\theta$

### 控制量反算
- **前轮线速度**：$v_f = \dfrac{L^f}{\Delta T}$  
- **前轮转向角**：  
 $$
  \gamma = \arctan\left(\frac{d}{L}\right)
 $$


参考:

[tricyclEbot](https://github.com/kuralme/tricyclEbot)

[tricycle_robot](https://github.com/duynamrcv/tricycle_robot)