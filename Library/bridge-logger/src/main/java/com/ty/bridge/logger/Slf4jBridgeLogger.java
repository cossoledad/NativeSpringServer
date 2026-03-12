package com.ty.bridge.logger;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Slf4jBridgeLogger {
    private static final Logger LOGGER = LoggerFactory.getLogger(Slf4jBridgeLogger.class);

    public void info(String category, String message) {
        LOGGER.info("[{}] {}", category, message);
    }

    public void warn(String category, String message) {
        LOGGER.warn("[{}] {}", category, message);
    }

    public void error(String category, String message) {
        LOGGER.error("[{}] {}", category, message);
    }
}
