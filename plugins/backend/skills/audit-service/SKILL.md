---
name: audit-service
description: "Audit a backend service against its implementation and documentation contract, producing evidence-backed findings and optionally remediating approved gaps. Use for operation completeness, service quality, or documentation-only audits; choose --scope to keep the review focused."
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<service-name> [--scope=implementation|docs|all] [--operation=...] [--area=...] [--auto-fix]"
---

# Audit Service

Audit a service against its current specification and local implementation. The audit is read-only until the user approves remediation. Every finding includes a source location, expected contract, observed behavior, severity, and a proposed next action.

## Scope

`--scope=implementation` checks declared operations, manifests, handlers, tests, and code quality. `--scope=docs` checks the service and operation documentation against the specification; it is the single owner for documentation-only audits. `--scope=all` runs both scopes (the default).

`--operation=<name>` limits findings to one or more operations. `--area=<name>` narrows the selected scope to a documented functional area. `--auto-fix` may apply only explicitly approved remediation; it never changes the specification implicitly.

Do not use this skill to create a service (`build-service`), build a data layer (`build-data`), implement an unapproved feature (`coding:write-code`), or perform a generic code review (`coding:review-code`).

## Inputs and outputs

Required input is a service name or package path. Resolve the service locally, then load the authoritative specification through `specification:sync-notion` when a Notion source is supplied. Use the local DESIGN/spec bundle when one is already present.

Write `AUDIT.md` beside the service (or the requested output path) with:

- selected scope and filters;
- contract and implementation/documentation sources;
- findings grouped by severity and operation;
- evidence with file/line or Notion references;
- remediation decisions and verification status.

Return a structured summary:

```yaml
status: success|partial|failure
service: <name>
scope: implementation|docs|all
operations_audited: []
findings: 0
remediated: 0
report: AUDIT.md
```

## Workflow

1. Resolve the service and specification. Refuse with `status: refused` when either cannot be identified; do not invent requirements.
2. Apply `--scope`, `--operation`, and `--area` before dispatching checks.
3. For `implementation`, inspect manifests, declarations, operation handlers, tests, and diagnostics. Delegate generic semantic review to `coding:review-code`, mechanical checks to `coding:lint`, and dead-code discovery to `coding:find-unused` as needed.
4. For `docs`, compare service and operation pages with the specification: required pages, operation names, inputs/outputs, error behavior, examples, status, and links. Documentation findings remain in this report; do not route them to a deleted skill.
5. Run independent checks in parallel where their inputs do not overlap. Keep each check read-only and record its evidence.
6. Consolidate duplicate findings, classify severity, and write `AUDIT.md`.
7. Present the report and wait for decisions unless `--auto-fix` was explicitly supplied. Approved implementation fixes route to `build-service` or `coding:fix`; approved documentation edits use the owning documentation workflow. Never mutate Notion or code merely because a discrepancy exists.
8. Re-run the affected checks, record verification, and return the structured summary.

## Boundaries

- `implementation` owns code/manifest/operation completeness.
- `docs` owns service and operation documentation completeness.
- `all` is composition of those two scopes, not a third review protocol.
- `coding:review-code` owns broad semantic/security review; this skill supplies service contract context.
- `specification:sync-notion` owns Notion pull/push/merge mechanics; this skill only delegates to it.
- Findings without concrete evidence are incomplete and must not be reported as verified.
