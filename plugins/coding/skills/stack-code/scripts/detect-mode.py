#!/usr/bin/env python3
"""Detect create vs split vs noop mode for stack-code.

Heuristics:
- Working copy clean AND no diverged commits atop `main@origin`   -> noop
  (nothing to stack; orchestrator should refuse cleanly)
- >5 changed files OR >300 LOC diff from main                     -> split
- Diverged commits exist on top of main@origin                    -> split
- Otherwise (small dirty change)                                  -> create

Emits JSON: {"mode": "create"|"split"|"noop", "slug": "...", "rationale": "..."}.

`create` is reserved for the small-uncommitted-change path; the legacy "clean
WC means create" branch is replaced by `noop` to disambiguate "I have an
outline to build" (caller forces `--mode create`) from "nothing to do".
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lib import (
    emit_json,
    has_executable,
    jj,
    jj_diff_stats,
    repo_root,
    run,
    slug_derive,
)


SPLIT_FILE_THRESHOLD = 5
SPLIT_LOC_THRESHOLD = 300


def current_branch_hint() -> str:
    res = run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"])
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    res = jj("log", "-r", "@", "--no-graph", "-T", "description.first_line()")
    return res.stdout.strip() or "stack"


def diverged_from_main(*, dry_run: bool) -> bool:
    """True when working revision has commits not in main@origin."""
    if not has_executable("jj"):
        res = run(["git", "rev-list", "--count", "origin/main..HEAD"], dry_run=dry_run)
        try:
            return int(res.stdout.strip() or "0") > 0
        except ValueError:
            return False
    res = jj("log", "-r", "main@origin..@-", "--no-graph", "-T", "change_id ++ '\\n'", dry_run=dry_run)
    return bool(res.stdout.strip())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="detect stack-code mode")
    ap.add_argument("--slug", help="override derived slug")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    files, loc = jj_diff_stats(dry_run=args.dry_run)
    diverged = diverged_from_main(dry_run=args.dry_run)
    slug = args.slug or slug_derive(current_branch_hint())

    if not files and not diverged:
        rationale = "working copy is clean and at main@origin — nothing to stack"
        mode = "noop"
    elif len(files) > SPLIT_FILE_THRESHOLD or loc > SPLIT_LOC_THRESHOLD:
        rationale = (
            f"chunky uncommitted change ({len(files)} files, {loc} LOC) "
            f"exceeds split threshold ({SPLIT_FILE_THRESHOLD} files / {SPLIT_LOC_THRESHOLD} LOC)"
        )
        mode = "split"
    elif diverged:
        rationale = "diverged commits exist on top of main@origin; treat as split candidate"
        mode = "split"
    else:
        rationale = f"small uncommitted change ({len(files)} files, {loc} LOC); planned create flow"
        mode = "create"

    emit_json({"mode": mode, "slug": slug, "rationale": rationale, "files": len(files), "loc": loc})
    return 0


if __name__ == "__main__":
    sys.exit(main())
