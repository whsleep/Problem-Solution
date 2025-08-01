import numpy as np
import matplotlib.pyplot as plt

# 参数
d = 0.2
gamma = np.linspace(-np.pi/2, np.pi/2, 400)   # γ
v     = np.linspace(-1.0, 1.0, 300)           # v 范围

# 网格化
G, V = np.meshgrid(gamma, v)      # G: γ 网格, V: v 网格
TAN_G = np.tan(G)                 # tan(γ)

# 计算 θ̇
theta_dot = V * TAN_G / d         # 形状 (len(v), len(gamma))

# 绘图
fig, ax = plt.subplots(figsize=(6, 4))
im = ax.pcolormesh(theta_dot, V, G * 180 / np.pi,
                   shading='auto', cmap='coolwarm')
ax.set_xlabel(r'$\dot{\theta} \; (\mathrm{rad/s})$')
ax.set_ylabel(r'$v \; (\mathrm{m/s})$')
cbar = fig.colorbar(im, ax=ax)
cbar.set_label(r'$\gamma \; (\mathrm{deg})$')

ax.set_title(r'$\dot{\theta}=v\tan\gamma/d,\; d=0.2\,\mathrm{m},\; '
             r'\gamma\in[-\pi/3,\pi/3],\; v\in[-1,1]$')
ax.grid(True, ls='--', lw=0.5)

plt.tight_layout()
plt.show()