# 具有控制屏障函数的多面体之间的安全关键控制与避障规划

## 优化问题描述

### 离散时间动态系统

- 状态为 $x \in \mathbb{X} \subseteq \mathbb{R}^n$
- 输入为 $u \in \mathbb{U} \subseteq \mathbb{R}^m$
- 系统动态方程为：$x_{k+1} = f(x_k, u_k)$

其中 $x_k := x(k)$，$u_k := u(k)$，$k \in \mathbb{Z}_+$，$\mathbb{U}$ 是一个紧集，且 $f$ 是连续的。

> 紧集：紧集是有界的闭集，$[-1,3]$ 是有界闭集即紧集

### 离散时间控制障碍函数（DCBFs）

障碍物规避的安全性是通过其轨迹相对于一个连通集合的不变性来定义的。

换句话说，如果动态系统相对于集合 $S \subseteq \mathbb{X}$ 是安全的，

那么从集合 $S$ 内部开始的任何轨迹都会一直保持在集合 $S$ 内部。

集合 $S$ 被定义为连续函数 $h: \mathbb{X} \rightarrow \mathbb{R}$ 的0-超水平集：
$$
 S := \{ x \in \mathbb{X} \subseteq \mathbb{R}^n \mid h(x) \geq 0 \} 
$$
称 $S$ 为安全集，它表示障碍物外部的区域。

> 对于一个函数 $h: \mathbb{X} \rightarrow \mathbb{R}$，其0-超水平集是指所有使得函数值大于或等于0的点的集合。

如果对于所有 $x \in S$ 和 $u \in \mathbb{U}$，满足以下条件：
$$
h(f(x, u)) - \gamma(x) h(x) \geq 0
$$

其中 $\gamma(x) < 1$，则称 $h$ 为离散时间控制障碍函数（DCBF）。

满足条件上述条件意味着 

$$
h(x_{k+1}) \geq \gamma(x_k) h(x_k)
$$

即DCBF的下界以指数速率衰减，衰减率为 $\gamma$。

给定一个 $\gamma(x)$ 的选择，我们记 $K(x)$ 为：

$$
K(x) := \{ u \in \mathbb{U} \mid h(f(x, u)) - \gamma(x) h(x) \geq 0 \}
$$
