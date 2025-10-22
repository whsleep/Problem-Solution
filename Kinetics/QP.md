# 线性化 QP

**系统方程如下：**

$$
\begin{align}
\dot{x}&=v_fcos\gamma cos\theta\\
\dot{y}&=v_fcos\gamma sin\theta\\
\dot{\theta}&=\frac{v_f sin\gamma}{d}\\
\end{align}
$$

- $x,y$ 为全局坐标，

- $\theta$ 为车辆整体方位角

- $\gamma$ 为车辆前轮的转向角

- $v_f$ 为前轮线速度

## MPC 问题形式

$$
\begin{align}
&\underset{\Delta t_0, \Delta t_1,...,\Delta t_{N-1}}
{\underset{\mathrm{x}[0],\mathrm{x}[1],...,\mathrm{x}[N]}{\underset{\mathrm{u}[0],\mathrm{u}[1],...,\mathrm{u}[N-1]}
{min}}}
 J_f\big(\mathrm{x[N]}\big)+\sum_{k=0}^{N-1} l\big(\mathrm{x}[k],\mathrm{u}[k]\big)\Delta t_k\\
&\mathrm{subject~to}\\
&\qquad \mathrm{x}[0]=\mathrm{x}_s,\quad\mathrm{x}[N]=\mathrm{x}_f\\
&\qquad \big(\mathrm{u}[k+1]-\mathrm{u}[k+1]\big)\Delta t^{-1}\in\mathrm{U_d}\\
&\qquad \mathrm{u[k]}\in \mathrm{U}\\
&\qquad \Delta t_{min} \le\Delta t_0 \le \Delta t_{max}, \quad \Delta t_k = \Delta t_{k+1}\\
&\qquad \phi(\mathrm{x}[k+1], \mathrm{x}[k], \mathrm{u}[k], \Delta t_k)=0,\quad k=0,1,...,N-1
\end{align}
$$