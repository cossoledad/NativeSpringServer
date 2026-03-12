from __future__ import annotations

import sys
from pathlib import Path

from invoke import task

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Tools.invoke_support import invoke_task, remove_paths, run, task_scope
from Tools.project_config import DEFAULT_CONAN_REMOTE_NAME, DEFAULT_CONAN_REMOTE_URL, PROJECT_CONAN_CMD, PROJECT_MAVEN_SETTINGS


ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT.parent
FOUNDATION_DIR = APP_DIR / "foundation"
TARGET_DIR = ROOT / "target"


def _maven_settings_arg(settings_file: str) -> str:
    return f"-s {settings_file}" if settings_file else ""


@task
def deps(c, mvn_cmd="mvn", settings_file=PROJECT_MAVEN_SETTINGS):
    """Resolve backend Maven dependencies."""
    with task_scope("App backend deps"):
        settings_arg = _maven_settings_arg(settings_file)
        run(
            c,
            f"{mvn_cmd} {settings_arg} -q dependency:go-offline".strip(),
            cwd=ROOT,
            title="Resolve Maven dependencies",
        )


@task
def clean(c):
    """Remove generated backend outputs."""
    with task_scope("App backend clean"):
        removed, _ = remove_paths(TARGET_DIR)
        if removed:
            print(f"Removed: {removed[0]}")
        else:
            print(f"Nothing to clean: {TARGET_DIR}")


@task
def build(
    c,
    mvn_cmd="mvn",
    settings_file=PROJECT_MAVEN_SETTINGS,
    skip_tests=True,
    conan_cmd=PROJECT_CONAN_CMD,
    remote=DEFAULT_CONAN_REMOTE_NAME,
    remote_url=DEFAULT_CONAN_REMOTE_URL,
    profile="",
    foundation_build_type="Release",
    foundation_jobs="",
):
    """Build foundation first, then build backend."""
    with task_scope("App backend build"):
        deps(c, mvn_cmd=mvn_cmd, settings_file=settings_file)
        foundation_args = [
            f"--remote={remote}",
            f"--remote-url={remote_url}",
            f"--build-type={foundation_build_type}",
            f"--conan-cmd={conan_cmd}",
        ]
        if profile:
            foundation_args.append(f"--profile={profile}")
        if foundation_jobs:
            foundation_args.append(f"--jobs={foundation_jobs}")
        invoke_task(c, search_root=FOUNDATION_DIR, task_name="build", args=foundation_args, cwd=ROOT)
        skip_flag = "-DskipTests" if skip_tests else ""
        settings_arg = _maven_settings_arg(settings_file)
        run(
            c,
            f"{mvn_cmd} {settings_arg} clean package {skip_flag}".strip(),
            cwd=ROOT,
            title="Build backend package",
        )


@task
def rebuild(
    c,
    mvn_cmd="mvn",
    settings_file=PROJECT_MAVEN_SETTINGS,
    skip_tests=True,
    conan_cmd=PROJECT_CONAN_CMD,
    remote=DEFAULT_CONAN_REMOTE_NAME,
    remote_url=DEFAULT_CONAN_REMOTE_URL,
    profile="",
    foundation_build_type="Release",
    foundation_jobs="",
):
    """Clean and rebuild backend."""
    with task_scope("App backend rebuild"):
        clean(c)
        build(
            c,
            mvn_cmd=mvn_cmd,
            settings_file=settings_file,
            skip_tests=skip_tests,
            conan_cmd=conan_cmd,
            remote=remote,
            remote_url=remote_url,
            profile=profile,
            foundation_build_type=foundation_build_type,
            foundation_jobs=foundation_jobs,
        )
