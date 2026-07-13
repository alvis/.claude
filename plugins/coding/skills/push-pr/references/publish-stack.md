# Publish a Saved Change or Stack

Publication is an orchestrator-driven bottom-to-top loop because
`coding:write-pr` is an agent skill, not a shell command. See
[SKILL.md](../SKILL.md). The parent holds the stack plan in working context;
do not create a JSON proposal file or publication script.

## Pre-conditions

1. The selected chain is saved, clean, and linear up to `main@origin`. If not,
   invoke `coding:commit --reorder` and resume only after its integrity checks
   pass (see [workflow-reorder.md](../../commit/references/workflow-reorder.md)).
2. Each change in the chain compiles + lints + tests standalone.
3. All conventional titles match
   [conventional-commits.md](../../commit/references/conventional-commits.md).
4. No selected change is merged on origin unless
   [workflow-correct-merged.md](../../commit/references/workflow-correct-merged.md)
   already completed the local rewrite and recorded the user's explicit
   consent; otherwise stop and route through that workflow.
5. Branch prefix is known: derive from the chain's overall scope, or take from `--branch-prefix <name>`.

## Procedure

Walk the selected chain bottom-up. For an existing open stack, retain its
bookmarks and PR numbers unless the parent chain requires a base repair.

For each change in order, with index `NN` starting at `01`:

### 1. Require an isolated saved change

If a change is mixed or unsaved, stop publication and invoke `coding:commit`
to split/save it. Resume from preconditions; `coding:push-pr` does not directly
mutate commit structure here.

### 2. Validate the description

Validate the existing description against
[conventional-commits.md](../../commit/references/conventional-commits.md)
before any remote mutation. If it fails, invoke `coding:commit` to reword it,
then restart this iteration.

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

### 5. Invoke `coding:write-pr`

Delegate title + body composition entirely to the sibling skill and capture
its exact `title\n\nbody` stream:

```text
coding:write-pr <change_id>
```

The skill returns the conventional title and full PR body on stdout. Capture both. Never compose inline.

### 6. Open or update the draft PR per `GIT-PR-STACK-06`

```bash
# $TITLE and $BODY captured from coding:write-pr stdout
gh pr create \
  --draft \
  --title "$TITLE" \
  --body-file - \
  --base "<previous-bookmark-or-main>" \
  --head "<branch-prefix>/NN-<scope>" \
  <<<"$BODY"
```

`--base`:
- For the FIRST PR in the stack: `main` (the upstream branch tracked by `main@origin`).
- For each subsequent PR: the bookmark of the previous PR (e.g. PR 02's base is `feat-avatar/01-data`).

Capture the returned PR URL.

When the head already has an open PR, update it instead of creating a
duplicate:

```bash
gh pr edit <pr> --title "$TITLE" --body-file - --base "<base>" <<<"$BODY"
gh pr ready <pr> --undo
```

The second command preserves the required draft state; skip it only when the
PR is already draft. Capture its PR number and URL with `gh pr view`.

### 7. Advance to the next change

Move `@` (or the LLM-tracked pointer) to the next change in the chain and repeat steps 1-6.

## Hard rules

- The orchestrator, not a shell script, owns the loop — `coding:write-pr`
  cannot be invoked from inside bash.
- Conventional regex enforced PER PR before any mutation in that iteration.
- NEVER `git push` directly; only `jj git push --bookmark`.
- Bookmark naming MUST follow `GIT-PR-STACK-01` (`<branch-prefix>/NN-<scope>`).
- All PRs created as DRAFTS per `GIT-PR-STACK-06`.
- Base chain mirrors jj parent chain — each PR rebased downstream when ancestors update.

## Mandatory follow-ups

- **`restack.sh` is required after every subsequent rewrite** of a change with
  a downstream bookmark:

  ```bash
  bash "${CLAUDE_PLUGIN_ROOT}/skills/push-pr/scripts/restack.sh" <branch-prefix>
  ```

  This loops over unmerged bookmarks in the stack, rebases each, re-pushes,
  and reparents each open PR via `gh pr edit --base`. The parent then confirms
  every PR base mirrors the jj parent chain.

- Run the `coding:commit` integrity check after any history rewrite and report
  every pushed bookmark and PR URL.

## Error / edge cases

| Symptom | Action |
|---|---|
| `gh pr create` fails (auth) | `gh auth status`; surface to user. |
| Bookmark already exists | `jj bookmark set` is idempotent on the same revision; on conflict, confirm and update. |
| One change in the chain is merged on origin | STOP → [workflow-correct-merged.md](../../commit/references/workflow-correct-merged.md). |
| `coding:write-pr` returns non-conventional title | Reject; invoke `coding:commit` to reword, then retry. |
| Push rejected (remote ahead) | `jj git fetch`; rebase locally; retry. |
| Existing PR has the wrong base | `gh pr edit <pr> --base <expected-parent-bookmark-or-main>`, then verify. |
| Restack conflicts | Stop; resolve through `coding:commit`, run integrity checks, then repush bottom-up. |
| User wants ready-for-review | Keep drafts unless the user explicitly authorizes dropping `--draft` or running `gh pr ready`. |
