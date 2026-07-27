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

## Work ID

A slug naming what the work is about, at most 32 bytes. It carries no type
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

Retirement deletes a stream's `works/` and `archive/` directories after its
retention window, so those two directories cannot be the only record of which
IDs are spoken for. A retired ID is still spent: the durable promotion record
retirement leaves under `docs/` names it, and that record is what a later
stream checks before reclaiming a familiar-looking name.

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
slices are `feat/work-id-naming/01-resolver` and so on. The type is chosen for
the work, and never becomes part of the ID or of the state path.

Git stores refs as files, so `feat/<work-id>` and `feat/<work-id>/01-resolver`
cannot both exist — creating the second while the first is present fails with
`cannot lock ref`. A stream that grows past one pull request moves into the
namespace: push the numbered branches first, repoint any open pull request at
the branch that now carries its commits, and delete the bare branch last, so
no published pull request is ever left without a head.

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
