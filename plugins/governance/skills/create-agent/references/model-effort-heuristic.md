# Model & Effort Heuristic

Shared decision table for `create-agent` and `update-agent`. Both model and effort are FIXED at authoring (one value each for everything the role will ever do, not tuned per task). Pick the cheapest setting that clears the role's bar; effort, not the model, carries the depth distinction.

## Model — two tiers

- `haiku` — deterministic/mechanical roles with a known procedure (run tests, lint, collect output, mechanical sweeps).
- `opus` — every other role, from routine edits to adversarial scrutiny, research, design, and orchestration. Set the reasoning depth with `effort`.

## Effort — reasoning depth the role's work demands

Omit for `haiku` (it does not support effort); live Claude Code docs win on exact semantics.

- `low` — shallow, near-deterministic; the procedure is known.
- `medium` — a few genuine decision points.
- `high` — sustained multi-step judgment; correctness hinges on the reasoning.
- `xhigh` — deep adversarial scrutiny or synthesis across many sources.
- `max` — exhaustive reasoning for a pivotal one-shot decision; reserve for gates where cost is no object.

## Archetype → (model, effort) starting points

- mechanical / leaf-mechanical → (`haiku`, effort omitted)
- routine / scaffolding producer → (`opus`, `low`)
- judgment producer → (`opus`, `medium`)
- critic → (`opus`, `medium`)
- adversarial / deep-reasoning / research / design → (`opus`, `high`)
- orchestrator / tech-lead → (`opus`, `high`)
- one-shot deep-reasoning gate → (`opus`, `xhigh`–`max`)

## permissionMode by launch scenario

- main/spawned → `auto` for leads, orchestrators, and unattended deep-reasoning or automation producers; `acceptEdits` for producers whose output is scoped file edits; `default` for critics
- workflow-spawned → always `acceptEdits`
- teammate → inherits the lead's

## Tools

Always omit `tools` so the agent inherits every tool available at runtime; an explicit allowlist hides tools that
were unknown when the definition was authored. Leaf posture is behavioral: a leaf must not spawn even when
`Agent` is present, while a coordinating role uses it only under the shared orchestration rules.

## Memory and isolation

- `memory`: set `user`/`project`/`local` only when the agent genuinely self-curates a persistent `.claude/agent-memory/<name>/MEMORY.md` across sessions; OMIT the key to disable — there is no `memory: none`.
- `isolation`: set `worktree` only for agents that must not race the main working copy (adversarial red-team, parallel research); otherwise omit.
