---
name: sync-spec
description: Materialize a hard local copy of a Notion specification page tree (root SPEC.md + recursive child pages + leaf-only linked pages) into a target directory, with INDEX.md, frontmatter on every file, and a .gitignore at the bundle root. Hard-gates on root SPEC.md persistence. Use when downloading a Notion spec to disk, mirroring a Notion spec page tree locally, pulling a spec bundle for a ticket, refreshing a stale .code-spec bundle, or any time a guaranteed-on-disk copy of a Notion spec is needed before downstream analysis or codegen.
model: opus
context: fork
agent: general-purpose
allowed-tools: Read, Grep, Glob, Bash, Task, TodoWrite, mcp__plugin_specification_notion__notion-fetch, mcp__plugin_specification_notion__notion-search
argument-hint: <notion-url-or-id> [--spec-path=<dir>]
---

# Sync Spec

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Download a Notion specification page tree to disk as a self-contained markdown bundle. Always wipes and re-downloads — this skill never caches, never merges, never preserves prior contents. Hard-gates on root `SPEC.md` persistence: if the root spec cannot be saved locally, the skill refuses with a structured reason and writes nothing else.

**When to use**:

- When the user asks to download or pull a Notion spec to disk
- When a ticket's `.code-spec/<slug>/` bundle is stale and needs a fresh copy
- When mirroring a Notion spec page tree locally before downstream codegen, audit, or review
- When any caller needs a guaranteed-on-disk hard copy of a Notion spec before proceeding
- When refreshing a local spec bundle to pick up Notion-side edits

**Prerequisites**:

- Notion MCP access for the target workspace and page (`notion-fetch`, `notion-search`)
- Write access to the resolved `<spec-path>` directory
- A working directory inside (or under) a project (so `<spec-path>` defaults can resolve to a project root); otherwise falls back to `<CWD>/.code-spec`

### Your Role

You are a **Spec Bundle Operator** who orchestrates a single Notion-fetch specialist subagent and validates the on-disk result. You never write Notion data yourself — every page conversion happens inside the dispatched subagent. Your responsibilities are:

- **Path Discipline**: Resolve `<spec-path>` deterministically (project-root walk-up, then CWD fallback) and refuse to operate outside the project tree
- **Wipe Discipline**: Always wipe `<spec-path>` before the fetch — no caching, no merging, no preservation
- **Hard-Gate Authority**: After dispatch, verify `<spec-path>/SPEC.md` is present and non-empty; refuse the entire skill if not
- **Zero Direct Writes**: You never run `mcp__notion-fetch` for content — your tool surface is path validation, wipe, gitignore, and final verification
- **Faithful Reporting**: Emit a single YAML completion report describing every file persisted, with refusal reasons surfaced explicitly when applicable

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **`<notion-url-or-id>`**: Full Notion URL or bare 32-char hex id of the root spec page. Dashes are stripped during normalization.

#### Optional Inputs

- **`--spec-path=<dir>`**: Directory to write the bundle into. **Default**: walk up from CWD to the closest project root (first ancestor containing any of `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) and use `<root>/.code-spec`. If no project root marker is found anywhere up to the filesystem root, fall back to `<CWD>/.code-spec`.

There are NO other arguments. There is **no** `--use-cache`, **no** `--repo`, **no** `--slug`, and **no** sync mode. The skill always wipes and re-downloads.

#### Expected Outputs

- **Bundle on disk** at `<spec-path>/`:
  - `SPEC.md` — root page (hard-gated; missing/empty causes refusal)
  - `INDEX.md` — tree-of-contents listing every file with kind/title/notion_id/summary
  - `children/*.md` — recursive child pages (only present if any exist)
  - `linked/*.md` — leaf-only linked pages from inline mentions (only present if any exist)
  - `.gitignore` — single line `*`, idempotent (never overwrites an existing gitignore)
- **Frontmatter on every markdown file**: `notion_id`, `title`, `url`, `kind: spec|child|linked`, `fetched_at`
- **Completion Report (YAML)**: `status` (`completed` | `refused`), refusal `reason` if applicable, `outputs.notion`, `outputs.spec_bundle.spec_path`, `outputs.spec_bundle.index_path`, `outputs.spec_bundle.files[]`

#### Data Flow Summary

The skill takes a Notion URL or id, normalizes it to a 32-char hex id, resolves an absolute `<spec-path>` (project-root walk-up with CWD fallback), safety-checks that the path is inside the resolved project root or under CWD, wipes the directory, writes a `*` gitignore (only if absent), dispatches one Notion Bundle Specialist subagent to recursively fetch root + child pages and leaf-only linked pages with frontmatter and INDEX.md, hard-gate verifies that `<spec-path>/SPEC.md` exists and is non-empty, and emits a YAML completion report. There is no caching, no merge, no second pass.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                                  SUBAGENT
(Orchestrates Only)                     (Performs Notion Fetch)
   |                                         |
   v                                         v
[START]
   |
   v
[Step 1: Resolve & Normalize]
   |    • strip dashes, validate 32-char hex
   |    • walk up to project root for <spec-path>
   |    • refuse on invalid_id
   v
[Step 2: Wipe & Prepare]
   |    • safety check: path inside project root OR under CWD
   |    • Bash rm -rf <spec-path>
   |    • mkdir -p <spec-path>
   |    • ALWAYS wipes (no cache, ever)
   v
[Step 3: Auto-write .gitignore]
   |    • single line `*`
   |    • only if file does not already exist
   v
[Step 4: Notion Bundle Fetch] ───────→ (Notion Bundle Specialist subagent)
   |                                    • root → SPEC.md
   |                                    • children/ recursive
   |                                    • linked/ leaf-only (from inline mentions)
   |                                    • frontmatter + INDEX.md
   v
[Step 5: Hard-Gate Verification]  *** HARD GATE ***
   |    • Bash test -s <spec-path>/SPEC.md
   |    • subagent failure OR SPEC.md missing/empty → refuse
   |    • partial + SPEC.md ok → completed (warnings)
   |    • partial + SPEC.md missing/empty → refuse (downgrade)
   |    • success + SPEC.md ok → completed
   v
[Step 6: Skill Completion Report]
   |    • emit YAML
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You orchestrate (path discipline + wipe + verify)
• RIGHT SIDE: Subagent performs all Notion fetch + markdown writes
• ARROWS (───→): You dispatch work
• Step 5 is the HARD GATE — no completed status without SPEC.md on disk
• Skill is LINEAR: 1 → 2 → 3 → 4 → 5 → 6
• On invalid_id (Step 1) or refusal at Step 5: jump straight to Step 6
═══════════════════════════════════════════════════════════════════

Note:
• You: Resolve, wipe, gitignore, hard-gate, report
• Subagent: All Notion MCP fetches + all markdown writes (1 dispatch)
• No caching: every invocation is a fresh download
• No merging: pre-existing contents at <spec-path> are deleted
```

### Skill Steps

1. Resolve & Normalize (You) — strip dashes, validate 32-char hex, resolve `<spec-path>`
2. Wipe & Prepare (You) — safety check + `rm -rf` + `mkdir -p`
3. Auto-write `.gitignore` (You) — single `*` line, only if absent
4. Notion Bundle Fetch (Subagent) — recursive fetch + INDEX.md
5. Hard-Gate Verification (You) — `test -s <spec-path>/SPEC.md`
6. Skill Completion Report (You) — emit YAML

## 3. SKILL IMPLEMENTATION

### Step 1: Resolve & Normalize

**Step Configuration**:

- **Purpose**: Normalize the Notion id to 32-char hex and resolve an absolute `<spec-path>` deterministically. Refuse on malformed input before any disk mutation.
- **Input**: `<notion-url-or-id>`, optional `--spec-path=<dir>`
- **Output**: `notion_id` (32-char hex), `spec_path` (absolute), `project_root` (absolute or null)
- **Sub-skill**: None
- **Parallel Execution**: No

#### Actions (You)

1. **Receive inputs** from invocation; parse `<notion-url-or-id>`:
   - If a full URL, extract the trailing id segment
   - Strip all dashes
   - Validate the result is exactly 32 hex characters (`/^[0-9a-f]{32}$/i`)
   - **On validation failure**: set `status=refused`, `reason=invalid_id`, jump to Step 6. Do NOT wipe. Do NOT dispatch subagent.
2. **Resolve `<spec-path>`**:
   - If `--spec-path=<dir>` provided: take it as-is, resolve to absolute path
   - Otherwise: walk up from CWD looking for the first ancestor containing any of `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`
     - If found: `spec_path = <root>/.code-spec`
     - If no marker found anywhere up to filesystem root: `spec_path = <CWD>/.code-spec` (fallback)
   - Record `project_root` (the resolved root, or null if fallback fired)
3. **Use TodoWrite** to seed todos for Steps 2–6 (`wipe-prepare`, `write-gitignore`, `notion-fetch`, `hard-gate-verify`, `completion-report`).
4. Cache `notion_id`, `spec_path`, `project_root` for downstream steps.

### Step 2: Wipe & Prepare

**Step Configuration**:

- **Purpose**: Guarantee a clean target directory before fetch. Always wipes — no caching, no preservation. Safety-checked against path escapes.
- **Input**: `spec_path`, `project_root` (from Step 1)
- **Output**: `<spec-path>` exists, empty, writable
- **Sub-skill**: None
- **Parallel Execution**: No

#### Actions (You)

1. **Safety check**: `spec_path` MUST be inside the resolved `project_root` OR under CWD.
   - Compute the absolute, normalized form of `spec_path`
   - Confirm it begins with `<project_root>/` (when `project_root` is non-null) OR with `<CWD>/`
   - **On failure** (path escapes both): set `status=refused`, `reason=spec_bundle_unavailable`, attach a one-line explanation in `issues`, jump to Step 6. Do NOT wipe.
2. **Wipe** via Bash: `rm -rf <spec-path>` — unconditional. This deletes any prior bundle, junk files, or partial downloads. There is no caching path; every invocation starts from a clean slate.
3. **Recreate** via Bash: `mkdir -p <spec-path>`.
4. Update TodoWrite: mark `wipe-prepare` as `completed`.

### Step 3: Auto-write `.gitignore`

**Step Configuration**:

- **Purpose**: Ensure `<spec-path>/.gitignore` contains a single `*` line so bundles never accidentally land in git history. Idempotent.
- **Input**: `spec_path`
- **Output**: `<spec-path>/.gitignore` exists with content `*`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Actions (You)

1. Check whether `<spec-path>/.gitignore` already exists (Bash `test -e`).
2. **If absent**: write a single line `*` (newline-terminated) into `<spec-path>/.gitignore`.
3. **If present**: leave untouched. Never overwrite a user-managed gitignore. Record this in `issues` only if the existing file is empty (no `*` rule), as an advisory.
4. Update TodoWrite: mark `write-gitignore` as `completed`.

### Step 4: Notion Bundle Fetch

**Step Configuration**:

- **Purpose**: Dispatch one Notion Bundle Specialist subagent to fetch the root page, recurse through child pages, leaf-fetch any linked pages discovered via inline mentions, write frontmatter to every file, and produce `INDEX.md`.
- **Input**: `notion_id`, `spec_path`
- **Output**: `spec_bundle` = `{ spec_path, index_path, files[], cache_hit: false }`
- **Sub-skill**: None (uses Notion MCP via subagent)
- **Parallel Execution**: Yes — child-page fetches dispatch in parallel batches inside the subagent

#### Phase 1: Planning (You)

1. Confirm `<spec-path>` exists and is empty (sanity check after Step 2).
2. Update TodoWrite: mark `notion-fetch` as `in_progress`.
3. Prepare a single Notion Bundle Specialist task assignment.

**OUTPUT from Planning**: One queued subagent task to fetch + walk + index the bundle.

#### Phase 2: Execution (Subagent)

In a single message, you spin up one Notion Bundle Specialist subagent (`general-purpose`).

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about faithful mirroring and recursion semantics
- **[IMPORTANT]** Use TodoWrite to keep `notion-fetch` as `in_progress` until the subagent reports back
- **[IMPORTANT]** Do NOT recurse into linked pages — they are fetched as leaves only

Request the subagent to perform the following fetch and write:

    >>>
    **ultrathink: adopt the Notion Bundle Specialist mindset**

    - You're a **Notion Bundle Specialist**:
      - **Faithful Mirroring**: Convert each Notion page to clean markdown preserving headings, lists, code blocks, tables, and links
      - **Recursive on Children, Leaf-Only on Links**: Recurse fully through `child_page` / `child_database` blocks (no depth cap). Linked-page references are fetched as leaves only — never recursed.
      - **Deduplicate by Notion ID**: Each unique page is written once even if referenced multiple times

    **Assignment**

    - Bundle root: `<spec_path>` (absolute path)
    - Root page: `<notion_id>`
    - Linked-page seeds: any inline `mention` blocks discovered while fetching root + child pages (no external seed list)

    **Steps**

    1. Fetch the root page; convert to markdown; save to `<spec_path>/SPEC.md`
    2. Walk child blocks for `child_page` and `child_database` references; for each, fetch + save to `<spec_path>/children/<slug-of-title>.md`. Recurse fully (no depth cap).
    3. Resolve linked-page mentions in property values (the four seeds above, plus any inline `mention` blocks); save unique linked pages to `<spec_path>/linked/<slug>.md` (skip duplicates by Notion id). Linked pages are leaves — do NOT recurse into them.
    4. **Frontmatter on every file**: `notion_id`, `title`, `url`, `kind: spec|child|linked`, `fetched_at`
    5. Build `<spec_path>/INDEX.md`: a one-line-per-file index with kind, title, relative path, and a one-sentence summary (extracted from the page's first paragraph)

    **Report**

    ```yaml
    status: success|partial|failure
    outputs:
      spec_bundle:
        root_path: '<abs path>'
        index_path: '<abs path>/INDEX.md'
        cache_hit: false
        files:
          - kind: spec|child|linked
            notion_id: '...'
            title: '...'
            path: '<rel path>'
            summary: '<one-liner>'
    issues: []
    ```
    <<<

#### Phase 4: Decision (You)

1. Parse the subagent's YAML report.
2. Cache `spec_bundle` (rename `root_path` to `spec_path` in your internal state for the completion report).
3. Note the subagent's `status` (`success` | `partial` | `failure`); the actual gating happens in Step 5 against the on-disk file, not the subagent's self-report.
4. Update TodoWrite: mark `notion-fetch` as `completed`.

### Step 5: Hard-Gate Verification

**Step Configuration**:

- **Purpose**: Defence-in-depth verification that the on-disk bundle has a non-empty root `SPEC.md`. This is the hard gate that distinguishes `completed` from `refused`. The subagent's self-reported status is advisory; the filesystem is authoritative.
- **Input**: `spec_path`, subagent's reported `status`
- **Output**: `final_status` (`completed` | `refused`), `final_reason` (when refused)
- **Sub-skill**: None
- **Parallel Execution**: No

#### Actions (You)

1. Run `Bash test -s <spec-path>/SPEC.md` to confirm the file exists and is non-empty.
2. Apply the decision matrix:

   | Subagent status | `SPEC.md` present non-empty? | Outcome                                                                                       |
   |-----------------|-------------------------------|-----------------------------------------------------------------------------------------------|
   | `failure`       | (any)                         | `status=refused`, `reason=spec_bundle_unavailable` — jump to Step 6                            |
   | `partial`       | No                            | Downgrade: `status=refused`, `reason=spec_bundle_unavailable` — jump to Step 6                 |
   | `partial`       | Yes                           | `status=completed` with warnings — surface missing-children list in `issues`                  |
   | `success`       | No                            | Treat as failure: `status=refused`, `reason=spec_bundle_unavailable` — jump to Step 6          |
   | `success`       | Yes                           | `status=completed`                                                                            |

3. Cache `final_status` and `final_reason` for the completion report.
4. Update TodoWrite: mark `hard-gate-verify` as `completed`.

### Step 6: Skill Completion Report

**Step Configuration**:

- **Purpose**: Emit the canonical YAML completion report. Always runs — even on refusal — so callers receive a structured outcome.
- **Input**: `notion_id`, `spec_path`, `spec_bundle` (when available), `final_status`, `final_reason`
- **Output**: YAML block to stdout
- **Sub-skill**: None
- **Parallel Execution**: No

#### Actions (You)

Emit the following YAML. Populate `outputs.spec_bundle` with the materialized bundle when `status=completed`. On refusal, include `outputs.notion.id` (so callers can correlate) and omit or null-out `spec_bundle` fields that did not materialize.

```yaml
skill: sync-spec
status: completed | refused
# refusal reasons: notion_not_found | notion_unavailable | invalid_id | spec_bundle_unavailable
outputs:
  notion:
    id: '<32-char hex>'
    title: '<page title>'
  spec_bundle:
    spec_path: '<abs path>'
    index_path: '<abs path>/INDEX.md'
    files:
      - kind: spec | child | linked
        notion_id: '...'
        title: '...'
        path: '<rel path from spec-path>'
        summary: '<one-liner>'
issues: []
```

Update TodoWrite: mark `completion-report` as `completed`. End of skill.
