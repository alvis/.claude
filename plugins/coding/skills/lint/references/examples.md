# Lint Skill Examples

Loaded by `SKILL.md` "Examples" pointer. Reference for invocation patterns.

## Default Usage (Uncommitted Changes)

```bash
/lint
# Lints only files with uncommitted changes (default --scope=uncommitted)
# Linter focuses on changed line ranges and their surrounding context
```

## Uncommitted Scope with Specifier

```bash
/lint "src/utils/"
# Lints only uncommitted files within src/utils/
# If no uncommitted changes in src/utils/, reports "No uncommitted changes found"
```

## Lint Entire Files

```bash
/lint "src/utils/helper.ts" --scope=all
# Lints the entire file regardless of git status (legacy behavior)
```

## Focus on Specific Area

```bash
/lint "src/services/" --scope=mocks
# Linter interprets "mocks" and focuses on mock/stub sections within each file
```

## Complex Usage with Directory

```bash
/lint "src/components/" --scope=all
# Processes all TypeScript and JavaScript files in the components directory
```

## Pattern-Based Linting

```bash
/lint "**/*.test.ts" --scope=all
# Lints all test files across the entire project
```

## Error Case Handling

```bash
/lint "node_modules/"
# Error: Cannot lint vendor/dependency files
# Suggestion: Target source code directories instead
# Alternative: Use '/lint "src/"' for source files
```

## Large-Scale Processing

```bash
/lint "src/" --scope=uncommitted
#   Discovers uncommitted files under src/, creates lint-team:
#   - linter-1 (haiku): Handles src/components/Button.tsx, src/components/Modal.tsx
#   - linter-2 (haiku): Handles src/utils/format.ts (parallel)
#   Each linter uses git diff to focus on changed hunks within assigned files.
#   Linter-1 finds violations → 2 reviewers assigned for that batch.
#   Linter-2 reports compliant → review skipped for that batch.
#   Agents report context_level after each task:
#     - context < 60%: agent reused for next task
#     - context >= 60%: agent retired, fresh replacement spawned
#   Team is cleaned up after all batches complete.
```

## Iterating Until Clean With /goal

```bash
/goal violations_found_total reaches 0 from a fresh /coding:lint pass on src/, or stop after 5 turns
/lint "src/" --scope=uncommitted
# Pass 1: 7 violations fixed across 4 files; report shows status: success
# Goal evaluator (Haiku) returns no → Claude re-invokes /coding:lint
# Pass 2: 1 violation fixed; status: success
# Pass 3: violations_found_total: 0, status: compliant → goal met, session pauses
```

## Single Pass (No Goal)

```bash
/lint "src/"
# Runs the workflow once. With no active /goal, the session pauses after the pass.
```

## Headless / Non-Interactive

```bash
claude -p "/goal violations_found_total reaches 0 from a fresh /coding:lint pass on src/, or stop after 5 turns" \
       -p "/lint src/ --scope=uncommitted"
# Single invocation runs the goal loop to completion; exit when condition met or cap hit.
```
