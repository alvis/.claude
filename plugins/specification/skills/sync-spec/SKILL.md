---
name: sync-spec
description: Materialize a guaranteed-on-disk Notion specification tree as a flat `.code-spec/` bundle of `{kebab-title}-{32hex-id}.md` files plus `.gitignore`. Use before downstream analysis or code generation, when refreshing a stale bundle, or when a ticket requires local spec evidence; fail unless the root id-suffix file exists and is non-empty.
model: opus
context: fork
agent: general-purpose
allowed-tools: Read, Grep, Glob, Bash, TodoWrite
argument-hint: "<notion-url-or-id> [--spec-path=<dir>]"
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

- `notion-sync` CLI on PATH (verify with `Bash: notion-sync --help`)
- `NOTION_TOKEN` environment variable set in the current shell (export before invoking)
- Write access to the resolved `<spec-path>` directory
- A working directory inside (or under) a project (so `<spec-path>` defaults can resolve to a project root); otherwise falls back to `<CWD>/.code-spec`

### Your Role

You are a **Spec Bundle CLI Operator** who runs a single recursive `notion-sync pull` and validates the on-disk result. Your responsibilities are:

- **Path Discipline**: Resolve `<spec-path>` deterministically (project-root walk-up, then CWD fallback) and refuse to operate outside the project tree
- **Wipe Discipline**: Always wipe `<spec-path>` before the fetch — no caching, no merging, no preservation
- **One-Shot Recursion**: Issue exactly ONE `notion-sync pull <id> --follow --out <spec-path>` call. The CLI walks children + databases + links + files in a single invocation. Do NOT iterate per-page across tool turns.
- **Hard-Gate Authority**: After the pull, verify the file whose `{32hex-id}` filename suffix matches the input `notion_id` exists and is non-empty. Refuse the entire skill if not.
- **Faithful Reporting**: Emit a single YAML completion report describing every file persisted, with refusal reasons surfaced explicitly when applicable

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **`<notion-url-or-id>`**: Full Notion URL or bare 32-char hex id of the root spec page. Dashes are stripped during normalization.

#### Optional Inputs

- **`--spec-path=<dir>`**: Directory to write the bundle into. **Default**: walk up from CWD to the closest project root (first ancestor containing any of `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) and use `<root>/.code-spec`. If no project root marker is found anywhere up to the filesystem root, fall back to `<CWD>/.code-spec`.

There are NO other arguments. There is **no** `--use-cache`, **no** `--repo`, **no** `--slug`, and **no** sync mode. The skill always wipes and re-downloads.

#### Expected Outputs

- **Bundle on disk** at `<spec-path>/` (flat, no subdirectories):
  - `{kebab-title}-{32hex-id}.md` for every page in the pulled subgraph (root + recursive children + linked leaves + database rows)
  - `.gitignore` — auto-written by `notion-sync`, single line `*`
- **Page identity** is the 32-hex suffix of the filename. The root page is the file whose suffix equals the input `notion_id`.
- **Completion Report (YAML)**: `status` (`completed` | `refused`), refusal `reason` if applicable, `outputs.notion`, `outputs.spec_bundle.spec_path`, `outputs.spec_bundle.files[]` (each entry `{ path, notion_id }`)

#### Data Flow Summary

The skill takes a Notion URL or id, normalizes it to a 32-char hex id, resolves an absolute `<spec-path>` (project-root walk-up with CWD fallback), safety-checks that the path is inside the resolved project root or under CWD, wipes the directory, runs ONE `notion-sync pull <id> --follow --out <spec-path>` call (which recursively writes flat `{kebab-title}-{32hex-id}.md` files for the entire subgraph plus a `.gitignore`), hard-gate verifies that the root file (filename suffix matches input `notion_id`) exists and is non-empty, and emits a YAML completion report. There is no caching, no merge, no second pass, and no per-page iteration across tool turns.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU
(CLI Operator — single linear flow)
   |
   v
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
[Step 3: One-Shot Recursive Pull]
   |    • Bash: notion-sync pull <notion_id> --follow --out <spec-path>
   |    • SINGLE call walks children + databases + links + files
   |    • CLI auto-writes .gitignore at <spec-path>/.gitignore
   |    • files land flat: {kebab-title}-{32hex-id}.md
   |    • DO NOT iterate per-page across turns
   v
[Step 4: Enumerate]
   |    • Glob: <spec-path>/*.md → file list
   |    • parse 32-hex suffix from each filename → notion_id
   v
[Step 5: Hard-Gate Verification]  *** HARD GATE ***
   |    • locate file whose {32hex-id} suffix matches input notion_id
   |    • Bash test -s <root-file>
   |    • CLI exit ≠ 0 OR root file missing/empty → refuse
   |    • CLI exit 0 + root file present non-empty → completed
   v
[Step 6: Skill Completion Report]
   |    • emit YAML
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• Single operator — no subagent dispatch, no parallel fan-out
• ONE notion-sync pull does everything (recursion via --follow)
• Step 5 is the HARD GATE — no completed status without root file on disk
• Skill is LINEAR: 1 → 2 → 3 → 4 → 5 → 6
• On invalid_id (Step 1) or refusal at Step 5: jump straight to Step 6
═══════════════════════════════════════════════════════════════════

Note:
• Recursion happens INSIDE the CLI, not across tool turns
• No caching: every invocation is a fresh download
• No merging: pre-existing contents at <spec-path> are deleted
• No INDEX.md, no children/, no linked/ — bundle is flat
```

### Skill Steps

1. Resolve & Normalize (You) — strip dashes, validate 32-char hex, resolve `<spec-path>`
2. Wipe & Prepare (You) — safety check + `rm -rf` + `mkdir -p`
3. One-Shot Recursive Pull (You) — `notion-sync pull <id> --follow --out <spec-path>`
4. Enumerate (You) — `Glob: <spec-path>/*.md`, parse 32-hex suffix per filename
5. Hard-Gate Verification (You) — `test -s` on the file whose suffix matches input id
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
   - **On validation failure**: set `status=refused`, `reason=invalid_id`, jump to Step 6. Do NOT wipe. Do NOT call `notion-sync`.
2. **Resolve `<spec-path>`**:
   - If `--spec-path=<dir>` provided: take it as-is, resolve to absolute path
   - Otherwise: walk up from CWD looking for the first ancestor containing any of `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`
     - If found: `spec_path = <root>/.code-spec`
     - If no marker found anywhere up to filesystem root: `spec_path = <CWD>/.code-spec` (fallback)
   - Record `project_root` (the resolved root, or null if fallback fired)
3. **Use TodoWrite** to seed todos for Steps 2–6 (`wipe-prepare`, `notion-pull`, `enumerate`, `hard-gate-verify`, `completion-report`).
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

### Step 3: One-Shot Recursive Pull

**Step Configuration**:

- **Purpose**: Run a SINGLE `notion-sync pull` invocation that mirrors the entire Notion subgraph (root + children + linked leaves + database rows + files) into `<spec-path>` as flat `{kebab-title}-{32hex-id}.md` files. The CLI also auto-writes `<spec-path>/.gitignore`.
- **Input**: `notion_id`, `spec_path`
- **Output**: Files on disk; CLI exit code; stdout/stderr captured
- **Sub-skill**: None (direct CLI call)
- **Parallel Execution**: No (one CLI process; the CLI internally parallelizes via `-c` concurrency)

#### Actions (You)

1. Confirm `<spec-path>` exists and is empty (sanity check after Step 2).
2. Update TodoWrite: mark `notion-pull` as `in_progress`.
3. Confirm `NOTION_TOKEN` is exported in the current shell. If unset, set `status=refused`, `reason=notion_unavailable`, attach a one-line explanation in `issues` (`"NOTION_TOKEN environment variable is not set"`), jump to Step 6.
4. Issue exactly ONE Bash invocation:

   ```bash
   notion-sync pull <notion_id> --follow --out <spec-path>
   ```

   - `--follow` is the umbrella flag that walks `--follow-children --follow-database --follow-links --follow-files` in a single pass.
   - Default depths are `children=3`, `database=1`, `link=1`. Override with `--depth N` or per-axis flags only when the caller explicitly requested deeper recursion.
   - You MAY add `--bail` to fail fast on the first per-page error and `-c 25` (default concurrency) if not already.
5. **DO NOT** loop — one pull call walks the entire subgraph. Per-page iteration across tool turns is forbidden.
6. Capture the CLI exit code as `cli_exit_code`. Capture stderr only on non-zero exit (for the `issues` field).
7. Update TodoWrite: mark `notion-pull` as `completed`.

### Step 4: Enumerate

**Step Configuration**:

- **Purpose**: Discover every markdown file the CLI wrote and parse each filename's `{32hex-id}` suffix into a `notion_id`. Builds the `files[]` payload for the completion report.
- **Input**: `spec_path`
- **Output**: `spec_bundle.files[]` = `[{ path, notion_id }, ...]`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Actions (You)

1. `Glob: <spec-path>/*.md` to list every markdown file (flat — no recursion needed; the CLI does not create subdirectories).
2. For each file path, parse the trailing `-{32hex}.md` segment to extract the `notion_id`. Reject any filename that does not match `/-[0-9a-f]{32}\.md$/i`; record an advisory in `issues` for skipped entries.
3. Build `spec_bundle.files = [{ path: '<abs or rel path>', notion_id: '<32hex>' }, ...]`.
4. Cache `spec_bundle` (with `spec_path` + `files[]`) for the completion report.

### Step 5: Hard-Gate Verification

**Step Configuration**:

- **Purpose**: Defence-in-depth verification that the on-disk bundle has a non-empty root file. The root file is the one whose filename suffix matches the input `notion_id`. CLI exit code is advisory; the filesystem is authoritative.
- **Input**: `spec_path`, `notion_id`, `cli_exit_code`, `spec_bundle.files[]`
- **Output**: `final_status` (`completed` | `refused`), `final_reason` (when refused), `root_file_path` (when present)
- **Sub-skill**: None
- **Parallel Execution**: No

#### Actions (You)

1. Find the root file by scanning `spec_bundle.files[]` for the entry whose `notion_id` equals the input `notion_id`. Record `root_file_path` if found.
2. Run `Bash: test -s <root_file_path>` to confirm the file exists and is non-empty.
3. Apply the decision matrix:

   | `cli_exit_code` | Root file present non-empty? | Outcome                                                                                |
   |-----------------|------------------------------|----------------------------------------------------------------------------------------|
   | non-zero        | (any)                        | `status=refused`, `reason=spec_bundle_unavailable` — jump to Step 6                     |
   | `0`             | No                           | `status=refused`, `reason=spec_bundle_unavailable` — jump to Step 6                     |
   | `0`             | Yes                          | `status=completed` (any per-page warnings surface in `issues`)                          |

4. Cache `final_status` and `final_reason` for the completion report.
5. Update TodoWrite: mark `hard-gate-verify` as `completed`.

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
    files:
      - path: '<abs or rel path>/<kebab-title>-<32hex-id>.md'
        notion_id: '<32hex>'
issues: []
```

Update TodoWrite: mark `completion-report` as `completed`. End of skill.
