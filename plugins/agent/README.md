# agent

A 20-agent specialist team for Claude Code, plus the operating rules that make it work as a team: a team-first mandate for the main session (`CLAUDE.md`, injected every session), subagent conduct including the Workflow-proxy protocol (`SUBAGENT.md`, injected at every subagent start), and per-agent delegation topology carried in each agent's own definition.

## Install

Ask Claude to "install the agents" (the `install-agents` skill). It copies `skills/install-agents/references/agents/*.md` into `~/.claude/agents/`, overwriting managed same-named files and leaving unrelated user agents untouched. The definitions here are the source of truth — edits require a re-install, and the agent list is fixed at session start, so changes take effect in the next session.

## Roster

| Agent | Role | Model | Permission | Flags |
| --- | --- | --- | --- | --- |
| `raj-patel-techlead` | Tech Lead — decomposes projects, forms teams, sole Workflow initiator | fable | auto | memory |
| `maya-rodriguez-principal` | Principal Engineer — escalation sink for hard debugging/perf/algorithms | fable | auto | gated, worktree, memory |
| `james-mitchell-service-implementation` | Service Implementation — backend/API build-out | sonnet | acceptEdits | gated, worktree |
| `ethan-kumar-data-architect` | Data Architect — schemas, data models, pipelines | opus | auto | gated |
| `priya-sharma-frontend-implementer` | Frontend Implementer — builds approved designs in React/TS | sonnet | acceptEdits | gated, worktree |
| `coco-laurent-frontend-designer` | Frontend Designer — designs only, never builds | fable | auto | worktree |
| `zara-ahmad-ml-engineer` | ML Engineer — ML/AI features, one-shot background runs | opus | auto | leaf, gated, background |
| `felix-anderson-devops` | DevOps — CI/CD and infra automation, background passes | sonnet | auto | gated, background |
| `nova-chen-research-engineer` | Research Engineer — prototypes and reproducible benchmarks | opus | auto | worktree, memory |
| `oliver-singh-data-scientist` | Data Scientist — analysis and ML insights | opus | auto | worktree |
| `dexter-cho-harness-eval-engineer` | Harness & Eval Engineer — eval suites and quality gates as code | opus | auto | gated |
| `ava-thompson-testing-evangelist` | Testing Evangelist — authors test suites via TDD | sonnet | acceptEdits | leaf, gated, memory |
| `tess-park-test-runner` | Test Runner — mechanical lint/type/test sweeps, summarized | haiku | acceptEdits | leaf, background |
| `marcus-williams-code-quality` | Code Quality Critic — the independent quality gate | opus | default | critic (write-fenced), memory |
| `nina-petrov-security-champion` | Security Champion — read-only security review | fable | default | critic |
| `kai-raven-adversarial-redteam` | Adversarial Red-Team — PoC exploits in an isolated worktree | opus | default | leaf, worktree |
| `penelope-sterling-aesthetic-evaluator` | Aesthetic Evaluator — design and build-vs-design judgment | fable | default | leaf, critic (write-fenced), memory |
| `sam-taylor-specification` | Specification Expert — DESIGN.md, requirements, Notion | sonnet | acceptEdits | leaf |
| `ada-bishop-initializer` | Project Initializer — run-once bootstrap | sonnet | acceptEdits | leaf |
| `taylor-kim-workflow-optimizer` | Workflow Optimizer — meta-review of agents/skills, proposes diffs only | opus | auto | leaf, background, memory |

Each agent's `## Collaboration` section is the authoritative statement of its own delegation edges; this README is the reference summary.

## Delegation topology

Spawn edges (the `Agent` tool channel — who dispatches whom as a subagent):

```
raj-patel-techlead (initiator; forms Agent Teams; ×N priya fan-out; final marcus gate)
  └── any registered agent
james-mitchell ──► maya (escalation), nina (security consult), tess
ethan-kumar   ──► tess
maya-rodriguez ─► nina (critic), tess
coco-laurent  ──► penelope (design sign-off)
priya-sharma  ──► penelope (fidelity check), tess
oliver-singh  ──► marcus (optional review)
nova-chen     ──► marcus (prototype review), tess
felix-anderson ► marcus, nina, tess; escalates to maya
dexter-cho    ──► tess
marcus-williams ► nina (security depth), kai (adversarial proof)
nina-petrov   ──► kai
```

Leaf agents (explicit `tools` list omitting `Agent` — cannot spawn): `ava`, `zara`, `taylor`, `sam`, `ada`, `penelope`, `kai`, `tess`. They delegate through the team channel instead.

Team hand-off edges (the SendMessage channel inside an agent team, `A → B: trigger`):

```
james → marcus: implementation complete, before commit (gate)
marcus → james: gate failure, with findings
marcus → lead:  gate pass, or 2 rounds exhausted
ava → james/priya: coverage gap found mid-implementation
ava → tess (via lead): sweep execution
coco → priya (via lead): approved design handoff
priya → penelope: build complete, fidelity check
ethan ↔ oliver: schema design ↔ data-profiling consults
zara → ethan/oliver (via lead): data questions
dexter ↔ ava: test-strategy/harness alignment
dexter ↔ marcus: gate-charter alignment
sam → lead: spec delivery, routed to implementers
ada → raj: bootstrap complete
any producer → maya: blocked on a hard technical problem
any agent → main agent: Workflow launch request (see SUBAGENT.md)
```

Note: an `Agent(name)` parenthetical allowlist binds on the main session thread only — a spawned agent holding the `Agent` tool can technically spawn any registered agent. The edges above are design intent, enforced by each agent's own instructions; true leaves are enforced by tool-list omission.

## Team shapes

- **Warm core** (trusting, low-friction hand-offs): raj, marcus, ava, james, dexter.
- **On-demand specialists**: maya, ethan, nina, nova, oliver, coco, priya, penelope, kai, sam, ada.
- **Background** (one run per spawn): felix, zara, taylor.
- **Mechanical**: tess.

## Gates

- **Gated producers** (embedded prompt-type routing Stop gate, verbatim in each definition; 2-round cap): maya, ava, james, ethan, felix, zara, dexter, priya. The gate is a single tool-less prompt hook that checks the producer's final message: if code changed and no `REVIEWED: marcus verdict=<ok|blocked> round=<n>` attestation is present, it blocks the stop with routing instructions — send the diff to marcus as a live teammate via SendMessage, spawn `marcus-williams-code-quality` via the Agent tool, or ask the main agent to relay the review — then attest his verdict and stop again. Pure-analysis output passes on first stop; an unreachable reviewer or a spent 2-round budget releases the gate rather than deadlocking. `oliver` is deliberately ungated — exploratory analysis isn't production code; his work passes through marcus only when it graduates.
- **Write-fenced critics** (PreToolUse fence): marcus, penelope — may only write to their agent-memory dir or review reports.

## Team operation

- The main session works team-first: it initiates an agentic team for any non-trivial task, hands each task to the owning specialist and its team (coding is always raj's), and keeps teammates warm while their context stays under 75% of the window (see `CLAUDE.md`).
- Subagents never launch the `Workflow` tool: they compose the complete tool input and SendMessage it to the main agent, which launches it and replies with the result (see `SUBAGENT.md`). Plans authored by a specialist in plan mode flow back to the main agent the same way for ExitPlanMode presentation.

## Notes

- The copy-install into `~/.claude/agents/` is load-bearing for the hooks: Claude Code honors `hooks`, `permissionMode`, and `mcpServers` frontmatter only for agents in `~/.claude/agents/` / `.claude/agents/` — agents registered via a plugin ignore those fields. Do not convert the roster to plugin-registered agents, or every embedded gate and fence goes dead.
- `zara-ahmad-ml-engineer` uses the `theriety:build-service` skill — it requires the plugin whose manifest name is `theriety` (this marketplace registers it under the entry name `backend`; the manifest-vs-marketplace name mismatch is known).
- Agent definitions are intentionally single self-contained files (the install step copies them to `~/.claude/agents/`, so they can't reference plugin-relative shared files) — this is why the routing Stop gate is embedded verbatim in all eight gated producers, diverging from the governance stitch-pipeline template.
- Standards references (`SD-*`) in the definitions never use literal plugin paths — they name a standard plus its owning plugin's constitution, resolved at runtime against the `Root Path` each standards plugin announces under "Plugin Constitution" in the subagent start context. This works because this plugin declares `coding`, `web`, `react`, and `backend` as dependencies, so their SubagentStart constitution hooks run for every spawned agent.
