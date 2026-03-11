package com.example.cloudlogger;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

final class CloudLoggerNativeLoader {

    private static final String[] LIB_FILES = {
        "libcloudlogger_bridge.so",
        "libcloudlogger_jni.so"
    };

    private static volatile boolean loaded = false;

    private CloudLoggerNativeLoader() {
    }

    static void load() {
        if (loaded) {
            return;
        }
        synchronized (CloudLoggerNativeLoader.class) {
            if (loaded) {
                return;
            }

            String explicitDir = System.getenv("CLOUD_LOGGER_NATIVE_DIR");
            if (explicitDir != null && !explicitDir.isBlank()) {
                loadFromDirectory(Path.of(explicitDir));
                loaded = true;
                return;
            }

            loadFromResources();
            loaded = true;
        }
    }

    private static void loadFromDirectory(Path dir) {
        for (String lib : LIB_FILES) {
            System.load(dir.resolve(lib).toAbsolutePath().toString());
        }
    }

    private static void loadFromResources() {
        try {
            Path tempDir = Files.createTempDirectory("cloudlogger-native-");
            tempDir.toFile().deleteOnExit();

            for (String lib : LIB_FILES) {
                String resource = "/native/lib/" + lib;
                Path target = tempDir.resolve(lib);
                try (InputStream in = CloudLoggerNativeLoader.class.getResourceAsStream(resource)) {
                    if (in == null) {
                        throw new IllegalStateException("Native library resource not found: " + resource);
                    }
                    Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
                }
                target.toFile().deleteOnExit();
                System.load(target.toAbsolutePath().toString());
            }
        } catch (IOException e) {
            throw new RuntimeException("Failed to load cloud-logger native libraries", e);
        }
    }
}
