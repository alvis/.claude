# Creating the review tree

Load this from *Locate or create the review tree* in `coding:review-pr`, once reuse
has been ruled out. The change-tracking path was already selected; follow only its
row.

## Checkout forms

Fetch the head through `pull/<n>/head`, which resolves same-repo and fork heads
alike without adding a remote. `jj` has no equivalent for fetching a bare PR ref, so
`git fetch` is correct even on the jj path — in a colocated repository both share the
same object store, and the fetched commit is immediately visible to `jj`.

| Case | Condition | Checkout |
|---|---|---|
| jj workspace | In the target repository, jj path | `jj workspace add --revision "$HEAD_OID" "$REVIEW_DIR"` |
| git worktree | In the target repository, git path | `git worktree add --detach "$REVIEW_DIR" "$HEAD_OID"` |
| Fresh clone | Not in the target repository, or `--repo` names another | `gh repo clone "$OWNER/$REPO" "$REVIEW_DIR" -- --no-checkout`, then fetch and `git -C "$REVIEW_DIR" checkout --detach "$HEAD_OID"` |

The workspace and worktree forms reuse local objects and are the fast path. In the
clone form the clone is itself the disposable checkout, so its cleanup has no
registration to release first.

## Cleanup contract

```bash
cleanup() {
  if [ "${REVIEW_TREE_OWNED:-false}" = true ] &&
     [ -n "${REVIEW_DIR:-}" ] && [ "$REVIEW_DIR" != / ]; then
    jj workspace forget "$(basename "$REVIEW_DIR")" >/dev/null 2>&1 ||
      git worktree remove --force "$REVIEW_DIR" >/dev/null 2>&1 || true
    rm -rf -- "$REVIEW_DIR"
  fi
}
```

<IMPORTANT>
The `REVIEW_TREE_OWNED` guard is the whole safety property. A reused tree is the
user's working copy or worktree; removing it destroys real work. Never widen this
condition, and never call `cleanup` for a tree this run did not create.
</IMPORTANT>

Release the workspace or worktree registration before removing the directory —
skipping the release leaves a stale entry in `jj workspace list` or
`git worktree list` even after the files are gone. Run on pass, failure, blocked
discovery, and cancellation alike, then confirm nothing was left behind:

```bash
jj workspace list 2>/dev/null | grep -F "$REVIEW_DIR" && echo "stale jj workspace"
git worktree list | grep -F "$REVIEW_DIR" && echo "stale git worktree"
```

A stale entry is a reportable failure with its recovery command
(`jj workspace forget <name>` or `git worktree prune`).

Read files from the review tree and nowhere else, so the review reflects the PR head
rather than whatever the local working copy happens to hold.
