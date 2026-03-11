#include "foundation_math.hpp"

#include "cloud_logger_bridge.hpp"

#include <string>

namespace foundation {

int MathApi::add(int left, int right) {
    const int result = left + right;
    cloudlogger::CloudLoggerRegistry::upload(
        "foundation-math",
        "foundation add(" + std::to_string(left) + ", " + std::to_string(right) + ") = " +
            std::to_string(result));
    return result;
}

} // namespace foundation
