# native-spring-server-bridge Architecture

## 1. reference 项目分析
参考项目：`reference/JniMvnLib/CloudLogger`

核心设计分成 4 层：
1. C++ Bridge 层：定义 `CloudLogger` 抽象类与 `CloudLoggerRegistry`，供 foundation 侧调用。
2. SWIG/JNI 绑定层：通过 `cloud_logger.i` 生成 Java 可调用类 + JNI so。
3. Java 实现层：继承 SWIG 生成的 `CloudLogger`，实现 `upload` 逻辑。
4. Spring 自动装配层：在 Spring 启动时加载 native 库并把 Java logger 注册到 C++ registry。

这套设计满足“foundation 与 backend 解耦”：
- foundation 只依赖 C++ 头文件和桥接调用。
- backend 只通过 Maven 引入 Java 包，即可在启动时把日志上报能力注入到 C++ 层。

当前模拟场景扩展：
- 主项目仍保持“日志库”职责，不在日志 bridge 中引入业务计算接口。
- `App/foundation` 额外模拟一个“计算库”：
  - C++ `MathApi::add(int, int)`
  - SWIG/JNI 导出为 Java `com.example.foundation.math.MathApi`
  - 计算内部通过 Conan2 引入的日志库 `cloudlogger-native` 调用 `CloudLoggerRegistry.upload(...)`
- `App/backend` 作为服务层：
  - 通过 Maven 引入日志库 Java 实现（保证日志链路正确）
  - 通过 foundation 生成的 SWIG Java API 调用计算库
  - 暴露 `GET /add?a=&b=`

## 2. 本项目目标框架
目录与职责：

```text
.
├── App
│   ├── foundation                           # Conan2 消费 native 包的 C++ 应用侧模块
│   └── backend                              # Maven 消费 Java 包的 Spring Boot 主应用
├── Library
│   ├── conanfile.py                         # Native Conan recipe
│   ├── bridge-core
│   │   ├── native                           # C++ bridge + SWIG
│   │   └── pom.xml                          # core 模块（com.ty:native-spring-server-bridge）
│   ├── bridge-logger                        # Java 日志实现模块（Slf4j）
│   ├── bridge-network                       # 网络模块（String GET/POST）
│   ├── pom.xml                              # parent 聚合 pom
│   └── tasks.py                             # invoke 构建脚本
├── Script
│   └── generate_vscode_config.sh            # 生成本机专用 VS Code 配置
├── Tools
│   └── invoke_support.py                    # invoke 公共输出、颜色、子任务调用工具
└── ARCHITECTURE.md
```

构建产物约定：
- SWIG 生成 Java：`Library/bridge-core/target/generated-sources/cloudlogger-swig`
- Native so 输出：`Library/bridge-core/target/native/lib`
- 最终分发：`Library/dist/native`、`Library/dist/java`

## 3. 构建链路
1. `Library/bridge-core/native/CMakeLists.txt` 构建：
   - `libcloudlogger_bridge.so`
   - `libcloudlogger_jni.so`
   - SWIG Java 绑定代码
2. `Library/tasks.py::java_build` 先编译 SWIG Java classes，再由 Maven 构建多模块 Java 包。
3. core Maven 将 `Library/bridge-core/target/native/lib` 作为资源打进 jar（路径：`native/lib`）。
4. logger 模块中的 Spring 初始化器在应用启动时加载 native 并完成 registry 注册。

## 4. invoke 基础命令
- `Tools/invoke_support.py` 提供统一的任务头、成功/失败提示、颜色输出和子任务调用封装。
  - 默认会在有真实终端时自动启用 PTY，保证 Maven/Conan/CMake 日志实时输出。
  - 可通过 `INVOKE_FORCE_PTY=1` 强制开启，或 `INVOKE_DISABLE_PTY=1` 强制关闭。
- `App/`、`App/backend/`、`App/foundation/` 都提供统一的 `deps` / `clean` / `build` / `rebuild`。
- 在 `App/` 目录执行 `invoke build`，即可串联 foundation 与 backend，无需再逐层 `cd`。
- 以下命令都在 `Library/` 目录执行。
- `invoke native-clean`：清理 native 产物
- `invoke native-build`：构建 C++/SWIG
- `invoke native-package`：产出 `dist/native`（headers + so）
- `invoke java-build`：构建多模块 Java jar（自动触发 native-build + SWIG Java 编译）
- `invoke java-package`：产出 `dist/java/*.jar`
- `invoke clean`：清理全部构建目录
- `invoke build`：完整构建 native + java
- `invoke package`：完整打包到 dist
- `invoke conan-remote`：配置 Conan2 远端（默认 `conan-pr`）
- `invoke conan-create`：本地创建 native Conan 包
- `invoke conan-upload`：上传本地 Conan 包到远端
- `invoke conan-publish`：一键完成 remote + create + upload
- `invoke java-publish`：发布 Java 核心库到 Maven 仓库（默认 `maven-releases`）
  - 认证信息来自本机 `~/.m2/settings.xml` 的 `<server id="maven-releases">...`
- `invoke release-publish --version X.Y.Z`：同版本发布 Conan + Maven，并持久更新 `Library/pom.xml` 的 `<revision>`
- `invoke app-foundation`：执行 Conan2 消费链路（install + build）
- `invoke app-backend`：执行 Maven 消费链路（spring-boot:run）
  - 兼容旧名字：`test-foundation`、`test-backend`

## 5. 说明
当前实现是“基础框架版本”：
- 已具备 reference 项目的关键解耦机制与自动装配路径。
- 现在已按职责拆成 `Library` 与 `App` 两层，后续扩展边界更清晰。
- Conan2 发布目标默认仓库：`http://172.27.128.1:19091/repository/conan-pr/`
- Maven 发布目标默认仓库：`http://172.27.128.1:19091/repository/maven-releases/`
