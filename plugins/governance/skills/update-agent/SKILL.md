---
name: update-agent
description: Update explicitly selected agent definitions to the current two-file template or a stated behavior change while preserving useful role expertise, trigger boundaries, context, collaboration links, and working voice. Use when migrating agents to a template revision, correcting agent configuration, or batch-updating selected agents; require an exact selector and route genuinely new roles to create-agent.
model: opus
context: fork
allowed-tools: Agent, Read, Write, Edit, Glob, Grep, Bash
argument-hint: "<agent path, name, or glob> [--changes=...] [--all]"
---

# Update Agent

Find selected pairs under `plugins/*/templates/agents/<name>/`, then update
their `base.md` and `frontmatter/claude.json` to the current template or a
stated behavior change. `create-agent` owns genuinely new roles.

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
- **Owner token**: paths and ownership use the source-directory name under
  `plugins/` (for example, `backend`; its manifest namespace is `theriety`).
- **Prerequisites**: `${CLAUDE_SKILL_DIR}/../../constitution/templates/agent.md`,
  `role-prompt.md` beside it, and
  `${CLAUDE_SKILL_DIR}/../../constitution/references/context-catalog.md`.

## Workflow

1. Search every plugin's `templates/agents/` directory for the selector. Read
   the agent template, `role-prompt.md`, the context catalog, the owning
   plugin's `CLAUDE.md`, relevant team edges, every selected source pair, and real callers. List exact
   targets before mutation. Reject missing or malformed pairs, ambiguous
   globs, locked/in-use targets, or a request that actually creates a new
   role.
2. Snapshot each target before editing:
   - owned outcome, positive/negative triggers, expertise, role-specific
     working voice, and stop rule;
   - exact `SD-*`/`RP-*` context, collaboration/spawn edges, and
     skills/MCP/hooks;
   - model, fixed effort, permissionMode, absence of a tools allowlist, memory, isolation,
     background, maxTurns, and `initialPrompt`;
   - the explicit requested changes and the protected fields not authorized
     to change.
3. Re-evaluate the role classification and launch scenario against
   [../create-agent/references/model-effort-heuristic.md](../create-agent/references/model-effort-heuristic.md)
   (model, effort, permissionMode, runtime tool inheritance, memory, and isolation criteria).
   Change those fields only when the requested migration or template requires
   it; report every such change.
4. Reconcile `frontmatter/claude.json` with the live template key surface.
   Remove obsolete keys only with evidence. Always omit `tools` so runtime-provided capabilities remain visible;
   encode leaf and delegation posture in the role charter and shared orchestration rules. Use
   `disallowedTools` only for narrow durable restrictions on read-mostly roles, never as a general allowlist.
   For every review-routing Stop hook, keep concrete default reviewers aligned
   with Collaboration; include each reviewer's role and main task, the explicit
   independent-review action, and the better-runtime-specialist override.
5. Reconcile `base.md` with the required functional sections while preserving
   expertise and voice: integrate approved changes into the existing prose
   and remove superseded instructions — never append an update log or second
   personality. Keep definition paths, frontmatter names, headings, and identity
   prose role-only; descriptions end with exactly three distinct preferred short
   names for main-agent teammate naming. Correct context aliases against the
   catalog. Keep Collaboration to concise outbound collaborator/delegation bullets,
   referencing each known agent's role-only name and main task. Do not duplicate Essential's shared runtime discovery,
   handoff, workflow proxy, spawn-budget, or independent-review policy.
6. Rewrite `initialPrompt` from `role-prompt.md` whenever the role's first
   move, the artifact/brief it needs, or its guardrail changed. It must remain
   a 2-4 sentence no-task first-turn directive (first move → wait → deferred
   context + guardrail), must not restate identity, announce no task, or
   preload standards, and must agree exactly with `base.md`.
7. Recheck positive and near-miss triggers against neighboring agents and
   real dispatch sites through a paper-only thought experiment and blindspot
   test. If notes are written down, keep them temporary as a Markdown scratch
   document in an OS temp
   folder (for example `${TMPDIR:-/tmp}/check.md`) using
   `${CLAUDE_SKILL_DIR}/../../constitution/references/check.md` as the
   example table format with `:white_check_mark:`/`:x:` status markers,
   and delete them before staging; they are not deliverables and must not be
   committed. Keep the task-to-agent row in the
   owning plugin's `CLAUDE.md` aligned with the resulting trigger surface; do
   not create a central routing table or widen role ownership incidentally.
8. Independent targets may be delegated per
   `${CLAUDE_SKILL_DIR}/../../constitution/references/delegation.md` in
   bounded batches — one agent pair per subagent, never exceeding the declared
   task-wide child-spawn budget (default three new children) — but each assignment must name exact source pairs and
   protected behavior. Review the integrated diff for cross-agent trigger and
   edge conflicts.
9. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- Run Essential's deterministic stitch helper for every selected source pair,
  writing only temporary output, and inspect the generated definitions:
  `python3 plugins/essential/skills/install-agents/scripts/stitch_agent.py plugins/<owner>/templates/agents/<name> --output <temporary-path>`.
- Always parse each JSON file with `python3 -m json.tool`, check for
  placeholders, and validate the key surface, model/effort compatibility,
  permission values, tool/spawn posture, context paths, namespaced skills,
  MCP/hooks, initialPrompt/base consistency, trigger separation, and the owning
  plugin routing row. Do not claim official runtime validation unless the
  installed loader was actually run.

## Completion

Return the selector, targets, preserved role traits, changed fields, trigger
examples, thought-experiment and blindspot coverage, validation evidence,
runtime-loading status, confirmation that temporary Markdown
thought-experiment notes were deleted before commit, and unresolved issues.
Completion requires every selected pair to validate and no unrequested role,
voice, permission, or ownership change.
