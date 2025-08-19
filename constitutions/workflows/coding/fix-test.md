# Fix Test

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Fix issues found in test files including incorrect behavior, standards violations, and any other test-related problems while preserving test intent and correctness.
**When to use**:

- Test files have incorrect behavior or logic errors
- Tests violate coding standards and need compliance fixes
- Test files have type safety issues or poor patterns
- Tests need correction for proper mock usage or fixtures
- Focus on fixing correctness, not just making tests pass

**Prerequisites**:

- Existing test files to fix
- Access to current testing, TypeScript, and documentation standards
- Understanding of project testing patterns and conventions
- Test runner and coverage tools configured
- Knowledge that this workflow ONLY fixes test code, never source code

### Your Role

You are a **Test Correction Director** who orchestrates the test fixing workflow like a quality assurance director. You never execute fixes directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break test fixes into parallel correction tasks and assign to specialized testing subagents
- **Parallel Coordination**: Maximize efficiency by fixing multiple test files simultaneously when dependencies allow
- **Quality Oversight**: Review correction results objectively without being involved in code changes
- **Decision Authority**: Make go/no-go decisions based on correctness verification and compliance results

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Test Files/Directory**: Path to specific test file(s) or directory containing tests to fix

#### Optional Inputs

- **Test Specifier**: Either file name, directory path, or area of function (if not specified, consider all test files by default)
- **Changes**: Any specific changes the user wants to make to the test code

#### Expected Outputs

- **Fixed Test Files**: Test files corrected to fix issues and meet all applicable standards
- **Compliance Report**: Detailed matrix showing standards compliance for each file
- **Issue Resolution Report**: Before/after summary of issues fixed with verification status
- **Standards Application Summary**: List of all standards applied with discovery details
- **Action Items**: List of any issues requiring manual review or follow-up

#### Data Flow Summary

The workflow takes existing test files, analyzes them against testing, TypeScript, and documentation standards (plus any additional discovered standards), identifies issues and violations, creates a correction plan, executes fixes in parallel batches, verifies correctness and compliance, and produces corrected tests with full compliance reports.

### Visual Overview

#### Main Workflow Flow

```plaintext
   YOU                        SUBAGENTS EXECUTE
(Orchestrates Only)                 (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Fix Test Issues & Standards] ───────────→ (Subagents: execute test correction batches)
   |                                 ├─ Correction Agent A: Batch 1 (≤10 files)                ─┐
   |                                 ├─ Correction Agent B: Batch 2 (≤10 files)                ─┼─→ [Decision: Continue?]
   |                                 └─ Correction Agent N: Batch N (remaining files)          ─┘
   v
[Step 2: Optimize Test Structure] ─────────────→ (Subagents: execute fixture/mock correction batches)
   |                             ├─ Optimization Agent A: Batch 1 (≤10 fixtures/mocks)     ─┐
   |                             ├─ Optimization Agent B: Batch 2 (≤10 fixtures/mocks)     ─┼─→ [Decision: Continue?]
   |                             └─ Optimization Agent N: Batch N (remaining fixtures)      ─┘
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel batches
• ARROWS (───→): You assign work to multiple parallel subagents
• DECISIONS: You decide based on all batch reports
• CORRECTNESS FOCUS: Fix test behavior, never modify to make them pass
═══════════════════════════════════════════════════════════════════

Note: 
• You: Lists files, creates batches (max 10 per batch), assigns parallel tasks, makes decisions
• Multiple Agents per Step: Each handles one batch in parallel (≤10 files/fixtures)
• Workflow is LINEAR: Step 1 → 2 with parallel execution within each step
• CRITICAL: Only test files, mocks, and fixtures are modified - NEVER source code
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Fix Test Issues & Standards Compliance
2. Optimize Test Structure & Fixtures

### Step 1: Fix Test Issues & Standards Compliance

**Step Configuration**:

- **Purpose**: Fix issues in test files and ensure compliance with testing, TypeScript, and documentation standards plus any additional discovered standards while preserving test correctness
- **Input**: Test Files/Directory from workflow inputs, Test Specifier (optional), Changes (optional)
- **Output**: Corrected tests with compliance report and correctness verification
- **Sub-workflow**: None
- **Parallel Execution**: Yes - can process multiple files in parallel

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive test file list** from workflow inputs (use Test Specifier if provided)
2. **List all test files** using ls command (do NOT read contents)
3. **Determine the minimum required standards** to send to subagents to follow:
   - constitutions/standards/coding/testing.md (REQUIRED)
   - constitutions/standards/coding/typescript.md (REQUIRED)
   - constitutions/standards/coding/documentation.md (REQUIRED)
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on test files found
   - Limit each batch to max 10 test files
   - Assign one Correction Agent per batch for parallel execution
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare batch assignments** with specific file lists and Changes requirements for each Correction Agent
7. **Queue all batches** for parallel execution by multiple Correction Agents

**OUTPUT from Planning**: Multiple batch task assignments as todos, ready for parallel dispatch

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, You spin up multiple Correction Agents to perform batch correction, up to **10** batches at a time.

- **[IMPORTANT]** When there are any issues reported, You must stop dispatching further agents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all agents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each Correction Agent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Test Correction Expert mindset**

    - You're a **Test Correction Expert** with deep expertise in test fixing who follows these technical principles:
      - **Batch Focus**: Process your assigned batch of test files (≤10 files) thoroughly
      - **Standards Discovery**: Dynamically discover and apply all relevant standards beyond the minimum 3
      - **Correctness First**: Fix test behavior and logic, never modify tests just to make them pass
      - **Standards Compliance**: Apply all discovered standards consistently across your batch
      - **Test-Only Modification**: NEVER modify source code - only test files, mocks, and fixtures
      - **Issue Resolution**: Fix problems while preserving test intent and correctness

    **STEP 1: Dynamically discover all available standard files first**
    
    Before reading any assigned standards, use ls/find commands to list ALL available standard files in the constitutions/standards directory. Then determine which additional standards beyond the minimum 3 apply to test code.

    **Read the following MINIMUM REQUIRED standards** and follow them recursively (if A references B, read B too):

    - constitutions/standards/coding/testing.md
    - constitutions/standards/coding/typescript.md  
    - constitutions/standards/coding/documentation.md

    **Read any ADDITIONAL DISCOVERED standards** that apply to your test code batch:

    - [List additional standards you discovered that apply to test files]
    - [Include any standards referenced by the minimum 3 standards]

    **Assignment**
    You're assigned to fix issues in the following test files in Batch [X]:

    - [test file 1 from batch X]
    - [test file 2 from batch X]
    - [... up to 10 files maximum]

    **Specific changes requested**: [Include Changes input if provided, otherwise "General issue fixes"]

    **Steps**

    1. **Standards Discovery**: List all available standard files and identify which apply to test code
    2. **Analysis Phase**: Read each test file in your batch to understand current issues, violations, and incorrect behavior
    3. **Issue Identification**: Identify correctness issues, standards violations, and improvement opportunities
    4. **Correction Planning**: Create fixing strategy focusing on correctness, standards compliance, and proper test patterns
    5. **Execution Phase**: Apply all corrections to fix issues and meet all applicable standards while preserving test intent
    6. **Verification Phase**: Run tests to ensure fixes work correctly and verify standards compliance - DO NOT modify tests to make them pass

    **CRITICAL CONSTRAINTS**:
    - ONLY modify test files, mock files, and fixture files
    - NEVER modify source code under test
    - Focus on test correctness, not on making tests pass
    - If tests fail due to source code issues, report this but do not fix the source code

    **Report**
    **[IMPORTANT]** You're requested to return the following batch results:

    - Standards discovery results and which ones were applied
    - Modified test files list with specific issues fixed
    - Issue resolution summary with before/after status
    - Standards compliance verification for all applied standards
    - Any source code issues found that need developer attention

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Batch [X]: Fixed Y issues across Z test files with standards compliance verification'
    modifications: ['test/file1.spec.ts', 'test/file2.spec.ts', ...]
    outputs:
      batch_info:
        batch_number: X
        files_processed: Z
        total_issues_fixed: Y
      standards_discovery:
        standards_found: ['list', 'of', 'all', 'discovered', 'standards']
        standards_applied: ['list', 'of', 'applied', 'standards']
        minimum_required: ['testing.md', 'typescript.md', 'documentation.md']
        additional_applied: ['other', 'standards', 'applied']
      issue_resolution:
        correctness_issues_fixed: X
        standards_violations_fixed: Y  
        type_safety_issues_fixed: Z
        pattern_improvements: N
        total_fixes: M
      verification:
        tests_passing: true|false
        correctness_verified: true|false
        standards_compliance:
          overall: pass|fail
          testing_standard: pass|fail
          typescript_standard: pass|fail
          documentation_standard: pass|fail
          [additional_standards]: pass|fail
        source_code_issues_found: ['list', 'of', 'source', 'issues', 'requiring', 'developer', 'attention']
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

**When You Triggers Review**: Always performed for Step 1 to ensure all test files comply with all applied standards

**What You Send to Review Subagents**:

In a single message, You spin up Review Subagents to check quality for ALL batches, up to **10** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each Review Subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the Test Standards Review Specialist mindset**

    - You're a **Test Standards Review Specialist** with expertise in quality assurance who follows these principles:
      - **Comprehensive Compliance**: Verify ALL standards are met, including minimum required and additional discovered standards
      - **Recursive Standards Review**: When a standard references other standards, verify compliance with ALL referenced standards
      - **Critical Analysis**: Identify any deviation from standards requirements or remaining correctness issues
      - **Zero Tolerance**: Any standards violation or correctness issue must be flagged as a failure

    **Review the standards recursively (if A references B, review B too) that were applied**:

    - constitutions/standards/coding/testing.md - Verify compliance with this standard and all its referenced standards
    - constitutions/standards/coding/typescript.md - Verify compliance with this standard and all its referenced standards  
    - constitutions/standards/coding/documentation.md - Verify compliance with this standard and all its referenced standards
    - [Additional standards discovered and applied by execution agents]

    **Review Assignment**
    You're assigned to review the following test files that were modified in Batch [X]:

    - [test file 1]:
      - [Summary of what issues were fixed in this file]
    - [test file 2]:
      - [Summary of what issues were fixed in this file]
    - ...

    **Review Steps**

    1. **Read ALL Applied Standards**: Read all standards that were applied and identify ALL requirements including recursive references
    2. **Verify Minimum Standards**: Check each test file against ALL requirements in testing.md, typescript.md, documentation.md
    3. **Verify Additional Standards**: Check each test file against ALL requirements in additional standards discovered
    4. **Check Recursive References**: Verify any standards referenced by applied standards are also met
    5. **Verify Correctness**: Ensure test logic and behavior is correct and appropriate
    6. **Report Compliance**: Provide detailed pass/fail for each standard and correctness verification

    **Report**
    **[IMPORTANT]** You're requested to verify and report:

    - All applied standards compliance status (minimum + additional discovered)
    - Test correctness and logic verification
    - Complete verification matrix for the batch

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Batch [X]: Verified Y test files against all applied standards and correctness requirements'
    checks:
      testing_standard: pass|fail
      typescript_standard: pass|fail
      documentation_standard: pass|fail
      additional_standards_complete: pass|fail
      correctness_verification: pass|fail
      batch_verification_complete: pass|fail
    standards_matrix:
      - file: 'test/file1.spec.ts'
        testing_std: pass|fail
        typescript_std: pass|fail
        documentation_std: pass|fail
        additional_std: pass|fail
        correctness: pass|fail
      - file: 'test/file2.spec.ts'
        testing_std: pass|fail
        typescript_std: pass|fail
        documentation_std: pass|fail
        additional_std: pass|fail
        correctness: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Any standards violations or correctness issues found
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all batch reports** (execution + mandatory verification for Step 1)
2. **Apply decision criteria**:
   - Review any critical batch failures
   - Review mandatory verification results for standards compliance and correctness
   - Consider verification recommendations
3. **Select next action**:
   - **PROCEED**: All batches success or acceptable partial success → Move to Step 2
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical failures → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||

In phase 4, you(the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' batches as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all batches as 'failed' and add rollback todos
5. **Prepare transition**: Package all successful batch outputs for Step 2

### Step 2: Optimize Test Structure & Fixtures

**Step Configuration**:

- **Purpose**: Fix issues in test fixtures and mocks, ensuring proper structure and organization while maintaining correctness
- **Input**: Fixed test files from Step 1
- **Output**: Corrected and optimized fixtures/mocks with proper organization and type safety
- **Sub-workflow**: None
- **Parallel Execution**: Yes - can process multiple fixture groups in parallel

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive fixed files** from Step 1
2. **Scan for fixture/mock issues** using grep (do NOT read full contents)
3. **Identify fixture/mock correction opportunities**:
   - Incorrect fixture definitions or mock behavior
   - Type safety issues in fixtures/mocks
   - Organizational problems
   - Standards violations in test support files
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on fixture/mock patterns found
   - Limit each batch to max 10 related fixtures/mocks
   - Assign one Optimization Agent per batch for parallel execution
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare batch assignments** with specific fixture/mock lists for each Optimization Agent
7. **Queue all batches** for parallel execution by multiple Optimization Agents

**OUTPUT from Planning**: Multiple fixture batch assignments as todos, ready for parallel dispatch

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, You spin up multiple Optimization Agents to perform batch optimization in parallel, up to **10** batches at a time.

- **[IMPORTANT]** When there are any issues reported, You must stop dispatching further agents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all agents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each Optimization Agent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Fixture Correction Specialist mindset**

    - You're a **Fixture Correction Specialist** with deep expertise in test data management who follows these technical principles:
      - **Batch Focus**: Process your assigned batch of fixtures/mocks (≤10 items) thoroughly
      - **Correctness First**: Fix fixture/mock behavior and accuracy, ensure they represent realistic data
      - **Standards Compliance**: Apply all applicable testing standards to fixture/mock organization
      - **Test-Only Modification**: Only modify test support files - NEVER modify source code
      - **Verification Integration**: Self-verify all changes before reporting

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - constitutions/standards/coding/general-principles.md
    - constitutions/standards/coding/typescript.md
    - constitutions/standards/coding/functions.md
    - constitutions/standards/coding/documentation.md
    - constitutions/standards/coding/testing.md

    **Assignment**
    You're assigned to fix issues in the following fixtures/mocks in Batch [X]:

    - [fixture/mock pattern 1 from batch X]
    - [fixture/mock pattern 2 from batch X]
    - [... up to 10 fixtures/mocks maximum]

    **Steps**

    1. **Analysis Phase**: Identify all fixture/mock issues in your batch including correctness, type safety, and organizational problems
    2. **Issue Identification**: Find incorrect behavior, standards violations, and improvement opportunities
    3. **Correction Planning**: Create fixing strategy focusing on accuracy, standards compliance, and proper organization
    4. **Execution Phase**: Apply all corrections to fix issues while ensuring fixtures/mocks represent accurate test data
    5. **Verification Phase**: Run tests to verify fixtures work correctly and maintain test accuracy

    **CRITICAL CONSTRAINTS**:
    - ONLY modify test fixtures, mock files, and test support files
    - NEVER modify source code under test
    - Focus on fixture/mock correctness and accuracy
    - Ensure fixtures represent realistic and valid test data

    **Report**
    **[IMPORTANT]** You're requested to return the following batch results:

    - Created/modified fixture/mock files with specific issues fixed
    - Correctness improvements applied to your batch
    - Standards compliance status for your batch
    - Any issues encountered during optimization

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Batch [X]: Fixed Y fixture/mock issues with Z improvements applied'
    modifications: ['spec/fixtures/batch-X.fixture.ts', 'spec/mocks/batch-X.mock.ts', ...]
    outputs:
      batch_info:
        batch_number: X
        fixtures_processed: Y
        issues_fixed: Z
      corrections_applied:
        correctness_fixes: N
        type_safety_fixes: M
        organization_fixes: L
        standards_compliance_fixes: K
      fixtures_created:
        - file: 'spec/fixtures/batch-X.fixture.ts'
          fixtures: ['createUser', 'createAdminUser']
        - file: 'spec/mocks/batch-X.mock.ts'  
          mocks: ['mockApiClient', 'mockResponse']
      verification:
        tests_passing: true|false
        fixtures_accurate: true|false
        standards_compliance:
          testing_standard: pass|fail
          typescript_standard: pass|fail
          documentation_standard: pass|fail
          organization: pass|fail
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Decision (You)

**What You Do**:

1. **Analyze all batch reports** from execution phase
2. **Apply decision criteria**:
   - Review any critical batch failures
   - Consider verification recommendations
3. **Select next action**:
   - **PROCEED**: All batches success or acceptable partial success → Complete workflow
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical failures → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||

In phase 4, you(the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' batches as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all batches as 'failed' and add rollback todos
5. **Prepare completion**: Package all successful batch outputs for final confirmation

### Final Step: Completion Confirmation

**Step Configuration**:

- **Purpose**: Confirm successful workflow completion and package final outputs
- **Input**: All outputs from Steps 1-2: fixed tests and corrected fixtures
- **Output**: Final deliverables matching workflow Expected Outputs specification
- **Sub-workflow**: None
- **Parallel Execution**: No

**Completion Checklist**:

- [ ] Step 1: All test correction batches completed with mandatory standards verification
- [ ] Step 2: All fixture/mock correction batches completed
- [ ] All batch outputs produced and validated by batch agents
- [ ] Test correctness verified (focus on fixing behavior, not making tests pass)
- [ ] Standards compliance achieved for all discovered and applied standards
- [ ] No pending retry or rollback batch items
- [ ] All modifications limited to test files, mocks, and fixtures only

### Workflow Completion

**Report the workflow output as specified:**

```yaml
workflow: fix-test
status: completed
outputs:
  fixed_test_files:
    - file: 'test/services/auth.spec.ts'
      issues_fixed: 5
      standards_violations_resolved: 3
    - file: 'test/components/Button.spec.ts'
      issues_fixed: 2
      standards_violations_resolved: 1
  compliance_report:
    testing_standards: pass
    typescript_standards: pass
    documentation_standards: pass
    additional_standards_applied:
      - 'constitutions/standards/coding/functions.md'
      - 'constitutions/standards/coding/general-principles.md'
    compliance_matrix:
      - file: 'test/services/auth.spec.ts'
        testing: pass
        typescript: pass
        documentation: pass
      - file: 'test/components/Button.spec.ts'
        testing: pass
        typescript: pass
        documentation: pass
  issue_resolution_report:
    total_issues_found: 12
    issues_resolved: 12
    correctness_fixes: 7
    standards_fixes: 5
    before_state:
      - 'Tests using any type without satisfies operator'
      - 'Missing AAA pattern structure'
      - 'Incorrect mock behavior'
    after_state:
      - 'All fixtures use satisfies operator for type safety'
      - 'AAA pattern consistently applied'
      - 'Mocks accurately represent real behavior'
  standards_application_summary:
    discovered_standards: 8
    applied_standards: 5
    minimum_required: ['testing.md', 'typescript.md', 'documentation.md']
    additionally_applied: ['functions.md', 'general-principles.md']
  action_items:
    - 'Source code issue in auth.service.ts line 45 needs developer attention'
    - 'Consider refactoring database mock for better reusability'
summary: |
  Successfully fixed [N] test files across [M] batches, resolving [X] issues total.
  Applied [Y] standards (3 required + [Z] discovered). All tests now comply with
  Testing Standards, TypeScript Standards, and Documentation Standards. Focused on
  correctness over making tests pass. Identified [A] source code issues requiring
  developer attention. All modifications limited to test code only.
```

**Finalization Instructions:**

1. **Run Test Suite**: Execute all fixed tests to verify correctness improvements
2. **Verify Correctness**: Ensure tests are testing the right behavior, not just passing
3. **Review Source Issues**: Address any source code issues identified during test fixes
4. **Update Test Documentation**: Document any new patterns or conventions established
5. **Share Standards Applied**: Communicate which additional standards were discovered and applied

**Important Notes:**
- Test fixes focused on correctness, not on making tests pass artificially
- Any failing tests due to source code issues have been reported but not "fixed"
- All standards violations have been resolved across the test suite
- Fixture and mock improvements enhance test maintainability and accuracy
