# Create Test

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Create the ABSOLUTE MINIMUM tests needed for either covering uncovered code lines OR scaffolding tests for unwritten code following TDD principles, strictly adhering to the minimal testing principle where every test must add unique value.
**When to use**: 
- When you need to create tests for uncovered code areas to improve coverage
- When implementing TDD approach by writing tests before code implementation
- When scaffolding test structure for planned features
**Prerequisites**: TypeScript/JavaScript codebase with testing framework (Vitest), understanding of existing coverage gaps OR interface specifications for TDD, and Testing Standards knowledge.

### Your Role

You are a **Test Coverage Optimizer** who orchestrates minimal test creation like a efficiency expert eliminating all redundancy while achieving coverage goals or establishing TDD structure. You never execute coding tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Assign coverage analysis and minimal test creation to specialized subagents
- **Redundancy Elimination**: Ensure every test adds unique value with zero duplication
- **Coverage Focus**: Only create tests that actually improve line coverage or define intended behavior
- **Minimal Principle Authority**: Enforce that fewer tests with same coverage is always better

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- None

#### Optional Inputs

- **Test Scope**: Specific files, directories, or code areas to test (default: all uncovered code in codebase)
- **Test Mode**: "coverage" for coverage-based testing or "tdd" for test-driven development (default: "coverage")
- **Interface Definition**: Optional interface/API specification for TDD tests
- **Intended Behavior**: Description of expected behavior for unwritten code (for TDD mode)

#### Expected Outputs

- **Minimal Test Files**: Absolute minimum tests achieving maximum coverage or TDD scaffolding
- **Coverage Report**: Validation showing coverage improvement with test count (coverage mode only)
- **TDD Scaffolding**: Test structure for unwritten code (TDD mode only)
- **Redundancy Analysis**: Report of tests avoided/removed through consolidation
- **Standards Compliance**: Confirmation of minimal testing principle adherence

#### Data Flow Summary

The workflow takes an optional test scope and mode, either identifies uncovered code lines to create minimum tests OR scaffolds TDD tests for unwritten code based on interfaces/behavior, while aggressively eliminating any redundancy and ensuring logical test expectations.

### Visual Overview

#### Main Workflow Flow

```plaintext
   YOU                        SUBAGENT EXECUTES
(Orchestrates Only)              (Performs Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Minimal Test Creation] ─────→ (4-Phase Execution)
   |                                    │
   ├─ Phase 1: Coverage/TDD Analysis ───┤ (Single subagent)
   ├─ Phase 2: Test Execution ──────────┤ (Single subagent)
   ├─ Phase 3: Redundancy Removal ──────┤ (Single subagent)
   └─ Phase 4: Fix & Iterate ───────────┘
       ↑                    │
       └────────────────────┘ (Loop if needed)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Single subagent per phase (no parallel)
• LOOP: Phase 4 returns to Phase 2 if fixes/removals needed
• FOCUS: Absolute minimum tests with logical correctness
═══════════════════════════════════════════════════════════════════

Note: 
• You: Enforce minimal testing principle throughout
• Subagents: Create ONLY necessary tests with logical expectations
• Review: Aggressively remove redundant tests
• Success: Maximum coverage/TDD structure with minimum tests
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Minimal Test Creation with 4-Phase Execution

### Step 1: Minimal Test Creation with 4-Phase Execution

**Step Configuration**:

- **Purpose**: Create absolute minimum tests to cover uncovered lines or scaffold TDD tests through iterative refinement
- **Input**: Optional test scope, mode, interface definition, and intended behavior from workflow inputs
- **Output**: Minimal test files, coverage report (if coverage mode), TDD scaffolding (if TDD mode) for workflow outputs
- **Sub-workflow**: None
- **Parallel Execution**: No - single subagent per phase

#### Phase 1: Coverage/TDD Analysis & Test Proposal (You + Subagent)

**What You Do**:

1. **Receive inputs** including optional test scope, mode, interface definition
2. **Determine analysis approach**:
   - If coverage mode: Prepare to run coverage scripts
   - If TDD mode: Prepare to analyze interfaces/behavior specifications
3. **Use TodoWrite** to track analysis task
4. **Dispatch single subagent** for analysis

**What You Send to Analysis Subagent**:

In a single message, You spin up ONE subagent to analyze coverage gaps or TDD requirements.

- **[CRITICAL]** Subagent MUST use coverage scripts for coverage mode
- **[CRITICAL]** Subagent MUST propose MINIMUM tests for maximum value
- **[CRITICAL]** Use TodoWrite to track analysis progress

Request the subagent to perform analysis:

    >>>
    **ultrathink: adopt the Minimal Coverage/TDD Analyst mindset**

    - You're a **Minimal Coverage/TDD Analyst** with expertise in identifying the absolute minimum tests needed:
      - **Coverage Excellence**: Use coverage tools to find uncovered lines
      - **TDD Planning**: Identify interfaces needing test scaffolding
      - **Minimal Principle**: Propose ONLY tests that add unique value
      - **Efficiency Focus**: Maximize coverage/behavior definition per test

    **Read the following assigned standards** and follow them recursively:

    - constitutions/standards/coding/testing.md (ESPECIALLY the Minimal Testing Principle section)
    - constitutions/standards/coding/typescript.md
    - constitutions/standards/coding/naming/files.md

    **Assignment**
    You're assigned to analyze for [mode: coverage|tdd]:

    - Test Scope: [scope areas or 'all uncovered']
    - Test Mode: [coverage|tdd]
    - Interface Definition: [if provided for TDD]
    - Intended Behavior: [if provided for TDD]

    **[CRITICAL INSTRUCTION]**: You MUST only propose tests that are ABSOLUTELY NECESSARY. Each test must verify a DIFFERENT code path or behavior.

    **Steps**

    For Coverage Mode:
    1. Run coverage script:
       - Execute `npm run coverage` or `vitest coverage` or similar
       - Parse coverage report output
       - Identify ALL uncovered lines/branches
       - Group related uncovered sections
       - Skip lines marked with /* v8 ignore */
    
    For TDD Mode:
    1. Analyze interfaces/behavior:
       - Review provided interface definitions
       - Identify each method/function needing tests
       - Plan test cases for expected behaviors
       - Determine if skeleton (todo) or actual tests needed
    
    2. Propose MINIMAL test set:
       - For coverage: ONE test per group of related uncovered lines
       - For TDD: Minimum tests to define all expected behaviors
       - NEVER propose multiple tests for same logic
       - Identify where parameterized tests can be used
       - Ensure NO redundancy in proposals

    3. Validate necessity:
       - Each proposed test covers unique behavior
       - No existing test covers this path (coverage mode)
       - Test defines essential behavior contract (TDD mode)

    **Report**
    **[CRITICAL]** You MUST return:

    - Coverage data or interface analysis results
    - MINIMAL set of tests proposed
    - Tests explicitly NOT created due to redundancy
    - Confirmation that EVERY proposed test is necessary

    ```yaml
    status: success|failure
    summary: 'Analysis complete: X tests needed'
    outputs:
      mode: coverage|tdd
      analysis_data:
        uncovered_lines: [...] # for coverage mode
        interfaces_found: [...] # for TDD mode
      proposed_tests:
        - name: 'test description'
          type: 'actual|todo' # todo for skeleton tests
          covers: 'lines X-Y' # or 'behavior: ...'
          unique_value: 'why this test is necessary'
      tests_avoided: ['redundant test 1', 'redundant test 2']
      minimal_validation: 'Confirmed no test can be removed'
    issues: []
    ```
    <<<

#### Phase 2: Test Execution (Subagent)

**What You Send to Test Creation Subagent**:

In a single message, You spin up ONE subagent to create the proposed minimal tests.

- **[CRITICAL]** Every test MUST have LOGICAL expectations (e.g., sum(1,1) = 2, NOT 3)
- **[CRITICAL]** NO test variations with different data
- **[CRITICAL]** Use TodoWrite to track test creation

Request the subagent to create minimal tests:

    >>>
    **ultrathink: adopt the Minimal Test Creator mindset**

    - You're a **Minimal Test Creator** who creates the absolute minimum tests:
      - **Zero Redundancy**: NEVER create tests that duplicate coverage
      - **Logical Correctness**: ALL test expectations MUST make logical sense
      - **TDD Support**: Create todo skeletons or actual tests as appropriate
      - **Maximum Efficiency**: Each test must provide maximum value

    **Read the following assigned standards** and follow them recursively:

    - constitutions/standards/coding/testing.md (FOCUS on Zero Redundancy Rule)
    - constitutions/standards/coding/typescript.md
    - constitutions/standards/coding/naming/files.md

    **Assignment**
    Create these MINIMAL tests:

    - Test Mode: [coverage|tdd]
    - Proposed Tests: [from Phase 1]
    - Interface Definition: [if TDD mode]

    **[CRITICAL INSTRUCTION]**: 
    1. You are EXPLICITLY FORBIDDEN from creating redundant tests
    2. ALL test expectations MUST be mathematically/logically correct (e.g., sum(1,1) MUST equal 2, not 3)
    3. For TDD without implementation: use describe.todo() or create tests that won't run yet

    **Steps**

    1. Create each proposed test based on mode:
       
       For Coverage Mode:
       - Write test using AAA pattern with proper spacing
       - Use vi.hoisted pattern for mocks
       - Ensure test covers ALL intended lines
       - Expectations MUST be logically correct
       
       For TDD Mode (no implementation exists):
       - If no interface: Use describe.todo() and it.todo() syntax:
         ```typescript
         describe.todo('fn:calculateTotal')
         it.todo('should sum all item prices')
         it.todo('should apply discounts correctly')
         ```
       - If interface provided: Create actual tests (won't run):
         ```typescript
         describe('fn:calculateTotal', () => {
           it('should sum all item prices', () => {
             const items = [{ price: 10 }, { price: 20 }];
             const expected = 30; // LOGICAL expectation
             
             const result = calculateTotal(items);
             
             expect(result).toBe(expected);
           });
         });
         ```
    
    2. Verify logical correctness:
       - ALL mathematical operations must be correct
       - String operations must produce logical results
       - Boolean logic must be sound
       - NO arbitrary test values
    
    3. Apply minimal principle:
       - If multiple tests cover same path, DELETE extras
       - Use parameterized tests instead of copies
       - Ensure EVERY line of test code is necessary

    **Report**
    **[CRITICAL]** You MUST return:

    - Tests created (with coverage or behavior defined)
    - Confirmation of logical correctness
    - Tests consolidated/removed to avoid redundancy

    ```yaml
    status: success|failure
    summary: 'Created X minimal tests'
    modifications: ['test-file-1.spec.ts', 'test-file-2.spec.ts']
    outputs:
      tests_created: 
        - file: 'feature.spec.ts'
          test_count: 3
          test_type: 'actual|todo'
          logical_validation: 'all expectations verified correct'
      tests_not_created: ['avoided 5 redundant tests']
      minimal_confirmation: 'No test removable without losing value'
    issues: []
    ```
    <<<

#### Phase 3: Redundancy Removal & Logic Review (Subagent)

**What You Send to Review Subagent**:

In a single message, You spin up ONE review subagent to eliminate redundancy and verify logical correctness.

- **[CRITICAL]** Review MUST verify ALL test expectations are logical
- **[CRITICAL]** Consolidate tests wherever possible
- **[CRITICAL]** Use TodoWrite to track review

Request the review subagent to validate tests:

    >>>
    **ultrathink: adopt the Test Logic & Redundancy Validator mindset**

    - You're a **Test Logic & Redundancy Validator** who ensures test quality:
      - **Logic Verification**: Ensure ALL expectations make mathematical/logical sense
      - **Aggressive Removal**: Delete ANY test that doesn't add unique value
      - **Consolidation Expert**: Merge similar tests into parameterized versions
      - **Quality Champion**: Tests must be both minimal AND correct

    **Review the standards that were applied**:

    - constitutions/standards/coding/testing.md - Enforce Zero Redundancy Rule

    **Review Assignment**
    Review these created tests for logic and redundancy:

    - Test files: [from Phase 2]
    - Test mode: [coverage|tdd]

    **[CRITICAL INSTRUCTION]**: 
    1. EVERY test expectation must be logically sound (e.g., 2+2=4, not 5)
    2. Your SUCCESS is measured by tests removed AND logical correctness verified

    **Review Steps**

    1. Verify logical correctness:
       - Check ALL mathematical calculations are correct
       - Verify string manipulations produce expected results
       - Ensure boolean logic is sound
       - Flag ANY nonsensical test values
       - Example violations to catch:
         * sum(1, 1) expecting 3
         * concat('a', 'b') expecting 'c'
         * isValid(validData) expecting false
    
    2. Analyze for redundancy:
       - Find tests covering same code paths
       - Identify data variation tests
       - Locate consolidation opportunities
       - Find overlapping coverage
    
    3. Validate minimal set:
       - Confirm removals maintain coverage/behavior definition
       - Verify no further consolidation possible
       - Ensure absolute minimum achieved

    **Report**
    **[CRITICAL]** You MUST report:

    - Logical correctness verification results
    - Tests identified for removal (with reasons)
    - Consolidation opportunities found
    - Final minimal set confirmation

    ```yaml
    status: pass|fail
    summary: 'Logic verified, X redundant tests found'
    checks:
      logical_correctness: pass|fail
      logic_issues_found: ['test X: sum(1,1) expects 3']
      redundancy_found: true|false
      removals_proposed: 5
      consolidations_proposed: 3
    fatals: ['critical logic errors']
    warnings: ['minor issues']
    recommendation: fix_logic|remove_redundancy|proceed
    ```
    <<<

#### Phase 4: Fix & Iterate Decision (You)

**What You Do**:

1. **Analyze all reports** from Phases 1-3
2. **Apply decision criteria**:
   - Are there logical errors in test expectations?
   - Are there failing tests that need fixes?
   - Was redundancy found that needs removal?
3. **Select next action**:
   - **ITERATE**: Issues found → Loop back to Phase 2
     - Fix logical errors first (highest priority)
     - Then handle redundancy removal
     - Continue until minimal set with correct logic
   - **COMPLETE**: All tests logical, minimal, and passing → Finish
4. **Use TodoWrite** to update task status:
   - Mark completed phases
   - Add iteration tasks if needed
5. **Continue iteration** until:
   - All test expectations are logically correct
   - No redundancy remains
   - No test can be removed without losing value

**Iteration Logic**:

```
WHILE (logic errors OR redundancy OR consolidation possible):
    IF logic errors found:
        Return to Phase 2 → Fix logical expectations
    IF redundancy found:
        Return to Phase 2 → Remove/consolidate tests
    IF further minimization possible:
        Return to Phase 2 → Apply consolidation
    Review again in Phase 3
END WHILE
```

### Workflow Completion

**Report the workflow output as specified:**

```yaml
workflow: create-test
status: completed
outputs:
  test_mode: coverage|tdd
  minimal_tests_created:
    - path: 'src/feature.spec.ts'
      tests_count: 3  # Absolute minimum needed
      test_type: 'actual|todo'
      coverage_added: '12%'  # for coverage mode
      behaviors_defined: 5   # for TDD mode
      redundancy_avoided: 7  # Tests NOT created
  coverage_report:  # Only for coverage mode
    initial_coverage: '75%'
    final_coverage: '95%'
    coverage_increase: '20%'
    uncovered_lines_before: 250
    uncovered_lines_after: 50
  tdd_scaffolding:  # Only for TDD mode
    interfaces_covered: ['IUserService', 'ICalculator']
    todo_tests_created: 5
    actual_tests_created: 3
    behaviors_defined: ['sum calculation', 'error handling']
  logic_validation:
    all_expectations_correct: true
    logic_errors_fixed: 0
    nonsensical_values_prevented: 3
  redundancy_analysis:
    tests_proposed_initially: 25
    tests_created_finally: 10
    tests_removed: 5
    tests_consolidated: 10
    efficiency_ratio: '2.5x'  # Value per test
  standards_compliance:
    minimal_principle: 'ENFORCED'
    zero_redundancy: 'ACHIEVED'
    logical_correctness: 'VERIFIED'
    maintenance_burden: 'MINIMIZED'
summary: |
  Mode: ${test_mode}
  Created MINIMUM viable test set: ${tests_created_finally} tests.
  ${coverage_mode ? `Coverage: ${coverage_increase}% gain` : `TDD: ${behaviors_defined} behaviors defined`}
  All test expectations logically verified (e.g., sum(1,1)=2).
  Eliminated ${tests_removed + tests_consolidated} redundant tests.
  Every test adds unique value with zero redundancy.
```

**Critical Success Validation:**

Before marking complete, validate:

- [ ] All test expectations are mathematically/logically correct
- [ ] No test can be removed without losing coverage/behavior definition
- [ ] No two tests cover the same code path
- [ ] All data variation tests consolidated to parameterized
- [ ] Coverage goals achieved OR TDD structure established
- [ ] Testing Standards minimal principle fully enforced

**Enforcement Note:**
This workflow FAILS if:
1. Even ONE redundant test is created
2. Any test has illogical expectations (e.g., sum(1,1)=3)
3. Coverage scripts aren't used when available (coverage mode)

Success is measured by achieving maximum value with MINIMUM tests and LOGICAL correctness.