#!/usr/bin/env python3
"""Eval: --fix-up rewrites the existing owning change in-place.

Sub-flow A/B per references/workflow-correct.md. Verifies:
  1. Lower bookmark commit count unchanged (rewrite, not append).
  2. Lower bookmark commit hash changed (rewrite happened).
  3. Upper bookmark rebased onto the new lower-tip
     (its parent change_id == rewritten lower-bookmark tip).
  4. stdout JSON contains `fix_up: true` and a non-empty
     `restacked_downstream_bookmarks` array.

Run: STACK_CODE_AUTO_APPROVE=1 python3 evals/fix_up_rewrite.py
"""

from __future__ import annotations

import sys

import _harness as h


def main() -> int:
    print("scenario: --fix-up rewrites the existing owning change")
    with h.fresh_repo(prefix="stack-code-eval-fixup-") as repo:
        # Stage 1: build the initial 2-PR stack.
        h.setup_initial_stack(repo)

        lower_bm = "demo/01-lower"
        upper_bm = "demo/02-upper"

        commits_before = h.jj_commit_count_on_bookmark(repo, lower_bm)
        lower_commit_before = h.jj_tip_commit_id(repo, lower_bm)
        lower_change_before = h.jj_tip_change_id(repo, lower_bm)
        print(
            f"  pre: lower commits={commits_before} "
            f"commit_id={lower_commit_before} change_id={lower_change_before}"
        )

        # Stage 2: edit a file owned by the lower bookmark.
        h.edit_lower_file(repo)

        # Stage 3: re-run with --fix-up.
        rc, stdout, stderr = h.execute_stack(
            repo, h.initial_two_pr_proposal(), fix_up=True,
        )
        h.assert_eq(rc, 0, "execute-stack --fix-up exit code")

        # Assertion 1: commit count on lower bookmark unchanged.
        commits_after = h.jj_commit_count_on_bookmark(repo, lower_bm)
        h.assert_eq(commits_after, commits_before, "lower commit count")

        # Assertion 2: lower bookmark's tip commit_id changed (rewrite).
        lower_commit_after = h.jj_tip_commit_id(repo, lower_bm)
        h.assert_ne(
            lower_commit_after, lower_commit_before,
            "lower bookmark tip commit_id (rewrite)",
        )

        # Assertion 3: upper rebased onto new lower tip.
        # `bookmark-` resolves to the parent of the bookmark's tip commit.
        upper_parent_change = h.jj_parent_change_id(repo, upper_bm)
        new_lower_change = h.jj_tip_change_id(repo, lower_bm)
        h.assert_eq(
            upper_parent_change, new_lower_change,
            "upper parent change_id == new lower tip change_id",
        )

        # Assertion 4: stdout JSON shape.
        payload = h.parse_stdout_json(stdout)
        h.assert_eq(payload.get("fix_up"), True, "stdout.fix_up")
        restacked = payload.get("restacked_downstream_bookmarks") or []
        h.assert_true(
            isinstance(restacked, list) and len(restacked) > 0,
            "stdout.restacked_downstream_bookmarks is non-empty",
        )

    print("PASS: fix_up_rewrite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
