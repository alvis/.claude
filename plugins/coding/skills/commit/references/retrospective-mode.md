# Retrospective Mode (`--retrospective`)

Active when `--retrospective` flag was recorded in Step 1. Workflow continues linearly through all steps but the classification, confirmation, and execution branches behave as below.

## Step 1.3 — Classification (retrospective branch)

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
- No fixup targets found: Fall back to normal (non-retrospective) classification (see `references/splitting.md`)
- All changes are fixups: Skip new-commit creation, proceed directly to rebase in Step 3
- Target SHA not in current branch: Treat the change as a new commit instead

## Step 2 — Confirmation (retrospective branch)

Present this plan to the user BEFORE any git write operations:

```text
## Retrospective Commit Plan

### Fixups

Target: abc1234 feat(auth): add login endpoint
  - Fix validation bug in auth.ts
  - Add missing error handler in auth.ts

Target: def5678 test(auth): add login tests
  - Fix assertion in login.spec.ts

### New Commits

  feat(auth): add logout endpoint
  Files: auth.ts, auth.spec.ts

### Projected History (after rebase)

  abc1234' feat(auth): add login endpoint        [amended]
  def5678' test(auth): add login tests            [amended]
  ghi9012  feat(auth): add logout endpoint         [new]

Proceed? [Y/n]
```

Wait for explicit user confirmation before continuing. If the user declines, abort gracefully with no side effects. If the user requests changes to the plan, revise and re-present.

## Step 3 — Execution (retrospective branch)

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
