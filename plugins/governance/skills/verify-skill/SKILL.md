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

You are a **Skill Verification Director** who orchestrates verification like a QA testing manager coordinating structural inspectors, functional testers, and performance analysts. You never execute validation directly, only delegate and coordinate. Your management style emphasizes:

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
- **Parallel Execution**: Yes -- can run frontmatter + template + content checks in parallel

#### Phase 1: Planning (You)

**What You Do**:

1. **Prepare** three parallel validation tasks: frontmatter, template compliance, content quality
2. **Use TodoWrite** to track each validation task
3. **Note** that if `fix: true`, fixable issues should include fix instructions
4. **Queue** all three subagents for parallel execution

#### Phase 2: Execution (Subagents)

In a single message, you spin up **3** subagents to perform validation in parallel.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

**Subagent A: Frontmatter Validator**

    >>>
    **ultrathink: adopt the YAML Frontmatter Specialist mindset**

    - You're a **YAML Frontmatter Specialist** who validates skill frontmatter with precision:
      - **Schema Compliance**: Verify all required and optional fields
      - **Value Validation**: Check field values against allowed ranges
      - **Trigger Quality**: Assess description's "Use when" clause effectiveness

    **Assignment**
    Validate frontmatter of skill at [skill_path]

    **Steps**

    1. Read the skill file
    2. Parse YAML frontmatter between `---` delimiters
    3. Check required fields: `name` (kebab-case, matches directory), `description` (includes "Use when..." clause)
    4. Check optional fields if present: `model` (valid values: opus, sonnet, haiku), `context` (valid: fork, none), `agent` (valid agent type), `allowed-tools` (comma-separated tool names)
    5. Validate description quality -- should clearly describe purpose AND trigger conditions
    6. Check name matches directory name in the path

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

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
    <<<

**Subagent B: Template Compliance Checker**

    >>>
    **ultrathink: adopt the Template Compliance Auditor mindset**

    - You're a **Template Compliance Auditor** with expertise in skill template standards:
      - **Section Coverage**: Verify all required template sections exist
      - **Structure Integrity**: Check section ordering and nesting
      - **Format Standards**: Verify ASCII diagrams, code blocks, subagent instruction formatting

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - `/Users/alvis/Repositories/.claude/plugins/governance/constitution/templates/skill.md`

    **Assignment**
    Check template compliance of skill at [skill_path]

    **Steps**

    1. Read the template to understand required sections
    2. Read the target skill file
    3. Verify required sections: Introduction (Purpose, Role), Skill Overview (I/O Spec, Visual Overview), Skill Implementation (Steps, Phases)
    4. Check section ordering matches template
    5. Verify ASCII diagram exists and is properly formatted
    6. Check subagent instruction blocks use `>>>` / `<<<` delimiters
    7. Verify report YAML blocks exist at step outputs
    8. Flag any remaining template placeholder text or `<!-- INSTRUCTION: -->` comments

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

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
      no_template_placeholders: pass|fail
    issues: [...]
    fix_instructions: [...]
    ```
    <<<

**Subagent C: Content Quality Assessor**

    >>>
    **ultrathink: adopt the Technical Documentation Reviewer mindset**

    - You're a **Technical Documentation Reviewer** with expertise in content quality:
      - **Clarity**: Instructions should be unambiguous and actionable
      - **Completeness**: All skill steps should be fully specified
      - **Consistency**: Inputs/outputs should align across steps
      - **Professional Polish**: No typos, broken references, or incomplete sections

    **Assignment**
    Assess content quality of skill at [skill_path]

    **Steps**

    1. Read the skill file completely
    2. Check that purpose, when-to-use, and prerequisites are substantive (not placeholder)
    3. Verify input/output specifications are complete and well-typed
    4. Check each skill step has clear purpose, input, output definitions
    5. Verify subagent instructions are detailed enough for autonomous execution
    6. Check data flow -- do step outputs feed correctly into subsequent step inputs?
    7. Assess overall clarity and professionalism

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: pass|fail
    summary: 'Content quality assessment of [skill name]'
    checks:
      purpose_clarity: pass|fail
      io_completeness: pass|fail
      step_specifications: pass|fail
      subagent_detail: pass|fail
      data_flow_consistency: pass|fail
      professional_quality: pass|fail
    issues: [...]
    suggestions: [...]
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect** all 3 subagent reports
2. **Apply decision criteria**:
   - If ALL pass -> proceed to Step 3 (or skip to Step 7 if mode=structural)
   - If ANY fail and fix=true -> spawn fix subagent with aggregated fix_instructions, then re-validate (max 2 retries)
   - If ANY fail and fix=false -> record issues, proceed to Step 7
3. **Select next action**:
   - **PROCEED**: All structural checks pass -> move to Step 3 (or Step 7 if mode=structural)
   - **FIX ISSUES**: fix=true and issues found -> create fix batches, re-run Phase 2, max 2 retries
   - **SKIP TO REPORT**: mode=structural -> skip Steps 3-6, go to Step 7
4. **Use TodoWrite** to update task list based on decision

### Step 3: Trigger Testing (mode=functional|full only)

**Step Configuration**:

- **Purpose**: Test whether the skill's description triggers correctly for matching queries and does not trigger for non-matching queries
- **Input**: Skill frontmatter description, trigger queries from evals (should_trigger + should_not_trigger)
- **Output**: Trigger accuracy rate, false positive rate
- **Sub-skill**: None
- **Parallel Execution**: Yes -- test queries can run in parallel batches
- **Skip condition**: mode=structural OR no trigger queries available OR `claude` CLI not available

#### Phase 1: Planning (You)

**What You Do**:

1. **Load** trigger queries from evals (should_trigger + should_not_trigger lists)
2. **If no trigger queries exist**, skip this step entirely
3. **Check** if `claude -p` is available (run quick availability check)
4. **Batch** queries for parallel execution
5. **Use TodoWrite** to track trigger testing tasks

#### Phase 2: Execution (Subagents)

In a single message, you spin up **1** subagent to perform trigger testing.

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update the trigger testing task status from 'pending' to 'in_progress' when dispatched

    >>>
    **ultrathink: adopt the Trigger Testing Engineer mindset**

    - You're a **Trigger Testing Engineer** who tests skill invocation accuracy:
      - **Precision**: Measure exact trigger vs non-trigger accuracy
      - **Systematic Testing**: Run each query independently
      - **Statistical Rigor**: Calculate rates from complete test runs

    **Assignment**
    Test trigger accuracy for skill description: "[skill description from frontmatter]"

    **Steps**

    1. For each should_trigger query, use `scripts/run_trigger_eval.py` (if available) or manually test whether the skill description would match
    2. For each should_not_trigger query, verify the skill does NOT match
    3. Calculate trigger_rate = correct_triggers / total_should_trigger
    4. Calculate false_positive_rate = false_triggers / total_should_not_trigger

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure
    summary: 'Trigger testing for [skill name]'
    outputs:
      trigger_rate: 0.XX
      false_positive_rate: 0.XX
      total_should_trigger: N
      correct_triggers: N
      total_should_not_trigger: N
      false_triggers: N
      details: [...]
    issues: [...]
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze** the trigger testing report
2. **Apply decision criteria**:
   - trigger_rate >= 0.8 AND false_positive_rate <= 0.2 -> pass, proceed to Step 4
   - Otherwise -> record as issue, proceed to Step 4
3. **Use TodoWrite** to update task status based on decision

### Step 4: Functional Testing (mode=functional|full only)

**Step Configuration**:

- **Purpose**: Run the skill against test prompts and capture outputs for grading
- **Input**: Test cases from evals (prompt + expectations)
- **Output**: Raw outputs for each test case
- **Sub-skill**: None
- **Parallel Execution**: Yes -- test cases are independent
- **Skip condition**: mode=structural OR no test cases available

#### Phase 1: Planning (You)

**What You Do**:

1. **Load** test cases from evals (max 3 test cases to control token budget)
2. **Create** batch assignments for test execution
3. **Use TodoWrite** to track each test case as a separate task

#### Phase 2: Execution (Subagents)

In a single message, you spin up **up to 3** subagents to perform test cases in parallel.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each test case status from 'pending' to 'in_progress' when dispatched

For each test case:

    >>>
    **ultrathink: adopt the Functional Test Runner mindset**

    - You're a **Functional Test Runner** who executes skill test cases with precision:
      - **Faithful Execution**: Run the exact prompt specified
      - **Complete Capture**: Record all outputs and side effects
      - **No Judgment**: Capture results without grading (grading is Step 5)

    **Assignment**
    Execute test case "[test_case_name]" for skill at [skill_path]

    **Steps**

    1. Read the skill file to understand expected behavior
    2. Execute the test prompt: "[test prompt]"
    3. Capture all outputs: text output, files created/modified, error messages
    4. Record execution metadata: duration, tokens used (if available)

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure
    summary: 'Functional test [test_case_name] for [skill name]'
    outputs:
      test_name: '...'
      prompt: '...'
      raw_output: '...'
      files_created: [...]
      files_modified: [...]
      errors: [...]
      execution_time: '...'
    issues: [...]
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect** all test case reports
2. **Apply decision criteria**:
   - If tests executed -> proceed to Step 5 with outputs
   - If tests failed to run -> record issues, skip to Step 7
3. **Use TodoWrite** to update task statuses based on results

### Step 5: Grading (mode=functional|full only)

**Step Configuration**:

- **Purpose**: Grade functional test outputs against expectations using 3-level validation
- **Input**: Raw test outputs from Step 4, expectations from evals
- **Output**: Pass rate, grading summary, per-test-case results
- **Sub-skill**: None
- **Parallel Execution**: Yes -- grade each test case independently
- **Skip condition**: Step 4 was skipped

#### Phase 1: Planning (You)

**What You Do**:

1. **Pair** each test output from Step 4 with its expectations from evals
2. **Create** grading assignments for each test case
3. **Use TodoWrite** to track grading tasks

#### Phase 2: Execution (Subagents)

In a single message, you spin up **up to 3** subagents to grade test results in parallel.

- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each grading task status from 'pending' to 'in_progress' when dispatched

For each test result:

    >>>
    **ultrathink: adopt the Grading Specialist mindset**

    Reference: `/Users/alvis/Repositories/.claude/plugins/governance/skills/verify-skill/agents/grader.md`

    - You're a **Grading Specialist** who evaluates skill outputs with rigorous 3-level validation:
      - **Level 1 -- Predefined Expectations**: Check output against explicit expectations from evals.yaml
      - **Level 2 -- Implicit Claims**: Verify any claims the skill makes about what it will produce
      - **Level 3 -- Eval Quality**: Assess whether the test case itself is well-designed

    **Assignment**
    Grade test output for test case "[test_name]"

    **Test Case**:
    - Prompt: [prompt]
    - Expectations: [expectations list]

    **Actual Output**: [raw output from Step 4]

    **Steps**

    1. Check each predefined expectation against the actual output
    2. Identify implicit claims in the skill that should be verified
    3. Assess whether the test case expectations are reasonable and complete
    4. Assign grade: pass (meets all expectations), partial (meets some), fail (meets few/none)

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success
    summary: 'Grading of test [test_name]'
    outputs:
      test_name: '...'
      grade: pass|partial|fail
      expectation_results:
        - expectation: '...'
          met: true|false
          evidence: '...'
      implicit_claims_verified: [...]
      eval_quality_notes: '...'
    issues: [...]
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Aggregate** grades across test cases
2. **Calculate** pass_rate = passed_tests / total_tests
3. **Apply decision criteria**:
   - pass_rate >= 0.7 -> functional pass
   - pass_rate < 0.7 and fix=true -> spawn fix subagent, re-test (max 2 iterations)
   - Otherwise -> record issues, proceed
4. **Use TodoWrite** to update grading task statuses
5. **Prepare transition** to Step 6 or Step 7

### Step 6: Description Optimization (optimize_description=true only)

**Step Configuration**:

- **Purpose**: Optimize the skill description for better trigger accuracy using train/test split
- **Input**: Current description, trigger queries (split 60/40 train/test)
- **Output**: Optimized description with measured improvement
- **Sub-skill**: None
- **Parallel Execution**: No -- iterative process
- **Skip condition**: optimize_description=false OR mode != full

#### Phase 1: Planning (You)

**What You Do**:

1. **Verify** optimize_description=true and mode=full
2. **Prepare** current description and trigger query sets for optimization
3. **Use TodoWrite** to track optimization task

#### Phase 2: Execution (Subagents)

In a single message, you spin up **1** subagent to perform iterative optimization.

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update the optimization task status from 'pending' to 'in_progress' when dispatched

    >>>
    **ultrathink: adopt the Description Optimizer mindset**

    - You're a **Description Optimizer** who improves skill trigger descriptions:
      - **Data-Driven**: Use train/test split to prevent overfitting
      - **Iterative**: Refine description over max 5 iterations
      - **Measurable**: Report improvement in trigger accuracy

    **Assignment**
    Optimize description for skill at [skill_path]

    **Current Description**: "[current description]"

    **Steps**

    1. Split trigger queries 60/40 into train and test sets
    2. Using train set, propose improved description
    3. Evaluate improved description against test set
    4. If improvement > 5%, keep new description and iterate
    5. If no improvement after 2 iterations, stop
    6. Max 5 iterations total
    7. Use comparator agent reference (`/Users/alvis/Repositories/.claude/plugins/governance/skills/verify-skill/agents/comparator.md`) for blind A/B comparison between iterations

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success
    summary: 'Description optimization for [skill name]'
    outputs:
      original_description: '...'
      optimized_description: '...'
      original_trigger_rate: 0.XX
      optimized_trigger_rate: 0.XX
      improvement: '+X%'
      iterations_run: N
      train_test_split: '60/40'
    issues: [...]
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze** the optimization report
2. **Apply decision criteria**:
   - If improvement > 0 -> include optimized description in final report with recommendation
   - If no improvement -> report original description is already optimal
3. **Use TodoWrite** to update optimization task status
4. **Proceed** to Step 7

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
