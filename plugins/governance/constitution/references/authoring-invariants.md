# Skill-Authoring Invariants

These are the shared repository rules for `create-skill`, `update-skill`, and
`verify-skill`. Claude Code's validator remains authoritative for manifest and
frontmatter syntax.

## Content

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
  envelopes.
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

- Use valid Claude Code skill frontmatter. Require `name` and `description`;
  quote scalar values when YAML punctuation could change their meaning.
- Make descriptions concrete trigger guidance. Aim for 25-60 words and explain
  neighboring exclusions only when they prevent a real trigger collision.
- Omit `context` for inline execution; use `context: fork` only when isolation is
  intentional and supported by Claude Code.
- Keep `allowed-tools` in any Claude-supported representation; do not rewrite a
  valid value for cosmetic uniformity.

## Validation

1. Run `claude plugin validate --strict <plugin-path>` for schema correctness.
2. Run `quick_validate.py` for repository policies such as body length,
   placeholders, description budget, and unresolved local Markdown links.
3. Reason through representative positive and near-miss prompts when behavior
   or trigger ownership changed. This is a paper-only thought experiment and
   blindspot test unless an executable evaluation runs; do not report runtime
   behavior as exercised from paper reasoning alone. Any
   written scratch notes should be Markdown tables following
   [check.md](check.md) with `:white_check_mark:`/`:x:` status
   markers, stored only in an OS temp folder (for example
   `${TMPDIR:-/tmp}/check.md`). They are temporary reasoning aids,
   not deliverables, and must be deleted before staging or committing.
