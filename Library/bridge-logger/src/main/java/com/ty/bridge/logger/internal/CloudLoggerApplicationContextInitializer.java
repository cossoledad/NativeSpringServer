package com.ty.bridge.logger.internal;

import com.example.cloudlogger.bridge.CloudLoggerRegistry;
import java.time.OffsetDateTime;
import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;

public class CloudLoggerApplicationContextInitializer
    implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    private static volatile boolean initialized = false;
    private static DefaultCloudLogger pinnedLogger;

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        log(
            "initialize() invoked, initialized=%s, appContext=%s",
            initialized,
            applicationContext.getClass().getName()
        );
        if (initialized) {
            log("initializer skipped because logger bridge is already initialized");
            return;
        }
        synchronized (CloudLoggerApplicationContextInitializer.class) {
            if (initialized) {
                log("initializer skipped inside lock because logger bridge is already initialized");
                return;
            }
            log("calling CloudLoggerNativeLoader.load()");
            CloudLoggerNativeLoader.load();
            log("constructing DefaultCloudLogger director instance");
            pinnedLogger = new DefaultCloudLogger();
            log(
                "registering DefaultCloudLogger into CloudLoggerRegistry, identity=%s",
                System.identityHashCode(pinnedLogger)
            );
            CloudLoggerRegistry.registerLogger(pinnedLogger);
            initialized = true;
            log("logger bridge initialization completed");
        }
    }

    private static void log(String format, Object... args) {
        System.out.printf(
            "[%s][pid=%s][thread=%s][CloudLoggerInitializer] %s%n",
            OffsetDateTime.now(),
            ProcessHandle.current().pid(),
            Thread.currentThread().getName(),
            String.format(format, args)
        );
    }
}
