#ifndef CLOUD_LOGGER_BRIDGE_HPP
#define CLOUD_LOGGER_BRIDGE_HPP

#include <string>

namespace cloudlogger {

class CloudLogger {
public:
    virtual ~CloudLogger() = default;
    virtual void info(const std::string& category, const std::string& message) = 0;
    virtual void warn(const std::string& category, const std::string& message) = 0;
    virtual void error(const std::string& category, const std::string& message) = 0;
};

class CloudLoggerRegistry {
public:
    static void registerLogger(CloudLogger* logger);
    static CloudLogger* get();
    static void info(const std::string& category, const std::string& message);
    static void warn(const std::string& category, const std::string& message);
    static void error(const std::string& category, const std::string& message);
    // Backward-compatible facade used by existing C++ callers.
    static void upload(const std::string& category, const std::string& message);

private:
    static CloudLogger* instance;
};

} // namespace cloudlogger

#endif // CLOUD_LOGGER_BRIDGE_HPP
