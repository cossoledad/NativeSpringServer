from __future__ import annotations

import sys
from pathlib import Path

from invoke import task

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Tools.invoke_support import invoke_task, task_scope


ROOT = Path(__file__).resolve().parent
FOUNDATION_DIR = ROOT / "foundation"
BACKEND_DIR = ROOT / "backend"


@task
def deps(c):
    """Install dependencies for App/foundation and App/backend."""
    with task_scope("App deps"):
        invoke_task(c, search_root=FOUNDATION_DIR, task_name="deps", cwd=ROOT)
        invoke_task(c, search_root=BACKEND_DIR, task_name="deps", cwd=ROOT)


@task
def clean(c):
    """Clean App/backend and App/foundation outputs."""
    with task_scope("App clean"):
        invoke_task(c, search_root=BACKEND_DIR, task_name="clean", cwd=ROOT)
        invoke_task(c, search_root=FOUNDATION_DIR, task_name="clean", cwd=ROOT)


@task
def build(c):
    """Build App/foundation then App/backend."""
    with task_scope("App build"):
        invoke_task(c, search_root=FOUNDATION_DIR, task_name="build", cwd=ROOT)
        invoke_task(c, search_root=BACKEND_DIR, task_name="build", cwd=ROOT)


@task
def rebuild(c):
    """Clean and rebuild the full App layer."""
    with task_scope("App rebuild"):
        invoke_task(c, search_root=ROOT, task_name="clean", cwd=ROOT)
        invoke_task(c, search_root=ROOT, task_name="build", cwd=ROOT)
