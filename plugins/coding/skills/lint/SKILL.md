---
name: lint
description: Apply coding standards and linting to specified code areas. Use when enforcing style guidelines, fixing lint errors, or standardizing code formatting across files.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep, Skill, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [specifier] [--scope=SCOPE] [--max-iterations=N]
---

# Linting

Apply applicable coding standards to ensure consistent code quality across the specified files. Standards are discovered at runtime from all active plugins and system context.

## Arguments

- **specifier** (positional, optional): File path, directory, or glob pattern selecting which files to lint.
- **--scope** (optional, default: `uncommitted`): The area within each file to focus linting on. The linter agent interprets this value at runtime. Common values:
  - `uncommitted` — Focus on line ranges with uncommitted changes (staged + unstaged). The linter uses `git diff` to identify changed hunks and lints those areas plus their immediate surrounding context (enclosing functions/blocks).
  - `all` — Lint each file in its entirety (legacy behavior).
  - Any other value (e.g., `mocks`, `handlers`, a function name) — The linter interprets the value as a hint for which sections of the code to focus on.
- **--max-iterations** (optional, default: `5`): Maximum lint passes to run. The skill delegates iteration to `/loop`, which re-invokes `/coding:lint` with `--max-iterations=1` until either zero violations are reported or the cap is reached. Use `--max-iterations=1` to force a single pass and skip looping entirely.

**Lead pre-filter for `uncommitted` scope**: Before batching, the lead runs `git diff --name-only` to identify files with uncommitted changes. Files with no changes are excluded from batching to save linter tokens. If no specifier is given, all changed files are included. If a specifier is given, only changed files matching the specifier are batched.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- does not modify configuration files (tsconfig.json, eslintrc, etc.)
- does not install or update linting packages
- does not create new linting rules or configurations
- does not process binary files or non-code assets
- does not modify gitignored or vendor files

**When to REJECT**:

- target is a configuration file that shouldn't be linted
- no valid source files found in the specified area
- target is outside the project directory
- no files match the specifier after scope pre-filtering (e.g., `--scope=uncommitted` but no uncommitted changes in the specified files)

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 0: Loop Dispatch

Parse `--max-iterations` from `$ARGUMENTS` (default `5`; positive integer).

- **If `max_iterations > 1`**: invoke the `Skill` tool with `skill: "loop"` and `args: "/coding:lint <original-args-minus-max-iterations> --max-iterations=1"`. The `/loop` skill self-paces, re-firing `/coding:lint --max-iterations=1` each cycle. It stops when the inner report says `violations_found_total: 0` or when its own iteration count reaches the original `--max-iterations`. After the `Skill` call returns, emit a final aggregated summary (iteration count, total violations fixed, termination reason: `converged | hard_cap_reached | no_progress`) and exit. **Do not run Steps 1–3 in this outer call.**
- **If `max_iterations == 1`**: skip the `Skill` invocation and continue to Step 1. This is the per-iteration single pass; the existing workflow runs unmodified, and Step 3 reporting must surface the convergence signal described below.

This dispatch keeps lint's convergence logic out of the skill — `/loop` owns iteration and pacing.

### Step 1: Run the lint workflow

Follow `references/team-mode.md` exactly. Standards are passed by path only —
you never read them. Concurrency: max 4 linters (haiku), max 2 reviewers
(sonnet); retire any agent at `context_level >= 60%`.

### Step 3: Reporting

**Output Format** (same for both modes):

The report MUST begin with the following top-level keys so `/loop`'s pacing model can read convergence state without parsing prose:

```
violations_found_total: <int>   # sum across all batches in this pass
status: compliant | success | partial | failure
iteration_hint: max_iterations=<N>  # echoed from input so the loop model can track its cap
```

Use `status: compliant` and `violations_found_total: 0` together to signal convergence (no further `/loop` iterations needed). Use `status: success` when violations were found and all fixed (loop should continue to verify a clean pass). Use `partial` or `failure` when issues remain unresolved.

The remainder of the summary follows below:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Scope: [uncommitted|all|custom]
- Files scanned: [count]
- Files modified: [count]
- Files already compliant: [count]
- Standards compliance: [PASS/FAIL]
- Linting status: [all_pass/some_fail]
- Execution mode: [team/subagent]

## Actions Taken
1. Added/updated JSDoc comments in [X] files
2. Reordered functions in [Y] files
3. Standardized error messages in [Z] files
4. Fixed logging formats in [W] files

## Workflows Applied
- Linting workflow: [Status]

## Review Cycles (team mode only)
- Batch 1: [N] review rounds until both reviewers approved
- Batch 2: compliant — review skipped
- ...

## Review Coverage (team mode only)
- Batches reviewed: [count] (violations found, sent to reviewers)
- Batches skipped: [count] (already compliant, review not needed)

## Agent Lifecycle (team mode only)
- Agents spawned: [count]
- Agents reused: [count]
- Agents retired (context >= 60%): [count]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## 📝 Examples

For the full set of usage examples (default, scope variants, team-mode walkthrough, subagent fallback walkthrough, looping, single-pass), see `references/examples.md`.
