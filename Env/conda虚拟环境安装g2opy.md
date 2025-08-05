# conda虚拟环境安装g2opy

## 进入需要安装的虚拟环境

⚠️`your_env`是你自己的虚拟环境

```shell
conda activate your_env
```

## `clone`&&`cmake`&&`make`

```shell
git clone https://github.com/uoip/g2opy.git
cd g2opy
mkdir build
cd build
cmake -DPYTHON_EXECUTABLE=$(which python) ..
```

### `make`前的修改

🎗️实际测试`ubuntu18.04`可以跳过此步，`ubuntu20.04`必须进行此项修改才可编译通过

参考[【備忘録】g2o / g2opyのインストール@Ubuntu20.04 ](https://novnote.com/g2o-g2opy-install/762/)

> 将`g2opy/python/core/eigen_types.h` 的第 185 ~ 188 行进行以下修改
 ```cpp
// 修改前
.def("x", (double (Eigen::Quaterniond::*) () const) &Eigen::Quaterniond::x)
.def("y", (double (Eigen::Quaterniond::*) () const) &Eigen::Quaterniond::y)
.def("z", (double (Eigen::Quaterniond::*) () const) &Eigen::Quaterniond::z)
.def("w", (double (Eigen::Quaterniond::*) () const) &Eigen::Quaterniond::w)
// ↓
// 修改后
.def("x", [](const Eigen::Quaterniond& q) { return q.x(); })
.def("y", [](const Eigen::Quaterniond& q) { return q.y(); })
.def("z", [](const Eigen::Quaterniond& q) { return q.z(); })
.def("w", [](const Eigen::Quaterniond& q) { return q.w(); })
```
> 修改后即可`make`成功

### `make`

```shell
make -j8
cd ..
```

### `install`

```
python setup.py install
```

⚠️这一步可能会出现 

<font color='red'>
error: Multiple top-level packages discovered in a flat-layout: ['lib', 'g2o', 'script', 'contrib', 'EXTERNAL', 'cmake_modules'].`
</font>

对`setup.py`进行以下修改即可

```python
# 引用部分添加 find_packages
from setuptools import setup, find_packages
# setup部分添加 packages=find_packages(include=['g2o*']),
setup(
    name='g2opy',
    version='0.1',
    packages=find_packages(include=['g2o*']),
    # 其他配置...
)
```

再次执行`python setup.py install`即可安装成功。

## 一些检查工作

### \1

```shell
cd lib
ls g2o*
```

这里会输出编译完成的动态库
我的`python`版本为`3.9`这里的输出结果为
`g2o.cpython-39-x86_64-linux-gnu.so`

### \2

```shell
python setup.py install
```

这一步骤主要目的是将编译完成的动态库拷贝到指定地址,执行完上述命令会输出

```shell
copying ./lib/g2o.cpython-39-x86_64-linux-gnu.so -> /home/whf/anaconda3/envs/ir-sim/lib/python3.9/site-packages
```

即为拷贝地址,可以检查是否正确


## 参考

[g2opy](https://github.com/uoip/g2opy.git)

[【備忘録】g2o / g2opyのインストール@Ubuntu20.04 ](https://novnote.com/g2o-g2opy-install/762/)

[Use g2opy to do a simple two-dimensional loop optimization Slam (with python code)
PointCloud-Slam-Image-Web3](https://medium.com/ros-c-other/use-g2opy-to-do-a-simple-two-dimensional-loop-optimization-slam-with-python-code-9a42fc18fcf8)