---
name: create-standard
description: Create a new technical standard under a plugin constitution with meta.md, scan.md, write.md, and rules/. Use when a reusable policy is missing and needs explicit scope, detection guidance, implementation guidance, and actionable rules. Do not use for revising an existing standard or creating a skill.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Task
argument-hint: "<plugin>/<standard-name> [--detail=...]"
---

# Create standard

Create one new three-tier standard directory. `update-standard` owns existing standards; `create-skill` owns reusable workflow capabilities.

## Inputs and validation

- Required lowercase, hyphenated standard name and target plugin.
- Optional detail, examples, related standards, and rule identifiers.
- Target directory must exist and must not already contain the standard.
- Read the standard templates and neighboring standards before authoring.

Reject an unclear name, duplicate directory, invalid target, or request for non-standard files.

## Workflow

1. Define the owned outcome, non-goals, related standards, severity model, and rule IDs.
2. Create `meta.md`, `scan.md`, `write.md`, and `rules/` from the current templates. Keep meta (why), scan (how to detect), and write (how to comply) consistent; include only examples that clarify a rule.
3. Delegate authoring when the standard is substantial; provide exact paths and require the smallest coherent documents without personas, diagrams, or fixed phases.
4. Review for contradictions, duplicate rule IDs, unresolved local links, and actionable scan/write guidance. Run strict Claude validation and repository policy checks.

## Completion

Report the standard path, tier files, rule IDs, related standards, validation commands, and any deferred rule. Do not overwrite an existing standard without an explicit update request.
