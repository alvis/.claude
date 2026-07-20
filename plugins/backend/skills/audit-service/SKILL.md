---
name: audit-service
description: Audit a backend service against its work-local authoritative specification and canonical review areas, with optional approved remediation. Use for implementation, operation completeness, documentation, semantic, security, testing, and quality audits.
model: opus
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<service-name> --work-id=<id> [--scope=implementation|docs|all] [--operation=...] [--area=...] [--auto-fix]"
---

# Audit Service

Audit a service against its active work specification and implementation/docs,
then route findings to the canonical review taxonomy. Approved fixes remain
with Backend/Coding owners.

## Boundaries

- Implementation scope checks manifests, handlers, declarations, tests, and
  runtime contract; docs scope checks service/operation documentation. `all`
  composes both.
- Route contract omissions/drift to `alignment.md`; semantic defects to
  `correctness.md`; remaining findings to security, quality, testing, docs, or
  style. One finding has one owner.
- Do not create standalone/root audit or deviations artifacts. Summarize under
  `.engineering/work/<work-id>/review.md` and keep detail in `reviews/*.md`.
- Do not mutate code, docs, MDC, or Notion merely because a discrepancy exists.

## Inputs

- **Required**: service/package and `--work-id=<id>`.
- **Optional**: scope, operation/area filters, and auto-fix for eligible
  explicitly accepted remediation.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve the work root;
   read `working.md`, then `state.md`, then referenced spec/review paths.
2. Materialize a missing/stale Notion source through
   `specification:sync-spec`. Use its receipt and frontmatter refs, not a local
   independent specification export or filename convention. Refuse
   unidentified sources.
3. Apply filters before checks. Inspect implementation evidence and delegate
   generic semantic/security review to `coding:review-code`, mechanical checks
   to lint, and unused-code discovery as needed.
4. For docs scope, map declared operations to versioned documentation and
   authoritative work-spec refs. Detect missing, duplicate, orphaned, stale, or
   ambiguous pages and compare overview, signatures, inputs/outputs, errors,
   examples, ownership, status, and links.
5. Run independent blind checks in bounded parallel batches. Adversarially
   validate and deduplicate candidates, route survivors to one canonical review
   file, and preserve stable IDs across reruns.
6. Write/update `review.md` with only area verdicts, counts, dispositions, and
   relative paths. Track `open`, `fixed`, `acknowledged`, `deferred`, or
   `skipped` decisions with rationale, owner, and recheck condition.
7. Route approved implementation fixes to `backend:build-service` or
   `coding:fix`. Route durable documentation fixes to their owning documentation
   skill. A specification change uses `specification:mdc`, then verified
   `specification:sync-spec` completion. Re-run affected checks and record
   before/after evidence.
8. For remediation tracking, create a lowercase work-local change child and
   return PM reconciliation for `changes.md`/`state.md`; workers do not edit
   those PM-owned files.
9. Return explicit final paths generated or materially rewritten as
   `generated_files`. Do not run `wc -c`; the PM owns the final batch pass.

## Verification

- Canonical review details and `review.md` agree; every finding has evidence,
  severity, disposition, and next action.
- Correctness and security evidence exist even when alignment fails.
- Fixed pages/code have content-level re-verification; exit code alone is not
  success. Contract changes have verified sync/derivation receipts.
- PM reconciliation and `generated_files` are complete.

## Completion

Return status, service/work/spec receipt, scope/filters, per-area verdicts and
dispositions, documentation page-map counts, remediation/sync verification,
PM reconciliation, and `generated_files`.
