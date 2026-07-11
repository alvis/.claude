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
3. Write failing trigger or behavior evaluations before the skill when the
   change is testable; capture the baseline failure.
4. Create the smallest `skills/<name>/SKILL.md` that teaches the missing
   behavior. Keep always-used instructions inline and conditional bulk in
   references.
5. Add supporting scripts only for deterministic operations that prose should
   not reproduce. Test scripts before documenting them.
6. Run structural and policy validation, then exercise positive and near-miss
   evaluations. Revise until the intended skill triggers and neighbors do not.

## Verification

```bash
claude plugin validate --strict <plugin-path>
python3 "${CLAUDE_SKILL_DIR}/../verify-skill/scripts/quick_validate.py" <skill-or-plugin-path>
```

Use `governance:verify-skill` when functional or trigger evaluation is needed.

## Completion

Report the created path, ownership boundary, evaluations, validation results,
and any intentionally deferred cases.
