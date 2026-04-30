#!/usr/bin/env python3
"""Eval: default (no --fix-up) appends a follow-up commit on the bookmark.

Sub-flow E per references/workflow-correct.md. Verifies:
  1. Lower bookmark gained exactly one new commit (count = previous + 1).
  2. Original commit on the bookmark is still present (no rewrite —
     old change_id still exists in `jj log`).
  3. Upper bookmark rebased onto the new tip (restack ran).
  4. stdout JSON contains `fix_up: false` and a non-empty
     `restacked_downstream_bookmarks` array.

Run: STACK_CODE_AUTO_APPROVE=1 python3 evals/follow_up_commit.py
"""

from __future__ import annotations

import sys

import _harness as h


def main() -> int:
    print("scenario: default (no --fix-up) appends a follow-up commit")
    with h.fresh_repo(prefix="stack-code-eval-followup-") as repo:
        h.setup_initial_stack(repo)

        lower_bm = "demo/01-lower"
        upper_bm = "demo/02-upper"

        commits_before = h.jj_commit_count_on_bookmark(repo, lower_bm)
        lower_change_before = h.jj_tip_change_id(repo, lower_bm)
        print(
            f"  pre: lower commits={commits_before} "
            f"change_id={lower_change_before}"
        )

        h.edit_lower_file(repo)

        rc, stdout, stderr = h.execute_stack(
            repo, h.initial_two_pr_proposal(), fix_up=False,
        )
        h.assert_eq(rc, 0, "execute-stack (no --fix-up) exit code")

        # Assertion 1: lower gained exactly one commit.
        commits_after = h.jj_commit_count_on_bookmark(repo, lower_bm)
        h.assert_eq(
            commits_after, commits_before + 1,
            "lower commit count grew by exactly 1",
        )

        # Assertion 2: original change_id still present (no rewrite).
        h.assert_true(
            h.jj_change_exists(repo, lower_change_before),
            f"original lower change_id {lower_change_before!r} still in repo",
        )

        # Assertion 3: upper rebased onto the new lower tip.
        new_lower_change = h.jj_tip_change_id(repo, lower_bm)
        upper_parent_change = h.jj_parent_change_id(repo, upper_bm)
        h.assert_eq(
            upper_parent_change, new_lower_change,
            "upper parent change_id == new lower tip change_id",
        )

        # Assertion 4: stdout JSON shape.
        payload = h.parse_stdout_json(stdout)
        h.assert_eq(payload.get("fix_up"), False, "stdout.fix_up")
        restacked = payload.get("restacked_downstream_bookmarks") or []
        h.assert_true(
            isinstance(restacked, list) and len(restacked) > 0,
            "stdout.restacked_downstream_bookmarks is non-empty",
        )

    print("PASS: follow_up_commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
