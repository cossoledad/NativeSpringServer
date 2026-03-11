package com.example.backend;

import java.nio.file.Path;

public final class FoundationMathNativeLoader {

    private static volatile boolean loaded = false;

    private FoundationMathNativeLoader() {}

    public static void load() {
        if (loaded) {
            return;
        }
        synchronized (FoundationMathNativeLoader.class) {
            if (loaded) {
                return;
            }
            String libDir = System.getProperty(
                "foundation.math.lib.dir",
                Path.of("..", "foundation", "build", "native", "lib").toAbsolutePath().normalize().toString()
            );
            String libPath = Path.of(libDir, "libfoundation_math_jni.so").toAbsolutePath().normalize().toString();
            System.load(libPath);
            loaded = true;
        }
    }
}
