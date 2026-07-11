---
name: update-skill
description: "Use when revising one or more existing Claude Code skills, aligning skill instructions with current repository policy, narrowing overlapping ownership, or applying a deliberate behavior change without creating a competing skill."
model: opus
context: fork
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite
argument-hint: "[skill specifier] [--changes=...]"
---

# Update Skill

## Boundaries

- Update existing skill behavior and documentation; use `create-skill` when no
  suitable owner exists.
- Preserve established public behavior unless the requested change explicitly
  removes or reassigns it.
- Do not modernize unrelated skills merely because they are nearby.

Follow `${CLAUDE_SKILL_DIR}/../../constitution/references/authoring-invariants.md`.
The current skill and its real callers are authoritative; the template is a
concise aid, not a migration target whose headings must be copied.

## Inputs

- Required: a path, plugin-qualified skill name, glob, or explicit `--all`.
- Optional: requested behavior, trigger, wording, or policy changes.
- Never interpret an empty selector as permission to update every skill.

## Workflow

1. Resolve the selector and list exact targets. Reject ambiguity before edits.
2. Read each target completely, including directly referenced files and real
   cross-skill invocations.
3. Define current ownership and the requested end state. Record positive and
   near-miss evaluation cases for changed triggers or behavior.
4. Capture a failing baseline for testable behavior, then rewrite the existing
   document coherently. Remove superseded instructions and stale references.
5. Keep the core workflow concise; move only genuinely conditional bulk to
   references. Do not add personas, diagrams, fixed phases, or delegation
   ceremony unless they materially clarify this particular skill.
6. Validate each affected plugin and run repository policy checks.
7. Run relevant functional and trigger evaluations. Fix regressions without
   widening the requested scope.

Independent targets may be delegated in bounded batches — at most 8 skills per
batch and 8 parallel `Task` calls per dispatch. Each assignment must name exact
paths and constraints; review the combined diff afterward.

## Verification

```bash
claude plugin validate --strict <plugin-path>
python3 "${CLAUDE_SKILL_DIR}/../verify-skill/scripts/quick_validate.py" <target>
```

Use `governance:verify-skill` for functional and trigger evaluation with
`fix: true`; in bulk updates bound the loop to 2 fix iterations per skill,
record remaining issues, and continue to the next target.

## Completion

Report updated skills, ownership changes, validation and evaluation results,
and unresolved ambiguity. Never claim a bulk update without listing its targets.
