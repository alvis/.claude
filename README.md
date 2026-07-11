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

- `coding:commit` — Save code changes cleanly with jj-first, git-compatible routing. Use for commits, split/absorb/edit operations, stacked changes, restacks, history reordering, retrospective blame fixes, or PR materialization; preserve the repository history policy and keep coding:commit as the sole history-mutation owner.
- `coding:complete-code` — Complete explicit production implementation stubs in an existing scope. Use for canonical implementation TODOs, temporary production stubs, and draft-code sentinels; route bugs, test work, unstubbed functionality, new features, and ambiguous markers to their owning workflows.
- `coding:complete-test` — Author and improve tests for pending test cases, coverage gaps, fixtures, and redundancy cleanup. Use for test TODOs, it.todo or describe.todo entries, explicit test-writing requests, or coverage work. Production implementation stubs belong to complete-code; diagnosed failures belong to fix.
- `coding:document` — Create or update a package README and optional ARCHITECTURE.md from the actual implementation. Use after meaningful code changes, when docs are missing or stale, or when a package needs a source-backed structure overview. Preserve existing project voice and route specification documentation to specification skills.
- `coding:draft-code` — Draft TypeScript-compliant code skeletons with canonical TODO(implementation) placeholders. Use when starting an already-specified implementation or preparing typed production structure for later completion; do not implement business logic or create ambiguous plain TODO markers.
- `coding:finalize-commits` — Run isolated per-commit QA across every unpushed commit, report ordering or message issues, and coordinate approved corrections. Use before publishing a stack; coding:commit remains the sole owner of history mutations, reword, fold, reorder, and push.
- `coding:find-unused` — Perform read-only dead-code discovery for commented-out code, unused symbols, and unused test helpers. Use when identifying removal candidates; report evidence without deleting, refactoring, linting, or otherwise modifying the inspected source.
- `coding:fix` — Fix diagnosed incorrect behavior, failed tests, type errors, lint failures, or broken CI. Use when a concrete failure can be reproduced or review findings identify a defect; route new functionality to write-code and green structural cleanup to refactor.
- `coding:handover` — Persist CONTEXT.md, NOTES.md, and PLAN.md for later continuation of coding work. Use when pausing implementation or transferring repository state; this skill records the current session and does not create or execute a cross-domain plan.
- `coding:lint` — Use when source files need mechanical coding-standard enforcement, lint-error correction, or consistent formatting across a selected scope, including calls extended by another plugin's portable lint profile.
- `coding:modernize` — Apply version-supported syntax and API upgrades based on the project runtime and toolchain. Use when replacing legacy constructs with supported modern equivalents; do not claim general refactoring, dependency upgrades, or behavioral feature work.
- `coding:refactor` — Improve green code through behavior-preserving structural changes to organization, naming, readability, or documentation. Use when existing tests pass and the requested outcome is maintainability rather than a bug fix, new feature, or version-driven API upgrade.
- `coding:review-code` — Review semantic correctness, security, test intent, documentation, sibling consistency, and alignment with the implementation plan. Use after code changes or for explicit review requests; report findings without editing code and leave mechanical standards enforcement to lint.
- `coding:setup-project` — Ensure project structure exists before development, creating barebone scaffolding only if needed. Use when initializing new projects, validating project setup, or ensuring monorepo component structure.
- `coding:sync-tool` — Install or update coding CLI tools (brew, jj, gh) across macOS, Linux, and Windows. Use when tools are missing, stale, or needed on PATH for a sibling skill, including requests to install jj/gh/brew, update coding tools, or verify CLI dependencies before work.
- `coding:takeover` — Resume interrupted implementation from persisted handover documents. Use when CONTEXT.md, NOTES.md, and PLAN.md describe valid continuation state; this adapter validates those inputs and delegates the actual continuation to the standard write-code resume workflow.
- `coding:write-code` — Write production-ready code end to end through a TDD lifecycle of design, skeleton, implementation, tests, and refactoring. Use for new functions, features, modules, components, CLI or API endpoints, or approved tickets; route diagnosed failures to fix and explicit production stubs to complete-code.
- `coding:write-pr` — Author a conventional-commit PR title and unified body from a jj or git change ref, emitting output for gh pr create. Use for PR descriptions, draft pull requests, stacked coding:commit PR bodies, and callers that need a unified title/body template from a commit.

### essential

Documentation creation, code design, product strategy, and Notion integration for knowledge management

- `essential:autoresearch` — Run a metric-driven research loop: define a metric, evaluator, baseline, and target; evolve candidate solutions; score and adversarially verify them; then mutate survivors until the target, budget, or plateau ends the run. Use for measurable optimization of prompts, code, experiments, or creative variants; use deep-research for fact-finding.
- `essential:deep-research` — Conduct comprehensive multi-source research with AI-assisted analysis and explicit source synthesis. Use when investigating complex topics, comparing evidence, gathering current information, or producing a fact-finding report with citations and uncertainty notes. Do not use for metric-driven candidate optimization.
- `essential:handoff` — Create or execute a context-complete cross-domain plan as an orchestrator. Use when another agent must continue without prior context, or when a multi-domain plan needs coordinated execution while this skill retains decision ownership. For coding-session persistence, use coding:handover.
- `essential:install-statusline` — Install the bundled Bullet Train statusline into ~/.claude and wire settings.json statusLine. Use when setting up Claude Code on a new machine, installing or restoring the statusline, or repairing its configuration; preserve the bundled executable and report permission or platform limitations.
- `essential:think` — Structure pre-implementation reasoning for ambiguous problems. Use when the requested outcome, constraints, or safe solution are unclear and deliberate options, objections, dependencies, edge cases, and rollback need to be resolved before any modification or creation begins.

### governance (depends on: essential)

Tools for creating and managing Claude Code configuration files including commands, skills, standards, and agents

- `governance:create-agent` — Create a new specialist agent from the repository agent template as base.md plus frontmatter/claude.json. Use when adding a distinct role, trigger surface, or delegation capability that existing agents do not own. Confirm model, effort, and permission settings before authoring unless explicit overrides are supplied.
- `governance:create-skill` — Use when creating a reusable Claude Code skill, defining a new repeatable agent capability, or replacing a one-off workflow with discoverable instructions that need clear ownership, validation, and trigger behavior.
- `governance:create-standard` — Create a new technical standard under a plugin constitution with meta.md, scan.md, write.md, and rules/. Use when a reusable policy is missing and needs explicit scope, detection guidance, implementation guidance, and actionable rules. Do not use for revising an existing standard or creating a skill.
- `governance:update-agent` — Update one or more existing agent definitions to the current template or an explicit change request while preserving each role's useful expertise, triggers, context assignments, and collaboration links. Use for agent maintenance or migration; use create-agent when no suitable agent exists.
- `governance:update-skill` — Use when revising one or more existing Claude Code skills, aligning skill instructions with current repository policy, narrowing overlapping ownership, or applying a deliberate behavior change without creating a competing skill.
- `governance:update-standard` — Update explicitly selected technical standards to the current three-tier template or a stated policy change, preserving valid rules and examples while removing superseded wording. Use for standard maintenance or bounded bulk migration; use create-standard when the target directory does not exist.
- `governance:verify-skill` — Use when validating a new or changed Claude Code skill, checking structural and repository policy compliance, testing whether descriptions trigger accurately, or grading representative skill outputs before deployment.

### react (depends on: coding, essential)

React component development with UI implementation, design systems, Next.js expertise, and fullstack capabilities

- `react:lint` — Use when React JSX, components, hooks, accessibility, project structure, tests, or Storybook files need mechanical standards enforcement through the shared Coding lint workflow; React owns framework rules while Coding owns generic execution and reporting.
- `react:react` — Use when creating, editing, reviewing, or routing work involving React, JSX, hooks, components, accessibility behavior, project structure, tests, or Storybook stories; this router selects React standards while Coding owns generic execution.

### specification (depends on: coding, essential)

Design specifications, architecture specs, requirements gathering, and technical documentation with Notion integration for knowledge management

- `specification:implement-code` — Execute approved specification tickets end to end by resolving ticket intent, materializing the authoritative spec bundle, coordinating implementation and tests, and reviewing alignment. Use after plan-code approval or to resume an explicitly scoped implementation. Keep contract authoring in spec-code and generic coding in the coding plugin.
- `specification:mdc` — Read, edit, and author MDC (Contextual Markdown, @theriety/mdc) files safely with native text tools. Use when asked to "edit this .mdc file", "add a block to <doc>.mdc", "update the annotation for ref <x>", "convert this to MDC", whenever a .mdc file must be read or written, or when mutating any file under .code-spec/.
- `specification:plan-code` — Generate DRAFT.md as a commit blueprint and PLAN.md as an execution roadmap from an approved proposal or specification. Use when planning implementations, defining atomic commits, documenting change proposals, or preparing a coding workflow with explicit verification and ownership boundaries.
- `specification:review-implementation` — Review an implementation against an authoritative local or Notion specification, then run the general coding and security review. Use for specification alignment, delivered-ticket validation, or detecting omissions, drift, and unsanctioned behavior before handoff.
- `specification:spec-code` — Design or document technical specifications in the canonical template, then delegate Notion synchronization to sync-notion. Use for greenfield specs, updates to an existing DESIGN.md, or documenting an implementation without inventing requirements.
- `specification:sync-notion` — Synchronize local Markdown files with Notion through the notion-sync CLI, including recursive pulls, creates, updates, diffs, conflict resolution, and integrity checks. Use when documentation must move between local files and Notion. Keep specification authoring in spec-code and implementation planning in plan-code.
- `specification:sync-spec` — Materialize a guaranteed-on-disk Notion specification tree as a flat `.code-spec/` bundle of `{kebab-title}-{32hex-id}.md` files plus `.gitignore`. Use before downstream analysis or code generation, when refreshing a stale bundle, or when a ticket requires local spec evidence; fail unless the root id-suffix file exists and is non-empty.

### web (depends on: coding, essential)

Web development tools including UX design, growth optimization, rapid prototyping, browser automation via agent-browser, Next.js debugging via Chrome DevTools, and design auditing

- `web:audit` — Audit a rendered web interface against the 60-rule design standard with deterministic DOM checks, isolated-browser evidence, responsive viewports, accessibility checks, and focused visual review. Use for design QA, WCAG checks, visual review, or launch assessment. Report findings only; route implementation changes to the owning coding or client skill.
- `web:css` — Scaffold or maintain a project's root stylesheet using the CSS-only light, dark, and system color-mode contract. Use for theme.css, globals.css, or app.css setup, migration from class-driven dark mode, semantic token wiring, or color-mode corrections. This skill edits CSS only and never ships JavaScript.
- `web:design` — Design or redesign a web interface with a coherent visual direction, responsive layout, typography, color, motion, and accessible interaction states. Use for new pages, component polish, mockups, or a facelift of an existing site. Produce DESIGN.md and a verifiable preview; route assessment to audit and runtime debugging to next.
- `web:imagine` — Generate or edit images through the bundled multi-provider CLI, or write structured prompts and analyze visual styles from references. Use for concept art, product shots, covers, UI assets, transparent or vector output, inpainting, background changes, batch variants, and prompt-only work. Keep image generation separate from web design decisions and visual audits.
- `web:next` — Diagnose Next.js runtime behavior with next-browser and Chrome DevTools MCP: React components, routes, SSR errors, DOM/styles, performance, Lighthouse, network, device emulation, JavaScript debugging, storage, screenshots, and interactions. Use for evidence-backed browser diagnosis; route visual creation to design and story-state assessment to storybook.
- `web:storybook` — Audit a Storybook instance for setup failures, accessibility violations, interaction errors, and visual regressions across meaningful story states. Use when checking stories before release, validating addon panels, or finding missing focus behavior. Report evidence and findings; do not edit components or stories.

### theriety (depends on: coding, specification, essential)

Domain-specific service and data orchestrator lifecycle management for Theriety — build and audit services and data layers

- `theriety:audit-data` — Audit data orchestrators against specifications, generate discrepancy reports, and remediate approved changes. Use when reviewing data domain completeness, checking schema compliance, or performing data layer quality audits.
- `theriety:audit-service` — Audit a backend service against its implementation and documentation contract, producing evidence-backed findings and optionally remediating approved gaps. Use for operation completeness, service quality, or documentation-only audits; choose --scope to keep the review focused.
- `theriety:build-data` — Build complete data orchestrators from spec to commit, including schema setup, operations, controllers, and quality gates. Use when creating new data domains, adding operations to existing orchestrators, or implementing Prisma schemas from Notion.
- `theriety:build-service` — Build complete backend services from spec to commit, including operation declaration, implementation, and quality gates. Use when creating new services, adding operations to existing services, or declaring manifest schemas.

### client (depends on: essential)

Client-facing screen design and UX documentation with Notion integration

- `client:create-screen-design` — Create new responsive screen-design documentation in Notion for a named product and screen. Use when a product needs a new UX contract, layout alternatives, interaction states, or handoff-ready design notes. Do not use for changing an existing screen; route those requests to update-screen-design.
- `client:update-screen-design` — Update existing responsive screen-design pages in Notion while preserving approved content and applying an explicit change request. Use for template migrations, accessibility corrections, or scoped screen revisions. Do not use for new pages; route creation to create-screen-design.

## Validation

```bash
claude plugin validate --strict .
python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py .
```

Run `python3 scripts/generate_readme.py --check` to confirm this inventory is current.
