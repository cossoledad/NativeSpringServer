#include "foundation_math.hpp"

#include <iostream>
#include <string>

int main() {
    const int left = 7;
    const int right = 5;
    const int result = foundation::MathApi::add(left, right);
    std::cout << "foundation add(" << left << ", " << right << ") = " << result << std::endl;
    return 0;
}
