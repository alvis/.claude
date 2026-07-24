# Claude Code Plugin Marketplace

Nine composable plugins that turn Claude Code into a disciplined engineering
(and production) team: specifications with real provenance, plans with stable
task identity, execution state that survives crashes and machine moves, and
decisions that never silently rewrite history. This README explains how the
system thinks and how to get the most out of it; each plugin's own
`README.md` documents its skills in depth.

## How the system thinks

Everything in this marketplace is built around one observation: **long-running
AI work fails less from missing memory than from stale memory** — an agent
that remembers yesterday's plan perfectly and doesn't notice the world moved.
The system therefore separates six kinds of truth and refuses to let one
impersonate another (`plugins/essential/references/truth.md`):

| Kind | Question it answers | Lives in |
| --- | --- | --- |
| Contract | What are we trying to make now? | `goal.md` charters, canonical specs |
| Decision | Why this, and what replaced the old choice? | decision records, ADRs |
| Execution state | What is happening right now? | `.engineering/` work state |
| Evidence | What was verified, against which exact inputs? | task evidence, reviews, receipts |
| Artifact | What was actually produced? | outputs named by revision or hash |
| Memory | What reusable lesson may help later? | agent memory |

Five rules are constitutional:

1. Never edit an accepted decision into its replacement — supersede it.
2. Never approve an artifact without naming its exact revision.
3. Never treat `done` as synonymous with `current` — status is history,
   validity is now.
4. Every derived artifact names the inputs it was derived from.
5. Deleting `.engineering/` must never erase anything consequential.

Practical consequences you will see day to day:

- **`.engineering/` is an operational projection, not the record of record.**
  It is ignored, per-worktree working memory — rich, continuously persisted,
  and reconstructible. Accepted decisions, approvals, and published artifact
  identities also live in versioned `docs/`, external anchors (issue, PR,
  Notion), and compact checkpoints published to those anchors.
- **Completed work stays completed.** When a decision or spec change
  invalidates a finished task, its row keeps `✓ done` and gains
  `validity: stale (<reason>)`; new remediation tasks carry the rework. The
  system recomputes only what the changed truth touched instead of restarting
  everything — and history is never falsified.
- **Approvals bind to exact revisions.** "Approved" names the artifact, its
  hash or immutable revision, the reviewer, and the scope. An approval of v7
  never silently carries to v8.
- **Concurrency is technical, not social.** One coordinator per work stream
  holds an on-disk lease (`engineering-lease`); state writes are atomic and
  bump a monotonic `State revision`; an append-only journal records causality
  so drift between tables is settled by evidence, not guesswork. A small
  read-only `engineering-doctor` catches structural defects (cycles,
  dangling dependencies, contradictory statuses) without ever judging prose.
- **Context is revealed progressively.** Only the tiny `CLAUDE.md` /
  `MAINAGENT.md` / `SUBAGENT.md` entry points are injected into every
  session. Contracts load on demand at the moment they matter, so agents
  spend context on your work, not on ceremony.

## Install

```bash
cd /path/to/target-project
claude plugin marketplace add alvis/.claude --scope project
claude plugin install specification@alvis --scope project
```

`specification` is the recommended end-to-end bundle; its declared
dependencies install `coding` and `essential`. After installation, ask Claude
to run `/essential:install-agents`, restart the session, and run
`/reload-plugins` after marketplace updates.

| Scope | Use |
|---|---|
| `local` | Try the plugin privately in one target checkout. |
| `project` | Record the plugin for collaborators in the target project. |
| `user` | Enable it for the current developer across projects. |

Project scope writes marketplace and enabled-plugin declarations to the
target's `.claude/settings.json`; review before committing. Keep
`NOTION_TOKEN` and every other credential out of project settings and version
control.

The core lifecycle expects Claude Code, Bash, `jq`, Git, and Python 3, plus
the target project's own build and test tools. The publication path
additionally expects an authenticated `gh` and a jj-colocated Git repository.
Notion synchronization is optional — see
[the specification plugin README](plugins/specification/README.md) for its
transport-profile requirements.

## The lifecycle, end to end

A work stream is born, executes, and retires through one continuous
discipline:

1. **Bootstrap.** The PM confirms a stable work ID, the resolver enforces the
   `.engineering/` ignore gate, and a no-clobber bootstrap creates the
   charter (`goal.md`), state (`state.md`), focus pointer
   (`state/working.md`), and journal.
2. **Charter.** `goal.md` owns the goal, scope, and numbered success criteria
   (`SC-1`…) with expected evidence — so status churn can never drift the
   definition of done. It also declares the stream's workspace anchors
   (a git worktree by default; media projects and asset stores for
   production work).
3. **Lease.** The coordinator acquires the stream's on-disk lease before any
   state write. Two sessions can never both believe they own a stream; an
   expired lease yields only to an explicit, journaled takeover.
4. **Specify and plan.** Specs carry provenance and approval binds to exact
   content; plans are task tables with stable three-letter IDs, explicit
   dependency graphs, and per-task acceptance. Plan approval is a checkpoint.
5. **Execute.** Every status change is journaled first, then reconciled into
   the tables ("append first, reconcile second"). Workers return evidence
   with their `capability_id`; only the lease holder writes state.
6. **Decide.** Decisions record what they supersede, affect, invalidate, and
   preserve. Acceptance triggers a blast-radius sweep that marks stale work
   and spawns remediation — and emits a checkpoint.
7. **Review and approve.** Seven canonical review areas; every approval
   carries the full binding tuple. Spec freshness is re-checked at named
   moments (before planning, each dispatch batch, review, completion).
8. **Pause and resume.** `essential:handover` persists everything and emits a
   portable receipt; `essential:takeover` resumes locally or rehydrates the
   receipt on another machine, checks the lease, and drives streams to
   their success criteria (`essential:doctor` owns structural audits).
9. **Promote and retire.** Stable knowledge promotes to versioned `docs/`
   with provenance; every accepted decision gets an explicit disposition
   (promote to ADR / product / production record, retain in receipt, or
   archive); a retirement checkpoint lands; only then is the operational
   projection deleted.

### Golden development lifecycle

| Stage | Developer action | Owner and gate |
|---|---|---|
| 1. Start | Name the target repository, tracker-derived work ID, scope, and success criteria. | The PM resolves one workspace-local work root and bootstraps it only after the ignore gate. |
| 2. Discover | Run `/essential:discover` for blind spots, references, or a disposable prototype. | Discovery records evidence separately from its marked `DSC01`-style task graph and says whether the work is ready for a decision. |
| 3. Decide | Run `/essential:decide` only when material alternatives need a choice. | After approval, Decide records the decision with its causal metadata and invokes the selected next owner itself. Do not invoke that owner a second time. |
| 4. Specify | If no prior Decide handoff already invoked it, run `/specification:spec-code` with one explicit local, inline, or Notion source and a capability slug. | Approve the exact specification content, confirmed by direct comparison. A transport mirror is never the authored source. |
| 5. Plan | Run `/specification:plan-code` against that specification. | Approve the task definitions and dependency graph recorded in `state.md` before implementation; changing them later requires reapproval. |
| 6. Implement | Run `/specification:implement-code --defer-publication` when you want the manual save/finalize/publish stops shown below; use `/coding:write-code` directly only for a non-specification coding task. | Execute only dependency-ready leaf task IDs using target-native tests. Child writers return status evidence; the coordinator alone reconciles work state. |
| 7. Document | Let implementation invoke `/coding:document` when public behavior, configuration, operations, or developer workflow changed. | Documentation finishes before review and save-manifest sealing. |
| 8. Review, lint, and repair | Let implementation run review, fixes, touched-scope lint, and final target-native checks. | All findings block closure. A correction reruns affected tests/reviews. |
| 9. Reconcile the spec | Let implementation run the applicable Notion completion gate or local source/carrier recheck. | A change in specification content invalidates plan/code/review evidence; done tasks keep their status and gain stale validity with remediation tasks. |
| 10. Save and finalize | On deferred `needs_save`, run the exact returned `/coding:commit --paths-from=... --manifest-sha256=...`; on `ready_for_finalization`, skip save; on `no_change`, stop. Then `/coding:finalize-commits` once. | The closed-set save preserves unrelated staged and dirty developer work. |
| 11. Publish | If no PR was already published, run `/coding:push-pr` only when GitHub, `gh`, and jj prerequisites are satisfied. | It creates or updates draft PRs and monitors CI. A human decides when a green draft becomes ready. |
| 12. Close or transfer | Mark the work complete after acceptance, decision dispositions, and the retirement checkpoint, or run `/essential:handover`. | Every required executable leaf must be done. `.engineering/` is not the transfer mechanism. |

When the target is a standalone or non-TypeScript repository, verify each
selected skill against the repository's native commands before use.

### Five-minute local-spec path

Use a lowercase tracker-derived ID that will remain stable, such as
`eng-421-checkout-refunds`:

```text
/essential:discover "Find delivery blind spots for checkout refunds" --work-id=eng-421-checkout-refunds --mode=blindspots --persist
/specification:spec-code "Design idempotent checkout refunds from these requirements" --work-id=eng-421-checkout-refunds --capability=checkout-refunds
/specification:plan-code --work-id=eng-421-checkout-refunds --spec=docs/specs/checkout-refunds/index.md
/specification:implement-code docs/specs/checkout-refunds/index.md --work-id=eng-421-checkout-refunds --repo=/absolute/path/to/target-project --defer-publication
```

This path avoids Notion and remote publication entirely. It leaves verified
code, work-local evidence and reviews, and durable specification documents.
The deferred result tells you what remains (`needs_save`,
`ready_for_finalization`, or `no_change`); follow stage 10 above. Add Notion
or PR publication only after the local flow is understood.

## The plugins

| Plugin | What it owns | README |
|---|---|---|
| `essential` | The engineering-work lifecycle backbone: truth model, work state, lease, journal, doctor, checkpoints, handover/takeover, research and decision skills, agent installer. Every other plugin depends on it. | [plugins/essential](plugins/essential/README.md) |
| `specification` | Specs with provenance: authoring, planning, implementation orchestration, seven-area review, and safe Notion synchronization. | [plugins/specification](plugins/specification/README.md) |
| `coding` | General code production: TDD write/fix/refactor, scoped saves, stacked PRs, lint, docs, cleanup. | [plugins/coding](plugins/coding/README.md) |
| `governance` | The meta-layer: creating and verifying agents, skills, and standards. | [plugins/governance](plugins/governance/README.md) |
| `backend` | Theriety-specific service and data orchestrator build/audit (manifest name `theriety`). | [plugins/backend](plugins/backend/README.md) |
| `client` | Client-facing screen-design contracts with Notion integration. | [plugins/client](plugins/client/README.md) |
| `react` | React/JSX standards routing over the shared coding workflows. | [plugins/react](plugins/react/README.md) |
| `web` | Web UX design, audits, imaging, Next.js diagnosis, Storybook checks. | [plugins/web](plugins/web/README.md) |
| `production` | Media/creative production: asset provenance, render manifests, revision-bound review. | [plugins/production](plugins/production/README.md) |

## Work state, handover, and recovery

- `.engineering/works/<work-id>/` is ignored, workspace-local coordination
  memory — an operational projection, never a backup or transfer mechanism.
- `working.md` is the short current-focus pointer; `state.md` is the complete
  lifecycle, plan, task graph, and evidence index; `state/journal.md` is the
  append-only causal record the tables are views over.
- Tasks use stable IDs (`LFE`, `LFE01`) that are never renamed or reused;
  removed scope becomes a cancelled tombstone. Every task shows a mark and
  word (`- planned`, `⧗ working`, `✓ done`, `X failed`, `! blocked`,
  `⊘ cancelled`); validity is a separate dimension.
- To pause, run `/essential:handover`; to resume, `/essential:takeover`
  (locally, or with a receipt on another machine). Never claim a handover is
  portable while code exists only as an uncommitted working copy.
- Full detail, including the lease and doctor tools:
  [plugins/essential/README.md](plugins/essential/README.md).

## Agent team

A 23-agent team for Claude Code organized into a main-session Project Manager, domain leads, and their teammates. Shared operation lives in `plugins/essential/CLAUDE.md` and `MAINAGENT.md`, subagent conduct including the Workflow-proxy protocol lives in `plugins/essential/SUBAGENT.md`, owner-specific routing lives in each contributing plugin's `CLAUDE.md`, and per-agent delegation topology lives in each agent definition.

Install via the `essential:install-agents` skill (ask Claude to "install the agents"). Canonical sources live under `plugins/<owner>/templates/agents/<name>/` as `base.md` plus `frontmatter/claude.json`. The installer discovers source-checkout siblings or enabled same-marketplace plugins, validates the complete discovered roster, stages stitched files, and copies them into `~/.claude/agents/`. It overwrites current same-named discoveries and leaves unrelated or stale files untouched. Edits require a re-install, and changes take effect in the next session.

### Roster

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

### Delegation topology

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

### Team shapes

- **Domain leads**: `tech-lead` for coding delivery, `design-lead` for design delivery, and `ai-research-lead` for research delivery.
- **Warm-core specialists** (trusting, low-friction hand-offs): `code-quality-critic`, `testing-evangelist`, `service-implementation-engineer`, `generalist-engineer`, `harness-eval-engineer`.
- **On-demand specialists**: `principal-engineer`, `data-architect`, `frontend-designer`, `frontend-implementer`, `desktop-implementer`, `mobile-implementer`, `ml-engineer`, `security-champion`, `aesthetic-evaluator`, `adversarial-red-team`, `specification-expert`, `project-initializer`.
- **Background** (one run per spawn): `devops`, `workflow-optimizer`.
- **Mechanical**: `test-runner`.

### Gates

- **Gated producers** (embedded prompt-type routing Stop gate; 2-round cap): `principal-engineer`, `testing-evangelist`, `service-implementation-engineer`, `data-architect`, `devops`, `ml-engineer`, `harness-eval-engineer`, `frontend-implementer`, `generalist-engineer`, `desktop-implementer`, `mobile-implementer`. Each gate checks the producer's final message for the generic `REVIEWED: source=<specialist|general|external|none> reviewer=<agent-id|tool-name|none> verdict=<ok|blocked|unavailable> round=<n>` attestation and requests review through a known reviewer `agent_id` or the main agent.
- **Write-fenced critics** (PreToolUse fence): `code-quality-critic`, `aesthetic-evaluator` — may only write to their agent-memory dir or review reports.

### Team operation

- Works team-first: The Project Manager initiates the team, appoints domain leads, and handles staffing and user/session proxies. Each lead gathers teammate advice, decomposes its assigned work, owns the domain's implementation decisions, assigns and monitors the pieces across its team, and reconciles delivery. `plugins/essential/CLAUDE.md` carries shared operation rules; each owner plugin's `CLAUDE.md` carries only its task-to-specialist rows.
- Subagents reply to the assigning teammate's `agent_id`. Roles and configured names are never direct-message addresses. For continuing work they message the best-known teammate directly when they have its ID, ask the main agent to resolve the ID when the teammate is known, and ask the main agent to suggest a warm peer by folder/feature history or spawn a new named teammate only when they cannot identify the owner.
- Subagents never launch the `Workflow` tool: they compose the complete tool input and SendMessage it to the main agent, which launches it and replies with the result (see `plugins/essential/SUBAGENT.md`). Plans authored by a specialist in plan mode flow back to the main agent the same way for presentation.

### Notes

- The copy-install into `~/.claude/agents/` is load-bearing for the hooks: Claude Code honors `hooks`, `permissionMode`, and `mcpServers` frontmatter only for agents in `~/.claude/agents/` / `.claude/agents/` — agents registered via a plugin ignore those fields. Do not convert the roster to plugin-registered agents, or every embedded gate and fence goes dead.
- `ml-engineer` uses the `theriety:build-service` skill — it requires the plugin whose manifest name is `theriety` (this marketplace registers it under the entry name `backend`; the manifest-vs-marketplace name mismatch is known).
- Installed agent definitions are intentionally single self-contained files even though their canonical source is split. This is why the routing Stop gate is embedded verbatim in all eleven gated producers.
- Standards references (`SD-*`) in the definitions never use literal installation paths. They name a standard plus its owning plugin constitution, resolved at runtime when that plugin is enabled. A partial enabled roster is valid, so cross-plugin handoffs and context are best-effort when their owner plugin is absent.

## Completion checklist

- The work ID, repository, and authoritative specification source are
  unambiguous.
- Specification approval names the exact specification content; plan and
  review track task definitions directly from `state.md`, with reapproval on
  any change.
- Every stable task ID and edge in `state.md` is accounted for, with no cycle
  or contradictory parent roll-up (`engineering-doctor` confirms), and every
  required executable leaf is `✓ done` with current validity.
- Target-native tests, lint, type checks, and builds pass where applicable.
- Canonical review artifacts have no outstanding findings; approvals carry
  their full binding tuples.
- Notion reconciliation and verification completed when the specification is
  Notion-backed.
- Durable docs match delivered behavior; every accepted decision has its
  completion-gate disposition; checkpoints exist at the external anchor.
- Acceptance, receipts, and final work-state status are recorded before
  cleanup.

## Validation

```bash
claude plugin validate --strict .
python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py .
```

Useful references: [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [plugin installation and scopes](https://code.claude.com/docs/en/discover-plugins), and [plugin reference](https://code.claude.com/docs/en/plugins-reference).
