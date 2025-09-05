cmake_minimum_required(VERSION 3.22)
# 设置项目名称和版本
project(EigenDemo VERSION 1.0)

# 指定C++标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 寻找Eigen库
find_package(Eigen3 REQUIRED)

# 包含Eigen头文件
include_directories(${Eigen3_INCLUDE_DIRS})

# 添加可执行文件
add_executable(MatrixDemo 1_Matrix.cpp)
add_executable(ArrayDemo 2_Array.cpp)

# 链接Eigen库
target_link_libraries(MatrixDemo Eigen3::Eigen)
target_link_libraries(ArrayDemo Eigen3::Eigen)