---
name: build-service
description: Build or extend a backend service from an approved work-local specification through manifests, implementation, tests, canonical review, and handoff. Use for new services, operations, integrations, webhooks, or manifest schemas; keep audits in audit-service.
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<service-name> <operations...> --work-id=<id> [--extend] [--notion-url=...]"
---

# Build Service

Own a service implementation lifecycle while consuming the active work
specification and preserving PM-owned coordination state.

## Boundaries and inputs

- Require service, operation descriptions, and `--work-id=<id>`. Optional data
  domain, integrations, peers, webhooks, guards, extend mode, and Notion ref
  remain supported.
- Do not build data packages, perform audit-only work, or invent an unresolved
  contract.
- Workers edit assigned source/tests and child evidence only, never
  `working.md`, `state.md`, or overview indexes.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve the work root;
   read `working.md`, then `state.md`, then referenced plan/spec paths.
2. Materialize a supplied/stale Notion specification via
   `specification:sync-spec`. Use receipt/frontmatter identity rather than a
   legacy independent specification export. Resolve new/extend mode, packages,
   operations,
   dependencies, and acceptance mappings; stop on ambiguity or missing data
   dependency.
3. Declare missing manifests using
   [references/manifest-declaration.md](references/manifest-declaration.md), at
   most three independent operations concurrently. Each child receives the
   Essential contract path, work/spec pointers, acceptance slice, and output
   manifest contract. Proceed only when schemas compile.
4. Scaffold new packages through `coding:setup-project`, then run the sequential
   draft/complete/test owners with context from
   [references/implementation-patterns.md](references/implementation-patterns.md).
5. Run Coding fix (maximum three cycles), lint, refactor, and exact package
   typecheck/lint/test gates. Run `coding:review-code` into canonical work-local
   review areas and reconcile `review.md`; findings return to their owning fix.
6. Record material departures in lowercase work-local change children, return
   PM reconciliation for `changes.md`/`state.md`, and route contract drift to
   alignment. Do not create a standalone deviations file.
7. Commit through `coding:commit` after approval or hand over through
   `coding:handover`. Collect/deduplicate child manifests and return explicit
final paths generated or materially rewritten as `generated_files`. Do not run
file sizing; the PM checks only eligible work Markdown inside the target
`.engineering/`.

## Verification

- Service and any manifest package pass typecheck/lint/tests; every operation is
  declared, registered, implemented, and covered by required tests.
- Canonical review detail and `review.md` agree with no hidden blocker.
- Contract refs, acceptance evidence, and departures are traceable.
- No worker wrote PM-owned files; reconciliation and `generated_files` are
  complete.

## Completion

Report work/spec receipt, mode, package/manifest paths, operations,
integrations/webhooks, gates, review, commit/handover, departures, PM
reconciliation, and `generated_files`.
