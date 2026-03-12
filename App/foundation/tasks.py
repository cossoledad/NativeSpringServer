from __future__ import annotations

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
