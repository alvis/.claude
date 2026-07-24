# Governance

The meta-layer: creating and maintaining the Claude Code configuration this
marketplace is made of — agents, skills, and standards — with validation
before anything ships. Depends on `essential`. Routes to two agents:
`harness-eval-engineer` (eval harnesses, benchmarks, feasibility prototypes)
and `workflow-optimizer` (meta-review of agents, skills, and collaboration
patterns).

## Skills

| Skill | Use when |
| --- | --- |
| `governance:create-skill` | Turning a repeatable workflow into a discoverable skill with clear ownership and triggers. |
| `governance:update-skill` | Revising existing skills, narrowing overlap, applying deliberate behavior changes. |
| `governance:verify-skill` | Structural + policy validation of a new or changed skill, with representative trigger reasoning and optional isolated runtime checks. |
| `governance:create-agent` | Scaffolding a new specialist agent (two stitched sources: `base.md` + `frontmatter/claude.json`). |
| `governance:update-agent` | Migrating selected agents to the current template or a stated behavior change. |
| `governance:create-standard` | Establishing a new standard (meta/scan/write + per-rule guides) under a plugin's constitution. |
| `governance:update-standard` | Scoped rule changes and template migrations for existing standards. |

`constitution/` holds the authoring templates and invariants (agent, skill,
command, standard shells; authoring-invariants, delegation, context-catalog
references). Validation entry point:
`skills/verify-skill/scripts/quick_validate.py`.
