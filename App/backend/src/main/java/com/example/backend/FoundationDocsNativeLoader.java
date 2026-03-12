package com.example.backend;

import java.time.OffsetDateTime;
import java.nio.file.Path;

public final class FoundationDocsNativeLoader {

    private static volatile boolean loaded = false;

    private FoundationDocsNativeLoader() {}

    public static void load() {
        log("load() invoked, loaded=%s", loaded);
        if (loaded) {
            log("load() skipped because foundation docs JNI is already loaded");
            return;
        }
        synchronized (FoundationDocsNativeLoader.class) {
            if (loaded) {
                log("load() skipped inside lock because foundation docs JNI is already loaded");
                return;
            }
            String libDir = System.getProperty(
                "foundation.docs.lib.dir",
                Path.of("..", "foundation", "build", "native", "lib").toAbsolutePath().normalize().toString()
            );
            String libPath = Path.of(libDir, "libfoundation_docs_jni.so").toAbsolutePath().normalize().toString();
            log("resolved foundation.docs.lib.dir=%s", libDir);
            log("about to System.load %s", libPath);
            System.load(libPath);
            log("System.load succeeded for %s", libPath);
            loaded = true;
            log("foundation docs JNI loader completed");
        }
    }

    private static void log(String format, Object... args) {
        System.out.printf(
            "[%s][pid=%s][thread=%s][FoundationDocsNativeLoader] %s%n",
            OffsetDateTime.now(),
            ProcessHandle.current().pid(),
            Thread.currentThread().getName(),
            String.format(format, args)
        );
    }
}
