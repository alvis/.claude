# Claude Code and Codex compatibility

Load this reference only when a Claude Code or Codex difference affects a
skill's execution, required tools, or validation.

## Behavior-affecting differences

- Explicit skill selection does not test implicit discovery. Use
  natural-language intent for agent activation guidance and trigger checks.
- Claude Code path substitutions and frontmatter extensions have no portable
  meaning. Do not put them in the shared `SKILL.md`.
- Resolve every supporting file from the skill root according to
  `references/authoring.md`.
- Do not translate a Claude-only control or runtime command into a Codex
  equivalent by analogy. Use only behavior documented by the target harness.

## Validation

After the portable checks in `references/authoring.md`, run the root
`SKILL.md` verification command when the target includes Claude Code. This
repository defines no general Codex validator or runtime evaluator, so do not
invent one. When an isolated Codex check is unavailable, report the unverified
behavior instead of substituting a Claude result.

## Sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/slash-commands)
- [OpenAI skill building](https://developers.openai.com/plugins/build/skills)
