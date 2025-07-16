import casadi as ca
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class ReplanSolver:
    def __init__(self,
                 start: np.ndarray,
                 end: np.ndarray,
                 obs: np.ndarray,
                 n = None,          # 允许 None -> 自动设定轨迹点数量
                 vmax: float = 1.0,
                 wmax: float = 1.5,
                 rmin: float = 0.5,
                 safe_dis: float = 0.3,
                 auto_hz: float = 10.0):        # 控制频率
        self.start = np.copy(np.asarray(start, float))  
        self.end = np.copy(np.asarray(end, float))    
        self.obs      = np.copy(np.asarray(obs, float))
        self.vmax     = vmax
        self.wmax     = wmax
        self.rmin     = rmin
        self.safe_dis = safe_dis
        self.auto_hz  = auto_hz

        # 1. 自动计算 n
        if n is None:
            self._auto_size()
        else:
            self.n = n

        self._last_sol = None

    def _auto_size(self):
        dist = np.linalg.norm(self.end[:2] - self.start[:2])
        t_min = dist / self.vmax
        self.n = max(4, int(np.ceil(t_min * self.auto_hz)))
        print(f'[Auto] dist={dist:.2f}, t_min={t_min:.2f}, n={self.n}')

    # ---------- 内部 ----------
    def _build_nlp(self, obs_now):
        n = self.n
        x  = ca.SX.sym('x', n)
        y  = ca.SX.sym('y', n)
        θ  = ca.SX.sym('θ', n)
        ΔT = ca.SX.sym('ΔT', n+1)
        w  = ca.vertcat(x, y, θ, ΔT)

        pts = [ca.DM(self.start)]
        for k in range(n):
            pts.append(ca.vertcat(x[k], y[k], θ[k]))
        pts.append(ca.DM(self.end))

        def norm_angle(a):
            return ca.atan2(ca.sin(a), ca.cos(a))

        res = []
        for i in range(n+1):
            p0, p1   = pts[i][:2], pts[i+1][:2]
            th0, th1 = pts[i][2], pts[i+1][2]
            seg = ca.norm_2(p1 - p0)
            dt  = ΔT[i]

            res.append(seg)
            res.append(dt)
            if 1 <= i <= n:
                dists = [ca.norm_2(pts[i][:2] - o) for o in obs_now]
                dmin  = ca.mmin(ca.vertcat(*dists))
                res.append(ca.fmax(0, self.safe_dis - dmin))
            v = seg / (dt + 1e-6)
            res.append(ca.fmax(0, ca.fabs(v) - self.vmax))
            dth = norm_angle(th1 - th0)
            ω   = dth / (dt + 1e-6)
            res.append(ca.fmax(0, ca.fabs(ω) - self.wmax))
            l0 = ca.vertcat(ca.cos(th0), ca.sin(th0))
            l1 = ca.vertcat(ca.cos(th1), ca.sin(th1))
            d  = p1 - p0
            cross = (l0[0]+l1[0])*d[1] - (l0[1]+l1[1])*d[0]
            res.append(10*cross)
            # 计算转弯半径（考虑速度方向）
            r = v / (ca.fabs(ω) + 1e-6)
            # 确保转弯半径的绝对值大于等于最小转弯半径
            res.append(10*ca.fmax(0, ca.fabs(r) - self.rmin))


        residuals = ca.vertcat(*res)
        nlp = {'x': w, 'f': 0.5 * ca.dot(residuals, residuals)}
        opts = {'ipopt.print_level': 0, 'print_time': 1,
                        'ipopt.warm_start_init_point': 'yes',
                        'ipopt.max_iter': 500}
        return ca.nlpsol('solver', 'ipopt', nlp, opts)

    def _init_guess(self):
        if self._last_sol is not None:
            return self._last_sol
        n = self.n
        return np.hstack([
            np.linspace(self.start[0], self.end[0], n+2)[1:-1],
            np.linspace(self.start[1], self.end[1], n+2)[1:-1],
            np.unwrap(np.linspace(self.start[2], self.end[2], n+2))[1:-1],
            np.full(n+1, 0.2)
        ])

    # ---------- 公开 ----------
    def solve(self,
            obs_new=None,
            start_new=None,
            end_new=None,
            pos_th: float = 0.05,   # 位置变化阈值 [m]
            ang_th: float = 0.10):  # 角度变化阈值 [rad]
        """
        在线重规划入口
        obs_new    : 新障碍物坐标 (Nx2)
        start_new  : 新起点 (3,) 或 None
        end_new    : 新终点 (3,) 或 None
        pos_th     : 位置变化触发阈值
        ang_th     : 角度变化触发阈值
        返回:
        traj, cost
        """

        # 1. 障碍物更新
        if obs_new is not None:
            self.obs = np.asarray(obs_new, float)

        # 2. 起点 / 终点更新 + 偏差检测
        dirty_n = False
        if start_new is not None:
            start_new = np.asarray(start_new, float)
            if (np.linalg.norm(start_new[:2] - self.start[:2]) > pos_th or
                    abs(np.arctan2(np.sin(start_new[2] - self.start[2]),
                                np.cos(start_new[2] - self.start[2]))) > ang_th):
                self.start = np.copy(start_new) 
                dirty_n = True

        if end_new is not None:
            end_new = np.asarray(end_new, float)
            if (np.linalg.norm(end_new[:2] - self.end[:2]) > pos_th or
                    abs(np.arctan2(np.sin(end_new[2] - self.end[2]),
                                np.cos(end_new[2] - self.end[2]))) > ang_th):
                self.end = np.copy(end_new) 
                dirty_n = True

        # 3. 只有起点/终点变化时才重算 n 并清空上一次解
        if dirty_n:
            self._auto_size()
            self._last_sol = None          # 强制重新生成初值

        # 4. 其余流程保持不变
        solver = self._build_nlp(self.obs)
        sol = solver(x0=self._init_guess(), lbx=-10, ubx=10)
        if sol['f'] is None:
            return None, np.inf
        w_opt = np.array(sol['x']).flatten()
        self._last_sol = w_opt
        traj = np.vstack([self.start,
                        np.column_stack([w_opt[:self.n],
                                        w_opt[self.n:2*self.n],
                                        w_opt[2*self.n:3*self.n]]),
                        self.end])
        return traj, float(sol['f'])

def run_interactive(start, end, obs):
    pos_th = 0.05      # 位置变化阈值 [m]
    ang_th = 0.10      # 角度变化阈值 [rad]

    solver = ReplanSolver(start, end, obs)
    n     = solver.n

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.set_xlim(-0.4, 2.4)
    ax.set_ylim(-0.4, 2.4)

    pt_radius   = 0.06
    pick_radius = 0.18
    head_scale  = 0.4

    # 存储所有动态元素（圆、箭头、轨迹线段），用于全量清除
    dynamic_elements = []
    circles = []
    arrows = []
    traj_lines = []

    # 初始化起点/终点箭头（用于显示角度）
    start_arrow = None
    end_arrow = None

    # 障碍物及安全区域（静态，无需频繁清除）
    obs_scat = ax.scatter(obs[:, 0], obs[:, 1], s=300, c='k', picker=True)
    safe_circs = [plt.Circle(o, solver.safe_dis, color='k', alpha=0.1) for o in obs]
    for c in safe_circs:
        ax.add_patch(c)

    def draw_dir_arrows():
        nonlocal start_arrow, end_arrow
        # 清除旧箭头
        if start_arrow is not None:
            start_arrow.remove()
        if end_arrow is not None:
            end_arrow.remove()
        # 绘制新箭头
        dx = 1.5 * pt_radius * np.cos(start[2])
        dy = 1.5 * pt_radius * np.sin(start[2])
        start_arrow = ax.arrow(start[0], start[1], dx, dy,
                              head_width=head_scale * pt_radius, fc='b', ec='b')
        dx = 1.5 * pt_radius * np.cos(end[2])
        dy = 1.5 * pt_radius * np.sin(end[2])
        end_arrow = ax.arrow(end[0], end[1], dx, dy,
                            head_width=head_scale * pt_radius, fc='g', ec='g')

    def update_plot(full):
        nonlocal dynamic_elements, circles, arrows, traj_lines, solver
        if full is None:
            return

        # 1. 全量清除所有动态元素（关键：解决n变化导致的残留）
        for elem in dynamic_elements:
            try:
                elem.remove()
            except:
                pass
        dynamic_elements.clear()
        circles.clear()
        arrows.clear()
        traj_lines.clear()

        # 2. 重建轨迹点的圆和箭头
        for k in range(len(full)):
            x, y, th = full[k]
            # 轨迹点圆（起点/终点用特殊颜色）
            r = pick_radius if k in (0, len(full)-1) else pt_radius
            color = 'tab:blue' if k == 0 else 'tab:green' if k == len(full)-1 else 'tab:red'
            c = plt.Circle((x, y), r, color=color, alpha=0.2, picker=True)
            ax.add_patch(c)
            circles.append(c)
            dynamic_elements.append(c)
            # 轨迹点方向箭头
            dx = pt_radius * np.cos(th)
            dy = pt_radius * np.sin(th)
            ar = ax.arrow(x, y, dx, dy,
                          head_width=head_scale * pt_radius, fc='k', ec='k')
            arrows.append(ar)
            dynamic_elements.append(ar)

        # 3. 绘制轨迹线段（连接相邻点）
        for k in range(len(full)-1):
            x0, y0 = full[k][0], full[k][1]
            x1, y1 = full[k+1][0], full[k+1][1]
            line = ax.plot([x0, x1], [y0, y1], 'b-', linewidth=1.5)[0]
            traj_lines.append(line)
            dynamic_elements.append(line)

        # 更新障碍物位置和方向箭头
        obs_scat.set_offsets(obs)
        for c, o in zip(safe_circs, obs):
            c.center = o
        draw_dir_arrows()
        fig.canvas.draw_idle()

    # 首次求解并绘图
    traj, cost = solver.solve()
    print('Initial cost =', cost)
    update_plot(traj)

    dragging = None  # 记录当前拖动的元素：('obs', idx) / ('start', None) / ('end', None)

    def on_pick(event):
        nonlocal dragging
        if event.artist == obs_scat:
            dragging = ('obs', event.ind[0])
        elif event.artist in circles:
            k = circles.index(event.artist)
            if k == 0:
                dragging = ('start', None)
            elif k == len(circles)-1:
                dragging = ('end', None)

    def on_motion(event):
        if dragging is None or event.xdata is None:
            return
        x, y = event.xdata, event.ydata
        kind, idx = dragging
        if kind == 'obs':
            obs[idx] = [x, y]
            obs_scat.set_offsets(obs)
            safe_circs[idx].center = (x, y)
            fig.canvas.draw_idle()
        elif kind == 'start':
            start[0], start[1] = x, y
            draw_dir_arrows()
            fig.canvas.draw_idle()
        elif kind == 'end':
            end[0], end[1] = x, y
            draw_dir_arrows()
            fig.canvas.draw_idle()

    def on_release(event):
        nonlocal dragging
        if dragging is None:
            return
        dragging = None

        # 重新规划路径并更新绘图
        traj, cost = solver.solve(obs_new=obs,
                                  start_new=start,
                                  end_new=end,
                                  pos_th=pos_th,
                                  ang_th=ang_th)
        if traj is not None:
            print('Re-solved cost =', cost)
            update_plot(traj)

    def on_scroll(event):
        if event.inaxes != ax:
            return
        # 滚动起点/终点调整角度
        if np.linalg.norm([event.xdata, event.ydata] - end[:2]) < pick_radius * 1.5:
            end[2] += np.sign(event.step) * 0.2
            draw_dir_arrows()
            fig.canvas.draw_idle()
        elif np.linalg.norm([event.xdata, event.ydata] - start[:2]) < pick_radius * 1.5:
            start[2] += np.sign(event.step) * 0.2
            draw_dir_arrows()
            fig.canvas.draw_idle()

    # 绑定事件
    fig.canvas.mpl_connect('pick_event', on_pick)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
    fig.canvas.mpl_connect('button_release_event', on_release)
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    plt.show()

if __name__ == "__main__":
    start = np.array([0.0, 0.0, -np.pi])
    end   = np.array([2.0, 2.0, np.pi / 3])
    obs   = np.array([[0.5, 0.75],
                      [1.5, 1.25],
                      [0.5, 1.75],
                      [1.5, 0.85]])
    run_interactive(start, end, obs)