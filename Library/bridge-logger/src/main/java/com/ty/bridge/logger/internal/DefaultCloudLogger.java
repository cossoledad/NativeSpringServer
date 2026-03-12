package com.ty.bridge.logger.internal;

import com.example.cloudlogger.bridge.CloudLogger;
import com.ty.bridge.logger.Slf4jBridgeLogger;

public class DefaultCloudLogger extends CloudLogger {
    private final Slf4jBridgeLogger logger = new Slf4jBridgeLogger();

    @Override
    public void info(String category, String message) {
        logger.info(category, message);
    }

    @Override
    public void warn(String category, String message) {
        logger.warn(category, message);
    }

    @Override
    public void error(String category, String message) {
        logger.error(category, message);
    }
}
