# Per-Commit QA

This reference defines observation and verification only. It never mutates
history. Run one isolated QA pass per unpushed commit, oldest first:

1. Record the target revision and create a disposable worktree through the
   repository's supported tooling.
2. Run the complete install, lint, test/coverage, and build gate in that clean
   worktree. Capture each exit status directly and report failures.
3. Check markers and conventional-commit conformance without changing the
   target. A skipped gate still reports its reason and required follow-up.
4. Return the existing per-commit report fields: `status`, `skipped_by_marker`,
   `qa`, `lock_folded`, `gate_bypassed_wrappers`, `message_action`, `marked`,
   `pending_decision`, and `newSha`, plus the target revision. Preserve these
   keys even when their value is false, empty, or `none`.

If a correction, fold, reword, reorder, checkpoint, reset, branch move, or push
is approved, invoke `coding:commit` with the exact operation and target. Do not
run `git` or `jj` history-mutating commands directly from this reference or its
workers. Re-run the full QA pass after every delegated mutation.
