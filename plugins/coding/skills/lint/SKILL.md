---
name: lint
description: Use when source files need mechanical coding-standard enforcement, lint-error correction, or consistent formatting across a selected scope.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep, Skill, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: "[specifier] [--scope=SCOPE] [--profile=ABSOLUTE_PATH]"
---

# Linting

Apply generic coding standards mechanically. This skill owns file discovery, scope handling, batching, the generic scanner, verification, aggregation, and the final report. It does not select or dispatch framework skills.

## Inputs

- `specifier`: optional file, directory, or glob. Default: repository root.
- `--scope`: `uncommitted` (default), `all`, or a focused section hint.
- `--profile=<absolute-path>`: internal extension contract for another plugin. Reject relative or unreadable paths.

The caller forwards its original arguments unchanged and may append one profile. Direct calls without a profile apply generic checks to every eligible source file, regardless of framework.

## Profile contract

Read the profile before discovery. A profile may narrow eligible files, add standards, add scanners, define exclusions, and supply a report label. It cannot replace generic standards, the generic scanner, verification, status semantics, or report shape.

Profile headings are declarative:

- `Eligibility`: included extensions and conditional file kinds.
- `Standards`: additional standard directories or names.
- `Scanners`: additional commands, run after the generic scanner.
- `Exclusions`: paths or file kinds removed from the candidate set.
- `Report label`: label shown in the unchanged report shape.

Fail before editing if the profile is invalid, references a missing standard/scanner, or attempts to redefine orchestration or reporting.

## Workflow

1. Parse `specifier`, `--scope`, and the optional profile independently of argument order.
2. Resolve candidate files:
   - `uncommitted`: union unstaged, staged, and untracked files, then apply the specifier.
   - `all` or a custom scope: resolve the specifier directly.
   - Always exclude ignored files, dependencies, generated output, and paths outside the repository.
3. Apply profile eligibility and exclusions when supplied. Stop cleanly if no files remain.
4. Discover generic coding standards from active plugin context. Add profile standards without replacing or duplicating generic standards.
5. Batch related files, with at most two files per batch.
6. For each batch, delegate mechanical linting to a suitable available subagent that cannot delegate further:
   - Run `plugins/coding/scripts/pyrun.sh plugins/coding/scripts/scan_potential_violations.py <files> --category all --before 5 --after 10` exactly once.
   - Run each profile scanner exactly once, in declared order.
   - Treat scanner output as advisory; confirm candidates against the matching rule before editing.
   - Apply generic and profile standards only within the requested scope.
   - Run project lint, type, and focused test commands after edits.
   - Return `violations_found`, `status`, files changed, checks run, and remaining issues.
7. Independently review batches that changed files. Already-compliant batches need no review.
8. Aggregate batch counts and use the worst status: `failure > partial > success > compliant`.

## Verification

- Every target was eligible and inside the repository.
- The generic scanner ran once per batch; every profile scanner ran once per batch.
- Every edit is justified by a loaded rule or project tool failure.
- Relevant project checks pass, or their exact failure is reported.
- All delegated work is complete and temporary teams are shut down.

## Report

Begin with these keys:

```yaml
violations_found_total: 0
status: compliant # compliant | success | partial | failure
```

Then report the command, profile report label when present, scope, files scanned and modified, standards and scanners applied, verification commands, review coverage, and remaining issues. Use `compliant` only for a clean pass with no edits and `success` when violations were fixed. A caller using a profile receives this same report shape.
