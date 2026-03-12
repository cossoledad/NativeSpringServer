package com.example.backend;

import java.nio.file.Path;

public final class FoundationDocsNativeLoader {

    private static volatile boolean loaded = false;

    private FoundationDocsNativeLoader() {}

    public static void load() {
        if (loaded) {
            return;
        }
        synchronized (FoundationDocsNativeLoader.class) {
            if (loaded) {
                return;
            }
            String libDir = System.getProperty(
                "foundation.docs.lib.dir",
                Path.of("..", "foundation", "build", "native", "lib").toAbsolutePath().normalize().toString()
            );
            String libPath = Path.of(libDir, "libfoundation_docs_jni.so").toAbsolutePath().normalize().toString();
            System.load(libPath);
            loaded = true;
        }
    }
}
