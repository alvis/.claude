"""Shared helpers for sync-tool.

Provides OS detection, executable lookup, command running with dry-run/force
support, version comparison, and a poll-with-banner helper used by gh.sh's
post-install auth wait (via subprocess from the shell side).
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Callable, Iterable


# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------

OS_DARWIN = "darwin"
OS_LINUX = "linux"
OS_WINDOWS = "windows"
OS_UNKNOWN = "unknown"


def detect_os() -> str:
    """Return one of darwin | linux | windows | unknown.

    Mirrors the `uname -s` branching in the installer shell scripts.
    """

    sysname = platform.system().lower()
    if sysname == "darwin":
        return OS_DARWIN
    if sysname == "linux":
        return OS_LINUX
    if sysname.startswith(("mingw", "msys", "cygwin")) or sysname == "windows":
        return OS_WINDOWS
    return OS_UNKNOWN


# ---------------------------------------------------------------------------
# Executable lookup
# ---------------------------------------------------------------------------


def has_executable(name: str) -> bool:
    """Return True iff `name` is on PATH."""

    return shutil.which(name) is not None


# ---------------------------------------------------------------------------
# Command execution
# ---------------------------------------------------------------------------


@dataclass
class RunResult:
    """Result of a `run` invocation."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run(
    cmd: list[str] | str,
    *,
    env: dict[str, str] | None = None,
    cwd: str | None = None,
    check: bool = False,
    capture: bool = True,
    dry_run: bool = False,
) -> RunResult:
    """Execute `cmd`, optionally only echoing it under dry_run.

    If `dry_run` is True, prints `+ <cmd>` to stderr and returns a successful
    RunResult without executing. Honors `check=True` to raise on non-zero exit.
    """

    shell = isinstance(cmd, str)
    pretty = cmd if shell else " ".join(cmd)

    if dry_run:
        print(f"+ {pretty}", file=sys.stderr)
        return RunResult(returncode=0, stdout="", stderr="")

    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    proc = subprocess.run(
        cmd,
        shell=shell,
        env=merged_env,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    result = RunResult(
        returncode=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
    )
    if check and not result.ok:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, output=result.stdout, stderr=result.stderr
        )
    return result


# ---------------------------------------------------------------------------
# Version comparison
# ---------------------------------------------------------------------------

_VERSION_RE = re.compile(r"(\d+(?:\.\d+){1,3})")


def parse_version(text: str) -> tuple[int, ...] | None:
    """Extract the first dotted version found in `text` and return as tuple.

    Returns None if no version-looking substring is present.
    """

    if not text:
        return None
    match = _VERSION_RE.search(text)
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def version_at_least(actual: str, minimum: str) -> bool:
    """Return True iff `actual` parses to a version >= `minimum`.

    If `actual` cannot be parsed, returns False (treat as outdated).
    """

    actual_tuple = parse_version(actual)
    minimum_tuple = parse_version(minimum)
    if actual_tuple is None or minimum_tuple is None:
        return False
    # Pad shorter tuple with zeros for fair comparison.
    width = max(len(actual_tuple), len(minimum_tuple))
    a = actual_tuple + (0,) * (width - len(actual_tuple))
    m = minimum_tuple + (0,) * (width - len(minimum_tuple))
    return a >= m


def get_version(executable: str, *, args: Iterable[str] = ("--version",)) -> str | None:
    """Run `<executable> --version` and return the captured stdout (or None)."""

    if not has_executable(executable):
        return None
    result = run([executable, *args], capture=True)
    if not result.ok:
        return None
    return (result.stdout or result.stderr).strip() or None


# ---------------------------------------------------------------------------
# Poll-with-banner helper (used by gh post-install auth wait)
# ---------------------------------------------------------------------------


def poll_until(
    check: Callable[[], bool],
    *,
    banner: str,
    interval_seconds: float = 5.0,
    reprint_every_n_polls: int = 6,
    no_wait: bool = False,
) -> bool:
    """Poll `check` every `interval_seconds`, printing `banner` periodically.

    Returns True when `check()` returns True. Raises KeyboardInterrupt on Ctrl-C
    so callers can translate to a non-zero exit.

    If `no_wait` is True, prints the banner once and returns False without polling.
    """

    print(banner, flush=True)
    if no_wait:
        return False

    poll_count = 0
    while True:
        if check():
            return True
        poll_count += 1
        if reprint_every_n_polls > 0 and poll_count % reprint_every_n_polls == 0:
            print(banner, flush=True)
        time.sleep(interval_seconds)


# ---------------------------------------------------------------------------
# Convenience: print formatted per-tool status line
# ---------------------------------------------------------------------------


def status_line(tool: str, status: str, action: str) -> str:
    """Format a per-tool status line per the SKILL.md spec."""

    return f"{tool}: {status} ({action})"
