---
name: create-agent
description: "Creates a new specialist agent as two stitched source files, base.md plus frontmatter/claude.json, proposing model, effort, and permissions by role archetype and confirming them with the user before writing. Use when adding a new subagent, defining a new specialist role, scaffolding an agent definition, or when update-agent hands off new-agent creation."
model: opus
context: fork
allowed-tools: Task, Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash
argument-hint: "<role description> [--plugin=<owner>] [--model=...] [--effort=...] [--permission=...] [--yes]"
---

# Create Agent

Create `plugins/<owner>/templates/agents/<name>/base.md` and
`plugins/<owner>/templates/agents/<name>/frontmatter/claude.json` for one
genuinely distinct role, with ownership and critical settings confirmed before
anything is written. `update-agent` owns changes to existing definitions.

## Boundaries

- Use for: adding a new specialist subagent, scaffolding an agent definition
  from scratch, or accepting a new-role handoff from `update-agent`.
- Do not use for: modifying an existing agent (`update-agent`), creating
  skills (`create-skill`), or a role an existing agent already covers —
  reject the duplicate and route to `update-agent` instead of authoring a
  competing trigger surface.

## Inputs

- **Required**: a role name or description clear enough to classify into an
  archetype and to write trigger-bearing frontmatter.
- **Optional**: `--plugin=<owner>` pins the plugin that owns the role;
  `--model=...`, `--effort=...`, `--permission=...` pin that
  setting and skip its confirmation prompt; `--yes` accepts every
  recommendation without prompting.
- **Owner token**: use the plugin's source-directory name under `plugins/`
  (for example, `backend`; its manifest namespace remains `theriety`).
- **Prerequisites**: `${CLAUDE_SKILL_DIR}/../../constitution/templates/agent.md`,
  `role-prompt.md` beside it, and
  `${CLAUDE_SKILL_DIR}/../../constitution/references/context-catalog.md`.

## Workflow

1. Read the agent template, `role-prompt.md`, the context catalog, relevant
   team/edge definitions, and neighboring agents; search existing
   descriptions and callers. Reject a duplicate role, unclear outcome,
   invalid name (lowercase kebab, personalized-name-role such as
   `priya-fullstack`), or missing authoritative template.
2. Select the owning plugin by responsibility and existing trigger surface.
   If `--plugin` is omitted, recommend the closest owner and confirm it with
   the user before the settings confirmation. The owner must be a plugin in
   this repository; do not default all agents to Governance or Essential.
3. Classify the role — producer, critic, or orchestrator; leaf or
   spawn-capable; interactive, workflow-spawned, teammate, or background —
   and derive:
   - positive trigger phrases, near-miss exclusions, owned outcome, and stop
     condition;
   - the exact `SD-*` and `RP-*` aliases verbatim from the context catalog —
     invent no alias or path;
   - model, fixed effort, launch-appropriate `permissionMode`, and memory and
     isolation settings from
     [references/model-effort-heuristic.md](references/model-effort-heuristic.md)
     — pick the cheapest model that clears the role's bar and raise effort
     within a tier before upgrading the model;
   - an explicit tools list omitting `Agent` for a leaf, or a spawn-capable
     tool surface;
   - background, maxTurns, skills, MCP, hooks, and collaboration edges only
     when the role needs them.
4. Confirm before writing: compose one `AskUserQuestion` battery of at most
   four questions covering model, effort, and — only when they deviate from
   the archetype default — permissionMode and leaf-vs-spawn posture. List the
   recommended value first marked "(Recommended)" with a free-text override
   as the last option. Flags override their named fields and skip their
   prompts; `--yes` accepts all recommendations. No file is written before
   this gate resolves; record the confirmed settings.
5. Create only the two canonical source files beneath the confirmed owner's
   `templates/agents/<name>/` directory. `frontmatter/claude.json` must
   be valid JSON using only keys currently allowed by the live template;
   `initialPrompt` is required.
6. Build `initialPrompt` from `role-prompt.md` in 2-4 sentences as a no-task
   first-turn directive: its first move (propose if the role's next work is
   legible from repo state, else greet and state the artifact/brief it needs),
   an explicit wait, then deferred context loading and one role-specific
   guardrail. It must NOT restate identity, announce that no task was given, or
   preload standards, and it must agree with `base.md`.
7. Write `base.md` as the role's own continuous working voice, preserving the
   template's functional sections: role/mission, expertise and operating
   style, communication style, exact base context, coordination loop and stop
   rule, and collaboration/spawn posture. "Voice" means stable role-specific
   instructions, not a disposable persona or decorative biography.
8. Add or update the task-to-agent routing row in the owning plugin's
   `CLAUDE.md`, creating that file if necessary. Keep only this agent's owned
   tasks there; do not rebuild a central roster table.
9. Check tools against behavior: a leaf cannot mention delegation; a
   spawn-capable agent must have `Agent`; read-mostly critics must not
   accidentally receive mutation tools; workflow-spawned and teammate
   permissions must follow template rules. Also check model/effort
   compatibility, allowed permission values, valid color/model values,
   context aliases and paths, namespaced skills, MCP references, hooks,
   memory semantics, initialPrompt/base consistency, explicit triggers, and
   non-overlap with neighbors.
10. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- Run `python3 -m json.tool plugins/<owner>/templates/agents/<name>/frontmatter/claude.json`.
- Run Essential's deterministic stitch helper against the source directory,
  writing only to a temporary output, then inspect that artifact:
  `python3 plugins/essential/skills/install-agents/scripts/stitch_agent.py plugins/<owner>/templates/agents/<name> --output <temporary-path>`.
- Check placeholders, the template key allowlist and required keys, referenced
  files/aliases/skills, duplicate seams, prompt contradictions, and the owning
  plugin routing row. Official runtime loading remains "not exercised" unless
  the installed loader was actually run.

## Completion

Report created paths, the confirmed settings and who confirmed them (user,
flags, or `--yes`), archetype, trigger/near-miss examples, context
assignments, validation commands and results, whether runtime loading was
exercised, and any unresolved concern. Completion requires both files, a
non-overlapping trigger surface, a role-specific voice, and all available
validation passing.
