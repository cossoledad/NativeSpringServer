#include "cloud_logger_bridge.hpp"

namespace cloudlogger {

CloudLogger* CloudLoggerRegistry::instance = nullptr;

void CloudLoggerRegistry::registerLogger(CloudLogger* logger) {
    instance = logger;
}

CloudLogger* CloudLoggerRegistry::get() {
    return instance;
}

void CloudLoggerRegistry::upload(const std::string& category, const std::string& message) {
    if (instance != nullptr) {
        instance->upload(category, message);
    }
}

} // namespace cloudlogger
