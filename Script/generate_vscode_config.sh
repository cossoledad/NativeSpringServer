#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VSCODE_DIR="${REPO_ROOT}/.vscode"
BACKEND_POM="${REPO_ROOT}/App/backend/pom.xml"

BLUE='\033[1;34m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
RESET='\033[0m'

log_step() {
  printf '\n%b== %s ==%b\n' "${BLUE}" "$1" "${RESET}"
}

log_info() {
  printf '%b> %s%b\n' "${BLUE}" "$1" "${RESET}"
}

log_warn() {
  printf '%b! %s%b\n' "${YELLOW}" "$1" "${RESET}"
}

log_ok() {
  printf '%bOK %s%b\n' "${GREEN}" "$1" "${RESET}"
}

log_err() {
  printf '%bERR %s%b\n' "${RED}" "$1" "${RESET}" 1>&2
}

xml_text() {
  local tag="$1"
  local file="$2"
  sed -n "0,/<${tag}>/{s/.*<${tag}>\\([^<]*\\)<\\/${tag}>.*/\\1/p;}" "${file}" | head -n 1
}

JAVA_BIN="${JAVA_BIN:-$(command -v java || true)}"
GDB_BIN="${GDB_BIN:-$(command -v gdb || true)}"
BACKEND_ARTIFACT_ID="$(xml_text artifactId "${BACKEND_POM}")"
BACKEND_VERSION="$(xml_text version "${BACKEND_POM}")"
BACKEND_MAIN_CLASS="com.example.backend.BackendSmokeApplication"
BACKEND_JAR_REL="App/backend/target/${BACKEND_ARTIFACT_ID}-${BACKEND_VERSION}.jar"
FOUNDATION_LIB_DIR_REL="App/foundation/build/native/lib"
FOUNDATION_EXE_REL="App/foundation/build/foundation_smoke"

if [[ -z "${BACKEND_ARTIFACT_ID}" || -z "${BACKEND_VERSION}" ]]; then
  log_err "无法从 ${BACKEND_POM} 解析 backend artifactId/version"
  exit 1
fi

if [[ -z "${JAVA_BIN}" ]]; then
  JAVA_BIN="java"
  log_warn "未检测到 java，可在运行前通过 JAVA_BIN 环境变量覆盖"
fi

if [[ -z "${GDB_BIN}" ]]; then
  GDB_BIN="gdb"
  log_warn "未检测到 gdb，可在运行前通过 GDB_BIN 环境变量覆盖"
fi

mkdir -p "${VSCODE_DIR}"

log_step "Generate settings.json"
cat > "${VSCODE_DIR}/settings.json" <<'EOF'
{
  "files.exclude": {
    "**/.DS_Store": true,
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/build": true,
    "**/target": true,
    "**/dist": true,
    "**/CMakeFiles": true
  },
  "files.watcherExclude": {
    "**/.git/**": true,
    "**/__pycache__/**": true,
    "**/build/**": true,
    "**/target/**": true,
    "**/dist/**": true,
    "**/CMakeFiles/**": true
  },
  "search.exclude": {
    "**/__pycache__": true,
    "**/build": true,
    "**/target": true,
    "**/dist": true
  },
  "java.import.exclusions": [
    "Library/**",
    "**/target/**",
    "**/build/**",
    "**/dist/**"
  ],
  "java.configuration.updateBuildConfiguration": "interactive",
  "java.debug.settings.onBuildFailureProceed": true,
  "java.compile.nullAnalysis.mode": "automatic",
  "cmake.configureOnOpen": false
}
EOF
log_ok "Wrote .vscode/settings.json"

log_step "Generate tasks.json"
cat > "${VSCODE_DIR}/tasks.json" <<'EOF'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Config: Generate VS Code files",
      "type": "shell",
      "command": "${workspaceFolder}/Script/generate_vscode_config.sh",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "App: deps",
      "type": "shell",
      "command": "invoke --search-root App deps",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "App: clean",
      "type": "shell",
      "command": "invoke --search-root App clean",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "App: build",
      "type": "shell",
      "command": "INVOKE_FORCE_PTY=1 invoke --search-root App build",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "App: rebuild",
      "type": "shell",
      "command": "INVOKE_FORCE_PTY=1 invoke --search-root App rebuild",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "Backend: build",
      "type": "shell",
      "command": "INVOKE_FORCE_PTY=1 invoke --search-root App/backend build",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "Backend: debug classpath",
      "type": "shell",
      "command": "mvn -q -f App/backend/pom.xml dependency:copy-dependencies -DincludeScope=runtime -DoutputDirectory=target/dependency",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "dependsOn": "Backend: build",
      "problemMatcher": []
    },
    {
      "label": "Foundation: build",
      "type": "shell",
      "command": "INVOKE_FORCE_PTY=1 invoke --search-root App/foundation build",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "App: debug classpath",
      "type": "shell",
      "command": "mvn -q -f App/backend/pom.xml dependency:copy-dependencies -DincludeScope=runtime -DoutputDirectory=target/dependency",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "dependsOn": "App: build",
      "problemMatcher": []
    }
  ]
}
EOF

python3 - <<EOF
from pathlib import Path
path = Path("${VSCODE_DIR}/tasks.json")
text = path.read_text(encoding="utf-8")
text = text.replace("backend-smoke-0.1.2-SNAPSHOT.jar", "${BACKEND_ARTIFACT_ID}-${BACKEND_VERSION}.jar")
path.write_text(text, encoding="utf-8")
EOF
log_ok "Wrote .vscode/tasks.json"

log_step "Generate launch.json"
cat > "${VSCODE_DIR}/launch.json" <<EOF
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "App Service (Run/Debug Java)",
      "type": "java",
      "request": "launch",
      "mainClass": "${BACKEND_MAIN_CLASS}",
      "cwd": "\${workspaceFolder}/App/backend",
      "console": "integratedTerminal",
      "vmArgs": "-Dfoundation.math.lib.dir=\${workspaceFolder}/${FOUNDATION_LIB_DIR_REL}",
      "classPaths": [
        "\${workspaceFolder}/App/backend/target/classes",
        "\${workspaceFolder}/App/backend/target/dependency/*"
      ],
      "preLaunchTask": "App: debug classpath"
    },
    {
      "name": "App Service (Debug Foundation JNI C++)",
      "type": "cppdbg",
      "request": "launch",
      "program": "${JAVA_BIN}",
      "args": [
        "-Dfoundation.math.lib.dir=\${workspaceFolder}/${FOUNDATION_LIB_DIR_REL}",
        "-jar",
        "\${workspaceFolder}/${BACKEND_JAR_REL}"
      ],
      "cwd": "\${workspaceFolder}",
      "environment": [
        {
          "name": "LD_LIBRARY_PATH",
          "value": "\${workspaceFolder}/${FOUNDATION_LIB_DIR_REL}:\${env:LD_LIBRARY_PATH}"
        }
      ],
      "MIMode": "gdb",
      "miDebuggerPath": "${GDB_BIN}",
      "externalConsole": false,
      "stopAtEntry": false,
      "setupCommands": [
        {
          "description": "Enable pretty printing",
          "text": "-enable-pretty-printing",
          "ignoreFailures": true
        }
      ],
      "preLaunchTask": "App: build"
    },
    {
      "name": "Backend (Debug Java)",
      "type": "java",
      "request": "launch",
      "mainClass": "${BACKEND_MAIN_CLASS}",
      "cwd": "\${workspaceFolder}/App/backend",
      "console": "integratedTerminal",
      "vmArgs": "-Dfoundation.math.lib.dir=\${workspaceFolder}/${FOUNDATION_LIB_DIR_REL}",
      "classPaths": [
        "\${workspaceFolder}/App/backend/target/classes",
        "\${workspaceFolder}/App/backend/target/dependency/*"
      ],
      "preLaunchTask": "Backend: debug classpath"
    },
    {
      "name": "Foundation Smoke (Debug C++)",
      "type": "cppdbg",
      "request": "launch",
      "program": "\${workspaceFolder}/${FOUNDATION_EXE_REL}",
      "args": [],
      "cwd": "\${workspaceFolder}/App/foundation",
      "environment": [
        {
          "name": "LD_LIBRARY_PATH",
          "value": "\${workspaceFolder}/${FOUNDATION_LIB_DIR_REL}:\${env:LD_LIBRARY_PATH}"
        }
      ],
      "MIMode": "gdb",
      "miDebuggerPath": "${GDB_BIN}",
      "externalConsole": false,
      "stopAtEntry": false,
      "setupCommands": [
        {
          "description": "Enable pretty printing",
          "text": "-enable-pretty-printing",
          "ignoreFailures": true
        }
      ],
      "preLaunchTask": "Foundation: build"
    }
  ]
}
EOF
log_ok "Wrote .vscode/launch.json"

log_step "Summary"
log_info "java: ${JAVA_BIN}"
log_info "gdb: ${GDB_BIN}"
log_info "backend jar: ${BACKEND_JAR_REL}"
log_ok "VS Code configuration generated under ${VSCODE_DIR}"
