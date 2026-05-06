---
name: commit
description: 'Create well-formatted atomic git commits using conventional commit messages. Triggers when: "commit my changes", "commit this", "make a commit", "git commit", "write a commit message". Also use when: staging and committing work-in-progress, splitting large diffs into atomic commits, generating conventional commit messages. Examples: "commit my changes", "commit these files as a fix", "make a conventional commit for this feature".'
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

Analyzes changes and creates atomic commits with conventional commit messages. Automatically runs pre-commit checks and suggests splitting large changes into multiple commits when appropriate.

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

   - IF `--retrospective`: classify each hunk as fixup-of-prior-commit vs new commit using `git blame`/`git log` and produce a fixup mapping. See `references/retrospective-mode.md` for the strategies table, classification rules, and edge cases.
   - ELSE: split by infrastructure-vs-feature, module boundary, then change type; build a dependency tree between groups and topologically order commits; evolve shared files (package.json, tsconfig, lock files, etc.) incrementally with no forward references. See `references/splitting.md` for the heuristic table, what-belongs-together rules, dependency-tree procedure, and incremental-evolution examples.

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

- IF `--retrospective`: present fixups + new commits + projected history per `references/retrospective-mode.md`.
- ELSE present the standard plan:

```text
## Commit Plan

Pre-commit checks: [PASS / SKIP (--no-verify)]

### Commit 1
  <type>(scope): <description>
  Files: <file list>

### Commit 2
  <type>(scope): <description>
  Files: <file list>

Proceed? [Y/n]
```

- Wait for explicit user confirmation before continuing
- If the user declines, abort gracefully with no side effects
- If the user requests changes to the plan, revise and re-present

### Step 3: Execution

- IF `--retrospective`: create fixup commits, then any new commits, then `GIT_SEQUENCE_EDITOR=true git rebase --interactive --autosquash <base>`, then display resulting history. See `references/retrospective-mode.md` for the full procedure including merge-conflict handling against `$BACKUP_PATH`.
- ELSE follow the standard execution path:

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
- [Type: Description]

## Next Steps (if applicable)
- [Push to remote]
- [Create pull request]
```

---

## Examples

See `references/examples.md` for usage variants: simple commit, `--no-verify`, suggested split, initial-project dependency-ordered split, `--retrospective`, error cases, and pre-commit failure handling.

## Commit Guidelines

**Message Format**:

- Title: aim for <=50 characters; if a longer title offers better clarity, use up to 72 characters; 72-character hard limit
- Present tense, imperative mood
- No period at end of subject line
- **No emoji prefix**: NEVER prefix the subject line with an emoji or emoji shortcode (e.g., do NOT use `:sparkles: feat: ...`, `✨ feat: ...`, or `feat: :bug: fix ...`). Plain conventional-commits format only.
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
