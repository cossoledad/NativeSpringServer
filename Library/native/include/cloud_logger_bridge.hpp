#ifndef CLOUD_LOGGER_BRIDGE_HPP
#define CLOUD_LOGGER_BRIDGE_HPP

#include <string>

namespace cloudlogger {

class CloudLogger {
public:
    virtual ~CloudLogger() = default;
    virtual void upload(const std::string& category, const std::string& message) = 0;
};

class CloudLoggerRegistry {
public:
    static void registerLogger(CloudLogger* logger);
    static CloudLogger* get();
    static void upload(const std::string& category, const std::string& message);

private:
    static CloudLogger* instance;
};

} // namespace cloudlogger

#endif // CLOUD_LOGGER_BRIDGE_HPP
