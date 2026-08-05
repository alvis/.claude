# GitHub Stack Interoperability

This optional operator map adapts the non-interactive workflows from the pinned
[`github/gh-stack` contract](https://github.com/github/gh-stack/blob/14fc42ed9b6c376a53b2f999f138d3bd26dac546/skills/gh-stack/SKILL.md).
Load it for the explicit `coding:pr stack` route, or when `gh stack --help`
succeeds and the user asks for GitHub Stack grouping or an existing PR chain
is already grouped there.

The upstream contract revision is `14fc42ed9b6c376a53b2f999f138d3bd26dac546`.
Re-check this pin before adopting a newer `gh stack` flag or behavior.

## Contents

- [Select the integration path](#select-the-integration-path)
- [Discover or check out an existing stack](#discover-or-check-out-an-existing-stack)
- [Create or extend](#create-or-extend)
- [Update a lower layer](#update-a-lower-layer)
- [Reorder, remove, or rename](#reorder-remove-or-rename)
- [Non-interactive and recovery rules](#non-interactive-and-recovery-rules)

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

## Discover or check out an existing stack

Both actions require authenticated GitHub CLI access:

```bash
gh auth status || exit $?
```

Stop if authentication fails. Listing requires only authenticated `gh` access
to a repository with the Stacks API; checkout additionally requires the
`github/gh-stack` extension.

`coding:pr stack list` lists the current repository's GitHub stacks through the
official paginated `GET /repos/{owner}/{repo}/stacks` REST endpoint. Never run
bare `gh stack checkout`: its no-argument picker combines local and remote
stacks and is human-only discovery because it requires a TTY. Fetch every page
and retain JSON for agent decisions:

```bash
REPOSITORY=$(gh repo view --json nameWithOwner --jq '.nameWithOwner') || exit $?
STACKS_JSON=$(gh api --paginate --slurp \
  -H 'Accept: application/vnd.github+json' \
  "repos/$REPOSITORY/stacks?per_page=100") || exit $?
jq '[.[][] | {
  number,
  url,
  base: .base.ref,
  open,
  pullRequests: [.pull_requests[] | {
    number,
    state,
    draft,
    mergedAt: .merged_at,
    head: .head.ref
  }]
}] | sort_by(.number) | reverse' <<<"$STACKS_JSON" || exit $?
```

An empty array is a successful empty result. A nonzero `gh api` status is a
failed discovery: preserve stderr and stop. In particular, the pinned client
treats HTTP 404 as stacked PRs unavailable for the repository.

`coding:pr stack checkout <stack-number-or-pr-number-or-pr-url-or-local-branch>`
requires the caller's explicit selector and a clean worktree. Bind
`STACK_SELECTOR` to that exact selector; for the preferred selector this runs
`gh stack checkout <stack-number>`:

```bash
gh stack --help || exit $?
WORKTREE_STATUS=$(git status --porcelain) || exit $?
test -z "$WORKTREE_STATUS" || {
  echo 'refusing stack checkout: worktree has uncommitted changes' >&2
  exit 1
}
REMOTE_COUNT=$(git remote | jq -Rsc 'split("\n") | map(select(length > 0)) | length') || exit $?
if [ "$REMOTE_COUNT" -gt 1 ]; then
  git config --get remote.pushDefault >/dev/null || {
    echo 'refusing stack checkout: configure remote.pushDefault' >&2
    exit 1
  }
fi
gh stack checkout "$STACK_SELECTOR" || exit $?
git branch --show-current || exit $?
gh stack view --json || exit $?
```

If the extension check fails, stop and ask whether to install it with
`gh extension install github/gh-stack`; do not install it implicitly.

Prefer the listed stack number. Resolution tries a numeric stack number first,
then a locally tracked PR, a GitHub PR, and finally a local-only branch; it also
accepts a PR URL. A nonnumeric local-only branch resolves only against local
stack tracking. A remote stack checkout fetches its PR branches, creates
missing local branches from their remote refs, completes local tracking setup,
and records local stack state. A stack number selects the topmost unmerged
branch; a PR number or URL selects that PR's branch. With multiple remotes,
require `remote.pushDefault` before checkout because this command has no
`--remote` flag.

On divergent composition between local and GitHub stacks, the extension
prompts a human to replace local state, delete remote grouping, or cancel. An
agent must stop and report both compositions instead of choosing. Likewise,
stop on any nonzero exit and preserve stderr; the pinned contract assigns
distinct failures to not being in a stack, API errors, invalid arguments,
ambiguity, lock contention, and unavailable repository support. Exit zero
means the command completed, but still verify the checked-out branch and
`gh stack view --json`. A human who uses the no-argument picker may also exit
zero after cancelling or finding no available stacks, so that mode never
proves a checkout occurred.

## Create or extend

1. Shape independent bottom-to-top changes through `coding:commit`.
2. Publish through `coding:pr create`; for an extension with at least one open
   PR, use `coding:pr update` against the lowest existing PR.
3. Link the complete open chain with explicit `--base`, `--remote`, and branch
   arguments. To append to a known GitHub stack, an explicit stack number may
   be the first argument followed by only the new branches or PRs.
   In the pinned upstream contract, `gh stack link --open` marks new and
   existing PRs ready for review; it is not merely a browser-opening flag.
   `gh stack submit --auto --open` likewise submits the stack with PRs ready for
   review. Use either only when the caller requested ready state.
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
3. Reshape through `coding:commit --reorder` or the applicable commit workflow.
   Preserve the head branch name of every open stacked PR: GitHub does not
   transfer a stacked PR's immutable head ref when a branch is renamed. If a
   reorder truly requires a different head name, stop after unstacking and get
   explicit approval for the close-and-recreate migration, recording the old
   PR/branch and replacement mapping. A non-stacked PR may use the forge's head
   rename operation, but verify the PR head/base map afterward and never close
   or delete it silently.
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
