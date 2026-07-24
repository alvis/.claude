# Action: update

Loaded by `SKILL.md` when the first argument is `update`. Revise one or more
existing skills; the shared policy, thought-experiment/blindspot test,
verification commands, and completion contract live in `SKILL.md`.

Recommended tools for this action: `Bash, Task, Read, Glob, Edit, MultiEdit,
TodoWrite`.

## Boundaries

- Update existing skill behavior and documentation; use the `create` action
  when no suitable owner exists.
- Preserve established public behavior unless the requested change explicitly
  removes or reassigns it.
- Do not modernize unrelated skills merely because they are nearby.

The current skill and its real callers are authoritative; the template is a
concise aid, not a migration target whose headings must be copied.

## Inputs

- **Required**: a path, plugin-qualified skill name, glob, or explicit `--all`.
- **Optional**: requested behavior, trigger, wording, or policy changes.
- Never interpret an empty selector as permission to update every skill.

## Workflow

1. Resolve the selector and list exact targets. Reject ambiguity before edits.
2. Read each target completely, including directly referenced files and real
   cross-skill invocations.
3. Define current ownership and the requested end state. Run the shared
   thought-experiment and blindspot test (see `SKILL.md`) over positive and
   near-miss cases for changed triggers or behavior.
4. Capture a failing baseline for testable behavior when a deterministic check
   exists, then rewrite the existing document coherently. Remove superseded
   instructions and stale references.
5. Keep the core workflow concise; move only genuinely conditional bulk to
   references. Do not add personas, diagrams, fixed phases, or delegation
   ceremony unless they materially clarify this particular skill.
6. Validate each affected plugin and run repository policy checks (see
   `SKILL.md`).
7. Re-run the thought experiment and blindspot test for relevant functional and
   trigger behavior. Fix identified blindspots without widening the requested
   scope. Do not claim runtime behavior was exercised unless an executable
   evaluation actually ran.

Independent targets may be delegated in bounded batches — at most 8 skills per
batch and 8 parallel `Task` calls per dispatch. Each assignment must name exact
paths and constraints; review the combined diff afterward.

Use the `verify` action for functional and trigger evaluation with `fix: true`;
in bulk updates bound the loop to 2 fix iterations per skill, record remaining
issues, and continue to the next target.

## Completion

Report updated skills, ownership changes, validation results, thought-experiment
and blindspot coverage, runtime evaluation status (including "not exercised"),
and unresolved ambiguity. Confirm temporary Markdown thought-experiment notes
were deleted before commit. Never claim a bulk update without listing its
targets.
