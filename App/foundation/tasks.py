from __future__ import annotations

import re
import sys
from pathlib import Path

from invoke import task

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Tools.invoke_support import remove_paths, run, task_scope
from Tools.project_config import DEFAULT_CONAN_REMOTE_NAME, DEFAULT_CONAN_REMOTE_URL, PROJECT_CONAN_CMD


ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "build"
TARGET_DIR = ROOT / "target"

SUPPRESS_WARNINGS_PATTERNS = (
    re.compile(r"^\s*@SuppressWarnings\(\"deprecation\"\)\s*$", re.MULTILINE),
    re.compile(r"^\s*@SuppressWarnings\(\{\"deprecation\",\s*\"removal\"\}\)\s*$", re.MULTILINE),
)


def _sanitize_generated_java() -> int:
    java_root = BUILD_DIR / "java"
    if not java_root.exists():
        return 0

    changed = 0
    for java_file in java_root.rglob("*.java"):
        text = java_file.read_text(encoding="utf-8")
        new_text = text
        for pattern in SUPPRESS_WARNINGS_PATTERNS:
            new_text = pattern.sub("", new_text)
        # Collapse extra blank lines produced by removals.
        new_text = re.sub(r"\n{3,}", "\n\n", new_text)
        if new_text != text:
            java_file.write_text(new_text, encoding="utf-8")
            changed += 1
    return changed


@task
def deps(
    c,
    remote=DEFAULT_CONAN_REMOTE_NAME,
    remote_url=DEFAULT_CONAN_REMOTE_URL,
    profile="",
    build_type="Release",
    conan_cmd=PROJECT_CONAN_CMD,
):
    """Install foundation dependencies and generate Conan/CMake config."""
    with task_scope("App foundation deps"):
        profile_arg = f"-pr {profile}" if profile else ""
        run(c, f"{conan_cmd} remote add {remote} {remote_url} --force", cwd=ROOT, title="Configure Conan remote")
        run(
            c,
            (
                f"{conan_cmd} install . --build=missing -r {remote} "
                f"-s build_type={build_type} {profile_arg} -of build"
            ).strip(),
            cwd=ROOT,
            title="Install Conan dependencies",
        )


@task
def clean(c):
    """Remove generated foundation outputs."""
    with task_scope("App foundation clean"):
        remove_paths(BUILD_DIR, TARGET_DIR)


@task
def build(
    c,
    remote=DEFAULT_CONAN_REMOTE_NAME,
    remote_url=DEFAULT_CONAN_REMOTE_URL,
    profile="",
    build_type="Release",
    conan_cmd=PROJECT_CONAN_CMD,
    jobs="",
):
    """Generate config and build foundation native/JNI outputs."""
    with task_scope("App foundation build"):
        deps(c, remote=remote, remote_url=remote_url, profile=profile, build_type=build_type, conan_cmd=conan_cmd)
        jobs_arg = f"-j{jobs}" if jobs else "-j"
        run(
            c,
            (
                "cmake -S . -B build "
                "-DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake "
                f"-DCMAKE_BUILD_TYPE={build_type}"
            ),
            cwd=ROOT,
            title="Configure CMake",
        )
        run(c, f"cmake --build build {jobs_arg}", cwd=ROOT, title="Build foundation")
        sanitized = _sanitize_generated_java()
        if sanitized:
            print(f"Sanitized SWIG Java warnings in {sanitized} generated file(s).")


@task
def rebuild(
    c,
    remote=DEFAULT_CONAN_REMOTE_NAME,
    remote_url=DEFAULT_CONAN_REMOTE_URL,
    profile="",
    build_type="Release",
    conan_cmd=PROJECT_CONAN_CMD,
    jobs="",
):
    """Clean and rebuild foundation."""
    with task_scope("App foundation rebuild"):
        clean(c)
        build(
            c,
            remote=remote,
            remote_url=remote_url,
            profile=profile,
            build_type=build_type,
            conan_cmd=conan_cmd,
            jobs=jobs,
        )
