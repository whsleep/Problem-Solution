#include <iostream>
#include <Eigen/Dense>

using namespace Eigen;

int main()
{
    // 定义一个3x3的矩阵，元素类型为double
    Matrix3d matrix1;
    matrix1 << 1, 2, 3,
        4, 5, 6,
        7, 8, 9;
    std::cout << "Matrix1:\n"
              << matrix1 << std::endl;

    // 定义一个2x2的矩阵，元素全为0
    Matrix<double, 2, 2> matrix2 = Matrix<double, 2, 2>::Zero();
    std::cout << "\nMatrix2:\n"
              << matrix2 << std::endl;

    // 矩阵乘法
    Matrix3d matrix3 = matrix1 * matrix1.transpose();
    std::cout << "\nMatrix3 (matrix1 * matrix1^T):\n"
              << matrix3 << std::endl;

    return 0;
}