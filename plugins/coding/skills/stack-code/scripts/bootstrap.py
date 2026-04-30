#!/usr/bin/env python3
"""Idempotent environment bootstrap for stack-code.

Verifies `jj`, runs `jj git init --colocate` if absent, sets the auto-track config,
and creates `.jj/stack-code/` for state files.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from lib import has_executable, jj, repo_root, state_dir


def ensure_tools(*, dry_run: bool = False) -> bool:
    """Delegate tool install/update to the sibling coding:sync-tool skill.

    Skips delegation when both `jj` and `gh` are already on PATH. Otherwise streams
    sync-tool's output so the user can see planned/actual install actions. Returns
    True if jj and gh are available afterwards, False otherwise.
    """
    if has_executable("jj") and has_executable("gh"):
        return True

    sync_script = (
        Path(__file__).resolve().parent.parent.parent
        / "sync-tool"
        / "scripts"
        / "sync.py"
    )
    if not sync_script.is_file():
        print(
            f"bootstrap: sibling sync-tool script not found at {sync_script}",
            file=sys.stderr,
        )
        return False

    cmd = [sys.executable, str(sync_script), "--only=jj,gh"]
    if dry_run:
        cmd.append("--dry-run")
    try:
        result = subprocess.run(cmd)
    except FileNotFoundError as exc:
        print(f"bootstrap: failed to invoke sync-tool: {exc}", file=sys.stderr)
        return False
    if result.returncode != 0:
        print(
            f"bootstrap: sync-tool exited {result.returncode}; "
            f"please install jj and gh manually (see {sync_script})",
            file=sys.stderr,
        )
        return False
    if dry_run:
        return True
    if not (has_executable("jj") and has_executable("gh")):
        print(
            "bootstrap: jj/gh still missing after sync-tool ran successfully",
            file=sys.stderr,
        )
        return False
    return True


def ensure_colocated(root: Path, *, dry_run: bool) -> None:
    if (root / ".jj").is_dir():
        return
    print("initialising jj (colocated) at", root, file=sys.stderr)
    jj("git", "init", "--colocate", dry_run=dry_run, cwd=root)


def ensure_auto_track(*, dry_run: bool) -> None:
    jj(
        "config",
        "set",
        "--repo",
        "remotes.origin.auto-track-created-bookmarks",
        "glob:*",
        dry_run=dry_run,
    )


def ensure_state_dir(root: Path) -> Path:
    d = state_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    return d


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="bootstrap stack-code environment")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if not ensure_tools(dry_run=args.dry_run):
        return 2
    root = repo_root()
    ensure_colocated(root, dry_run=args.dry_run)
    ensure_auto_track(dry_run=args.dry_run)
    d = ensure_state_dir(root)
    print(f"ok: state-dir={d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
