import numpy as np

class NonlinearModel:
    """表示非线性模型的类，包含残差和Jacobian矩阵的计算。"""
    def __init__(self, func, jacobian):
        """
        :param func: 非线性模型函数
        :param jacobian: Jacobian矩阵的计算函数
        """
        self.func = func
        self.jacobian = jacobian
    
    def residuals(self, x_data, y_data, theta):
        """计算残差向量"""
        return y_data - self.func(x_data, theta)
    
    def jacobian_matrix(self, x_data, theta):
        """计算给定参数下的Jacobian矩阵"""
        return self.jacobian(x_data, theta)


class LevenbergMarquardt:
    """Levenberg-Marquardt算法的实现类。"""
    def __init__(self, model, tolerance=1e-6, max_iters=100, lambda_init=0.01):
        """
        :param model: 待拟合的非线性模型对象
        :param tolerance: 收敛阈值
        :param max_iters: 最大迭代次数
        :param lambda_init: 初始阻尼因子lambda
        """
        self.model = model
        self.tolerance = tolerance
        self.max_iters = max_iters
        self.lambda_init = lambda_init
    
    def fit(self, x_data, y_data, initial_theta):
        """使用Levenberg-Marquardt算法拟合模型参数"""
        theta = initial_theta
        lambda_factor = self.lambda_init
        
        for i in range(self.max_iters):
            residuals = self.model.residuals(x_data, y_data, theta)
            jacobian = self.model.jacobian_matrix(x_data, theta)
            
            # 计算Hessian近似
            H = jacobian.T @ jacobian
            
            # 更新公式中增加lambda项
            delta_theta = np.linalg.inv(H + lambda_factor * np.eye(H.shape[0])) @ jacobian.T @ residuals
            
            # 更新参数
            theta_new = theta + delta_theta
            
            # 计算新的残差
            residuals_new = self.model.residuals(x_data, y_data, theta_new)
            
            # 判断是否收敛
            if np.linalg.norm(delta_theta) < self.tolerance:
                print(f"迭代收敛，共迭代 {i+1} 次")
                return theta_new
            
            # 动态调整lambda
            if np.linalg.norm(residuals_new) < np.linalg.norm(residuals):
                lambda_factor /= 10  # 减少lambda
                theta = theta_new
            else:
                lambda_factor *= 10  # 增加lambda
        
        print("达到最大迭代次数，未能完全收敛。")
        return theta


# 使用示例
if __name__ == "__main__":
    # 定义非线性模型 y = a * exp(b * x)
    def func(x, theta):
        return theta[0] * np.exp(theta[1] * x)
    
    # 定义Jacobian矩阵
    def jacobian(x, theta):
        J = np.zeros((len(x), len(theta)))
        J[:, 0] = np.exp(theta[1] * x)
        J[:, 1] = theta[0] * x * np.exp(theta[1] * x)
        return J
    
    # 创建模型和LM算法实例
    model = NonlinearModel(func, jacobian)
    lm_solver = LevenbergMarquardt(model)
    
    # 生成数据
    x_data = np.linspace(0, 1, 10)
    y_data = 2 * np.exp(3 * x_data) + np.random.normal(0, 0.1, size=x_data.shape)
    
    # 初始参数猜测
    initial_theta = np.array([1, 1])
    
    # 执行拟合
    optimal_theta = lm_solver.fit(x_data, y_data, initial_theta)
    print("最优参数:", optimal_theta)