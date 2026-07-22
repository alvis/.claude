# Claude Code Plugin Marketplace

Eight focused plugins provide composable Claude Code skills. Plugin manifests and each skill's `SKILL.md` are the source of truth; the inventory in this file is generated while the developer workflow and agent-team guide are preserved.

## Install

```bash
cd /path/to/target-project
claude plugin marketplace add alvis/.claude --scope project
claude plugin install specification@alvis --scope project
```

`specification` is the recommended end-to-end bundle; its declared dependencies install `coding` and `essential`. Use `--scope local` for a private trial or `--scope user` across your projects. For a private source-checkout trial, add its absolute path at local scope rather than committing a machine-specific project path.

## Developer workflow

This guide describes work in a target codebase. Do not run feature work against this marketplace checkout unless the marketplace itself is the target.

### Prerequisites and activation

The core lifecycle expects Claude Code, Bash, `jq`, Git, and Python 3, plus the target project's own build and test tools. The publication path additionally expects an authenticated `gh` and a jj-colocated Git repository. Notion synchronization is optional and requires `NOTION_TOKEN`, access to every selected page, and an explicit absolute destination-local [transport profile](plugins/specification/skills/sync-notion/references/transport-profile.md). The strict profile pins one external executable and binds each exact command/flag vector and JSON output contract to checksum-bound conformance evidence; conditional update and conditional create are proven independently. This repository does not bundle or endorse a distribution. A missing or invalid profile returns `transport_unverified`; a verified profile without the conditional capability required by the selected write returns `refused` with `next_action: provide_conditional_transport`. Local and inline workflows remain usable in either case.

After installation, start Claude Code in the target repository and ask Claude to run `/essential:install-agents` before using the full golden lifecycle. Review and team orchestrators depend on the installed specialist roles and must block when a required role has no supported fallback. The installer writes stitched agent definitions contributed by the enabled plugins to `~/.claude/agents/`; restart the Claude Code session after installing or updating them. Run `/reload-plugins` after marketplace updates.

Installation scopes have different intent:

| Scope | Use |
|---|---|
| `local` | Try the plugin privately in one target checkout. |
| `project` | Record the plugin for collaborators in the target project. |
| `user` | Enable it for the current developer across projects. |

Project scope writes the marketplace and enabled-plugin declarations to the target's `.claude/settings.json`; review that file before committing it. Keep `NOTION_TOKEN` and every other credential outside project settings and version control. The transport profile is secret-free but machine-local because it contains an absolute executable path; do not copy an origin machine's profile into a portable handover. Run `python3 plugins/specification/skills/sync-notion/scripts/validate-transport-profile.py --print-template` from this checkout for a deliberately unverified starter shape; replacing its placeholders and attaching real conformance evidence is mandatory before use.

### Five-minute local-spec path

Use a lowercase tracker-derived ID that will remain stable, such as `eng-421-checkout-refunds`. Then give Claude an explicit target, capability slug, and authoritative requirements:

```text
/essential:discover "Find delivery blind spots for checkout refunds" --work-id=eng-421-checkout-refunds --mode=blindspots --persist
/specification:spec-code "Design idempotent checkout refunds from these requirements" --work-id=eng-421-checkout-refunds --capability=checkout-refunds
/specification:plan-code --work-id=eng-421-checkout-refunds --spec=docs/specs/checkout-refunds/index.md
```

On first use, the PM confirms the work identity, handles the exact `.engineering/` ignore rule, and invokes the no-clobber bootstrap before discovery writes its ledger. For an inline source, `spec-code` uses the bundled neutral template when the project has not selected one, records the approved candidate in work state, and creates its durable carrier under `docs/specs/`; a work-local `spec/` materialization exists only for a selected Notion source. Approve the exact specification content, confirmed by direct comparison, then read the resulting `state.md` task table directly for the immutable task definitions and dependency edges; there is no separate plan-digest re-validation. Status, owner, evidence, timestamps, formatting, and derived diagrams never require reapproval; changing a task definition does. Pass the returned authoritative path or ref when asking Claude to implement:

```text
/specification:implement-code docs/specs/checkout-refunds/index.md --work-id=eng-421-checkout-refunds --repo=/absolute/path/to/target-project --defer-publication
```

Inline prompt text is evidence, not a durable contract. `spec-code` writes the complete candidate under the ignored work root, binds approval to the exact candidate content confirmed by direct comparison, and promotes a content-equivalent carrier plus `provenance.json` under `docs/specs/checkout-refunds/`; later stages never depend on the chat transcript. The deferred implementation result tells you what remains. For `needs_save`, execute its exact `/coding:commit --paths-from=<manifest> --manifest-sha256=<sha256>` command, require the PASS preservation receipt, then run `/coding:finalize-commits`. Start directly with finalization for `ready_for_finalization`; do nothing for `no_change`. Never replace the returned scoped command with plain `/coding:commit`.

This path deliberately avoids Notion and remote publication. It should leave verified code, saved local history when requested, work-local evidence and reviews, and durable specification documents. Add Notion or PR publication only after the local flow is understood.

### Golden development lifecycle

| Stage | Developer action | Owner and gate |
|---|---|---|
| 1. Start | Name the target repository, tracker-derived work ID, scope, and success criteria. | The PM resolves one workspace-local work root and bootstraps it only after the ignore gate. |
| 2. Discover | Run `/essential:discover` for blind spots, references, or a disposable prototype. | Discovery records evidence separately from its marked `DSC01`-style task graph and says whether the work is ready for a decision. |
| 3. Decide | Run `/essential:decide` only when material alternatives need a choice. | After approval, Decide records the decision and invokes the selected next owner itself. Do not invoke that owner a second time. |
| 4. Specify | If no prior Decide handoff already invoked it, run `/specification:spec-code` with one explicit local, inline, or Notion source and a capability slug. | Approve the exact specification content, confirmed by direct comparison. A transport mirror is never the authored source. |
| 5. Plan | Run `/specification:plan-code` against that specification. | Approve the task definitions and dependency graph recorded in `state.md` before implementation; changing them later requires reapproval, not a digest. Three-letter parent tasks and their numbered subtasks form an explicit linear or branching DAG; unresolved decisions remain blockers. |
| 6. Implement | Run `/specification:implement-code --defer-publication` when you want the manual save/finalize/publish stops shown below; use `/coding:write-code` directly only for a non-specification coding task. | Execute only dependency-ready leaf task IDs using target-native tests. Child writers return status evidence; the coordinator alone reconciles work state. |
| 7. Document | Let implementation invoke `/coding:document` when public behavior, configuration, operations, or developer workflow changed. | Documentation finishes before review and save-manifest sealing; product specifications remain owned by Specification. |
| 8. Review, lint, and repair | Let implementation run review, fixes, touched-scope lint, and final target-native checks. A manual lint recovery uses `/coding:lint <touched-specifier> --scope=uncommitted --skip-unused`. | All findings block closure. A correction reruns affected tests/reviews; project-wide unused cleanup is a separate explicit task. |
| 9. Reconcile the spec | Let implementation run the applicable Notion completion gate or local source/carrier recheck. | A change in specification content, confirmed by direct comparison, or a verified path/layout change invalidates plan/code/review evidence; identity/logical-ID/carrier-kind drift refuses as invalid evidence. Only a structured revision/`last_edited_time`-only change refreshes exact evidence without invalidating semantic approval. |
| 10. Save and finalize | On deferred `needs_save`, run the exact returned `/coding:commit --paths-from=... --manifest-sha256=...`; on `ready_for_finalization`, skip save; on `no_change`, stop. After a PASS scoped-save receipt, run `/coding:finalize-commits` once over the complete unpushed chain. | The closed-set save preserves unrelated staged and dirty developer work. Any project writer after sealing invalidates the manifest and requires the owning implementation/review/sync steps to run again before resealing. |
| 11. Publish | If no PR was already published, run `/coding:push-pr` only when GitHub, `gh`, and jj prerequisites are satisfied. | It creates or updates draft PRs and monitors CI. Do not publish twice; a human owner decides when a green draft becomes ready and when it may merge. |
| 12. Close or transfer | Mark the work complete after acceptance and terminal task validation, or run `/essential:handover`. | Every required executable leaf must be done. A handover must reference remotely reachable source or carry an approved external patch/bundle; `.engineering/` is not the transfer mechanism. |

Choose one publication owner. With `--defer-publication`, `implement-code` still completes documentation, review, lint, verification, and specification reconciliation, then stops before history finalization/publication. Without it, the same parent delegates scoped save, finalization, and draft-PR publication itself; do not repeat stages 10–11 manually. Direct `coding:write-code` has no public defer flag and owns its complete path.

When the target is a standalone or non-TypeScript repository, verify each selected skill against the repository's native commands before use. Scaffolding and several authoring workflows are currently strongest in TypeScript monorepos; do not let a generic default replace the target's established toolchain.

### Notion-backed specifications

Treat a synchronized specification as three distinct copies:

| Copy | Purpose |
|---|---|
| Base | Immutable content and remote revision from the last verified materialization. |
| Local | The work-local authored `.mdc` used by planning, implementation, and review. |
| Remote | A fresh staging pull of the current Notion page immediately before a sync decision. |

Select one exact repository-contained, ignored transport mirror; `.engineering/notion/` is only a convention. Never hand-edit the mirror. Edit the work-local copy through `/specification:mdc` so `ref:` identity, MDC structure, and transport-owned `last_edited_time` remain intact. The examples assume your team supplied the secret-free profile at `/absolute/path/to/notion-sync-transport.json`.

Before planning or implementation, materialize the Notion source:

```text
/specification:sync-spec <notion-page-ref> --work-id=eng-421-checkout-refunds --mirror=.engineering/notion --transport-profile=/absolute/path/to/notion-sync-transport.json --mode=materialize
```

Normally `spec-code` and `implement-code` invoke the appropriate completion stage. For advanced recovery, choose exactly one stage for the current gate—do not paste both commands as a sequence:

```text
# After final specification-content approval:
/specification:sync-spec <notion-page-ref> --work-id=eng-421-checkout-refunds --mirror=.engineering/notion --transport-profile=/absolute/path/to/notion-sync-transport.json --mode=complete --stage=specification --capability=checkout-refunds

# Or, after clean implementation review against that same content:
/specification:sync-spec <notion-page-ref> --work-id=eng-421-checkout-refunds --mirror=.engineering/notion --transport-profile=/absolute/path/to/notion-sync-transport.json --mode=complete --stage=implementation --capability=checkout-refunds
```

The safe decision table is:

| Local since base | Notion since base | Required result |
|---|---|---|
| unchanged | unchanged | No content write; record verification. |
| unchanged | transport metadata only | Refresh the exact base/revision receipt only after unit-by-unit identity, path, kind, logical ID, and semantic projection match; retain semantic approval, plan, code, and review. |
| unchanged | verified path/layout changed, identities intact | Return `status: success`, `classification: structural_change`, `next_action: revalidate`; materialize the verified structure and invalidate dependent approval, plan, code, and review even when the specification content is otherwise unchanged. Identity, logical-ID, or carrier-kind drift refuses as invalid evidence. |
| changed | unchanged | Review and approve the exact local specification content, recheck the remote revision, then publish and verification-pull. |
| unchanged | semantic change | Return `status: success`, `classification: remote_only`, `next_action: revalidate`; materialize the verified remote copy into Local, issue a new immutable base/receipt, and restart from that base. Do not overwrite Notion or reread stale Local. |
| changed | semantic change | Stop with Base/Local/Remote evidence. At specification stage, the developer may approve a merge proposal. At implementation stage, publish nothing: resolve and approve it through specification completion, verification-pull and materialize it, then reapprove/repeat plan, implementation, review, and implementation completion. |
| no trustworthy base | any state | Refuse publication and establish a verified baseline first. |

For every remote write, pull fresh remote state, compare all three copies directly, and bind approval/review to the final specification content, confirmed by direct comparison; use the remote revision for recheck evidence. Immediately before updating an existing page, recheck its remote revision and require the profile's conformance-proven `conditional_update` vector. Page creation uses the validated create command, repeats search/absence and parent checks, and requires independently proven atomic `conditional_create`; conditional update never proves create-if-absent. Without the capability required by that operation, publish nothing and return `status: refused` with `next_action: provide_conditional_transport`. Any changed precondition aborts and restarts reconciliation. `Keep Both` requires approval of the synthesized content; `Skip` leaves both canonical sides untouched and never publishes a TODO. A verification pull and immutable receipt complete a permitted operation.

Each participating process also takes a deterministic per-page lease under the exact shared transport root. That prevents two plugin runs using the same mirror from racing, but it is not a Notion-wide or cross-machine lock; independently proven conditional update or conditional create remains the real cross-client guard for its corresponding operation. A crashed owner leaves a contended lease that requires owner/session verification, a fresh read-only pull, and compare-token recovery. If a recursive write may have partially mutated Notion, stop and reconcile from a fresh pull—never retry an ambiguous mutation. Local MDC editing preserves transport-owned `last_edited_time` byte-for-byte; local edit timestamps belong in work evidence, not the page frontmatter.

Thought experiment: a developer edits an error-handling section locally while a product manager changes the same Notion section. The base proves both diverged. The plugin must not select either side, concatenate prose, or push a placeholder. It stages a conflict packet. If implementation has already started, the merge returns to specification ownership for content approval, guarded completion, verification-pull, and materialization; the old plan, implementation, and review are then repeated against the new content before implementation completion retries. If the product manager edits again before the guarded write, publication stops and the reconciliation cycle restarts.

### Work state, handover, and recovery

- `.engineering/works/<work-id>/` is ignored, workspace-local coordination memory. It is not a backup and is not shared automatically between Git worktrees or jj workspaces.
- `working.md` is the short current-focus pointer; `state.md` is the complete lifecycle, plan pointer, task graph, and evidence index. Detailed decisions, reviews, changes, design, and sync receipts live in their owned children.
- Top-level tasks use stable three-letter uppercase IDs such as `LFE`; one level of subtasks uses `LFE01` through `LFE99`. IDs are never renamed or reused. The authoritative overall graph uses full IDs, for example `LFE → {API,DOC} → VAL`; a local child graph may be shown as `01 → {02,03} → 04`, but stored edges use `LFE01`-style IDs.
- Every task shows both a mark and word: `- planned`, `⧗ working`, `✓ done`, `X failed`, `! blocked`, or `⊘ cancelled`. Parent status is derived from required child state. Dependency order, not row order, determines what is runnable.
- The PM reads `state.md` directly before closure or handover; there is no separate validation step. A status-only change needs nothing further; changing an ID, task definition, requiredness, acceptance mapping, target, or dependency requires reapproval and invalidates its downstream closure.
- `docs/specs/` and `docs/architecture/` are durable and versioned. For inline or unreachable `local-approved:` origins, the promoted specification entry is the sole authority. A reachable `repo:` local source remains authoritative and its entry is a checked derivation. A Notion-backed entry derives from the verified MDC pairing. `provenance.json` records source/carrier content references, an `approved_content_ref` pointing at the exact approved content for local/inline sources so a resumed spec is confirmed by direct comparison, and which case applies.
- To pause, run `/essential:handover` (optionally with a work-id filter) and publish its plain-Markdown receipt to an issue, PR, task, or approved Notion anchor. The receipt opens with a `## Work index` listing every work stream, then embeds a `## Work stream: <work-id>` section for each continuable stream (`initialized`/`active`/`blocked`); `complete` and `retiring` streams stay index-only. Each embedded section carries a per-stream plain-git source anchor (a remote revision, a `git format-patch` patch, or an externally attached `git bundle` ref), the raw contents of that stream's `state.md`, `working.md`, and every continuity-relevant detail file (each fenced with a collision-safe backtick run), any specification needed to continue, and a continuation note. To resume, run `/essential:takeover <receipt-or-anchor>` in the new workspace. It parses the index, lets you multi-select which continuable streams to continue, groups them by source anchor, rehydrates the group matching the current worktree into the default worktree's memory, writes each work-state file back to its work-relative path, stages the specifications, and hands off each stream to the relevant implementation skill.
- Never claim a handover is portable when code exists only as an uncommitted working copy. Publish an approved branch/commit or attach a patch/bundle to the external receipt first.

### Completion checklist

- The work ID, repository, and authoritative specification source are unambiguous.
- Specification approval names the exact specification content, confirmed by direct comparison; plan and review track task definitions directly from `state.md`, with reapproval on any change rather than a digest.
- Every stable task ID and edge in `state.md` is accounted for, with no cycle or contradictory parent roll-up, and every required executable leaf is marked `✓ done`.
- Target-native tests, lint, type checks, and builds pass where applicable.
- Canonical review artifacts have no outstanding findings or malformed dispositions.
- Notion reconciliation and verification completed when the specification is Notion-backed; any changed final content was revalidated.
- Durable specification, package, and architecture docs match delivered behavior.
- Each commit passes isolated QA; published PRs are green and point at the expected revisions.
- Acceptance, external receipts, and the final work-state status are recorded before cleanup.

Useful references: [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [plugin installation and scopes](https://code.claude.com/docs/en/discover-plugins), and [plugin reference](https://code.claude.com/docs/en/plugins-reference).

## Plugins and skills

### coding (depends on: essential)

General code writing tools including quality checks, testing, architecture, and implementation support

- `coding:cleanup` — Audit and safely retire stale development state across git branches, registered Git worktrees, jj workspaces, and workspace-local engineering work directories. Use for /cleanup or abandoned-work audits; require evidence, retention, recoverable backup, and per-target approval before removal.
- `coding:commit` — Save code changes cleanly with jj-first, git-compatible routing. Use for commits, manifest-scoped lifecycle saves, split/absorb/edit operations, stacked changes, history reordering, retrospective blame fixes, or the --create-pr compatibility handoff; preserve the repository history policy and keep coding:commit as the sole history-mutation owner.
- `coding:complete-code` — Complete explicit production implementation stubs in an existing scope. Use for canonical implementation TODOs, temporary production stubs, and draft-code sentinels; route bugs, test work, unstubbed functionality, new features, and ambiguous markers to their owning workflows.
- `coding:complete-test` — Author and improve tests for pending test cases, coverage gaps, fixtures, and redundancy cleanup. Use for test TODOs, it.todo or describe.todo entries, explicit test-writing requests, or coverage work. Production implementation stubs belong to complete-code; diagnosed failures belong to fix.
- `coding:document` — Create or update source-backed package usage documentation and durable architecture documentation. Use after meaningful code changes, when docs are missing or stale, or when a package needs an architecture overview under docs/architecture; route specifications and Notion content to specification skills.
- `coding:draft-code` — Draft TypeScript-compliant code skeletons with canonical TODO(implementation) placeholders. Use when starting an already-specified implementation or preparing typed production structure for later completion; do not implement business logic or create ambiguous plain TODO markers.
- `coding:finalize-commits` — Run isolated per-commit QA across every unpushed commit, report ordering or message issues, and coordinate approved corrections. Use before publishing a stack; coding:commit owns history mutations and coding:push-pr owns publication.
- `coding:find-unused` — Perform read-only dead-code discovery for commented-out code, unused symbols, and unused test helpers. Use when identifying removal candidates; report evidence without deleting, refactoring, linting, or otherwise modifying the inspected source.
- `coding:fix` — Fix diagnosed incorrect behavior, failed tests, type errors, lint failures, or broken CI. Use when a concrete failure can be reproduced or review findings identify a defect; route new functionality to write-code and green structural cleanup to refactor.
- `coding:lint` — Enforce coding standards mechanically across a selected scope with batched linters and independent reviewers. Use when source files need lint-error correction, standards enforcement, or consistent formatting, including calls extended by another plugin's portable lint profile; behavior-changing repairs belong to fix.
- `coding:merge-pr` — Merge a linear stack of GitHub pull requests while restacking descendants between merges. Use when a user invokes /merge-pr with PR numbers, asks to merge stacked PRs, or needs gh-driven bottom-up PR merging with automatic downstream rebase.
- `coding:modernize` — Apply version-supported syntax and API upgrades based on the project runtime and toolchain. Use when replacing legacy constructs with supported modern equivalents; do not claim general refactoring, dependency upgrades, or behavioral feature work.
- `coding:push-pr` — Publish saved changes as draft pull requests and drive GitHub CI to green. Use when asked to push the latest commit, create or update a PR, repush after a fix, babysit pending checks, repair red CI, monitor every check, or converge a PR stack.
- `coding:refactor` — Improve green code through behavior-preserving structural changes to organization, naming, readability, or documentation. Use when existing tests pass and the requested outcome is maintainability rather than a bug fix, new feature, or version-driven API upgrade.
- `coding:review-code` — Review alignment, semantic correctness, security, test intent, documentation, quality, and style after code changes. Use for explicit post-implementation or pre-merge review; write canonical work-local review artifacts without editing the reviewed code.
- `coding:setup-project` — Ensure project structure exists before development, creating barebone scaffolding only if needed. Use when initializing new projects, validating project setup, or ensuring monorepo component structure.
- `coding:sync-tool` — Install or update registered coding CLI tools (brew, jj, gh, fallow, python) across macOS, Linux, and Windows. Use when tools are missing, stale, or needed on PATH for a sibling skill, including requests to install jj/gh/brew, update coding tools, or verify CLI dependencies before work.
- `coding:write-code` — Write production-ready code end to end through a TDD lifecycle of design, skeleton, implementation, tests, and refactoring. Use for new functions, features, modules, components, CLI or API endpoints, or approved tickets; route diagnosed failures to fix and explicit production stubs to complete-code.
- `coding:write-pr` — Author a conventional-commit PR title and unified body from a jj or git change ref, emitting output for gh pr create. Use for PR descriptions, draft pull requests, stacked coding:push-pr PR bodies, and callers that need a unified title/body template from a commit.

### essential

Documentation creation, code design, product strategy, and Notion integration for knowledge management

- `essential:autoresearch` — Run a metric-driven research loop: define a metric, evaluator, baseline, and target; evolve candidate solutions; score and adversarially verify them; then mutate survivors until the target, budget, or plateau ends the run. Use for measurable optimization of prompts, code, experiments, or creative variants; use deep-research for fact-finding.
- `essential:decide` — Decides between researched approaches before implementation. Use when asked to choose an approach, challenge a recommendation, make an architecture decision, compare options, define rollback and falsification signals, or obtain approval; routes blindspot passes, brainstorms, interviews, references, and prototypes to essential:discover.
- `essential:deep-research` — Conduct comprehensive multi-source research with AI-assisted analysis, adversarial claim verification, and explicit source synthesis. Use when investigating complex topics, comparing evidence, gathering current information, or producing a fact-finding report with citations and uncertainty notes. Do not use for metric-driven candidate optimization.
- `essential:discover` — Discovers material unknowns before planning. Use for a blindspot pass or unknown unknowns, to brainstorm approaches from cheapest to ambitious, interview about architecture, extract reference implementation semantics, make a disposable prototype before touching the real app, or check whether discovery is ready for a decision; researched option selection belongs to essential:decide.
- `essential:handoff` — Create or execute a context-complete cross-domain plan as an orchestrator. Use when another agent must continue without prior context, or when a multi-domain plan needs coordinated execution while this skill retains decision ownership. For coding-session persistence, use essential:handover.
- `essential:handover` — Persist the current source tree's engineering work stream state and update the default source tree's global cross-tree overview, then emit a portable receipt that indexes the current tree's streams and embeds each continuable one. Use when pausing or transferring coding work; this skill records continuity and does not execute the work.
- `essential:install-agents` — Discover, validate, stitch, and install specialist agent templates contributed by Essential and other enabled plugins in the same marketplace. Use when asked to install agents, set up subagents, refresh the agent team, or configure Claude Code on a new machine.
- `essential:install-statusline` — Install the bundled Bullet Train statusline into ~/.claude and wire settings.json statusLine. Use when setting up Claude Code on a new machine, installing or restoring the statusline, or repairing its configuration; preserve the bundled executable and report permission or platform limitations.
- `essential:takeover` — Resume paused engineering work. With no argument, default to the current source tree's own incomplete work streams read straight from on-disk state files, and use the default source tree's global .engineering/overview.md to also offer other source trees' streams — switching the working directory to that tree if one is chosen. Given a portable receipt or anchor, rehydrate the paused streams into workspace-local memory first. Then resolve pending decisions and hand each selected stream to its declared continuation skill.

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

- `specification:implement-code` — Execute an approved specification work item from an authoritative local, inline, or Notion-backed contract through delegated coding, review, applicable completion sync, and durable derivation. Use after plan-code approval, when resuming partial work, or when auditing delivered ticket work.
- `specification:mdc` — Read, edit, and author Notion-backed MDC files safely with native text tools while preserving @theriety/mdc grammar and ref identity. Use for any authored .mdc body change. Keep transport, pairing, and conflict orchestration in sync-notion and sync-spec.
- `specification:plan-code` — Build an implementation-ready plan from an approved specification inside an active engineering work item. Use to resolve the decision surface, define atomic implementation slices, and prepare verification without creating independent root planning or change artifacts.
- `specification:review-implementation` — Review implementation against an authoritative local, inline-origin, or Notion specification, coordinate the seven canonical review areas, and summarize dispositions in the active work item. Use for alignment, ticket validation, omissions, drift, and unsanctioned behavior.
- `specification:spec-code` — Design, update, or retrospectively document a technical specification from a user-selected local, inline, or Notion source through an active engineering work item and versioned derived docs. Use for specification authoring; keep Notion transport in sync-notion and implementation planning in plan-code.
- `specification:sync-notion` — Synchronize paired local files and Notion pages in a declared direction, including recursive pulls, guarded pushes, and explicit base-aware conflict resolution. Own Notion transport and pairing; keep specification orchestration in sync-spec and authored MDC edits in mdc.
- `specification:sync-spec` — Materialize a required Notion specification into an active engineering work directory or complete approved specification changes through an explicitly selected local transport pair. Use before specification planning, implementation, or review and when publishing a reviewed contract. Delegate transport and conflicts to sync-notion.

### web (depends on: coding, essential)

Web development tools including UX design, growth optimization, rapid prototyping, browser automation via agent-browser, Next.js debugging via Chrome DevTools, and design auditing

- `web:audit` — Audit a rendered web interface against the design standard with the bundled deterministic CLI, shared-browser evidence, responsive viewports, accessibility checks, and focused visual adjudication. Use for design QA, WCAG checks, visual review, or launch assessment. Route findings into canonical work reviews; route fixes to the owning implementation skill.
- `web:css` — Scaffold or maintain a project's root stylesheet using the CSS-only light, dark, and system color-mode contract. Use for theme.css, globals.css, or app.css setup, migration from class-driven dark mode, semantic token wiring, or color-mode corrections. Detect conflicts, obtain migration approval, preserve existing tokens, and edit CSS only.
- `web:design` — Design or redesign a web interface — and implement it when authorized — with coherent visual direction, responsive layout, typography, color, motion, and accessible states. Maintains work-local design contracts and ranked variant boards, then drives an independent implement-evaluate loop with visual-diff confirmation. Use for new pages, component polish, mockups, or facelifts.
- `web:imagine` — Generate or edit images through the bundled multi-provider CLI, or write structured prompts and analyze visual styles from references. Use for concept art, product shots, covers, UI assets, transparent or vector output, inpainting, background changes, batch variants, and prompt-only work. Keep image generation separate from web design decisions and visual audits.
- `web:next` — Diagnose Next.js runtime behavior with next-browser and Chrome DevTools MCP: React components, routes, SSR errors, DOM/styles, performance, Lighthouse, network, device emulation, JavaScript debugging, storage, screenshots, and interactions. Use for evidence-backed browser diagnosis; route visual creation to design and story-state assessment to storybook.
- `web:storybook` — Audit a Storybook instance for setup failures, accessibility violations, interaction errors, and visual regressions across meaningful story states. Use before release or when validating addons and focus behavior. Run the bundled lifecycle in order, preserve evidence, and report findings; do not edit components, stories, or configuration.

### theriety (depends on: coding, specification, essential)

Domain-specific service and data orchestrator lifecycle management for Theriety — build and audit services and data layers

- `theriety:audit-data` — Audit a data orchestrator against its work-local authoritative specification and the canonical review taxonomy, then remediate explicitly approved gaps. Use for schema, operation, controller, testing, and data-layer quality review; keep service audits in audit-service.
- `theriety:audit-service` — Audit a backend service against its work-local authoritative specification and canonical review areas, with optional approved remediation. Use for implementation, operation completeness, documentation, semantic, security, testing, and quality audits.
- `theriety:build-data` — Build or extend a data orchestrator from an approved work-local specification through schema, operations, controller integration, tests, canonical review, and handoff. Use for new data domains, operations, or Prisma schemas; keep audits in audit-data.
- `theriety:build-service` — Build or extend a backend service from an approved work-local specification through manifests, implementation, tests, canonical review, and handoff. Use for new services, operations, integrations, webhooks, or manifest schemas; keep audits in audit-service.

### client (depends on: essential)

Client-facing screen design and UX documentation with Notion integration

- `client:create-screen-design` — Create a new responsive screen-design contract from user-selected product and specification context, keep temporary exploration in the active work item, synchronize approved content through the selected MDC/Notion mechanism, and promote durable design docs. Route existing screens to update-screen-design.
- `client:update-screen-design` — Update explicitly selected responsive screen-design contracts from user-selected product and specification context, preserving identity and approved content while recording temporary work design and promoting durable versioned design. Require a selector or --all; route missing pages to create-screen-design.

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
