# Levenberg-Marquardt (LM) 算法

## 非线性最小二乘问题

观测向量为 $\mathrm{y}=\{y_1,\cdots,y_m\}^T$

待估计的系统参数为 $\mathrm{x}=\{x_1,\cdots,x_n\}^T$

> 这里仅考虑 $m>n$ 的超定问题，通常​​没有精确解​​，但可寻求​​最小二乘解​​（使残差平方和最小），希望用​​足够多的观测数据​​（m较大）来​​可靠地估计​​一组​​数量相对较少​​的参数（n较小），以避免过拟合并提高估计的稳健性。大多数最小二乘算法（如高斯-牛顿法、LM算法）都默认处理这种情况。

理想系统模型为 $\mathrm{y}=\mathrm{f}(\mathrm{x})$

> $\mathrm{f}(x)=[f_1(\mathrm{x}),\cdots,f_m(\mathrm{x})]^T$

实际中必然不会满足 $\mathrm{y}=\mathrm{f}(\mathrm{x})$, 所以 $||\mathrm{y}-\mathrm{f}(\mathrm{x})||_2\neq 0$

所以非线性最小二乘问题为：($\mathrm{f}(\mathrm{x})$ 为非线性函数)

$$
\underset{\mathrm{x}}{min}\quad g(\mathrm{x}) = \frac{1}{2}\sum_{i=1}^m [r_i(\mathrm{x})]^2=\frac{1}{2}\sum_{i=1}^m [y_i-f_i(\mathrm{x})]^2=\frac{1}{2}||r(\mathrm{x})||_2^2
$$

其中 
- $r_i(x)$ 为残差函数
- $||\cdot||_2$范数（欧几里得范数），即向量元素平方和的平方根

该形式的目的就是寻找 $x$ 使得残差最小。

## 原理

在优化非线性最小二乘问题时，常用的方法包括高斯-牛顿算法和梯度下降法：

**高斯-牛顿算法**：利用目标函数的二阶泰勒展开，忽略二阶导数项，适用于接近线性的问题，收敛速度较快，但对初始值敏感，可能在远离最优解时表现不佳。

**梯度下降法**：依赖于目标函数的一阶导数信息，具有全局收敛性，但收敛速度较慢，尤其在接近最优解时。

$Levenberg-Marquardt$ 算法通过引入阻尼因子 $\lambda$，结合了上述两种方法的优点，实现了更为稳健和高效的优化过程。

## 推导

残差函数 $r_i(x)$ 的泰勒展开为

$$
S(\mathrm{x}+\Delta \mathrm{x})≈S(\mathrm{x})+J^T\Delta \mathrm{x}+\frac{1}{2}\Delta \mathrm{x}^TH\Delta \mathrm{x}
$$

- $J$ 为雅可比矩阵,$J_{i,j}=\frac{\sigma f_i}{\sigma x_j}$
- $H$ 为海森矩阵，近似为 $J^TJ$ 
# 参考

- [Python 实现 LM 算法（Levenberg-Marquardt）](https://jishuzhan.net/article/1835561546999140353)