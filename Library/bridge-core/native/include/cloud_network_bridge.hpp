#ifndef CLOUD_NETWORK_BRIDGE_HPP
#define CLOUD_NETWORK_BRIDGE_HPP

#include <string>

namespace cloudlogger {

class CloudNetwork {
public:
    virtual ~CloudNetwork() = default;
    virtual std::string get(const std::string& url, const std::string& params) = 0;
    virtual std::string post(const std::string& url, const std::string& body) = 0;
};

class CloudNetworkRegistry {
public:
    static void registerNetwork(CloudNetwork* network);
    static CloudNetwork* get();
    static std::string get(const std::string& url, const std::string& params);
    static std::string post(const std::string& url, const std::string& body);

private:
    static CloudNetwork* instance;
};

} // namespace cloudlogger

#endif // CLOUD_NETWORK_BRIDGE_HPP
