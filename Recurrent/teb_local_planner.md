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

#
cat /usr/include/boost/version.hpp | grep BOOST_LIB_VERSION
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




