package com.example.cloudlogger;

import com.example.cloudlogger.bridge.CloudLogger;

import java.time.Instant;

public class DefaultCloudLogger extends CloudLogger {

    @Override
    public void upload(String category, String message) {
        // Demo implementation. Replace with real cloud sink in production.
        System.out.printf("[CloudLogger][%s][%s] %s%n", Instant.now(), category, message);
    }
}
