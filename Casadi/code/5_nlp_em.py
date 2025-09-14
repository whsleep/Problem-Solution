import casadi as ca 

x = ca.SX.sym('x')
y = ca.SX.sym('y')
z = ca.SX.sym('z')
"""
NLP 格式 列向量 'x', 函数 `f`, 约束 `g`
"""
nlp = {'x':ca.vertcat(x,y,z), 'f':x**2+100*z**2, 'g':z+(1-x)**2-y}
S = ca.nlpsol('S', 'ipopt', nlp)
print(S)
# x0初值，约束函数上下界均为0，即表示为 0=<g<=0
r = S(x0=[2.5,3.0,0.75],\
      lbg=0, ubg=0)
x_opt = r['x']
print('x_opt: ', x_opt)