from casadi import *

# 创建2×3和3×2的MX矩阵（符号变量）
A = MX.sym('A', 2, 3)  # 2行3列的MX符号矩阵
B = MX.sym('B', 3, 2)  # 3行2列的MX符号矩阵

# 矩阵乘法（结果为2×2的MX矩阵）
C = A @ B  

# 提取C的第1行（子矩阵操作）
C_row = C[0, :]  

# 定义第一个函数：f(x) = x²（输入输出均为MX类型）
x = MX.sym('x')
f = Function('f', [x], [x**2])
print(f(2))

# 定义第二个函数：g(y) = sin(y)（输入输出均为MX类型）
y = MX.sym('y')
g = Function('g', [y], [sin(y)])
print(g(4))

# 组合为复合函数：h(x) = g(f(x)) = sin(x²)
h = Function('h', [x], [g(f(x))])  # 直接嵌套，基于MX变量传递
print(h(2))
