# Manage Stacked Pull Requests

Load this reference when a create or update target contains multiple dependent
changes, when merge receives more than one PR, or when the caller has not chosen
a PR shape and the review surface may benefit from a stack.

## Suggest a stack

Calculate the active `GIT-PR-SIZE-*` zone from every changed file and net LOC,
including generated or vendored paths and project threshold overrides. The
default green zone is at most 15 files and 500 net LOC because that is the
review surface one reader can hold at once.

Require a split regardless of size or a standalone preference when one PR mixes
categories that the standard requires isolated, including migration with logic
(`GIT-PR-TYPE-03`) or mechanical refactoring with behaviour
(`GIT-PR-TYPE-04`). Otherwise respect an explicit standalone-or-stack choice.

When no shape was chosen, proactively suggest a stack when the proposed PR
exceeds the active green zone and its files form at least two domain-coherent
slices that compile, test, and deliver reviewable value in bottom-to-top order
without forward references.

Do not suggest a split based on counts alone. Generated output, an atomic
migration, or a mechanical refactor may be larger while remaining easier to
review as one change. Every proposed slice must be independently valid:
backward-compatible configuration, schema, contract, migration, or feature-flag
prerequisites may land before their consumers, but dangling updates may not.
Keep tests and lockfiles with the change that needs them. When splitting would
break integrity or merely scatter one mechanical operation, keep one PR and
apply its actual size zone.

Present the suggestion before publication:

```text
Suggested stack:
01 <conventional title> — <files or domain>; base: <destination>
02 <conventional title> — <files or domain>; base: <01 head>
...
```

Ask whether to use an optional proposed stack. A declined optional suggestion
proceeds as one PR with its zone-required sections. A mandatory category split
blocks publication until accepted and shaped through `coding:commit`; neither
path silently reshapes history.

## Stack contract

The default contract below applies when the caller is not operating a GitHub PR
stack. For a GitHub PR stack, [github-stacks.md](github-stacks.md) supersedes
these generic lifecycle operators wherever `gh stack` supports the action.

- Shape local history through `coding:commit`; `coding:pr` does not split,
  reorder, amend, or absorb changes.
- Name each head `<feature-slug>/NN-<scope>` per `GIT-PR-STACK-01`; `NN` is a
  zero-padded bottom-to-top ordinal.
- Require one linear chain from the destination through every selected head.
- Open every PR as draft. PR 01 targets the destination; each later PR targets
  the previous head.
- Fix a finding in the earliest unmerged change that owns it. Once a lower PR
  merges, fix forward instead of rewriting public history.
- Update and merge the complete affected chain bottom-up.

Load [github-stacks.md](github-stacks.md) for every GitHub PR-stack request,
including discovery, checkout, creation, publication, update, navigation,
restructure, unstack, or merge. Use the current `gh stack` commands there for
the stack lifecycle. `coding:commit` still owns a plain commit within a layer,
and `coding:pr review` still owns review. That reference owns the dynamic
selection between an advertised non-interactive machine-readable list
capability and its REST fallback.

## Inspect with jj

Use jj only when it is functionally colocated with Git. Inspect the candidate
chain and bookmark placement without mutating it:

```bash
jj log -r '<destination>@origin..<selected-top-change>' --no-graph \
  -T 'change_id.short() ++ " " ++ bookmarks ++ " " ++ description.first_line() ++ "\n"'
jj bookmark list --all
jj log -r '<parent-change> & ::<child-change>' --no-graph -T 'commit_id'
```

For new publication, the containment query uses the selected local change IDs
because remote bookmarks do not exist yet. For an existing stack, repeat it
with `<parent>@origin` and `<child>@origin` to verify the published chain. Every
query must return a commit ID for its adjacent pair. If one saved change must be
split, invoke `coding:commit` with the accepted slices. Reserve
`coding:commit --reorder` for an already partitioned chain that needs reordering
or reparenting. After the result is linear, use
`coding:pr create <bottom-change>` for new PRs or
`coding:pr update <bottom-pr-or-head>` for an existing stack. The create/update
workflow owns bookmark placement, leased pushes, PR bases, and the explicit
restack map.

After a lower PR merges, use `coding:pr merge` for the remaining round. It
records the pre-merge change IDs, rebases the child-exclusive root with
`jj rebase -s`, moves only the remaining bookmarks, and pushes them through
jj's remote-change safety checks.

## Inspect with Git

Inspect the candidate chain and branch placement without mutating it:

```bash
git log --reverse --oneline origin/<destination>..<selected-top-ref>
git branch --list '<feature-slug>/*'
git merge-base --is-ancestor <parent-commit> <child-commit>
```

For new publication, use selected local commit IDs. For an existing stack,
repeat the command with `origin/<parent-head>` and `origin/<child-head>`.
Every ancestry command must exit zero. If one commit must be split, invoke
`coding:commit` with the accepted slices; use `coding:commit --reorder` only
for an already partitioned chain needing reorder or reparenting. Then use
`coding:pr create <bottom-commit>` for new PRs or
`coding:pr update <bottom-pr-or-head>` for an existing stack. The create/update
workflow owns branch placement,
force-with-lease pushes, PR bases, and the explicit restack map.

After a lower PR merges, use `coding:pr merge` for the remaining round. It
records immutable parent tips and replays only child-exclusive commits with
`git rebase --onto <new-parent> <old-parent-tip> <child>`, then pushes each
remaining head with `--force-with-lease`. Retarget the immediate child's PR to
the destination and verify that base before resuming the next merge round.

## Verify

Before publication and after every restack, confirm:

- each change is independently green;
- branch/bookmark names and PR bases express the same bottom-to-top chain;
- each remote PR head SHA equals the recorded local SHA;
- no merged revision was rewritten;
- every new PR is still draft.

The create/update workflow owns publication and CI convergence; the merge
workflow owns per-round merge and descendant restacking. This reference owns
shape selection and the shared jj/git operator map.
