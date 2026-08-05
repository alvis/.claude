# GitHub PR Stacks

Use the current upstream skill at
<https://github.com/github/gh-stack/blob/main/skills/gh-stack/SKILL.md>, the
[official documentation](https://gh.io/stacks), and
`gh stack <command> --help` for the latest contract. Load this reference for
every GitHub PR-stack request, regardless of which `coding:pr` route received
it.

`gh stack` owns supported stack operations: initialize, add a layer, link,
checkout, view, rebase, sync, push, submit, modify, unstack, merge, and
navigate. `coding:commit` owns a plain commit within a layer, while
`coding:pr review` owns review. Do not route a supported stack action through a
generic jj/git implementation.

## Contents

- [Run the requested action](#run-the-requested-action)
- [List or check out](#list-or-check-out)
- [Create, extend, and publish](#create-extend-and-publish)
- [Update and synchronize](#update-and-synchronize)
- [Restructure or remove grouping](#restructure-or-remove-grouping)
- [Merge and navigate](#merge-and-navigate)
- [Verify and recover](#verify-and-recover)

## Run the requested action

Attempt the requested command or API call directly. Do not run `gh auth status`
or a general extension probe first. The root-help inspection for `stack list`
below is the sole capability-discovery exception. Authentication, repository
support, and extension availability are operational failures, not
preconditions.

If an attempted `gh stack` action reports that the extension is missing or
offers installation, ask before running:

```bash
gh extension install github/gh-stack
```

Never install implicitly. For every other failure, preserve stderr, stop, and
report the command and unchanged or partial state. Do not convert an auth or API
failure into a speculative setup step.

Agents must select non-interactive forms:

| Action | Agent form | Avoid |
| --- | --- | --- |
| inspect | `gh stack view --json` | bare `view` |
| submit | `gh stack submit --auto [--remote <name>]` | bare `submit` |
| checkout | `gh stack checkout <target>` | bare `checkout` |
| initialize | `gh stack init [--base <trunk>] <branch>...` | bare `init` |
| add layer | `gh stack add <branch>` | bare `add` |
| merge | `gh stack merge <target> --yes --<method>` | interactive merge |

`modify` is an interactive TUI and has no non-interactive restructure form.
An agent may use only `modify --continue` or `modify --abort` for an existing
session; otherwise ask the user to operate the TUI or use the explicit
unstack-and-reinitialize path below.

Set `--remote <name>` on `link`, `push`, `submit`, `sync`, and `rebase` when the
repository has multiple remotes. `checkout` has no remote flag: use configured
remote resolution and stop on the command's actual ambiguity or remote error.

## List or check out

For `/coding:pr stack list`, first inspect the subcommand table advertised by
`gh stack --help`. This is capability discovery, not an authentication
preflight. If root help reports that the extension is missing or offers
installation, ask for confirmation. On acceptance, install the latest extension
with `gh extension install github/gh-stack`, rerun root help, and select from
the newly advertised capabilities. On an explicit decline, use the REST
fallback below.

If root help advertises a non-mutating `list` subcommand, inspect
`gh stack list --help` and use only its documented non-interactive,
machine-readable form. If current help documents no such form, use the REST
fallback rather than inventing flags or parsing human-oriented output.

Do not use `gh stack list --help` itself for capability detection: when `list`
is unadvertised, that call may misleadingly print root help and exit zero.
Never substitute bare `gh stack checkout`, which is an interactive checkout
chooser rather than a list operation.

If the installed extension does not advertise `list`, use the current
repository's paginated `GET /repos/{owner}/{repo}/stacks` REST endpoint. Fetch
every page and retain the JSON for agent decisions. Unlike the checkout chooser,
the REST inventory keeps fully merged and closed stacks returned by the API.

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
    head: .head.ref,
    headSha: .head.sha
  }]
}] | sort_by(.number) | reverse' <<<"$STACKS_JSON" || exit $?
```

An empty array is success. A nonzero API status is failure; preserve stderr and
stop.

Bare `gh stack checkout` is a human-only interactive checkout chooser for local
and remote stacks. It is never a list or discovery action. Agent checkout is
explicit and deterministic: require the caller's stack number, PR number, PR
URL, or locally tracked branch. As plugin safety policy, require a clean
worktree before either checkout path below; this is not an upstream CLI
precondition:

```bash
WORKTREE_STATUS=$(git status --porcelain) || exit $?
test -z "$WORKTREE_STATUS" || {
  echo 'refusing stack checkout: worktree has uncommitted changes' >&2
  exit 1
}
```

For the preferred selector, then run an explicit
`gh stack checkout <stack-number>`:

```bash
gh stack checkout "$STACK_SELECTOR" || exit $?
git branch --show-current || exit $?
gh stack view --json || exit $?
```

Prefer a stack number from the selected listing path. Resolution tries a
numeric stack number first, then a locally tracked PR, a GitHub PR, and a
local-only branch. A PR URL is accepted. A branch name resolves only against
local stack tracking. Remote checkout may fetch PR branches and create local
tracking branches; verify the selected branch and JSON composition afterward.
If checkout reports that a different local stack already covers those branches,
it cannot force replacement. Report the conflict. Only with explicit approval,
rerun the clean-worktree guard above immediately before removing that local
tracking, then retry the same explicit checkout:

```bash
gh stack unstack --local || exit $?
gh stack checkout "$STACK_SELECTOR" || exit $?
git branch --show-current || exit $?
gh stack view --json || exit $?
```

## Create, extend, and publish

For a new plain-Git stack, initialize explicit bottom-to-top branches and add
later layers with current extension commands:

```bash
git config rerere.enabled true || exit $?
gh stack init --base "$DESTINATION" "$BOTTOM" "$NEXT" "$TOP" || exit $?
gh stack add "$NEW_TOP" || exit $?
```

Existing branches are adopted by `init`; missing ones are created, and the last
branch is checked out. Enabling rerere prevents `init` from opening its first-run
confirmation prompt. `add` must run from the current top. Use `coding:commit`
for each layer's plain commit rather than `add -m`/`-A`/`-u`.

For branches managed by jj, Sapling, git-town, or another history owner, link
the externally managed bottom-to-top chain without local gh-stack tracking.
Provide at least two branch or PR selectors:

```bash
gh stack link --base "$DESTINATION" --remote "$REMOTE" \
  "$BOTTOM_BRANCH" "$NEXT_BRANCH" "$TOP_BRANCH" || exit $?
```

`gh stack link` may push branches, create missing PRs, repair bases, and add
members; it never removes existing members. A known stack number may be the
first argument when appending new branches or PRs. `--open` marks new and
existing PRs ready for review, so omit it unless the caller requested ready
state. Because `link` creates no local tracking, verify its grouping through
the paginated Stacks REST projection above and verify every PR with
`gh pr view`.

For a locally tracked stack, publish with:

```bash
gh stack submit --auto --remote "$REMOTE" || exit $?
gh stack view --json || exit $?
```

`submit --auto` skips the editor and creates new PRs as drafts. Add `--open`
only when ready-for-review state was requested. Submission pushes branches,
creates or updates PRs and their bases, and creates or updates GitHub grouping.
The PR, base, and grouping steps are best-effort, so verify all remote state.

## Update and synchronize

Check out the earliest unmerged owning layer, put the plain commit there through
`coding:commit`, then propagate it with the extension:

```bash
gh stack checkout "$OWNING_BRANCH" || exit $?
# Invoke /coding:commit for the owning layer before continuing.
gh stack rebase --upstack --remote "$REMOTE" || exit $?
gh stack push --remote "$REMOTE" || exit $?
gh stack view --json || exit $?
```

Use `rebase --downstack` for trunk through the current layer, `--no-trunk` for
inter-layer alignment only, and `--continue` or `--abort` after conflicts.

For full remote reconciliation use:

```bash
gh stack sync --remote "$REMOTE" || exit $?
gh stack view --json || exit $?
```

`sync` fetches, reconciles remote membership, updates trunk, cascade-rebases,
pushes, refreshes PR state, and links two or more open PRs. It never creates
PRs. Add `--prune` only with explicit approval to delete local merged branches.
It may exit zero after a divergence abort or a push warning; verify post-state.

## Restructure or remove grouping

For a human-operated restructure, `gh stack modify` can drop, fold, insert,
reorder, and rename layers; afterward the agent runs
`gh stack submit --auto [--remote <name>]` to publish the new shape. Agents do
not drive this TUI.

For a deterministic regroup, record `gh stack view --json`, then remove only
the grouping with an explicit target:

```bash
gh stack unstack "$STACK_NUMBER" || exit $?
```

Stop and verify the intended remote unstack through the paginated Stacks REST
projection and `gh pr view`. Only after that verification succeeds, rebuild and
publish the local stack:

```bash
gh stack init --base "$DESTINATION" "$BOTTOM" "$NEXT" "$TOP" || exit $?
gh stack submit --auto --remote "$REMOTE" || exit $?
gh stack view --json || exit $?
```

`gh stack unstack <stack-number>` deletes neither PRs nor branches. `--local`
removes only local tracking and preserves GitHub grouping. GitHub may refuse
some members and keep the stack and local tracking, so verify both scopes after
the call. Verify remote unstack or regrouping through the paginated Stacks REST
projection and each member through `gh pr view`. After `unstack --local`, verify
that the former branch reports no local stack while the REST projection still
contains the remote grouping. Never delete or close a PR merely to change stack
membership.

## Merge and navigate

Use GitHub's atomic stack merge, not `gh pr merge` or the generic bottom-up
loop, for a GitHub PR stack:

```bash
gh stack merge "$STACK_OR_PR_NUMBER" --yes \
  --merge-method "$MERGE_METHOD" || exit $?
```

Bind `MERGE_METHOD` from the caller or repository policy; do not select a
default. The equivalent explicit flags are `--squash`, `--rebase`, or
`--merge`. A PR target merges that PR and every unmerged PR below it; a stack
target merges the whole stack. The operation is all-or-nothing unless a merge
queue accepts the stack, in which case repository queue policy controls
landing.

`gh stack up [n]`, `down [n]`, `top`, `bottom`, and `trunk` are supported
non-interactive navigation commands. For automation, prefer
`gh stack checkout <exact-branch-or-PR>` followed by `view --json` when the
destination is known. Do not use interactive `gh stack switch`.

## Verify and recover

After every locally tracked mutation, use `gh stack view --json` to confirm
saved local order, current branch, PR URLs, heads, bases, merge state, and
`needsRebase`. Its API refresh is best-effort, so separately use `gh pr view`
to verify remote head SHAs, bases, and draft state. For `link`, remote unstack,
and regrouping, verify grouping through the paginated Stacks REST projection;
`view --json` cannot verify state that has no local tracking.

- Do not trust exit status alone: divergence and push-warning paths can leave
  `sync` at exit zero. Verify post-state.
- `push` and `submit` may update earlier branches before a later lease fails.
  Preserve the pre-operation remote head map, report partial progress, and
  retry only after resolving the rejected branch.
- Resolve a rebase conflict, stage files, and run `rebase --continue`, or run
  `rebase --abort`; never leave a partial rebase as success.
- Repository support, authentication, API, ambiguity, lock, and invalid-input
  errors are command failures. Preserve their stderr and stop.
