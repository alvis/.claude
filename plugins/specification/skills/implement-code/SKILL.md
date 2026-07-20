---
name: implement-code
description: Execute an approved specification work item from authoritative Notion-backed contract through delegated coding, review, completion sync, and durable derivation. Use after plan-code approval, when resuming partial work, or when auditing delivered ticket work.
model: opus
context: fork
allowed-tools: Task, Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion, Workflow, TodoWrite
argument-hint: "<notion-url-or-id> --work-id=<id> [--repo=<path>] [--dry-run] [--skip-approval]"
---

# Implement Specification

Orchestrate one specification work item. Coding skills own source/test edits;
commit/push skills own history and publication; Specification skills own
contract materialization, MDC authoring, alignment, and completion sync.

## Boundaries

- Do not author the contract directly, perform generic unticketed feature work,
  shape history, publish, or hand-edit `.mdc`.
- Consume the work-local plan under `.engineering/work/<work-id>/state/`; do
  not create or require root draft, plan, or deviations files.
- Material departures are work-local `changes/<slug>.md` children and PM
  state updates. Contract drift also appears in `reviews/alignment.md`.
- Subagents may write assigned children/evidence but never PM-owned
  `working.md`, `state.md`, overview indexes, or `review.md`.

## Inputs

- **Required**: Notion ref and `--work-id=<id>`.
- **Optional**: target repo, `--dry-run`, `--skip-approval`, `--use-cache`.
- **Prerequisites**: resolved active work state, Notion tooling, and target
  repository.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve active/default
   workspaces, work root, repository, and PM-owned state paths.
2. Invoke `Skill(sync-spec)` in `materialize` mode. `--use-cache` may reuse the
   work spec only when its receipt matches the requested root `ref:`, all files
   exist, and recorded hashes still match; otherwise refresh. Filename shape is
   never an identity gate.
3. Read `working.md` for fast pointers, then `state.md`, the linked plan detail,
   materialization receipt, relevant spec sections, and current code. Select
   exactly one mode and load its branch from
   [references/modes.md](references/modes.md): planned execution, iteration,
   draft-required, audit/complete, verify-only, mismatch, or refusal.
4. Build one evidence map from specification requirements to plan slices,
   implementation sites, tests, and acceptance evidence. Mark absent, partial,
   implemented, or contradictory behavior.
5. Run an architecture/contract soundness pass. Stop for unresolved material
   decisions. Record an approved contract answer only through `Skill(mdc)`,
   refresh the source hash in the work receipt, and re-read it before coding.
6. Require approval of mode, scope, evidence map, and soundness decisions unless
   skipped. `--dry-run` stops with the plan/evidence report and no writes.
7. Capture immutable `base_rev` before dispatch. Prepare PM reconciliation
   entries for plan phase and status; do not edit PM-owned files from children.
8. Execute by capability: when Workflow is available for a code-producing
   mode, load [references/execute-workflow.md](references/execute-workflow.md);
   otherwise use the sequential chain in `references/modes.md`. Every dispatch
   receives repo path, work id, exact spec pointers, plan slice, acceptance map,
   output-manifest contract, and deviation policy. On `pending_decision`, stop,
   ask, record via `mdc`, and resume the same run.
9. When commits land, load
   [references/stack-aware-sizing.md](references/stack-aware-sizing.md) and
   delegate any history/publication action to its Coding owner.
10. Invoke `Skill(review-implementation)` with the work id. Retry P0/P1
    alignment fixes at most three passes; general and security review run every
    pass. Then run the usage trace in
    [references/thought-experiment.md](references/thought-experiment.md).
11. If authoritative specification content changed and reviews approve it,
    invoke `Skill(sync-spec)` in `complete` mode. Require outbound verification,
    refreshed default mirror, regenerated versioned spec, derivation receipt,
    and dependent `needs_revalidation` results before `completed`.
12. Collect every child `generated_files` manifest, deduplicate it, and return
it to the PM with state/overview/review reconciliation payloads. Never run file
sizing; after all writers return, the PM checks only eligible work Markdown
inside the target `.engineering/`.

## Verification

- Materialization identity/hashes held before coding and every acceptance item
  has implementation/test evidence or a named gap.
- `base_rev` predates all children; history/publication stayed with Coding.
- Every material departure has evidence, disposition, and remaining-plan
  revalidation in a work-local change child.
- Alignment, correctness/general, and security evidence exist. Contract changes
  completed the verified Notion/derivation round trip.
- No child wrote PM-owned files or MDC; collected `generated_files` is complete.

## Completion

Report status, ticket/stage/mode, work and spec receipt paths, repo/base rev,
acceptance coverage, decisions, dispatched children/commits, departures,
review/usage verdicts, completion-sync/derivation/revalidation result, PM
reconciliation payload, and `generated_files`.
