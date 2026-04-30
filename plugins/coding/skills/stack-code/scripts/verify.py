#!/usr/bin/env python3
"""Post-mutation verification.

- Auto-detect typecheck:
    * `tsconfig.json`        -> `npx tsc --noEmit`
    * `pyproject.toml` mypy  -> `mypy`
    * else                   -> skip with note
- State integrity: every PR in state has a real change_id resolvable via `jj log`.
- Full tests: prompts the user; never auto-runs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lib import confirm, emit_json, has_executable, jj, repo_root, run, state_load


def detect_typecheck(root: Path) -> list[str] | None:
    if (root / "tsconfig.json").is_file() and has_executable("npx"):
        return ["npx", "tsc", "--noEmit"]
    pyproj = root / "pyproject.toml"
    if pyproj.is_file() and "mypy" in pyproj.read_text(encoding="utf-8") and has_executable("mypy"):
        return ["mypy", "."]
    return None


def typecheck(root: Path, *, dry_run: bool) -> tuple[str, int]:
    cmd = detect_typecheck(root)
    if not cmd:
        return ("skipped (no tsconfig.json or mypy config)", 0)
    res = run(cmd, dry_run=dry_run, cwd=root)
    return (" ".join(cmd), res.returncode)


def state_integrity(slug: str, root: Path, *, dry_run: bool) -> list[str]:
    state = state_load(slug, root=root)
    issues: list[str] = []
    for pr in state.get("prs", []):
        cid = str(pr.get("change_id", ""))
        if not cid:
            issues.append(f"pr#{pr.get('n')} has no change_id")
            continue
        res = jj("log", "-r", cid, "--no-graph", "-T", "change_id", dry_run=dry_run)
        if res.returncode != 0 or not res.stdout.strip():
            issues.append(f"pr#{pr.get('n')} change_id {cid} not resolvable")
    return issues


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="verify stack-code state and typecheck")
    ap.add_argument("--slug", help="state slug to verify; omit to skip integrity")
    ap.add_argument("--full-tests", action="store_true", help="run full test suite (still prompts)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    root = repo_root()
    cmd, rc = typecheck(root, dry_run=args.dry_run)
    issues = state_integrity(args.slug, root, dry_run=args.dry_run) if args.slug else []

    test_status = "skipped"
    if args.full_tests and confirm("Run full test suite now? (may take a while)"):
        if (root / "package.json").is_file() and has_executable("npm"):
            test_status = f"npm test rc={run(['npm', 'test'], dry_run=args.dry_run, cwd=root).returncode}"
        elif has_executable("pytest"):
            test_status = f"pytest rc={run(['pytest'], dry_run=args.dry_run, cwd=root).returncode}"

    emit_json(
        {
            "typecheck": {"cmd": cmd, "returncode": rc},
            "state_issues": issues,
            "tests": test_status,
        }
    )
    return 0 if rc == 0 and not issues else 1


if __name__ == "__main__":
    sys.exit(main())
