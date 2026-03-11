package com.example.cloudlogger;

import com.example.cloudlogger.bridge.CloudLoggerRegistry;
import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;

public class CloudLoggerApplicationContextInitializer
    implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    private static volatile boolean initialized = false;
    private static DefaultCloudLogger pinnedLogger;

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        if (initialized) {
            return;
        }
        synchronized (CloudLoggerApplicationContextInitializer.class) {
            if (initialized) {
                return;
            }
            CloudLoggerNativeLoader.load();
            pinnedLogger = new DefaultCloudLogger();
            CloudLoggerRegistry.registerLogger(pinnedLogger);
            initialized = true;
            System.out.println("CloudLogger bridge initialized successfully!");
        }
    }
}
