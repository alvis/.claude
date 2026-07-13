# Partial hunks → existing branch

Save a subset of `@`'s hunks directly onto an existing bookmark (typically `master`) without first carving `@` into two jj changes. Sibling to [workflow-split.md](./workflow-split.md), but the target is an existing branch — not a new sibling change. See [SKILL.md](../SKILL.md) for the overall pipeline.

## When triggered

- User names a target branch AND asks to save part of `@` (e.g. "land just the typo on master", "commit the doc fix to master and keep the rest on the feature branch").
- One concern in `@` logically belongs to a different already-existing branch.
- Not for stacked PR publication — `/coding:commit --create-pr` remains the compatibility call and delegates to [`coding:push-pr`](../../push-pr/SKILL.md).

If `@` mixes concerns but they all belong on the same new change → [workflow-split.md](./workflow-split.md).

## Pre-flight

This route rewrites history (`jj bookmark move --allow-backwards` can rewind a published branch). The PreToolUse backup hook fires per [SKILL.md](../SKILL.md) Step 0.

```bash
jj bookmark list | grep '^<target>'      # confirm target bookmark exists locally
jj log -r '<target>' --no-graph -T 'change_id.short() ++ " " ++ description ++ "\n"'
jj diff --stat                            # confirm the partial subset is identifiable
```

If the target is already merged on origin → defer to [workflow-correct-merged.md](./workflow-correct-merged.md).

## Procedure

### 1. Surface the hunk plan

List the files / hunks intended for the target branch. Get user confirmation before staging.

### 2. Stage hunks of interest

```bash
git add -p              # interactive hunk selection
# or: git add <path>... # for whole-file granularity
git diff --cached --stat
```

If `git diff --cached --stat` is empty → abort, no-op.

### 3. Emit the git commit

```bash
git commit -m "<conventional-subject>" -m "<body>"
```

- Conventional Commits subject regex MUST match BEFORE running, per [conventional-commits.md](./conventional-commits.md).
- Compose subject/body using the same rules as [workflow-save-local.md](./workflow-save-local.md) Step 4.
- `--no-verify` only if the user passed it to the skill.

This is the **sanctioned** hand-run `git commit` inside this skill (see Hard Rules carve-out below).

### 4. Import the new git commit into jj

```bash
jj git import
jj log -r '@-' --no-graph -T 'change_id.short() ++ " " ++ description ++ "\n"'
```

Capture the new change id from the second line.

### 5. Move the target bookmark

```bash
jj bookmark move <target> --allow-backwards --to <new-change-id>
```

- `--allow-backwards` is required only when the move is non-fast-forward. The skill MUST check (`jj log -r '<target>..<new-change-id>'` vs `jj log -r '<new-change-id>..<target>'`) and confirm with the user before a backward move.
- Outside this route, backward bookmark moves require explicit `--allow-rewrite-merged` consent per `GIT-PR-STACK-03`.

### 6. Hand off publication when requested

Invoke [`coding:push-pr`](../../push-pr/SKILL.md) with `<target>` after the
local bookmark move and integrity check. Its
[publication workflow](../../push-pr/references/publish-stack.md) owns the
push, remote tracking, and PR update.

### 7. Confirm leftover working copy

```bash
jj diff --stat
```

The unstaged hunks remain on `@` untouched — verify they match the user's expectation.

## Verification

The PostToolUse hook fires `verify.sh` after the rewrite ops. Read the `── Integrity Check ──` block per [SKILL.md](../SKILL.md) Verification. `GIT_TREE_MATCH` reflects the new HEAD on the target branch, not `@`.

Run project scripts (unless `--no-verify`):

```bash
npm run lint
npm run test
npm run build
```

## Hard rules carve-out

- This route is the ONE sanctioned use of hand-run `git commit` inside this skill.
- This route is the ONE sanctioned use of `jj bookmark move ... --allow-backwards` without an explicit `--allow-rewrite-merged` flag — the user-named target branch IS the consent.
- PR titles + bodies still go through `/coding:write-pr` if a PR follows.
- All other Hard Rules in [SKILL.md](../SKILL.md) still apply.

## Mandatory follow-ups

- If the target branch carries unmerged bookmarks downstream, invoke
  `coding:push-pr` with the resolved stack per the [SKILL.md](../SKILL.md)
  publication handoff.
- Report per [SKILL.md](../SKILL.md) Completion.

## Error / edge cases

| Symptom | Action |
|---|---|
| `git add -p` selected zero hunks | Abort, no-op. |
| `git commit` fails (pre-commit hook) | Surface output; fix; re-run from Step 3. Do NOT `--amend`. |
| Conventional regex fails | Fix subject; re-run from Step 3. Do not bypass. |
| Target bookmark not tracking remote | Let `coding:push-pr` publish it with the required new-bookmark handling. |
| Target already merged on origin | Defer to [workflow-correct-merged.md](./workflow-correct-merged.md). |
| Backward move not desired | Drop `--allow-backwards`; jj rejects the move; reconsider target. |
| Integrity check FAIL | STOP, surface diff, `jj op restore <id>` from Step 0 to roll back. |
