# Action: create

Loaded by `SKILL.md` when the requested action is `create`. Add a new reusable
skill; the shared policy, thought-experiment/blindspot test, and verification
commands live in `SKILL.md`.

## Boundaries

- Create a skill only for reusable judgment or workflow guidance.
- Do not encode one-off project facts as a skill; use project documentation.
- Search existing skills first. Update an existing owner (the `update` action)
  when the capability overlaps instead of creating a competing trigger.

Use the strict shared structure in `references/authoring.md`. When a harness
difference affects the result, follow `references/harnesses.md`.

## Inputs

- **Required**: skill purpose, name, and concrete trigger examples.
- **Optional**: supporting references, scripts, assets, and output contract.

## Workflow

1. Inspect neighboring skills and call sites.
2. Define the new skill's owned outcome, positive triggers, near-miss prompts,
   exclusions, inputs, failure behavior, and verification.
3. Before writing the skill, run the shared thought-experiment and blindspot
   test (see `SKILL.md`) for the intended triggers and behavior.
4. Create the smallest self-contained `<name>/SKILL.md` that teaches the
   missing behavior. Keep always-used instructions inline and conditional bulk
   in root-relative supporting resources.
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
coverage, validation results, runtime evaluation status (`exercised`, `not
requested`, or `blocked`), and any intentionally deferred cases.
