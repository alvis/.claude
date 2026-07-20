---
name: push-pr
description: 'Publish saved changes as draft pull requests and drive GitHub CI to green. Use when asked to push the latest commit, create or update a PR, repush after a fix, babysit pending checks, repair red CI, monitor every check, or converge a PR stack.'
model: opus
argument-hint: "[<commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--dry-run]"
---

# Push Pull Request

Publish one saved change or an ordered stack as draft pull requests, then own the hosted-CI lifecycle until every PR is green or a concrete blocker requires user action or external state. Because repair can edit existing work, the governing rule is **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. `coding:write-pr` remains the PR-text owner.

## Boundaries

- Use for publishing or republishing a saved jj change, branch, current draft
  PR, or ordered stack and monitoring every GitHub check through repair.
- Do not use for saving work without publication (`coding:commit`), authoring
  PR text only (`coding:write-pr`), reviewing code, merging PRs, or creating a
  new stack solely by reshaping local history (`coding:stack-code`).
- Delegate noisy commands to one small read-only tester before publication and
  one small read-oriented poller after publication, following the repository
  [delegation contract](../../../governance/constitution/references/delegation.md).

<IMPORTANT>
- Ownership is singular: `coding:commit` owns direct history mutations;
  `coding:stack-code` orchestrates reshaping/reparenting when a root cause
  belongs in a lower PR outside the current PR; the
  [core publication phase](references/push-pr/20-publish-bottom-up.md) owns
  push, restack, and PR-base mechanics. The parent alone accepts
  fixer edits and performs commit, push, and restack mutations; the poller may
  dispatch exactly one scoped fixer when the red branch requires it.
- `--skip-local-test` skips only local command execution. It never skips CI
  discovery, publication, hosted monitoring, evidence, repair, or convergence.
- Fix root causes. MUST NOT weaken a correct test, alter a valid expectation,
  add ignores/suppressions, or delete checks merely to pass. Edit a test only
  when captured failure evidence proves the test itself is the root cause.
- Never report success while any PR in the resulting stack is pending or red.
</IMPORTANT>

## Inputs

- **Required**: none; default to the current saved jj change and include its
  ordered unmerged descendants when they form a stack.
- **Optional**:

| Input | Effect |
|---|---|
| `<commit-ref>` | Publish a resolvable jj change ID/revset/bookmark or git branch/SHA and its selected stack. |
| `--branch-prefix <name>` | Override the derived stack bookmark prefix. |
| `--skip-local-test` | Skip only the local tester dispatch and commands. |
| `--dry-run` | Print the test, publication, and monitoring plan without agents or local/remote mutations. |

- **Prerequisites**: a clean saved change or linear stack, a jj-colocated
  repository, authenticated `gh`, and remote push access.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Publication-only runs may proceed
without creating work artifacts; before any red-CI repair, resolve or mint the
work ID/root by that contract, read `working.md` then `state.md`, and give every
fixer only the relevant linked contract/evidence paths. Fixers never write
PM-owned `working.md` or reconcile overview files.

## Workflow

Load the workflow children in order. They are one publication lifecycle, and
later phases inherit every boundary and prerequisite established earlier.

1. [Resolve the target and reproduce local CI](references/push-pr/10-resolve-and-local-ci.md)
2. [Publish the stack bottom-up](references/push-pr/20-publish-bottom-up.md)
3. [Monitor hosted checks and repair root causes](references/push-pr/30-monitor-and-repair.md)
4. [Verify convergence and report completion](references/push-pr/40-verification-and-completion.md)

Do not report success before the final phase confirms every selected PR is
green. Return every project file materially rewritten by a repair in
`generated_files`; the PM owns the one final Markdown batch check.
