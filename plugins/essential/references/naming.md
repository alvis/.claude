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

`<kind>-<scope>`, under 32 bytes, where `<kind>` is a conventional-commit type
(`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`,
`style`, `test`) and `<scope>` is what the stream is about:

```text
feat-work-id-naming
chore-contract-footprint-budget
```

That one name is also the stream's source tree directory
(`~/.workspaces/<project>/feat-work-id-naming`) and the root of its branch.

A work ID is an identity and is never renamed. Before taking one, read every
ID under `works/` **and** `archive/`; if the name is occupied, append the next
free ordinal (`chore-lint`, then `chore-lint-2`). That ordinal makes a
distinct stream, not a slice of the one it collided with.

Streams that come from a tracker keep the tracker's identifier instead
(`eng-421-checkout-refunds`); the `<kind>-<scope>` shape applies to a stream
the team names itself.

## Branch

The branch is the work ID with its first `-` as `/`. A stream that is one pull
request is that branch alone; a stream split into a stack or into sub-tasks is
a set of numbered branches beneath it, ordinals always two digits:

```text
feat/work-id-naming                    # the whole stream, one PR
feat/work-id-naming/01-resolver        # a stack or sub-task split
feat/work-id-naming/02-contract
feat/work-id-naming/03-docs
```

Git stores refs as files, so `feat/work-id-naming` and
`feat/work-id-naming/01-resolver` cannot both exist — creating the second
while the first is present fails with `cannot lock ref`. A stream that grows
past one pull request renames its branch into the namespace before adding the
second. The segment after the ordinal is free-form: name the slice, not its
`GIT-PR-TYPE-01` category.

Naming the branch this way is what lets `resolve-engineering-workspace` select
the stream from whichever branch is checked out. A branch shaped otherwise
resolves to nothing, and the PM is asked instead — which is the intended
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
