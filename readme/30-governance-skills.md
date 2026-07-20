# governance skills (depends on: essential)

[Back to marketplace overview](../README.md#plugins-and-skills)

Tools for creating and managing Claude Code configuration files including commands, skills, standards, and agents

This catalog is generated from the plugin manifest and each skill's `SKILL.md` frontmatter. Run `python3 scripts/generate_readme.py` after changing either source.

- `governance:create-agent` — Creates a new specialist agent as two stitched source files, base.md plus frontmatter/claude.json, proposing model, effort, and permissions by role archetype and confirming them with the user before writing. Use when adding a new subagent, defining a new specialist role, scaffolding an agent definition, or when update-agent hands off new-agent creation.
- `governance:create-skill` — Use when creating a reusable Claude Code skill, defining a new repeatable agent capability, or replacing a one-off workflow with discoverable instructions that need clear ownership, validation, and trigger behavior.
- `governance:create-standard` — Create a new technical standard at a plugin's canonical constitution/standards root using meta.md, scan.md, write.md, and per-rule guides. Use when establishing new coding standards, documenting technical requirements, or creating compliance guidelines for reusable policy with explicit dependencies, detection, compliant patterns, and stable rule IDs. Route existing-standard revisions to update-standard.
- `governance:update-agent` — Update explicitly selected agent definitions to the current two-file template or a stated behavior change while preserving useful role expertise, trigger boundaries, context, collaboration links, and working voice. Use when migrating agents to a template revision, correcting agent configuration, or batch-updating selected agents; require an exact selector and route genuinely new roles to create-agent.
- `governance:update-skill` — Use when revising one or more existing Claude Code skills, aligning skill instructions with current repository policy, narrowing overlapping ownership, or applying a deliberate behavior change without creating a competing skill.
- `governance:update-standard` — Update explicitly selected plugin standards to the current meta.md, scan.md, write.md, and rules contract while preserving valid policy and stable rule IDs. Use when applying scoped rule changes, migrating standards to a template revision, or batch-updating the standards library. Require a path, glob, or --all; route missing targets to create-standard.
- `governance:verify-skill` — Use when validating a new or changed Claude Code skill, checking structural and repository policy compliance, reasoning through representative trigger and behavior cases, or optionally exercising isolated runtime prompts before deployment.
