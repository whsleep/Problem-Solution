# Eigen常用内容

## 注意事项

## Matrix和Array模板类

### Matrix 模板类

**定义** ：

```cpp
  Matrix<typename Scalar, 
         int RowsAtCompileTime, 
         int ColsAtCompileTime, 
         int Options = 0, 
         int MaxRowsAtCompileTime = RowsAtCompileTime, 
         int MaxColsAtCompileTime = ColsAtCompileTime>
```
其中：

- `Scalar`：元素类型
- `RowsAtCompileTime`：行
- `ColsAtCompileTime`：列
- `Options`：比特标志位
- `MaxRowsAtCompileTime` 和 `MaxColsAtCompileTime`：表示编译阶段矩阵的上限。

**示例** ：
    
- `typedef Matrix<int, 3, 3> Matrix3i;`：定义一个 3 行 3 列、元素类型为 `int` 的矩阵

- `typedef Matrix<double, 3, 1> Vector3d;`：定义一个 3 行 1 列、元素类型为 `double` 的列向量

- `typedef Matrix<float, 1, 3> RowVector3f;`：定义一个 1 行 3 列、元素类型为 `float` 的行向量

- **动态大小示例** ：
    * `typedef Matrix<double, Dynamic, Dynamic> MatrixXd;`：行和列均为动态的、元素类型为 `double` 的矩阵
    * `typedef Matrix<float, Dynamic, 1> VectorXf;`：行数动态、列数固定为 1、元素类型为 `float` 的列向量

### Array 模板类

**定义** ：

```cpp
Array<typename _Scalar, 
      int _Rows, 
      int _Cols, 
      int _Options, 
      int _MaxRows, 
      int _MaxCols>
```
定义方式与 `Matrix` 类似

**常见类定义示例** ：

- `typedef Array<float, Dynamic, 1> ArrayXf;`：动态大小、元素类型为 `float` 的一维数组
- `typedef Array<float, 3, 1> Array3f;`：3 行 1 列、元素类型为 `float` 的数组
- `typedef Array<double, Dynamic, Dynamic> ArrayXXd;`：行列均为动态、元素类型为 `double` 的二维数组
- `typedef Array<double, 3, 3> Array33d;`：3 行 3 列、元素类型为 `double` 的二维数组

**相关操作示例** ：
- `ArrayXf a = ArrayXf::Random(5);`：创建一个大小为 5、元素类型为 `float` 的数组，元素为随机数
- `a.abs();`：求数组中各元素的绝对值
- `a.sqrt();`：求数组中各元素的平方根
- `a.min(a.abs().sqrt());`：对数组中各元素及其绝对值的平方根进行比较，取较小值组成新数组

### 二者区别

`Martix` 表示的是矩阵，运算为矩阵运算，运算时尺寸需要遵循矩阵运算规则

`Array` 和 `Matrix` 数据组成相同，但运算规则为逐元素运算，需要相同尺寸数据进行运算

以下是 `Matrix` 和 `Array` 的使用及转换示例：

### `Matrix` 的使用

```cpp
#include <iostream>
#include <Eigen/Dense>

using namespace Eigen;

int main() {
    // 定义一个3x3的矩阵，元素类型为double
    Matrix3d matrix1;
    matrix1 << 1, 2, 3,
               4, 5, 6,
               7, 8, 9;
    std::cout << "Matrix1:\n" << matrix1 << std::endl;

    // 定义一个2x2的矩阵，元素全为0
    Matrix<double, 2, 2> matrix2 = Matrix<double, 2, 2>::Zero();
    std::cout << "\nMatrix2:\n" << matrix2 << std::endl;

    // 矩阵乘法
    Matrix3d matrix3 = matrix1 * matrix1.transpose();
    std::cout << "\nMatrix3 (matrix1 * matrix1^T):\n" << matrix3 << std::endl;

    return 0;
}
```

### `Array` 的使用

```cpp
#include <iostream>
#include <Eigen/Dense>

using namespace Eigen;

int main() {
    // 定义一个3元素的数组，元素类型为float
    Array3f array1;
    array1 << 1.0f, 2.0f, 3.0f;
    std::cout << "Array1:\n" << array1 << std::endl;

    // 定义一个2x2的数组，元素全为1
    Array<float, 2, 2> array2 = Array<float, 2, 2>::Ones();
    std::cout << "\nArray2:\n" << array2 << std::endl;

    // 逐元素相乘
    Array3f array3 = array1.array() * array1.array();
    std::cout << "\nArray3 (array1 * array1):\n" << array3 << std::endl;

    return 0;
}
```

### `Matrix` 和 `Array` 的转换示例

```cpp
#include <iostream>
#include <Eigen/Dense>

using namespace Eigen;

int main() {
    // 定义一个3x3的矩阵
    Matrix3d matrix;
    matrix << 1, 2, 3,
              4, 5, 6,
              7, 8, 9;

    // 将Matrix转换为Array
    Array3d array = matrix.array();
    std::cout << "Array converted from Matrix:\n" << array << std::endl;

    // 对Array进行逐元素操作
    Array3d abs_array = array.abs();
    std::cout << "\nAbsolute value of array:\n" << abs_array << std::endl;

    return 0;
}
```

### 将 `Array` 转换为 `Matrix`

```cpp
#include <iostream>
#include <Eigen/Dense>

using namespace Eigen;

int main() {
    // 定义一个3x3的数组
    Array3d array;
    array << 1, 2, 3,
             4, 5, 6,
             7, 8, 9;

    // 将Array转换为Matrix
    Matrix3d matrix = array.matrix();
    std::cout << "Matrix converted from Array:\n" << matrix << std::endl;

    // 对Matrix进行矩阵乘法
    Matrix3d matrix_transpose = matrix.transpose();
    Matrix3d result = matrix * matrix_transpose;
    std::cout << "\nMatrix * Matrix^T:\n" << result << std::endl;

    return 0;
}
```


## 参考

- [Eigen 使用教程](https://www.zywvvd.com/notes/coding/cpp/eigen/eigen-usage/)
- [Eigen](https://libeigen.gitlab.io/eigen/docs-nightly/GettingStarted.html)
- [快速入门矩阵运算——开源库Eigen](https://zhuanlan.zhihu.com/p/293023673)