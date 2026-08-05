# Claude Code and Codex compatibility

Load this reference only when a Claude Code or Codex difference affects a
skill's invocation, execution, required tools, or validation. The
[authoring invariants](../../../constitution/references/authoring-invariants.md)
own the shared Agent Skills contract.

## Behavior-affecting differences

- Claude Code invokes a skill explicitly as `/skill-name`; Codex uses
  `$skill-name`. Do not present either syntax as portable or use explicit
  invocation as evidence of implicit discovery.
- Claude Code path variables and frontmatter controls have no portable meaning.
  Apply the shared-source placement and fallback rules in the
  [authoring invariants](../../../constitution/references/authoring-invariants.md);
  keep harness-only metadata in that single shared file under those rules.
- Resolve shared supporting files relative to the loaded skill directory. When
  a command needs an absolute path, set a variable from the path used to load
  that skill's `SKILL.md`; do not depend on a fixed root or current working
  directory.
- Do not translate a Claude-only control or runtime command into a Codex
  equivalent by analogy. Use only behavior documented by the target harness.

## Validation

Validate the shared skill against the Agent Skills specification. Run
`skills-ref validate "$TARGET_SKILL_DIR"` when `skills-ref` is available, with
`TARGET_SKILL_DIR` resolved to the directory containing the target `SKILL.md`;
otherwise record the specification checks performed and that no standard
validator ran.

For Claude Code and repository policy, run the commands in
[the write-skill verification section](../SKILL.md#verification). This
repository defines no general Codex validator or runtime evaluator, so do not
invent a `codex plugin validate` command. When an isolated Codex check is
unavailable, report the unverified Codex behavior instead of substituting a
Claude result.

## Sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/slash-commands)
- [OpenAI skill building](https://developers.openai.com/plugins/build/skills)
