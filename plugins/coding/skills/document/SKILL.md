---
name: document
description: Create or update a package's README.md and optionally an ARCHITECTURE.md from the actual code implementation. Use when writing project documentation, drafting a new README, refreshing stale docs after code changes, documenting monorepo packages, or producing an ARCHITECTURE.md reflecting current source structure. Follows existing README.template.md or sibling package READMEs when present; otherwise falls back to bundled templates in references/ and only enters plan mode when neither exists.
model: opus
context: fork
agent: general-purpose
---

# Document

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Produce accurate, professional `README.md` (and optionally `ARCHITECTURE.md`) files that faithfully reflect the actual code implementation of a package. The skill prioritizes consistency with the surrounding repository — existing templates, checklists, and sibling package READMEs are authoritative references that the skill follows without asking. Only when the target is truly greenfield does the skill switch to plan mode to negotiate a content outline with the user.

**When to use**:

- When creating a fresh `README.md` for a newly scaffolded package
- When refreshing a stale `README.md` after substantive code changes (new exports, renamed modules, removed features, changed CLI surface)
- When adding an `ARCHITECTURE.md` describing file structure and main components
- When aligning a package's docs with a monorepo-wide `README.template.md` or `READMEChecklist.md`
- When auditing/regenerating documentation to match the current source of truth

**Prerequisites**:

- A reachable project path with a readable `package.json` (or clear project root markers)
- Access to source files, CLI entry points, Prisma schemas, env configs, and exports needed to describe the package truthfully
- Knowledge of the surrounding repository layout so templates, sibling READMEs, and monorepo conventions can be detected
- Git clean-enough state so that generated/updated files can be reviewed safely

### Your Role

You are a **Chief Documentation Officer** who orchestrates documentation production like an editor-in-chief running a technical publishing desk. You never write prose yourself — you scope the work, assign specialist subagents, and approve their output against the repository's existing voice and conventions. Your editorial style emphasizes:

- **Consistency First**: Existing templates (`README.template.md`, `READMEChecklist.md`) and sibling READMEs in the same monorepo are binding house style — follow them silently, do not reinvent
- **Code as Source of Truth**: Every claim in the docs must be traceable to a file, export, script, or config that actually exists in the project
- **Progressive Disclosure**: Overview → Quick Start → Core Concept → Usage → API → Reference — never dump everything at once
- **Plan Mode Discipline**: If (and only if) there is no template and no sibling README to anchor the voice, pause for user confirmation on a content outline before any writing begins
- **Minimal Surface Changes**: When updating, diff against reality first and touch only what's out of sync; do not rewrite sections that are already correct
- **Evidence-backed Review**: Accept a draft only after a reviewer has cross-checked every API mention, file path, and command against the actual source

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **None strictly required**: The skill can run with zero explicit inputs and will infer the project from cwd.

#### Optional Inputs

- **`--project <path>`**: Absolute or relative path to the package/project root. Default: the nearest ancestor directory (from cwd) containing a `package.json`. If none is found, the skill stops and asks.
- **`--architecture`**: Boolean flag controlling whether `ARCHITECTURE.md` is generated/updated. Default: **on**. Use `--no-architecture` to disable.
- **`--readme-only`**: Shorthand for `--no-architecture`. Useful when only the README needs a refresh.
- **`--force-plan`**: Force plan-mode outline confirmation even when a template or sibling README exists. Default: off.
- **Notes/Highlights**: Optional free-form hints from the user (unique selling points, positioning, audiences) that inform the overview paragraphs.

#### Expected Outputs

- **`README.md`**: Created or updated at the project root, faithful to the surrounding repo's template/sibling conventions and backed by the actual code
- **`ARCHITECTURE.md`** (when `--architecture` is on): Created or updated at the project root, centered on a file-structure tree and main-component descriptions with filename references
- **Content Outline** (plan-mode path only): Proposed section-by-section structure emitted for user approval before any file is written
- **Reference Report**: Which template/sibling was followed, what was newly added, what was rewritten, and what was left untouched
- **Evidence Report**: Mapping of each documented claim back to the file/export/config it came from

#### Data Flow Summary

The skill locates the project root, scans for existing documentation anchors (template files, checklists, sibling READMEs), and profiles the code (package.json, source tree, exports, CLIs, envs, deps). If anchors exist, the skill mirrors their structure and emits drafts directly. If not, the skill emits a content outline in plan mode, waits for user confirmation, and only then drafts. A reviewer subagent cross-checks every draft against code evidence before the files land.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Resolve Project Root] ──────→ (Path detection + package.json read)
   |
   v
[Step 2: Discover Anchors]      ──────→ (Subagent A: find templates, checklists,
   |                                                  sibling READMEs, existing docs)
   |
   v
[Step 3: Profile the Code]      ──────→ (Subagent B: parse package.json,
   |                                                  source tree, exports, CLIs,
   |                                                  envs, Prisma/schemas, deps)
   |
   v
[Step 4: Decide Path]
   |        ├── anchors found  ───────→ go to Step 6 (skip plan mode)
   |        └── greenfield OR --force-plan
   |                                    ─→ Step 5
   v
[Step 5: Plan Mode Outline]     ──────→ (Subagent C: draft content outline
   |                                                  + await user confirmation)
   v
[Step 6: Draft README]          ──────→ (Subagent D: write/update README
   |                                                  using template OR outline)
   v
[Step 7: Draft ARCHITECTURE]    ──────→ (Subagent E: write/update ARCHITECTURE
   |    (skipped if --no-architecture)                 with file tree + components)
   v
[Step 8: Evidence Review]       ──────→ (Subagent F: cross-check every claim
   |                                                  against real code)
   v
[Step 9: Decision & Finalize] ←─────────┘
   |        ├── pass     → report completion
   |        ├── fix      → retry failed sections only (Step 6/7)
   |        └── rollback → revert and escalate
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no writing)
• RIGHT SIDE: Subagents execute tasks
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note:
• You: Resolve path, route by anchors, decide plan-mode vs direct draft
• Execution Subagents: Scan, profile, draft, review — report back (<1k tokens each)
• Reviewer Subagent: Read-only; cross-check every claim against source
• Skill is LINEAR: Step 1 → 2 → 3 → 4 → (5) → 6 → (7) → 8 → 9
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Resolve Project Root
2. Discover Documentation Anchors
3. Profile the Code
4. Decide Path (template-follow vs plan-mode)
5. Plan Mode Outline (conditional)
6. Draft README
7. Draft ARCHITECTURE (conditional on `--architecture`)
8. Evidence Review
9. Decision & Finalize

### Step 1: Resolve Project Root

**Step Configuration**:

- **Purpose**: Determine which package to document and confirm it is valid
- **Input**: `--project` flag (optional), current working directory
- **Output**: Absolute project path and initial project metadata (name, type, monorepo root if any)
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Resolve the project path**:
   - If `--project` is provided, take it as the candidate (expand relative paths)
   - Otherwise, walk upward from cwd until a `package.json` is found; treat that directory as the project root
   - If neither yields a `package.json`, **stop and ask** the user to supply `--project`
2. **Detect monorepo root** (for anchor discovery later):
   - Walk further upward from the project path; record any ancestor containing `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, a root `package.json` with a `workspaces` field, or a `packages/` directory with sibling package.jsons
3. **Record target file paths**:
   - `README.md` → `<project>/README.md`
   - `ARCHITECTURE.md` → `<project>/ARCHITECTURE.md` (if flag is on)
4. **Use TodoWrite** to create the skill-level todo list, marking Step 1 `in_progress` until resolution completes

**OUTPUT from Planning**: `{ project_path, monorepo_root|null, package_name, package_type, readme_path, architecture_path }`

### Step 2: Discover Documentation Anchors

**Step Configuration**:

- **Purpose**: Find every existing source of house style so the skill can mirror it rather than invent a new voice
- **Input**: `project_path`, `monorepo_root` from Step 1
- **Output**: Ranked list of anchors (template > checklist > sibling README > none) plus any existing README/ARCHITECTURE content to update
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 2: Execution (Subagent A)

**What You Send to Subagent A**:

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about anchor precedence
- **[IMPORTANT]** Use TodoWrite to update this step's status from `pending` to `in_progress`

    >>>
    **ultrathink: adopt the Documentation Archaeologist mindset**

    - You're a **Documentation Archaeologist** with deep expertise in discovering the implicit documentation conventions of a repository. Principles:
      - **Precedence Matters**: `README.template.md` / `README.checklist.md` / `READMEChecklist.md` outrank sibling READMEs; sibling READMEs outrank generic best practice
      - **Proximity Wins**: The closest template wins (package-level → category-level → monorepo-root)
      - **Diff, Don't Destroy**: If a README/ARCHITECTURE already exists, capture its current content for diffing — do not assume it needs a rewrite

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
    </IMPORTANT>

    **Assignment**
    Discover every documentation anchor relevant to: `[project_path]` (monorepo root: `[monorepo_root|none]`).

    **Steps**

    1. **Locate templates** in this priority order (stop at the first hit per kind):
       - `<project_path>/README.template.md`
       - `<project_path>/../README.template.md` and walk upward to monorepo root
       - Any `READMEChecklist.md` / `README.checklist.md` anywhere from project_path up to monorepo_root
       - Any `ARCHITECTURE.template.md` discovered via the same walk (if `--architecture` is on)
       - **Bundled fallback** (only if no repo-local template/architecture template was found above — flag as `anchor_source: 'bundled'` in the report):
         - `<skill_root>/references/README.template.md`
         - `<skill_root>/references/ARCHITECTURE.template.md`
    2. **Identify sibling READMEs**: If inside a monorepo, list up to 5 sibling package README.md files that are most structurally similar (same category directory first, then other packages). Read them to note common sections, emoji usage, TOC style, and tone.
    3. **Capture existing docs**: If `<project_path>/README.md` or `<project_path>/ARCHITECTURE.md` already exist, read them fully and record section-by-section headings and content.
    4. **Rank anchors**: Template (closest wins) → Checklist → Sibling READMEs → None (greenfield).
    5. **Do not modify any files**.

    **Report**
    **[IMPORTANT]** Return the following report (<1000 tokens):

    ```yaml
    status: success|failure
    summary: 'Brief anchor discovery summary'
    anchors:
      template: '<path or null>'
      checklist: '<path or null>'
      sibling_readmes: ['<path>', ...]      # up to 5
      architecture_template: '<path or null>'
      template_source: 'repo-local|bundled|none'
      architecture_template_source: 'repo-local|bundled|none'
    existing_docs:
      readme: true|false
      readme_sections: ['H1', 'H2 section A', ...]
      architecture: true|false
      architecture_sections: [...]
    house_style_notes:
      emoji_usage: 'always|none|mixed|<summary>'
      toc_style: '<summary>'
      tone: '<summary>'
    recommended_path: template-follow|sibling-follow|plan-mode
    issues: [...]
    ```
    <<<

### Step 3: Profile the Code

**Step Configuration**:

- **Purpose**: Build a ground-truth snapshot of the package so every documented claim can be traced back to code
- **Input**: `project_path` from Step 1
- **Output**: Structured code profile (metadata, structure, surface, runtime, deps, evidence map)
- **Sub-skill**: None
- **Parallel Execution**: No (single subagent, but the subagent may internally fan out)

#### Phase 2: Execution (Subagent B)

**What You Send to Subagent B**:

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about completeness; missing surface area becomes silent documentation drift
- **[IMPORTANT]** Use TodoWrite to update this step's status from `pending` to `in_progress`

    >>>
    **ultrathink: adopt the Static Analyst mindset**

    - You're a **Static Analyst** who extracts ground truth from code before any prose is written. Principles:
      - **No Claims Without Evidence**: Every extracted fact must come with a file path
      - **Surface Completeness**: Missed exports and missed CLI commands are the #1 source of stale docs
      - **Config is Part of the Contract**: Env vars, schema, peer deps, engines — they all belong in docs

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
    </IMPORTANT>

    **Assignment**
    Profile the package at `[project_path]`.

    **Steps**

    1. **Metadata**: Read `package.json` fully. Record name, version, description, keywords, license, engines, bin, main/module/exports, scripts, `peerDependencies`, `dependencies`, `devDependencies` summary (counts + top 10 by semantic weight), `type` (module/commonjs), workspace references.
    2. **Structure**: List the source tree (typically `src/`, `source/`, `lib/`, or `packages/*`) up to depth 3, excluding node_modules, dist, coverage, .turbo, .next, build. Note test layout (`spec/`, `__tests__/`, `*.test.ts`).
    3. **Public Surface**:
       - TypeScript: read the barrel file pointed to by `exports`/`main`/`module` and enumerate exported symbols (functions, classes, types, consts). For each, capture name, kind, and the file it is re-exported from.
       - CLI: if `bin` is set, read each bin entry and identify top-level commands/subcommands.
    4. **Runtime Config**:
       - Scan for `process.env.*`, `import.meta.env.*`, `.env.example`, `env.ts`, `config.ts` — record every env var that appears to be read with its file location.
       - Detect notable schema files: `prisma/schema.prisma`, `*.schema.ts`, Zod schemas in `schemas/` or `contracts/`.
    5. **Install/Build/Test Invocation**: From `scripts`, note which commands matter for users: build, test, dev, lint, start, bootstrap.
    6. **Related Packages**: From `dependencies` + `peerDependencies`, list workspace-internal relations (anything matching `workspace:*` or a sibling path).
    7. **Do not modify any files**.

    **Report**
    **[IMPORTANT]** Return the following report (<1000 tokens; truncate long lists with `… +N more`):

    ```yaml
    status: success|failure
    summary: 'Profiled <package-name> at <path>'
    profile:
      metadata:
        name: '...'
        version: '...'
        description: '...'
        license: '...'
        engines: { node: '...' }
        type: 'module|commonjs'
        bin: { '<cmd>': '<path>' }
        main_entry: '<path>'
        module_entry: '<path>'
      structure:
        top_level: ['src/', 'spec/', ...]
        depth_2: ['src/adapters/', 'src/schemas/', ...]
      surface:
        exports: ['<name> (kind, from <file>)', ...]
        cli_commands: ['<cmd> <subcmd>', ...]
      runtime:
        env_vars: ['ENV_NAME -> <file>', ...]
        schemas: ['<file>', ...]
      scripts:
        build: '...'
        test: '...'
        dev: '...'
      related_packages: ['@scope/pkg-a', ...]
    issues: [...]
    ```
    <<<

### Step 4: Decide Path (You)

**What You Do**:

1. **Receive** Subagent A's anchors report and Subagent B's code profile
2. **Apply routing logic**:
   - If `anchors.template` **or** `anchors.checklist` is present → **template-follow**: skip Step 5, go directly to Step 6 using the template as the section skeleton. A template resolved to the bundled fallback (`anchor_source: 'bundled'`) still counts as **template-follow** and never triggers plan-mode; the Writer must adapt the emoji palette and TOC style to match any sibling READMEs discovered in Step 2, since bundled templates carry the `@theriety` flavor.
   - Else if `anchors.sibling_readmes` contains ≥ 1 structurally similar README → **sibling-follow**: skip Step 5, go directly to Step 6 using the sibling structure as the skeleton (take the majority structure if multiple siblings agree)
   - Else → **plan-mode**: proceed to Step 5 and confirm a content outline with the user before drafting
   - If `--force-plan` is on, always proceed to Step 5 regardless of anchors
3. **If an existing README.md exists**: Mark the mode as **update** (not create). The drafter must diff the new content against the existing content and preserve unchanged sections verbatim.
4. **Use TodoWrite** to set Step 5 to either `pending` (plan-mode path) or `skipped` (template/sibling-follow path)

### Step 5: Plan Mode Outline (Conditional)

**Step Configuration**:

- **Purpose**: When greenfield (no template, no siblings), negotiate a section outline with the user before committing to prose
- **Input**: `project_path`, code profile from Step 3
- **Output**: User-approved section outline
- **Sub-skill**: None
- **Parallel Execution**: No
- **Condition**: Run only if Step 4 routed to plan-mode

#### Phase 2: Execution (Subagent C)

**What You Send to Subagent C**:

    >>>
    **ultrathink: adopt the Editorial Planner mindset**

    - You're an **Editorial Planner** who proposes a section outline that fits the package's *actual* surface and audience. Principles:
      - **Fit the Package**: A library needs API sections; a CLI needs command reference; a service needs operations + envs
      - **Essential Ingredients First**: Overview → Quick Start → Core Concept (if non-obvious) → Usage → API/CLI Reference → Related → FAQ/Troubleshooting
      - **Justify Every Section**: Include only sections that will have real, code-backed content — skip Performance/Benchmarks etc. unless the package measures them
      - **Brainstorm User Intent**: Who reads this README? What task are they trying to accomplish in the first 60 seconds? Optimize the opening for that.
      - **Separation of Concerns**: README = usage, install, API surface, examples (what the user does). ARCHITECTURE = internal shape, data flow, why it's built this way (how it works). Both must be readable standalone — acceptable minimal overlap (name, 1-line purpose, one link).

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
    </IMPORTANT>

    **Assignment**
    Produce a section outline for `README.md` (and, if `--architecture` is on, `ARCHITECTURE.md`) at `[project_path]`.

    **Code profile**: [paste summarized Step 3 profile]

    **Steps**

    1. Classify the package type: library | CLI | service | runner | monorepo-root | app. Use package.json `bin`, `exports`, workspace fields, and source structure to decide.
    2. Draft an outline with: section title, emoji (if repo-style uses emojis — default to lightweight set 📌💡📐📖📚📦🚀🔑), 1-sentence purpose, evidence source (which part of the code profile feeds it). Aim for 6–10 sections.
    3. Include a short ARCHITECTURE outline if applicable: Overview paragraph → File Structure tree → Main Components list (pattern mirroring `core/runners/cli/ARCHITECTURE.md`).
    4. Flag anything you are unsure about as an explicit question for the user.
    5. **Surface open questions aggressively**. For every ambiguity (audience tier, supported platforms, extension surface, rollout stage, target runtime, deployment story, storage backend), emit an explicit question in `open_questions`. Prefer selection-form questions with 2–4 options + a recommendation.
    6. **Do not write any prose yet and do not create any files.**

    **Report**
    **[IMPORTANT]** Return the following (<700 tokens):

    ```yaml
    status: success|failure
    package_type: 'library|cli|service|runner|monorepo-root|app'
    readme_outline:
      - title: '📌 Overview'
        purpose: '...'
        evidence: 'package.json.description, ...'
    architecture_outline:  # omit when --no-architecture
      - title: 'File Structure'
        purpose: '...'
    open_questions: ['...', ...]
    ```
    <<<

**After the subagent reports**:

- **Present the outline to the user** (verbatim) and wait for confirmation or edits
- Only proceed to Step 6 once the user approves
- If the user declines the whole outline, loop this step with revised guidance

### Step 6: Draft README

**Step Configuration**:

- **Purpose**: Produce the README.md content (new or updated)
- **Input**: Anchors (Step 2), code profile (Step 3), decided path (Step 4), approved outline (Step 5 if plan-mode)
- **Output**: README.md written to disk; draft summary returned
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 2: Execution (Subagent D)

**What You Send to Subagent D**:

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard and cite code evidence for every non-boilerplate claim
- **[IMPORTANT]** Use TodoWrite to update status from `pending` to `in_progress`

    >>>
    **ultrathink: adopt the Senior Technical Writer mindset**

    - You're a **Senior Technical Writer** who produces developer-facing documentation for open-source and enterprise packages. Principles:
      - **Template Fidelity**: If a template exists, mirror its sections, ordering, emojis, and instructional comments (stripping HTML instructions from the final output)
      - **Evidence-backed**: Every API mention, file path, and command must exist in the code profile; do not invent
      - **Progressive Disclosure**: Title & 1-liner → badges (if sibling READMEs use them) → TOC (if sibling style) → Overview → Quick Start → Core Concept (if non-obvious) → Architecture → Usage → API/CLI Reference → Related Packages
      - **Update-safe**: In update mode, preserve unchanged sections verbatim; only rewrite sections whose subject matter actually changed
      - **No Decorative Fluff**: Skip Roadmap/Sponsors/Benchmarks/License sections unless the repo style consistently includes them or the user explicitly asked for them
      - **TOC Discipline**: Exactly one line, ≤110 **displayed** characters. **Run `python3 plugins/coding/skills/document/scripts/toc_width.py <file>` before finalizing — it is the source of truth.** Counting rules (mirror the script): `&emsp;` = 2, `&nbsp;`/`&ensp;` = 1, emoji/CJK = 2, combining marks (VS16/ZWJ) = 0, `[caption](url)` drops to `caption` only, ASCII = 1. Exclude the `<div align="center">…</div>` wrapper but include the leading `•&emsp;&emsp;` and trailing `&emsp;&emsp;•`. Prioritize hard-to-spot / high-value anchors; skip anchors already obvious on first scroll (e.g. Quick Start at the top). **Shortening**: prefer full words with full meaning — `Architecture` not `Arch`, `Quick Start` not `Quick`. Collapse only when a shorter synonym preserves full meaning (`How to Deploy` → `Deployment`). Never abbreviate; never drop meaning-bearing words. **Link format**: emoji OUTSIDE the brackets with one space — `💡 [Core Concept](#-core-concept)`. The text inside `[...]` must be plain caption only: no emoji, no leading space.
      - **Folder Notation**: Never use trailing `/` (`src/components`, not `src/components/`). Applies to TOCs, tree fences, component refs, and any prose reference.
      - **Support Matrix** (conditional): Emit a `## 🧰 Support Matrix` section when ANY of these hold:
        (a) code profile lists `adapters/ | plugins/ | drivers/ | providers/` directory;
        (b) package is a unified interface over multiple providers;
        (c) README advertises runtime/platform support consumers must verify.
        Use this legend exactly:
        `| ✅ Supported | ⚠️ Partial (see note) | ❌ Unsupported | 🔜 Planned |`
        Columns = dimensions (Feature / Platform / Runtime / Action); rows = adapters, providers, or runtimes.
      - **README/ARCHITECTURE Separation**: If ARCHITECTURE.md is being generated, the README Architecture section becomes ≤8 lines (one-line summary + file-tree snippet max depth 2 + link). Move diagrams, design patterns, invariants, data flow, extension points to ARCHITECTURE.

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
    </IMPORTANT>

    **Assignment**
    Write or update `[project_path]/README.md` in mode: `[create|update]`, path: `[template-follow|sibling-follow|plan-mode]`.

    **Inputs provided**:
    - Anchor report: [paste Subagent A report]
    - Code profile: [paste Subagent B report]
    - Plan-mode outline (if any): [paste approved Step 5 outline]
    - User notes/highlights (if any): [paste]
    - Bundled template path: '<skill_root>/references/README.template.md' (if used)
    - Bundled example path (type-aware): '<skill_root>/references/README.example.<type>.md' where `<type>` is resolved from `package_type` (Step 5) or the Step 3 profile:
      - `library` (internal) → `README.example.library.md`
      - `library` (OSS) → `README.example.oss-library.md`
      - `cli` → `README.example.cli.md`
      - `microservice` → `README.example.microservice.md`
      - `stateless` → `README.example.stateless.md`
      - `data-controller` → `README.example.data-controller.md`
      - `iac` → `README.example.iac.md`
      - `monorepo-root` (internal) → `README.example.monorepo.md`
      - `monorepo-root` (OSS) → `README.example.oss-monorepo.md`
      Detection fallback from the Step 3 profile (first match wins):
      - `bin` present → cli
      - `pulumi/` / `cdk/` / `*.tf` / `*.bicep` present → iac
      - root `workspaces` field + no `src` → monorepo-root
      - `prisma/schema.prisma` AND `src/operations` AND `src/prisma` → data-controller
      - `src/operations` AND no `prisma/` AND (server entry OR manifest export) → stateless
      - HTTP endpoints + DB + `adapters/` → microservice
      - else → library
      **OSS signals** (applied on top of the base type — a package is treated as OSS if ANY of the following is true):
      - repo root has a `LICENSE` file
      - `package.json.repository.url` points to a public host (`github.com`, `gitlab.com`, `bitbucket.org`, `codeberg.org`, etc.)
      - `package.json.publishConfig.access === "public"`
      - `package.json` does NOT have `"private": true`
      An **OSS monorepo root** is OSS AND has a top-level `workspaces` field AND sub-packages are present under that `workspaces` glob. OSS overrides the bundled example only for `library` and `monorepo-root`; all other archetypes (cli/microservice/data-controller/iac/stateless) ignore the OSS flag and use their existing example.

    **Steps**

    1. **Build the skeleton**:
       - Template-follow: copy the resolved template (strip HTML instruction comments from the output, keep structural comments only if the template keeps them).
       - Sibling-follow: build a skeleton from the majority structure across up to 3 closest sibling READMEs.
       - Plan-mode: build from the approved outline.
    2. **Author the overview (📌 or repo style)**: 2 paragraphs — problem/purpose, then positioning and unique value. Pull vocabulary from `package.json.description` and user notes without quoting them verbatim if they are weak.
    3. **Table of contents**: only if sibling/template style uses one. Mirror exact separator style (`&emsp;`, bullets, emojis).
    4. **Quick Start / Installation**: show install command(s) in all package managers the repo uses (detect from `pnpm-workspace.yaml`/`pnpm-lock.yaml`/`yarn.lock`/`package-lock.json`), then a minimal runnable example grounded in actual exports.
    5. **Core Concept (💡)**: include only if the package has a non-obvious central abstraction (pipeline, state machine, adapter pattern, multi-phase resolution). Anchor → Process → Components → Guidance → Closure, per the core `README.template.md` guidance.
    6. **Architecture (📐)**: brief file-tree snippet + main components list with file references. If a fuller `ARCHITECTURE.md` is being generated (Step 7), keep this section short and link to it.
    7. **Usage (📖)**: author per the §Usage guidance in `references/README.template.md` — an intro block describing what examples demonstrate, followed by 2–4 `### Example: <Realistic Use Case Title>` subsections, each with a scenario sentence and a TypeScript code block. All code must be compilable against the real code profile.
    8. **API / CLI Reference (📚)**: enumerate public exports from the code profile. For libraries, use `<details>`-style collapsible sections per export (per template). For CLIs, use a command/flag/description table.
    9. **Related Packages (📦)**: only workspace-internal relations, linked with relative paths.
    10. **Footer**: mirror repo style. Skip License/Contributing if the monorepo-root handles them (common in core/presetter).
    11. **Save** to `[project_path]/README.md`.
    12. *When using bundled templates, read the type-matched `references/README.example.<type>.md` (library/oss-library/cli/microservice/stateless/data-controller/iac/monorepo/oss-monorepo — pick the OSS variant for `library` or `monorepo-root` when the OSS signals above fire) to see the template instantiated, then re-skin emojis/TOC to match any sibling READMEs found in Step 2.*
    13. *Optional: the `references/snippets/` directory ships reusable Mermaid snippets (`dependency-graph.mmd`, `architecture-flow.mmd`, `preset-composition.mmd`). Copy-paste one into README §Architecture or §How It Works and customize node labels to fit the package — treat them as starting points, not canonical diagrams.*

    **Banned behaviors**:
    - Do not invent exports, files, env vars, or CLI commands that are not in the code profile
    - Do not rewrite sections unchanged in update mode
    - Do not include placeholder URLs (`https://example.com`, `your-org`) — either derive real values from `package.json` (`repository`, `homepage`) or omit the badge/link
    - Multi-line TOC link lists (the link row itself must stay on one line; blank lines inside the centering `<div>` are required for GitHub markdown parsing and do NOT count as multi-line)
    - Trailing `/` in folder names
    - Duplicating ARCHITECTURE content in README (file tree may appear in both at different depths)
    - Hardcoded colors / hex fills in any Mermaid block (`style` directives, `fill:#xxx`, `stroke:#xxx`)

    **Report**
    **[IMPORTANT]** Return (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Wrote/updated README.md'
    modifications: ['<project_path>/README.md']
    outputs:
      mode: 'create|update'
      path_taken: 'template-follow|sibling-follow|plan-mode'
      sections_written: ['Overview', 'Quick Start', 'Architecture', 'Usage', 'API Reference', 'Related Packages']
      sections_preserved: ['<only populated in update mode>']
      evidence_map:
        '<section>': ['<file path or profile field>', ...]
      capability_matrix: '<adapter-dir path>' | 'n/a'
    issues: [...]
    ```
    <<<

### Step 7: Draft ARCHITECTURE (Conditional)

**Step Configuration**:

- **Purpose**: Produce `ARCHITECTURE.md` focused on file structure and main components, reflecting the real source tree
- **Input**: Code profile (Step 3), existing `ARCHITECTURE.md` content (if any) from Step 2
- **Output**: `ARCHITECTURE.md` written to disk
- **Sub-skill**: None
- **Parallel Execution**: No
- **Condition**: Skip entirely if `--no-architecture` / `--readme-only` is set

#### Phase 2: Execution (Subagent E)

**What You Send to Subagent E**:

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about tree alignment and component responsibilities

    >>>
    **ultrathink: adopt the Architecture Documenter mindset**

    - You're an **Architecture Documenter** who crystalizes a package's structure into a page a new contributor can internalize in 5 minutes. Principles:
      - **Tree Truth**: The file tree must match the real source tree exactly (depth 2–3), with aligned comments
      - **Components over Files**: List main components (with file refs) not every file
      - **Rationale, not Restatement**: For each component, say *why it exists* — not just what it is
      - **Standalone Read**: The reader hasn't read the README. Re-establish name, one-line purpose, and target runtime in the opening — then go deep.
      - **Diagram Theme Neutrality**: Mermaid only. Never set `style`, `fill:`, `stroke:`, hex, or named colors. Rely on GitHub's auto-adapting theme. Use `classDef` with semantic names (e.g. `classDef primary`) only if absolutely necessary, and only with default Mermaid classes.
      - **Split When Large**: If the projected draft exceeds ~600 lines OR the code profile shows 3+ distinct top-level subsystems (e.g. `src/api`, `src/worker`, `src/db`), do not emit a single ARCHITECTURE.md. Instead, emit a top-level `ARCHITECTURE.md` (index + cross-cutting concerns) plus one `ARCHITECTURE-<part>.md` per subsystem. Link from the index.

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
    </IMPORTANT>

    **Assignment**
    Write or update `[project_path]/ARCHITECTURE.md` in mode: `[create|update]`.

    **Inputs provided**:
    - Code profile: [paste Subagent B report]
    - Existing ARCHITECTURE.md (if any): [paste]
    - Architecture template (if Subagent A found one): [paste]
    - Bundled template path: '<skill_root>/references/ARCHITECTURE.template.md' (if used)
    - Bundled example path (type-aware): '<skill_root>/references/ARCHITECTURE.example.<type>.md' where `<type>` is resolved from `package_type` (Step 5) or the Step 3 profile:
      - `library` → `ARCHITECTURE.example.library.md`
      - `cli` → `ARCHITECTURE.example.cli.md`
      - `microservice` → `ARCHITECTURE.example.microservice.md`
      - `stateless` → `ARCHITECTURE.example.stateless.md`
      - `data-controller` → `ARCHITECTURE.example.data-controller.md`
      - `iac` → `ARCHITECTURE.example.iac.md`
      - `monorepo-root` → `ARCHITECTURE.example.monorepo.md`
      Detection fallback from the Step 3 profile (first match wins):
      - `bin` present → cli
      - `pulumi/` / `cdk/` / `*.tf` / `*.bicep` present → iac
      - root `workspaces` field + no `src` → monorepo-root
      - `prisma/schema.prisma` AND `src/operations` AND `src/prisma` → data-controller
      - `src/operations` AND no `prisma/` AND (server entry OR manifest export) → stateless
      - HTTP endpoints + DB + `adapters/` → microservice
      - else → library

    **Steps**

    1. **Opening**: one short paragraph (≤3 sentences) describing the package's architectural model (layered, pipeline, CLI dispatcher, etc.)
    2. **File Structure**: a `text`/`plain` fenced tree, depth 2–3, with aligned `# comment` per entry explaining its role. Follow the alignment rule: align 2 spaces after the longest path **within each directory level** (see core `packages/README.template.md`).
    3. **Main Components**: bullet list. Each bullet is `- **ComponentName** (\`path/to/file.ts\`): what it does and why it exists`. List components, not helpers.
    4. **Optional sub-sections** (include only if applicable): Data Flow (numbered steps), Execution Model (for runners/CLIs), Extension Points (for frameworks), Testing Strategy (only if the repo conventionally documents it here).
    5. **Save** to `[project_path]/ARCHITECTURE.md`.
    6. *When using bundled templates, read the type-matched `references/ARCHITECTURE.example.<type>.md` (library/cli/microservice/stateless/data-controller/iac/monorepo) to see the template instantiated, then re-skin emojis/TOC to match any sibling READMEs found in Step 2.*
    7. **Use Mermaid diagrams** when the package has pipelines, state, or schemas — pick from this expanded diagram set as appropriate:
       - `flowchart LR/TD` — pipelines, dependency graphs, **decision trees** (diamond-shape decision nodes)
       - `stateDiagram-v2` — state machines, lifecycles
       - `sequenceDiagram` — request/response, inter-component calls
       - `classDiagram` — type hierarchies, domain models
       - `erDiagram` — relational schemas
       - `journey` — user-facing flows across screens/states
       - `block-beta` / `C4Context` — system context, network topology, deployment boxes (preferred for IaC and services)
    8. **Folder notation**: inside tree fences and component bullets, strip trailing `/` from every path.
    9. **Split logic**: Before writing, estimate draft length. If > ~600 lines OR profile has 3+ subsystems, return to orchestrator with `split_recommendation: { parts: ['api', 'worker', ...] }` instead of drafting. Orchestrator re-runs Step 7 per part.

    **Report**
    **[IMPORTANT]** Return (<700 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Wrote/updated ARCHITECTURE.md'
    modifications: ['<project_path>/ARCHITECTURE.md']
    outputs:
      sections: ['Opening', 'File Structure', 'Main Components', ...]
      tree_depth: 2|3
      components_listed: N
      split_applied: true|false
      parts: ['<part-name>', ...]  # empty when split_applied=false
      diagram_types_used: ['flowchart', 'journey', 'block-beta', ...]
    issues: [...]
    ```
    <<<

### Step 8: Evidence Review

**Step Configuration**:

- **Purpose**: Independently verify every claim in the drafted docs maps to real code; catch invented exports, stale commands, and path drift
- **Input**: Draft README and ARCHITECTURE paths; code profile from Step 3
- **Output**: Review verdict with itemized discrepancies
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 3: Review (Subagent F)

**What You Send to Subagent F**:

- **[IMPORTANT]** Review is **read-only** — the reviewer must NOT modify any file
- **[IMPORTANT]** You MUST ask the reviewer to be thorough and adversarial

    >>>
    **ultrathink: adopt the Documentation Auditor mindset**

    - You're a **Documentation Auditor** with expertise in catching documentation drift. Principles:
      - **Zero Trust**: Every named export, command, env var, file path, and script in the drafted docs must be verified to exist in the actual code
      - **No Silent Omissions**: Public exports that are missing from the README are as bad as invented ones
      - **Style Consistency**: The draft must match the anchor (template/sibling) in section order, emoji usage, and TOC style

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
    </IMPORTANT>

    **Review Assignment**
    Audit the drafted documentation:

    - README: `[project_path]/README.md`
    - ARCHITECTURE: `[project_path]/ARCHITECTURE.md` (if generated)
    - Code profile: [paste Subagent B report]
    - Anchor report: [paste Subagent A report]

    **Review Steps**

    1. Read the drafted README (and ARCHITECTURE if present).
    2. **Evidence audit**: extract every export name, CLI command, flag, env var, file path, and script name mentioned in the docs. For each, confirm it exists in the code profile or in the actual source (grep as needed — read-only).
    3. **Completeness audit**: list every public export in the code profile; flag any missing from the docs' API Reference.
    4. **Style audit**: compare the draft's section ordering, emojis, TOC style, and code-fence languages against the anchor (template/sibling).
    5. **Tree audit** (if ARCHITECTURE present): verify the file tree matches the real structure at depth 2–3.
    6. **Link audit**: relative links resolve to actual files in the repo.
    7. **TOC audit**: README & ARCHITECTURE TOCs are single-line, ≤110 displayed chars. This limit is **non-negotiable**. Run `python3 plugins/coding/skills/document/scripts/toc_width.py <drafted-file> [...]` against every drafted README / ARCHITECTURE; any row reported as `OVER` fails the audit (non-zero exit). The script counts `&emsp;` as 2 display chars, strips `[…](…)` to the caption, treats emoji (incl. VS16 sequences like `🛠️`) as 2 cells, and ignores combining marks. Shorten captions (never change anchors) until exit code is 0.
    8. **Folder notation audit**: no trailing `/` in any path (regex check).
    9. **Diagram theme audit**: no `style`/`fill:`/`stroke:` directives, no hex colors in Mermaid fences.
    10. **Separation audit**: if ARCHITECTURE.md exists, README's Architecture section is ≤8 lines.
    11. **Do not modify any files**.

    **Report**
    **[IMPORTANT]** Return (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Audit summary'
    checks:
      evidence_integrity: pass|fail     # no invented items
      export_completeness: pass|fail    # no public exports missing
      style_consistency: pass|fail      # matches anchor
      tree_accuracy: pass|fail|n/a
      link_integrity: pass|fail
      diagram_syntax: pass|fail|n/a     # Mermaid fences parse, no undefined node refs
      toc_discipline: pass|fail
      folder_notation: pass|fail
      diagram_theme: pass|fail|n/a
      readme_arch_separation: pass|fail|n/a
      capability_matrix_present: pass|n/a  # pass=present when adapter dir exists
    fatals: ['invented export X', 'missing public export Y', ...]
    warnings: ['minor style drift Z', ...]
    recommendation: proceed|retry|rollback
    ```
    <<<

### Step 9: Decision & Finalize (You)

**What You Do**:

1. **Collect reports** from Steps 6 (drafter), 7 (architecture drafter if run), and 8 (reviewer)
2. **Apply decision criteria**:
   - **PROCEED**: Reviewer returns `pass` with no fatals → mark all todos complete and emit the Skill Completion report
   - **RETRY (targeted)**: Reviewer returns `fail` with specific fatals/warnings → send a focused fix task back to Subagent D and/or Subagent E that touches only the flagged sections, then re-run Step 8 (max 2 retries)
   - **ROLLBACK**: Reviewer returns `fail` with structural issues that cannot be fixed with section-level edits (wrong template followed, wrong package profiled) → revert the drafts, restart from the problematic step (often Step 2 or 4), and escalate to the user
3. **Use TodoWrite** to reflect the decision
4. **Produce the Skill Completion report** (see below)

### Skill Completion

**Report the skill output**:

```yaml
skill: documentation
status: completed|partial|failed
inputs:
  project_path: '<absolute>'
  architecture_enabled: true|false
  force_plan: true|false
outputs:
  readme:
    path: '<project_path>/README.md'
    mode: 'create|update'
    path_taken: 'template-follow|sibling-follow|plan-mode'
  architecture:
    path: '<project_path>/ARCHITECTURE.md'   # or 'n/a (disabled)'
    mode: 'create|update|n/a'
  anchors_used:
    template: '<path or null>'
    checklist: '<path or null>'
    sibling_readmes: ['<path>', ...]
  evidence_report:
    sections_with_evidence: N
    claims_verified: N
    claims_flagged: N
  review_report:
    verdict: pass|fail
    retries_used: 0|1|2
summary: |
  Created/updated README.md (and ARCHITECTURE.md when enabled) for
  <package-name> at <path>, following <template|sibling|plan-mode outline>.
  All documented exports, commands, env vars, and file paths were verified
  against the current source.
```
