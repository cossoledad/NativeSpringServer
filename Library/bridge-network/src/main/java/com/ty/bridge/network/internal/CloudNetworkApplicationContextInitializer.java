package com.ty.bridge.network.internal;

import com.example.cloudlogger.bridge.CloudNetworkRegistry;
import java.time.OffsetDateTime;
import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;

public class CloudNetworkApplicationContextInitializer
    implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    private static volatile boolean initialized = false;
    private static DefaultCloudNetwork pinnedNetwork;

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        log(
            "initialize() invoked, initialized=%s, appContext=%s",
            initialized,
            applicationContext.getClass().getName()
        );
        if (initialized) {
            log("initializer skipped because network bridge is already initialized");
            return;
        }
        synchronized (CloudNetworkApplicationContextInitializer.class) {
            if (initialized) {
                log("initializer skipped inside lock because network bridge is already initialized");
                return;
            }
            log("calling CloudNetworkNativeLoader.load()");
            CloudNetworkNativeLoader.load();
            log("constructing DefaultCloudNetwork director instance");
            pinnedNetwork = new DefaultCloudNetwork();
            log(
                "registering DefaultCloudNetwork into CloudNetworkRegistry, identity=%s",
                System.identityHashCode(pinnedNetwork)
            );
            CloudNetworkRegistry.registerNetwork(pinnedNetwork);
            initialized = true;
            log("network bridge initialization completed");
        }
    }

    private static void log(String format, Object... args) {
        System.out.printf(
            "[%s][pid=%s][thread=%s][CloudNetworkInitializer] %s%n",
            OffsetDateTime.now(),
            ProcessHandle.current().pid(),
            Thread.currentThread().getName(),
            String.format(format, args)
        );
    }
}
