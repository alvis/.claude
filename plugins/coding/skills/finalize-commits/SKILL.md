---
name: finalize-commits
description: "Run isolated per-commit QA across every unpushed commit, report ordering or message issues, and coordinate approved corrections. Use before publishing a stack; coding:commit remains the sole owner of history mutations, reword, fold, reorder, and push."
model: opus
context: fork
allowed-tools: Bash, Read, Grep, Glob, Agent, AskUserQuestion, Skill, TodoWrite
argument-hint: "[--auto-push]"
---

# Finalize Commits

Verify that every unpushed commit is independently shippable. This skill owns
isolated per-commit QA and the finalization report. `coding:commit` is the sole
owner of history mutations.

## Boundaries

- Enumerate the unpushed stack oldest first without changing it.
- Run each commit's install, lint, test or coverage, and build gate in a fresh
  isolated worktree.
- Diagnose failures and propose the smallest correction. Code corrections route
  to `coding:fix` before the commit is tested again.
- Route every fold, squash, amend, reword, reorder, restack, abandon, bookmark or
  branch move, and push through `coding:commit`. Never issue a direct `git` or `jj`
  history-mutating command from this skill or its QA workers.
- Stop for user approval when a correction changes commit meaning or order.
- Push only when `--auto-push` was explicitly supplied and all commits are green;
  the push itself is delegated to `coding:commit`.

## Workflow

1. Detect jj or git and record the current working state and upstream without mutation. Load [references/dependency-scan.md](references/dependency-scan.md) to enumerate unpushed commits oldest first and determine dependency order.
2. Load [references/workflow.md](references/workflow.md) for the coordination and approval contract. Report any recommended reorder or fold before QA.
3. For each commit, load [references/qa-loop.md](references/qa-loop.md), create a disposable worktree at that revision, and run the repository's complete QA gate. Never split a required gate to hide failure.
4. If QA changes source or a generated lockfile, validate the correction in the
   isolated worktree, then invoke `coding:commit` to apply it to the owning commit.
5. If a subject is non-conforming, propose the truthful replacement and invoke
   `coding:commit` for the approved reword.
6. Load [references/squash-fixups.md](references/squash-fixups.md) only when a fixup/fold is approved. Re-run the affected commit and all dependent later commits after any mutation.
7. Verify a clean, conflict-free final stack. If requested, invoke `coding:commit`
   for the push only after every commit passes.

## QA markers

Load [references/markers.md](references/markers.md) when reading or writing QA markers. A marker is valid only when its stored lockfile-excluded stable patch ID equals the current commit's. It may skip the skippable lint/test legs, but never a required install/lock regeneration. Write or replace it only after install, lint, test/coverage, build, message checks, and delegated folds are green with no pending decision.

## Completion

Report commit order, dependency findings, corrections routed through `coding:commit`, remaining decisions, final stack state, and push status. Preserve these fields for every commit, including false/empty values: `revision`, `status`, `skipped_by_marker`, `qa` (install/lint/test/coverage/build commands and exits), `lock_folded`, `gate_bypassed_wrappers`, `message_action`, `marked`, `pending_decision`, and `newSha`.
