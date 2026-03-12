#include "cloud_logger_bridge.hpp"

namespace cloudlogger {

CloudLogger* CloudLoggerRegistry::instance = nullptr;

void CloudLoggerRegistry::registerLogger(CloudLogger* logger) {
    instance = logger;
}

CloudLogger* CloudLoggerRegistry::get() {
    return instance;
}

void CloudLoggerRegistry::info(const std::string& category, const std::string& message) {
    if (instance != nullptr) {
        instance->info(category, message);
    }
}

void CloudLoggerRegistry::warn(const std::string& category, const std::string& message) {
    if (instance != nullptr) {
        instance->warn(category, message);
    }
}

void CloudLoggerRegistry::error(const std::string& category, const std::string& message) {
    if (instance != nullptr) {
        instance->error(category, message);
    }
}

void CloudLoggerRegistry::upload(const std::string& category, const std::string& message) {
    info(category, message);
}

} // namespace cloudlogger
