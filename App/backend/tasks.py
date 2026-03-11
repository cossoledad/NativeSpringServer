from __future__ import annotations

import sys
from pathlib import Path

from invoke import task

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Tools.invoke_support import invoke_task, remove_paths, run, task_scope


ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT.parent
FOUNDATION_DIR = APP_DIR / "foundation"
TARGET_DIR = ROOT / "target"


@task
def deps(c, mvn_cmd="mvn"):
    """Resolve backend Maven dependencies."""
    with task_scope("App backend deps"):
        run(c, f"{mvn_cmd} -q dependency:go-offline", cwd=ROOT, title="Resolve Maven dependencies")


@task
def clean(c):
    """Remove generated backend outputs."""
    with task_scope("App backend clean"):
        remove_paths(TARGET_DIR)


@task
def build(
    c,
    mvn_cmd="mvn",
    skip_tests=True,
    conan_cmd="conan",
    remote="conan-pr",
    remote_url="http://172.27.128.1:19091/repository/conan-pr/",
    profile="",
    foundation_build_type="Release",
    foundation_jobs="",
):
    """Build foundation first, then build backend."""
    with task_scope("App backend build"):
        deps(c, mvn_cmd=mvn_cmd)
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
        run(
            c,
            f"{mvn_cmd} clean package {skip_flag}".strip(),
            cwd=ROOT,
            title="Build backend package",
        )


@task
def rebuild(
    c,
    mvn_cmd="mvn",
    skip_tests=True,
    conan_cmd="conan",
    remote="conan-pr",
    remote_url="http://172.27.128.1:19091/repository/conan-pr/",
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
            skip_tests=skip_tests,
            conan_cmd=conan_cmd,
            remote=remote,
            remote_url=remote_url,
            profile=profile,
            foundation_build_type=foundation_build_type,
            foundation_jobs=foundation_jobs,
        )
