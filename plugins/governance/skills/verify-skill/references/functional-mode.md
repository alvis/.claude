# Functional Mode Steps (Steps 3–6)

Loaded by `SKILL.md` when `mode=functional` or `mode=full`. Step 6 additionally requires `optimize_description=true` and `mode=full`. These steps are the gated branch of the verify-skill workflow; the always-on core (Steps 1, 2, 7) lives in `SKILL.md`.

## Step 3: Trigger Testing (mode=functional|full only)

**Step Configuration**:

- **Purpose**: Test whether the skill's description triggers correctly for matching queries and does not trigger for non-matching queries
- **Input**: Skill frontmatter description, trigger queries from evals (should_trigger + should_not_trigger)
- **Output**: Trigger accuracy rate, false positive rate
- **Sub-skill**: None
- **Parallel Execution**: Yes -- test queries can run in parallel batches
- **Skip condition**: mode=structural OR no trigger queries available OR `claude` CLI not available

### Phase 1: Planning (You)

**What You Do**:

1. **Load** trigger queries from evals (should_trigger + should_not_trigger lists)
2. **If no trigger queries exist**, skip this step entirely
3. **Check** if `claude -p` is available (run quick availability check)
4. **Batch** queries for parallel execution
5. **Use TodoWrite** to track trigger testing tasks

### Phase 2: Execution (Subagents)

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

### Phase 4: Decision (You)

**What You Do**:

1. **Analyze** the trigger testing report
2. **Apply decision criteria**:
   - trigger_rate >= 0.8 AND false_positive_rate <= 0.2 -> pass, proceed to Step 4
   - Otherwise -> record as issue, proceed to Step 4
3. **Use TodoWrite** to update task status based on decision

## Step 4: Functional Testing (mode=functional|full only)

**Step Configuration**:

- **Purpose**: Run the skill against test prompts and capture outputs for grading
- **Input**: Test cases from evals (prompt + expectations)
- **Output**: Raw outputs for each test case
- **Sub-skill**: None
- **Parallel Execution**: Yes -- test cases are independent
- **Skip condition**: mode=structural OR no test cases available

### Phase 1: Planning (You)

**What You Do**:

1. **Load** test cases from evals (max 3 test cases to control token budget)
2. **Create** batch assignments for test execution
3. **Use TodoWrite** to track each test case as a separate task

### Phase 2: Execution (Subagents)

In a single message, you spin up **up to 3** subagents to perform test cases in parallel.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each test case status from 'pending' to 'in_progress' when dispatched

For each test case:

    >>>
    You are an independent test runner. Treat the target skill file as unfamiliar; capture raw results without judging quality (grading is Step 5).

    **Inputs**
    - Target skill file: [skill_path]
    - Test case name: [test_case_name]
    - Test prompt: "[test prompt]"
    - Report template: YAML block below

    **Steps**

    1. Read the skill file to understand expected behavior.
    2. Execute the test prompt as given.
    3. Capture all outputs: text output, files created/modified, error messages.
    4. Record execution metadata: duration, tokens used (if available).

    **Report**
    Return the following execution report (<1000 tokens):

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

### Phase 4: Decision (You)

**What You Do**:

1. **Collect** all test case reports
2. **Apply decision criteria**:
   - If tests executed -> proceed to Step 5 with outputs
   - If tests failed to run -> record issues, skip to Step 7
3. **Use TodoWrite** to update task statuses based on results

## Step 5: Grading (mode=functional|full only)

**Step Configuration**:

- **Purpose**: Grade functional test outputs against expectations using 3-level validation
- **Input**: Raw test outputs from Step 4, expectations from evals
- **Output**: Pass rate, grading summary, per-test-case results
- **Sub-skill**: None
- **Parallel Execution**: Yes -- grade each test case independently
- **Skip condition**: Step 4 was skipped

### Phase 1: Planning (You)

**What You Do**:

1. **Pair** each test output from Step 4 with its expectations from evals
2. **Create** grading assignments for each test case
3. **Use TodoWrite** to track grading tasks

### Phase 2: Execution (Subagents)

In a single message, you spin up **up to 3** subagents to grade test results in parallel.

- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each grading task status from 'pending' to 'in_progress' when dispatched

For each test result:

    >>>
    You are an independent grader. Treat the test output as unfamiliar; do not assume it is correct.

    **Inputs**
    - Test case name: [test_name]
    - Prompt: [prompt]
    - Expectations: [expectations list]
    - Actual output: [raw output from Step 4]
    - Rubric: `../agents/grader.md`
    - Report template: YAML block below

    **Steps**

    1. Check each predefined expectation against the actual output.
    2. Identify implicit claims in the skill that should be verified.
    3. Assess whether the test case expectations are reasonable and complete.
    4. Assign grade: pass (meets all expectations), partial (meets some), fail (meets few/none).

    **Report**
    Return the following execution report (<1000 tokens):

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

### Phase 4: Decision (You)

**What You Do**:

1. **Aggregate** grades across test cases
2. **Calculate** pass_rate = passed_tests / total_tests
3. **Apply decision criteria**:
   - pass_rate >= 0.7 -> functional pass
   - pass_rate < 0.7 and fix=true -> spawn fix subagent, re-test (max 2 iterations)
   - Otherwise -> record issues, proceed
4. **Use TodoWrite** to update grading task statuses
5. **Prepare transition** to Step 6 or Step 7

## Step 6: Description Optimization (optimize_description=true only)

**Step Configuration**:

- **Purpose**: Optimize the skill description for better trigger accuracy using train/test split
- **Input**: Current description, trigger queries (split 60/40 train/test)
- **Output**: Optimized description with measured improvement
- **Sub-skill**: None
- **Parallel Execution**: No -- iterative process
- **Skip condition**: optimize_description=false OR mode != full

### Phase 1: Planning (You)

**What You Do**:

1. **Verify** optimize_description=true and mode=full
2. **Prepare** current description and trigger query sets for optimization
3. **Use TodoWrite** to track optimization task

### Phase 2: Execution (Subagents)

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
    7. Use comparator agent reference (`../agents/comparator.md`) for blind A/B comparison between iterations

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

### Phase 4: Decision (You)

**What You Do**:

1. **Analyze** the optimization report
2. **Apply decision criteria**:
   - If improvement > 0 -> include optimized description in final report with recommendation
   - If no improvement -> report original description is already optimal
3. **Use TodoWrite** to update optimization task status
4. **Proceed** to Step 7
