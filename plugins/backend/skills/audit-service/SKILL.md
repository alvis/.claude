---
name: audit-service
description: "Audit a backend service against its implementation and documentation contract, producing evidence-backed findings and optionally remediating approved gaps. Use for operation completeness, service quality, or documentation-only audits; choose --scope to keep the review focused."
model: opus
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<service-name> [--scope=implementation|docs|all] [--operation=...] [--area=...] [--auto-fix]"
---

# Audit Service

Owns read-only auditing of a backend service against its current
specification and local implementation, plus approved remediation of the
gaps it finds. Every finding includes a source location, expected contract,
observed behavior, severity, and a proposed next action.

## Boundaries

- Use for: implementation audits (`--scope=implementation` owns
  code/manifest/operation completeness — declared operations, manifests,
  handlers, tests, code quality), documentation audits (`--scope=docs` is
  the single owner of documentation-only audits — service and operation
  documentation against the specification), or both (`--scope=all`, the
  default, is a composition of those two scopes, not a third review
  protocol).
- Do not use for: creating a service (`backend:build-service`), building a
  data layer (`backend:build-data`), implementing an unapproved feature
  (`coding:write-code`), or generic code review (`coding:review-code` owns
  broad semantic/security review; this skill supplies service contract
  context).
- `specification:sync-notion` owns Notion pull/push/merge mechanics; this
  skill only delegates to it.
- Findings without concrete evidence are incomplete and must not be reported
  as verified.

## Inputs

- **Required**: service name or package path.
- **Optional**: `--scope=implementation|docs|all` (default `all`);
  `--operation=<name>` limits findings to one or more operations;
  `--area=<name>` narrows the selected scope to a documented functional
  area; `--auto-fix` may apply only explicitly approved remediation and
  never changes the specification implicitly.
- **Prerequisites**: the specification is reachable — load it through
  `specification:sync-notion` when a Notion source is supplied, or use the
  local DESIGN/spec bundle when one is already present.

## Workflow

1. Resolve the service and specification. Refuse with `status: refused`
   when either cannot be identified; do not invent requirements.
2. Apply `--scope`, `--operation`, and `--area` before dispatching checks.
3. For `implementation`, inspect manifests, declarations, operation
   handlers, tests, and diagnostics. Delegate generic semantic review to
   `coding:review-code`, mechanical checks to `coding:lint`, and dead-code
   discovery to `coding:find-unused` as needed.
4. For `docs`, discover the documentation set before comparing it: resolve
   the service page from its spec ref/database entry, enumerate declared
   operations, follow child/linked operation pages in one recursive pull,
   and map each expected operation to exactly one page. Record missing,
   duplicate, orphaned, or ambiguously named pages. Then compare overview,
   operation names, signatures, inputs/outputs, errors, examples, status,
   ownership, and cross-links against the specification and implementation
   evidence. Documentation findings remain in this report; do not route
   them to a deleted skill.
5. Run independent checks in parallel where their inputs do not overlap, at
   most 2 operation audits at a time (per the bounds in
   plugins/governance/constitution/references/delegation.md). Keep each
   check read-only and record its evidence.
   <IMPORTANT>
   Dispatch each auditing subagent blind: the prompt contains ONLY the spec
   path, implementation path(s), output template, and applicable standards
   paths — never the parent narrative, intent, or expected conclusions —
   and instructs the auditor to treat the implementation as unfamiliar
   rather than assuming it matches the spec.
   </IMPORTANT>
6. Consolidate duplicate findings, classify severity, and write `AUDIT.md`
   beside the service (or at the requested output path) with: the selected
   scope and filters; contract and implementation/documentation sources;
   findings grouped by severity and operation; evidence with file/line or
   Notion references; remediation decisions and verification status.
7. Present the report and collect an explicit **accept** (will fix),
   **reject** (won't fix), or **defer** (later) decision per finding;
   `--auto-fix` auto-accepts all findings. Approved implementation fixes
   route to `backend:build-service` or `coding:fix`. For approved
   documentation remediation, edit the paired local Markdown, preserve page
   identity/frontmatter, show `notion-sync diff`, and delegate the push to
   `specification:sync-notion local-to-notion`; create a missing page only
   with an explicit parent. Never mutate Notion or code merely because a
   discrepancy exists.
8. Re-pull or diff every remediated page, re-run the affected
   implementation checks, and record before/after evidence. Then run the
   verification below; when a check fails, fix the cause and re-run that
   check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- `AUDIT.md` exists and every finding carries file/line or Notion evidence
  with severity and a proposed next action.
- Every remediated page is re-pulled or diffed and every affected
  implementation check re-run, with before/after evidence recorded. A
  command exit without content/metadata verification is not remediation
  success.

## Completion

Return a structured summary naming the status (success, partial, failure, or
refused), service, scope, operations audited, finding count, remediated
count, and the report path (`AUDIT.md`). For documentation scope also
include `pages_expected`, `pages_found`, `missing_pages`,
`duplicate_pages`, `orphan_pages`, `operation_page_map`, `sync_actions`,
and `post_sync_verification`.
