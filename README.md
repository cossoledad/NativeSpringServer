# NativeSpringServer

一个用于验证 `Spring Boot + JNI/SWIG + Conan/CMake` 协作方式的示例工程。

项目重点不是单一语言实现，而是把三层能力拆开：
- `Library`：基础库层，负责 C++ bridge、SWIG/JNI、Java 封装和发布脚本
- `App`：主应用层，包含 backend 服务和 foundation 本地库消费者
- `Tools` / `Script`：统一的构建脚本工具和本机开发环境配置生成脚本

## 环境要求

- Linux 开发环境
- JDK 21
- Maven
- Python 3
- Conan 2
- invoke
- CMake
- GCC / G++
- SWIG
- GDB（如果需要调试 C++ / JNI）

## 环境安装

### 1. 使用 apt 安装基础构建工具

建议先安装系统级构建依赖：

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  cmake \
  ninja-build \
  gdb \
  swig \
  pkg-config \
  curl \
  zip \
  unzip
```

说明：
- `build-essential`：提供 `gcc/g++/make`
- `cmake`：用于 native 和 Conan 生成后的 CMake 构建
- `ninja-build`：可选，加快 CMake 构建
- `gdb`：用于调试 foundation 或 JNI
- `swig`：用于生成 JNI / Java 绑定

### 2. 使用 SDKMAN 安装 Java

本项目 Java 侧要求 JDK 21，推荐通过 `sdkman` 安装。

安装 SDKMAN：

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
```

安装并启用 Java 21：

```bash
sdk list java
sdk install java 21-tem
sdk use java 21-tem
```

如果你希望默认使用该版本：

```bash
sdk default java 21-tem
```

验证：

```bash
java -version
javac -version
```

### 3. 安装 Maven

如果机器上还没有 Maven：

```bash
sudo apt install -y maven
mvn -version
```

### 4. 创建 Python 虚拟环境并安装 Conan2 / Invoke

本项目的 Python 工具链建议通过 `venv` 单独隔离。

创建虚拟环境：

```bash
python3 -m venv /home/ganjb/pyvenv/conan2py
```

激活虚拟环境：

```bash
source /home/ganjb/pyvenv/conan2py/bin/activate
```

安装依赖：

```bash
pip install --upgrade pip
pip install conan invoke
```

验证：

```bash
conan --version
invoke --version
```

如果你希望每次打开 shell 自动进入这个环境，可以把下面这行写进 `~/.bashrc`：

```bash
source /home/ganjb/pyvenv/conan2py/bin/activate
```

## 项目架构

当前目录结构：

```text
.
├── App
│   ├── backend
│   │   ├── pom.xml
│   │   └── tasks.py
│   ├── foundation
│   │   ├── CMakeLists.txt
│   │   ├── conanfile.txt
│   │   └── tasks.py
│   └── tasks.py
├── Library
│   ├── conanfile.py
│   ├── native
│   ├── src
│   ├── pom.xml
│   └── tasks.py
├── Script
│   └── generate_vscode_config.sh
├── Tools
│   └── invoke_support.py
├── ARCHITECTURE.md
└── README.md
```

### Library

`Library` 是基础库工程，承担以下职责：

- C++ bridge 层
- SWIG/JNI 绑定生成
- Java 封装与 Spring 自动装配
- Conan 包构建与发布
- Maven 包构建与发布

关键目录：
- `Library/native`：C++ bridge 与 SWIG 接口
- `Library/src/impl-java`：Java 实现层
- `Library/src/main/resources`：Spring 自动装配资源
- `Library/tasks.py`：库层 invoke 任务入口

### App

`App` 是主应用层，表示实际运行和联调的业务侧。

其中：
- `App/backend`：Spring Boot 服务
- `App/foundation`：C++/JNI foundation 库消费者
- `App/tasks.py`：聚合 `backend` 与 `foundation` 的构建入口

### Tools

`Tools/invoke_support.py` 提供统一的 invoke 工具能力：

- 标准化日志头
- 成功 / 失败输出
- 颜色输出
- 跨子项目 invoke 调用封装
- 按终端情况自动切换 PTY，尽量保证日志实时输出

`Tools/project_config.py` 提供统一的项目配置读取能力：
- 优先读取 `Config/project-config.json`（机器本地覆盖）
- 回退读取 `Config/project-config-template.json`（仓库默认模板）
- 上传相关默认参数（Conan/Maven）与 Maven settings 均从此处获取

### Script

`Script/generate_vscode_config.sh` 用于在每台机器本地生成 `.vscode` 配置。

因为 Java、GDB、工作目录等环境因机器而异，所以 VS Code 配置不直接入库，而是本地生成。

`Script/generate_maven_settings.sh` 用于基于模板生成项目内 Maven settings：
- 模板：`Config/maven-settings-template.xml`
- 当前机器配置：`Config/maven-settings.xml`
- 默认本地仓库：`${repo}/.m2/repository`（避免污染用户目录下全局仓库）

## 常用命令

### App 层

在仓库根目录执行：

```bash
invoke --search-root App deps
invoke --search-root App clean
invoke --search-root App build
invoke --search-root App rebuild
```

或者进入 `App` 目录后执行：

```bash
cd App
invoke deps
invoke clean
invoke build
invoke rebuild
```

### Library 层

```bash
cd Library
invoke native-build
invoke java-build
invoke build
invoke package
```

## VS Code 配置生成

由于 `.vscode` 被加入忽略，需要每台机器手动生成一次：

```bash
bash Script/generate_vscode_config.sh
```

它会生成：
- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/launch.json`

支持：
- 直接启动 App 服务
- 调试 App 服务（Java）
- 启动 App 服务并调试 foundation / JNI（C++）
- 单独调试 backend
- 单独调试 foundation

说明：
- `Script/generate_vscode_config.sh` 会从 `Config/project-config*.json` 读取 `PROJECT_MAVEN_SETTINGS`
- 若该值非空，会写入 `.vscode/settings.json` 的 `java.configuration.maven.userSettings`

建议先执行：

```bash
bash Script/generate_maven_settings.sh
bash Script/generate_vscode_config.sh
```

## 补充说明

- 如果你需要发布 Maven 包，可能还需要本机 `~/.m2/settings.xml` 中配置仓库认证
- 如果你需要使用 Conan 远端，确保本机 Conan remote 已正确配置
- 如果遇到 JNI / C++ 调试问题，优先检查 `gdb`、`LD_LIBRARY_PATH`、`foundation.math.lib.dir` 是否正确
