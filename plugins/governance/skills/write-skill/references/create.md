# Action: create

Loaded by `SKILL.md` when the first argument is `create`. Add a new reusable
skill; the shared policy, thought-experiment/blindspot test, verification
commands, and completion contract live in `SKILL.md`.

## Boundaries

- Create a skill only for reusable judgment or workflow guidance.
- Do not encode one-off project facts as a skill; use project documentation.
- Search existing skills first. Update an existing owner (the `update` action)
  when the capability overlaps instead of creating a competing trigger.

Start from `${CLAUDE_SKILL_DIR}/../../constitution/templates/skill.md`, adapting
headings to the capability.

## Inputs

- **Required**: skill purpose, target plugin, and concrete trigger examples.
- **Optional**: allowed tools, execution context, references, and output
  contract.

## Workflow

1. Inspect neighboring skills, plugin conventions, and call sites.
2. Define the new skill's owned outcome, positive triggers, near-miss prompts,
   exclusions, inputs, failure behavior, and verification.
3. Before writing the skill, run the shared thought-experiment and blindspot
   test (see `SKILL.md`) for the intended triggers and behavior.
4. Create the smallest `skills/<name>/SKILL.md` that teaches the missing
   behavior. Keep always-used instructions inline and conditional bulk in
   references.
5. Add supporting scripts only for deterministic operations that prose should
   not reproduce. Test scripts before documenting them.
6. Run structural and policy validation (see `SKILL.md`), then re-run the
   thought experiment and blindspot test against positive and near-miss
   prompts. Revise until the intended trigger boundary is explicit and
   neighboring work remains excluded. Do not claim runtime trigger behavior was
   exercised unless an executable evaluation actually ran.

Use the `verify` action when functional or trigger evaluation is needed, with
`fix: true`; loop fix and re-verify at most 3 times, then report partial
completion with the remaining issues.

## Completion

Report the created path, ownership boundary, thought-experiment and blindspot
coverage, validation results, runtime evaluation status (including "not
exercised"), and any intentionally deferred cases. Confirm any temporary
Markdown thought-experiment notes were deleted before commit.
