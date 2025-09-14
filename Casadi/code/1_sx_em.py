from casadi import *

# 1x1 符号矩阵
x = SX.sym("x")
print(x)
# 1x5 符号矩阵
y = SX.sym("y", 5)
print(y)
# 4x2 符号矩阵
z = SX.sym("z", 4, 2)
print(z)
# 符号数学表达式
f = x*x + 3/x
print(f)
# 全零密集 4x5 矩阵
zer = SX.zeros(4, 5)
print(zer)
# 稀疏空矩阵 4x5 矩阵
spar = SX(4, 5)
print(spar)
# 稀疏 4x4 矩阵
# e = SX.eye(4)
# print(e)