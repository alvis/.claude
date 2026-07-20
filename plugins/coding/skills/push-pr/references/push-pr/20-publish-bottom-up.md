# Publish bottom-up

### 3. Publish bottom-up

Require a saved, clean, linear chain to `main@origin`, standalone green changes,
conventional descriptions per
[conventional-commits.md](../../../commit/references/conventional-commits.md), no
selected change merged on origin, and a derived or supplied branch prefix. If
needed, invoke `coding:commit --reorder`; for merged history follow
[workflow-correct-merged.md](../../../commit/references/workflow-correct-merged.md).

For each change bottom-up, preserve its existing bookmark when the caller
selected an existing branch, it is already the head of an open PR, or the
ordered stack already has explicit bookmarks. This is existing-bookmark mode:
push and update that exact head; never replace it with a generated bookmark.
Only for an unbookmarked new change/stack, index `NN` from `01` and set
`BOOKMARK=<branch-prefix>/NN-<scope>` where scope matches the conventional
commit scope (kebab-case, at most 30 characters). Record which mode selected
each bookmark before mutation.

```bash
jj bookmark set "$BOOKMARK" --revision "$CHANGE_ID"
jj git push --bookmark "$BOOKMARK" --allow-new
```

Never use `git push`; jj updates rewritten bookmarks with force-with-lease.
Invoke `coding:write-pr <change-id>` and capture its exact `title\n\nbody`
output as `TITLE` and `BODY`. Set `BASE=main` for PR 01 and the previous
bookmark for every later PR. When no open PR has this head, create a draft:

```bash
gh pr create --draft --title "$TITLE" --body-file - \
  --base "$BASE" --head "$BOOKMARK" <<<"$BODY"
```

When the head already has an open PR, update it without duplication and retain
draft state:

```bash
gh pr edit "$PR" --title "$TITLE" --body-file - --base "$BASE" <<<"$BODY"
gh pr ready "$PR" --undo # skip only when already draft
```

Capture each PR number, URL, head, base, bookmark, and change ID. After each
push, record `expected_head_oid` from the pushed bookmark and verify it against
`gh pr view "$PR" --json headRefOid --jq .headRefOid`; a mismatch is not the
published result and must be resolved before monitoring. After any accepted
repair/history rewrite with downstream bookmarks, synchronize the whole stack
before monitoring again:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/push-pr/scripts/restack.sh" \
  "$BOOKMARK_01=$EXPECTED_HEAD_OID_01" \
  "$BOOKMARK_02=$EXPECTED_HEAD_OID_02"
```

Supply every selected bookmark explicitly in bottom-up order with the exact
local git commit SHA expected after the rewrite; never rediscover the set from
a prefix. The sync script preflights the entire set, pushes each already-shaped
unmerged bookmark, verifies the remote SHA, and updates open PR bases with
`gh pr edit --base`; it does not reshape history. Verify the PR base chain and
each PR `headRefOid` mirror the recorded map.

| Publication error | Action |
|---|---|
| `gh pr create` authentication failure | Run `gh auth status`; report a user/external blocker. |
| Bookmark conflict | Confirm the intended change, then update the bookmark idempotently. |
| Push rejected because remote advanced | `jj git fetch`, rebase through `coding:commit`, then retry. |
| Conventional title invalid | Reword through `coding:commit`, then restart that iteration. |
| Existing PR has wrong base | `gh pr edit "$PR" --base "$BASE"`, then verify. |
| Restack conflict | Resolve through `coding:commit`, run integrity checks, then republish bottom-up. |
