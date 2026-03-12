#include "cloud_network_bridge.hpp"

namespace cloudlogger {

CloudNetwork* CloudNetworkRegistry::instance = nullptr;

void CloudNetworkRegistry::registerNetwork(CloudNetwork* network) {
    instance = network;
}

CloudNetwork* CloudNetworkRegistry::get() {
    return instance;
}

std::string CloudNetworkRegistry::get(const std::string& url, const std::string& params) {
    if (instance != nullptr) {
        return instance->get(url, params);
    }
    return "";
}

std::string CloudNetworkRegistry::post(const std::string& url, const std::string& body) {
    if (instance != nullptr) {
        return instance->post(url, body);
    }
    return "";
}

} // namespace cloudlogger
