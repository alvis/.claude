---
name: audit-data
description: Audit a data orchestrator against its work-local authoritative specification and the canonical review taxonomy, then remediate explicitly approved gaps. Use for schema, operation, controller, testing, and data-layer quality review; keep service audits in audit-service.
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<domain-name> --work-id=<id> [--operation=...] [--entity=...] [--auto-fix]"
---

# Audit Data

Audit `@theriety/data-{domain}` against the active work specification and write
evidence to canonical work-local review areas. Approved remediation routes to
`backend:build-data`.

## Boundaries

- Audit is read-only until remediation is explicitly approved.
- Specification mismatch/completeness belongs in `reviews/alignment.md`;
  independently wrong behavior in `correctness.md`; other findings route to
  `security.md`, `quality.md`, `testing.md`, `docs.md`, or `style.md`.
- Do not create a standalone aggregate audit/departures report. `review.md` is the
  concise roll-up; plan departures live in work state and change children.
- Do not mutate Notion directly. Materialization/completion route through
  Specification skills.

## Inputs

- **Required**: domain name and `--work-id=<id>`.
- **Optional**: operation/entity filters; `--auto-fix` accepts remediation but
  does not waive decisions that change contract, data, security, or behavior.
- **Prerequisites**: existing data package and a materializable authoritative
  specification.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve the work root;
   read `working.md`, then `state.md`, then only referenced spec/review paths.
2. Invoke `specification:sync-spec` in materialize mode when the receipt is
   absent or stale. Identify entities/operations by receipt/frontmatter refs,
   never filenames. Refuse rather than infer missing requirements.
3. Read Prisma schema, operations, controller, tests, and filters. Dispatch the
   blind schema/operation/controller streams in
   [references/audit-streams.md](references/audit-streams.md), plus Coding
   semantic/security review, lint, and unused-code discovery as applicable.
4. Adversarially check and deduplicate candidates, then route each survivor to
   exactly one canonical review file. Preserve stable finding IDs on rerun.
   Generate/update `review.md` with per-area verdict/count/disposition/path,
   never copied finding detail.
5. Track `open`, `fixed`, `acknowledged`, `deferred`, or `skipped` disposition
   per finding with rationale, owner, and recheck condition. Auto-fix marks
   eligible findings for fixing; it never silently acknowledges contract risk.
6. For accepted remediation, write a lowercase work-local
   `changes/<slug>.md` child, return PM reconciliation for `changes.md` and
   `state.md`, and invoke `backend:build-data --extend` with exact spec/finding
   pointers. Re-run affected detection and update dispositions.
7. When resolution changes the authoritative specification, route authored MDC
   through `specification:mdc` and verified completion through
   `specification:sync-spec`; otherwise do not push review decisions to Notion.
8. Return explicit final paths generated or materially rewritten as
`generated_files`. Do not run file sizing; after all writers finish, the PM
checks only eligible work Markdown inside the target `.engineering/`.

## Verification

- All findings have evidence, stable identity, one canonical area, severity,
  disposition, and next action; review summary counts match details.
- Every fixed finding passes rerun; non-fixed findings retain owner/rationale/
  recheck state.
- Contract changes complete the verified Notion/derivation round trip.
- No worker edited PM-owned overview/state/working files; PM reconciliation and
  `generated_files` are complete.

## Completion

Report domain, work/spec receipt, scope, per-area verdicts/counts/dispositions,
remediation and contract-sync outcomes, PM reconciliation, and
`generated_files`.
