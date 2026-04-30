#!/usr/bin/env python3
"""Eval: --fix-up refuses to rewrite an already-MERGED bookmark.

Sub-flow C / GIT-PR-STACK-03 per references/workflow-correct.md. Verifies:
  1. Script exits non-zero with stderr naming `GIT-PR-STACK-03` and
     pointing to `references/workflow-correct.md` sub-flow C.
  2. No jj mutation: lower bookmark commit_id unchanged, and
     `jj op log` count is unchanged from the snapshot taken before the re-run.

Mocks `gh` via PATH-shim (see `_harness._install_gh_shim`) so that
`gh pr view --json state` returns 'MERGED' for the lower bookmark.

Run: STACK_CODE_AUTO_APPROVE=1 python3 evals/merged_history_guard.py
"""

from __future__ import annotations

import sys

import _harness as h


def main() -> int:
    print("scenario: --fix-up refuses to rewrite a MERGED bookmark (sub-flow C)")
    with h.fresh_repo(prefix="stack-code-eval-merged-") as repo:
        h.setup_initial_stack(repo)

        lower_bm = "demo/01-lower"

        # Flip the gh-shim's state so `pr view --json state` returns MERGED.
        h.write_gh_state(repo, "MERGED")

        lower_commit_before = h.jj_tip_commit_id(repo, lower_bm)
        ops_before = h.jj_op_count(repo)
        print(
            f"  pre: lower commit_id={lower_commit_before} jj_ops={ops_before}"
        )

        h.edit_lower_file(repo)

        # Expect non-zero exit; do not raise on failure.
        rc, stdout, stderr = h.execute_stack(
            repo, h.initial_two_pr_proposal(), fix_up=True, expect_failure=True,
        )

        # Assertion 1a: non-zero exit.
        h.assert_true(rc != 0, "exit code is non-zero")

        # Assertion 1b: stderr names GIT-PR-STACK-03.
        h.assert_true(
            "GIT-PR-STACK-03" in stderr,
            "stderr names GIT-PR-STACK-03",
        )

        # Assertion 1c: stderr points to references/workflow-correct.md sub-flow C.
        h.assert_true(
            "workflow-correct.md" in stderr,
            "stderr cites references/workflow-correct.md",
        )
        h.assert_true(
            "sub-flow C" in stderr,
            "stderr names sub-flow C",
        )

        # Assertion 2a: lower bookmark commit_id unchanged.
        lower_commit_after = h.jj_tip_commit_id(repo, lower_bm)
        h.assert_eq(
            lower_commit_after, lower_commit_before,
            "lower bookmark commit_id unchanged",
        )

        # Assertion 2b: jj op log count is unchanged from the snapshot.
        # The merged-guard fires BEFORE any jj write, so the only ops since the
        # snapshot would be the working-copy snapshot from `edit_lower_file`
        # (jj auto-snapshots on the next jj command). We invoked one jj command
        # for the snapshot itself (jj_tip_commit_id), which may or may not bump
        # the op count depending on whether the working copy actually changed.
        # Tolerance: at most 1 op delta (the wc snapshot), and zero ops
        # attributable to execute-stack itself.
        ops_after = h.jj_op_count(repo)
        delta = ops_after - ops_before
        h.assert_true(
            delta <= 1,
            f"jj op delta <= 1 (no script-attributable mutation); got {delta}",
        )

    print("PASS: merged_history_guard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
