---
name: build-data
description: Build or extend a data orchestrator from an approved work-local specification through schema, operations, controller integration, tests, canonical review, and handoff. Use for new data domains, operations, or Prisma schemas; keep audits in audit-data.
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<domain-name> <operations...> --work-id=<id> [--extend] [--notion-url=...]"
---

# Build Data

Own the implementation lifecycle for `@theriety/data-{domain}` while treating
the work-local specification and PM state as coordination boundaries.

## Boundaries and inputs

- Require domain, operations/entities, and `--work-id=<id>`. Validate verb
  contracts and package prerequisites. Optional extend mode, Notion ref, and
  selector pattern remain supported.
- Do not build services or audit existing data layers.
- Workers may edit assigned source/tests and work-local child artifacts only;
  they never edit `working.md`, `state.md`, or overview indexes.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve the work root;
   read `working.md`, then `state.md`, then referenced plan/spec paths.
2. Materialize a supplied/stale Notion specification via
   `specification:sync-spec`. Use exact receipt paths and refs. Detect new/extend
   mode, validate dependencies/verbs, read existing surfaces, choose selector
   pattern (`simple` up to three entities, otherwise `complex`), and produce an
   implementation manifest tied to acceptance criteria.
3. Dispatch one schema owner with
   [references/schema-implementation.md](references/schema-implementation.md).
   Proceed only when Prisma generation and package build pass.
4. In new mode, run `coding:setup-project` for the established data-package
   structure. Draft typed operation signatures, selectors, exports, and
   controller wiring once through `coding:draft-code`; bodies belong only to
   the implementation step.
5. Dispatch related operation batches (maximum three) using
   [references/operation-implementation.md](references/operation-implementation.md),
   then one controller integration owner. Every child receives the Essential
   contract path, work/spec pointers, acceptance slice, and manifest contract.
6. Run Coding fix/lint/refactor and the package's exact typecheck/lint/test
   gates. Run `coding:review-code` into the work's canonical `reviews/`
   directory and reconcile `review.md`; loop findings through the owning fix
   step within bounded retries.
7. For any material implementation departure, create a lowercase
   `changes/<slug>.md` child with evidence/disposition and return PM
   reconciliation for `changes.md`/`state.md`. Contract drift also routes to
   `reviews/alignment.md`; do not create a deviations log.
8. Commit through `coding:commit` after approval or hand over through
   `coding:handover` when incomplete. Collect child manifests, deduplicate, and
   return explicit final paths generated or materially rewritten as
   `generated_files`. Do not run `wc -c`; the PM performs the final batch pass.

## Verification

- Prisma generation and package typecheck/lint/tests pass; every requested
  operation is implemented, integration-tested, and exposed by the controller.
- Review summary and canonical area details agree with no unreported blocker.
- Spec refs/acceptance mappings and material departures are traceable.
- No worker edited PM-owned files; reconciliation and `generated_files` are
  complete.

## Completion

Report work/spec receipt, mode, package, entities/selectors/operations, gates,
canonical review result, commit/handover, departures, PM reconciliation, and
`generated_files`.
