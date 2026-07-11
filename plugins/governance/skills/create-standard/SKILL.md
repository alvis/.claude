---
name: create-standard
description: Create a new technical standard at a plugin's canonical constitution/standards root using meta.md, scan.md, write.md, and per-rule guides. Use when reusable policy is missing and needs explicit dependencies, detection, compliant patterns, and stable rule IDs. Route existing-standard revisions to update-standard.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
argument-hint: "<plugin>/<standard-name> [--detail=...]"
---

# Create standard

Create exactly one new directory at `plugins/<plugin>/constitution/standards/<standard-name>/`. The name is lowercase kebab-case; the rule prefix is a unique short uppercase mnemonic. Never write to a repository-level shorthand root or overwrite an existing standard.

## Required templates and discovery

Resolve these installed governance templates from `${CLAUDE_SKILL_DIR}/../../constitution/templates/`:

- `standard-meta.md` → `<target>/meta.md`
- `standard-scan.md` → `<target>/scan.md`
- `standard-write.md` → `<target>/write.md`

Read all three templates, the target plugin's constitution references, and neighboring standards before writing. Search every standard under `plugins/*/constitution/standards/` for the proposed prefix and rule IDs. Reject a duplicate target, duplicate prefix/ID, unknown plugin, missing templates, or policy that belongs to an existing owner.

## Authoring procedure

1. Define scope, non-goals, dependent standards, stricter requirements, exception policy, rule groups, and stable IDs before drafting examples.
2. Create the target and `rules/`. Populate `meta.md` from the meta template: dependencies use `standard:<name>` within the plugin or `plugin:<plugin>:standard:<name>` across plugins; every declared group matches the chosen prefix.
3. Populate `scan.md` from the scan template. Every quick-scan item and matrix row names one declared rule ID and describes a mechanically or reviewably detectable violation.
4. Populate `write.md` from the write template. Every rule ID has actionable compliant guidance; patterns and decisions do not contradict scan criteria.
5. Create `rules/<lowercase-rule-id>.md` for every rule that requires detail. Link it from the tiers using relative links and ensure no guide introduces an undeclared ID.
6. Remove all template placeholders and instructions. Keep examples only when they disambiguate detection or compliance.

## Cross-tier verification

Build sets of IDs from meta groups, scan bullets/matrix, write summaries, and rule filenames. Fail when an ID is undeclared, missing from scan or write, duplicated, uses another prefix, or links to a missing guide. Resolve every local Markdown link from its containing file. Verify dependent-standard targets exist and no dependency cycle is introduced.

Run `claude plugin validate --strict plugins/<plugin>` plus governance repository policy checks. Exercise at least one violating and one compliant example per rule group against scan/write guidance. Return target, source templates, prefix, complete rule-ID list, dependency/link checks, validation commands/results, and unresolved policy questions.
