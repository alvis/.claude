---
name: verify-skill
description: Verify skill documents for structural correctness, functional quality, and trigger accuracy. Use when validating new or updated skills, running quality checks on existing skills, testing skill trigger descriptions, or grading skill output quality.
model: opus
context: fork
agent: general-purpose
---

# Verify Skill

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Verify skill documents for structural correctness, functional quality, and trigger accuracy. Supports structural-only (fast), functional (with test cases), and full verification modes.
**When to use**: After creating or updating a skill; when validating existing skills; when optimizing skill descriptions for trigger accuracy.
**Prerequisites**: Target SKILL.md must exist at a valid plugin skill path.

### Your Role

You are a **Skill Verification Director** who orchestrates verification like a QA testing manager coordinating structural inspectors, functional testers, and performance analysts, never executing validation directly but delegating and coordinating. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. That standard is exactly what your structural pass checks for in any skill that itself performs content edits — and what your `fix: true` mode is held to: corrections must dissolve into the surrounding section rather than land as a parallel "fixed" block beside the original wording. Your management style emphasizes:

- **Strategic Delegation**: Route structural, functional, and trigger checks to the right specialist subagents
- **Parallel Coordination**: Run independent checks simultaneously when dependencies allow
- **Quality Oversight**: Review verification results objectively
- **Decision Authority**: Make pass/fail decisions based on subagent reports

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **skill_path**: Path to the SKILL.md file to verify

#### Optional Inputs

- **mode**: `structural` | `functional` | `full` (default: `structural`)
  - `structural`: Frontmatter, template compliance, content quality only (fast, cheap)
  - `functional`: Structural + run test cases from evals.yaml, grade outputs
  - `full`: Functional + trigger testing + description optimization option
- **fix**: `true` | `false` (default: `false`) -- auto-fix issues or just report
- **optimize_description**: `true` | `false` (default: `false`) -- run description optimization loop (only in `full` mode)

#### Expected Outputs

```yaml
status: pass | fail | partial
structural:
  frontmatter: pass|fail
  template_compliance: pass|fail
  content_quality: pass|fail
functional:  # only if mode=functional|full
  pass_rate: 0.XX
  test_cases: N
  grading_summary: ...
trigger:     # only if mode=functional|full
  trigger_rate: 0.XX
  false_positive_rate: 0.XX
description: # only if optimize_description=true
  original: "..."
  optimized: "..."
  improvement: "+X%"
issues: [...]
suggestions: [...]
```

#### Data Flow Summary

The skill reads the target SKILL.md, runs mode-gated verification steps (structural -> functional -> trigger), and aggregates results into a consolidated pass/fail report with actionable suggestions. When `fix: true`, it spawns fix subagents to auto-correct issues.

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
[Step 1: Analysis] ──────────→ (Analyze target skill, load/generate evals)
   |
   v
[Step 2: Structural] ────────→ (Validate frontmatter, template, content)
   |                ├─ Subagent A: Frontmatter Validator    ─┐
   |                ├─ Subagent B: Template Compliance       ─┼─→ [Decision: All pass?]
   |                └─ Subagent C: Content Quality Assessor  ─┘
   v
   ─── if mode=functional|full ───
   |
[Step 3: Trigger Testing] ───→ (Test description triggers via `claude -p`)
   |
   v
[Step 4: Functional Testing] → (Run skill against test prompts, capture)
   |                ├─ Subagent: Test Case 1 ─┐
   |                ├─ Subagent: Test Case 2  ─┼─→ [Decision: Outputs captured?]
   |                └─ Subagent: Test Case 3  ─┘
   v
[Step 5: Grading] ───────────→ (Grade outputs, aggregate metrics)
   |
   v  ─── if optimize_description=true ───
[Step 6: Description Opt.] ──→ (Train/test split trigger optimization)
   |
   v
[Step 7: Report] ────────────→ (Consolidated report + fix suggestions)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute verification tasks
• ARROWS (──→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
• Steps 3-4 conditional (skip for structural mode)
• Step 6 opt-in (optimize_description=true only)
═══════════════════════════════════════════════

Note:
• You: Receives inputs, batches work, assigns tasks, makes decisions
• Execution Subagents: Perform actual verification, report back (<1k tokens)
• Skill is LINEAR: Step 1 → 2 → 3 → ... → 7
```

## 3. SKILL IMPLEMENTATION

### Content Placement Rule

The **Content Placement & Coherence Rule** this skill validates against is defined canonically in `plugins/governance/constitution/references/authoring-invariants.md`: SKILL.md holds only the always-on core workflow, conditional bulk (>~50 lines, gated) offloads to `references/<topic>.md` or splits into a separate skill, and references must not hide always-on core steps. Step 2 Structural Validation enforces it via the **Content Placement Validator** subagent (D), while the **Content Quality Assessor** subagent (C) enforces the inline Coherence Mandate.

### Skill Steps

1. Analysis -- Analyze target skill, generate or load evals
2. Structural Validation -- Frontmatter, template compliance, content quality
3. Trigger Testing -- Test description triggers via `claude -p` (mode=functional|full only)
4. Functional Testing -- Run skill against test prompts (mode=functional|full only)
5. Grading -- Grade outputs against expectations, aggregate metrics
6. Description Optimization -- Train/test split trigger optimization (optimize_description=true only)
7. Report -- Consolidated pass/fail with improvement suggestions

### Step 1: Analysis

**Step Configuration**:

- **Purpose**: Analyze the target skill file and load or generate evaluation criteria
- **Input**: skill_path, mode from skill inputs
- **Output**: Skill metadata, eval criteria (loaded from evals/evals.yaml or generated), test plan
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** skill_path and mode
2. **Check** if evals/evals.yaml exists alongside the target SKILL.md
3. **Determine** which steps to execute based on mode
4. **Use TodoWrite** to create task list for all applicable steps
5. **Queue** analysis subagent

#### Phase 2: Execution (Subagents)

In a single message, you spin up **1** subagent to perform the analysis.

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update the analysis task status from 'pending' to 'in_progress' when dispatched

Request the subagent to perform the following steps:

    >>>
    **ultrathink: adopt the Skill Analyst mindset**

    - You're a **Skill Analyst** with deep expertise in skill document analysis who follows these principles:
      - **Thorough Reading**: Read the complete skill document before any assessment
      - **Structural Awareness**: Identify all sections, frontmatter fields, and structural elements
      - **Eval Awareness**: Check for existing evals.yaml and load test cases if present

    **Assignment**
    Analyze the skill file at: [skill_path]

    **Steps**

    1. Read the target SKILL.md completely
    2. Extract frontmatter fields (name, description, model, context, agent, allowed-tools)
    3. Identify all sections and their content
    4. Check if evals/evals.yaml exists in the skill directory
    5. If evals.yaml exists, load test cases and trigger queries
    6. If evals.yaml does NOT exist and mode requires functional testing, generate basic eval criteria from the skill's purpose and description
    7. Classify skill type: objective (deterministic outputs), subjective (quality-based), or process (workflow-based)

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    <report>
    ```yaml
    status: success|failure
    summary: 'Analysis of [skill name]'
    outputs:
      skill_name: '...'
      skill_type: objective|subjective|process
      has_evals: true|false
      eval_source: loaded|generated|none
      sections_found: [list of section headers]
      frontmatter_fields: {name: ..., description: ..., ...}
      test_cases_count: N
      trigger_queries_count: N
    issues: [...]
    ```
    </report>
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze** the analysis report
2. **Apply decision criteria**:
   - If analysis succeeds -> proceed to Step 2
   - If skill file not found -> abort with clear error
3. **Use TodoWrite** to update task status based on decision

### Step 2: Structural Validation

**Step Configuration**:

- **Purpose**: Validate structural correctness -- frontmatter, template compliance, content quality
- **Input**: Skill metadata from Step 1
- **Output**: Structural validation results (pass/fail per check)
- **Sub-skill**: None
- **Parallel Execution**: Yes -- can run frontmatter + template + content + content-placement checks in parallel

#### Phase 1: Planning (You)

**What You Do**:

1. **Prepare** four parallel validation tasks: frontmatter, template compliance, content quality, content placement
2. **Use TodoWrite** to track each validation task
3. **Note** that if `fix: true`, fixable issues should include fix instructions
4. **Queue** all four subagents for parallel execution

#### Phase 2: Execution (Subagents)

In a single message, you spin up **4** subagents to perform validation in parallel.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

**Subagent A: Frontmatter Validator**

    >>>
    You are an independent validator. Treat the target skill file as unfamiliar; do not assume the author's intent is correct.

    **Inputs**
    - Target skill file: [skill_path]
    - Rubric: frontmatter checklist below
    - Report template: YAML block below

    **Checklist**

    1. Read the skill file.
    2. Parse YAML frontmatter between `---` delimiters.
    3. Check required fields: `name` (kebab-case, matches directory), `description` (includes "Use when..." clause).
    4. Check optional fields if present: `model` (valid values: opus, sonnet, haiku), `context` (valid: fork, none), `agent` (valid agent type), `allowed-tools` (comma-separated tool names).
    5. Validate description quality -- should clearly describe purpose AND trigger conditions.
    6. Check name matches directory name in the path.

    **Report**
    Return the following execution report (<1000 tokens):

    <report>
    ```yaml
    status: pass|fail
    summary: 'Frontmatter validation of [skill name]'
    checks:
      frontmatter_present: pass|fail
      name_field: pass|fail
      name_matches_directory: pass|fail
      description_field: pass|fail
      use_when_clause: pass|fail
      optional_fields_valid: pass|fail
    issues: [...]
    fix_instructions: [...]
    ```
    </report>
    <<<

**Subagent B: Template Compliance Checker**

    >>>
    You are an independent validator. Treat the target skill file as unfamiliar; do not assume the author's intent is correct.

    **Inputs**
    - Target skill file: [skill_path]
    - Rubric/template: `template:skill` (resolves to `plugins/governance/constitution/templates/skill.md`; follow references recursively if A points to B)
    - Report template: YAML block below

    **Checklist**

    1. Read the template to understand required sections.
    2. Read the target skill file.
    3. Verify required sections: Introduction (Purpose, Role), Skill Overview (I/O Spec, Visual Overview), Skill Implementation (Steps, Phases).
    4. Check section ordering matches template.
    5. Verify ASCII diagram exists and is properly formatted.
    6. Check subagent instruction blocks use `>>>` / `<<<` delimiters.
    7. Verify report YAML blocks exist at step outputs.
    8. Check report/output blocks are wrapped in `<report>...</report>` boundary tags (advisory convention — see `plugins/governance/constitution/references/authoring-invariants.md`). Record `report_boundary_tags: pass|warn`, never `fail`; list any unwrapped report blocks under issues as a recommendation. This check MUST NOT set the overall status to fail.
    9. Flag any remaining template placeholder text or `<!-- INSTRUCTION: -->` comments.

    **Report**
    Return the following execution report (<1000 tokens):

    <report>
    ```yaml
    status: pass|fail
    summary: 'Template compliance check of [skill name]'
    checks:
      introduction_section: pass|fail
      skill_overview_section: pass|fail
      implementation_section: pass|fail
      section_ordering: pass|fail
      ascii_diagram: pass|fail
      subagent_formatting: pass|fail
      report_boundary_tags: pass|warn
      no_template_placeholders: pass|fail
    issues: [...]
    fix_instructions: [...]
    ```
    </report>
    <<<

**Subagent C: Content Quality Assessor**

    >>>
    You are an independent validator. Treat the target skill file as unfamiliar; do not assume the author's intent is correct.

    **Inputs**
    - Target skill file: [skill_path]
    - Rubric: content-quality checklist below
    - Report template: YAML block below

    **Checklist**

    1. Read the skill file completely.
    2. Check that purpose, when-to-use, and prerequisites are substantive (not placeholder).
    3. Verify input/output specifications are complete and well-typed.
    4. Check the Role/Purpose narrative reads as one continuous editorial voice — and, if the skill performs content edits on existing work (prose, code, configuration, specs), confirm it carries the verbatim **Coherence Mandate** paragraph (`grep -c "Coherence Mandate"` ≥ 1) woven into that Role/Purpose section rather than appended as a trailing bullet, callout, or standalone `## Coherence Mandate` section. Apply the seam test: re-read the host paragraph and check whether the mandate sentences are identifiable as "added later"; if they read as a bolted-on addendum or sit beside the role description as a parallel block, fail this check and instruct the fix to dissolve the seam.
    5. Check each skill step has clear purpose, input, output definitions.
    6. Verify subagent instructions are detailed enough for autonomous execution.
    7. Check data flow -- do step outputs feed correctly into subsequent step inputs?
    8. Assess overall clarity and professionalism.

    **Report**
    Return the following execution report (<1000 tokens):

    <report>
    ```yaml
    status: pass|fail
    summary: 'Content quality assessment of [skill name]'
    checks:
      purpose_clarity: pass|fail
      io_completeness: pass|fail
      coherence_mandate_integration: pass|fail|not_applicable
      step_specifications: pass|fail
      subagent_detail: pass|fail
      data_flow_consistency: pass|fail
      professional_quality: pass|fail
    issues: [...]
    suggestions: [...]
    ```
    </report>
    <<<

**Subagent D: Content Placement Validator**

    >>>
    You are an independent validator. Treat the target skill file as unfamiliar; do not assume the author's intent is correct.

    **Inputs**
    - Target skill file: [skill_path]
    - Skill directory (for sibling `references/` lookup): [skill_dir]
    - Rubric: Content Placement & Coherence Rule (see `plugins/governance/constitution/references/authoring-invariants.md`) and the structured findings schema in `plugins/governance/skills/verify-skill/references/schemas.md` ("Content Placement Validation Report")
    - Report template: YAML block below

    **Duties**

    1. **Identify gated section blocks** — scan headings and prose for mode/scope/flag/language gates. Cues: "When mode is X", "If --flag", "Step 2A / 2B" branch tables, "(language=ts only)", mode matrices, "Skip condition: ...", per-language checklists.
    2. **Flag inline conditional bulk** — for each gated block, count its lines (heading to next sibling heading). If a gated block exceeds 50 lines and lives inline in SKILL.md, flag it with `severity: required_offload`. Suggest a `references/<topic>.md` filename and the one-line pointer that should replace it.
    3. **Detect inverse hiding** — read each file in the sibling `references/` directory. If a reference file contains *unconditional* core workflow steps (steps every invocation must run), flag it with `severity: hidden_core` — always-on work must live in SKILL.md, not behind a pointer.
    4. **Suggest workflow splits** — if a gated block is a coherent, independently-triggerable workflow (has its own clear input, output, and trigger conditions), include a `suggested_split` finding (severity `suggestion`, never required). The user decides per case.
    5. **Allow short conditionals** — non-bulky `if X then do Y` lines (under ~50 lines) MAY stay inline; do not flag them.
    6. **Allow always-on bulk** — long checklists or tables consulted every run MAY stay inline; flag only if you can demonstrate the content is gated.

    **Report**
    Return the following execution report (<1500 tokens):

    <report>
    ```yaml
    status: pass|fail
    summary: 'Content placement validation of [skill name]'
    checks:
      no_inline_conditional_bulk: pass|fail
      no_hidden_core_in_references: pass|fail
    findings:
      - severity: required_offload|hidden_core|suggestion
        location: 'SKILL.md:line_start-line_end' | 'references/<file>.md'
        gate: 'mode=functional' | 'flag --fix' | 'language=ts' | 'always-on (inverse)'
        line_count: N
        summary: 'one-line description of the block'
        recommendation: 'move to references/<topic>.md' | 'split into separate skill <name>' | 'inline into SKILL.md core'
        replacement_pointer: 'For X, see references/<topic>.md'  # only when recommending offload
    issues: [...]
    suggestions: [...]
    ```
    </report>
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect** all 4 subagent reports
2. **Apply decision criteria**:
   - If ALL pass -> proceed to Step 3 (or skip to Step 7 if mode=structural)
   - If ANY fail and fix=true -> spawn fix subagent with aggregated fix_instructions, then re-validate (max 2 retries)
   - If ANY fail and fix=false -> record issues, proceed to Step 7
3. **Select next action**:
   - **PROCEED**: All structural checks pass -> move to Step 3 (or Step 7 if mode=structural)
   - **FIX ISSUES**: fix=true and issues found -> create fix batches, re-run Phase 2, max 2 retries
   - **SKIP TO REPORT**: mode=structural -> skip Steps 3-6, go to Step 7
4. **Use TodoWrite** to update task list based on decision

### Steps 3–6: Functional Mode Branch (mode=functional|full only)

The functional branch — trigger testing, functional testing, grading, and optional description optimization — is loaded on demand to keep this SKILL.md focused on the always-on core. When `mode=functional` or `mode=full`, follow `references/functional-mode.md` for the complete step bodies.

> **Step 3 (functional/full mode only)** — Trigger Testing: dispatch 1 subagent to measure trigger_rate and false_positive_rate against eval queries. See `references/functional-mode.md#step-3-trigger-testing-modefunctionalfull-only`.
>
> **Step 4 (functional/full mode only)** — Functional Testing: dispatch up to 3 parallel subagents to execute test prompts and capture raw outputs. See `references/functional-mode.md#step-4-functional-testing-modefunctionalfull-only`.
>
> **Step 5 (functional/full mode only)** — Grading: dispatch up to 3 parallel grader subagents to score outputs against expectations and aggregate pass_rate. See `references/functional-mode.md#step-5-grading-modefunctionalfull-only`.
>
> **Step 6 (mode=full + optimize_description=true only)** — Description Optimization: dispatch 1 subagent to iteratively refine the description via 60/40 train/test split (max 5 iterations). See `references/functional-mode.md#step-6-description-optimization-optimize_descriptiontrue-only`.

After completing the applicable branch steps (or skipping them when `mode=structural`), proceed to Step 7.

### Step 7: Report

**Step Configuration**:

- **Purpose**: Consolidate all verification results into a final pass/fail report
- **Input**: Results from all completed steps
- **Output**: Final verification report
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Collect** all step results from Steps 1-6 (whichever were executed)
2. **Determine** overall status: pass (all checks pass), fail (any fatal), partial (non-fatal issues)
3. **Compile** issues and suggestions from all steps

#### Phase 2: Execution (You)

No subagent needed -- you aggregate the results yourself.

1. **Compile** structural results from Step 2 (frontmatter, template_compliance, content_quality)
2. **Compile** functional results from Steps 3-5 if executed (trigger_rate, false_positive_rate, pass_rate, grading_summary)
3. **Compile** description optimization results from Step 6 if executed
4. **Aggregate** all issues and suggestions
5. **Determine** final status based on all results

#### Phase 4: Decision (You)

**What You Do**:

1. **Finalize** the verification report
2. **Use TodoWrite** to mark all remaining tasks as completed
3. **Output** the final report

### Skill Completion

**Report the skill output as specified**:

<report>
```yaml
skill: verify-skill
status: completed
outputs:
  verification_report:
    status: pass|fail|partial
    structural:
      frontmatter: pass|fail
      template_compliance: pass|fail
      content_quality: pass|fail
      content_placement: pass|fail
    functional:
      pass_rate: 0.XX
      test_cases: N
      grading_summary: '...'
    trigger:
      trigger_rate: 0.XX
      false_positive_rate: 0.XX
    description:
      original: '...'
      optimized: '...'
      improvement: '+X%'
    issues: [...]
    suggestions: [...]
summary: |
  Verification of [skill name] completed with status [status].
  [Summary of findings and recommendations]
```
</report>
