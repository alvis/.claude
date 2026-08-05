# Action: verify

Loaded by `SKILL.md` when the first argument is `verify`. Validate a new or
changed skill; the shared policy, thought-experiment/blindspot test, and
verification commands live in `SKILL.md`.

## Boundaries

- The Agent Skills specification owns the portable directory, required
  frontmatter, and supporting-file contract.
- Claude Code's validator owns Claude manifest and frontmatter schema
  correctness only.
- `quick_validate.py` owns repository policies only; it must not duplicate the
  evolving Claude schema. Its default run delegates schema validation to
  Claude; `--policy-only` is the bounded path when that validator is not
  available.
- Codex validation uses the documented Agent Skills contract and applicable
  documented Codex behavior. Do not invent a `codex plugin validate` command
  or infer Codex support from a Claude-only field.
- Functional and trigger checks are required when behavior or discovery changed,
  not for a wording-only edit with unchanged meaning.

## Inputs

- **Required**: a `SKILL.md`, skill directory, plugin, marketplace, or plugins
  path.
- **Optional** mode: `structural`, `functional`, or `full` (default `full`).
- **Optional** representative prompts supplied inline and `runtime: true|false`
  (default `false`).
- **Optional** `fix: true|false` (default `false`) — apply fixes for reported
  causes and rerun the failed checks.

## Workflow

1. Resolve the target and enumerate affected skills and plugin roots.
2. Validate the portable core and load [harnesses.md](harnesses.md). Run only
   the applicable checks for the target harnesses. Report unavailable commands
   as not run or blocked rather than substituting a private validator.
3. Run `<write-skill-root>/scripts/quick_validate.py` on the target. Review body
   length, description budget, unresolved local references, and placeholders.
   Use `--policy-only` only when Claude validation is not part of the available
   target environment, and report that omission.
4. For functional or full mode, derive a transient representative-case matrix
   from the owned outcome and any caller-supplied prompts. Keep it in context or
   a temporary Markdown scratch file in the OS temp folder (for example
   `${TMPDIR:-/tmp}/check.md`). Follow [functional-mode.md](functional-mode.md)
   for the case shape, paper-only reasoning, and optional isolated runtime
   execution.
5. Include positive trigger prompts, nearby negative prompts, and behavior or
   failure cases relevant to the change. Separate reasoned outcomes from
   observed runtime evidence; a pass must not claim execution that did not run.
6. Aggregate evidence by skill and delete any temporary scratch file. When fixes
   are requested, change only reported causes and rerun the failed checks.

No harness-neutral validator requires fixed headings, personas, diagrams,
subagent prompts, XML report envelopes, or a section literally named "Skill
Completion."

## Verification

After every fix iteration, re-run the verification commands in `SKILL.md`.
Trigger and functional results must include the prompt, expectation, reasoned or
observed outcome, and pass/fail rationale.

## Completion

Return a concise per-skill verdict with Agent Skills, Claude, and Codex statuses
as applicable; policy issues; transient functional/trigger evidence when
applicable; runtime status (`exercised`, `not requested`, or `blocked`); scratch
cleanup confirmation; and actionable failures.
