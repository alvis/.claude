# PR extraction into a temporary checkout

Load this at step 3 of `coding:review-pr`. The change-tracking path was selected in
step 2; follow only that path's row.

## Fetch the head

GitHub exposes every PR head — same-repo and fork alike — at `pull/<n>/head`, so
one fetch covers both and no fork remote is added:

```bash
git fetch --no-tags origin "pull/${PR}/head"
git cat-file -e "${HEAD_OID}^{commit}"
```

`jj` has no equivalent for fetching a bare PR ref; in a colocated repository this
`git fetch` is still correct on the jj path, because both share the same object
store. A missing object after a successful fetch means the head moved since step 1 —
re-resolve rather than review an older revision.

## Materialize the checkout

| Case | Condition | Checkout |
|---|---|---|
| jj workspace | In the target repository, jj path | `jj workspace add --revision "$HEAD_OID" "$REVIEW_DIR"` |
| git worktree | In the target repository, git path | `git worktree add --detach "$REVIEW_DIR" "$HEAD_OID"` |
| Fresh clone | Not in the target repository, or `--repo` names another | `gh repo clone "$OWNER/$REPO" "$REVIEW_DIR" -- --no-checkout`, then fetch and `git -C "$REVIEW_DIR" checkout --detach "$HEAD_OID"` |

The workspace and worktree forms reuse local objects and are the fast path. In the
clone form the clone is itself the disposable checkout, so cleanup is a plain
`rm -rf` with nothing to release first.

## Cleanup contract

```bash
cleanup() {
  if [ -n "${REVIEW_DIR:-}" ] && [ "$REVIEW_DIR" != / ]; then
    jj workspace forget "$(basename "$REVIEW_DIR")" >/dev/null 2>&1 ||
      git worktree remove --force "$REVIEW_DIR" >/dev/null 2>&1 || true
    rm -rf -- "$REVIEW_DIR"
  fi
}
```

Release the workspace or worktree registration before removing the directory —
skipping the release leaves a stale entry in `jj workspace list` or
`git worktree list` even after the files are gone. A form that does not apply is a
harmless no-op. Run on pass, failure, blocked discovery, and cancellation alike.

Afterwards, confirm nothing was left behind:

```bash
jj workspace list 2>/dev/null | grep -F "$REVIEW_DIR" && echo "stale jj workspace"
git worktree list | grep -F "$REVIEW_DIR" && echo "stale git worktree"
```

A stale entry is a reportable failure with its recovery command
(`jj workspace forget <name>` or `git worktree prune`).

Read files from `$REVIEW_DIR` and nowhere else — that is what makes the review
reflect the PR head rather than the local working copy.
