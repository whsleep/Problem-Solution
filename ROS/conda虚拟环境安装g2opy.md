# conda虚拟环境安装g2opy

## 进入需要安装的虚拟环境

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
make -j8
cd ..
python setup.py install
```

执行上述步骤前可用
```shell
which python
```

检测该路径是否为你需要安装的虚拟环境

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