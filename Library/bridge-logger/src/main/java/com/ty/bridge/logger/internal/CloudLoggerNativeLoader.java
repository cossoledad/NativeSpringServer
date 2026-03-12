package com.ty.bridge.logger.internal;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.OffsetDateTime;

final class CloudLoggerNativeLoader {

    private static final String[] LIB_FILES = {
        "libcloudlogger_bridge.so",
        "libcloudlogger_jni.so"
    };
    private static final String SHARED_DIR_PROPERTY = "com.ty.bridge.native.dir";
    private static final String SHARED_LOADED_PROPERTY = "com.ty.bridge.native.loaded";
    private static final String SHARED_LOCK = "com.ty.bridge.native.load.lock";

    private static volatile boolean loaded = false;

    private CloudLoggerNativeLoader() {
    }

    static void load() {
        log("load() invoked, loaded=%s, sharedLoaded=%s", loaded, System.getProperty(SHARED_LOADED_PROPERTY));
        if (loaded) {
            log("load() short-circuited because loader state is already true");
            return;
        }
        synchronized (SHARED_LOCK.intern()) {
            log("entered shared native load lock");
            if (loaded) {
                log("load() short-circuited inside lock because loader state is already true");
                return;
            }
            if (Boolean.getBoolean(SHARED_LOADED_PROPERTY)) {
                log("shared loaded property is already true; skipping System.load and marking loader as loaded");
                loaded = true;
                return;
            }

            String explicitDir = System.getenv("CLOUD_LOGGER_NATIVE_DIR");
            log("resolved CLOUD_LOGGER_NATIVE_DIR=%s", explicitDir);
            if (explicitDir != null && !explicitDir.isBlank()) {
                loadFromDirectory(Path.of(explicitDir));
                log("native libraries loaded from explicit directory");
                System.setProperty(SHARED_DIR_PROPERTY, explicitDir);
                System.setProperty(SHARED_LOADED_PROPERTY, Boolean.TRUE.toString());
                loaded = true;
                log("native loader completed via explicit directory; sharedDir=%s", explicitDir);
                return;
            }

            String sharedDir = System.getProperty(SHARED_DIR_PROPERTY);
            log("resolved shared native dir property=%s", sharedDir);
            if (sharedDir != null && !sharedDir.isBlank()) {
                loadFromDirectory(Path.of(sharedDir));
                log("native libraries loaded from existing shared directory");
                System.setProperty(SHARED_LOADED_PROPERTY, Boolean.TRUE.toString());
                loaded = true;
                log("native loader completed via shared directory; sharedDir=%s", sharedDir);
                return;
            }

            Path extractedDir = loadFromResources();
            log("native libraries loaded from packaged resources into %s", extractedDir);
            System.setProperty(SHARED_DIR_PROPERTY, extractedDir.toString());
            System.setProperty(SHARED_LOADED_PROPERTY, Boolean.TRUE.toString());
            loaded = true;
            log(
                "native loader completed via resources; sharedDir=%s, sharedLoaded=%s",
                extractedDir,
                System.getProperty(SHARED_LOADED_PROPERTY)
            );
        }
    }

    private static void loadFromDirectory(Path dir) {
        log("loadFromDirectory(%s)", dir);
        for (String lib : LIB_FILES) {
            Path libPath = dir.resolve(lib).toAbsolutePath().normalize();
            log(
                "about to System.load %s (exists=%s, size=%s)",
                libPath,
                Files.exists(libPath),
                sizeIfExists(libPath)
            );
            System.load(libPath.toString());
            log("System.load succeeded for %s", libPath);
        }
    }

    private static Path loadFromResources() {
        try {
            log("loadFromResources() started");
            Path tempDir = Path.of(
                System.getProperty("java.io.tmpdir"),
                "cloudlogger-native-shared"
            ).toAbsolutePath().normalize();
            Files.createDirectories(tempDir);
            tempDir.toFile().deleteOnExit();
            log("using shared extraction directory %s", tempDir);

            for (String lib : LIB_FILES) {
                String resource = "/native/lib/" + lib;
                Path target = tempDir.resolve(lib);
                log("copying resource %s to %s", resource, target);
                try (InputStream in = CloudLoggerNativeLoader.class.getResourceAsStream(resource)) {
                    if (in == null) {
                        logError("resource not found: %s", resource);
                        throw new IllegalStateException("Native library resource not found: " + resource);
                    }
                    Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
                }
                target.toFile().deleteOnExit();
                log("copied %s (size=%d)", target, Files.size(target));
                log("about to System.load extracted library %s", target.toAbsolutePath().normalize());
                System.load(target.toAbsolutePath().normalize().toString());
                log("System.load succeeded for extracted library %s", target.toAbsolutePath().normalize());
            }
            return tempDir;
        } catch (IOException e) {
            logError("loadFromResources() failed with IOException: %s", e);
            throw new RuntimeException("Failed to load cloud-logger native libraries", e);
        } catch (RuntimeException e) {
            logError("loadFromResources() failed with RuntimeException: %s", e);
            throw e;
        }
    }

    private static long sizeIfExists(Path path) {
        try {
            return Files.exists(path) ? Files.size(path) : -1L;
        } catch (IOException e) {
            return -2L;
        }
    }

    private static void log(String format, Object... args) {
        System.out.printf(
            "[%s][pid=%s][thread=%s][CloudLoggerNativeLoader] %s%n",
            OffsetDateTime.now(),
            ProcessHandle.current().pid(),
            Thread.currentThread().getName(),
            String.format(format, args)
        );
    }

    private static void logError(String format, Object... args) {
        System.err.printf(
            "[%s][pid=%s][thread=%s][CloudLoggerNativeLoader][ERROR] %s%n",
            OffsetDateTime.now(),
            ProcessHandle.current().pid(),
            Thread.currentThread().getName(),
            String.format(format, args)
        );
    }
}
