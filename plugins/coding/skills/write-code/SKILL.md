---
name: write-code
description: 'Write production-ready code end to end through a TDD lifecycle of design, skeleton, implementation, tests, and refactoring. Use for new functions, features, modules, components, CLI or API endpoints, or approved tickets; route diagnosed failures to fix and explicit production stubs to complete-code.'
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<instruction> [--resume]"
---

# Write Code

Composite orchestrator for the complete TDD lifecycle. It owns phase order,
interactive gates, PM state reconciliation, and final artifact batching; atomic
children own implementation phases. Remove superseded scaffolding rather than
leaving parallel paths or addenda.

## Boundaries

- Use for new functions, features, modules, components, endpoints, or an
  approved specification implemented and tested end to end; use `--resume` for
  a rehydrated engineering work item.
- Route skeleton-only work to `coding:draft-code`, accepted production stubs to
  `coding:complete-code`, diagnosed failures to `coding:fix`, green structural
  cleanup to `coding:refactor`, and reviews to `coding:review-code`.
- Reject vague requirements without acceptance criteria or projects without a
  configured test framework.

## Inputs

- Required `<instruction>` with scope, behavior, and acceptance criteria.
- Optional `--resume`; require a resolved work ID/root whose `state.md` defines
  unfinished scope. A missing local root must be rehydrated through
  `coding:takeover`, never recovered from root continuation files.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Resolve the workspace-local work root,
schemas, lifecycle, and final batch interface before dispatching children.
A direct PM run resolves or mints the work ID by the contract; every delegated
child receives the explicit work ID/root.

The main agent/PM owns `working.md` and reconciliation of `state.md`,
`proposals.md`, `changes.md`, `decisions.md`, and `design.md`. Every child reads
`working.md` first, then `state.md` and only its linked relevant detail/spec
paths. Children never write `working.md`; they may write assigned child,
review, evidence, source, and test files and return `generated_files` to the PM.

## Composition

Run child skills in this order:

1. `coding:setup-project`, only if essential structure is missing.
2. `coding:draft-code`, for types, skeleton, canonical implementation markers,
   and red/pending test structure.
3. `coding:complete-code`, then `coding:complete-test` for pending tests.
4. `coding:fix` for diagnosed test/type/lint failures; mechanical standards
   route to `coding:lint` and coverage/fixture work to `coding:complete-test`.
5. `coding:refactor` for green behavior-preserving cleanup.
6. `coding:commit --create-pr` for a conditional split, or `coding:push-pr` for
   an existing-stack restack, per
   [references/stack-split.md](references/stack-split.md).

Pass `--from-composite` only to children that declare it (`setup-project`,
`draft-code`, `fix`, `refactor`). Never pass it to `complete-code` or
`complete-test`.

## Workflow

1. Parse the instruction. Separate user intent, observed facts, inferences,
   accepted reversible assumptions, and unresolved decisions. Resolve material
   unknowns before dependent work. Initialize or refresh the work root and
   `state.md` with the complete goal, plan/lifecycle, criteria, decisions,
   dependencies, blockers, reviews, evidence, promotion, and sync state; link
   `working.md`. Refresh PM-owned `working.md` with current focus and fast paths
   only, aiming editorially at 4,096 bytes.
2. For `--resume`, read `working.md`, `state.md`, and linked artifacts; map the
   recorded file substate to `draft-code`, `complete-code`, `fix`, or
   `refactor`. Revalidate contradictions reported by takeover before resuming.
3. Conditionally invoke setup, then invoke each required implementation child
   in composition order. Give it the work ID/root and exact relevant paths, and
   require an explicit `generated_files` manifest.
4. After each child, verify its manifest and evidence, reconcile full lifecycle
   truth into `state.md`, refresh `working.md`, and reconcile any lazy overview
   whose children changed. A material deviation is recorded in state and, when
   it changes an approved contract, in an alignment review; stop invalidated
   branches and revalidate remaining work.
5. After draft, completion/tests, fix, and refactor, offer: proceed; rerun the
   current child with change direction; resume elsewhere; or pause through
   `coding:handover`.
6. Apply the stack decision. <IMPORTANT>Never invoke `jj split` or
   `gh pr create` directly; history shaping belongs to `coding:commit` and
   publication belongs to `coding:push-pr`.</IMPORTANT>
7. After every artifact writer is finished, deduplicate the combined
   `generated_files` manifest. Select only `.md` paths inside the resolved
   target `.engineering/`, excluding `working.md`, and invoke the Essential
   checker once when eligible paths remain. If it returns `split_required`,
   coordinate one complete split round for all oversized files, preserving
   each original as overview, then run one new batch pass. Never size files
   after each write; paths outside `.engineering/`, including `docs/**`, are
   not mechanically size-gated.
8. Run tests, types, lint, and coverage for the touched scope. Route each
   failure to its owner and repeat until green or concretely blocked.

## Verification

- Tests, types, lint, and the repository coverage target pass; no owned
  implementation or pending-test markers remain.
- `state.md` contains complete current truth and links current-focus-only
  `working.md`; all lazy indexes match their children.
- Every child returned a verified `generated_files` manifest and the scoped
  `.engineering` Markdown gate ran as one batch per pass when applicable.
- Commit/push ownership was preserved and any stack dispatch reported URLs.

## Completion

Report requirements, phases run/skipped, material discoveries, assumptions and
recheck triggers, deviations, decisions, blockers, validation, stack outcome,
work root, and the deduplicated `generated_files` list. Recommend
`/coding:commit` when no stack was dispatched.
