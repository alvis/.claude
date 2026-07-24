# Action: verify

Loaded by `SKILL.md` when the first argument is `verify`. Validate a new or
changed skill; the shared policy, verification commands, and completion contract
live in `SKILL.md`.

## Boundaries

- Claude Code's validator owns manifest and frontmatter schema correctness.
- `quick_validate.py` owns repository policies only; it must not duplicate the
  evolving Claude schema.
- Functional and trigger checks are required when behavior or discovery changed,
  not for a wording-only edit with unchanged meaning.

## Inputs

- **Required**: a `SKILL.md`, skill directory, plugin, marketplace, or plugins
  path.
- **Optional** mode: `structural`, `functional`, or `full` (default `full`).
- **Optional** representative prompts supplied inline and `runtime: true|false`
  (default `false`).

## Workflow

1. Resolve the target and enumerate affected skills and plugin roots.
2. Resolve each affected plugin root from the target path, then run official
   strict validation for every affected plugin. Report Claude's errors verbatim
   enough to identify their source; do not reinterpret valid fields through a
   private schema.
3. Run `${CLAUDE_SKILL_DIR}/scripts/quick_validate.py` on the target. Review body
   length, description budget, unresolved local references, and placeholders.
4. For functional or full mode, derive a transient representative-case matrix
   from the owned outcome and any caller-supplied prompts. Keep it in context or
   a temporary Markdown scratch file outside the repository. Follow
   [functional-mode.md](functional-mode.md) for the case shape, paper-only
   reasoning, and optional isolated runtime execution.
5. Include positive trigger prompts, nearby negative prompts, and behavior or
   failure cases relevant to the change. Separate reasoned outcomes from
   observed runtime evidence; a pass must not claim execution that did not run.
6. Aggregate evidence by skill and delete any temporary scratch file. When fixes
   are requested, change only reported causes and rerun the failed checks.

The validator does not require fixed headings, personas, diagrams, subagent
prompts, XML report envelopes, or a section literally named "Skill Completion."

## Verification

```bash
claude plugin validate --strict <plugin-path>
python3 "${CLAUDE_SKILL_DIR}/scripts/quick_validate.py" <skill-or-plugin-path>
```

Run both commands after every fix iteration. Trigger and functional results must
include the prompt, expectation, reasoned or observed outcome, and pass/fail
rationale.

## Completion

Return a concise per-skill verdict with official validation status, policy
issues, transient functional/trigger evidence when applicable, runtime status
(`exercised`, `not requested`, or `blocked`), scratch cleanup confirmation, and
actionable failures.
