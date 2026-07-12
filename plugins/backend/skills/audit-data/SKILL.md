---
name: audit-data
description: "Audit data orchestrators against specifications, generate discrepancy reports, and remediate approved changes. Use when reviewing data domain completeness, checking schema compliance, or performing data layer quality audits."
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<domain-name> [--operation=...] [--entity=...] [--auto-fix]"
---

# Audit Data

Owns read-only auditing of a `@theriety/data-{domain}` orchestrator against
its Notion specification — schema completeness, operation coverage,
controller alignment, and code quality — plus approved remediation through
`backend:build-data`. `backend:audit-service` owns service audits.

## Boundaries

- Use for: reviewing data domain completeness after spec updates; validating
  Prisma schema alignment with Notion entity definitions; checking operation
  coverage for declared entities; verifying controller methods match
  implemented operations; quality assurance before release.
- Do not use for: building new data orchestrators (`backend:build-data`),
  auditing services (`backend:audit-service`), or modifying Notion
  specifications without user approval.
- The audit is read-only until the user approves remediation; every finding
  carries specific file, line, or model evidence.

## Inputs

- **Required**: domain name (maps to `@theriety/data-{domain}`).
- **Optional**: `--operation=<name>` and `--entity=<name>` to focus the
  audit; `--auto-fix` to auto-accept every finding.
- **Prerequisites**: the data orchestrator package exists; the specification
  is reachable in the Notion Data Controllers database (or a local DESIGN.md
  export).

## Workflow

1. **Load the spec.** Run `specification:sync-notion` in pull mode: search
   for the Data Controllers database, locate the controller page for the
   domain, and extract entity definitions with attributes, operation
   specifications, and relationship definitions.
2. **Plan the audit.** List all entities and operations from the spec; read
   the local Prisma schema, operations directory, and controller class;
   apply the `--operation`/`--entity` filters; define three audit streams —
   schema, operations, controller.
3. **Dispatch the audit streams.** Run three parallel read-only audit
   subagents with the blind-dispatch prompts in
   [references/audit-streams.md](references/audit-streams.md), and execute
   `coding:review-code`, `coding:lint`, and `coding:find-unused` alongside
   them. Reports stay under 1000 tokens each, per the bounds in
   plugins/governance/constitution/references/delegation.md.
   <IMPORTANT>
   Dispatch each auditor blind: the prompt contains ONLY the spec path,
   implementation path(s), output template path, and applicable standards
   paths — never the parent narrative, intent, or expected conclusions — and
   instructs the auditor to treat the implementation as unfamiliar and to
   modify nothing.
   </IMPORTANT>
4. **Generate AUDIT.md.** Consolidate the three stream reports and the
   quality results into `AUDIT.md` using the structure in
   [references/audit-streams.md](references/audit-streams.md): summary
   counts, findings tables (schema, operation, controller) with severity and
   recommendation, code-quality summary, and a decisions checklist.
5. **Decision gate.** Present AUDIT.md to the user and collect an explicit
   accept (will fix), reject (won't fix), or defer (fix later) decision per
   finding; `--auto-fix` auto-accepts all findings.
6. **Sync decisions to Notion.** Run `specification:sync-notion` in push
   mode to record the decisions on the controller page.
7. **Remediate.** Skip when no finding was accepted. Compile the accepted
   schema changes, missing operations, and controller fixes into a domain
   extension spec and run `backend:build-data` in extend mode with it.
8. Re-run the audit checks affected by remediation, then the verification
   below; when a check fails, fix the cause and re-run that check. Repeat
   until every check passes or a concrete blocker remains, then report the
   blocker instead of looping.

## Verification

- `AUDIT.md` exists and every finding carries file, line, or model evidence
  with severity and recommendation.
- Every accepted finding is remediated and its originating audit check
  passes on re-run.
- Notion reflects the recorded decisions after the push sync.

## Completion

Report the domain, entities and operations audited, findings total and per
decision (accepted, rejected, deferred), schema/operation/controller
compliance per item, remediation status (completed, partial, or skipped),
and whether Notion was synced. Point to `AUDIT.md` as the evidence record.
