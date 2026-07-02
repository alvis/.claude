# Base-Context Catalog

The menu of standards (`SD-*`) and repo-derived context (`RP-*`) an agent's `base.md` may cite, plus the per-agent
assignment map. This catalog is the single source of truth for context aliases — an agent's base.md never invents
its own alias or path; it cites entries from here verbatim.

## Rules

- **No shared universal core.** There is no `SD-*` bundle every agent inherits. Each agent lists only its own
  role-scoped subset from the assignment map below. Two agents with an overlapping subset still each declare it
  independently — there is no implicit inheritance to fall back on.
- **`RP-AREA` is lazy.** `RP-AREA`, `RP-CONFIG`, `RP-HANDOVER`, and `RP-STANDARDS` are repo-derived — resolved
  per task, from whatever repo the agent is currently working in. They are NEVER preloaded at agent-definition
  time and never hold a fixed path in this catalog; an agent's base.md states that it resolves them lazily, not
  what they currently point to.
- **`SD-*` are stable standards.** These live at fixed paths in this repo (the plugin `constitution/standards/`
  trees) and MAY be named as preload candidates for producers/critics per the assignment map.
- **Each memory-carrying agent self-curates its own `MEMORY.md`.** There is no external memory steward role and
  no shared memory file. An agent with a `memory` frontmatter key maintains
  `.claude/agent-memory/<name>/MEMORY.md` itself, pruning and rewriting it as its own judgment dictates.

## SD- menu (stable standards, real paths)

| Alias | Path |
|---|---|
| `SD-UNIVERSAL` | `coding/constitution/standards/universal/` |
| `SD-FUNCTION` | `coding/constitution/standards/function/` |
| `SD-TYPESCRIPT` | `coding/constitution/standards/typescript/` |
| `SD-NAMING` | `coding/constitution/standards/naming/` |
| `SD-TESTING` | `coding/constitution/standards/testing/` |
| `SD-GIT` | `coding/constitution/standards/git/` |
| `SD-DOCS` | `coding/constitution/standards/documentation/` |
| `SD-OBSERVABILITY` | `coding/constitution/standards/observability/` |
| `SD-REVIEW` | `coding/constitution/standards/code-review.md` |
| `SD-FILE-STRUCTURE` | `coding/constitution/standards/file-structure.md` |
| `SD-PYTHON` | `coding/constitution/standards/python/` |
| `SD-RUST` | `coding/constitution/standards/rust/` |
| `SD-DATA` | `backend/constitution/standards/{data-entity.md,data-operation.md}` |
| `SD-DESIGN` | `web/constitution/standards/{css,design,theming}/` + `react/constitution/standards/{components,accessibility,hooks,project-structure,storybook}/` |

Paths are relative to the plugin root (e.g. `SD-UNIVERSAL` resolves to
`plugins/coding/constitution/standards/universal/`). Directories (trailing slash, no `.md`) mean "read every file
under this tree, following cross-references"; single files (`.md`, no trailing slash) mean exactly that file.

### GAP note

`SD-AUTH` / `SD-DATA-PROTECT` do not exist. No `authentication.md` or `data-protection.md` standard has been
written anywhere in this repo. Any agent, template, or prior agent file that cites `authentication.md`,
`data-protection.md`, `communication.md`, `checklist.md`, `infrastructure.md`, `monitoring.md`, `deployment.md`,
`naming/README.md`, or the aliases `SD-AUTH`/`SD-DATA-PROTECT`/`SD-COMMS`/`SD-INFRA`/`SD-DEPLOY`/`SD-GOV`/
`SD-MONITOR` is citing a standard that was never written — those are fake and MUST NOT appear in any agent's base
context. Security- and data-protection-sensitive agents (e.g. `nina-petrov-security-champion`) fall back to
`SD-REVIEW` + `SD-UNIVERSAL` until a real auth/data-protection standard is authored; do not paper over the gap by
inventing a path.

## RP- menu (repo-derived, lazy — never preloaded, no fixed path here)

| Alias | Resolves to (at task time, from the target repo) |
|---|---|
| `RP-AREA` | The functional area/module the current task touches (its own conventions, siblings, existing patterns) |
| `RP-CONFIG` | The target repo's build/lint/test configuration (`package.json` scripts, tsconfig, eslint config, CI) |
| `RP-HANDOVER` | Any handover/design notes left for the current task (`coding:handover` output, design docs) |
| `RP-STANDARDS` | Repo-local standard overrides or additions layered on top of the `SD-*` set, if the target repo defines any |

An agent's base.md names which `RP-*` aliases it consults and states that resolution happens lazily per task — it
never bakes in a repo path, because the agent is not scoped to one repo.

## Per-agent context assignment map

Producers get `SD-UNIVERSAL` + `SD-FUNCTION` + `SD-TYPESCRIPT` + role SDs + `RP-AREA`(lazy) + `RP-CONFIG`(lazy).
Critics get `SD-REVIEW` + role SDs + `RP-AREA`(lazy). The table below is each agent's role-scoped `SD-*` subset;
every row additionally carries the lazy `RP-*` aliases implied by its producer/critic posture.

| Agent | SD- subset |
|---|---|
| `maya-rodriguez-principal` | `SD-UNIVERSAL`, `SD-FUNCTION`, `SD-TYPESCRIPT`, `SD-OBSERVABILITY`, `SD-REVIEW` |
| `raj-patel-techlead` | `SD-UNIVERSAL`, `SD-REVIEW`, `SD-GIT` |
| `marcus-williams-code-quality` | `SD-REVIEW`, `SD-UNIVERSAL`, `SD-FUNCTION`, `SD-TYPESCRIPT` |
| `ava-thompson-testing-evangelist` | `SD-TESTING`, `SD-FUNCTION`, `SD-TYPESCRIPT`, `SD-REVIEW` |
| `nina-petrov-security-champion` | `SD-REVIEW`, `SD-UNIVERSAL` |
| `james-mitchell-service-implementation` | `SD-UNIVERSAL`, `SD-FUNCTION`, `SD-TYPESCRIPT`, `SD-DATA`, `SD-TESTING` |
| `ethan-kumar-data-architect` | `SD-DATA`, `SD-UNIVERSAL`, `SD-TYPESCRIPT`, `SD-NAMING` |
| `felix-anderson-devops` | `SD-UNIVERSAL`, `SD-OBSERVABILITY`, `SD-GIT` |
| `nova-chen-research-engineer` | `SD-UNIVERSAL`, `SD-OBSERVABILITY`, `SD-REVIEW` |
| `oliver-singh-data-scientist` | `SD-UNIVERSAL`, `SD-PYTHON`, `SD-OBSERVABILITY` |
| `zara-ahmad-ml-engineer` | `SD-UNIVERSAL`, `SD-PYTHON`, `SD-FUNCTION`, `SD-TESTING` |
| `taylor-kim-workflow-optimizer` | `SD-UNIVERSAL`, `SD-DOCS` |
| `sam-taylor-specification` | `SD-DOCS`, `SD-NAMING`, `SD-UNIVERSAL` |
| `ada-bishop-initializer` | `SD-UNIVERSAL`, `SD-FILE-STRUCTURE`, `SD-GIT` |
| `coco-laurent-frontend-designer` | `SD-DESIGN`, `SD-UNIVERSAL`, `SD-TYPESCRIPT` |
| `penelope-sterling-aesthetic-evaluator` | `SD-DESIGN`, `SD-REVIEW` |
| `kai-raven-adversarial-redteam` | `SD-REVIEW`, `SD-UNIVERSAL` |
| `dexter-cho-harness-eval-engineer` | `SD-TESTING`, `SD-UNIVERSAL`, `SD-FUNCTION` |
| `tess-park-test-runner` | `SD-TESTING` |

19 agents total. Each row is exhaustive for that agent's `SD-*` subset — do not add standards beyond what is
listed here without updating this catalog first; the catalog, not the agent file, is authoritative.

## How an agent cites this catalog

An agent's `base.md` Base Context section lists its `SD-*` subset by alias + real path (copied verbatim from the
menu above — no re-deriving), states which `RP-*` aliases it resolves lazily, and — if it carries a `memory`
frontmatter key — states that it self-curates `.claude/agent-memory/<name>/MEMORY.md`. See
`templates/agent.md` for the section shape and `templates/role-prompt.md` for how the same context list is
compressed into an `initialPrompt` load-context clause.
