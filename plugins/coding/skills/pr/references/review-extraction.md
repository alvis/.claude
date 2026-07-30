# Creating the review tree

Load this from *Locate or create the review tree* in `coding:pr review`, once reuse
has been ruled out. The change-tracking path was already selected; follow only its
row.

## Checkout forms

Fetch the head through `pull/<n>/head`, which resolves same-repo and fork heads
alike without adding a remote. `jj` has no equivalent for fetching a bare PR ref, so
`git fetch` is correct even on the jj path — in a colocated repository both share the
same object store, and the fetched commit is immediately visible to `jj`.

Create owned trees through `scripts/temp-tree.sh`; its lease is the cleanup
handle and keeps shell functions or traps out of the skill tool call.

| Case | Condition | Helper |
|---|---|---|
| jj workspace | In the target repository, jj path | `temp-tree.sh open-jj "$REPOSITORY_ROOT" "$HEAD_OID"` |
| git worktree | In the target repository, git path | `temp-tree.sh open-git "$REPOSITORY_ROOT" "$HEAD_OID"` |
| Fresh clone | Not in the target repository, or `--repo` names another | `gh repo clone "$OWNER/$REPO" "$REVIEW_DIR" -- --no-checkout`, then fetch and `git -C "$REVIEW_DIR" checkout --detach "$HEAD_OID"` |

The workspace and worktree forms reuse local objects and are the fast path. In the
clone form the clone is itself the disposable checkout, so its cleanup has no
registration to release first.

## Cleanup contract

For an owned tree, run
`bash "${CLAUDE_PLUGIN_ROOT}/skills/pr/scripts/temp-tree.sh" close "$TREE_LEASE"`.
The helper releases the git worktree or jj workspace before deleting its
guarded temporary lease directory.

<IMPORTANT>
The `REVIEW_TREE_OWNED` guard and exact helper-issued lease are the whole safety
property. A reused tree belongs to the user; never pass it to `close`.
</IMPORTANT>

Close on pass, failure, blocked discovery, and cancellation alike, then confirm
nothing was left behind:

```bash
jj workspace list 2>/dev/null | grep -F "$REVIEW_DIR" && echo "stale jj workspace"
git worktree list | grep -F "$REVIEW_DIR" && echo "stale git worktree"
```

A stale entry is a reportable failure with its recovery command
(`jj workspace forget <name>` or `git worktree prune`).

Read files from the review tree and nowhere else, so the review reflects the PR head
rather than whatever the local working copy happens to hold.
