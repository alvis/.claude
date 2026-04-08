---
name: commit
description: Creates well-formatted commits with conventional messages and emoji. Use when committing code changes, following conventional commit standards, or automating commit message generation.
model: opus
allowed-tools: Bash(git:*), Bash(npm:*), Bash(pnpm:*), Bash(bash ${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/*), Read, Grep, Glob, Agent
argument-hint: [--no-verify] [--retrospective]
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/pre-commit-hook.sh"
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/post-rebase-hook.sh"
---

## Script Setup

Backup and verification scripts are bundled at `${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/`.

PreToolUse/PostToolUse hooks in the frontmatter auto-trigger these scripts. **If hooks did not fire** (no `Auto-backup:` context visible), you MUST run them manually as described in Steps 0 and 5.

# Create Commit with Conventional Format

Analyzes changes and creates atomic commits with conventional commit messages and appropriate emoji. Automatically runs pre-commit checks and suggests splitting large changes into multiple commits when appropriate.

## Purpose & Scope

**What this command does NOT do**:

- Push commits to remote repository
- Create merge commits
- Force-push to any branch
- Add any co-authorship footer
- **Run `git push` in any form** -- this is a HARD prohibition; the agent must NEVER execute any push command, even if the user asks for it within this skill's scope

> Note: `--retrospective` modifies local commit history via interactive rebase, but never force-pushes.

**When to REJECT**:

- No changes to commit
- Working directory has merge conflicts
- Pre-commit checks fail (unless --no-verify)
- Uncommitted changes would be lost

## Visual Overview

```plaintext
Step 0: Pre-Flight Safety
   |
   v
Step 1: Planning
   |-- Analyze requirements (record --no-verify, --retrospective flags)
   |-- Pre-commit verification (skip if --no-verify)
   |-- Change classification  <-- IF/ELSE branch point
   |      IF --retrospective: git-blame classification + fixup mapping
   |      ELSE: splitting heuristic + dependency tree
   |-- Risk assessment
   |
   v
Step 2: Confirmation  <-- IF/ELSE branch point
   |      IF --retrospective: fixups + new commits + projected history
   |      ELSE: standard commit plan
   |
   v
Step 3: Execution  <-- IF/ELSE branch point
   |      IF --retrospective: fixup commits -> new commits -> rebase -> git log
   |      ELSE: stage + commit per group
   |
   v
Step 4: Post-Commit Verification (skip if --no-verify)
   |
   v
Step 5: Integrity Verification
   |
   v
Step 6: Reporting
```

## Workflow

ultrathink: you'd perform the following steps

### Step 0: Pre-Flight Safety

**Check**: Look for `Auto-backup: GIT_TREE_SHA=... CONTENT_HASH=... BACKUP_PATH=...` in your recent context (injected by the PreToolUse hook before the first `git commit`/`git rebase`).

- **If present**: Backup already done. Note the values and proceed to Step 1.
- **If absent**: Hook did not fire. Run backup manually:

  ```bash
  bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/backup.sh"
  ```

  Record the output values (GIT_TREE_SHA, CONTENT_HASH, BACKUP_PATH) — you need them in Step 5.

What the backup does:
1. Copies full working tree to `${TMPDIR:-/tmp}/git-backups/<repo>/<epoch>-<pid>/`
2. Computes **Git Tree SHA** via `git write-tree` inside backup copy (isolated index)
3. Computes **Content Hash**: deterministic SHA-256 of all files excl `.git/`
4. Writes checkpoint to `<tmpdir>/git-backups/<repo>/.checkpoint`

### Step 1: Planning

1. **Analyze Requirements**
   - Check for `--no-verify` flag (skips both pre-commit checks in Step 1 and post-commit verification in Step 4)
   - Check for `--retrospective` flag (record as mode variable; workflow continues linearly through all steps)
   - Identify files to commit
   - Determine project scripts available from package metadata such as package.json
   - Determine pre-commit checks needed

2. **Pre-commit Verification**
   - Run linting script (if any) to ensure code quality
   - Run build script (if any) to verify build succeeds
   - Run document generation script (if any) to update documentation
   - Run test script (if any) to ensure all tests pass
   - Skip if `--no-verify` flag present

3. **Change Classification -- Mandatory**

   Classify EVERY changed file by logical concern. Source code and its tests belong TOGETHER in the same commit (per TDD standards).

   IF `--retrospective`:

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

   **Map fixup targets**: For each fixup group, run `git blame` on the affected lines to find the original commit SHA, cross-reference with `git log` to confirm it exists in the current branch, and record the mapping: `change hunk -> target SHA`.

   **Edge cases**:
   - Mixed hunks in a single file: Use `git add -p` to stage individual hunks into separate fixup commits
   - No fixup targets found: Fall back to normal (non-retrospective) classification below
   - All changes are fixups: Skip new-commit creation, proceed directly to rebase in Step 3
   - Target SHA not in current branch: Treat the change as a new commit instead

   ELSE:

   **Splitting heuristic** -- group by:

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
   2. Topologically sort the groups -- leaf nodes (no dependencies) are committed first, root nodes (depended on by nothing) last
   3. Each commit must only import/use code from commits that come BEFORE it in the chain
   4. If a circular dependency exists between groups, merge them into one commit

   **Self-containment through incremental file evolution**:

   Shared files (package.json, tsconfig.json, config files) must NOT be committed as their final version in the first commit. Instead, each commit includes only the entries relevant to what it introduces.

   - **Shared files evolve incrementally**: Each commit adds only the entries it introduces to shared files. The init commit contains the minimal viable version; later commits modify shared files to add their entries.
   - **No forward references**: A commit must NEVER reference code, modules, paths, imports, or exports that don't exist yet in the chain. If a commit mentions it, it must exist at that point.
   - **Modify files to achieve this**: You MUST modify file contents to make each commit self-contained. This includes removing entries from package.json that reference future code, removing imports for future modules, and trimming config to match what exists.
   - **Config files go with their feature**: `vitest.config.e2e.ts` goes with the e2e test commit, not the init commit. The `bin` field in package.json goes with the CLI commit.

   Concrete examples of incremental evolution:
   - **package.json in init commit**: Only basic metadata, dependencies, and scripts -- NO `bin`, NO feature-specific `exports`, NO module-specific subpath imports
   - **package.json in feat(cli) commit**: ADD `bin` field, ADD `exports["./cli"]`
   - **package.json in feat(pull) commit**: ADD `exports["./pull"]` or `imports["#pull"]` if applicable
   - **tsconfig.json**: Only include paths that exist at that commit point
   - **vitest.config.ts**: Only the base test config in init; e2e-specific config added with e2e commit
   - **package.json `dependencies` in init commit**: Only packages actually imported by init-commit code -- NO packages used exclusively by future feature commits
   - **package.json in feat(api) commit**: ADD `dependencies` entries (e.g., `node-fetch`, `bottleneck`) that this feature's code imports
   - **package.json in feat(cache) commit**: ADD `better-sqlite3` to `dependencies` -- each commit introduces only the packages its own code requires
   - **Lock file** (`pnpm-lock.yaml` / `package-lock.json` / `yarn.lock`): Regenerated in EVERY commit that modifies `dependencies` or `devDependencies` -- run the package manager's lockfile-only install command (e.g., `pnpm install --ignore-scripts`) and include the lock file change in the same commit
   - **pnpm `allowBuilds`**: When a newly added package requires native build scripts (e.g., `better-sqlite3`, `esbuild`, packages using `node-gyp` or `prebuild-install`), add it to `allowBuilds` in `pnpm-workspace.yaml` in the same commit. See https://pnpm.io/settings#allowbuilds

   END IF

   Rules (apply to both modes):
   - This classification + dependency analysis is MANDATORY -- you must show both the categorization AND the dependency tree (or fixup mapping) before proceeding to Step 2
   - There are ZERO exceptions: initial commits, interdependent code, "everything is one feature" -- NONE of these exempt you from classification
   - If a single commit would contain more than ~20 files, look harder for sub-groups
   - The minimum expected output for any non-trivial change set is 2+ commits

4. **Risk Assessment**
   - Check for uncommitted changes
   - Verify no merge conflicts
   - Ensure build stability

### Step 2: Confirmation

Present a structured commit plan to the user BEFORE any git write operations.

IF `--retrospective`:

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

ELSE:

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

END IF

- Wait for explicit user confirmation before continuing
- If the user declines, abort gracefully with no side effects
- If the user requests changes to the plan, revise and re-present

### Step 3: Execution

IF `--retrospective`:

1. **Create fixup commits** (one per target):
   - Stage the relevant hunks (use `git add -p` for mixed-hunk files)
   - `git commit --fixup=<target-SHA>`

2. **Create new commits** for remaining changes:
   - Stage and commit normally following Commit Guidelines

3. **Rebase to squash fixups**:
   - Determine the base commit (parent of the oldest fixup target)
   - `GIT_SEQUENCE_EDITOR=true git rebase --interactive --autosquash <base>`
   - If merge conflicts arise, consult the backup at `$BACKUP_PATH` as reference for the intended final state (the backup reflects the full final working tree -- resolution may only need a portion of the backup file). Attempt auto-resolution; if complex, delegate to a teammate to resolve, then continue the rebase

4. **Display resulting history**:
   - `git log --oneline <base>..HEAD`

ELSE:

1. **File Staging**
   - Check git status for staged files
   - If no staged files, add all modified/new files
   - Confirm files ready for commit

2. **Commit Splitting**
   - Group changes by logical concern -- splitting is the default, not the exception
   - Stage files (and individual hunks via `git add -p` when needed) for each logical commit
   - **Merge conflict resolution**: If merge conflicts arise during rebase, consult the backup at `$BACKUP_PATH` as reference for the intended final state. Note: the backup reflects the final working tree -- merge conflict resolution may only need a subset of the backup file's content, not necessarily the entire file.
   - Create separate commits for each group, ordered so each commit is independently valid

3. **Commit Message Generation**
   - Analyze changes for commit type for each commit group
   - Generate message suggestions following the `Commit Guidelines` below

4. **Commit Creation**
   - Execute git commit with message and signature
   - Verify commit succeeded
   - Report completion status

END IF

### Step 4: Post-Commit Verification

> Skip this entire step if `--no-verify` is set.

After all commits are created, verify each affected commit passes quality checks.

1. **Identify affected commits** created during this session
2. **For each commit** (oldest to newest), delegate to a **teammate** (coding specialist subagent):
   - Teammate checks out the commit
   - Runs lint and tests with coverage
   - **Lint/coverage/test failures**: teammate investigates and presents a fix plan to the orchestrator. The orchestrator presents to the user for confirmation. Teammate does NOT auto-fix anything -- all fixes require explicit user approval before proceeding.
3. **After all fixes**: run `GIT_SEQUENCE_EDITOR=true git rebase --interactive --autosquash` to absorb fixup commits. Note: when preceded by retrospective execution (Step 3), this rebase applies only to fixup commits from the verification loop itself, not a re-run of the retrospective rebase.
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

### Step 5: Integrity Verification

**Check**: If the PostToolUse hook fired after a `git rebase`, you'll see an `── Integrity Check ──` block in stderr output. If present, read the results below.

**If no auto-verify output** (hook didn't fire, or last operation wasn't a rebase), run manually:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/verify.sh"
```

| `GIT_TREE_MATCH` | `CONTENT_MATCH` | Action |
|---|---|---|
| PASS | PASS | Integrity confirmed → Step 6 |
| FAIL | PASS | Staging/rebase error → **STOP**, show diff, await user |
| PASS | FAIL | Non-git files changed → **STOP**, show diff, await user |
| FAIL | FAIL | Significant corruption → **STOP**, show diff, await user |

### Step 6: Reporting

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

## Examples

### Simple Commit

```bash
/commit
# Runs pre-commit checks, presents plan, creates single commit
```

### Skip Verification

```bash
/commit --no-verify
# Skips pre-commit and post-commit verification for quick commits
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

### Retrospective Commit

```bash
/commit --retrospective
# Classifies changes as fixups to prior commits or new commits.
# Uses git blame to map changed hunks to original commit SHAs.
# Presents retrospective plan (fixups + new + projected history).
# Creates fixup commits, rebases to squash, verifies chain.
# Combine with --no-verify to skip pre/post-commit checks.
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

- Title: aim for <=50 characters; if a longer title offers better clarity, use up to 72 characters; 72-character hard limit
- Present tense, imperative mood
- No period at end of subject line
- Follow conventional format:
  - `<type>: <description>` for global or non-project/feature specific changes
  - `<type>(<scope>): <description>` for project or feature specific changes -- use **short package name** as scope, dropping the catalog prefix (e.g., `@theriety/`, `@amino/`). For cross-package concerns, name the concern. For global changes, omit scope.

**Atomic Commits**:

- Each commit serves a single logical purpose
- Related changes grouped together, unrelated changes split into separate commits
- Logical grouping takes priority over historical accuracy -- the goal is an ideal commit chain, not a record of how code was developed
- Intermediate states do NOT need to have existed independently during development -- they just need to be logically coherent
- Each split commit MUST be standalone: it must compile, pass lint, and pass all tests independently. If splitting would break a commit in isolation, adjust the grouping until every commit is self-contained and green
- Shared files (package.json, tsconfig, configs) MUST evolve incrementally -- each commit adds only the entries it introduces. The init commit contains the minimal viable version; later commits modify the file to add their entries.
- Dependencies (`dependencies`/`devDependencies`) MUST be added progressively -- each commit only adds packages that its own code imports. Lock files must be regenerated and included in every commit that changes dependency entries.
- A commit must NEVER contain forward references to code, modules, or files that don't exist yet in the chain. If a file references future code, you must modify it to remove those references for that commit.

**Split Criteria**:

- Different concerns or modules
- Mixed change types (feat/fix/docs)
- Large changes needing breakdown
- Different file patterns
- Initial commits (empty repo with many files -- MUST still be split)
- "Interdependent" code (all code is interdependent -- split by concern anyway)

> NEVER refuse to split for ANY of these reasons:
> - "artificial splitting would create false intermediate states" -- creating ideal logical commits IS the purpose of this skill
> - "this is the initial commit" or "no prior commits exist" -- initial commits follow the exact same splitting rules
> - "files are interdependent" or "everything is one feature" -- all code is interdependent; split by concern anyway
>
> A file MAY appear in multiple commits if different hunks serve different logical purposes.
