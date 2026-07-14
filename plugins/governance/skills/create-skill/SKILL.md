---
name: create-skill
description: "Use when creating a reusable Claude Code skill, defining a new repeatable agent capability, or replacing a one-off workflow with discoverable instructions that need clear ownership, validation, and trigger behavior."
model: opus
context: fork
---

# Create Skill

## Boundaries

- Create a skill only for reusable judgment or workflow guidance.
- Do not encode one-off project facts as a skill; use project documentation.
- Search existing skills first. Update an existing owner when the capability
  overlaps instead of creating a competing trigger.

Follow `${CLAUDE_SKILL_DIR}/../../constitution/references/authoring-invariants.md`.
Start from `${CLAUDE_SKILL_DIR}/../../constitution/templates/skill.md`, adapting
headings to the capability.

## Inputs

- Required: skill purpose, target plugin, and concrete trigger examples.
- Optional: allowed tools, execution context, references, and output contract.

## Workflow

1. Inspect neighboring skills, plugin conventions, and call sites.
2. Define the new skill's owned outcome, positive triggers, near-miss prompts,
   exclusions, inputs, failure behavior, and verification.
3. Before writing the skill, conduct a paper-only thought experiment and
   blindspot test for trigger or behavior changes. If written notes are useful,
   keep them temporary as a Markdown scratch document in an OS temp
   folder (for example `${TMPDIR:-/tmp}/check.md`) using
   `${CLAUDE_SKILL_DIR}/../../constitution/references/check.md` as the
   example table format with `:white_check_mark:`/`:x:` status markers.
   Delete the scratch document before staging; these notes are reasoning aids,
   not deliverables, and must not be committed.
4. Create the smallest `skills/<name>/SKILL.md` that teaches the missing
   behavior. Keep always-used instructions inline and conditional bulk in
   references.
5. Add supporting scripts only for deterministic operations that prose should
   not reproduce. Test scripts before documenting them.
6. Run structural and policy validation, then re-run the thought experiment and
   blindspot test against positive and near-miss prompts. Revise until the
   intended trigger boundary is explicit and neighboring work remains excluded.
   Do not claim runtime trigger behavior was exercised unless an executable
   evaluation actually ran.

## Verification

```bash
claude plugin validate --strict <plugin-path>
python3 "${CLAUDE_SKILL_DIR}/../verify-skill/scripts/quick_validate.py" <skill-or-plugin-path>
```

Use `governance:verify-skill` when functional or trigger evaluation is needed,
with `fix: true`; loop fix and re-verify at most 3 times, then report partial
completion with the remaining issues.

## Completion

Report the created path, ownership boundary, thought-experiment and blindspot
coverage, validation results, runtime evaluation status (including "not
exercised"), and any intentionally deferred cases. Confirm any temporary
Markdown thought-experiment notes were deleted before commit.
