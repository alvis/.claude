---
name: update-standard
description: Update explicitly selected technical standards to the current three-tier template or a stated policy change, preserving valid rules and examples while removing superseded wording. Use for standard maintenance or bounded bulk migration; use create-standard when the target directory does not exist.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Write
argument-hint: "<standard path, name, or glob> [--changes=...] [--all]"
---

# Update standard

Update only the selected standard directories. `--all` is required for an intentional library-wide migration.

## Inputs and boundaries

- Required standard path, name, glob, or explicit `--all`.
- Optional policy changes, rule additions, or template migration details.
- Read the three templates and every selected standard's `meta.md`, `scan.md`, `write.md`, and rules before editing.
- Preserve existing rule intent unless the request explicitly reassigns it. Do not modify templates or unrelated files.

Reject an empty/ambiguous selector, missing tiers, malformed changes, or a request to create a new standard.

## Workflow

1. Resolve and list exact targets. Compare each tier with the current templates and nearby standards; identify duplicate or conflicting rule IDs.
2. Rewrite selected tiers in place so rationale, detection, implementation, and rules stay coherent. Move conditional examples to references when they are not needed for every reader; do not append changelog sections.
3. Delegate independent batches when useful, passing exact paths and acceptance criteria. Review the combined diff for rule consistency and scope drift.
4. Run strict Claude validation, repository policy checks, unresolved-link checks, and representative trigger/scan examples. Correct only reported failures and repeat validation.

## Completion

Report selector, exact targets, changed tiers/rules, preserved content, validation evidence, and unresolved issues. Never claim a bulk migration without naming every target.
