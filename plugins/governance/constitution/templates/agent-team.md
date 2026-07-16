<!-- INSTRUCTION: This is the companion template for forming an Agent Team — persistent teammates that
     coordinate conversationally around a warm core, as distinct from a Dynamic Workflow. Only the main agent
     forms the team, assigns configured teammate names, and spawns new persistent teammates. A spawned subagent
     or existing teammate asks the main agent to broker continuing delegation. `tech-lead` is the default coding
     lead, not the only lead a runtime roster may expose. -->

# Agent Team — Template

## When to reach for this

An Agent Team earns its overhead when several roles must retain context through an extended back-and-forth — a
design review, incident bridge, or multi-role build where `service-implementation-engineer`,
`testing-evangelist`, and `code-quality-critic` need to see one another's reasoning rather than only final
artifacts. Independent dispatch-and-score slices belong to parallel `Agent` calls; high-volume scored iteration
belongs to a Dynamic Workflow.

## Identity at runtime

Keep the three identifiers separate:

- **Definition name / agent type** — the role-only registry name, such as `principal-engineer`. Use it to select
  the role and as `subagent_type`; never personalize definition paths or frontmatter names.
- **Configured teammate name** — a human-readable label assigned only by the main agent. Choose one of the three
  preferred short names in the role description and format `<short-name>-<role>-<task>`; choose another
  suggestion when a living teammate already uses that short name.
- **`agent_id`** — the runtime address returned after spawn. Every direct message targets this ID. Never use the
  definition name, `subagent_type`, configured name, or label as a `SendMessage` address.

## Warm core

The default warm core is `tech-lead`, `code-quality-critic`, `testing-evangelist`,
`service-implementation-engineer`, `generalist-engineer`, and `harness-eval-engineer`. Their own
`Coordination Posture` sections carry the trust and working style; this team template does not invent personas.

## Reusing a warm teammate

A teammate loads its base context once and stays warm across tasks. Separate spawns do not share cached context.

- Reuse a living teammate by its `agent_id` when it has the right role, relevant folder/feature history, and
  enough measured room.
- Retire a saturated teammate rather than topping it up; reuse is for warm-and-roomy peers.
- If a subagent needs continuing help but does not know a suitable `agent_id`, it sends the main agent the role,
  task, constraints, and relevant history. The main agent selects the best living match or spawns a new named
  teammate and returns its ID.
- Nested spawning is reserved for certainly one-off work whose single result ends the delegation. Such a call
  specifies `subagent_type`, omits a configured name, and does not create a standing teammate.

## Roles in a formed team

- **Lead** — selected from the live roster by role fit and always operating in the main session. `tech-lead` is
  the coding default. The lead alone forms and names the team.
- **Teammates** — members the main agent brings in. A teammate inherits the lead's `permissionMode` for the team
  session; its standalone value does not survive team formation.
- **Capabilities** — a teammate's own `skills` and `mcpServers` frontmatter are not applied in a team. The lead
  invokes or grants required capabilities at formation time.

## Coordination topology

State one topology when forming the team:

- **Star** — every teammate messages the lead's `agent_id`.
- **Chain** — one known `agent_id` hands directly to another known `agent_id`; use only for stable hand-offs.
- **Mesh** — known peers message one another directly for a bounded exchange. Use sparingly.

The topology describes allowed paths, but the actual `SendMessage` target is always an `agent_id`.

## Hand-offs

A hand-off transfers the complete unit of work — artifact paths, standards, acceptance criteria, constraints,
and why it matters. Document planned edges by role for readability, then bind each role to its returned
`agent_id` before the first message:

```text
service-implementation-engineer -> code-quality-critic: implementation complete, before commit
code-quality-critic -> service-implementation-engineer: gate failure, with findings
code-quality-critic -> tech-lead: gate pass, or two rounds exhausted
testing-evangelist -> service-implementation-engineer: coverage gap found during implementation
```

At runtime, the sender uses the recipient's captured ID, for example
`SendMessage(agent_id="agent-7f2", ...)`; it never addresses `code-quality-critic` as a type.

Every planned edge should already exist as a `Collaboration` statement in the source role's `base.md`. The team
activates proven edges; it does not invent ownership.

## Forming the team (main session only)

1. Inspect the live roster and select the lead by role fit; use `tech-lead` as the coding default.
2. Confirm the task needs persistent multi-role exchange rather than independent slices.
3. Select each teammate by role and prior working history, then read the three preferred short names in its
   description.
4. Assign a collision-free `<short-name>-<role>-<task>` configured name, spawn the teammate, and record the
   returned `agent_id` beside its role and task.
5. State the topology and role-level hand-off edges, then execute every direct hand-off with the recorded IDs.
6. If a subagent requests another continuing collaborator, reuse the best matching existing ID or spawn and
   name a new teammate; return the selected ID to the requester.
7. Work until each role's convergence predicate fires and the lead judges the overall task complete.

## Worked example — star with one chain edge

```text
Lead role: tech-lead
Lead configured name: raj-tech-lead-build-auth
Lead agent_id: agent-main

Teammates:
  - role: principal-engineer
    configured name: maya-principal-engineer-debug-cache
    agent_id: agent-41a
  - role: service-implementation-engineer
    configured name: james-service-implementation-engineer-build-auth
    agent_id: agent-52b
  - role: testing-evangelist
    configured name: ava-testing-evangelist-cover-auth
    agent_id: agent-63c
  - role: code-quality-critic
    configured name: marcus-code-quality-critic-review-auth
    agent_id: agent-74d

Topology: star, plus agent-52b -> agent-74d for the review gate
Convergence: agent-main closes when agent-74d reports gate pass and agent-63c reports no open coverage gap.
```
