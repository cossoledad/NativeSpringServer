#include "foundation_math.hpp"

#include "cloud_logger_bridge.hpp"
#include "cloud_network_bridge.hpp"

#include <string>

namespace foundation {

int MathApi::add(int left, int right) {
    const int result = left + right;
    cloudlogger::CloudLoggerRegistry::info(
        "foundation-math",
        "foundation add(" + std::to_string(left) + ", " + std::to_string(right) + ") = " +
            std::to_string(result));
    return result;
}

std::string MathApi::bridgeGet(const std::string& url, const std::string& params) {
    cloudlogger::CloudLoggerRegistry::info("foundation-network", "bridgeGet url=" + url + ", params=" + params);
    const std::string response = cloudlogger::CloudNetworkRegistry::get(url, params);
    if (response.empty()) {
        cloudlogger::CloudLoggerRegistry::warn("foundation-network", "bridgeGet got empty response");
    }
    return response;
}

std::string MathApi::bridgePost(const std::string& url, const std::string& body) {
    cloudlogger::CloudLoggerRegistry::info("foundation-network", "bridgePost url=" + url);
    const std::string response = cloudlogger::CloudNetworkRegistry::post(url, body);
    if (response.empty()) {
        cloudlogger::CloudLoggerRegistry::warn("foundation-network", "bridgePost got empty response");
    }
    return response;
}

} // namespace foundation
