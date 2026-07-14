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
- `coding:modernize` — Apply version-supported syntax and API upgrades based on the project runtime and toolchain. Use when replacing legacy constructs with supported modern equivalents; do not claim general refactoring, dependency upgrades, or behavioral feature work.
- `coding:push-pr` — Publish saved changes as draft pull requests and drive GitHub CI to green. Use when asked to push or update a PR, babysit pending checks, repair red CI, or converge every PR in a stack.
- `coding:refactor` — Improve green code through behavior-preserving structural changes to organization, naming, readability, or documentation. Use when existing tests pass and the requested outcome is maintainability rather than a bug fix, new feature, or version-driven API upgrade.
- `coding:review-code` — Review semantic correctness, security, test intent, documentation, sibling consistency, and alignment with the implementation plan. Use after code changes or for explicit review requests; report findings without editing code and leave mechanical standards enforcement to lint.
- `coding:setup-project` — Ensure project structure exists before development, creating barebone scaffolding only if needed. Use when initializing new projects, validating project setup, or ensuring monorepo component structure.
- `coding:sync-tool` — Install or update registered coding CLI tools (brew, jj, gh, fallow, python) across macOS, Linux, and Windows. Use when tools are missing, stale, or needed on PATH for a sibling skill, including requests to install jj/gh/brew, update coding tools, or verify CLI dependencies before work.
- `coding:takeover` — Resume interrupted implementation from persisted handover documents. Use when CONTEXT.md, NOTES.md, and PLAN.md describe valid continuation state; this adapter validates those inputs and delegates the actual continuation to the standard write-code resume workflow.
- `coding:write-code` — Write production-ready code end to end through a TDD lifecycle of design, skeleton, implementation, tests, and refactoring. Use for new functions, features, modules, components, CLI or API endpoints, or approved tickets; route diagnosed failures to fix and explicit production stubs to complete-code.
- `coding:write-pr` — Author a conventional-commit PR title and unified body from a jj or git change ref, emitting output for gh pr create. Use for PR descriptions, draft pull requests, stacked coding:push-pr PR bodies, and callers that need a unified title/body template from a commit.

### essential

Documentation creation, code design, product strategy, and Notion integration for knowledge management

- `essential:autoresearch` — Run a metric-driven research loop: define a metric, evaluator, baseline, and target; evolve candidate solutions; score and adversarially verify them; then mutate survivors until the target, budget, or plateau ends the run. Use for measurable optimization of prompts, code, experiments, or creative variants; use deep-research for fact-finding.
- `essential:deep-research` — Conduct comprehensive multi-source research with AI-assisted analysis and explicit source synthesis. Use when investigating complex topics, comparing evidence, gathering current information, or producing a fact-finding report with citations and uncertainty notes. Do not use for metric-driven candidate optimization.
- `essential:handoff` — Create or execute a context-complete cross-domain plan as an orchestrator. Use when another agent must continue without prior context, or when a multi-domain plan needs coordinated execution while this skill retains decision ownership. For coding-session persistence, use coding:handover.
- `essential:install-agents` — Discover, validate, stitch, and install specialist agent templates contributed by Essential and other enabled plugins in the same marketplace. Use when asked to install agents, set up subagents, refresh the agent team, or configure Claude Code on a new machine.
- `essential:install-statusline` — Install the bundled Bullet Train statusline into ~/.claude and wire settings.json statusLine. Use when setting up Claude Code on a new machine, installing or restoring the statusline, or repairing its configuration; preserve the bundled executable and report permission or platform limitations.
- `essential:think` — Structure pre-implementation reasoning for ambiguous problems. Use when the requested outcome, constraints, or safe solution are unclear and deliberate options, objections, dependencies, edge cases, and rollback need to be resolved before any modification or creation begins.

### governance (depends on: essential)

Tools for creating and managing Claude Code configuration files including commands, skills, standards, and agents

- `governance:create-agent` — Creates a new specialist agent as two stitched source files, base.md plus frontmatter/claude.json, proposing model, effort, and permissions by role archetype and confirming them with the user before writing. Use when adding a new subagent, defining a new specialist role, scaffolding an agent definition, or when update-agent hands off new-agent creation.
- `governance:create-skill` — Use when creating a reusable Claude Code skill, defining a new repeatable agent capability, or replacing a one-off workflow with discoverable instructions that need clear ownership, validation, and trigger behavior.
- `governance:create-standard` — Create a new technical standard at a plugin's canonical constitution/standards root using meta.md, scan.md, write.md, and per-rule guides. Use when establishing new coding standards, documenting technical requirements, or creating compliance guidelines for reusable policy with explicit dependencies, detection, compliant patterns, and stable rule IDs. Route existing-standard revisions to update-standard.
- `governance:update-agent` — Update explicitly selected agent definitions to the current two-file template or a stated behavior change while preserving useful role expertise, trigger boundaries, context, collaboration links, and working voice. Use when migrating agents to a template revision, correcting agent configuration, or batch-updating selected agents; require an exact selector and route genuinely new roles to create-agent.
- `governance:update-skill` — Use when revising one or more existing Claude Code skills, aligning skill instructions with current repository policy, narrowing overlapping ownership, or applying a deliberate behavior change without creating a competing skill.
- `governance:update-standard` — Update explicitly selected plugin standards to the current meta.md, scan.md, write.md, and rules contract while preserving valid policy and stable rule IDs. Use when applying scoped rule changes, migrating standards to a template revision, or batch-updating the standards library. Require a path, glob, or --all; route missing targets to create-standard.
- `governance:verify-skill` — Use when validating a new or changed Claude Code skill, checking structural and repository policy compliance, testing whether descriptions trigger accurately, or grading representative skill outputs before deployment.

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

A 20-agent specialist team for Claude Code, plus the operating rules that make it work as a team: shared main-session rules in `plugins/essential/CLAUDE.md` and `MAINAGENT.md`, subagent conduct including the Workflow-proxy protocol in `plugins/essential/SUBAGENT.md`, owner-specific routing in each contributing plugin's `CLAUDE.md`, and per-agent delegation topology carried in each agent's own definition.

Install via the `essential:install-agents` skill (ask Claude to "install the agents"). Canonical sources live under `plugins/<owner>/templates/agents/<name>/` as `base.md` plus `frontmatter/claude.json`. The installer discovers source-checkout siblings or enabled same-marketplace plugins, validates the complete discovered roster, stages stitched files, and copies them into `~/.claude/agents/`. It overwrites current same-named discoveries and leaves unrelated or stale files untouched. Edits require a re-install, and changes take effect in the next session.

### Roster

| Agent | Role | Model | Effort | Permission | Flags |
| --- | --- | --- | --- | --- | --- |
| `raj-patel-techlead` | Tech Lead — decomposes projects and routes milestones | fable | medium | auto | memory |
| `maya-rodriguez-principal` | Principal Engineer — escalation sink for hard debugging/perf/algorithms | fable | high | auto | gated, worktree, memory |
| `james-mitchell-service-implementation` | Service Implementation — backend/API build-out | sonnet | medium | acceptEdits | gated, worktree |
| `ethan-kumar-data-architect` | Data Architect — schemas, data models, pipelines | opus | high | auto | gated |
| `priya-sharma-frontend-implementer` | Frontend Implementer — builds approved designs in React/TS | sonnet | high | acceptEdits | gated, worktree |
| `coco-laurent-frontend-designer` | Frontend Designer — designs only, never builds | fable | high | auto | worktree |
| `zara-ahmad-ml-engineer` | ML Engineer — ML/AI features, one-shot background runs | opus | medium | auto | gated, background |
| `felix-anderson-devops` | DevOps — CI/CD and infra automation, background passes | sonnet | medium | auto | gated, background |
| `nova-chen-research-engineer` | Research Engineer — prototypes and reproducible benchmarks | opus | high | auto | worktree, memory |
| `oliver-singh-data-scientist` | Data Scientist — analysis and ML insights | opus | medium | auto | worktree |
| `dexter-cho-harness-eval-engineer` | Harness & Eval Engineer — eval suites and quality gates as code | opus | medium | auto | gated |
| `ava-thompson-testing-evangelist` | Testing Evangelist — authors test suites via TDD | sonnet | medium | acceptEdits | leaf, gated, memory |
| `tess-park-test-runner` | Test Runner — mechanical lint/type/test sweeps, summarized | haiku | — | acceptEdits | leaf, background |
| `marcus-williams-code-quality` | Code Quality Critic — the independent quality gate, day-to-day quality and security review | opus | medium | default | critic (write-fenced), memory |
| `nina-petrov-security-champion` | Security Champion — deep security review, explicit request only | fable | high | default | critic |
| `kai-raven-adversarial-redteam` | Adversarial Red-Team — PoC exploits in an isolated worktree | opus | high | default | leaf, worktree |
| `penelope-sterling-aesthetic-evaluator` | Aesthetic Evaluator — design and build-vs-design judgment | fable | medium | default | leaf, critic (write-fenced), memory |
| `sam-taylor-specification` | Specification Expert — DESIGN.md, requirements, Notion | sonnet | medium | acceptEdits | leaf |
| `ada-bishop-initializer` | Project Initializer — run-once bootstrap | sonnet | low | acceptEdits | leaf |
| `taylor-kim-workflow-optimizer` | Workflow Optimizer — meta-review of agents/skills, proposes diffs only | opus | high | auto | background, memory |

Each agent's `## Collaboration` section records its proven outbound collaborators and delegation targets. These are runtime defaults, not an allowlist; shared discovery and handoff policy lives in `plugins/essential/CLAUDE.md`.

### Delegation topology

Spawn edges (the `Agent` tool channel — who dispatches whom as a subagent):

```
raj-patel-techlead (team lead; ×N priya fan-out; independent quality gate)
  └── any registered agent
james-mitchell ──► maya (escalation), nina (security, explicit request only), tess (sweeps), marcus (review), ava (coverage)
ethan-kumar   ──► oliver (profiling), james (schema alignment), tess (sweeps), maya (escalation), marcus (review)
maya-rodriguez ─► nina (security, explicit request only), tess (sweeps), marcus (review)
coco-laurent  ──► penelope (design sign-off)
priya-sharma  ──► penelope (fidelity), marcus (review), tess (sweeps), coco (design mismatch), raj (structure)
oliver-singh  ──► marcus (optional review)
nova-chen     ──► marcus (prototype review), tess
felix-anderson ► marcus, nina (explicit request only), tess; escalates to maya
zara-ahmad    ──► ethan (data contracts), oliver (model analysis), tess (sweeps), maya (escalation), marcus (review)
dexter-cho    ──► ava (test strategy), marcus (gate alignment), tess (sweeps)
marcus-williams ► nina (security depth, explicit request only), kai (adversarial proof)
nina-petrov   ──► kai
taylor-kim    ──► runtime specialists (bounded audit slices and second opinions)
```

Leaf agents (explicit `tools` list omitting `Agent` — cannot spawn): `ava`, `sam`, `ada`, `penelope`, `kai`, `tess`. They hand work to live teammates through SendMessage or return it to their caller.

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
any agent → main agent: Workflow launch request (see plugins/essential/SUBAGENT.md)
```

Note: the edges above are proven defaults only. A spawn-capable agent discovers the current roster immediately before dispatch and chooses a better available specialist when one fits; true leaves are enforced by tool-list omission.

### Team shapes

- **Warm core** (trusting, low-friction hand-offs): raj, marcus, ava, james, dexter.
- **On-demand specialists**: maya, ethan, nina, nova, oliver, coco, priya, penelope, kai, sam, ada.
- **Background** (one run per spawn): felix, zara, taylor.
- **Mechanical**: tess.

### Gates

- **Gated producers** (embedded prompt-type routing Stop gate; 2-round cap): maya, ava, james, ethan, felix, zara, dexter, priya. Each gate checks the producer's final message for the generic `REVIEWED: source=<specialist|general|external|none> reviewer=<runtime-name|tool-name|none> verdict=<ok|blocked|unavailable> round=<n>` attestation. When changed code lacks one, the gate names that producer's proven reviewer defaults with each role and main task, requires discovery of a better runtime specialist when available, and tells the producer to request an independent artifact review through SendMessage, Agent, or its caller. Pure-analysis output passes on first stop; an unreachable reviewer or a spent 2-round budget releases the gate rather than deadlocking. Oliver Singh (Data Scientist; produces analyses and ML insights) is deliberately ungated because exploratory analysis is not production code; his production-bound work still receives independent review.
- **Write-fenced critics** (PreToolUse fence): marcus, penelope — may only write to their agent-memory dir or review reports.

### Team operation

- Works team-first: The main agent initiates an agentic team for non-trivial work, hands each task to the owning specialist and its team, and keeps teammates warm while measured runtime telemetry and task affinity show reuse remains useful. `plugins/essential/CLAUDE.md` carries shared operation rules; each owner plugin's `CLAUDE.md` carries only its task-to-specialist rows.
- Subagents reply to the teammate that assigned the work over SendMessage. Their `## Collaboration` edges are proven defaults, while runtime discovery may select a better available specialist (see `plugins/essential/SUBAGENT.md`).
- Subagents never launch the `Workflow` tool: they compose the complete tool input and SendMessage it to the main agent, which launches it and replies with the result (see `plugins/essential/SUBAGENT.md`). Plans authored by a specialist in plan mode flow back to the main agent the same way for presentation.

### Notes

- The copy-install into `~/.claude/agents/` is load-bearing for the hooks: Claude Code honors `hooks`, `permissionMode`, and `mcpServers` frontmatter only for agents in `~/.claude/agents/` / `.claude/agents/` — agents registered via a plugin ignore those fields. Do not convert the roster to plugin-registered agents, or every embedded gate and fence goes dead.
- `zara-ahmad-ml-engineer` uses the `theriety:build-service` skill — it requires the plugin whose manifest name is `theriety` (this marketplace registers it under the entry name `backend`; the manifest-vs-marketplace name mismatch is known).
- Installed agent definitions are intentionally single self-contained files even though their canonical source is split. This is why the routing Stop gate is embedded verbatim in all eight gated producers.
- Standards references (`SD-*`) in the definitions never use literal installation paths. They name a standard plus its owning plugin constitution, resolved at runtime when that plugin is enabled. A partial enabled roster is valid, so cross-plugin handoffs and context are best-effort when their owner plugin is absent.

## Validation

```bash
claude plugin validate --strict .
python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py .
```

Run `python3 scripts/generate_readme.py --check` to confirm this inventory is current.
