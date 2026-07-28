# Intelligence-Level Heuristic

Shared decision guide for `create-agent` and `update-agent`. An agent owns one fixed `intelligence` value in `frontmatter/meta.json`; Essential's [authoritative matrix](../../../../essential/skills/install-agents/references/intelligence-levels.json) projects it to each harness's native model and effort fields. Pick the least expensive level that clears the role's bar.

## Levels

- `mechanical` — deterministic roles with a known procedure, such as running tests, linting, collecting output, or mechanical sweeps.
- `low` — shallow, near-deterministic work whose procedure is known.
- `medium` — work with a few genuine decision points.
- `high` — sustained multi-step judgment where correctness hinges on reasoning.
- `xhigh` — deep adversarial scrutiny or synthesis across many sources.
- `max` — exhaustive reasoning for a pivotal one-shot decision where cost is secondary.
- `inherit` — intentionally defer model and effort selection to the active harness.

## Archetype starting points

- mechanical or leaf-mechanical → `mechanical`
- routine or scaffolding producer → `low`
- judgment producer or critic → `medium`
- adversarial, research, design, or orchestration role → `high`
- unusually deep synthesis or one-shot gate → `xhigh` or `max`

## Other settings

- `permissionMode`: use `auto` for leads, orchestrators, and unattended deep-reasoning or automation producers; `acceptEdits` for scoped edit producers; `default` for critics. Workflow-spawned agents always use `acceptEdits`; teammates inherit the lead's mode.
- Tools: omit `tools` so the agent inherits runtime capabilities. A leaf's no-spawn posture is behavioral.
- Memory: use project memory only when the role self-curates durable repository knowledge.
- Isolation: use `worktree` only when an agent must not race the main working copy.
