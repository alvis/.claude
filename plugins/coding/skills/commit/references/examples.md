# Commit Examples

## Simple Commit

```bash
/commit
# Runs pre-commit checks, presents plan, creates single commit
```

## Skip Verification

```bash
/commit --no-verify
# Skips pre-commit and post-commit verification for quick commits
```

## Suggested Split Example

```bash
/commit
# Detects multiple logical changes:
# Commit 1: feat: add user authentication
# Commit 2: docs: update API documentation
# Commit 3: fix: resolve memory leak
```

## Initial Project Commit (Dependency-Ordered Split)

```bash
/commit
# Initial project with 170 files.
# Dependency tree analysis -> topological commit order:
#
#   [config] -> [types] -> [utils] -> [api client] -> [cache] [formatters]
#                                          |              |        |
#                                      [pull] [push] [diff] [search]
#                                          |     |     |       |
#                                          [cli entrypoint]
#                                               |
#                                          [e2e tests]
#                                               |
#                                            [docs]
#
# Commits (bottom-up from dependency leaves):
#
#  1. init: lay the foundation for the project
#  2. feat: add Notion API types, config schema, and constants
#  3. feat: add shared utilities and helpers
#  4. feat(api): implement Notion API client with auth and rate limiting
#  5. feat(cache): add local caching layer with invalidation
#  6. feat(format): add output formatters for JSON, markdown, and table
#  7. feat(pull): implement page and database pull with transformation
#  8. feat(push): implement page and database push with conflict detection
#  9. feat(diff): implement block-level content diffing
# 10. feat(search): implement full-text and filtered search
# 11. feat(cli): add CLI entrypoint, command router, and help system
# 12. test(e2e): add end-to-end test suite with fixtures
# 13. docs: add README, architecture guide, and API reference
#
# Each commit evolves shared files incrementally (package.json, tsconfig,
# constants, barrel exports) -- no forward references allowed.
# Dependencies in package.json also evolve incrementally -- each commit
# adds only the npm packages its code imports, and regenerates the lock file.
```

## Retrospective Commit

```bash
/commit --retrospective
# Classifies changes as fixups to prior commits or new commits.
# Uses git blame to map changed hunks to original commit SHAs.
# Presents retrospective plan (fixups + new + projected history).
# Creates fixup commits, rebases to squash, verifies chain.
# Combine with --no-verify to skip pre/post-commit checks.
```

## Error Case Handling

```bash
/commit
# Error: No changes to commit
# Suggestion: Make changes first or check git status
```

## Pre-commit Check Failure

```bash
/commit
# Pre-commit checks failed:
# - Lint errors: 5
# - Build failed: TypeScript compilation errors
# Options: Fix issues or use --no-verify to skip
```
