import casadi as ca

# 定义符号变量
x = ca.SX.sym('x',2)
y = ca.SX.sym('y')
"""
定义函数:
    输入：符号变量 x,y
    函数运算：[x,ca.sin(y)*x]
    输入输出命名：['x','y'],['r','q']
""" 
f = ca.Function('f',[x,y], \
                [x,ca.sin(y)*x],\
                ['x','y'],['r','q'])
print(f)

#  按参数顺序传递（位置参数）
r0, q0 = f(1.1,3.3)
print('r0:',r0)
print('q0:',q0)

# 按参数名称传递（关键字参数）
res = f(y=3.3, x=1.1)
print("res:", res)  