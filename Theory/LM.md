### 一、实例背景：指数模型拟合
我们要拟合的非线性模型是：$y = a \cdot e^{b \cdot x}$，其中$a$和$b$是待估参数（即$\theta = [a, b]^T$）。

假设我们有观测数据$(x_i, y_i)$，其中$y_i$是带有噪声的观测值，我们的目标是找到最优参数$\theta^* = [a^*, b^*]^T$，使残差平方和最小。


### 二、核心概念与代码对应关系

#### 1. 残差函数（Residuals）
理论定义：$r_i(\theta) = y_i - f(x_i, \theta)$，其中$f(x_i, \theta) = a \cdot e^{b \cdot x_i}$

代码实现：
```python
def residuals(self, x_data, y_data, theta):
    """计算残差向量"""
    return y_data - self.func(x_data, theta)

# 模型函数
def func(x, theta):
    return theta[0] * np.exp(theta[1] * x)
```

对于我们的例子，残差具体为：$r_i(\theta) = y_i - a \cdot e^{b \cdot x_i}$


#### 2. 雅可比矩阵（Jacobian Matrix）
理论定义：$J_{i,j} = \frac{\partial f(x_i, \theta)}{\partial \theta_j}$

对于指数模型，雅可比矩阵元素为：
- $J_{i,0} = \frac{\partial f}{\partial a} = e^{b \cdot x_i}$
- $J_{i,1} = \frac{\partial f}{\partial b} = a \cdot x_i \cdot e^{b \cdot x_i}$

代码实现：
```python
def jacobian(x, theta):
    J = np.zeros((len(x), len(theta)))
    J[:, 0] = np.exp(theta[1] * x)  # 对a的偏导数
    J[:, 1] = theta[0] * x * np.exp(theta[1] * x)  # 对b的偏导数
    return J
```


#### 3. 目标函数与梯度
目标函数：$g(\theta) = \frac{1}{2} \sum_{i=1}^m r_i^2(\theta)$

梯度（一阶导数）：$\nabla g(\theta) = -J^T \cdot r(\theta)$


#### 4. 海森矩阵近似
理论近似：$H \approx J^T \cdot J$

代码实现：
```python
# 计算Hessian近似
H = jacobian.T @ jacobian
```

对于我们的例子，海森矩阵是一个2×2矩阵：
$$H \approx \begin{bmatrix} 
\sum (e^{b \cdot x_i})^2 & \sum (e^{b \cdot x_i} \cdot a \cdot x_i \cdot e^{b \cdot x_i}) \\
\sum (a \cdot x_i \cdot e^{b \cdot x_i} \cdot e^{b \cdot x_i}) & \sum (a \cdot x_i \cdot e^{b \cdot x_i})^2 
\end{bmatrix}$$


### 三、Levenberg-Marquardt算法迭代过程
LM算法通过以下步骤迭代求解最优参数：

1. **初始化**：设置初始参数$\theta_0 = [a_0, b_0]^T$和初始阻尼因子$\lambda$

2. **计算残差和雅可比矩阵**：
   ```python
   residuals = self.model.residuals(x_data, y_data, theta)
   jacobian = self.model.jacobian_matrix(x_data, theta)
   ```

3. **计算参数更新量**：
   $$\Delta\theta = (J^T J + \lambda I)^{-1} J^T r$$
   代码实现：
   ```python
   delta_theta = np.linalg.inv(H + lambda_factor * np.eye(H.shape[0])) @ jacobian.T @ residuals
   ```

4. **更新参数**：
   ```python
   theta_new = theta + delta_theta
   ```

5. **自适应调整阻尼因子**：
   - 如果残差减小（目标函数降低），接受新参数并减小$\lambda$
   - 如果残差增大（目标函数升高），拒绝新参数并增大$\lambda$
   ```python
   if np.linalg.norm(residuals_new) < np.linalg.norm(residuals):
       lambda_factor /= 10  # 减少lambda，更接近高斯-牛顿法
       theta = theta_new
   else:
       lambda_factor *= 10  # 增加lambda，更接近梯度下降法
   ```

6. **收敛判断**：当参数变化量小于阈值时停止迭代
   ```python
   if np.linalg.norm(delta_theta) < self.tolerance:
       print(f"迭代收敛，共迭代 {i+1} 次")
       return theta_new
   ```

