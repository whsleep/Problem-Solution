# 埃尔米特-辛普森配点法（Hermite–Simpson Collocation Method）

## 特点

与梯形配点法相比，Hermite–Simpson 配点法的关键差异在于：

- **近似阶数更高**：用**分段二次函数**近似目标函数和系统动力学（而非梯形法的分段线性函数），因此精度更高（通常为四阶精度）
- **状态轨迹特性**：状态轨迹被表示为**三次埃尔米特样条（cubic Hermite spline）**，其一阶导数（即动力学）连续，进一步提升了轨迹的光滑性

## Hermite–Simpson 配点法：积分的离散化

### 辛普森求积的原理

要推导辛普森求积公式中单个子区间的积分近似，需通过二次多项式插值和定积分计算完成。以下是详细步骤：

- 步骤 1：变量替换（标准化区间）
  考虑单个子区间 $[t_k, t_{k+1}]$，长度为 $h_k = t_{k+1} - t_k$。

  引入标准化变量 $s$（将区间映射到 $[0,1]$）：
  $ s = \frac{\tau - t_k}{h_k} \quad \Rightarrow \quad \tau = t_k + s \cdot h_k $

  其中 $s \in [0,1]$，微分关系为：
  $ d\tau = h_k \cdot ds $

  区间内三个关键节点的函数值：

  $s=0$（$\tau = t_k$）：$w(\tau) = w_k$

  $s=0.5$（$\tau = t_{k+1/2}$）：$w(\tau) = w_{k+1/2}$

  $s=1$（$\tau = t_{k+1}$）：$w(\tau) = w\_{k+1}$

- 步骤 2：构造二次插值多项式 $P(s)$
  用二次多项式 $P(s)$ 逼近被积函数，形式为：

  $ P(s) = \alpha s^2 + \beta s + \gamma $

  其中 $\alpha, \beta, \gamma$ 为待求系数，需满足插值条件

- 步骤 3：通过插值条件求解系数

  当 $s=0$ 时：$P(0) = w_k \quad \Rightarrow \quad \gamma = w_k$

  当 $s=0.5$ 时：$P(0.5) = w_{k+1/2} \quad \Rightarrow \quad 0.25\alpha + 0.5\beta + \gamma = w_{k+1/2}$

  当 $s=1$ 时：$P(1) = w_{k+1} \quad \Rightarrow \quad \alpha + \beta + \gamma = w_{k+1}$

  求解过程：
  代入 $\gamma = w_k$ 后，化简得方程组：

  $$
  \begin{cases}
  0.25\alpha + 0.5\beta = w_{k+1/2} - w_k \\
  \alpha + \beta = w_{k+1} - w_k
  \end{cases}
  $$

  解得：

  $$
    \begin{align}
    \alpha &= 2w_k + 2w_{k+1} - 4w_{k+1/2}\\
    \beta &= 4w_{k+1/2} - 3w_k - w_{k+1}
    \end{align}
  $$

- 步骤 4：计算二次多项式的积分

  单个子区间的积分近似为：

  $$
  \int_{t_k}^{t_{k+1}} w(\tau) d\tau \approx \int_{0}^{1} P(s) \cdot h_k \, ds
  $$

  计算 $P(s)$ 在 $[0,1]$ 上的积分：

  $$
  \int_{0}^{1} P(s) ds = \int_{0}^{1} (\alpha s^2 + \beta s + \gamma) ds = \frac{\alpha}{3} + \frac{\beta}{2} + \gamma
  $$

- 步骤 5：代入系数并化简

  将 $\alpha, \beta, \gamma$ 代入积分结果，合并同类项后得：

  $$
  \int_{0}^{1} P(s) ds = \frac{w_k + 4w_{k+1/2} + w\_{k+1}}{6}
  $$

最终结果，单个子区间的积分近似为：

$$
\int_{t_k}^{t_{k+1}} w(\tau) d\tau \approx \frac{h_k}{6} \left( w_k + 4w_{k+1/2} + w\_{k+1} \right)
$$

## 系统动力学的离散化

系统动力学 $\dot{x} = f(t, x, u)$ 的离散化同样基于积分形式，但引入了中点约束以匹配二次近似，最终形成两个配点约束

### 动力学的积分形式

对动力学方程在区间 $[t_k, t_{k+1}]$ 积分，得到状态变化与动力学积分的关系：  
$$x_{k+1} - x_k = \int_{t_k}^{t_{k+1}} f(\tau, x(\tau), u(\tau)) d\tau \tag{4.2}$$

### 辛普森求积近似积分

用辛普森求积公式近似右边的积分，得到第一个配点约束：

$$
x_{k+1} - x_k = \frac{h_k}{6} \left( f_k + 4f_{k+1/2} + f_{k+1} \right)
$$

其中

- $f_k = f(t_k, x_k, u_k)$
- $f_{k+1} = f(t_{k+1}, x_{k+1}, u_{k+1})$
- $f_{k+1/2} = f(t_{k+1/2}, x_{k+1/2}, u_{k+1/2})$

### 中点状态的插值约束

中点动力学 $f_{k+1/2}$ 依赖于中点状态 $x_{k+1/2}$，

但 $x_{k+1/2}$ 并非已知的决策变量（初始仅已知端点 $x_k, x_{k+1}$）

因此需要第二个约束：通过**三次埃尔米特样条插值**推导中点状态的表达式：

$$
x_{k+1/2} = \frac{1}{2} \left( x_k + x_{k+1} \right) + \frac{h_k}{8} \left( f_k - f_{k+1} \right)
$$
