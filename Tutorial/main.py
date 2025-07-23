#!/usr/bin/env python
# -*- coding: utf-8 -*-

import casadi as ca
import casadi.tools as ca_tools

import numpy as np
import time
from draw import Draw_MPC_point_stabilization_v1

def shift_movement(T, t0, x0, u, f):
    f_value = f(x0, u[:, 0])
    st = x0 + T*f_value
    t = t0 + T
    u_end = ca.horzcat(u[:, 1:], u[:, -1])

    return t, st, u_end.T

if __name__ == '__main__':
    T = 0.2 # 采样时间
    N = 100 # 预测步长度
    rob_diam = 0.3 # 圆形机器人直径
    v_max = 0.6 # 最大线速度
    omega_max = np.pi/4.0 # 最大角速度

    # 定义系统状态符号变量
    x = ca.SX.sym('x')
    y = ca.SX.sym('y')
    theta = ca.SX.sym('theta')
    # 将[x,y,theta]构建成一维向量
    states = ca.vertcat(x, y)
    states = ca.vertcat(states, theta)
    # 记录状态向量尺寸
    n_states = states.size()[0]

    # 定义系统输入符号变量
    v = ca.SX.sym('v')
    omega = ca.SX.sym('omega')
    # 系统输入[v,omega] 构建成一位向量
    controls = ca.vertcat(v, omega)
    # 记录系统输入尺寸
    n_controls = controls.size()[0]

    # 运动学模型计算结果
    rhs = ca.vertcat(v*ca.cos(theta), v*ca.sin(theta))
    rhs = ca.vertcat(rhs, omega)

    ## 运动学模型function(状态转移函数)
    f = ca.Function('f', [states, controls], [rhs], ['input_state', 'control_input'], ['rhs'])

    ## 构建MPC问题参数
    # 控制输入序列 2xN
    U = ca.SX.sym('U', n_controls, N)
    # 系统状态序列 3x(N+1)
    X = ca.SX.sym('X', n_states, N+1)
    # 参考状态 6*1
    P = ca.SX.sym('P', n_states+n_states)


    # 固定初始值
    X[:, 0] = P[:3] 

    # 利用状态转移函数遍历递推
    for i in range(N):
        f_value = f(X[:, i], U[:, i])
        X[:, i+1] = X[:, i] + f_value*T
    
    """
     序列输入的状态转移函数U为输入序列,
     P为参考状态,这里设置为起点和终点状态

     返回长度为N的预测状态
    """
    ff = ca.Function('ff', [U, P], [X], ['input_U', 'target_state'], ['horizon_states'])

    # 惩罚矩阵 
    Q = np.array([[1.0, 0.0, 0.0],[0.0, 5.0, 0.0],[0.0, 0.0, .1]])
    R = np.array([[0.5, 0.0], [0.0, 0.05]])

    # 目标函数
    obj = 0 
    # 遍历计算X,U序列产生的代价
    for i in range(N):
        # 每个状态与终点状态的差值添加惩罚
        obj = obj + (X[:, i]-P[3:]).T @ Q @ (X[:, i]-P[3:]) + U[:, i].T @ R @ U[:, i]

    # 添加等式约束
    g = []
    for i in range(N+1):
        g.append(X[0, i])
        g.append(X[1, i])
    # 构建NLP问题
    # f'为目标函数，'x'为需寻找的优化结果（优化目标变量），'p'为系统参数，'g'为约束条件
    nlp_prob = {'f': obj, 'x': ca.reshape(U, -1, 1), 'p':P, 'g':ca.vcat(g)}

    opts_setting = {'ipopt.max_iter':100, 'ipopt.print_level':0, 'print_time':0, 'ipopt.acceptable_tol':1e-8, 'ipopt.acceptable_obj_change_tol':1e-6, }
    solver = ca.nlpsol('solver', 'ipopt', nlp_prob, opts_setting)


    # Simulation
    lbg = -2.0
    ubg = 2.0
    lbx = []
    ubx = []
    for _ in range(N):
        lbx.append(-v_max)
        ubx.append(v_max)
        lbx.append(-omega_max)
        ubx.append(omega_max)
    t0 = 0.0
    x0 = np.array([0.0, 0.0, 0.0]).reshape(-1, 1)# initial state
    xs = np.array([1.5, 1.5, 0.0]).reshape(-1, 1) # final state
    u0 = np.array([0.0, 0.0]*N).reshape(-1, 2)# np.ones((N, 2)) # controls
    x_c = [] # contains for the history of the state
    u_c = []
    t_c = [] # for the time
    xx = []
    sim_time = 20.0

    ## start MPC
    mpciter = 0
    start_time = time.time()
    index_t = []
    c_p = np.concatenate((x0, xs))
    init_control = ca.reshape(u0, -1, 1)
    res = solver(x0=init_control, p=c_p, lbg=lbg, lbx=lbx, ubg=ubg, ubx=ubx)
    lam_x_ = res['lam_x']
    ### inital test
    while(np.linalg.norm(x0-xs)>1e-2 and mpciter-sim_time/T<0.0 ):
        ## set parameter
        c_p = np.concatenate((x0, xs))
        init_control = ca.reshape(u0, -1, 1)
        t_ = time.time()
        res = solver(x0=init_control, p=c_p, lbg=lbg, lbx=lbx, ubg=ubg, ubx=ubx, lam_x0=lam_x_)
        lam_x_ = res['lam_x']
        # res = solver(x0=init_control, p=c_p,)
        # print(res['g'])
        index_t.append(time.time()- t_)
        u_sol = ca.reshape(res['x'], n_controls, N) # one can only have this shape of the output
        ff_value = ff(u_sol, c_p) # [n_states, N+1]
        x_c.append(ff_value)
        u_c.append(u_sol[:, 0])
        t_c.append(t0)
        t0, x0, u0 = shift_movement(T, t0, x0, u_sol, f)

        x0 = ca.reshape(x0, -1, 1)
        xx.append(x0.full())
        mpciter = mpciter + 1
    t_v = np.array(index_t)
    print(t_v.mean())
    print((time.time() - start_time)/(mpciter))
    draw_result = Draw_MPC_point_stabilization_v1(rob_diam=0.3, init_state=x0.full(), target_state=xs, robot_states=xx, export_fig=False)