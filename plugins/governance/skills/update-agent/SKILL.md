---
name: update-agent
description: Update explicitly selected agent definitions to the current two-file template or a stated behavior change while preserving useful role expertise, trigger boundaries, context, collaboration links, and working voice. Use for bounded migrations and corrections; require an exact selector and route genuinely new roles to create-agent.
model: opus
context: fork
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash
argument-hint: "<agent path, name, or glob> [--changes=...] [--all]"
---

# Update agent

Update selected `base.md` and `frontmatter/claude.json` pairs. An empty selector never means all; intentional repository-wide work requires explicit `--all`.

## Resolve and preserve

Read `${CLAUDE_SKILL_DIR}/../../constitution/templates/agent.md`, `role-prompt.md`, and `${CLAUDE_SKILL_DIR}/../../constitution/references/context-catalog.md`, relevant team edges, every selected source pair, and real callers. List exact targets before mutation. Reject missing/malformed pairs, ambiguous globs, locked/in-use targets, or a request that actually creates a new role.

For each target, snapshot:

- owned outcome, positive/negative triggers, expertise, role-specific working voice, and stop rule;
- exact `SD-*`/`RP-*` context, collaboration/spawn edges, skills/MCP/hooks;
- model, fixed effort, permissionMode, tools, memory, isolation, background, maxTurns, and `initialPrompt`;
- explicit requested changes and protected fields not authorized to change.

Do not “modernize” by replacing role-specific prose with template boilerplate. Integrate approved changes into the existing voice and remove superseded instructions; never append an update log or second personality.

## Update procedure

1. Re-evaluate the role classification and launch scenario against the archetype table in `../create-agent/references/model-effort-heuristic.md`. Change model, effort, permission, tools, memory, isolation, or collaboration only when the requested migration/template requires it; report every such change.
2. Reconcile `frontmatter/claude.json` with the live template key surface. Remove obsolete keys only with evidence. Ensure a leaf has an explicit tools list omitting `Agent`; ensure described delegation is actually permitted; restrict mutation tools for read-mostly roles.
3. Reconcile `base.md` with required functional sections while preserving expertise and voice. Correct context aliases against the catalog and collaboration edges against actual team definitions.
4. Rewrite `initialPrompt` from `role-prompt.md` whenever loop, context, stop rule, budget, or guardrail changed. It must remain 3–6 role-specific sentences and agree exactly with `base.md`.
5. Recheck positive and near-miss triggers against neighboring agents and real dispatch sites. Do not widen role ownership incidentally.

Independent targets may be delegated in bounded batches — one agent pair per subagent, at most 8 parallel `Task` calls per dispatch — but each assignment must name exact source pairs and protected behavior. Review the integrated diff for cross-agent trigger and edge conflicts.

## Validation and fallback

Run the actual repository stitch/build/agent validator when discoverable; inspect generated definitions. Always parse each JSON file with `python3 -m json.tool`, check placeholders, and validate key surface, model/effort compatibility, permission, tool/spawn posture, context paths, namespaced skills, MCP/hooks, initialPrompt/base consistency, and trigger separation.

When no repository validator exists, state that fact and use the deterministic fallback: template-key allowlist, reference checks, temporary stitched artifact inspection, and representative positive/negative dispatch examples. Do not claim official runtime validation unless the loader was actually run.

Return selector, targets, preserved role traits, changed fields, trigger examples, validation evidence, runtime-loading status, and unresolved issues. Completion requires every selected pair to validate and no unrequested role, voice, permission, or ownership change.
