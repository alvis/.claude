---
name: lint
description: Apply React, JSX, hooks, accessibility, and Storybook standards to .tsx/.jsx files; auto-invoked by /coding:lint when React files are detected.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep, Skill, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [specifier] [--scope=SCOPE]
---

# React Linting

Apply React-specific coding standards (components, hooks, accessibility, Storybook, project structure) plus the universal coding standards (documentation, function, naming, typescript, universal) to `.tsx` / `.jsx` files. Standards are discovered at runtime from all active plugins and system context. This skill is normally dispatched by `/coding:lint` when React files are detected in a batch, but can also be invoked directly.

## Arguments

- **specifier** (positional, optional): File path, directory, or glob pattern selecting which React files to lint. Non-React files in the resolved set are ignored.
- **--scope** (optional, default: `uncommitted`): The area within each file to focus linting on. The linter agent interprets this value at runtime. Common values:
  - `uncommitted` — Focus on line ranges with uncommitted changes (staged + unstaged). The linter uses `git diff` to identify changed hunks and lints those areas plus their immediate surrounding context (enclosing components/hooks/blocks).
  - `all` — Lint each file in its entirety (legacy behavior).
  - Any other value (e.g., `hooks`, `stories`, a component name) — The linter interprets the value as a hint for which sections of the code to focus on.

Iteration is handled at the session level via [`/goal`](https://code.claude.com/docs/en/goal) — not by this skill. To run lint until clean, set a goal first, then invoke `/react:lint` (or run `/coding:lint`, which dispatches here automatically). The Step-2 report below is shaped so the goal evaluator (default Haiku) can read convergence state directly.

**Lead pre-filter for `uncommitted` scope**: Before batching, the lead runs `git diff --name-only` to identify React files with uncommitted changes. Files with no changes are excluded from batching to save linter tokens. If no specifier is given, all changed `.tsx/.jsx` files are included. If a specifier is given, only changed React files matching the specifier are batched.

## 🎯 Purpose & Scope

This skill mirrors `/coding:lint` but narrows the target file set to React files (`*.tsx`, `*.jsx`, including sibling `*.stories.tsx`) and loads React-specific standards in addition to the universal coding standards that all TypeScript/JavaScript files obey.

**What this command does NOT do**:

- does not modify configuration files (tsconfig.json, eslintrc, next.config.js, etc.)
- does not install or update linting packages
- does not create new linting rules or configurations
- does not process binary files or non-code assets
- does not modify gitignored or vendor files
- does not lint non-React `.ts` / `.js` files — those stay with `/coding:lint`

**When to REJECT**:

- target is a configuration file that shouldn't be linted
- no React source files (`*.tsx` or `*.jsx`) found in the specified area
- target is outside the project directory
- no files match the specifier after scope pre-filtering (e.g., `--scope=uncommitted` but no uncommitted React changes in the specified files)

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Run the lint workflow

Follow `references/team-mode.md` exactly. Standards are passed by path only —
you never read them. Concurrency: max 4 linters (haiku), max 2 reviewers
(sonnet); retire any agent at `context_level >= 60%`.

### Step 2: Reporting

**Output Format** (same shape as `/coding:lint` so the parent dispatcher can aggregate):

The report MUST begin with the following top-level keys so `/goal`'s evaluator (default Haiku) — and the dispatching `/coding:lint` orchestrator — can read convergence state without parsing prose:

```
violations_found_total: <int>   # sum across all batches in this pass
status: compliant | success | partial | failure
```

Use `status: compliant` and `violations_found_total: 0` together to signal the goal is met. Use `status: success` when violations were found and fixed in this pass. Use `partial` or `failure` when issues remain.

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
1. Fixed hook violations in [X] files
2. Added/updated JSDoc on components in [Y] files
3. Repaired a11y attributes in [Z] files
4. Standardized story exports in [W] files

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

For the full set of usage examples (default, scope variants, team-mode walkthrough, looping, single-pass), see `references/examples.md`.
