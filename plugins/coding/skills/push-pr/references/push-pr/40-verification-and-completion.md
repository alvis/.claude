# Verification and completion

## Verification and Completion

- Local checks passed with every command/result recorded, or command execution
  was explicitly skipped; hosted-only gaps and expected checks are named.
- Every bookmark was pushed with `jj git push`; every PR is draft, uses
  `coding:write-pr` output, and has the intended stack base.
- Report success only after the final poll observes every PR green. Include the
  stack map, local results, repair commits, push/restack actions, per-PR check
  states, CI wall times, and any blocker. Return every local project path
  created or materially rewritten during repair as `generated_files`. Do not
  run per-file Markdown sizing; the PM performs the single final batch after
  all repair writers finish.
