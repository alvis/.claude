# Claude Code Plugin Marketplace

Eight focused plugins provide composable Claude Code skills. Plugin manifests and each skill's `SKILL.md` are the source of truth; this file is generated.

## Install

```bash
claude plugin install ./plugins/<plugin>
```

Dependencies are declared in each plugin's `.claude-plugin/plugin.json`; installing a dependent plugin enables its required providers automatically.

## Plugins and skills

### coding (depends on: essential)

General code writing tools including quality checks, testing, architecture, and implementation support

- `coding:cleanup` — Audit stale development state across git branches, remote branches, git worktrees, and jj workspaces. Use when a user asks to run /cleanup, find abandoned branches/workspaces, or safely remove already-merged or duplicate local work with backups and confirmation.
- `coding:commit` — Save code changes cleanly with jj-first, git-compatible routing. Use for commits, split/absorb/edit operations, stacked changes, history reordering, retrospective blame fixes, or the --create-pr compatibility handoff; preserve the repository history policy and keep coding:commit as the sole history-mutation owner.
- `coding:complete-code` — Complete explicit production implementation stubs in an existing scope. Use for canonical implementation TODOs, temporary production stubs, and draft-code sentinels; route bugs, test work, unstubbed functionality, new features, and ambiguous markers to their owning workflows.
- `coding:complete-test` — Author and improve tests for pending test cases, coverage gaps, fixtures, and redundancy cleanup. Use for test TODOs, it.todo or describe.todo entries, explicit test-writing requests, or coverage work. Production implementation stubs belong to complete-code; diagnosed failures belong to fix.
- `coding:document` — Create or update a package README and optional ARCHITECTURE.md from the actual implementation. Use after meaningful code changes, when docs are missing or stale, or when a package needs a source-backed structure overview. Preserve existing project voice and route specification documentation to specification skills.
- `coding:draft-code` — Draft TypeScript-compliant code skeletons with canonical TODO(implementation) placeholders. Use when starting an already-specified implementation or preparing typed production structure for later completion; do not implement business logic or create ambiguous plain TODO markers.
- `coding:finalize-commits` — Run isolated per-commit QA across every unpushed commit, report ordering or message issues, and coordinate approved corrections. Use before publishing a stack; coding:commit owns history mutations and coding:push-pr owns publication.
- `coding:find-unused` — Perform read-only dead-code discovery for commented-out code, unused symbols, and unused test helpers. Use when identifying removal candidates; report evidence without deleting, refactoring, linting, or otherwise modifying the inspected source.
- `coding:fix` — Fix diagnosed incorrect behavior, failed tests, type errors, lint failures, or broken CI. Use when a concrete failure can be reproduced or review findings identify a defect; route new functionality to write-code and green structural cleanup to refactor.
- `coding:handover` — Persist CONTEXT.md, NOTES.md, and PLAN.md for later continuation of coding work. Use when pausing implementation or transferring repository state; this skill records the current session and does not create or execute a cross-domain plan.
- `coding:lint` — Enforce coding standards mechanically across a selected scope with batched linters and independent reviewers. Use when source files need lint-error correction, standards enforcement, or consistent formatting, including calls extended by another plugin's portable lint profile; behavior-changing repairs belong to fix.
- `coding:merge-pr` — Merge a linear stack of GitHub pull requests while restacking descendants between merges. Use when a user invokes /merge-pr with PR numbers, asks to merge stacked PRs, or needs gh-driven bottom-up PR merging with automatic downstream rebase.
- `coding:modernize` — Apply version-supported syntax and API upgrades based on the project runtime and toolchain. Use when replacing legacy constructs with supported modern equivalents; do not claim general refactoring, dependency upgrades, or behavioral feature work.
- `coding:push-pr` — Publish saved changes as draft pull requests and drive GitHub CI to green. Use when asked to push the latest commit, create or update a PR, repush after a fix, babysit pending checks, repair red CI, monitor every check, or converge a PR stack.
- `coding:refactor` — Improve green code through behavior-preserving structural changes to organization, naming, readability, or documentation. Use when existing tests pass and the requested outcome is maintainability rather than a bug fix, new feature, or version-driven API upgrade.
- `coding:review-code` — Review semantic correctness, security, test intent, documentation, sibling consistency, and alignment with the implementation plan. Use after code changes or for explicit review requests; report findings without editing code and leave mechanical standards enforcement to lint.
- `coding:setup-project` — Ensure project structure exists before development, creating barebone scaffolding only if needed. Use when initializing new projects, validating project setup, or ensuring monorepo component structure.
- `coding:sync-tool` — Install or update registered coding CLI tools (brew, jj, gh, fallow, python) across macOS, Linux, and Windows. Use when tools are missing, stale, or needed on PATH for a sibling skill, including requests to install jj/gh/brew, update coding tools, or verify CLI dependencies before work.
- `coding:takeover` — Resume paused coding work from CONTEXT.md, NOTES.md, and PLAN.md. Use for takeover, continuing yesterday's coding work, resuming a continuation bundle, or --revalidate; trust recorded assumptions for 24 hours, revalidate older state, and invoke coding:write-code --resume. For saving current state, use the session-persistence workflow.
- `coding:write-code` — Write production-ready code end to end through a TDD lifecycle of design, skeleton, implementation, tests, and refactoring. Use for new functions, features, modules, components, CLI or API endpoints, or approved tickets; route diagnosed failures to fix and explicit production stubs to complete-code.
- `coding:write-pr` — Author a conventional-commit PR title and unified body from a jj or git change ref, emitting output for gh pr create. Use for PR descriptions, draft pull requests, stacked coding:push-pr PR bodies, and callers that need a unified title/body template from a commit.

### essential

Documentation creation, code design, product strategy, and Notion integration for knowledge management

- `essential:autoresearch` — Run a metric-driven research loop: define a metric, evaluator, baseline, and target; evolve candidate solutions; score and adversarially verify them; then mutate survivors until the target, budget, or plateau ends the run. Use for measurable optimization of prompts, code, experiments, or creative variants; use deep-research for fact-finding.
- `essential:decide` — Decides between researched approaches before implementation. Use when asked to choose an approach, challenge a recommendation, make an architecture decision, compare options, define rollback and falsification signals, or obtain approval; routes blindspot passes, brainstorms, interviews, references, and prototypes to essential:discover.
- `essential:deep-research` — Conduct comprehensive multi-source research with AI-assisted analysis and explicit source synthesis. Use when investigating complex topics, comparing evidence, gathering current information, or producing a fact-finding report with citations and uncertainty notes. Do not use for metric-driven candidate optimization.
- `essential:discover` — Discovers material unknowns before planning. Use for a blindspot pass or unknown unknowns, to brainstorm approaches from cheapest to ambitious, interview about architecture, extract reference implementation semantics, make a disposable prototype before touching the real app, or check whether discovery is ready for a decision; researched option selection belongs to essential:decide.
- `essential:handoff` — Create or execute a context-complete cross-domain plan as an orchestrator. Use when another agent must continue without prior context, or when a multi-domain plan needs coordinated execution while this skill retains decision ownership. For coding-session persistence, use coding:handover.
- `essential:install-agents` — Discover, validate, stitch, and install specialist agent templates contributed by Essential and other enabled plugins in the same marketplace. Use when asked to install agents, set up subagents, refresh the agent team, or configure Claude Code on a new machine.
- `essential:install-statusline` — Install the bundled Bullet Train statusline into ~/.claude and wire settings.json statusLine. Use when setting up Claude Code on a new machine, installing or restoring the statusline, or repairing its configuration; preserve the bundled executable and report permission or platform limitations.

### governance (depends on: essential)

Tools for creating and managing Claude Code configuration files including commands, skills, standards, and agents

- `governance:create-agent` — Creates a new specialist agent as two stitched source files, base.md plus frontmatter/claude.json, proposing model, effort, and permissions by role archetype and confirming them with the user before writing. Use when adding a new subagent, defining a new specialist role, scaffolding an agent definition, or when update-agent hands off new-agent creation.
- `governance:create-skill` — Use when creating a reusable Claude Code skill, defining a new repeatable agent capability, or replacing a one-off workflow with discoverable instructions that need clear ownership, validation, and trigger behavior.
- `governance:create-standard` — Create a new technical standard at a plugin's canonical constitution/standards root using meta.md, scan.md, write.md, and per-rule guides. Use when establishing new coding standards, documenting technical requirements, or creating compliance guidelines for reusable policy with explicit dependencies, detection, compliant patterns, and stable rule IDs. Route existing-standard revisions to update-standard.
- `governance:update-agent` — Update explicitly selected agent definitions to the current two-file template or a stated behavior change while preserving useful role expertise, trigger boundaries, context, collaboration links, and working voice. Use when migrating agents to a template revision, correcting agent configuration, or batch-updating selected agents; require an exact selector and route genuinely new roles to create-agent.
- `governance:update-skill` — Use when revising one or more existing Claude Code skills, aligning skill instructions with current repository policy, narrowing overlapping ownership, or applying a deliberate behavior change without creating a competing skill.
- `governance:update-standard` — Update explicitly selected plugin standards to the current meta.md, scan.md, write.md, and rules contract while preserving valid policy and stable rule IDs. Use when applying scoped rule changes, migrating standards to a template revision, or batch-updating the standards library. Require a path, glob, or --all; route missing targets to create-standard.
- `governance:verify-skill` — Use when validating a new or changed Claude Code skill, checking structural and repository policy compliance, reasoning through representative trigger and behavior cases, or optionally exercising isolated runtime prompts before deployment.

### react (depends on: coding, essential)

React component development with UI implementation, design systems, Next.js expertise, and fullstack capabilities

- `react:lint` — Use when React JSX, components, hooks, accessibility, project structure, tests, or Storybook files need mechanical standards enforcement through the shared Coding lint workflow; React owns framework rules while Coding owns generic execution and reporting.
- `react:react` — Use when creating, editing, reviewing, or routing work involving React, JSX, hooks, components, accessibility behavior, project structure, tests, or Storybook stories; this router selects React standards while Coding owns generic execution.

### specification (depends on: coding, essential)

Design specifications, architecture specs, requirements gathering, and technical documentation with Notion integration for knowledge management

- `specification:implement-code` — Execute an approved specification ticket from authoritative contract through implementation, review, and commit planning. Use after plan-code approval, when resuming partial ticket work, or when auditing a delivered ticket. Keep contract authoring in spec-code and generic feature work in coding:write-code.
- `specification:mdc` — Read, edit, and author MDC (Contextual Markdown, @theriety/mdc) files safely with native text tools. Use when asked to "edit this .mdc file", "add a block to <doc>.mdc", "update the annotation for ref <x>", "convert this to MDC", whenever a .mdc file must be read or written, or when mutating any file under .code-spec/.
- `specification:plan-code` — Generate DRAFT.md as a commit blueprint and PLAN.md as an execution roadmap from an approved proposal or specification. Use when planning implementations, defining atomic commits, documenting change proposals, or preparing a coding workflow with explicit verification and ownership boundaries.
- `specification:review-implementation` — Review an implementation against an authoritative local or Notion specification, then run the general coding and security review. Use for specification alignment, delivered-ticket validation, or detecting omissions, drift, and unsanctioned behavior before handoff.
- `specification:spec-code` — Design or document technical specifications in the canonical template, then delegate Notion synchronization to sync-notion. Use for greenfield specs, updates to an existing DESIGN.md, or documenting an implementation without inventing requirements.
- `specification:sync-notion` — Synchronize one or more paired Markdown files and Notion pages in a declared direction. Use when local documentation must be published, remote pages must be materialized locally, or both sides require an explicit conflict-resolved merge. Keep specification authoring in spec-code.
- `specification:sync-spec` — Materialize a guaranteed-on-disk Notion specification tree as a flat `.code-spec/` bundle of `{kebab-title}-{32hex-id}.md` files plus `.gitignore`. Use before downstream analysis or code generation, when refreshing a stale bundle, or when a ticket requires local spec evidence; fail unless the root id-suffix file exists and is non-empty.

### web (depends on: coding, essential)

Web development tools including UX design, growth optimization, rapid prototyping, browser automation via agent-browser, Next.js debugging via Chrome DevTools, and design auditing

- `web:audit` — Audit a rendered web interface against the design standard with the bundled deterministic CLI, shared-browser evidence, responsive viewports, accessibility checks, and focused visual adjudication. Use for design QA, WCAG checks, visual review, or launch assessment. Produce reports and evidence only; route fixes to the owning implementation skill.
- `web:css` — Scaffold or maintain a project's root stylesheet using the CSS-only light, dark, and system color-mode contract. Use for theme.css, globals.css, or app.css setup, migration from class-driven dark mode, semantic token wiring, or color-mode corrections. Detect conflicts, obtain migration approval, preserve existing tokens, and edit CSS only.
- `web:design` — Design or redesign a web interface — and implement it when authorized — with coherent visual direction, responsive layout, typography, color, motion, and accessible states. Maintains a .design task workspace and ranked variant boards, then drives an independent implement-evaluate loop with visual-diff confirmation. Use for new pages, component polish, mockups, or facelifts.
- `web:imagine` — Generate or edit images through the bundled multi-provider CLI, or write structured prompts and analyze visual styles from references. Use for concept art, product shots, covers, UI assets, transparent or vector output, inpainting, background changes, batch variants, and prompt-only work. Keep image generation separate from web design decisions and visual audits.
- `web:next` — Diagnose Next.js runtime behavior with next-browser and Chrome DevTools MCP: React components, routes, SSR errors, DOM/styles, performance, Lighthouse, network, device emulation, JavaScript debugging, storage, screenshots, and interactions. Use for evidence-backed browser diagnosis; route visual creation to design and story-state assessment to storybook.
- `web:storybook` — Audit a Storybook instance for setup failures, accessibility violations, interaction errors, and visual regressions across meaningful story states. Use before release or when validating addons and focus behavior. Run the bundled lifecycle in order, preserve evidence, and report findings; do not edit components, stories, or configuration.

### theriety (depends on: coding, specification, essential)

Domain-specific service and data orchestrator lifecycle management for Theriety — build and audit services and data layers

- `theriety:audit-data` — Audit data orchestrators against specifications, generate discrepancy reports, and remediate approved changes. Use when reviewing data domain completeness, checking schema compliance, or performing data layer quality audits.
- `theriety:audit-service` — Audit a backend service against its implementation and documentation contract, producing evidence-backed findings and optionally remediating approved gaps. Use for operation completeness, service quality, or documentation-only audits; choose --scope to keep the review focused.
- `theriety:build-data` — Build complete data orchestrators from spec to commit, including schema setup, operations, controllers, and quality gates. Use when creating new data domains, adding operations to existing orchestrators, or implementing Prisma schemas from Notion.
- `theriety:build-service` — Build complete backend services from spec to commit, including operation declaration, implementation, and quality gates. Use when creating new services, adding operations to existing services, or declaring manifest schemas.

### client (depends on: essential)

Client-facing screen design and UX documentation with Notion integration

- `client:create-screen-design` — Create new responsive screen-design documentation in the canonical Notion Screens database for a named product and screen. Use when a product needs a new UX contract, layout alternatives, interaction states, or handoff notes. Preserve the live template and database relations; route existing-page changes to update-screen-design.
- `client:update-screen-design` — Update explicitly selected responsive screen-design pages in the canonical Notion Screens database while preserving approved content and applying a template migration or stated change. Use for scoped revisions and accessibility corrections. Require a selector or --all; route missing/new pages to create-screen-design.

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

## Validation

```bash
claude plugin validate --strict .
python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py .
```

Run `python3 scripts/generate_readme.py --check` to confirm this inventory is current.
