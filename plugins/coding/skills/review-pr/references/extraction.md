# PR extraction into a temporary checkout

Load this at step 3 of `coding:review-pr`. It covers fetching the PR head, the
three checkout forms, and the cleanup contract. The change-tracking path was
already selected in step 2; follow only that path's rows.

## Fetch the head

GitHub exposes every PR head — same-repo and fork alike — at `pull/<n>/head`, so
one fetch covers both and no fork remote is ever added:

```bash
git fetch --no-tags origin "pull/${PR}/head"
```

`jj` has no native equivalent for fetching a bare PR ref. In a colocated
repository this `git fetch` is still the correct call on the jj path: jj and git
share the same backing object store, so the fetched commit is immediately
visible to `jj`. Confirm the fetch landed the SHA the API reported:

```bash
git cat-file -e "${HEAD_OID}^{commit}"
```

A missing object after a successful fetch means the PR head moved between step 1
and here. Re-resolve the PR rather than reviewing an older revision.

## Materialize the checkout

| Case | Condition | Checkout |
|---|---|---|
| jj workspace | Inside the target repository, jj path selected | `jj workspace add --revision "$HEAD_OID" "$REVIEW_DIR"` |
| git worktree | Inside the target repository, git path selected | `git worktree add --detach "$REVIEW_DIR" "$HEAD_OID"` |
| Fresh clone | Not inside the target repository, or `--repo` names another one | `gh repo clone "$OWNER/$REPO" "$REVIEW_DIR" -- --no-checkout`, then fetch and `git -C "$REVIEW_DIR" checkout --detach "$HEAD_OID"` |

The workspace and worktree forms reuse local objects and are the fast path. The
clone form is self-contained: the clone *is* the disposable checkout, so its
cleanup is a plain `rm -rf` with no workspace or worktree to release first.

Detached is deliberate in every form. The review never needs a branch, and a
detached checkout cannot be mistaken for somewhere to commit.

## Cleanup contract

The trap from `SKILL.md` step 3 is installed **before** the checkout is created,
so an interrupted `jj workspace add` or `git worktree add` still cleans up. It
must satisfy all of the following:

- Guard `$REVIEW_DIR` against empty and `/` before removing anything.
- Release the workspace or worktree registration first, then remove the
  directory. Skipping the release leaves a stale entry in `jj workspace list` or
  `git worktree list` even after the files are gone.
- Tolerate a form that does not apply — the clone case has nothing to release —
  and never fail the run because a release command was a no-op.
- Run on pass, failure, blocked discovery, and cancellation alike.

After cleanup, confirm nothing was left behind and report the result:

```bash
jj workspace list 2>/dev/null | grep -F "$REVIEW_DIR" && echo "stale jj workspace"
git worktree list | grep -F "$REVIEW_DIR" && echo "stale git worktree"
```

A stale entry is a reportable failure with the exact recovery command
(`jj workspace forget <name>` or `git worktree prune`), not something to leave
for the next run to trip over.

## Reading the checkout

Reviewers read files from `$REVIEW_DIR` and nowhere else — that is what makes
the review reflect the PR head rather than whatever the local working copy
happens to contain.

<IMPORTANT>
The PR branch is untrusted code. Read it, grep it, and diff it. Do not run its
scripts, build, tests, install hooks, or any tooling it configures. Verifying
that CI passes is `coding:write-pr`'s job and happens on GitHub's runners, not
here.
</IMPORTANT>
