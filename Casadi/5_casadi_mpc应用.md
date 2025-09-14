# casadi_mpc应用

## 参考开源项目

[simple_casadi_mpc
](https://github.com/Kotakku/simple_casadi_mpc)

**注意**：请确保已经安装 `casadi` ，安装参考[1_安装CASADI](1_安装CASADI.md)

**安装编译**

```shell
git clone https://github.com/Kotakku/simple_casadi_mpc.git
cd simple_casadi_mpc/
mkdir build
cd build
cmake ..
make -j8
```

**示例运行**

这里提供三个示例

- `diff_drive_mpc_example`
- `double_integrator_mpc_example`
- `inverted_pendulum_mpc_example`

只关注 `diff_drive_mpc_example` 其他示例运行同理

```shell
cd build
./diff_drive_mpc_example
```

![](pic/diff.gif)

## 内容说明

### 需要关注的文件

这里不在关注可视化部分代码，仅考虑MPC的运算内容

- [diff_drive_mpc_example](code/sim_mpc/simple_casadi_mpc/example/diff_drive_mpc_example.cpp)
- [casadi_utils](code/sim_mpc/simple_casadi_mpc/include/simple_casadi_mpc/casadi_utils.hpp)
- [simple_casadi_mpc](code/sim_mpc/simple_casadi_mpc/include/simple_casadi_mpc/simple_casadi_mpc.hpp)

### diff_drive_mpc_example

从 `main` 函数看流程

```cpp
int main() {
    // 问题定义
    auto prob = std::make_shared<DiffDriveProb>();
    // 求解器定义
    MPC mpc(prob);
    // 求解器参数配置
    casadi::DMDict param_list;
    param_list["x_ref"] = {1, -1.0, -M_PI / 2, 0, 0};
    Eigen::VectorXd x(5);
    x << -1, 1, 0, 0, 0;
    const double dt = 0.01;
    const size_t sim_len = 600;
    // 循环仿真
    for (size_t i = 0; i < sim_len; i++) {
        // 求解
        Eigen::VectorXd u = mpc.solve(x, param_list);
        // 仿真
        x = prob->simulate(x, u, dt);
    }
    // 可视化内容
}
```

流程为 `问题定义` - `求解器定义` - `求解器配置` - `循环求解、仿真`，围绕问题和求解器展开

所以我们主要看 `DiffDriveProb` 和 `MPC` 两个类即可

#### DiffDriveProb

`DiffDriveProb` 公共继承 `Problem` 类，作为实例化的类，其本身内容已经很清晰

**运动学方程**

```cpp
    virtual casadi::MX dynamics(casadi::MX x, casadi::MX u) override {
        using namespace casadi;

        auto lacc = u(0);
        auto racc = u(1);
        auto theta = x(2);
        auto v = x(3);
        auto omega = x(4);
        auto vx = v * cos(theta);
        auto vy = v * sin(theta);

        return vertcat(vx, vy, omega, lacc, racc);
    }
```

- 状态向量为 $\mathrm{x} = [x,y,\theta,v,\omega]^T$
- 控制向量为 $\mathrm{u} = [a_v,a_\omega]^T$

$$
\begin{align}
\dot{\mathrm{x}} = \mathrm{f}(\mathrm{x},\mathrm{u})
\end{align}
$$

**目标函数**

目标函数由 `stage_cost` 和 `terminal_cost` 组成

```cpp
    virtual casadi::MX stage_cost(casadi::MX x, casadi::MX u, size_t k) override {
        (void)k;
        using namespace casadi;
        MX L = 0;
        auto e = x - x_ref;
        L += 0.5 * mtimes(e.T(), mtimes(Q, e));
        L += 0.5 * mtimes(u.T(), mtimes(R, u));
        return dt() * L;
    }

    virtual casadi::MX terminal_cost(casadi::MX x) {
        using namespace casadi;
        auto e = x - x_ref;
        return 0.5 * mtimes(e.T(), mtimes(Qf, e));
    }
```

$$
\frac{1}{2}(\mathrm{x}-\mathrm{x_{ref}})^TQ(\mathrm{x}-\mathrm{x_{ref}})+\frac{1}{2}\mathrm{u}^TR\mathrm{u}
$$

## 参考

- [simple_casadi_mpc
](https://github.com/Kotakku/simple_casadi_mpc)