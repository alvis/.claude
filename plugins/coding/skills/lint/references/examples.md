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

## Looping Until Clean (Default)

```bash
/lint "src/" --scope=uncommitted
# Default: --max-iterations=5
# Pass 1 (via /loop): 7 violations fixed across 4 files
# Pass 2: rediscovers files, 1 violation fixed
# Pass 3: violations_found_total: 0 → /loop stops
# Final: Termination reason: converged
```

## Single Pass (No Loop)

```bash
/lint "src/" --max-iterations=1
# Runs the existing workflow once; no /loop wrapping. Equivalent to legacy behavior.
```
