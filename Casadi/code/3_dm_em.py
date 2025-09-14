import casadi as ca

# 创建DM标量（1×1矩阵）
a = ca.DM(3.14)
print(a)

# 创建DM向量（3×1列向量）
b = ca.DM([1, 2, 3]) 
print(b)

# 创建DM矩阵（2×2矩阵）
c = ca.DM([[1.5, 2.5], [3.5, 4.5]])
print(c)

x = ca.DM([[2, 3], [4, 5]])
y = ca.DM([[1, 1], [1, 1]])

# 数值运算：矩阵加法
z = x + y  # 结果为 DM([[3,4],[5,6]])

# 数值运算：矩阵乘法
w = x @ y  # 结果为 DM([[5,5],[9,9]])

x = ca.SX.sym('x')
y = ca.SX.sym('y')
f = x**2 + y  # SX符号表达式

"""
连接符号计算与数值求解
"""
# 1. 定义SX符号变量
x = ca.SX.sym('x')  # 符号变量x
y = ca.SX.sym('y')  # 符号变量y

# 2. 构建SX符号表达式
f = x**2 + y  # 表达式：f(x,y) = x² + y

# 3. 用Function编译表达式（定义输入和输出）
# 第一个参数是函数名，第二个参数是输入变量列表，第三个参数是输出表达式列表
f_func = ca.Function('f_func', [x, y], [f])

# 4. 定义要代入的数值（用DM类型存储）
x_val = ca.DM(2)   # x的数值：2
y_val = ca.DM(3)   # y的数值：3

# 5. 调用编译好的函数，传入数值计算结果
f_val = f_func(x_val, y_val)  # 计算 2² + 3 = 7

# 打印结果（f_val是DM类型，用.full()可转换为NumPy数组便于查看）
print("计算结果：", f_val)          # 输出：7
print("转换为NumPy数组：", f_val.full())  # 输出：[[7.]]