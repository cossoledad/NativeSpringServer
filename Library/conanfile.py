from __future__ import annotations

import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy


class CloudLoggerNativeConan(ConanFile):
    name = "cloudlogger-native"
    version = "0.1.1"
    package_type = "shared-library"

    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "native/*"
    generators = "CMakeToolchain", "CMakeDeps"

    def layout(self):
        cmake_layout(self, build_folder="build/conan")

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="native")
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="*.hpp",
            src=os.path.join(self.source_folder, "native", "include"),
            dst=os.path.join(self.package_folder, "include"),
        )

        native_lib_dir = os.path.join(self.source_folder, "target", "native", "lib")
        for pattern in ("*.so", "*.dylib", "*.dll", "*.a", "*.lib"):
            copy(self, pattern=pattern, src=native_lib_dir, dst=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        # Foundation side links against bridge lib. JNI lib is shipped for runtime use.
        self.cpp_info.libs = ["cloudlogger_bridge"]
