# Naming

Read this before naming a work stream, a branch, or a generated document.
Every name here is decided by following these rules — there is no deriving
executable, and none should be written.

## Slugs

Lowercase ASCII words joined by single hyphens. Fold accents to their base
letter, drop everything else, and collapse runs of separators to one hyphen:
`Crème brûlée déjà vu` is `creme-brulee-deja-vu`, `Payments / refunds?! v2.0`
is `payments-refunds-v2-0`. Shorten by dropping whole trailing words, never
part of a word.

Keep a slug at or under 48 bytes, which is the widest a generated filename
gets before it stops fitting a listing. Where one word is longer than that on
its own, cut the word — there is no smaller boundary left to keep.

A name with nothing to fold — `影師嗎` — leaves an empty slug, which is not a
name. Write an English slug for what the thing is instead; the source string
was never the identity, only the usual shortest route to one.

## Work ID

A slug naming what the work is about, kept at or under 32 bytes — the ID is
repeated in every state path, in the source tree path, and in a branch that
itself nests under a type and over a slice, so 32 keeps the longest of those
(`feat/<work-id>/01-<scope>`) inside a terminal column and a PR title. That
bound is the convention, not a gate: a longer name chosen deliberately is
honoured, and only the shape is enforced, since a name outside the grammar
does not survive the trip through a path and a branch. The ID carries no type
prefix — the type belongs to the branch, not to the identity:

```text
work-id-naming
contract-footprint-budget
eng-421-checkout-refunds      # a stream that came from a tracker keeps its key
```

That one name is the stream's state directory (`.state/works/<work-id>/`) and
its source tree directory (`~/.workspaces/<project>/<work-id>`).

A work ID is an identity and is never renamed or reused. Before taking one,
read every ID under `works/` **and** `archive/`; if the name is occupied,
append the next free ordinal — shortening the scope first so the ordinal still
fits in 32 bytes, since `<31-byte-name>-2` would not. That ordinal makes a
distinct stream, not a slice of the one it collided with.

Those directories are where a name is looked up, not what makes it spent: a
name is taken while **any** trace of it survives, including a branch or a
source tree left behind by a stream whose `works/` entry is already gone. Take
a colliding name only after establishing that nothing is still using it.

Retirement deletes a stream's `works/` and `archive/` directories after its
retention window, so those two directories cannot be the only record of which
IDs are spoken for. A retired ID is still spent, and a stream with nothing to
promote is the case that proves it — code-only work leaves no durable document
to carry its name. Retirement therefore records every ID it retires in
`docs/retired-work-ids.md`, whether or not anything else was promoted
([retirement.md](retirement.md)). One record per line, the ID first and the
retirement date after it (`refunds 2026-07-27`), so the ID is readable as the
first field. That file is the third place a new name is checked against.

## Branch

The branch is the work ID under a conventional-commit type: `<type>/<work-id>`.
A stream that is one pull request is that branch alone; a stream split into a
stack or into sub-tasks is a set of numbered branches beneath it, ordinals
always exactly two digits:

```text
feat/<work-id>                    # the whole stream, one PR
feat/<work-id>/01-resolver        # a stack or sub-task split
feat/<work-id>/02-contract
feat/<work-id>/03-docs
```

So a work ID of `work-id-naming` gives `feat/work-id-naming`, and its stack
slices are `feat/work-id-naming/01-resolver` and so on. The type describes the
branch, never the identity: it is not part of the ID or the state path, and
`fix/work-id-naming` resolves to the same stream as `feat/work-id-naming`.

Git stores refs as files, so `feat/<work-id>` and `feat/<work-id>/01-resolver`
cannot both exist — creating the second while the first is present fails with
`cannot lock ref`, locally and on the remote alike. A stream that grows past
one pull request therefore cannot add a numbered branch beside the bare one;
it **renames** the bare branch into the first slice, which frees the namespace
in the same operation that vacates it. Both refs need it: `git branch -m`
(or `jj bookmark rename`) clears the local namespace, and the forge's own
branch rename clears the remote one while retargeting the open pull request —
never delete the remote ref instead, since that closes the pull request on it.

Renaming leaves this checkout pointing at a ref that is gone. Run
`git fetch --prune` and reset the renamed branch's upstream before pushing
anything: a stale `origin/<type>/<work-id>` fails the next
`--force-with-lease` with `stale info`, because the lease is a claim about a
remote value that no longer exists, and the same stale flat ref blocks
fetching the numbered child that has taken its name. Only once both renames
and that prune have landed do the later slices push.

The segment after the ordinal is free-form: name the slice, not its
`GIT-PR-TYPE-01` category.

Naming the branch this way is what lets the workspace resolution step select
the stream from whichever branch is checked out. Only these two shapes
resolve; anything else means the PM is asked instead — which is the intended
outcome, not a failure.

## Documents

- `docs/specs/<capability>/` takes the owning capability, never the task
  title.
- ADRs alone carry a zero-padded monotonic numeric prefix
  (`decisions/0007-<decision-slug>.md`) and are never renumbered.
- Ordinary work-local children take unnumbered semantic `<slug>.md` names —
  never `part-1`, `misc`, or the task title.
- Numbered `<nn>-<topic-slug>.md` children, in increments of 10, are reserved
  for the mechanical split of an oversized file.
- Two documents whose names would collide in the same directory: the later one
  takes the next free ordinal, as a work ID does (`change-explainer.md`, then
  `change-explainer-2.md`). Never overwrite a sibling to claim its name.
