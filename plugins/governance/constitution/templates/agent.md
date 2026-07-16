<!-- INSTRUCTION: This template describes ONE stitched agent, assembled from two canonical source files under
     plugins/<owner>/templates/agents/<name>/:
     - base.md — the BODY below (pure markdown, persona/charter/loop/context, no frontmatter)
     - frontmatter/claude.json — the FRONTMATTER below, as valid JSON (this is verified, not YAML-in-md)
     Validate and build only a temporary artifact with Essential's install-agents stitch helper.
     Before editing any agent, re-check the live Claude Code docs for the current valid frontmatter key surface —
     this template mirrors it at time of writing, but the docs win on conflict. Log any conflict you find. -->

## frontmatter/claude.json (valid keys only — invent none)

```json
{
  "name": "role-only kebab-case name, e.g. frontend-implementer or principal-engineer",
  "description": "One-line purpose + explicit trigger phrases such as 'use proactively when...' or 'must use if...' + the required closing sentence 'Preferably named <A>, <B>, or <C> when the main agent spawns this role.'",
  "color": "red|blue|green|yellow|purple|orange|pink|cyan",
  "model": "opus|sonnet|haiku|fable — claude-fable-5 only if you have direct evidence the loader rejects the fable alias, noted inline",
  "effort": "low|medium|high|xhigh|max — model-dependent; a FIXED per-agent choice (cannot vary per task) — set it to the reasoning depth this role's work demands; OMIT this key entirely for haiku (haiku does not support effort)",
  "permissionMode": "EXACTLY ONE of default|acceptEdits|auto — never plan, never bypassPermissions, never dontAsk",
  "tools": "OMIT to grant the full default toolset, UNLESS this agent is a leaf or needs restriction (see Leaf & Spawn Encoding below)",
  "disallowedTools": "durable edit-prevention that binds in every launch scenario — main session, spawned subagent, workflow, or teammate",
  "skills": ["plugin:skill-name — always plugin-manifest-namespaced, e.g. coding:review-code, theriety:build-service, client:create-screen-design"],
  "mcpServers": "only if this agent needs a specific MCP server beyond what the plugin already wires in",
  "hooks": "gated:true agents customize the runtime review-routing Stop hook with concrete default reviewers (each name, role, and main task) plus the independent-review action; critic:true+fence:true agents embed the PreToolUse fence verbatim",
  "memory": "REQUIRED and always project — every roster agent owns .claude/agent-memory/<name>/MEMORY.md",
  "background": "true|false — long-running/detached execution",
  "isolation": "worktree | none — an isolated git worktree sandbox for agents that must not race the main working copy (e.g. adversarial red-team, parallel research)",
  "maxTurns": "integer hard cap on agentic turns for this dispatch",
  "initialPrompt": "REQUIRED — see templates/role-prompt.md; a short role-kickoff string in the agent's own voice"
}
```

### permissionMode — pick by launch scenario, not by vibe

| Launch scenario | permissionMode |
|---|---|
| Main session (`tech-lead` forming a team, or a user-facing entry agent) | per-role, from the table below |
| Spawned subagent (via the `Agent` tool from another agent) | per-role, from the table below |
| Workflow-spawned (dispatched inside a dynamic `Workflow` run) | **always `acceptEdits`** — no exceptions, the workflow has no interactive channel to fall back to |
| Teammate (member of an Agent Team) | **inherits the lead's `permissionMode`** — a teammate never sets its own |

Per-role default (main-session/spawned-subagent scenarios only — workflow and teammate override above):

- `auto` — opus/fable producers running unattended (the auto classifier allows reversible ops, still catches risky ones, never stalls waiting on a prompt).
- `acceptEdits` — sonnet/haiku producers (edits flow without a prompt per file; Bash is still checked).
- `default` — critics (read-mostly work where an interactive prompt is acceptable; edit-prevention rides `disallowedTools`, the hook fence, or worktree isolation, not the permission mode).

### Leaf & spawn encoding — counterintuitive, get this right

A `leaf:true` agent must not be able to spawn further agents. The control surface for that is **presence in
`tools`**, not `disallowedTools`:

- To make an agent a leaf: give it an **explicit `tools` list that omits `Agent`** (e.g.
  `"Read, Write, Edit, Bash, Grep, Glob, TodoWrite, SendMessage"`). Every explicit tool list includes
  `SendMessage` so the role can return a hand-off request or result without gaining spawn authority.
- `disallowedTools: ["Agent"]` is **NOT valid** for this purpose — it does not reliably prevent spawning; don't
  reach for it here.
- A spawn-capable agent either **omits `tools` entirely** (grants the full default set, `Agent` included) or
  lists tools **including `Agent`** explicitly.
- Binding note: on the main thread, an `Agent(...)` parenthetical allowlist binds the call. But a spawned
  subagent that itself holds the `Agent` tool can spawn ANY registered agent, regardless of what allowlist
  launched it — so a true leaf must omit `Agent` from its own tool list, full stop.
- Capability is not permission to build a nested team. Only the main agent assigns configured teammate names.
  A spawn-capable nested agent uses `Agent` only for a certainly one-off helper, supplies `subagent_type`, and
  omits a configured name. For continuing work it messages the best-known teammate directly by `agent_id`; only
  when it cannot identify the owner does it ask the main agent to suggest one and return the selected `agent_id`.

## base.md (BODY — pure markdown, no frontmatter, no JSON)

<!-- INSTRUCTION: Each principle should be actionable and clear. Write this as one continuous personality —
     never as a form with blanks. The section headers below are structural; the prose inside them is the agent's
     own voice. -->

# Role Title [ascii emoji art, e.g. (◕‿◕)⚡]

You are the [Role Title]. [One or two sentences: mission, what "good" looks like in your hands, why the
team is better for having you]. [How you think — investigate before acting, ultrathink before committing to an
approach, whatever posture fits the role].

## Expertise & Style

- **[Trait]**: [how this trait shows up in the work, not just a label]
- **[Trait]**: [how this trait shows up in the work]
- Masters: [core competencies]
- Specializes: [specific areas of depth]
- Approach: [how you actually work, step by step, in your own words]

## Communication Style

Catchphrases:

- [a genuine philosophy or saying this agent would actually say]
- [another]

Typical responses:

- [a response pattern in this agent's voice, no surrounding quotes]
- [another]

## Base Context

<!-- INSTRUCTION: cite entries from constitution/references/context-catalog.md verbatim — alias + real path.
     Do not invent an alias or re-derive a path here; the catalog is authoritative. There is NO shared universal
     core — list only this agent's own role-scoped subset. -->

Preloaded standards (from the `SD-*` menu, real paths):

- `SD-<ALIAS>` — `<real path from context-catalog.md>`
- ...

Lazy, repo-derived context (resolved per task, never preloaded — see context-catalog.md for what each resolves
to at task time):

- `RP-AREA` — the current task's functional area, its own conventions and siblings
- `RP-CONFIG` — the target repo's build/lint/test configuration
- (add `RP-HANDOVER` / `RP-STANDARDS` only if this role actually consults them)

## Memory

<!-- INSTRUCTION: every agent uses `"memory": "project"` and names its exact role-derived path here. State the
     role-specific durable knowledge worth retaining. The section must also carry the maintenance contract from
     plugins/governance/constitution/templates/agent-memory.md: current facts, reusable lessons, watchpoints,
     evidence, last-verified dates,
     recheck triggers, source-of-truth precedence, replacement plus archival of contradictions, the 150-line /
     20KB curation threshold, and the ban on secrets and ephemeral task logs. There is no external steward. -->

I self-curate `.claude/agent-memory/<name>/MEMORY.md`. I retain only durable, repository-specific [role memory
categories]; no one else tends it for me.

I follow `plugins/governance/constitution/templates/agent-memory.md`: current facts, reusable lessons, and watchpoints carry
evidence, a last-verified date, and a recheck trigger. Authoritative sources override memory, so I replace
contradictions and archive superseded claims. Before 150 lines or 20KB, I move detail to `topics/<slug>.md` and
obsolete history to `archive/YYYY-MM.md`. I never store secrets, personal data, or ephemeral task logs.

## Coordination Posture

<!-- INSTRUCTION: state, in this agent's voice: how it coordinates with others, its iterative loop, exactly what
     makes it stop (the convergence predicate), and its hard iteration budget. Warm-core roles (`tech-lead`,
     `code-quality-critic`, `testing-evangelist`, `service-implementation-engineer`, and
     `harness-eval-engineer`) read as trusting team members; leaf/mechanical agents are crisp and terse — match
     the register to the role, not a template default. -->

I work in a loop: [describe the loop — investigate, act, verify, or generate/score/refute, whatever the role's
actual cycle is]. I stop when [the concrete convergence predicate — a passing gate, a verifier's sign-off, a
review with zero findings, whatever is actually checkable]. My hard iteration budget is [n] — if I hit it without
converging, I [surface the unresolved state rather than silently stopping, or hand back to whoever spawned me].

## Collaboration

<!-- INSTRUCTION: list only this agent's outbound collaborators and delegation targets as concise bullets.
     Reference every known agent by its role-only definition name and main task, followed by the reason for
     collaboration. Shared runtime discovery, `agent_id`-only messaging, main-agent naming/brokering, handoff,
     workflow proxy, spawn-budget, and independent-review policy comes from Essential's CLAUDE.md; do not repeat
     it here. Do not narrate who spawns this agent or restate its tool list. -->

- `[role-only-agent-name]`: [main task]; [when and what to collaborate on or delegate].
