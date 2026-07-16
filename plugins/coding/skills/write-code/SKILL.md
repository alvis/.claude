---
name: write-code
description: 'Write production-ready code end to end through a TDD lifecycle of design, skeleton, implementation, tests, and refactoring. Use for new functions, features, modules, components, CLI or API endpoints, or approved tickets; route diagnosed failures to fix and explicit production stubs to complete-code.'
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<instruction> [--resume]"
---

# Write Code

Composite orchestrator for the complete TDD lifecycle: it owns sequencing,
interactive gates, and state handover, while each phase is owned by the
atomic child skill it invokes. Each pass updates the same implementation
cleanly — remove superseded scaffolding; never leave duplicate code paths or
addendum-style patches.

## Boundaries

- Use for: new functions, features, modules, components, CLI or API endpoints
  built with tests end to end; turning a spec or approved ticket into working
  code; resuming interrupted lifecycle work with `--resume`.
- Do not use for: skeleton only (`coding:draft-code`), completing accepted
  production stubs only (`coding:complete-code`), fixing failing
  tests/lint/types only (`coding:fix`), refactoring without the full
  lifecycle (`coding:refactor`), code review (`coding:review-code`), or a
  stack with no implementation (`coding:commit --create-pr` directly).
- Reject when: the instruction is too vague to define acceptance criteria
  (ask for specific requirements), or the target project has no testing
  framework configured.

## Inputs

- **Required**: `<instruction>` — feature requirements with enough detail to
  derive scope and acceptance criteria.
- **Optional**: `--resume` — continue from handover documents instead of
  starting fresh.
- **Prerequisites**: for `--resume`, CONTEXT.md, NOTES.md, and PLAN.md exist
  in the working directory; otherwise reject with "No handover files found.
  Create them first with /coding:handover".

## Composition

Child skills run in `context: fork`, in this order:

1. `coding:setup-project` — conditional: only when essential structure is
   missing.
2. `coding:draft-code` — design discovery plus skeleton with canonical
   `TODO(implementation):` markers and describe.todo/it.todo test structure.
3. `coding:complete-code` — green phase: minimal implementations that make
   tests pass; then `coding:complete-test` for any pending test markers it
   reports.
4. `coding:fix` — diagnosed test/type/lint failures with root-cause analysis
   (batches file sets over 25 files). Mechanical standards violations route
   to `coding:lint`; fixture, mock, pending-test, and coverage work routes to
   `coding:complete-test`.
5. `coding:refactor` — green behavior-preserving cleanup, naming, JSDoc, and
   final quality validation.
6. `coding:commit --create-pr` for a conditional stack split, or
   `coding:push-pr` for an existing-stack restack; see
   [references/stack-split.md](references/stack-split.md).

State handover: children read and update CONTEXT.md, NOTES.md, and PLAN.md. For
a fresh run, create NOTES.md before the first child and keep it live across the
lifecycle; `coding:handover` later completes the full three-file bundle when a
pause or transfer is requested.

Composite convention: pass the internal `--from-composite` flag only to
children that declare it (`setup-project`, `draft-code`, `fix`, `refactor`)
to suppress redundant confirmation gates. Never pass it to `complete-code` or
`complete-test` — give them their normal scope plus a concise parent context
in the Skill payload. Unknown internal flags are errors, not silently ignored
compatibility options.

## Workflow

1. Parse `<instruction>` and flags; identify requirements, scope, and
   acceptance criteria. Separate user-stated intent, observed repository facts,
   inferences, accepted assumptions, and unresolved questions. A material
   unknown affecting architecture, public API, data model, security/privacy,
   destructive migration, user-visible semantics, or acceptance criteria must
   be resolved or explicitly deferred before its dependent work starts. A
   low-impact reversible assumption may proceed conservatively with a recheck
   trigger recorded in NOTES.md. Initialize or refresh NOTES.md sections for
   Discoveries, Accepted Assumptions, Deviations, Pending Decisions, and
   Invalidated Plan Steps. With
   `--resume`, read the handover documents, map the file substate to the
   resume point (`need-draft` → draft-code, `need-completion` →
   complete-code, `need-fixing` → fix, `need-refactoring` → refactor), and
   extract change direction from PLAN.md next steps or NOTES.md open
   questions.
2. Conditional setup: check for essential structure (package.json, source
   directories, test framework); invoke `coding:setup-project` with the
   target path and `--from-composite` only when missing.
3. Invoke `coding:draft-code` with the instruction and `--from-composite`,
   then hold the interactive gate below.
4. Invoke `coding:complete-code` with the target area, then
   `coding:complete-test` for pending test markers; gate.
5. Invoke `coding:fix` with the target area and `--from-composite`; gate.
6. Invoke `coding:refactor` with the target area and `--from-composite`;
   gate.

   After each child, update NOTES.md from repository or runtime evidence. When a material
   deviation invalidates a plan premise, record the observed evidence and
   affected steps, stop the stale branch, and revalidate the remaining plan
   before continuing.

   Interactive gate (after each of steps 3-6): offer the user
   (1) proceed to the next step, (2) re-run the current child with change
   direction, (3) resume from a different step, (4) pause and create handover
   documentation via `coding:handover`.
7. Stack decision: apply
   [references/stack-split.md](references/stack-split.md) — compute change
   size, detect open stacks, and dispatch `coding:commit --create-pr` for a
   split or `coding:push-pr` for an existing-stack restack when a trigger
   fires, surfacing the rationale to the user first.
   <IMPORTANT>Never invoke `jj split` or `gh pr create` directly; local history
   shaping belongs to `coding:commit` and publication belongs to
   `coding:push-pr`.</IMPORTANT>
8. Run the verification below; when a check fails, route the failure to the
   owning child (`coding:fix` for diagnosed failures, `coding:complete-test`
   for test/coverage gaps) and re-run that check. Repeat until every check
   passes or a concrete blocker remains, then report the blocker instead of
   looping.

## Verification

- Tests pass, types check, and lint is clean for the touched area.
- Coverage meets the project target; no `TODO(implementation):` or pending
  it.todo markers remain in scope.
- When a stack dispatch was triggered, the owning child reported the opened or
  restacked draft PRs.
- NOTES.md distinguishes observations, accepted reversible assumptions,
  deviations, pending decisions, and invalidated plan steps; no material
  unknown was silently implemented.

## Completion

Report the parsed instruction, steps executed and skipped, files created and
modified, test/type/lint/coverage results, the stack outcome (skipped, or the
opened/restacked PRs with bookmark and URL), and next steps (typically
`/coding:commit` when no stack was dispatched). Include material discoveries,
accepted assumptions and recheck triggers, deviations, pending decisions, and
plan pivots from NOTES.md. For a rejection, name the
matching boundary and the skill to use instead.
