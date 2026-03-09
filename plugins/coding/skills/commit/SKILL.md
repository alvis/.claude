---
name: commit
description: Creates well-formatted commits with conventional messages and emoji. Use when committing code changes, following conventional commit standards, or automating commit message generation.
model: opus
allowed-tools: Bash(git:*), Bash(npm:*), Bash(pnpm:*), Read, Grep, Glob, Agent
argument-hint: [--no-verify] [--retrospective]
---

# Create Commit with Conventional Format

Analyzes changes and creates atomic commits with conventional commit messages and appropriate emoji. Automatically runs pre-commit checks and suggests splitting large changes into multiple commits when appropriate.

## Purpose & Scope

**What this command does NOT do**:

- Push commits to remote repository
- Create merge commits
- Force-push to any branch
- Add any co-authorship footer

> Note: `--retrospective` DOES modify local commit history via interactive rebase, but never force-pushes.

**When to REJECT**:

- No changes to commit
- Working directory has merge conflicts
- Pre-commit checks fail (unless --no-verify)
- Uncommitted changes would be lost

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Planning

1. **Analyze Requirements**
   - Check for `--no-verify` flag (skips both pre-commit checks in Step 1 and post-commit verification in Step 4)
   - Check for `--retrospective` flag (if set, complete Step 1 items 2-4 first, then jump to Retrospective Workflow)
   - Identify files to commit
   - Determine project scripts available from package metadata such as package.json
   - Determine pre-commit checks needed

2. **Pre-commit Verification**
   - Run linting script (if any) to ensure code quality
   - Run build script (if any) to verify build succeeds
   - Run document generation script (if any) to update documentation
   - Skip if `--no-verify` flag present

3. **Change Analysis — Mandatory Classification**

   Classify EVERY changed file by logical concern. Source code and its tests belong TOGETHER in the same commit (per TDD standards).

   **Splitting heuristic** — group by:

   | Priority | Split by | Example commits |
   |----------|----------|-----------------|
   | 1st | Infrastructure vs features | `init: lay the foundation` separate from feature code |
   | 2nd | Module / feature boundary | `feat(auth): add login` vs `feat(search): add query` |
   | 3rd | Change type within a module | `feat(auth): add login` vs `docs(auth): add API docs` |

   **What goes TOGETHER in one commit**:
   - Feature implementation + its unit/integration tests
   - A type/interface + the code that uses it + tests for that code

   **What gets SEPARATE commits**:
   - Configuration & tooling (package.json, tsconfig, eslint, CI/CD)
   - Different features/modules (each feature = its own commit with its tests)
   - Standalone documentation not tied to a specific feature commit
   - Shared types/interfaces that serve multiple features (commit before the features that use them)

   **Dependency tree ordering**:

   After classifying files into groups, build a dependency tree between the groups:
   1. Analyze imports/requires across groups to determine which groups depend on which
   2. Topologically sort the groups — leaf nodes (no dependencies) are committed first, root nodes (depended on by nothing) last
   3. Each commit must only import/use code from commits that come BEFORE it in the chain
   4. If a circular dependency exists between groups, merge them into one commit

   **Self-containment through incremental file evolution**:

   Shared files (package.json, tsconfig.json, config files) must NOT be committed as their final version in the first commit. Instead, each commit includes only the entries relevant to what it introduces.

   - **Shared files evolve incrementally**: Each commit adds only the entries it introduces to shared files. The init commit contains the minimal viable version; later commits modify shared files to add their entries.
   - **No forward references**: A commit must NEVER reference code, modules, paths, imports, or exports that don't exist yet in the chain. If a commit mentions it, it must exist at that point.
   - **Modify files to achieve this**: You MUST modify file contents to make each commit self-contained. This includes removing entries from package.json that reference future code, removing imports for future modules, and trimming config to match what exists.
   - **Config files go with their feature**: `vitest.config.e2e.ts` goes with the e2e test commit, not the init commit. The `bin` field in package.json goes with the CLI commit.

   Concrete examples of incremental evolution:
   - **package.json in init commit**: Only basic metadata, dependencies, and scripts — NO `bin`, NO feature-specific `exports`, NO module-specific subpath imports
   - **package.json in feat(cli) commit**: ADD `bin` field, ADD `exports["./cli"]`
   - **package.json in feat(pull) commit**: ADD `exports["./pull"]` or `imports["#pull"]` if applicable
   - **tsconfig.json**: Only include paths that exist at that commit point
   - **vitest.config.ts**: Only the base test config in init; e2e-specific config added with e2e commit

   Rules:
   - This classification + dependency analysis is MANDATORY — you must show both the categorization AND the dependency tree before proceeding to Step 2
   - There are ZERO exceptions: initial commits, interdependent code, "everything is one feature" — NONE of these exempt you from classification
   - If a single commit would contain more than ~20 files, look harder for sub-groups
   - The minimum expected output for any non-trivial change set is 2+ commits

4. **Risk Assessment**
   - Check for uncommitted changes
   - Verify no merge conflicts
   - Ensure build stability

### Step 2: Confirmation

Present a structured commit plan to the user BEFORE any git write operations.

**Plan format**:

```text
## Commit Plan

Pre-commit checks: [PASS / SKIP (--no-verify)]

### Commit 1
  <emoji> <type>(scope): <description>
  Files: <file list>

### Commit 2
  <emoji> <type>(scope): <description>
  Files: <file list>

Proceed? [Y/n]
```

- Wait for explicit user confirmation before continuing
- If the user declines, abort gracefully with no side effects
- If the user requests changes to the plan, revise and re-present

### Step 3: Execution

1. **File Staging**
   - Check git status for staged files
   - If no staged files, add all modified/new files
   - Confirm files ready for commit

2. **Commit Splitting**
   - Group changes by logical concern — splitting is the default, not the exception
   - Stage files (and individual hunks via `git add -p` when needed) for each logical commit
   - Create separate commits for each group, ordered so each commit is independently valid

3. **Commit Message Generation**
   - Analyze changes for commit type for each commit group
   - Generate message suggestions following the `Commit Guidelines` below

4. **Commit Creation**
   - Execute git commit with message and signature
   - Verify commit succeeded
   - Report completion status

### Step 4: Post-Commit Verification

> Skip this entire step if `--no-verify` is set.

After all commits are created, verify each affected commit passes quality checks.

1. **Identify affected commits** created during this session
2. **For each commit** (oldest to newest), delegate to a **teammate** (coding specialist subagent):
   - Teammate checks out the commit
   - Runs lint and tests with coverage
   - **Lint/coverage issues**: teammate auto-fixes and creates a fixup commit
   - **Test failures**: teammate investigates, presents a fix plan to the orchestrator, the orchestrator presents to the user for confirmation, then teammate fixes and creates a fixup commit
3. **After all fixes**: run `GIT_SEQUENCE_EDITOR=true git rebase --interactive --autosquash` to absorb fixup commits
4. **Re-verify** with fresh teammates to confirm the chain is green
5. **Repeat** until all commits pass
6. **Return to HEAD**

**Verification output table**:

```text
Commit       | Lint | Coverage | Tests | Status
-------------|------|----------|-------|---------
abc1234 feat | PASS | 98%      | PASS  | OK
def5678 fix  | PASS | 97%      | PASS  | OK
```

### Step 5: Reporting

1. **Post-commit Validation**
   - Verify commit created successfully
   - Check git log for new commit
   - Confirm working directory clean

2. **Quality Assurance**
   - Message follows conventional format
   - Description is clear and concise

**Output Format**:

```text
[OK/FAIL] Command: commit

## Summary
- Files committed: [count]
- Commits created: [count]
- Pre-commit checks: [PASS/SKIP/FAIL]

## Actions Taken
1. [Pre-commit check results]
2. [Staging actions]
3. [Commit creation]

## Commit Messages
- [Emoji Type: Description]

## Next Steps (if applicable)
- [Push to remote]
- [Create pull request]
```

---

## Retrospective Workflow

> Activated when `--retrospective` is passed. This mode classifies uncommitted changes as fixups to prior commits or as genuinely new commits, then rewrites local history via interactive rebase to produce a clean commit chain.

### Step R1: Classify Changes

Analyze every changed hunk and determine whether it belongs to an existing commit or is new work. There is NO arbitrary limit on the number of commits produced -- let the changes dictate the grouping.

**Classification strategies** (apply in order):

| Priority | Strategy | Command | Signal |
|----------|----------|---------|--------|
| Primary | `git blame` on changed lines | `git blame <file>` on the pre-change version | Identifies the commit SHA that introduced the lines being modified |
| Secondary | File history | `git log --follow <file>` | Shows which commits previously touched the file |
| Tertiary | Keyword match | `git log --all --oneline` | Matches commit subjects to change intent |

**Classification rules**:

- **Fixup**: The change is a bug fix, design correction, WIP completion, wrong-implementation fix, or file split/refactor of code introduced by a prior commit in the current branch
- **New commit**: Genuinely new feature, test, or documentation not traceable to any prior commit

### Step R2: Map Fixup Targets

For each fixup group:

1. Run `git blame` on the affected lines to find the original commit SHA
2. Cross-reference the SHA with `git log` to confirm it exists in the current branch
3. Record the mapping: `change hunk -> target SHA`

### Step R3: Present Retrospective Plan (Confirmation Gate)

Present the full plan and wait for user approval.

**Plan format**:

```text
## Retrospective Commit Plan

### Fixups

Target: abc1234 feat(auth): add login endpoint
  - Fix validation bug in auth.ts
  - Add missing error handler in auth.ts

Target: def5678 test(auth): add login tests
  - Fix assertion in login.spec.ts

### New Commits

  <emoji> feat(auth): add logout endpoint
  Files: auth.ts, auth.spec.ts

### Projected History (after rebase)

  abc1234' feat(auth): add login endpoint        [amended]
  def5678' test(auth): add login tests            [amended]
  ghi9012  feat(auth): add logout endpoint         [new]

Proceed? [Y/n]
```

- Wait for explicit user confirmation
- If declined, abort with no side effects
- If the user requests changes, revise and re-present

### Step R4: Execute

1. **Create fixup commits** (one per target):
   - Stage the relevant hunks (use `git add -p` for mixed-hunk files)
   - `git commit --fixup=<target-SHA>`

2. **Create new commits** for remaining changes:
   - Stage and commit normally following Commit Guidelines

3. **Rebase to squash fixups**:
   - Determine the base commit (parent of the oldest fixup target)
   - `GIT_SEQUENCE_EDITOR=true git rebase --interactive --autosquash <base>`
   - If merge conflicts arise, attempt auto-resolution; if complex, delegate to a teammate to resolve, then continue the rebase

4. **Post-rebase verification**: proceed to Step 4 (Post-Commit Verification) unless `--no-verify` is set. Note: when entering Step 4 from retrospective mode, the rebase in Step 4 item 3 applies only to newly created fixup commits from the verification loop itself, not a re-run of the retrospective rebase

### Step R5: Present Final Chain

Display the resulting clean history:

```bash
git log --oneline <base>..HEAD
```

Then proceed to Step 5 (Reporting).

### Edge Cases

- **Mixed hunks in a single file**: Use `git add -p` to stage individual hunks into separate fixup commits
- **Merge conflicts during rebase**: Delegate to a teammate to resolve, then `git rebase --continue`
- **No fixup targets found**: Fall back to the normal (non-retrospective) commit workflow
- **All changes are fixups**: Skip new-commit creation, proceed directly to rebase
- **Target SHA not in current branch**: Treat the change as a new commit instead

---

## Examples

### Simple Commit

```bash
/commit
# Runs pre-commit checks, presents plan, creates single commit
```

### Skip Verification

```bash
/commit --no-verify
# Skips pre-commit checks and post-commit verification for quick commits
```

### Suggested Split Example

```bash
/commit
# Detects multiple logical changes:
# Commit 1: feat: add user authentication
# Commit 2: docs: update API documentation
# Commit 3: fix: resolve memory leak
```

### Initial Project Commit (Dependency-Ordered Split)

```bash
/commit
# Initial project (@theriety/notion CLI) with 170 files.
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
#     package.json (MODIFIED: minimal — metadata, deps, base scripts only.
#                   Remove: bin field, exports["./cli"], imports["#pull"],
#                   imports["#push"], etc. Keep only what exists now)
#     tsconfig.json, vitest.config.ts (base only), eslint.config.js,
#     .gitignore, Dockerfile, .github/workflows/ci.yml
#
#  2. feat: add Notion API types, config schema, and constants
#     src/types/block.ts, src/types/page.ts, src/types/database.ts,
#     src/types/config.ts, src/constants.ts, spec/types/*.spec.ts
#     src/types/index.ts (MODIFIED: only re-exports types that exist NOW
#                         — no forward references to api types, etc.)
#
#  3. feat: add shared utilities and helpers
#     src/utils/logger.ts, src/utils/retry.ts, src/utils/fs.ts,
#     src/utils/hash.ts, spec/utils/*.spec.ts
#
#  4. feat(api): implement Notion API client with auth and rate limiting
#     src/api/client.ts, src/api/auth.ts, src/api/rate-limiter.ts,
#     src/api/pagination.ts, spec/api/*.spec.ts
#     package.json (MODIFIED: add imports["#api"] subpath)
#     src/types/index.ts (MODIFIED: add export for api types)
#     (depends on: types, utils)
#
#  5. feat(cache): add local caching layer with invalidation
#     src/cache/store.ts, src/cache/invalidation.ts, src/cache/keys.ts,
#     spec/cache/*.spec.ts
#     (depends on: types, utils)
#
#  6. feat(format): add output formatters for JSON, markdown, and table
#     src/formatters/json.ts, src/formatters/markdown.ts,
#     src/formatters/table.ts, src/formatters/index.ts,
#     spec/formatters/*.spec.ts
#     (depends on: types)
#
#  7. feat(pull): implement page and database pull with transformation
#     src/commands/pull/index.ts, src/commands/pull/page.ts,
#     src/commands/pull/database.ts, src/commands/pull/transformer.ts,
#     spec/commands/pull/*.spec.ts
#     package.json (MODIFIED: add imports["#pull"] subpath)
#     src/constants.ts (MODIFIED: add PULL_BATCH_SIZE constant)
#     (depends on: api, cache, formatters)
#
#  8. feat(push): implement page and database push with conflict detection
#     src/commands/push/index.ts, src/commands/push/resolver.ts,
#     src/commands/push/conflict.ts, spec/commands/push/*.spec.ts
#     package.json (MODIFIED: add imports["#push"] subpath)
#     src/constants.ts (MODIFIED: add PUSH_CONFLICT_STRATEGY constant)
#     (depends on: api, cache)
#
#  9. feat(diff): implement block-level content diffing
#     src/commands/diff/index.ts, src/commands/diff/block-differ.ts,
#     src/commands/diff/renderer.ts, spec/commands/diff/*.spec.ts
#     (depends on: api, formatters)
#
# 10. feat(search): implement full-text and filtered search
#     src/commands/search/index.ts, src/commands/search/query-builder.ts,
#     src/commands/search/ranking.ts, spec/commands/search/*.spec.ts
#     (depends on: api, formatters)
#
# 11. feat(cli): add CLI entrypoint, command router, and help system
#     bin/notion.ts, src/cli/index.ts, src/cli/parser.ts,
#     src/cli/help.ts, spec/cli/*.spec.ts
#     package.json (MODIFIED: add bin field, add exports["./cli"])
#     (depends on: all commands)
#
# 12. test(e2e): add end-to-end test suite with fixtures
#     e2e/pull.e2e.ts, e2e/push.e2e.ts, e2e/diff.e2e.ts,
#     e2e/search.e2e.ts, e2e/fixtures/*, e2e/helpers/*
#     vitest.config.e2e.ts (ADDED: e2e-specific config goes here, not init)
#     (depends on: cli)
#
# 13. docs: add README, architecture guide, and API reference
#     README.md, docs/api.md, docs/usage.md, docs/architecture.md,
#     CHANGELOG.md, LICENSE
#
# The (MODIFIED: ...) annotations show incremental file evolution:
# - package.json appears in commits 1, 4, 7, 8, 11 — each time adding
#   only the entries introduced by that commit
# - src/constants.ts appears in commits 2, 7, 8 — each adding only the
#   constants needed by that feature
# - src/types/index.ts appears in commits 2, 4 — each adding only the
#   re-exports that exist at that point
# - vitest.config.e2e.ts appears ONLY in commit 12, not commit 1
```

```bash
# Example: src/constants.ts evolves across commits
#
# In commit 2 (types & constants):
#   export const API_VERSION = '2024-01-01';
#   export const DEFAULT_PAGE_SIZE = 100;
#   // Only constants used by types — NO command-specific constants yet
#
# In commit 7 (pull):
#   + export const PULL_BATCH_SIZE = 50;        // added with pull feature
#
# In commit 8 (push):
#   + export const PUSH_CONFLICT_STRATEGY = 'merge';  // added with push feature

# Example: src/types/index.ts evolves as barrel export
#
# In commit 2 (types):
#   export type { Block, Page, Database } from './block';
#   export type { Config } from './config';
#   // Only re-exports types that exist NOW — no forward references
#
# In commit 4 (api):
#   + export type { ApiResponse, ApiError } from './api';  // added with api types

# Example: src/api/client.ts in commit 4
#   import { API_VERSION } from '../constants';     // exists in commit 2
#   import type { Page, Database } from '../types'; // exists in commit 2
#   // Does NOT import from '../commands/pull' — that doesn't exist yet
```

### Retrospective Commit

```bash
/commit --retrospective
# Classifies changes as fixups to prior commits or new commits
# Presents retrospective plan, executes fixup + rebase, verifies chain
```

### Retrospective with No Verification

```bash
/commit --retrospective --no-verify
# Same as --retrospective but skips pre-commit and post-commit checks
```

### Error Case Handling

```bash
/commit
# Error: No changes to commit
# Suggestion: Make changes first or check git status
```

### Pre-commit Check Failure

```bash
/commit
# Pre-commit checks failed:
# - Lint errors: 5
# - Build failed: TypeScript compilation errors
# Options: Fix issues or use --no-verify to skip
```

## Commit Guidelines

**Message Format**:

- Title: aim for ≤50 characters; if a longer title offers better clarity, use up to 72 characters; 72-character hard limit
- Present tense, imperative mood
- No period at end of subject line
- Follow conventional format:
  - `<type>: <description>` for global or non-project/feature specific changes
  - `<type>(<scope>): <description>` for project or feature specific changes — use **short package name** as scope, dropping the catalog prefix (e.g., `@theriety/`, `@amino/`). For cross-package concerns, name the concern. For global changes, omit scope.

**Atomic Commits**:

- Each commit serves a single logical purpose
- Related changes grouped together, unrelated changes split into separate commits
- Logical grouping takes priority over historical accuracy — the goal is an ideal commit chain, not a record of how code was developed
- Intermediate states do NOT need to have existed independently during development — they just need to be logically coherent
- Each split commit MUST be standalone: it must compile, pass lint, and pass all tests independently. If splitting would break a commit in isolation, adjust the grouping until every commit is self-contained and green
- Shared files (package.json, tsconfig, configs) MUST evolve incrementally — each commit adds only the entries it introduces. The init commit contains the minimal viable version; later commits modify the file to add their entries.
- A commit must NEVER contain forward references to code, modules, or files that don't exist yet in the chain. If a file references future code, you must modify it to remove those references for that commit.

**Split Criteria**:

- Different concerns or modules
- Mixed change types (feat/fix/docs)
- Large changes needing breakdown
- Different file patterns
- Initial commits (empty repo with many files — MUST still be split)
- "Interdependent" code (all code is interdependent — split by concern anyway)

> NEVER refuse to split for ANY of these reasons:
> - "artificial splitting would create false intermediate states" — creating ideal logical commits IS the purpose of this skill
> - "this is the initial commit" or "no prior commits exist" — initial commits follow the exact same splitting rules
> - "files are interdependent" or "everything is one feature" — all code is interdependent; split by concern anyway
>
> A file MAY appear in multiple commits if different hunks serve different logical purposes.
