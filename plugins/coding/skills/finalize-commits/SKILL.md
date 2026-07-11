---
name: finalize-commits
description: "Run isolated per-commit QA across every unpushed commit, report ordering or message issues, and coordinate approved corrections. Use before publishing a stack; coding:commit remains the sole owner of history mutations, reword, fold, reorder, and push."
model: opus
context: fork
agent: general-purpose
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

1. Detect jj or git and record the current working state and upstream without
   mutation.
2. Enumerate unpushed commits oldest first. Inspect dependency order and report any
   recommended reorder or fold before QA.
3. For each commit, create a disposable worktree at that revision and run the
   repository's complete QA gate. Never split a required gate to hide failure.
4. If QA changes source or a generated lockfile, validate the correction in the
   isolated worktree, then invoke `coding:commit` to apply it to the owning commit.
5. If a subject is non-conforming, propose the truthful replacement and invoke
   `coding:commit` for the approved reword.
6. Re-run the affected commit and all dependent later commits after any mutation.
7. Verify a clean, conflict-free final stack. If requested, invoke `coding:commit`
   for the push only after every commit passes.

## Completion

Report commit order, per-commit commands and results, corrections routed through
`coding:commit`, remaining decisions or failures, final stack state, and whether a
push was performed or skipped.
