---
name: plan-code
description: Generate DRAFT.md as a commit blueprint and PLAN.md as an execution roadmap from an approved proposal or specification. Use when planning implementations, defining atomic commits, documenting change proposals, or preparing a coding workflow with explicit verification and ownership boundaries.
model: opus
context: fork
allowed-tools: Read, Glob, Grep, Bash, Write, Task, TodoWrite, AskUserQuestion, ExitPlanMode
argument-hint: "[--design=DESIGN.md] [--change=\"description\"]"
---

# Plan Code

Turn approved design documents, informed by optional discovery evidence, into
two artifacts: `DRAFT.md`, a commit
blueprint with copy-paste-ready code, and `PLAN.md`, a lightweight execution
roadmap of atomic, testable commits. `specification:spec-code` owns creating
the specifications this skill plans against; `coding:takeover` and
`specification:implement-code` own executing the resulting plan.

## Boundaries

- Use for: generating `DRAFT.md` and `PLAN.md` from design documents,
  processing `*_PROPOSED.md` proposals into `*_CHANGE.md` change records, and
  refining commit structure interactively before implementation begins.
- Do not use for: implementing code or touching source files, running git
  commits/pushes/branches, creating design specifications from scratch
  (`specification:spec-code`), executing an existing plan
  (`coding:takeover`), or modifying original design files directly.
- Refuse when: no design specification exists (run `specification:spec-code`
  first), the working directory is not a git repository, the request is
  implementation or commit execution rather than planning, or the design is
  too vague to plan against — name the missing sections when refusing.

## Inputs

- **Required**: at least one design document reachable from the working
  directory (`DESIGN.md`, `REQUIREMENTS.md`, `DATA.md`, `UI.md`, `NOTES.md`,
  or `REFERENCE.md`).
- **Optional**: `--design=<path>` to point at a specific design file
  (default: scan the current directory); `--change="description"` to focus
  planning on a described change; a reachable `DISCOVERY.md` evidence ledger.
- **Prerequisites**: the working directory is a git repository.

<IMPORTANT>
Coherence mandate: every plan revision must produce one continuous,
deliberate document. When a proposal modifies an existing `DRAFT.md` or
`PLAN.md`, rewrite the affected sections so the result reads as a single
coherent roadmap — never the prior plan with a "Proposed changes" appendix,
a parallel second step list, or visible patch seams.
</IMPORTANT>

## Workflow

1. Validate the environment: confirm the git repository, parse `--design`
   and `--change`, then scan for and read every design or discovery document
   present (`DISCOVERY.md`, `DESIGN.md`, `REQUIREMENTS.md`, `DATA.md`, `UI.md`,
   `NOTES.md`, `REFERENCE.md`). Preserve `DISCOVERY.md` provenance labels;
   inference and accepted assumptions do not become specification facts.
2. Scan for `*_PROPOSED.md` proposals. When found, present a summary and ask
   for approval; on approval, compare each proposal against its original and
   write the differences to a matching `*_CHANGE.md`. With no proposals,
   continue directly.
3. Build and present the decision surface before drafting implementation. Gather
   current architecture, technology stack, tests and coverage, then lead with
   the choices most expensive to change: data models and migrations, public
   interfaces and type contracts, user-visible flows and states, dependencies,
   security/privacy posture, and integration boundaries. Classify each as
   resolved, accepted low-impact assumption with a recheck trigger, explicitly
   deferred with an owner, or blocking. Route an underexplored material choice
   to `essential:discover`; route grounded competing options to
   `essential:decide`.
4. Refine the decision surface interactively via `AskUserQuestion`: each
   question offers 2-4 alternatives with clear rationales, prioritized by how
   much the answer changes architecture, scope, or acceptance criteria. Ask one
   high-coupling question at a time; batch only independent questions. Do not
   generate copy-paste-ready code while a blocking decision remains.
5. Generate `DRAFT.md`: cross-reference every source document and decision,
   plan the atomic commits, then write the draft with the decision surface at
   the top, a file-structure section showing commit associations, and a commit
   plan carrying full copy-paste-ready file contents. Put mechanical refactoring
   after the data, interface, UX, and integration decisions. Every commit must
   satisfy this checklist:
   - self-contained and independently testable
   - 100% test coverage for its scope
   - clear separation of concerns from other commits
   - conventional commit format `type(scope): description`
   - multiple commits per phase allowed
   - full file contents provided, copy-paste ready
6. Present a draft summary and request approval of `DRAFT.md`.
7. On approval, generate `PLAN.md`: group commits into phases and write the
   implementation phases, execution order, success criteria, accepted
   assumptions with recheck triggers, deferred decisions with owners, and
   evidence that requires a plan pivot.
8. Run the quality gate: spawn one review subagent via `Task` (a single
   reviewer — the artifacts are few and interdependent, so fan-out buys
   nothing), passing `DRAFT.md`, `PLAN.md`, and all design documents. It
   must verify architecture alignment with `DESIGN.md`, that every
   `REQUIREMENTS.md` item has both implementation and tests, schema accuracy
   against `DATA.md`, component fidelity to `UI.md`, adherence to `NOTES.md`
   decisions, and the absence of test-coverage gaps. Reviews are read-only.
   On findings, update `DRAFT.md`/`PLAN.md` and re-run the checklist.
9. Finalize proposals: replace each `*_PROPOSED.md` with its final version
   and preserve the `*_CHANGE.md` records.
10. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker
   remains, then report the blocker instead of looping.

## Verification

- Every commit in `DRAFT.md` satisfies the six-point checklist.
- The decision surface precedes implementation detail and contains no blocking
  decision disguised as an assumption.
- Every `REQUIREMENTS.md` item maps to at least one commit containing both
  implementation and tests.
- The review subagent's checklist passed with no open findings.
- Every `DRAFT.md` commit appears in exactly one `PLAN.md` phase and the
  execution order respects inter-commit dependencies.
- `PLAN.md` records accepted assumptions, deferred decisions, and pivot signals.

## Completion

Report the design source, proposals processed (and `*_CHANGE.md` files
written), the number of commits in `DRAFT.md` and phases in `PLAN.md`, the
quality-gate result, and next steps: review `DRAFT.md` for code accuracy,
review `PLAN.md` for execution order, then start implementation with
`coding:takeover` or `specification:implement-code`. A refusal names the
missing prerequisite — absent specs, vague sections, or a non-git directory.
