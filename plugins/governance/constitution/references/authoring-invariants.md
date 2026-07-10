# Skill-Authoring Invariants

These are the shared repository rules for `create-skill`, `update-skill`, and
`verify-skill`. Claude Code's validator remains authoritative for manifest and
frontmatter syntax.

## Content

- Write one coherent document. Integrate changes where readers expect them;
  remove superseded prose instead of appending corrections or addenda.
- Keep the always-used workflow in `SKILL.md` and move bulky conditional detail
  to `references/<topic>.md`, linked at the decision point.
- Keep a main `SKILL.md` below 500 body lines. Prefer concise instructions over
  personas, metaphors, diagrams, repeated phase descriptions, and fixed report
  envelopes.
- Use headings that fit the capability. Boundaries, inputs, workflow,
  verification, and completion are useful defaults, not mandatory names.
- Delegate only when the workflow benefits from independent work. A skill does
  not need subagents, diagrams, or orchestration ceremony to be complete.

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
3. Exercise the skill with representative positive and near-miss prompts when
   behavior or trigger ownership changed.
