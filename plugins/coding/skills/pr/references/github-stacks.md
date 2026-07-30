# GitHub Stack Interoperability

This optional operator map adapts the non-interactive workflows from
[`github/gh-stack`](https://github.com/github/gh-stack/blob/main/skills/gh-stack/SKILL.md).
Load it when `gh stack --help` succeeds and the user asks for GitHub Stack
grouping or an existing PR chain is already grouped there.

<IMPORTANT>
`gh stack` does not replace this plugin's owners. Shape or rewrite history
through `coding:commit`; author, push, lease, create/update PRs, review, and
drive CI through `coding:pr`. Use `gh stack` here for GitHub grouping and
machine-readable inspection after those owners have produced verified heads.
</IMPORTANT>

## Select the integration path

For jj, Sapling, git-town, or skill-owned Git history, use `gh stack link`.
It creates no local tracking state and is the upstream-recommended bridge for
externally managed branches. Require at least two PRs and pass branch names in
bottom-to-top order so a numeric first argument cannot be mistaken for a stack
number:

```bash
gh stack link --base "$DESTINATION" --remote "$REMOTE" \
  "$BOTTOM_BRANCH" "$NEXT_BRANCH" "$TOP_BRANCH"
```

Run it only after `coding:pr create` or `coding:pr update` has pushed and
verified every branch and PR. Omit `--open` while new PRs must remain draft;
pass it only when the caller explicitly requested ready-for-review state.
Because branch arguments may be pushed and bases may be corrected, re-read
every PR head SHA, base, and draft state after linking.

When a plain-Git checkout is already tracked by `gh stack`, its navigation and
JSON view may be used for discovery. Local branch creation, commits, rebases,
sync, pushes, and submission still route to the owners above; do not run
`init`, `add`, `rebase`, `sync`, `push`, or `submit` as a shortcut around their
validation and review loop.

## Create or extend

1. Shape independent bottom-to-top changes through `coding:commit`.
2. Publish through `coding:pr create`; for an extension with at least one open
   PR, use `coding:pr update` against the lowest existing PR.
3. Link the complete open chain with explicit `--base`, `--remote`, and branch
   arguments. To append to a known GitHub stack, an explicit stack number may
   be the first argument followed by only the new branches or PRs.
4. Verify the branch/PR chain through `gh pr view`. When local tracking already
   exists, also require `gh stack view --json` to report the expected order,
   heads, PR URLs, merge state, and `needsRebase: false`.

`gh stack link` is additive: it can append and repair bases, but it does not
remove existing members. A repository without GitHub Stacks support may reject
grouping; keep the already verified ordinary PR chain and report that optional
grouping was unavailable.

## Update a lower layer

Put the fix in the earliest unmerged owner. Run `coding:commit` there, then
`coding:pr update <lowest-affected-pr>` so descendants are replayed, pushed
with leases, reviewed, and driven through CI. Re-link the complete open order
after that supported update returns, then verify every head/base pair and
grouping. If linking changes any review surface unexpectedly, re-enter
`coding:pr update` rather than treating the earlier convergence as current.

This is the same invariant as `gh stack rebase --upstack`: a lower-layer edit
must propagate through every dependent branch. The PR skill uses its own
restack helper because it records exact expected SHAs, merged skips, partial
remote progress, and post-push base verification.

## Reorder, remove, or rename

GitHub grouping and branch history are separate state. For a structural edit:

1. Snapshot the stack number, destination, bottom-to-top PR/branch/head/base
   map, and `gh stack view --json` output when local tracking exists.
2. Run `gh stack unstack <stack-number>` to remove the GitHub grouping without
   deleting PRs or branches. Use `--local` only when intentionally keeping the
   remote grouping.
3. Reshape and rename through `coding:commit --reorder` or the applicable
   commit workflow. Prove content equivalence and linear ancestry.
4. Republish through `coding:pr update` when any selected head has an open PR;
   use `coding:pr create` only when none does.
5. Re-link the full new branch order, then verify every remote head, PR base,
   draft state, and GitHub grouping.

Unstack first for removal or reorder because linking is additive. Never delete
an underlying PR or branch merely to change its stack membership.

## Non-interactive and recovery rules

- Give `init`, `add`, and `checkout` explicit arguments if they are ever used
  for read/setup work; bare forms prompt. `submit` requires `--auto`, and
  `view` requires `--json`.
- Set `--remote` or `remote.pushDefault` when multiple remotes exist.
- Do not trust exit status alone. `gh stack sync` can report an aborted
  local/remote divergence with a successful exit; always verify post-state.
- Treat push/submit as non-transactional. Earlier branches may update before a
  later lease fails; recover from the recorded remote head map.
- A conflict must be completed or aborted explicitly. Never leave a rebase or
  partially regrouped stack as success.
- After squash or rebase merges, skip the stale merged head and replay only
  live descendants from the new destination, as
  [workflow-correct-merged.md](../../commit/references/workflow-correct-merged.md)
  and [merge.md](merge.md) require.
