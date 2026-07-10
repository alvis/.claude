---
name: review-implementation
description: 'Review implemented code for completeness and faithful alignment against an authoritative code specification (local `.code-spec` or Notion). Extends coding:review-code by adding an `alignment` area that maps every spec requirement to the implementation and flags drift, omissions, and unsanctioned additions. Runs the alignment area first and fails fast — when the implementation does not match the spec, the other review areas are skipped to avoid grading code that is about to churn. Triggers when: "review against spec", "check implementation matches spec", "audit alignment with .code-spec", "verify implementation against Notion spec", "spec-driven code review". Also use when: closing out a specification:implement-code ticket, validating delivered features against PLAN.md / SPEC.md, or auditing whether code drifted from approved design. Examples: "review implementation against ./.code-spec", "review-implementation src/auth --spec-path=https://notion.so/...", "check that this PR matches the spec".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion, TodoWrite, Workflow
argument-hint: "[specifier] [--area=test|documentation|code-quality|security|style|alignment|all] [--out=reviews] [--spec-path=./.code-spec]"
---

# Review Implementation

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Review implemented code for completeness and faithful alignment against an authoritative code specification. Extends the base `coding:review-code` skill by adding an `alignment` review area that maps every spec requirement to its implementation, flagging drift, omissions, and unsanctioned additions. The alignment area runs **first** and is a fail-fast gate: if the implementation does not align with the spec (any P0/P1 deviation), the remaining review areas are skipped rather than spend effort grading code that gap-closing work will churn.
**When to use**:

- When closing out a `specification:implement-code` ticket and verifying delivered features match the approved spec
- When validating a pull request against `PLAN.md`, `SPEC.md`, or a Notion specification
- When auditing whether the code has drifted from an approved design or contract
**Prerequisites**:
- An on-disk specification bundle (default `./.code-spec`) OR a Notion URL/ID resolvable by `specification:sync-spec`
- The specification bundle must contain at minimum one root spec markdown file. Bundles produced by `specification:sync-spec` are flat `{kebab-title}-{32hex-id}.md` files; enumerate them via `Glob: <spec-path>/*.md` and identify the root by the 32-hex suffix in its filename (matching the requested page id when known).
- A target file set, directory, PR, or git range to review (resolved via the same specifier semantics as `coding:review-code`)

### Your Role

You are an **Implementation Alignment Director** who orchestrates spec-driven code review like a senior engineering manager holding implementation accountable to the approved contract, never writing review content directly but delegating and coordinating. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. That same standard is what the alignment area enforces against the implementation: code paths the spec did not sanction, parallel "v2" helpers shadowing the canonical one, and addendum modules that duplicate existing responsibilities are themselves alignment violations to be flagged. Your management style emphasizes:

- **Spec is the Contract**: The on-disk specification is the single source of truth. Every line of implementation is judged against it.
- **Strategic Delegation**: Run the alignment area first; delegate the base review areas to `coding:review-code` (with its Plan-Adherence step skipped, so spec-conformance lives only in the alignment area) **only once alignment holds** — if alignment fails, fail fast and skip them rather than grade code that does not match the spec. Delegate deviation detection via one adversarial Find→Verify mechanism whose execution substrate adapts — a dynamic `Workflow` that fans out parallel finders and adversarial verifiers when the tool is available and scope warrants it, otherwise a single subagent running the same Find→Verify logic in-process. Do not re-implement work the base skill already does.
- **Evidence over Assertion**: Every alignment finding must cite a spec location and a code location. No vague "doesn't feel right" findings.
- **Interaction Stays With You**: Workflows cannot take mid-run input, so reconciling each deviation with the user and choosing the next action are your responsibility, in the main skill — never pushed into a subagent or workflow.
- **No Spec, No Review**: If the specification cannot be obtained on disk (sync failure, missing path, missing `SPEC.md`), refuse the alignment area cleanly with a structured report. Do not guess.

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **[specifier]**: Same semantics as `coding:review-code` — file path, directory, glob, package name, PR number, git range, or command output. Identifies the implementation under review.

#### Optional Inputs

- **--area**: One or more of `test`, `documentation`, `code-quality`, `security`, `style`, `alignment`, `all` (default `all`, which covers every area)
- **--out**: Output directory for review files (default `reviews/`, resolved against project root)
- **--spec-path**: Local path to an on-disk spec bundle OR a Notion URL/ID. Default `./.code-spec`, resolved against the closest project root via walk-up looking for `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, or `go.mod`.

#### Expected Outputs

- **All `coding:review-code` outputs** (per-area files: `SECURITY.md`, `QUALITY.md`, `TESTING.md`, `DOCS.md`, `STYLE.md`, `CORRECTNESS.md` as applicable). `CORRECTNESS.md` is re-scoped here to spec-**independent** semantic bugs only (races, off-by-ones, swallowed errors that are bugs regardless of what the spec says) because the base skill's Plan-Adherence step is skipped — all spec-conformance findings move to `ALIGNMENT.md`. These base-area files are produced only when alignment holds; on an alignment fail-fast (any P0/P1 while non-alignment areas were also requested) the base review is skipped and these files are absent.
- **`<out>/ALIGNMENT.md`** — the alignment area file *and* the deviation report, and the SOLE owner of all spec-conformance findings (drift, omissions, unsanctioned additions, violated spec-mandated behavior); prefix `ALIGN`, IDs `ALIGN-P<n>-<seq>`; conforms to the canonical `references/review.template.md` from the base skill. It carries an explicit `## Detected Deviations` list (the `## Issues` list grouped P0 → P3 serves as that list), each deviation enriched at finalize time with the user's chosen resolution and the concrete close-the-gap action, and ends with a `## Next-Action Plan`.
- **`<out>/README.md`** — refreshed index that lists every produced area file (including alignment) with verdicts and aggregate counts
- **Next action** — at runtime the skill asks whether to execute the gap-closing plan now (delegating to `specification:spec-code` / `coding:fix` / `specification:implement-code`) or to hand off via `coding:handover`.
- **Refusal report** — if the spec cannot be resolved to an on-disk bundle, the skill emits a structured YAML report with `status: refused`, `reason: spec_not_found`, and details. No alignment file is written in that case.

#### Data Flow Summary

The skill resolves the `--spec-path` to a local bundle (invoking `specification:sync-spec` for Notion sources), then runs the alignment area **first**: it detects deviations via one adversarial Find→Verify mechanism whose substrate adapts — a fan-out `Workflow` (parallel finders + adversarial verifiers) when available and scope warrants it, else a single subagent running the same Find→Verify logic — and writes `<out>/ALIGNMENT.md`. This is the **fail-fast gate**: if alignment fails (any P0/P1) while other areas were also requested, the base review is skipped entirely — grading the quality, style, or security of code that does not match the spec, only to have gap-closing work churn it, is wasted effort, so the skill surfaces the alignment report early. Otherwise it delegates the non-alignment areas to `coding:review-code` with its Plan-Adherence step skipped — so `CORRECTNESS.md` keeps only spec-independent semantic bugs and `ALIGNMENT.md` remains the sole owner of every spec-conformance finding. The skill then reconciles each detected deviation with the user, finalizes the report and `<out>/README.md` index, and asks at runtime whether to execute the close-the-gap plan or hand off. If the spec cannot be obtained on disk, the entire skill refuses cleanly without partial output.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                              SUBAGENTS / SUB-SKILLS / WORKFLOW
(Orchestrates + asks user)      (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Resolve Spec Source]   (HARD GATE — applies when alignment is requested)
   |   ├─ Local path → verify exists + has SPEC.md
   |   └─ Notion URL/ID ─────────→ (Sub-skill: specification:sync-spec)
   |                                  └─ Materialize bundle to <project-root>/.code-spec
   |   (on failure: refuse, abort entire skill)
   v
[Step 2: Detect Deviations]  ALIGNMENT FIRST  (one mechanism: adversarial Find → Verify)
   |   ├─ Planning (You): enumerate spec, resolve impl set, pick substrate
   |   ├─ Find ∥ → Verify ───────→ (Workflow fan-out, or single subagent):
   |   |     candidates cite spec-loc+code-loc; verifiers adversarially refute
   |   ├─ Write <out>/ALIGNMENT.md (## Detected Deviations = Issues P0→P3)
   |   ├─ Validate ──────────────→ (Subagent: read-only structural validation)
   |   └─ FAIL-FAST GATE: alignment verdict FAIL (any P0/P1) AND other areas requested?
   |         ├─ yes → SKIP Step 3 (assessing non-aligned code is wasted effort)
   |         └─ no  → run Step 3
   v
[Step 3: Delegate Base Review] ─────→ (Sub-skill: coding:review-code)
   |   areas = requested areas minus 'alignment'                      └─ Writes per-area files + README.md
   |   (skipped when alignment failed fast, or when --area=alignment only)
   v
[Step 4: Reconcile Deviations with User]
   |   └─ For EACH deviation: AskUserQuestion (batched, exhaustive) →
   |        Update spec | Update code | Accept as-is | Defer  (+ rationale)
   v
[Step 5: Finalize Report & Index]
   |   ├─ Rewrite ALIGNMENT.md: each deviation + resolution + gap rationale
   |   |    + close-the-gap action; append ## Next-Action Plan (A: handoff, B: execute)
   |   ├─ Regenerate <out>/README.md (alignment row → ALIGNMENT.md; note skipped base areas)
   |   └─ Aggregate counts; overall status via base-skill logic
   v
[Step 6: Choose Next Action]
   |   └─ AskUserQuestion: Execute now? ──┬─ Execute → delegate per decision:
   |                                      |     spec → specification:spec-code (+ sync)
   |                                      |     code → coding:fix | implement-code
   |                                      |     (+ optional re-detection round)
   |                                      └─ Hand off → coding:handover, then stop
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan, orchestrate, and ask the user (no execution)
• RIGHT SIDE: Subagents / sub-skills / the Workflow execute
• ARROWS (───→): You delegate work
• DECISIONS: You decide based on reports and on user answers
═══════════════════════════════════════════════════════════════════

Note:
• Step 1 is a HARD GATE: if spec cannot be obtained, the alignment area
  is refused and (when --area=alignment only) the whole skill refuses.
• Step 2 runs FIRST and produces ONLY the alignment file. ALIGNMENT.md is
  the SOLE owner of all spec-conformance findings (drift, omissions,
  unsanctioned additions, violated spec-mandated behavior). Tie-break:
  defect traceable to a spec requirement → ALIGNMENT.md; wrong
  regardless of the spec → CORRECTNESS.md; never both. The Workflow path
  and the single-subagent path are two execution substrates for ONE
  mechanism (adversarial Find → Verify) — not two mechanisms.
• FAIL-FAST: if alignment FAILS (any P0/P1) and non-alignment areas were
  also requested, Step 3 is skipped — there is no point grading the
  quality/style/security of code that does not yet match the spec, since
  closing the alignment gaps will churn it. Re-run the skill (or use
  Step 6's re-detection / base-review offer) once alignment holds to
  cover the base areas.
• Step 3 reuses coding:review-code with its Plan-Adherence step SKIPPED,
  so CORRECTNESS.md holds only spec-INDEPENDENT semantic bugs (races,
  off-by-ones, swallowed errors wrong regardless of the spec).
• Skill is NOT strictly linear: Steps 4 and 6 are interactive
  (AskUserQuestion), and Step 6 branches at runtime into execute or hand off.
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Resolve Spec Source
2. Detect Deviations (alignment area — runs first as a fail-fast gate)
3. Delegate Base Review (areas other than alignment — skipped on alignment fail-fast)
4. Reconcile Deviations with the User
5. Finalize Report & Index
6. Choose Next Action

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

#### Phase 3: Decision (You)

- **PROCEED** to Step 2 when `<spec-path>` is verified.
- **REFUSE** (terminal) when verification fails per above.

### Step 2: Detect Deviations

**Step Configuration**:

- **Purpose**: Produce `<out>/ALIGNMENT.md` — the alignment area file *and* the deviation report — by detecting every deviation between spec and implementation (omissions, drift, unsanctioned additions) through one adversarial Find→Verify mechanism whose execution substrate adapts to `Workflow` availability, then validating the written file.
- **Input**: `<spec-path>` from Step 1, `[specifier]`, `--out`.
- **Output**: `<out>/ALIGNMENT.md` conforming to `references/review.template.md`, whose `## Issues` list (grouped P0 → P3) is the `## Detected Deviations` list; a structural validation report.
- **Sub-skill**: None (handled by a dynamic `Workflow` or a dedicated subagent — the mechanism, contract, and dispatch prompts are inlined in Phase 2/3 below)
- **Parallel Execution**: Substrate-dependent — fans out massively under `Workflow`, single holistic subagent otherwise
- **Run/skip**: Runs FIRST, before any base review area, whenever `alignment` is among the requested `--area` values (it is under the default `--area=all`). If alignment was NOT requested, skip this entire step and Step 1's spec gate, and proceed straight to Step 3 for the base review.

#### Phase 1: Planning (You)

**What You Do**:

1. **Enumerate spec resources** by `Glob: <spec-path>/*.md` (do NOT read full file contents — paths only). Bundles are flat `{kebab-title}-{32hex-id}.md` files; identify any root spec by the 32-hex suffix of its filename when a target page id is known.
2. **Resolve the implementation file set** using the same specifier-resolution logic as `coding:review-code` (file path, directory, glob, package name, PR number, git range, or command output). Produce a list of absolute paths.
3. **Determine the existing target file**: check whether `<out>/ALIGNMENT.md` already exists. If yes, the re-run logic in the Phase 2 shared contract applies (preserve issue IDs, Pending Decisions, any prior `## Next-Action Plan`, and any per-issue reconciliation annotations already woven in — chosen resolution + rationale + close-the-gap action).
4. **Determine standards** (paths only, recursive — the mechanism reads them): `plugins/coding/constitution/standards/code-review.md` and `plugins/coding/constitution/standards/universal/scan.md`.
5. **Decide the execution substrate (capability gate "fan out agents if suitable")**: use the **Workflow fan-out** substrate if the `Workflow` tool is available AND scope is non-trivial (multiple spec files OR a broad implementation surface); otherwise use the **single-subagent** substrate. The mechanism (adversarial Find→Verify) is the same either way.
6. **Use TodoWrite** to add an `alignment-detection` task with status `pending`.

**OUTPUT from Planning**: the chosen substrate plus the assignment payload (spec path, implementation file set, output target, template, standards, re-run instruction) — paths only, no inlined content.

#### Phase 2: Detection (Workflow or Subagent)

Run **one** detection mechanism — an adversarial *Find → Verify* spec-to-code audit. Only its **execution substrate** varies: a `Workflow` fans the audit out across many agents when the tool is available and scope warrants it; otherwise a single subagent runs the identical Find→Verify logic in-process. Update the `alignment-detection` task from `pending` to `in_progress` when dispatched.

##### Shared contract (both substrates honor this)

- **Output target**: `<out>/ALIGNMENT.md`, written per `/Users/alvis/Repositories/.claude/plugins/coding/skills/review-code/references/review.template.md`.
- **Prefix** `ALIGN`, **issue IDs** `ALIGN-P<n>-<seq>`, area `alignment`.
- **Bidirectional traceability**: spec → code (omissions, drift) AND code → spec (unsanctioned additions). Both directions are mandatory.
- **Correctness vs. alignment tie-break**: if a defect is traceable to a spec requirement, it is an alignment deviation and belongs in `ALIGNMENT.md`. If it is wrong regardless of what the spec says, it is correctness and belongs in `CORRECTNESS.md`. This prevents the same defect being double-reported across the two files.
- **Evidence over assertion**: every finding cites a concrete spec location and a concrete code location with `file:line` references.
- **Severity by impact**: a broken acceptance criterion or weakened invariant is P0; contract drift (wrong shape, signature, behavior) is P0/P1 by blast radius; unsanctioned additions are P1 minimum unless trivial (logging, internal helpers consistent with siblings); documentation-only divergence is P2/P3.
- **`## Detected Deviations`**: the canonical `## Issues` list grouped P0 → P3 *is* the detected-deviations list. Do not emit a second parallel list — the report carries one. (Step 5 later enriches each entry with its reconciliation decision and appends `## Next-Action Plan`; the validator is taught to accept those alignment-specific sections.)
- **Re-run logic**: if `<out>/ALIGNMENT.md` already exists, read it first and apply the base-skill re-run logic — match new findings to prior unchecked entries by `Source` location + `Issue` text; reuse original IDs; preserve any `## Pending Decisions` context, any prior `## Next-Action Plan`, and any per-issue reconciliation annotations already woven in (the chosen resolution + rationale + close-the-gap action that Step 5 wove into each deviation); for prior unchecked items with no current match, confirm they no longer apply before dropping; new findings get the next available sequence per priority. Rewrite the file in full.

The report skeleton (both substrates produce this exact shape):

- Frontmatter (`area: alignment`, `prefix: ALIGN`, `reviewed_at`, `files_reviewed_count`)
- Title `# Alignment Review`
- Verdict line (`✅ PASS` or `❌ FAIL — N issues (P0:a, P1:b, P2:c, P3:d)`)
- `## General Status` with a Files Reviewed bullet list and a 2–4 sentence prose summary
- `## Issues` grouped strictly P0 → P3 (this section is the `## Detected Deviations` list)
- `## Pending Decisions` for any issue with `**Solution**: TBD`

##### Find → Verify core (substrate-independent logic)

1. **Find — build the requirement inventory** from the spec bundle (`Glob: <spec-path>/*.md`, flat `{kebab-title}-{32hex-id}.md` layout; identify the root by the 32-hex suffix when a target page id is known, else read alphabetically). For each requirement extract the functional contract, schema, invariant, acceptance criterion, or non-functional posture, with a stable per-requirement identifier.
2. **Find — map spec → code**: locate the implementing code via Grep/Read; mark each requirement `covered` / `partial` / `missing`, citing the implementing `file:line` range. **The omission search spans the ENTIRE repository, not just the specifier's file set**: before flagging a requirement as missing/omitted, search the whole repo for an implementing site — the specifier only bounds which code gets drift/quality scrutiny, it does NOT bound the omission search. A requirement implemented anywhere in the repo is `covered`, even outside the reviewed file set.
3. **Find — map code → spec**: flag any non-trivial behavior (functions, branches, side effects, error paths) NOT traceable to a spec requirement. Each unsanctioned addition is a finding (P1 minimum unless trivial — logging, internal helpers consistent with siblings).
4. **Find — identify drift and omissions**: drift where the implementation deviates from the spec (wrong shape/contract, weakened invariant, different error semantics/ordering/side-effect set) — P0 if it breaks a documented acceptance criterion or shared interface, P1 for observable public-surface change, P2 for internal-helper/naming, P3 for cosmetic; omissions where a spec requirement has no implementation — P0 if gated by an acceptance criterion or "MUST", P1 otherwise, P2 only if the spec marks it optional/future. Emit each as a **candidate** deviation citing **spec-loc + code-loc**, a proposed priority, and a one-line rationale. Candidates are not yet recorded findings.
5. **Verify — adversarially refute each candidate**: re-read the cited spec-loc and code-loc plus surrounding context and try to prove the deviation spurious — the requirement *is* covered elsewhere, the "unsanctioned" addition *is* sanctioned by another spec section or an explicit future/optional marker or a sibling implementation, the drift is within tolerance. A candidate is recorded only if it **cannot** be refuted. Survivors are deduplicated and assigned `ALIGN-P<n>-<seq>` IDs.

##### Running the Find → Verify work

The core above *is* the job — what scales is only how many hands you put on it, so brief it like you'd brief a team and let the surface decide the headcount. On a broad surface (many spec files, a wide implementation) you fan the audit out — the ultracode move: spin up a dynamic two-phase `Workflow` and hand it the spec bundle path, the resolved implementation file set, and the assigned standards (`plugins/coding/constitution/standards/code-review.md`, `plugins/coding/constitution/standards/universal/scan.md`). Its **Find** phase slices the requirement inventory across N finders (a slice each), each running core steps 1–4 to emit candidates; its **Verify** phase hands every candidate to a verifier running core step 5 (refute, hunting the sanctioning evidence a finder may have missed) and returning `refuted` (drop) or `survived` (record). On a contained surface — or whenever no `Workflow` is around — a single Specification Alignment Auditor subagent (model `opus`, agent type `general-purpose`) runs that very same core end-to-end in-process, refute pass and all. It's one mechanism, one output; only the headcount moves with the surface, so size it to the work rather than treating the two as different procedures.

Whoever runs it ultrathinks hard about coverage and traceability and CANNOT further delegate, and opens with the neutral preamble verbatim: `"You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct."` Survivors are deduped and assigned `ALIGN-P<n>-<seq>` IDs. The only wrinkle is who puts pen to paper: a single auditor writes `<out>/ALIGNMENT.md` itself, while a workflow instead **returns** the structured verified deviations (each with spec-loc, code-loc, priority, ID, rationale) and writes **no** file — so **you** write the report from what it returns, because a workflow cannot take the mid-run user input Step 4 needs and the report later needs reconciliation decisions woven in.

  Dispatch prompt (the single-auditor brief; for a workflow, give its finders the Find steps 1–4 and its verifiers the Verify step 5 of the same brief):

      >>>
      **ultrathink: adopt the Specification Alignment Auditor mindset**

      "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct."

      - You're a **Specification Alignment Auditor** with deep expertise in spec-to-code traceability who follows these technical principles:
        - **Spec is the Contract**: Every requirement in the spec must be either implemented, or its absence must be a finding.
        - **Bidirectional Traceability**: Spec → code (omissions, drift) AND code → spec (unsanctioned additions). Both directions are mandatory.
        - **Correctness vs. Alignment Tie-Break**: If a defect is traceable to a spec requirement, it is an alignment deviation (record it here, in ALIGNMENT.md). If it is wrong regardless of what the spec says, it is correctness (it belongs in CORRECTNESS.md, NOT here). Never record the same defect in both places.
        - **Evidence over Assertion**: Every finding cites a concrete spec location and a concrete code location with file:line references.
        - **Severity by Impact**: Missing acceptance criteria or weakened invariants are P0. Contract drift (wrong shape, wrong signature, wrong behavior) is P0/P1 by blast radius. Unsanctioned additions are P1 minimum unless trivial. Documentation-only divergence is P2/P3.

      <IMPORTANT>
        You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
      </IMPORTANT>

      **Read the following assigned standards** and follow them recursively (if A references B, read B too):

      - plugins/coding/constitution/standards/code-review.md
      - plugins/coding/constitution/standards/universal/scan.md

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
      - **Re-run instruction**: if <out>/ALIGNMENT.md already exists, read it first and apply the base-skill re-run logic — match new findings to prior unchecked entries by `Source` location + `Issue` text; reuse original IDs; preserve any Pending Decisions, any prior `## Next-Action Plan`, and any per-issue reconciliation annotations already woven in (chosen resolution + rationale + close-the-gap action); for prior unchecked items with no current match, confirm they no longer apply before dropping; new findings get the next available sequence per priority. Rewrite the file in full.

      **Steps**

      1. **Build a requirement inventory**: enumerate the bundle via `Glob: <spec-path>/*.md` (flat layout — files are `{kebab-title}-{32hex-id}.md`). Read every file. When a target page id is known, identify the root file by its filename's 32-hex suffix and read it first; otherwise read in alphabetical order. Extract functional contracts, schemas, invariants, acceptance criteria, and non-functional requirements. Each requirement gets a stable identifier you carry through to findings.

      2. **Map spec → code**: for each requirement, locate the implementing code via Grep/Read. Mark each requirement as `covered`, `partial`, or `missing`. Cite the implementing file:line range. The omission search MUST cover the ENTIRE repository for an implementing site — the specifier (the implementation file set below) only bounds which code gets drift/quality scrutiny, it does NOT bound the omission search. Before flagging a requirement as missing/omitted, Grep the whole repo; a requirement implemented anywhere in the repo is `covered`, even outside the reviewed file set.

      3. **Map code → spec**: for each implementation file, identify any non-trivial behavior (functions, branches, side effects, error paths) NOT traceable to a spec requirement. Each unsanctioned addition is a finding (P1 minimum unless trivial — e.g., logging, internal helpers consistent with siblings).

      4. **Identify drift and omissions** (Find): drift where the implementation deviates from the spec (wrong shape, wrong contract, weakened invariant, different error semantics, different ordering, different side-effect set) — P0 if it breaks a documented acceptance criterion or shared interface; P1 if it changes observable behavior of a public surface; P2 if it diverges in an internal helper or naming; P3 if purely cosmetic relative to spec wording. Omissions where a spec requirement has no implementation — P0 if gated by an acceptance criterion or labeled "MUST"; P1 otherwise; P2 only if the spec itself marks it optional/future. Emit each as a **candidate** citing spec-loc + code-loc, a proposed priority, and a one-line rationale; candidates are not yet recorded findings.

      5. **Adversarially self-refute every candidate before recording** (Verify): treat the findings from Find steps 3–4 as candidates only. For each, re-read the cited spec-loc and code-loc plus surrounding context and actively try to prove it spurious — the requirement *is* covered elsewhere, the "unsanctioned" addition *is* sanctioned by another spec section / an explicit future-or-optional marker / a sibling implementation, or the drift is within tolerance. Drop any candidate you can refute; record only the survivors. Dedupe survivors and assign `ALIGN-P<n>-<seq>` IDs.

      6. **Apply the base-skill re-run logic** when <out>/ALIGNMENT.md already exists (preserve IDs, preserve Pending Decisions, any prior Next-Action Plan, and any per-issue reconciliation annotations already woven in — chosen resolution + rationale + close-the-gap action; drop only after confirming no longer applicable).

      7. **Write the area file** at <out>/ALIGNMENT.md following references/review.template.md exactly:
         - Frontmatter (`area: alignment`, `prefix: ALIGN`, `reviewed_at`, `files_reviewed_count`)
         - Title `# Alignment Review`
         - Verdict line (`✅ PASS` or `❌ FAIL — N issues (P0:a, P1:b, P2:c, P3:d)`)
         - `## General Status` with files reviewed bullet list and 2–4 sentence prose summary
         - `## Issues` grouped strictly by P0 → P3 (this is the `## Detected Deviations` list)
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

Either substrate yields the same written report: an explicit `## Detected Deviations` list (the `## Issues` list grouped P0 → P3 serves as that list) plus a verdict line.

#### Phase 3: Validate (Subagent)

Dispatch one read-only validator subagent to confirm the written `<out>/ALIGNMENT.md` is structurally sound, whichever substrate produced it. The validator is taught to accept the alignment-specific sections this skill adds (`## Detected Deviations` — which is the `## Issues` list — and, on a finalized report, `## Next-Action Plan`).

- **[IMPORTANT]** Review is read-only — the subagent must NOT modify any file.
- **[IMPORTANT]** Track it as a separate `alignment-detection-validation` TodoWrite task.

Dispatch prompt:

    >>>
    **ultrathink: adopt the Alignment Review Validator mindset**

    - You're an **Alignment Review Validator** with expertise in review-template compliance who follows these principles:
      - **Template Compliance**: Verify the file matches references/review.template.md, accepting the alignment-specific sections.
      - **Verdict Integrity**: Confirm the verdict line matches the actual outstanding-issue count, accepting the three-state verdict form where each deviation is `open`, `decided`, or `resolved` — both `open` and `decided` count as outstanding, only `resolved` clears. A finalized report whose verdict counts `decided` deviations as outstanding is correct; do NOT flag it as a verdict mismatch.
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
    3. Verify the verdict line is present and well-formed. On a finalized report, accept the three-state verdict form (deviations marked `open` / `decided` / `resolved`); both `open` and `decided` count as outstanding and only `resolved` clears, so do not flag a verdict that counts `decided` deviations as outstanding.
    4. Verify issue blocks follow the canonical format (todo checkbox, ALIGN-P<n>-<seq> ID, Source, Issue, Solution fields). The `## Issues` list doubles as the `## Detected Deviations` list — do not flag the absence of a second deviations list.
    5. Verify Pending Decisions section is present iff any issue has `**Solution**: TBD`.
    6. **Accept** the alignment-specific sections when present and do not flag them as template violations: a `## Next-Action Plan` section (added at finalize time) and per-issue reconciliation annotations (chosen resolution + rationale woven into the issue body).

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
      alignment_sections: pass|fail|n_a
    fatals: ['issue1', ...]
    warnings: ['warning1', ...]
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect** the detection result (Workflow return or subagent report) and the validation report.
2. **Resolve the alignment verdict** from the written `<out>/ALIGNMENT.md`: read its verdict line and open `{ p0, p1, p2, p3 }` counts. Alignment **FAILS** when any P0 or P1 is outstanding.
3. **Apply decision logic**:
   - **Detection success + Validation pass**:
     - **Fail-fast gate** — when non-alignment areas were ALSO requested AND alignment FAILS (any P0/P1): set `base_review_skipped = true` and `base_review_skip_reason = alignment_failed_fast`, **SKIP Step 3 (base review)**, and PROCEED straight to Step 4. Assessing code that does not yet conform to the spec wastes effort on areas (quality, style, security posture) that the gap-closing work will churn anyway — so the skill surfaces the alignment report early instead.
     - **Otherwise** (alignment PASSES, only P2/P3 remain, or alignment was the only requested area): set `base_review_skipped = false` and PROCEED to Step 3 to run the base review areas (Step 3 self-skips when alignment was requested alone).
   - **Detection success + Validation fail with `recommendation: retry`** → re-run the detection mechanism's write (re-dispatch the auditor, or re-write from the Workflow's returned deviations; max 1 retry) with the validator's fatals attached as fix instructions, then re-validate.
   - **Detection failure** (the auditor errored and produced no `ALIGNMENT.md` — distinct from alignment *failing* with deviations) → mark this step as failed and set `base_review_skipped = false`; still PROCEED to Step 3 for the base review (it is independent of the detection error), then skip Step 4 reconciliation (no deviations to reconcile) and let Step 5 still regenerate the index while surfacing the missing alignment file in the console summary.
4. **Use TodoWrite** to update task statuses accordingly.

### Step 3: Delegate Base Review

**Step Configuration**:

- **Purpose**: Run all non-alignment review areas using the canonical `coding:review-code` skill, with its Plan-Adherence step skipped so spec-conformance stays owned by the `alignment` area. Do not duplicate its work here. Runs ONLY after alignment has held — see the Step 2 fail-fast gate.
- **Input**: `[specifier]`, `--out`, requested `--area` minus `alignment`, and the Step 2 `base_review_skipped` flag.
- **Output**: Per-area files written by `coding:review-code` and an interim `<out>/README.md` (which Step 5 will overwrite).
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/review-code/SKILL.md`
- **Parallel Execution**: No (`coding:review-code` manages its own internal parallelism)

#### Phase 1: Planning (You)

1. **Honor the Step 2 fail-fast gate**: if `base_review_skipped = true` (alignment FAILED with P0/P1 while other areas were requested), SKIP this step entirely and proceed to Step 4 — assessing non-aligned code is wasted effort. Record the skip reason for the completion report.
2. **Compute the area list to delegate**:
   - If `--area=alignment` (alone), SKIP this step entirely and proceed straight to Step 4.
   - If `--area=all`, delegate `test,documentation,code-quality,security,style` (everything the base skill supports).
   - Otherwise, delegate the requested areas with `alignment` removed.
3. **Use TodoWrite** to track this step.

#### Phase 2: Execution (You + sub-skill)

1. **Use Read tool to load** `/Users/alvis/Repositories/.claude/plugins/coding/skills/review-code/SKILL.md`.
2. **Parse the sub-skill** to identify its steps.
3. **Invoke the sub-skill** with:
   - `[specifier]` — passed through verbatim
   - `--area=<computed list>`
   - `--out=<out>` (passed through)
   - **Instruct `coding:review-code` to SKIP its mandatory Plan-Adherence step.** Spec-conformance is owned solely by the `alignment` area (`ALIGNMENT.md`), so the base skill must not carry spec-drift findings: its `code-quality` dispatch produces a `CORRECTNESS.md` re-scoped to spec-**independent** semantic bugs only (races, off-by-ones, swallowed errors that are bugs regardless of what the spec says). Drift, omissions, unsanctioned additions, and violated spec-mandated behavior all live in `ALIGNMENT.md` instead.
4. **Track via TodoWrite** as the sub-skill executes.
5. **Collect** the per-area file paths and verdicts the sub-skill reports back. Do not modify those files.

#### Phase 3: Decision (You)

- **PROCEED** to Step 4 once the sub-skill has written its per-area files and reported their verdicts — or immediately, when this step was skipped per the fail-fast gate or because alignment was requested alone.

### Step 4: Reconcile Deviations with the User

**Step Configuration**:

- **Purpose**: Resolve every detected deviation interactively. Workflows cannot take mid-run input, so reconciliation lives here in the main skill.
- **Input**: `<out>/ALIGNMENT.md` from Step 2 (its `## Detected Deviations` / `## Issues` list).
- **Output**: a per-deviation decision set (chosen resolution + rationale) held for Step 5.
- **Sub-skill**: None
- **Parallel Execution**: No (sequential interactive Q&A with the user)

#### Phase 1: Planning (You)

1. **Read** `<out>/ALIGNMENT.md` and extract the ordered list of detected deviations (every `ALIGN-P<n>-<seq>` issue, P0 → P3).
2. If there are zero deviations (verdict `✅ PASS`), record an empty decision set and skip to Step 5.
3. **Use TodoWrite** to add a `reconcile-deviations` task.

#### Phase 2: Execution (You — AskUserQuestion)

For **each** detected deviation, ask the user how to resolve it via `AskUserQuestion`. Batch the questions exhaustively (group multiple deviations per `AskUserQuestion` call where the tool allows, so the user is not prompted one painful round-trip at a time), but every deviation MUST be covered. For each, offer these resolutions:

- **Update spec to match code** — the implementation is correct; the spec is stale and will be amended.
- **Update code to match spec** — the spec is authoritative; the implementation will be fixed.
- **Accept as-is (sanctioned/waive)** — the deviation is acknowledged and explicitly tolerated.
- **Defer to next round** — leave open for a follow-up detection/close-the-gap round.

Capture a short **rationale** per decision (why this resolution, and what the residual gap is). Use TodoWrite to mark `reconcile-deviations` `in_progress` while asking and `completed` once every deviation has a decision.

#### Phase 3: Decision (You)

- **PROCEED** to Step 5 once every detected deviation carries a chosen resolution + rationale.
- The decision set is the input Step 5 weaves into the report.

### Step 5: Finalize Report & Index

**Step Configuration**:

- **Purpose**: Enrich `<out>/ALIGNMENT.md` with the reconciliation outcome and a forward plan, then regenerate the `<out>/README.md` index and recompute the overall verdict.
- **Input**: `<out>/ALIGNMENT.md`, the Step 4 decision set, and all area files under `<out>/`.
- **Output**: a rewritten `<out>/ALIGNMENT.md` (deviations + resolutions + `## Next-Action Plan`), a refreshed `<out>/README.md`, and the console summary.
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. **List `<out>/`** to identify all area files actually written (`SECURITY.md`, `QUALITY.md`, `TESTING.md`, `DOCS.md`, `STYLE.md`, `CORRECTNESS.md`, `ALIGNMENT.md`).
2. **Read the verdict line of each file verbatim** (pull as-is; do not recompute).
3. Hold the Step 4 decision set ready to merge into each deviation.

#### Phase 2: Execution (You)

1. **Rewrite `<out>/ALIGNMENT.md`** so each deviation is enriched, in place, with: its chosen resolution (from Step 4), a rich rationale about the **final gap** (what remains different and why that is acceptable or must change), and the concrete **close-the-gap action** (the exact edit or delegation that would resolve it). Dissolve these into each existing issue block — no parallel "Resolutions" appendix. Then append a single **`## Next-Action Plan`** section with two ready branches:
   - **Branch A — Hand off**: the spec/impl paths, this report's location, and exactly which delegations (`specification:spec-code` / `coding:fix` / `specification:implement-code`) remain to close each gap.
   - **Branch B — Execute now**: the same delegations sequenced for immediate execution, plus a follow-up detection round to confirm closure.
   Recompute the verdict line using the **three-state** model — each deviation is `open`, `decided`, or `resolved`:
   - **"Accept as-is / waive"** → **resolved** immediately (the gap is explicitly tolerated; no further action).
   - **"Update spec to match code"**, **"Update code to match spec"**, and **"Defer"** → **decided** (not resolved): a resolution is chosen but the gap is still open until Step 6 executes that decision's close-the-gap action, which flips the deviation to **resolved**.
   - A deviation with no chosen resolution stays **open**.
   Mark each deviation's state inline in its issue block. Only `resolved` deviations drop out of the verdict counts; both `open` and `decided` deviations still count as outstanding so the gate does not go green before Step 6 actually closes the gaps.
2. **Rewrite `<out>/README.md`** in full from the current area files: one row per area file including the alignment row linked as `[Alignment](./ALIGNMENT.md)`, reviewed timestamp, aggregate priority counts, the systemic-improvements section, and overall status. When aggregating alignment into the index, **map any `decided` deviation to `REQUIRES_CHANGES`** (treat it as outstanding, exactly like an `open` issue) so the overall gate does not go green prematurely — only `resolved` deviations are cleared. When the base review was skipped (alignment fail-fast), list each skipped non-alignment area explicitly as `SKIPPED (alignment fail-fast)` rather than omitting it silently or marking it PASS.
3. **Determine overall status** using the base-skill logic, with `decided` deviations counted as outstanding alongside `open` ones (only `resolved` clears): any P0 outstanding → **FAIL**; P1 outstanding, no P0 → **REQUIRES_CHANGES**; only P2/P3 outstanding → **PASS_WITH_SUGGESTIONS**; all deviations `resolved` and all areas ✅ PASS → **PASS**.
4. **Print the console summary** in the same format as `coding:review-code` (CI vs interactive), with `ALIGNMENT.md` listed alongside the other area files.

#### Phase 3: Decision (You)

- **PROCEED** to Step 6 once `<out>/ALIGNMENT.md` and `<out>/README.md` are rewritten and the summary is printed.
- **PARTIAL** when the alignment file is missing due to a Step 2 failure: still regenerate the index (it will mark alignment as missing), report partial status, and skip Step 6 (no plan to execute).

### Step 6: Choose Next Action

**Step Configuration**:

- **Purpose**: Decide, at runtime, whether to execute the close-the-gap plan now or hand it off — the second interactive step (workflows cannot ask).
- **Input**: the finalized `<out>/ALIGNMENT.md` (its `## Next-Action Plan`) and the Step 4 decision set.
- **Output**: either delegated gap-closing work (executed branch) or handover notes (handed-off branch); a `next_action` value for the completion report.
- **Sub-skills**: `specification:spec-code`, `coding:fix`, `specification:implement-code`, `specification:sync-notion` / `specification:sync-spec` (execute branch); `coding:handover` (hand-off branch)
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. If Step 5 reported PARTIAL (no alignment file) or there are no actionable deviations, skip this step and record `next_action: none`.
2. **Use TodoWrite** to add a `choose-next-action` task.

#### Phase 2: Execution (You — AskUserQuestion, then delegate)

1. **Ask** via `AskUserQuestion`: **Execute the plan now** or **Hand off**.
2. **If Execute now** → delegate per the Step 4 decision for each deviation:
   - **Spec changes** (Update spec to match code) → `specification:spec-code`, then persist with `specification:sync-notion` / `specification:sync-spec`.
   - **Code changes** (Update code to match spec) → `coding:fix` for targeted fixes, or `specification:implement-code` for ticket-scale work.
   - **Accept as-is** → no delegation (already `resolved` in the report).
   - **Defer** → carry into the optional follow-up round.
   As each `decided` deviation's close-the-gap action completes, flip that deviation from `decided` to `resolved` in `<out>/ALIGNMENT.md` and recompute the verdict/index so the gate goes green only once the gaps are actually closed. Offer an **optional re-detection round** (re-run Step 2) afterward to confirm gaps closed. If the base review was skipped by the fail-fast gate, also offer to **run it now** (re-run Step 3) once alignment is fully `resolved`, so the non-alignment areas finally get covered. Record `next_action: executed`.
3. **If Hand off** → invoke `coding:handover` to produce detailed handover notes for the next agent: the resolved per-deviation decisions, the report's `## Next-Action Plan`, the spec/impl paths, the `<out>/ALIGNMENT.md` location, and exactly which delegations (`spec-code` / `fix` / `implement-code`) remain to close each gap. Then **stop** — the skill ends after handover notes are written. Record `next_action: handed_off`.

#### Phase 3: Decision (You)

- **PROCEED** to Skill Completion once the chosen branch finishes (delegations dispatched, or handover notes written).
- Carry the resulting `next_action` value into the completion report.

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
  detection_substrate: workflow|single_subagent  # which Step 2 execution substrate ran
  base_review:
    ran: true|false
    skipped_reason: alignment_failed_fast|alignment_only|none  # why the non-alignment areas were not run (none = they ran)
  area_files:
    - { area: alignment, file: '<out>/ALIGNMENT.md', verdict: '...' }
    - { area: security, file: '<out>/SECURITY.md', verdict: '...' }
    # ... all areas actually produced
  index_file: '<out>/README.md'
  aggregate_open_issues: { p0: N, p1: N, p2: N, p3: N }
  overall_status: PASS|PASS_WITH_SUGGESTIONS|REQUIRES_CHANGES|FAIL
  reconciliation:  # per-deviation decisions captured in Step 4
    - { id: ALIGN-P0-1, resolution: update_spec|update_code|accept_as_is|defer, rationale: '...' }
    # ... one entry per detected deviation
  next_action: executed|handed_off|none
summary: |
  Reviewed <specifier> against spec at <spec-path>. Produced <N> area
  files including ALIGNMENT.md with <verdict> and a Next-Action Plan.
  Reconciled <M> deviations with the user; next_action: <executed|handed_off>.
  Index at <out>/README.md.
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
