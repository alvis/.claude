# React Lint Skill Examples

Loaded by `SKILL.md` "Examples" pointer. Reference for invocation patterns.

## Default Usage (Uncommitted React Changes)

```bash
/react:lint
# Lints only .tsx/.jsx files with uncommitted changes (default --scope=uncommitted)
# Linter focuses on changed line ranges and their surrounding component/hook bodies
```

## Uncommitted Scope with Specifier

```bash
/react:lint "src/components/"
# Lints only uncommitted React files within src/components/
# If no uncommitted .tsx/.jsx changes in src/components/, reports "No uncommitted React changes found"
```

## Lint Entire Files

```bash
/react:lint "src/components/Modal.tsx" --scope=all
# Lints the entire file regardless of git status (legacy behavior)
```

## Focus on Specific Area

```bash
/react:lint "src/hooks/" --scope=hooks
# Linter interprets "hooks" and focuses on use* calls and custom hook bodies
```

## Pattern-Based Linting

```bash
/react:lint "**/*.stories.tsx" --scope=all
# Lints all Storybook story files across the entire project
```

## Auto-Dispatch from /coding:lint

```bash
/coding:lint "src/" --scope=uncommitted
#   /coding:lint discovers a mixed set: src/utils/format.ts, src/components/Button.tsx
#   It partitions:
#     - .ts files → handled by /coding:lint's own team-mode batches
#     - .tsx files → dispatched as a sibling Task running Skill: react:lint
#   Both run in parallel. Final report sums violations_found_total from both
#   and reports the worst status.
```

## Error Case Handling

```bash
/react:lint "src/utils/"
# Error: No React source files (*.tsx or *.jsx) found in the specified area
# Suggestion: Use /coding:lint for plain .ts / .js files
```

## Iterating Until Clean With /goal

```bash
/goal violations_found_total reaches 0 from a fresh /react:lint pass on src/, or stop after 5 turns
/react:lint "src/" --scope=uncommitted
# Pass 1: 4 violations fixed across 3 components; report shows status: success
# Goal evaluator (Haiku) returns no → Claude re-invokes /react:lint
# Pass 2: violations_found_total: 0, status: compliant → goal met, session pauses
```

## Single Pass (No Goal)

```bash
/react:lint "src/components/"
# Runs the workflow once. With no active /goal, the session pauses after the pass.
```
