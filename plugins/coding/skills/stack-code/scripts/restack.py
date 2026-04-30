#!/usr/bin/env python3
"""Restack open PRs after main moves or a lower PR merges.

Steps:
  1. `jj git fetch`
  2. detect merged bookmarks (closed PRs in state) and drop from active stack
  3. for the next unmerged bookmark, `jj rebase -b <bookmark> -d main@origin`
  4. re-push all affected bookmarks
  5. `gh pr edit <num> --base <new_base>` for each affected PR, then VERIFY the
     change took effect (GitHub silently invalidates the base when the head
     branch of a just-merged base PR is deleted via `--delete-branch`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lib import emit_json, gh, jj, jj_last_op_id, repo_root, state_load, state_save


def fetch(*, dry_run: bool) -> None:
    jj("git", "fetch", dry_run=dry_run)


def is_merged(bookmark: str, *, dry_run: bool) -> bool:
    res = gh("pr", "view", bookmark, "--json", "state", "-q", ".state", dry_run=dry_run)
    return res.stdout.strip().upper() == "MERGED"


def rebase(bookmark: str, dest: str, *, dry_run: bool) -> None:
    jj("rebase", "-b", bookmark, "-d", dest, dry_run=dry_run)


def push(bookmark: str, *, dry_run: bool) -> None:
    jj("git", "push", "--bookmark", bookmark, dry_run=dry_run)


def _pr_base_and_state(bookmark: str, *, dry_run: bool) -> tuple[str, str]:
    """Return (baseRefName, state) for a PR. In dry-run, stub a matching success."""
    res = gh(
        "pr", "view", bookmark, "--json", "baseRefName,state", "-q", ".",
        dry_run=dry_run,
    )
    if dry_run:
        # Stub a successful state so the verify path is exercised but never fails dry-runs.
        return ("__dry_run__", "OPEN")
    try:
        payload = json.loads(res.stdout or "{}")
    except json.JSONDecodeError:
        return ("", "")
    return (str(payload.get("baseRefName", "")), str(payload.get("state", "")))


def reparent_pr(bookmark: str, base: str, *, dry_run: bool) -> None:
    """Reparent <bookmark>'s PR onto <base>, verifying the change actually took effect.

    GitHub silently invalidates the base reference when the head branch of the
    previous base PR was deleted on merge (`--delete-branch`); the PR is
    auto-CLOSED and `gh pr edit` returns 0 anyway. Verify post-edit and, on
    mismatch, attempt a single bounded recovery (reopen + re-edit). If still
    mismatched, raise loudly — no silent retries.
    """
    # gh expects a bare branch name; strip any jj-revset "@remote" suffix (e.g. "main@origin" -> "main").
    gh_base = base.split("@", 1)[0]
    gh("pr", "edit", bookmark, "--base", gh_base, dry_run=dry_run)

    base_ref, state = _pr_base_and_state(bookmark, dry_run=dry_run)
    if dry_run or (base_ref == gh_base and state == "OPEN"):
        return

    # Recovery (single attempt): reopen if auto-closed, then re-issue the edit.
    gh("pr", "reopen", bookmark, dry_run=dry_run)
    gh("pr", "edit", bookmark, "--base", gh_base, dry_run=dry_run)
    base_ref, state = _pr_base_and_state(bookmark, dry_run=dry_run)
    if base_ref == gh_base and state == "OPEN":
        return

    raise SystemExit(
        f"reparent of {bookmark} to {gh_base} failed after recovery: "
        f"state={state!r}, base={base_ref!r}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="restack open PRs against a moved base")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    root = repo_root()
    state = state_load(args.slug, root=root)
    if not state:
        print(f"no state file for slug={args.slug}", file=sys.stderr)
        return 2

    fetch(dry_run=args.dry_run)
    base = state.get("base", "main@origin")
    summary: list[str] = []

    surviving: list[dict[str, object]] = []
    for pr in state.get("prs", []):
        bm = str(pr["bookmark"])
        if pr.get("status") == "merged" or is_merged(bm, dry_run=args.dry_run):
            pr["status"] = "merged"
            summary.append(f"merged   {bm} (dropped)")
            continue
        surviving.append(pr)

    new_base = base
    for pr in surviving:
        bm = str(pr["bookmark"])
        rebase(bm, new_base, dry_run=args.dry_run)
        push(bm, dry_run=args.dry_run)
        reparent_pr(bm, new_base, dry_run=args.dry_run)
        summary.append(f"rebased  {bm} onto {new_base}")
        new_base = bm

    # status mutations above (pr["status"] = "merged") already updated the dicts
    # in state["prs"] in place; preserve original order so callers/tests can rely
    # on positional indexing.
    state["last_op_id"] = jj_last_op_id(dry_run=args.dry_run)
    state_save(args.slug, state, root=root)

    for line in summary:
        print(line, file=sys.stderr)
    emit_json({"slug": args.slug, "ops": summary, "last_op_id": state["last_op_id"]})
    return 0


if __name__ == "__main__":
    sys.exit(main())
