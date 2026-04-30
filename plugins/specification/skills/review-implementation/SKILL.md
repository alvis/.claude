---
name: review-implementation
description: 'Review implemented code for completeness and faithful alignment against an authoritative code specification (local `.code-spec` or Notion). Extends coding:review-code by adding an `alignment` area that maps every spec requirement to the implementation and flags drift, omissions, and unsanctioned additions. Triggers when: "review against spec", "check implementation matches spec", "audit alignment with .code-spec", "verify implementation against Notion spec", "spec-driven code review". Also use when: closing out a specification:implement-code ticket, validating delivered features against PLAN.md / SPEC.md, or auditing whether code drifted from approved design. Examples: "review implementation against ./.code-spec", "review-implementation src/auth --spec-path=https://notion.so/...", "check that this PR matches the spec".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion, TodoWrite
argument-hint: '[specifier] [--area=test|documentation|code-quality|security|style|alignment|all] [--out=reviews] [--spec-path=./.code-spec]'
---

# Review Implementation

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Review implemented code for completeness and faithful alignment against an authoritative code specification. Extends the base `coding:review-code` skill by adding an `alignment` review area that maps every spec requirement to its implementation, flagging drift, omissions, and unsanctioned additions.
**When to use**:

- When closing out a `specification:implement-code` ticket and verifying delivered features match the approved spec
- When validating a pull request against `PLAN.md`, `SPEC.md`, or a Notion specification
- When auditing whether the code has drifted from an approved design or contract
**Prerequisites**:
- An on-disk specification bundle (default `./.code-spec`) OR a Notion URL/ID resolvable by `specification:sync-spec`
- The specification bundle must contain at minimum a `SPEC.md` file (an `INDEX.md` is helpful for enumeration)
- A target file set, directory, PR, or git range to review (resolved via the same specifier semantics as `coding:review-code`)

### Your Role

You are an **Implementation Alignment Director** who orchestrates spec-driven code review like a senior engineering manager holding implementation accountable to the approved contract. You never write review content directly, only delegate and coordinate. Your management style emphasizes:

- **Spec is the Contract**: The on-disk specification is the single source of truth. Every line of implementation is judged against it.
- **Strategic Delegation**: Delegate base review areas to `coding:review-code` and the new alignment area to a dedicated specialist subagent. Do not re-implement work the base skill already does.
- **Evidence over Assertion**: Every alignment finding must cite a spec location and a code location. No vague "doesn't feel right" findings.
- **No Spec, No Review**: If the specification cannot be obtained on disk (sync failure, missing path, missing `SPEC.md`), refuse the alignment area cleanly with a structured report. Do not guess.

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **[specifier]**: Same semantics as `coding:review-code` — file path, directory, glob, package name, PR number, git range, or command output. Identifies the implementation under review.

#### Optional Inputs

- **--area**: One or more of `test`, `documentation`, `code-quality`, `security`, `style`, `alignment`, `all` (default `all`, which now includes the new `alignment` area)
- **--out**: Output directory for review files (default `reviews/`, resolved against project root)
- **--spec-path**: Local path to an on-disk spec bundle OR a Notion URL/ID. Default `./.code-spec`, resolved against the closest project root via walk-up looking for `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, or `go.mod`.

#### Expected Outputs

- **All `coding:review-code` outputs** (per-area files: `SECURITY.md`, `QUALITY.md`, `TESTING.md`, `DOCS.md`, `STYLE.md`, `CORRECTNESS.md` as applicable)
- **`<out>/ALIGNMENT.md`** — new area file produced by the alignment review; prefix `ALIGN`, IDs `ALIGN-P<n>-<seq>`; conforms to the canonical `references/review.template.md` from the base skill
- **`<out>/README.md`** — refreshed index that lists every produced area file (including alignment) with verdicts and aggregate counts
- **Refusal report** — if the spec cannot be resolved to an on-disk bundle, the skill emits a structured YAML report with `status: refused`, `reason: spec_not_found`, and details. No alignment file is written in that case.

#### Data Flow Summary

The skill resolves the `--spec-path` to a local bundle (invoking `specification:sync-spec` for Notion sources), then delegates non-alignment areas to `coding:review-code`, then runs an alignment subagent that maps every spec requirement to implementation evidence. Results converge into `<out>/` with a regenerated `<out>/README.md` index. If the spec cannot be obtained on disk, the entire skill refuses cleanly without partial output.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                              SUBAGENTS / SUB-SKILLS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Resolve Spec Source]
   |   ├─ Local path → verify exists + has SPEC.md
   |   └─ Notion URL/ID ─────────→ (Sub-skill: specification:sync-spec)
   |                                  └─ Materialize bundle to <project-root>/.code-spec
   |   (on failure: refuse, abort entire skill)
   v
[Step 2: Delegate Base Review] ─────→ (Sub-skill: coding:review-code)
   |   areas = requested areas minus 'alignment'                      └─ Writes per-area files + README.md
   |   (skipped when --area=alignment only)
   v
[Step 3: Run Alignment Review]
   |   ├─ Phase 1 Planning (You): paths only, build assignment
   |   ├─ Phase 2 Execution ─────→ (Subagent: Specification Alignment Auditor, opus)
   |   |                              └─ Writes <out>/ALIGNMENT.md
   |   ├─ Phase 3 Review ────────→ (Subagent: read-only structural validation)
   |   └─ Phase 4 Decision (You): PROCEED / RETRY / FAIL
   v
[Step 4: Index & Report]
   |   ├─ Regenerate <out>/README.md including alignment row
   |   ├─ Aggregate counts across ALL area files
   |   └─ Compute overall status using base-skill logic
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents / sub-skills execute
• ARROWS (───→): You delegate work
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note:
• Step 1 is a HARD GATE: if spec cannot be obtained, the alignment area
  is refused and (when --area=alignment only) the whole skill refuses.
• Step 2 reuses coding:review-code verbatim — do NOT re-implement it.
• Step 3 produces ONLY the alignment file. Do not duplicate findings
  into CORRECTNESS.md or any other area file.
• Skill is LINEAR: Step 1 → 2 → 3 → 4
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Resolve Spec Source
2. Delegate Base Review (areas other than alignment)
3. Run Alignment Review
4. Index & Report

### Step 1: Resolve Spec Source

**Step Configuration**:

- **Purpose**: Ensure an on-disk specification bundle exists before any alignment work begins. This is a HARD GATE.
- **Input**: `--spec-path` (default `./.code-spec`); resolved against the closest project root via walk-up for `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`.
- **Output**: Absolute path to a directory containing at least `SPEC.md`, OR a refusal report.
- **Sub-skill**: `specification:sync-spec` (only when the input is a Notion URL/ID)
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive `--spec-path`** from skill arguments (default `./.code-spec`).
2. **Walk up from the current working directory** to find the closest project root. A project root is any directory containing one of: `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, or `go.mod`. Use this as the anchor for relative paths.
3. **Detect source type**:
   - **Notion** if `--spec-path` matches a Notion URL (`https://www.notion.so/...`, `https://notion.so/...`, `https://*.notion.site/...`) OR a 32-character hex page ID (with or without dashes, e.g., `abc123...` or `abc12345-1234-1234-1234-...`).
   - **Local** otherwise. Resolve the path relative to the project root (or use it absolute if already absolute).
4. **Use TodoWrite** to track this step as `pending` then `in_progress`.

#### Phase 2: Execution (You + optional sub-skill)

**Local path branch**:

1. Verify the resolved directory exists.
2. Verify it contains a readable `SPEC.md` (case-sensitive).
3. If both checks pass, set `<spec-path>` = absolute resolved path and proceed to Step 2.

**Notion branch**:

1. Load `specification:sync-spec` as a sub-skill (Read its `SKILL.md`, parse its steps).
2. Invoke it with parameters:
   - `notion_url` = the input URL/ID
   - `--spec-path` = `<closest-project-root>/.code-spec`
3. After it completes, verify the bundle directory exists locally and contains `SPEC.md`.
4. Set `<spec-path>` = the local materialized path.

**Refusal**:

If any verification fails (sync error, missing directory, missing `SPEC.md`), abort the entire skill and emit:

```yaml
skill: review-implementation
status: refused
reason: spec_not_found
details:
  resolved_spec_path: '<absolute path that was checked>'
  missing: '<directory|SPEC.md|sync_failure>'
  message: 'Specification bundle could not be resolved to an on-disk path. The alignment area cannot run without a concrete spec.'
```

Do not write any file under `<out>/` for the alignment area. If `--area` requested non-alignment areas only, the spec gate does NOT apply — but if the user said `--area=all` or included `alignment`, the entire skill refuses.

#### Phase 4: Decision (You)

- **PROCEED** to Step 2 when `<spec-path>` is verified.
- **REFUSE** (terminal) when verification fails per above.

### Step 2: Delegate Base Review

**Step Configuration**:

- **Purpose**: Run all non-alignment review areas using the canonical `coding:review-code` skill. Do not duplicate its work here.
- **Input**: `[specifier]`, `--out`, requested `--area` minus `alignment`.
- **Output**: Per-area files written by `coding:review-code` and an interim `<out>/README.md` (which Step 4 will overwrite).
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/review-code/SKILL.md`
- **Parallel Execution**: No (`coding:review-code` manages its own internal parallelism)

#### Execute coding:review-code Sub-Skill (You)

When you reach this step:

1. **Compute the area list to delegate**:
   - If `--area=alignment` (alone), SKIP this step entirely.
   - If `--area=all`, delegate `test,documentation,code-quality,security,style` (everything the base skill supports).
   - Otherwise, delegate the requested areas with `alignment` removed.
2. **Use Read tool to load** `/Users/alvis/Repositories/.claude/plugins/coding/skills/review-code/SKILL.md`.
3. **Parse the sub-skill** to identify its steps.
4. **Invoke the sub-skill** with:
   - `[specifier]` — passed through verbatim
   - `--area=<computed list>`
   - `--out=<out>` (passed through)
5. **Track via TodoWrite** as the sub-skill executes.
6. **Collect** the per-area file paths and verdicts the sub-skill reports back. Do not modify those files.

After completion, continue to Step 3.

### Step 3: Run Alignment Review

**Step Configuration**:

- **Purpose**: Produce the new `<out>/ALIGNMENT.md` area file by mapping every spec requirement to implementation evidence and flagging drift, omissions, and unsanctioned additions.
- **Input**: `<spec-path>` from Step 1, `[specifier]`, `--out`.
- **Output**: `<out>/ALIGNMENT.md` conforming to `references/review.template.md` (reused from the base skill); subagent completion report with file path, open-issue counts per priority, and `context_level`.
- **Sub-skill**: None (handled by a dedicated subagent)
- **Parallel Execution**: No (single audit subagent; alignment requires holistic spec coverage)

#### Phase 1: Planning (You)

**What You Do**:

1. **Enumerate spec resources** by listing files under `<spec-path>` (do NOT read full file contents — paths only). Note the presence of `INDEX.md` and `SPEC.md`.
2. **Resolve the implementation file set** using the same specifier-resolution logic as `coding:review-code` (file path, directory, glob, package name, PR number, git range, or command output). Produce a list of absolute paths.
3. **Determine the existing target file**: check whether `<out>/ALIGNMENT.md` already exists. If yes, the subagent must apply the base-skill re-run logic (preserve issue IDs, preserve Pending Decisions context).
4. **Determine standards** (paths only, recursive — subagent reads them):
   - `plugins/coding/constitution/standards/code-review.md`
   - `universal/scan` (the universal scan standard family)
5. **Use TodoWrite** to add an `alignment-review` task with status `pending`.
6. **Prepare the assignment** for the subagent (paths only, no inlined content).

**OUTPUT from Planning**: A single subagent assignment with paths to spec, implementation files, output target, template, standards, and re-run instructions.

#### Phase 2: Execution (Subagent)

**What You Send to Subagent**:

In a single message, you spin up exactly one Specification Alignment Auditor subagent (model `opus`, agent type `general-purpose`).

- **[IMPORTANT]** Use TodoWrite to update the alignment task from `pending` to `in_progress` when dispatched.
- **[IMPORTANT]** The subagent must ultrathink hard about coverage and traceability.
- **[IMPORTANT]** Begin the dispatch prompt with the neutral preamble verbatim from the base skill: `"You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct."`

Request the subagent to perform the following audit with full detail:

    >>>
    **ultrathink: adopt the Specification Alignment Auditor mindset**

    "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct."

    - You're a **Specification Alignment Auditor** with deep expertise in spec-to-code traceability who follows these technical principles:
      - **Spec is the Contract**: Every requirement in the spec must be either implemented, or its absence must be a finding.
      - **Bidirectional Traceability**: Spec → code (omissions, drift) AND code → spec (unsanctioned additions). Both directions are mandatory.
      - **Evidence over Assertion**: Every finding cites a concrete spec location and a concrete code location with file:line references.
      - **Severity by Impact**: Missing acceptance criteria or weakened invariants are P0. Contract drift (wrong shape, wrong signature, wrong behavior) is P0/P1 by blast radius. Unsanctioned additions are P1 minimum unless trivial. Documentation-only divergence is P2/P3.

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - plugins/coding/constitution/standards/code-review.md
    - universal/scan

    **Assignment**

    You're assigned to produce the alignment area file for the following review:

    - **Spec bundle path** (read every file in this directory): <spec-path>
    - **Implementation files under review** (file paths only — read as needed):
      - <impl-file-1>
      - <impl-file-2>
      - ...
    - **Output target**: <out>/ALIGNMENT.md
    - **Template** (canonical structure to follow): /Users/alvis/Repositories/.claude/plugins/coding/skills/review-code/references/review.template.md
    - **Prefix**: ALIGN
    - **Issue ID format**: ALIGN-P<n>-<seq>
    - **Re-run instruction**: if <out>/ALIGNMENT.md already exists, read it first and apply the base-skill re-run logic — match new findings to prior unchecked entries by `Source` location + `Issue` text; reuse original IDs; preserve any Pending Decisions context; for prior unchecked items with no current match, confirm they no longer apply before dropping; new findings get the next available sequence per priority. Rewrite the file in full.

    **Steps**

    1. **Build a requirement inventory**: read every file under <spec-path> (start with INDEX.md if present, then SPEC.md, then any sub-documents). Extract:
       - Functional contracts (operations, signatures, inputs/outputs)
       - Schemas (data models, types, validation rules)
       - Invariants (must-hold conditions, ordering guarantees, idempotency claims)
       - Acceptance criteria (explicit "must" / "shall" statements, examples, scenarios)
       - Non-functional requirements (performance, security, observability, error handling posture)
       Each requirement gets a stable identifier you carry through to findings.

    2. **Map spec → code**: for each requirement, locate the implementing code via Grep/Read across the implementation file set. Mark each requirement as `covered`, `partial`, or `missing`. Cite the implementing file:line range.

    3. **Map code → spec**: for each implementation file, identify any non-trivial behavior (functions, branches, side effects, error paths) NOT traceable to a spec requirement. Each unsanctioned addition is a finding (P1 minimum unless trivial — e.g., logging, internal helpers consistent with siblings).

    4. **Identify drift**: where the implementation deviates from the spec (wrong shape, wrong contract, weakened invariant, different error semantics, different ordering, different side-effect set). Severity scales with blast radius:
       - P0 if it breaks a documented acceptance criterion or shared interface
       - P1 if it changes observable behavior of a public surface
       - P2 if it diverges in an internal helper or naming
       - P3 if it is purely cosmetic relative to spec wording

    5. **Identify omissions**: spec requirements with no implementation. P0 if the requirement is gated by an acceptance criterion or labeled "MUST"; P1 otherwise; P2 only if the spec itself marks it as optional/future.

    6. **Apply the base-skill re-run logic** when <out>/ALIGNMENT.md already exists (preserve IDs, preserve Pending Decisions, drop only after confirming no longer applicable).

    7. **Write the area file** at <out>/ALIGNMENT.md following references/review.template.md exactly:
       - Frontmatter (`area: alignment`, `prefix: ALIGN`, `reviewed_at`, `files_reviewed_count`)
       - Title `# Alignment Review`
       - Verdict line (PASS or `❌ FAIL — N issues (P0:a, P1:b, P2:c, P3:d)`)
       - `## General Status` with files reviewed bullet list and 2–4 sentence prose summary
       - `## Issues` grouped strictly by P0 → P3
       - `## Pending Decisions` for any issue with `**Solution**: TBD`

    **Report**

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of alignment audit completion'
    modifications: ['<out>/ALIGNMENT.md']
    outputs:
      file_path: '<out>/ALIGNMENT.md'
      verdict: 'PASS|FAIL'
      open_issues: { p0: N, p1: N, p2: N, p3: N }
      requirements_total: N
      requirements_covered: N
      requirements_partial: N
      requirements_missing: N
      unsanctioned_additions: N
      context_level: <percentage>
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagent)

**What You Send to Reviewer**:

In a single message, you spin up one read-only validator subagent to confirm the alignment file is structurally sound.

- **[IMPORTANT]** Review is read-only — the subagent must NOT modify any file.
- **[IMPORTANT]** Use TodoWrite to add a separate `alignment-review-validation` task.

Request the subagent to perform:

    >>>
    **ultrathink: adopt the Alignment Review Validator mindset**

    - You're an **Alignment Review Validator** with expertise in review-template compliance who follows these principles:
      - **Template Compliance**: Verify the file matches references/review.template.md exactly.
      - **Verdict Integrity**: Confirm the verdict line matches the actual open-issue count.
      - **ID Stability**: Confirm any prior unchecked issues that still apply retained their original ALIGN-P<n>-<seq> IDs.

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
    </IMPORTANT>

    **Review Assignment**

    You're assigned to validate the alignment area file:

    - **File**: <out>/ALIGNMENT.md
    - **Template**: /Users/alvis/Repositories/.claude/plugins/coding/skills/review-code/references/review.template.md

    **Review Steps**

    1. Read <out>/ALIGNMENT.md.
    2. Verify the frontmatter contains `area`, `prefix: ALIGN`, `reviewed_at`, `files_reviewed_count`.
    3. Verify the verdict line is present and well-formed.
    4. Verify issue blocks follow the canonical format (todo checkbox, ALIGN-P<n>-<seq> ID, Source, Issue, Solution fields).
    5. Verify Pending Decisions section is present iff any issue has `**Solution**: TBD`.

    **Report**

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief validation summary'
    checks:
      frontmatter: pass|fail
      verdict_line: pass|fail
      issue_format: pass|fail
      pending_decisions: pass|fail
      id_stability: pass|fail|n_a
    fatals: ['issue1', ...]
    warnings: ['warning1', ...]
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect** the execution and validation reports.
2. **Apply decision logic**:
   - **Execution success + Validation pass** → PROCEED to Step 4.
   - **Execution success + Validation fail with `recommendation: retry`** → re-dispatch the audit subagent (max 1 retry) with the validator's fatals attached as fix instructions.
   - **Execution failure** → mark Step 3 as failed; Step 4 will still regenerate the index but will surface the missing alignment file in the console summary.
3. **Use TodoWrite** to update task statuses accordingly.

### Step 4: Index & Report

**Step Configuration**:

- **Purpose**: Regenerate the `<out>/README.md` index so it lists the alignment area alongside all base areas, recompute aggregate counts, and print the console summary.
- **Input**: All area files under `<out>/` (from Step 2 and Step 3), plus the overall verdicts.
- **Output**: Refreshed `<out>/README.md`, console summary identical in shape to the base skill's output but extended with alignment.
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. **List `<out>/`** to identify all area files actually written (`SECURITY.md`, `QUALITY.md`, `TESTING.md`, `DOCS.md`, `STYLE.md`, `CORRECTNESS.md`, `ALIGNMENT.md`).
2. **Read the verdict line of each file verbatim** (do not recompute — pull as-is from the file's first verdict line).
3. **Aggregate open-issue counts** across all files (now including ALIGN findings).
4. **Determine overall status** using the base-skill logic, unchanged:
   - Any P0 open → **FAIL**
   - P1 open, no P0 → **REQUIRES_CHANGES**
   - Only P2/P3 open → **PASS_WITH_SUGGESTIONS**
   - All ✅ PASS → **PASS**

#### Phase 2: Execution (You)

1. **Rewrite `<out>/README.md`** in full from the current area files. Include one row per area file (now including the alignment row), reviewed timestamp, aggregate priority counts, the systemic improvements section, and overall status. Link each area name to its file (`[Alignment](./ALIGNMENT.md)`).
2. **Print the console summary** in the same format as `coding:review-code` (CI vs interactive), with `ALIGNMENT.md` listed alongside the other area files.

#### Phase 4: Decision (You)

- **PROCEED** to Skill Completion when `<out>/README.md` is regenerated and the summary is printed.
- **PARTIAL** when the alignment file is missing due to a Step 3 failure: still regenerate the index (it will mark alignment as missing) and report partial status.

### Skill Completion

**Report the skill output as specified**:

```yaml
skill: review-implementation
status: completed|partial|refused
inputs:
  specifier: '<specifier>'
  area: '<resolved area list>'
  out: '<out>'
  spec_path: '<resolved absolute path or original Notion URL>'
outputs:
  spec_resolution:
    source_type: local|notion
    resolved_spec_path: '<absolute path>'
    sync_invoked: true|false
  area_files:
    - { area: alignment, file: '<out>/ALIGNMENT.md', verdict: '...' }
    - { area: security, file: '<out>/SECURITY.md', verdict: '...' }
    # ... all areas actually produced
  index_file: '<out>/README.md'
  aggregate_open_issues: { p0: N, p1: N, p2: N, p3: N }
  overall_status: PASS|PASS_WITH_SUGGESTIONS|REQUIRES_CHANGES|FAIL
summary: |
  Reviewed <specifier> against spec at <spec-path>. Produced <N> area
  files including ALIGNMENT.md with <verdict>. Index at <out>/README.md.
```

**On refusal** (Step 1 hard gate failed AND alignment was requested):

```yaml
skill: review-implementation
status: refused
reason: spec_not_found
details:
  resolved_spec_path: '<absolute path that was checked>'
  missing: '<directory|SPEC.md|sync_failure>'
  message: 'Specification bundle could not be resolved to an on-disk path. The alignment area cannot run without a concrete spec.'
```
