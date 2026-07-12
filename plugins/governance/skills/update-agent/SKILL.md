---
name: update-agent
description: Update explicitly selected agent definitions to the current two-file template or a stated behavior change while preserving useful role expertise, trigger boundaries, context, collaboration links, and working voice. Use when migrating agents to a template revision, correcting agent configuration, or batch-updating selected agents; require an exact selector and route genuinely new roles to create-agent.
model: opus
context: fork
allowed-tools: Task, Read, Write, Edit, Glob, Grep, Bash
argument-hint: "<agent path, name, or glob> [--changes=...] [--all]"
---

# Update Agent

Update selected `base.md` and `frontmatter/claude.json` pairs to the current
template or a stated behavior change. `create-agent` owns genuinely new
roles.

## Boundaries

- Use for: bounded template migrations and explicit corrections to
  explicitly selected agent definitions.
- Do not use for: creating a new role (`create-agent`), deleting agents,
  "modernizing" role-specific prose into template boilerplate, or changing
  protected fields the request did not authorize.
- An empty selector never means all; intentional repository-wide work
  requires explicit `--all`.

## Inputs

- **Required**: an agent path, name, or glob — or explicit `--all`.
- **Optional**: `--changes=...` describing the requested behavior,
  configuration, or template migration.
- **Prerequisites**: `${CLAUDE_SKILL_DIR}/../../constitution/templates/agent.md`,
  `role-prompt.md` beside it, and
  `${CLAUDE_SKILL_DIR}/../../constitution/references/context-catalog.md`.

## Workflow

1. Read the agent template, `role-prompt.md`, the context catalog, relevant
   team edges, every selected source pair, and real callers. List exact
   targets before mutation. Reject missing or malformed pairs, ambiguous
   globs, locked/in-use targets, or a request that actually creates a new
   role.
2. Snapshot each target before editing:
   - owned outcome, positive/negative triggers, expertise, role-specific
     working voice, and stop rule;
   - exact `SD-*`/`RP-*` context, collaboration/spawn edges, and
     skills/MCP/hooks;
   - model, fixed effort, permissionMode, tools, memory, isolation,
     background, maxTurns, and `initialPrompt`;
   - the explicit requested changes and the protected fields not authorized
     to change.
3. Re-evaluate the role classification and launch scenario against
   [../create-agent/references/model-effort-heuristic.md](../create-agent/references/model-effort-heuristic.md)
   (model, effort, permissionMode, tools, memory, and isolation criteria).
   Change those fields only when the requested migration or template requires
   it; report every such change.
4. Reconcile `frontmatter/claude.json` with the live template key surface.
   Remove obsolete keys only with evidence. Ensure a leaf has an explicit
   tools list omitting `Agent`, described delegation is actually permitted,
   and mutation tools are restricted for read-mostly roles.
5. Reconcile `base.md` with the required functional sections while preserving
   expertise and voice: integrate approved changes into the existing prose
   and remove superseded instructions — never append an update log or second
   personality. Correct context aliases against the catalog and collaboration
   edges against actual team definitions.
6. Rewrite `initialPrompt` from `role-prompt.md` whenever the role's first
   move, the artifact/brief it needs, or its guardrail changed. It must remain
   a 2-4 sentence no-task first-turn directive (first move → wait → deferred
   context + guardrail), must not restate identity, announce no task, or
   preload standards, and must agree exactly with `base.md`.
7. Recheck positive and near-miss triggers against neighboring agents and
   real dispatch sites. Do not widen role ownership incidentally.
8. Independent targets may be delegated per
   `${CLAUDE_SKILL_DIR}/../../constitution/references/delegation.md` in
   bounded batches — one agent pair per subagent, at most 8 parallel `Task`
   calls per dispatch — but each assignment must name exact source pairs and
   protected behavior. Review the integrated diff for cross-agent trigger and
   edge conflicts.
9. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- Run the actual repository stitch/build/agent validator when discoverable
  and inspect the generated definitions; do not invent a command.
- Always parse each JSON file with `python3 -m json.tool`, check for
  placeholders, and validate the key surface, model/effort compatibility,
  permission values, tool/spawn posture, context paths, namespaced skills,
  MCP/hooks, initialPrompt/base consistency, and trigger separation.
- When no repository validator exists, state that fact and use the
  deterministic fallback: template-key allowlist, reference checks, temporary
  stitched artifact inspection, and representative positive/negative dispatch
  examples. Do not claim official runtime validation unless the loader was
  actually run.

## Completion

Return the selector, targets, preserved role traits, changed fields, trigger
examples, validation evidence, runtime-loading status, and unresolved issues.
Completion requires every selected pair to validate and no unrequested role,
voice, permission, or ownership change.
