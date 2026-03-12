package com.ty.bridge.network.internal;

import com.example.cloudlogger.bridge.CloudNetworkRegistry;
import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;

public class CloudNetworkApplicationContextInitializer
    implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    private static volatile boolean initialized = false;
    private static DefaultCloudNetwork pinnedNetwork;

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        if (initialized) {
            return;
        }
        synchronized (CloudNetworkApplicationContextInitializer.class) {
            if (initialized) {
                return;
            }
            CloudNetworkNativeLoader.load();
            pinnedNetwork = new DefaultCloudNetwork();
            CloudNetworkRegistry.registerNetwork(pinnedNetwork);
            initialized = true;
        }
    }
}
