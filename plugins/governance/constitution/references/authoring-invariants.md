# Skill-Authoring Invariants

These are the shared repository rules for authoring skills and agents — the
`write-skill` create, update, and verify actions, plus `create-agent` and
`update-agent`. The Agent Skills specification owns the portable skill
contract; each harness owns its extensions and manifest syntax.

## Content

- Before adding content, check it changes what someone does, and that what is
  missing isn't something else. Drop anything whose removal changes nothing —
  naming an example set of negations is unbounded and says nothing.
- Write one coherent document. Integrate changes where readers expect them;
  remove superseded prose instead of appending corrections or addenda.
- Keep the always-used workflow in `SKILL.md` and move bulky conditional detail
  to `references/<topic>.md`, linked at the decision point.
- Concision must preserve operational sufficiency. A skill is not complete when
  it names an outcome but omits the commands, decision gates, state handoff,
  failure behavior, or verification procedure needed to produce that outcome.
  Trim repetition and ceremony; never trim the executable contract.
- Keep a main `SKILL.md` below 500 body lines. Prefer concise instructions over
  personas, metaphors, diagrams, repeated phase descriptions, and fixed report
  envelopes. This is a skill-specific limit on top of the general artifact
  length rule, which is defined once in
  `essential:references/output-manifest.md` and is not restated here.
- Use headings that fit the capability. Boundaries, inputs, workflow,
  verification, and completion are useful defaults, not mandatory names.
- Delegate when performing a step directly would consume more session context
  than describing the task to a subagent and reading its report; keep small
  work inline — a skill does not need subagents, diagrams, or orchestration
  ceremony to be complete. When a skill does delegate, follow the batching,
  report, and decision guidance in [delegation.md](delegation.md).

## Content Boundary Convention

Enclose each block of important or long content in a semantically-named XML
tag so the block has an unambiguous, machine- and eye-visible boundary and
cannot bleed into surrounding prose. The tag names the content's role — it is
not a copy of the section heading and does not replace the `##`/`###`
headings that give the document its outline.

Tags in use: `<report>` encloses a machine-readable report or output
contract; `<IMPORTANT>` encloses a hard guardrail or critical instruction
that must not be missed.

- Name tags for the content, never for the section; do not wrap a short
  structural section in a tag that merely echoes its heading.
- Tags never replace headings — where both apply, keep both.
- Keep a language hint on a fenced block inside the tags (the tags are the
  boundary, the fence is the syntax hint).
- Every opening tag has a matching close.

## Frontmatter and discovery

- Require the Agent Skills `name` and `description`; make `name` lowercase
  kebab-case and identical to the skill directory. Quote scalar values when
  YAML punctuation could change their meaning.
- Make descriptions concrete trigger guidance. Aim for 25-60 words and explain
  neighboring exclusions only when they prevent a real trigger collision. Lead
  with the owned outcome and activation conditions because harnesses discover
  skills from metadata before loading the body.
- Keep the body and supporting-file references portable. Do not encode one
  harness's explicit invocation syntax, path variables, plugin namespace, or
  control fields as a cross-harness promise.
- Treat `allowed-tools` as experimental in the Agent Skills specification;
  preserve a valid target-harness representation, but do not promise identical
  semantics elsewhere.
- For Claude Code, omit `context` for inline execution and use `context: fork`
  only when intentional. Other Claude controls such as
  `disable-model-invocation`, `user-invocable`, and `paths` remain Claude-only
  unless another target harness independently documents them.

## Validation

1. Check the portable skill against the Agent Skills specification. Use a
   standard validator only when it is documented and available; otherwise
   record the reference checks performed.
2. Run `claude plugin validate --strict <plugin-path>` for Claude schema
   correctness when the target includes Claude Code.
3. Run `quick_validate.py` for repository policies such as body length,
   placeholders, description budget, and unresolved local Markdown links. Its
   default mode delegates schema validation to Claude; use `--policy-only` only
   when that branch is unavailable and report the omission.
4. For this marketplace's Codex target, validate the `.codex-plugin` manifest
   and the `.agents/plugins/marketplace.json` projection with the repository's
   configured tests; do not claim a Codex validator the repository does not
   provide.
5. Reason through representative positive and near-miss prompts when behavior
   or trigger ownership changed. This is a paper-only thought experiment and
   blindspot test unless an executable evaluation runs; do not report runtime
   behavior as exercised from paper reasoning alone. Any
   written scratch notes should be Markdown tables following
   [check.md](check.md) with `:white_check_mark:`/`:x:` status
   markers, stored only in an OS temp folder (for example
   `${TMPDIR:-/tmp}/check.md`). They are temporary reasoning aids,
   not deliverables, and must be deleted before staging or committing.
