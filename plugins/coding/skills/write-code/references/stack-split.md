# Conditional Stack Split and Restack

After `coding:refactor` lands and before reporting, decide whether the
resulting change should be sliced into a stack of ordered draft PRs, or
whether an existing open stack needs restacking. The orchestrator never
invokes `jj split` or `gh pr create` directly — it always delegates to
`coding:commit`.

## 1. Compute change size

Prefer `jj diff --summary --stat` when the working copy is jj-colocated;
fall back to `git diff --shortstat HEAD`. Capture the changed-file count and
the LOC diff.

## 2. Detect an open stack

Scan for bookmarks matching `<branch-prefix>/NN-<scope>`, for example via
`jj bookmark list` or `git branch --list '*/[0-9][0-9]-*'`.

## 3. Apply triggers

- **Large change** — more than 5 changed files, OR more than 300 LOC diff,
  OR multiple loosely-coupled domains (the bounds keep each PR independently
  reviewable). Dispatch `coding:commit --create-pr --from-composite` to slice
  the working copy into reviewable, ordered draft PRs.
- **Restack on semantic upstream change** — when an open stack is detected
  AND this change semantically modifies code that a lower (earlier-in-order)
  PR in the stack depends on: the signature, behavior, or contract of a
  symbol the lower PR establishes or relies on. Dispatch
  `coding:commit --from-composite` so the post-rewrite restack runs
  automatically. Incidental file overlap alone (formatting, unrelated
  co-edits) does not trigger a restack — judge by lower-PR correctness
  dependence.
- **Otherwise** (small, single-domain change with no semantic upstream
  impact): skip the dispatch and proceed straight to reporting.

## 4. Interactive gate

When a dispatch is triggered, surface the rationale — the size metrics or the
named lower PRs at risk — and the proposed mode to the user before
delegating. The child skill drives its own confirmation gates.
