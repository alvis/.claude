# Cross-harness Agent Skills

Load this reference when an action chooses skill locations, invocation,
frontmatter extensions, plugin packaging, or validation for Claude Code,
ChatGPT, or Codex. The Agent Skills specification is the portable source;
harness documentation owns product behavior.

## Portable core

A portable skill is one directory containing a required `SKILL.md` and optional
`references/`, `scripts/`, and `assets/`. Require `name` and `description`, make
`name` match the parent directory, and put the owned outcome and activation
conditions first in `description`. Harnesses discover from metadata and load the
body after activation, so keep always-needed procedure in `SKILL.md` and link
supporting files at the point they become relevant.

Write body instructions in terms of outcomes, inputs, tools, and files available
in every target harness. Use relative supporting-file references from the skill
root. Keep explicit invocation syntax, product path variables, namespaces, and
control fields out of the portable behavior. The Agent Skills specification
lists `allowed-tools` as experimental with implementation-dependent support.

Both supported harnesses can select a skill from metadata or by explicit user
invocation. That concept is portable; the syntax and policy controls below are
not.

## Claude Code

- Locations are managed enterprise skills, personal
  `~/.claude/skills/<name>/SKILL.md`, project
  `.claude/skills/<name>/SKILL.md`, and `<plugin>/skills/<name>/SKILL.md` while
  that plugin is enabled. Plugin skills use a plugin namespace.
- Explicit invocation uses Claude Code's `/skill-name` or namespaced plugin
  form. Do not present slash syntax as portable to Codex or ChatGPT.
- `${CLAUDE_SKILL_DIR}` and fields such as `context`,
  `disable-model-invocation`, `user-invocable`, `allowed-tools`, and `paths`
  have Claude-documented behavior. Keep them in a Claude branch and provide a
  portable fallback whenever the skill also targets Codex.
- Run `claude plugin validate --strict <plugin-path>` for Claude manifests and
  frontmatter. This marketplace's `quick_validate.py` invokes that validator in
  its default mode and then applies repository policy checks.

## Codex and ChatGPT

- Codex loads repository skills from `.agents/skills` from the current working
  directory through the repository root, user skills from `~/.agents/skills`,
  admin skills from `/etc/codex/skills`, and bundled system skills. Codex
  plugins expose shared skills through their `.codex-plugin/plugin.json`.
- Explicit invocation is `@skill-name` in ChatGPT and `$skill-name` in Codex.
  Neither form is a portable body-level contract.
- Optional OpenAI agent metadata at agents/openai.yaml configures interface, tool
  dependencies, and policy. `policy.allow_implicit_invocation: false` disables
  implicit selection while preserving explicit `$skill-name` use in Codex. Do
  not map Claude-only frontmatter controls onto this file by analogy.
- Validate the Agent Skills core against the current specification. If the
  target environment already provides a documented standard validator, run it
  and record the exact command; otherwise perform the reference checks and say
  no standard validator ran. Do not invent a `codex plugin validate` command.

## This marketplace

Keep one shared skill source at `plugins/<plugin>/skills/<name>/SKILL.md`.
Claude and Codex packaging are thin projections: each plugin has
`.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`; the authoritative
catalog is `.claude-plugin/marketplace.json`, and
`.agents/plugins/marketplace.json` is its generated Codex projection. Change a
manifest or catalog only when packaging changes, not for a body-only skill edit.

When the source catalog changes, regenerate and check the projection with:

```bash
uv run --python 3.13 scripts/generate_codex_marketplace.py
uv run --python 3.13 scripts/generate_codex_marketplace.py --check
```

Validate the dual manifests, shared Agent Skills contract, and catalog
projection with the repository's configured focused test:

```bash
uvx pytest scripts/test_plugin_marketplace.py
```

Run repository skill policy checks from the loaded write-skill root:

```bash
uv run --python 3.13 <write-skill-root>/scripts/quick_validate.py <target>
```

Use `--policy-only` only when Claude validation is unavailable and report the
Claude branch as not run or blocked. A cross-harness marketplace release is not
fully verified until both harness branches and the projection test pass.

## Sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/slash-commands)
- [OpenAI skill concepts](https://developers.openai.com/plugins/concepts/skills)
- [OpenAI skill building](https://developers.openai.com/plugins/build/skills)
