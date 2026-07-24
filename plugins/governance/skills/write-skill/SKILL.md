---
name: write-skill
description: "Use when authoring, revising, or validating a Claude Code skill through its create, update, and verify actions: define a new reusable capability, align existing skills with repository policy, or check structural, trigger, and behavior compliance before deployment. Invoke as write-skill create, update, or verify."
model: opus
context: fork
argument-hint: "<create|update|verify> [target] [--changes=...] [--mode=...] [--runtime]"
---

# Write Skill

Author, revise, and validate Claude Code skills. One skill, three actions:
`create` a new skill, `update` one or more existing skills, or `verify` a
skill's structural, policy, and trigger compliance. The first argument selects
the action; route to its reference below and follow that workflow.

## Actions

- **`create`** — Add a new reusable skill that teaches a missing behavior with
  clear ownership and triggers. See
  [references/create.md](references/create.md).
- **`update`** — Revise existing skill behavior, wording, or triggers, or align
  skills with current policy, without creating a competing skill. See
  [references/update.md](references/update.md).
- **`verify`** — Validate structural, repository-policy, and (when behavior or
  discovery changed) trigger and behavior compliance, optionally exercising
  isolated runtime prompts. See [references/verify.md](references/verify.md).

If the action is missing or ambiguous, ask which action is intended rather than
guessing. `create` requires that no suitable owner exists; when one does,
switch to `update`. `create` and `update` call the `verify` action for
functional and trigger evaluation.

## Shared policy

Follow
`${CLAUDE_SKILL_DIR}/../../constitution/references/authoring-invariants.md` for
all three actions. Claude Code's validator remains authoritative for manifest
and frontmatter schema; repository policy checks never duplicate the evolving
Claude schema.

## Shared thought experiment and blindspot test

Whenever an action changes a trigger or behavior, conduct a paper-only thought
experiment and blindspot test over positive and near-miss prompts before and
after the change. If written notes help, keep them as a temporary Markdown
scratch document in an OS temp folder (for example `${TMPDIR:-/tmp}/check.md`)
using `${CLAUDE_SKILL_DIR}/../../constitution/references/check.md` as the table
format with `:white_check_mark:`/`:x:` status markers. Delete the scratch
document before staging; these notes are reasoning aids, not deliverables, and
must not be committed. Do not claim runtime trigger behavior was exercised
unless an executable evaluation actually ran.

## Verification

```bash
claude plugin validate --strict <plugin-path>
python3 "${CLAUDE_SKILL_DIR}/scripts/quick_validate.py" <skill-or-plugin-path>
```

Run both commands after every fix iteration. When a check fails, change only
the reported cause and re-run that check; loop fix and re-verify at most 3
times, then report partial completion with the remaining issues.

## Completion

Report the action taken, affected skill paths, ownership boundaries or changes,
thought-experiment and blindspot coverage, validation results, runtime
evaluation status (`exercised`, `not requested`, `blocked`, or `not
exercised`), and any intentionally deferred cases or unresolved ambiguity.
Confirm any temporary Markdown thought-experiment notes were deleted before
commit. Never claim a bulk update without listing its targets.
