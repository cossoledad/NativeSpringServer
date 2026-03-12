# Foundation App (Conan2 Consumer)

This test project simulates a standalone foundation math library:
- foundation 提供 `MathApi::add(a, b)`，并通过 SWIG 导出给 Java/backend 使用。
- foundation 内部通过 Conan2 引入日志库 `cloudlogger-native`，并在计算时调用 `CloudLoggerRegistry.upload(...)`。

## Prerequisites

- `cloudlogger-native/0.1.1` is already uploaded to remote `conan-pr`.
- Conan remote exists and points to your server:

```bash
conan remote add conan-pr http://172.30.0.1:19091/repository/conan-pr/ --force
```

## Build

Preferred invoke workflow:

```bash
cd App/foundation
invoke deps
invoke build
```

Or from App root:

```bash
cd App
invoke build
```

Direct Conan/CMake run:

```bash
cd App/foundation
conan install . --build=missing -r conan-pr -s build_type=Release -of build
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```
