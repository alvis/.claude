<!-- INSTRUCTION: This is the companion template for forming an Agent Team — a set of persistent teammates that
     coordinate conversationally around a warm core, as distinct from a Dynamic Workflow (templates/dynamic-
     workflow.md), which is a deterministic script. Only the main session (Raj) forms a team, and only Raj
     initiates it — a spawned subagent or an existing teammate never calls the team-forming action itself. -->

# Agent Team — Template

## When to reach for this

An Agent Team earns its overhead when the task needs several roles holding context *together* over an extended,
back-and-forth exchange — design review, an incident bridge, a multi-role build where James, Ava, and Marcus need
to see each other's reasoning live, not just each other's final artifacts. If the task decomposes into
independent slices that only need to be dispatched and scored, that is a Dynamic Workflow's job, not a team's —
don't form a team to do a workflow's work more expensively.

## Warm core

The warm-core agents — Raj, Marcus, Ava, James, Dexter — read as a trusting team in their own base.md Axis-2
sections: familiar with each other's working style, quick to hand off without re-explaining context, comfortable
disagreeing without re-litigating settled ground. This warmth is authored once, in each agent's own
`Coordination Posture` section (templates/agent.md) — a team roster does not add warmth the agents don't already
carry; it activates agents whose posture already expects a team.

## Roles in a formed team

- **Lead** — always Raj, always the main session. Raj is the only agent who forms a team and the only one whose
  `permissionMode` is independently set (per its own frontmatter); every other member of the team inherits it.
- **Teammates** — the members Raj brings in. A teammate's `permissionMode` is NOT its own frontmatter value once
  it joins a team — **it inherits the lead's `permissionMode`** for the duration of the team's work, overriding
  whatever the teammate's standalone agent file specifies. This is a hard rule, not a default: do not author a
  team roster that assumes a teammate's individual `permissionMode` survives team formation.
- **`skills` and `mcpServers` frontmatter are NOT applied to teammates.** A teammate operates with the lead's
  tool/skill surface for the duration of the team session — its own `skills`/`mcpServers` list (meaningful when
  it runs standalone as a spawned subagent) is inert while it is a teammate. Do not rely on a teammate's own
  skills list to grant it capability inside a team; if the team needs a skill, the lead invokes it or grants it
  at team-formation time.

## Coordination topology

State the topology explicitly when forming a team — it is not always a star around the lead:

- **Star** (most common): Raj at the center, each teammate reporting back to Raj, teammates not directly
  addressing each other. Simplest to reason about; use when hand-offs are strictly lead-mediated.
- **Chain**: teammate A hands directly to teammate B without routing through Raj (e.g. James implements, hands
  directly to Marcus for the gate, Marcus hands back to Raj only on failure). Use when a hand-off is always the
  same two roles and routing through the lead adds a pointless hop.
- **Mesh**: any teammate may address any other for a bounded sub-exchange (e.g. a design review where Coco,
  Penelope, and Kai converge on one screen together). Use sparingly — mesh topologies are the hardest to keep
  convergent; prefer star or chain unless the task genuinely needs multi-way live disagreement.

## Hand-offs

A hand-off is a teammate explicitly transferring the current unit of work (with its full context, not a summary)
to another named teammate or back to the lead. Author each hand-off edge as `A → B: <trigger>` — the condition
under which A hands to B, not just that it can:

```
James → Marcus: on implementation complete, before commit (gate)
Marcus → James: on gate failure, with the specific findings
Marcus → Raj: on gate pass, or on 2 rounds exhausted without a pass
Ava → James: on a coverage gap found during implementation, not after
```

Every hand-off edge the team roster declares should already exist as a `Collaboration` statement in each
teammate's own base.md (templates/agent.md) — a team roster does not invent new spawn edges, it activates edges
the agents already declared for themselves.

## Forming the team (main session only)

1. Raj identifies the task needs a live, multi-role, back-and-forth session rather than a dispatch-and-score
   workflow.
2. Raj selects teammates by role fit, states the topology (star/chain/mesh) and the hand-off edges for this
   specific task.
3. Raj's own `permissionMode` propagates to every teammate for the session's duration; teammates' individual
   `skills`/`mcpServers`/`permissionMode` frontmatter is set aside while the team runs.
4. The team works the hand-off chain until the lead judges the task done — a team does not have a Dynamic
   Workflow's formal `stopCheck()`; convergence is the lead's call, informed by each teammate's own convergence
   predicate (from its base.md Axis-2 section) firing on its own piece of the work.

## Worked example — star topology, coding-team core

```
Lead: Raj Patel (permissionMode: auto)
Teammates (inherit auto for this session, regardless of their own frontmatter):
  - Maya Rodriguez — architecture sanity check
  - James Mitchell — implementation
  - Ava Thompson — test coverage
  - Marcus Williams — quality gate

Topology: star, with one chain edge (James → Marcus, gate-mediated)

Hand-offs:
  James → Marcus: on implementation complete, before commit
  Marcus → James: on gate failure, with findings
  Marcus → Raj: on gate pass
  Ava → James: on a coverage gap found mid-implementation

Convergence: Raj judges done when Marcus reports gate pass AND Ava reports no open coverage gap.
```
