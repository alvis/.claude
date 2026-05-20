# `--create-pr` — materialise stacked draft PRs

Opt-in stacked PRs. Per-PR loop is **LLM-driven** (no script) because `/coding:write-pr` is invokable only by the orchestrating agent. See [SKILL.md](../SKILL.md).

## When triggered

- User passes `--create-pr`
- Or default save / split detects multi-domain work AND user opts into stacking when prompted

## Pre-conditions

1. Chain is already CLEAN and LINEAR up to `main@origin`. If not, run `--reorder` first ([workflow-reorder.md](./workflow-reorder.md)).
2. Each change in the chain compiles + lints + tests standalone.
3. All conventional titles match the regex in [conventional-commits.md](./conventional-commits.md).
4. No change in the chain is already merged on origin (else → [workflow-correct-merged.md](./workflow-correct-merged.md)).
5. Branch prefix is known: derive from the chain's overall scope, or take from `--branch-prefix <name>`.

## Procedure (per change, in stack order)

The LLM walks the chain bottom-up. The plan is held in the LLM's working context — NO JSON proposal file.

For each change in order, with index `NN` starting at `01`:

### 1. Split (only when the change isn't already isolated)

If `@` still contains multi-change diffs (no upstream split done), carve out the next PR's files:

```bash
jj split <file1> <file2> ... <fileN>
```

If the upstream flow already produced separate changes, skip this step.

### 2. Validate + set the description

Validate the conventional title against [conventional-commits.md](./conventional-commits.md) regex BEFORE running `jj describe`. On match:

```bash
jj describe <change_id> -m "<conventional-title>" -m "<body>"
```

Reject and re-prompt if regex fails.

### 3. Set bookmark per `GIT-PR-STACK-01`

```bash
jj bookmark set <branch-prefix>/NN-<scope> --revision <change_id>
```

Bookmark format: `<branch-prefix>/NN-<scope>` where `<scope>` matches the conventional commit scope (kebab-case, ≤30 chars). Examples:

```
feat-avatar/01-data
feat-avatar/02-service
feat-avatar/03-web
```

### 4. Push the bookmark

```bash
jj git push --bookmark <branch-prefix>/NN-<scope> --allow-new
```

For an unmerged bookmark being updated after a rewrite, jj uses force-with-lease by default.

### 5. Invoke `/coding:write-pr`

Delegate title + body composition entirely to the sibling skill:

```text
/coding:write-pr <change_id>
```

The skill returns the conventional title and full PR body on stdout. Capture both. Never compose inline.

### 6. Open the draft PR per `GIT-PR-STACK-06`

```bash
# $TITLE and $BODY captured from /coding:write-pr stdout
gh pr create \
  --draft \
  --title "$TITLE" \
  --body-file - \
  --base "<prev_bookmark_or_main@origin>" \
  --head "<branch-prefix>/NN-<scope>" \
  <<<"$BODY"
```

`--base`:
- For the FIRST PR in the stack: `main` (the upstream branch tracked by `main@origin`).
- For each subsequent PR: the bookmark of the previous PR (e.g. PR 02's base is `feat-avatar/01-data`).

Capture the returned PR URL.

### 7. Advance to the next change

Move `@` (or the LLM-tracked pointer) to the next change in the chain and repeat steps 1-6.

## Hard rules

- LLM, NOT a shell script, owns the loop — `/coding:write-pr` cannot be called from inside bash.
- Conventional regex enforced PER PR before any mutation in that iteration.
- NEVER `git push` directly; only `jj git push --bookmark`.
- Bookmark naming MUST follow `GIT-PR-STACK-01` (`<branch-prefix>/NN-<scope>`).
- All PRs created as DRAFTS per `GIT-PR-STACK-06`.
- Base chain mirrors jj parent chain — each PR rebased downstream when ancestors update.

## Mandatory follow-ups

- **`restack.sh` REQUIRED after ANY subsequent edit** to a change with a downstream bookmark:

  ```bash
  bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/restack.sh" <branch-prefix>
  ```

  This loops over unmerged bookmarks in the stack, rebases each, re-pushes, and reparents the open PR via `gh pr edit --base`.

- Integrity check + project scripts per [SKILL.md](../SKILL.md) Step 5.
- Report each PR URL in the Step 6 summary.

## Error / edge cases

| Symptom | Action |
|---|---|
| `gh pr create` fails (auth) | `gh auth status`; surface to user. |
| Bookmark already exists | `jj bookmark set` is idempotent on the same revision; on conflict, confirm and update. |
| One change in the chain is merged on origin | STOP → [workflow-correct-merged.md](./workflow-correct-merged.md). |
| `/coding:write-pr` returns non-conventional title | Reject; re-invoke or surface to user. |
| Push rejected (remote ahead) | `jj git fetch`; rebase locally; retry. |
| User wants to skip drafts (open as ready-for-review) | Drop `--draft`; ONLY with explicit user consent — default per `GIT-PR-STACK-06` is draft. |
