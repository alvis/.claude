# Agent Skill authoring contract

Load this reference for every action. It owns the portable structure and
content rules for skills authored by `write-skill`.

## Directory contract

- Author one self-contained skill directory with `SKILL.md` at its root.
- Stop at the skill directory; installation and catalog placement are separate
  workflows.
- Put optional documentation in `references/`, deterministic executables in
  `scripts/`, and templates or static resources in `assets/`.
- Keep every required resource inside the skill root. Address files directly
  from that root, such as `references/<topic>.md` or `scripts/<check>.py`, even
  when the instruction appears in a supporting file.
- Never require the caller's current working directory, a hard-coded install
  path, `../`, or a harness-specific path substitution to find a resource.
- Maintain one shared `SKILL.md` for Claude Code and Codex. Do not generate a
  portable projection of a non-portable source.

## `SKILL.md`

Use the strict Agent Skills frontmatter:

```yaml
---
name: skill-name
description: Describe the owned outcome and the natural-language conditions that should activate it.
---
```

`name` is 1-64 lowercase ASCII letters, digits, or hyphens, with no leading,
trailing, or consecutive hyphens; it must match the directory name.
`description` is non-empty, no more than 1024 characters, and states what the
skill does and when an agent should use it. Aim for 25-60 words and put the
primary intent first.

Portable optional fields are `license`, non-empty `compatibility` of at most 500
characters, and `metadata` as a map of string keys to string values. Agent
Skills marks `allowed-tools` as experimental and its support varies; never
depend on it for shared behavior. Omit harness extensions from a shared skill.
Express activation conditions as natural-language intent, not user-interface
command syntax.

When requested behavior names a harness-only control, express equivalent
behavior as a portable body instruction. If an instruction cannot provide the
same semantics, report the incompatibility instead of adding an extension,
projection, or harness-specific branch.

Write one coherent workflow. Keep always-used instructions in `SKILL.md`; move
only conditional detail to a directly linked resource. Include the inputs,
decisions, failure behavior, output, and verification needed to execute the
workflow. Remove prose that does not change agent behavior. Keep the body below
500 lines.

Use `<IMPORTANT>` only for hard guardrails and `<report>` only for
machine-readable output contracts. Close every tag.

## Supporting resources

- Explain when to read each reference or use each asset.
- Add a script only when deterministic computation or file processing is more
  reliable than instructions and existing tools. Make it self-contained,
  document dependencies, handle edge cases, and emit useful errors.
- Keep reference chains shallow. Link required resources directly from
  `SKILL.md` when practical.

## Validation

1. Run the Agent Skills reference validator:

   ```bash
   uvx --python 3.13 --from skills-ref agentskills validate "<skill-root>"
   ```

   If it is unavailable, check the strict frontmatter and directory rules above
   and report that no standard validator ran.
2. Run the bundled `scripts/quick_validate.py --portable` as described in the
   root `SKILL.md`. It checks the self-contained path contract and validates a
   containing Claude plugin only when one is resolvable.
3. Apply the harness-specific checks in `references/harnesses.md` only when the
   target includes that harness.
4. When behavior or discovery changes, reason through representative positive
   and near-miss prompts. Do not report runtime behavior as exercised unless an
   executable evaluation ran.
