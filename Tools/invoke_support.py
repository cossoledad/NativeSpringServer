from __future__ import annotations

import shlex
import shutil
import time
from contextlib import contextmanager
from pathlib import Path


RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[34m"
CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"


def _paint(text: str, *styles: str) -> str:
    return "".join(styles) + text + RESET


def info(message: str) -> None:
    print(_paint(message, CYAN))


def warn(message: str) -> None:
    print(_paint(message, YELLOW))


def step(message: str) -> None:
    print(_paint(f"> {message}", BLUE, BOLD))


def success(message: str) -> None:
    print(_paint(f"OK  {message}", GREEN, BOLD))


def failure(message: str) -> None:
    print(_paint(f"ERR {message}", RED, BOLD))


@contextmanager
def task_scope(title: str):
    started = time.monotonic()
    print()
    print(_paint(f"== {title} ==", BLUE, BOLD))
    try:
        yield
    except Exception as exc:
        elapsed = time.monotonic() - started
        failure(f"{title} failed in {elapsed:.1f}s: {exc}")
        raise
    else:
        elapsed = time.monotonic() - started
        success(f"{title} finished in {elapsed:.1f}s")


def run(c, command: str, *, cwd: Path | None = None, title: str | None = None, pty: bool = True):
    if title:
        step(title)
    return c.run(command, cwd=str(cwd) if cwd else None, pty=pty)


def remove_paths(*paths: Path) -> None:
    for path in paths:
        if path.is_file() or path.is_symlink():
            path.unlink()
        elif path.exists():
            shutil.rmtree(path)


def invoke_task(c, *, search_root: Path, task_name: str, args: list[str] | None = None, cwd: Path | None = None):
    command = [
        "invoke",
        "--search-root",
        str(search_root),
        task_name,
        *(args or []),
    ]
    return run(
        c,
        " ".join(shlex.quote(part) for part in command),
        cwd=cwd,
        title=f"{search_root.name}: invoke {task_name}",
    )
