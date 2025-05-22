# 简化版TEB

## 开源来自

[teb_local_planner](https://github.com/gogongxt/teb_local_planner)

## 环境检测

```shell
# 检测opencv版本是否为 4.2.0
dpkg -l | grep libopencv

# 检测yaml-cpp版本是否为 0.7.0
pkg-config --modversion yaml-cpp

# 检测 eigen 版本是大于 3 3.4
pkg-config --modversion eigen3

# 查看Boost是否为1.8.1版本
cat /usr/include/boost/version.hpp | grep BOOST_LIB_VERSION

# 2020-04 版本
dpkg -l | grep g2o

# cere_solver 2.1.0
cat /usr/local/include/ceres/version.h
```

### 安装 `yaml-cpp.0.7.0`

⚠️ **注意：这里仅记录我的实际操作，仅供参考。**

```shell
cd ~

wget https://github.com/jbeder/yaml-cpp/archive/refs/tags/yaml-cpp-0.7.0.tar.gz

tar -xvf yaml-cpp-0.7.0.tar.gz

cd yaml-cpp-yaml-cpp-0.7.0

mkdir build

cd build

cmake -DYAML_BUILD_SHARED_LIBS=ON ..

```

这里`cmake` 操作会出现最小版本不匹配报错，如下


>CMake Error at CMakeLists.txt:2 (cmake_minimum_required):
> Compatibility with CMake < 3.5 has been removed from CMake.
>
>  Update the VERSION argument <min> value.  Or, use the <min>...<max> syntax
>
>  to tell CMake that the project requires at least <min> but has been updated
>
>  to work with policies introduced by <max> or earlier.
>
>  Or, add -DCMAKE_POLICY_VERSION_MINIMUM=3.5 to try configuring anyway.

需要将出错的 `CMakeLists.txt` 指定行进行以下更改即可

⚠️ **注意：请使用指令 `cmake --version ` 验证 `cmake` 版本，小于3.5首先进行升级，再执行以下操作。**

```shell
# 将最小版本要求修改为 `3.5`
cmake_minimum_required(VERSION 3.5)
```
一共会遇到四次同类型报错，分别在

```shell
CMake Error at CMakeLists.txt:2 (cmake_minimum_required)

CMake Error at test/gtest-1.10.0/CMakeLists.txt:4

CMake Error at test/gtest-1.10.0/googlemock/CMakeLists.txt:45

CMake Error at test/gtest-1.10.0/googletest/CMakeLists.txt:56
```

按照上述解决方式依次修改 `CMakeLists.txt` 报错行内容即可。

`cmake` 成功后继续执行以下指令

```shell
make -j$(nproc)

sudo make install

# 验证版本，终端输出 0.7.0 即安装成功
pkg-config --modversion yaml-cpp

# 删除相关无用文件
cd ../..
rm -rf yaml-cpp-0.7.0.tar.gz
rm -rf yaml-cpp-yaml-cpp-0.7.0
```

### 安装 `boost 1.81`

```shell
cd ~

wget https://archives.boost.io/release/1.81.0/source/boost_1_81_0.tar.gz

tar xzvf boost_1_81_0.tar.gz

cd boost_1_81_0

sudo apt-get update

sudo apt-get install build-essential g++ python-dev autotools-dev libicu-dev build-essential libbz2-dev libboost-all-dev

./bootstrap.sh --prefix=/usr/

# 出现 The Boost C++ Libraries were successfully built! 即编译成功
./b2

sudo ./b2 install

# 验证版本， 返回1.8.1即成功
cat /usr/include/boost/version.hpp | grep BOOST_LIB_VERSION

# 删除相关无用文件
cd ..
rm -rf boost_1_81_0.tar.gz
rm -rf boost_1_81_0
sudo rm -rf boost_1_81_0
```

### 安装 `cere_solver 2.1.0`

⚠️ **注意：如果你使用 `WSL2` 请先进行以下操作。**

> 终端输入 `echo $PATH` 检查输出结果是否存在包含 `mnt` 的路径，若不存在可跳过此步骤。
>
> 如果出现 `mnt` 路径，需要禁用 `$PATH` 中的 `windows` 的环境变量。
>
> 终端输入
>
> ```shell
>sudo vim /etc/wsl.conf
>
> # 粘贴以下内容
> # 不加载Windows中的PATH内容
> [interop]
> enabled=false
> appendWindowsPath = false
> # 不自动挂载Windows系统所有磁盘分区
> [automount]
> enabled = false
> ```
> 🎗️: `vim` 按 `i` 进入编辑模式，按 `esc` 加 `:` 输入`wq`保存退出。
>
> 修改完成后重启，并再次`echo $PATH`检查即可。

⚠️ **注意：需要使用 `vscode` 远程功能，需要再编译完成后，将 `[automount]` 的 `enabled` 修改为 `true`。**

```shell
cd ~

wget https://github.com/ceres-solver/ceres-solver/archive/refs/tags/2.1.0.tar.gz

tar zxf ceres-solver-2.1.0.tar.gz

mkdir ceres-bin

cd ceres-bin

cmake ../ceres-solver-2.1.0

make -j$(nproc)

sudo make install

# 检查版本
cat /usr/local/include/ceres/version.h

# 删除相关无用文件
rm -rf ceres-solver-2.1.0.tar.gz
rm -rf ceres-solver-2.1.0
rm -rf ceres-bin

```

### g2o安装

```shell
sudo apt-get update
sudo apt-get install -y libeigen3-dev libboost-all-dev libopencv-dev

cd ~
wget https://github.com/RainerKuemmerle/g2o/archive/refs/tags/20200410_git.tar.gz
tar zxf g2o-20200410_git.tar.gz
cd g2o-20200410_git/
mkdir build
cd build/
cmake ..
```

这里`cmake` 操作会出现最小版本不匹配报错，解决方式参考 `yaml-cpp.0.7.0` 。

还会出现一个 `CMake Error at g2o/apps/g2o_cli/CMakeLists.txt:26 (cmake_policy):`

将该目录下的 `CMakeLists.txt` 第 `26` 行改为

```shell
# cmake_policy(SET CMP0043 OLD)
cmake_policy(SET CMP0043 NEW)
```

```shell
make -j4
sudo make install

# 返回路径即安装成功
find /usr/local/include /usr/include -name "g2o"

# 删除相关无用文件
rm -rf g2o-20200410_git.tar.gz
rm -rf g2o-20200410_git/

```

## 一些适应性配置

先按照以下步骤执行

```shell
git clone https://github.com/gogongxt/teb_local_planner.git
cd teb_local_planner
mkdir build
cd build
```
### 修改

1. 将 `CMakeLists.txt` 中的 `find_package(OpenCV 4.8 REQUIRED)` 修改为 `find_package(OpenCV 4.2 REQUIRED)`，为了方便这里没有安装 `4.8` 版本，实测 `4.2` 版本也可以执行。

2. 修改 `config.yaml` 配置文件中的 `show_button` 为 `false`。

3. 将 `gxt/config.hpp` 中的 `ReadConfigXmlFile` 函数进行以下修改，主要修改 `config.yaml` 的绝对路径。

⚠️ **注意：`"/your_path/teb_local_planner/config.yaml"` 为你的 `config.yaml` 实际绝对路径，请勿复制粘贴以下内容。**

> ```cpp
>   // Load the YAML file
>   YAML::Node config = YAML::LoadFile( "/your_path/teb_local_planner/config.yaml");
> ```

4. 由于 `Eigen` 版本不同，需要修改矩阵定义，如下

文件为 `/inc/ceres_types/ceres_types.h`，第 135，136行。

> ```cpp
> // 修改前
> Eigen::Vector<T,2> current_pose(*x_a,*y_a);
> Eigen::Vector<T,2> pos_(T(pos(0)),T(pos(1)));
> // 修改后
> Eigen::Matrix<T, 2, 1> current_pose(*x_a,*y_a);
> Eigen::Matrix<T, 2, 1> pos_(T(pos(0)),T(pos(1)));
> ```


```shell
make -j16
./teb
```

弹出 `GUI` 界面即成功运行。


