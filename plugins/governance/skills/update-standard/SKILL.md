---
name: update-standard
description: Update explicitly selected plugin standards to the current meta.md, scan.md, write.md, and rules contract while preserving valid policy and stable rule IDs. Use for scoped rule changes or bounded template migration. Require a path, glob, or --all; route missing targets to create-standard.
model: opus
context: fork
allowed-tools: Bash, Task, Read, Glob, Grep, Edit, Write
argument-hint: "<standard path, name, or glob> [--changes=...] [--all]"
---

# Update standard

Update directories only under `plugins/<plugin>/constitution/standards/<standard-name>/`. Resolve an exact selector; `--all` is required for a library-wide migration. Do not create missing standards or modify governance templates.

## Grounding and snapshot

Read `${CLAUDE_SKILL_DIR}/../../constitution/templates/standard-meta.md`, `standard-scan.md`, and `standard-write.md`; then read each selected standard's complete `meta.md`, `scan.md`, `write.md`, `rules/`, dependent standards, and inbound local links. List exact targets and snapshot existing IDs, prefixes, dependencies, exceptions, detection criteria, compliant guidance, examples, and external references.

Reject an empty/ambiguous selector, missing tier, malformed request, duplicate target, or unapproved rule-ID renumbering. Rule IDs are public anchors: preserve them unless the request explicitly authorizes migration and all inbound references are updated.

## Update procedure

1. Map each requested change across all affected tiers before editing: rationale/dependency in meta, violation detection in scan, compliant behavior in write, detailed guide and links in rules.
2. Reconcile structure with the exact templates without replacing valid content with placeholders. Fold new policy into existing sections and remove superseded contradictions; do not append changelogs.
3. Keep meta concise and authoritative for dependencies, stricter requirements, exception policy, and groups. Keep scan violation-oriented and write compliance-oriented.
4. Update every affected `rules/<lowercase-rule-id>.md` and every inbound/outbound local link. Preserve unrelated rule examples and IDs.
5. For multiple independent targets, bounded delegation is allowed, but review the combined ID/dependency/link graph before validation.

## Cross-tier verification

For every selected standard, compare the declared meta groups and IDs with scan bullets/matrix, write summaries, rule filenames, and repository references. Fail on missing/extra/duplicate IDs, prefix drift, contradictory scan/write wording, unresolved links, missing dependencies, invalid exception fields, orphan guides, or unapproved breaking renames.

Run `claude plugin validate --strict plugins/<plugin>` and governance policy checks. Exercise representative violating and compliant examples for changed groups. For `--all`, report every target and per-target result; one failed target makes the migration partial.

Return selector, targets, templates used, preserved/added/deprecated IDs, cross-tier and link results, validation/evaluation evidence, and unresolved issues.
