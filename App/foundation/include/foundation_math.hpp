#ifndef FOUNDATION_MATH_HPP
#define FOUNDATION_MATH_HPP

#include <string>

namespace foundation {

class MathApi {
public:
    static int add(int left, int right);
    static std::string bridgeGet(const std::string& url, const std::string& params);
    static std::string bridgePost(const std::string& url, const std::string& body);
};

} // namespace foundation

#endif // FOUNDATION_MATH_HPP
