---
name: create-agent
description: Create a new specialist agent from the repository's two-file agent template when a distinct role, trigger surface, or delegation capability is missing. Confirm model, effort, permissions, tools, and context before authoring; validate the stitched definition and role-specific initial prompt without flattening the agent's working voice.
model: opus
context: fork
allowed-tools: Task, Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
argument-hint: "<role description> [--model=...] [--effort=...] [--permission=...] [--yes]"
---

# Create agent

Create `agents/<name>/base.md` and `agents/<name>/frontmatter/claude.json` for one genuinely distinct role. `update-agent` owns existing definitions.

## Grounding and decision gate

Read `${CLAUDE_SKILL_DIR}/../../constitution/templates/agent.md`, `role-prompt.md`, `references/context-catalog.md`, relevant team/edge definitions, and neighboring agents. Search existing descriptions and callers. Reject a duplicate role, unclear outcome, invalid kebab name, or missing authoritative template.

Classify the role as producer, critic, or orchestrator; leaf or spawn-capable; interactive, workflow-spawned, teammate, or background. Derive:

- positive trigger phrases, near-miss exclusions, owned outcome, and stop condition;
- the exact `SD-*` and `RP-*` aliases from the context catalog;
- model and fixed effort from cognitive demand, not prestige;
- launch-appropriate `permissionMode`;
- an explicit tools list omitting `Agent` for a leaf, or a spawn-capable tool surface;
- memory, isolation, background, maxTurns, skills, MCP, hooks, and collaboration edges only when the role needs them.

Present the proposed model, effort, permission, leaf/spawn posture, and exceptional capabilities in one confirmation gate. Flags override their named fields; `--yes` accepts the recommendations. Record the decision before writing.

## Authoring contract

1. Create only the two canonical source files. `frontmatter/claude.json` must be valid JSON and use only keys currently allowed by the live template. `initialPrompt` is required.
2. Build `initialPrompt` from `role-prompt.md` in 3–6 sentences: load exact context, state loop, convergence predicate, hard iteration budget, and one role-specific guardrail. It must agree with `base.md` and must not be generic kickoff prose.
3. Write `base.md` as the role's own continuous working voice, preserving the template's functional sections: role/mission, expertise and operating style, communication style, exact base context, coordination loop and stop rule, and collaboration/spawn posture. “Voice” means stable role-specific instructions, not a disposable persona or decorative biography.
4. Check tools against behavior: a leaf cannot mention delegation; a spawn-capable agent must have `Agent`; read-mostly critics must not accidentally receive mutation tools; workflow-spawned and teammate permissions must follow template rules.
5. Check model/effort compatibility, allowed permission values, valid color/model values, context aliases and paths, namespaced skills, MCP references, hooks, memory semantics, initialPrompt/base consistency, explicit triggers, and non-overlap with neighbors.

## Validation and fallback

Use the repository's real stitch/build/agent validator when one is discoverable from scripts or documentation, then inspect its generated definition. Do not invent a command. Always run `python3 -m json.tool agents/<name>/frontmatter/claude.json` and a placeholder/search check.

If no repository agent validator exists, perform and report the fallback explicitly: parse JSON, enforce the template key allowlist and required keys, verify referenced files/aliases/skills, stitch JSON-as-frontmatter plus `base.md` into a temporary artifact, and inspect that artifact for duplicate frontmatter/body seams and prompt contradictions. Official runtime loading remains “not exercised,” not “passed.”

Return created paths, confirmed settings, trigger/near-miss examples, context assignments, validation commands/results, whether runtime loading was exercised, and any unresolved concern. Completion requires both files, a non-overlapping trigger surface, a role-specific voice, and all available validation passing.
