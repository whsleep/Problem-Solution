#include <iostream>
#include <Eigen/Dense>

using namespace Eigen;

int main()
{
    // 定义一个3元素的数组，元素类型为float
    Array3f array1;
    array1 << 1.0f, 2.0f, 3.0f;
    std::cout << "Array1:\n"
              << array1 << std::endl;

    // 定义一个2x2的数组，元素全为1
    Array<float, 2, 2> array2 = Array<float, 2, 2>::Ones();
    std::cout << "\nArray2:\n"
              << array2 << std::endl;

    // 逐元素相乘
    Array3f array3 = array1.array() * array1.array();
    std::cout << "\nArray3 (array1 * array1):\n"
              << array3 << std::endl;

    return 0;
}