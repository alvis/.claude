# Agent team

[Back to marketplace overview](../README.md#agent-team)

A 23-agent team for Claude Code organized into a main-session Project Manager, domain leads, and their teammates. Shared operation lives in `plugins/essential/CLAUDE.md` and `MAINAGENT.md`, subagent conduct including the Workflow-proxy protocol lives in `plugins/essential/SUBAGENT.md`, owner-specific routing lives in each contributing plugin's `CLAUDE.md`, and per-agent delegation topology lives in each agent definition.

Install via the `essential:install-agents` skill (ask Claude to "install the agents"). Canonical sources live under `plugins/<owner>/templates/agents/<name>/` as `base.md` plus `frontmatter/claude.json`. The installer discovers source-checkout siblings or enabled same-marketplace plugins, validates the complete discovered roster, stages stitched files, and copies them into `~/.claude/agents/`. It overwrites current same-named discoveries and leaves unrelated or stale files untouched. Edits require a re-install, and changes take effect in the next session.

## Roster

| Agent | Role | Model | Effort | Permission | Flags |
| --- | --- | --- | --- | --- | --- |
| `tech-lead` | Tech Lead — decomposes projects, decides the approach, and routes milestones | fable | low | auto | memory |
| `design-lead` | Design Lead — decomposes and directs design initiatives across platforms | opus | high | auto | memory |
| `ai-research-lead` | AI Research Lead — decomposes and directs ML/RL/AI research initiatives | fable | medium | auto | memory |
| `principal-engineer` | Principal Engineer — escalation sink for hard debugging/perf/algorithms | fable | high | auto | gated, worktree, memory |
| `service-implementation-engineer` | Service Implementation — backend/API build-out | sonnet | medium | acceptEdits | gated, worktree, memory |
| `generalist-engineer` | Generalist Engineer — libraries, data pipelines, CLIs, glue code | sonnet | high | acceptEdits | gated, worktree, memory |
| `data-architect` | Data Architect — schemas, data models, pipelines | opus | high | auto | gated, memory |
| `frontend-designer` | Frontend Designer — designs all app screens (web/mobile/desktop), never builds | fable | high | auto | worktree, memory |
| `frontend-implementer` | Frontend Implementer — creates and edits production React/TS UI, with or without a design handoff | sonnet | high | acceptEdits | gated, worktree, memory |
| `desktop-implementer` | Desktop Implementer — builds approved designs as Electron/desktop apps | sonnet | high | acceptEdits | gated, worktree, memory |
| `mobile-implementer` | Mobile Implementer — builds approved designs as mobile apps in React Native | sonnet | high | acceptEdits | gated, worktree, memory |
| `ml-engineer` | ML Engineer — full ML lifecycle: data analysis and ML/AI features | opus | high | auto | gated, worktree, memory |
| `devops` | DevOps — CI/CD and infra automation, background passes | sonnet | medium | auto | gated, background, memory |
| `harness-eval-engineer` | Harness & Eval Engineer — eval suites, benchmarks, and prototypes as code | opus | high | auto | gated, worktree, memory |
| `testing-evangelist` | Testing Evangelist — authors test suites via TDD | sonnet | medium | acceptEdits | leaf, gated, memory |
| `test-runner` | Test Runner — mechanical lint/type/test sweeps, summarized | haiku | — | acceptEdits | leaf, background, memory |
| `code-quality-critic` | Code Quality Critic — the independent quality gate, day-to-day quality and security review | opus | medium | default | critic (write-fenced), memory |
| `security-champion` | Security Champion — deep security review, explicit request only | fable | high | default | critic, memory |
| `adversarial-red-team` | Adversarial Red-Team — PoC exploits in an isolated worktree | opus | high | default | leaf, worktree, memory |
| `aesthetic-evaluator` | Aesthetic Evaluator — design and build-vs-design judgment | fable | medium | default | leaf, critic (write-fenced), memory |
| `specification-expert` | Specification Expert — DESIGN.md, requirements, user docs, Notion | sonnet | medium | acceptEdits | leaf, memory |
| `project-initializer` | Project Initializer — run-once bootstrap | sonnet | low | acceptEdits | leaf, memory |
| `workflow-optimizer` | Workflow Optimizer — meta-review of agents/skills, proposes diffs only | opus | high | auto | background, memory |

Each agent's `## Collaboration` section records proven role-level collaborators and delegation targets using role-only definition names. These are runtime defaults, not an allowlist; naming, `agent_id` messaging, main-agent brokering, and nested-spawn policy live in `plugins/essential/CLAUDE.md`.

Every agent owns project-scoped memory at `.claude/agent-memory/<role>/MEMORY.md`. Definitions state the durable role-specific knowledge to retain, while `plugins/essential/templates/memory.md` defines the shared evidence, freshness, contradiction, archival, and size-control contract. Memory writers keep Write and Edit available without new hooks; source-read-only roles restrict those tools to memory by charter.

## Delegation topology

Role-routing defaults (the main agent may reuse a matching live `agent_id` or spawn a new named teammate):

```
Project Manager (forms and names teams; brokers the user and session tools)
  ├── tech-lead (engineering-domain lead; decomposes work; owns technical decisions and delivery)
  │   └── any registered teammate
  ├── design-lead ──► frontend-designer, frontend-implementer, desktop-implementer, mobile-implementer, aesthetic-evaluator
  └── ai-research-lead ──► ml-engineer, harness-eval-engineer, data-architect
service-implementation-engineer ──► principal-engineer, security-champion, test-runner, code-quality-critic, testing-evangelist
generalist-engineer ──► data-architect, code-quality-critic, test-runner, testing-evangelist, principal-engineer, tech-lead
data-architect ──► ml-engineer, service-implementation-engineer, test-runner, principal-engineer, code-quality-critic
principal-engineer ──► security-champion, test-runner, code-quality-critic
frontend-designer ──► aesthetic-evaluator, frontend-implementer, desktop-implementer, mobile-implementer
frontend-implementer ──► aesthetic-evaluator, code-quality-critic, test-runner, frontend-designer, tech-lead
desktop-implementer/mobile-implementer ──► aesthetic-evaluator, code-quality-critic, test-runner, frontend-designer, design-lead
devops ──► code-quality-critic, security-champion, test-runner; escalates to principal-engineer
ml-engineer ──► data-architect, test-runner, principal-engineer, code-quality-critic
harness-eval-engineer ──► testing-evangelist, code-quality-critic, test-runner, tech-lead
code-quality-critic ──► security-champion, adversarial-red-team
security-champion ──► adversarial-red-team
workflow-optimizer ──► runtime specialists for bounded audit slices and second opinions
```

Leaf-by-charter agents: `testing-evangelist`, `specification-expert`, `project-initializer`, `aesthetic-evaluator`, `adversarial-red-team`, and `test-runner`. Like every agent definition, they omit `tools` and inherit the runtime tool surface; their charter prohibits nested spawning. They message the best-known peer directly by `agent_id`; only when they cannot identify the owner do they ask the main agent to suggest one.

Team hand-off edges are documented by role for readability, but every `SendMessage` call targets the captured runtime `agent_id`:

```
design-lead → frontend-designer/frontend-implementer/desktop-implementer/mobile-implementer: initiative slice per platform
design-lead → aesthetic-evaluator: initiative sign-off
ai-research-lead → ml-engineer/harness-eval-engineer/data-architect: research or experiment slice
service-implementation-engineer → code-quality-critic: implementation complete, before commit
code-quality-critic → service-implementation-engineer: gate failure, with findings
code-quality-critic → tech-lead: gate pass, or two rounds exhausted
testing-evangelist → service-implementation-engineer/frontend-implementer/generalist-engineer: coverage gap found
frontend-designer → frontend-implementer/desktop-implementer/mobile-implementer: approved design handoff
frontend-implementer/desktop-implementer/mobile-implementer → aesthetic-evaluator: build complete, fidelity check
data-architect ↔ ml-engineer: schema design and data-profiling consults
harness-eval-engineer ↔ testing-evangelist: test-strategy and harness alignment
any producer → principal-engineer: blocked on a hard technical problem
any agent → main agent: Workflow launch request (see plugins/essential/SUBAGENT.md)
```

Only the main agent names persistent teammates. It chooses one of the three short names in the role description, formats `<short-name>-<role>-<task>`, and avoids collisions. Nested agents may spawn only certainly one-off helpers, specify `subagent_type`, and omit configured names; for continuing work they message the best-known teammate directly by `agent_id` and ask the main agent to suggest an owner only when they cannot identify one.

## Team shapes

- **Domain leads**: `tech-lead` for coding delivery, `design-lead` for design delivery, and `ai-research-lead` for research delivery.
- **Warm-core specialists** (trusting, low-friction hand-offs): `code-quality-critic`, `testing-evangelist`, `service-implementation-engineer`, `generalist-engineer`, `harness-eval-engineer`.
- **On-demand specialists**: `principal-engineer`, `data-architect`, `frontend-designer`, `frontend-implementer`, `desktop-implementer`, `mobile-implementer`, `ml-engineer`, `security-champion`, `aesthetic-evaluator`, `adversarial-red-team`, `specification-expert`, `project-initializer`.
- **Background** (one run per spawn): `devops`, `workflow-optimizer`.
- **Mechanical**: `test-runner`.

## Gates

- **Gated producers** (embedded prompt-type routing Stop gate; 2-round cap): `principal-engineer`, `testing-evangelist`, `service-implementation-engineer`, `data-architect`, `devops`, `ml-engineer`, `harness-eval-engineer`, `frontend-implementer`, `generalist-engineer`, `desktop-implementer`, `mobile-implementer`. Each gate checks the producer's final message for the generic `REVIEWED: source=<specialist|general|external|none> reviewer=<agent-id|tool-name|none> verdict=<ok|blocked|unavailable> round=<n>` attestation and requests review through a known reviewer `agent_id` or the main agent.
- **Write-fenced critics** (PreToolUse fence): `code-quality-critic`, `aesthetic-evaluator` — may only write to their agent-memory dir or review reports.

## Team operation

- Works team-first: The Project Manager initiates the team, appoints domain leads, and handles staffing and user/session proxies. Each lead gathers teammate advice, decomposes its assigned work, owns the domain's implementation decisions, assigns and monitors the pieces across its team, and reconciles delivery. `plugins/essential/CLAUDE.md` carries shared operation rules; each owner plugin's `CLAUDE.md` carries only its task-to-specialist rows.
- Subagents reply to the assigning teammate's `agent_id`. Roles and configured names are never direct-message addresses. For continuing work they message the best-known teammate directly when they have its ID, ask the main agent to resolve the ID when the teammate is known, and ask the main agent to suggest a warm peer by folder/feature history or spawn a new named teammate only when they cannot identify the owner.
- Subagents never launch the `Workflow` tool: they compose the complete tool input and SendMessage it to the main agent, which launches it and replies with the result (see `plugins/essential/SUBAGENT.md`). Plans authored by a specialist in plan mode flow back to the main agent the same way for presentation.

## Notes

- The copy-install into `~/.claude/agents/` is load-bearing for the hooks: Claude Code honors `hooks`, `permissionMode`, and `mcpServers` frontmatter only for agents in `~/.claude/agents/` / `.claude/agents/` — agents registered via a plugin ignore those fields. Do not convert the roster to plugin-registered agents, or every embedded gate and fence goes dead.
- `ml-engineer` uses the `theriety:build-service` skill — it requires the plugin whose manifest name is `theriety` (this marketplace registers it under the entry name `backend`; the manifest-vs-marketplace name mismatch is known).
- Installed agent definitions are intentionally single self-contained files even though their canonical source is split. This is why the routing Stop gate is embedded verbatim in all eleven gated producers.
- Standards references (`SD-*`) in the definitions never use literal installation paths. They name a standard plus its owning plugin constitution, resolved at runtime when that plugin is enabled. A partial enabled roster is valid, so cross-plugin handoffs and context are best-effort when their owner plugin is absent.
