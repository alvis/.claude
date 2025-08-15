# Update Test

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Update existing tests to conform to the latest testing standards, patterns, and best practices while preserving test coverage and intent.
**When to use**:

- Tests need refactoring for standards compliance
- Outdated testing patterns require modernization
- Duplicate fixtures need consolidation
- Type safety improvements are needed
**Prerequisites**:
- Existing test files to update
- Access to current testing standards documentation
- Understanding of project testing patterns and conventions
- Test runner and coverage tools configured

### Claude Role

You are a **Test Modernization Director** who orchestrates the test update workflow like a quality assurance director. You never execute refactorings directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break test updates into parallel refactoring tasks and assign to specialized testing subagents
- **Parallel Coordination**: Maximize efficiency by updating multiple test files simultaneously when dependencies allow
- **Quality Oversight**: Review refactoring results objectively without being involved in code changes
- **Decision Authority**: Make go/no-go decisions based on coverage reports and compliance verification results

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Test Files/Directory**: Path to specific test file(s) or directory containing tests to update

#### Optional Inputs

- **Testing Standards**: Path to testing standards document (default: `../../standards/quality/testing.md`)
- **TypeScript Standards**: Path to TypeScript standards document (default: `../../standards/code/typescript.md`)
- **Coverage Threshold**: Minimum coverage percentage to maintain (default: 100%)
- **Pattern Priority**: List of patterns to prioritize for migration
- **Batch Size**: Number of files to process in parallel (default: 10)

#### Expected Outputs

- **Updated Test Files**: Test files refactored to meet all testing standards
- **Compliance Report**: Detailed matrix showing standards compliance for each file
- **Coverage Report**: Before/after coverage metrics showing maintained or improved coverage
- **Migration Summary**: List of all pattern migrations completed with counts
- **Action Items**: List of any issues requiring manual review or follow-up

#### Data Flow Summary

The workflow takes existing test files, analyzes them against current testing standards, creates a migration plan, executes refactorings in parallel batches, verifies compliance and coverage, and produces updated tests with full compliance reports.

### Visual Overview

#### Main Workflow Flow

```plaintext
     Claude                    SUBAGENTS EXECUTE
     (Orchestrates Only)                 (Perform Tasks)
            |                                   |
            v                                   v
[START]
   |
   v
[Step 1: Analyze, Plan & Execute] ──────→ (Parallel Batch Updates + Mandatory Verification)
   |                                ├─ Refactoring Agent A: Batch 1 (≤10 files)                ─┐
   |                                ├─ Refactoring Agent B: Batch 2 (≤10 files)                ─┼─→ [Mandatory Verification]
   |                                └─ Refactoring Agent N: Batch N (remaining files)          ─┘      ↓
   |                                                                                                [Decision: Continue?]
   v
[Step 2: Fixture Optimization] ─────────→ (Parallel Batch Optimization)
   |                                ├─ Optimization Agent A: Batch 1 (≤10 fixtures/mocks)     ─┐
   |                                ├─ Optimization Agent B: Batch 2 (≤10 fixtures/mocks)     ─┼─→ [Decision: Continue?]
   |                                └─ Optimization Agent N: Batch N (remaining fixtures)      ─┘
   v
[Step 3: Final Review] ─────────────────→ (Direct Completion)
   |                                        └─ Claude Direct Review (No Subagents)
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: Claude plans & orchestrates (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel batches
• ARROWS (───→): Claude assigns work to multiple parallel subagents
• DECISIONS: Claude decides based on all batch reports
═══════════════════════════════════════════════════════════════════

Note: 
• Claude: Lists files, creates batches (max 10 per batch), assigns parallel tasks, makes decisions
• Multiple Agents per Step: Each handles one batch in parallel (≤10 files/fixtures)
• Step 3: Claude performs direct review without delegation
• Workflow is LINEAR: Step 1 → 2 → 3 with parallel execution within each step
```

#### Workflow State Machine

##### Main Workflow States

```
[INIT] ──> [STEP_1] ──> [STEP_2] ──> [STEP_3] ──> [COMPLETE]
              ↑  ↓         ↑  ↓         ↑  ↓
              └──┘         └──┘         └──┘
           (retry)      (retry)      (retry)
              ↓            ↓            ↓
          [FAILED]     [FAILED]     [FAILED]
```

##### Step Internal States (for EACH main step)

```
[PLANNING] ──> [EXECUTING] ──> [REPORTING] ──> [VERIFYING] ──> [DECIDING]
     ↑              ↓               ↓               ↓              ↓
     └──────────────┴───────────────┴───────────────┴──────────────┘
                            (retry/rollback paths)
```

### Dependencies & Patterns

#### Step Execution Pattern

```
     Claude                SUBAGENTS EXECUTE
(Orchestrates Only)         (Perform Tasks)
        |                          |
        v                          v

[Step N Phase 1: Plan] ─────────→ (Claude: batches work)
        |
        v
[Step N Phase 1: Assign] ───────→ (Claude: assigns to subagents)
        |                          |
        v                          v
[Step N Phase 2: Execute] ──────→ (Multiple Agents: parallel batch execution)
        |                   ├─ Refactoring Agent A: Batch 1 (≤10 resources)             ─┐
        |                   ├─ Refactoring Agent B: Batch 2 (≤10 resources)             ─┼─→ [Reports]
        |                   └─ Refactoring Agent N: Batch N (remaining resources)       ─┘
        v
[Step N Phase 3: Review] ───────→ (Claude: reviews reports)
        |
        v
[Step N Phase 4: Verify] ───────→ (Claude: mandatory verification for all batches)
        |                          |
        |                          v
        |                    (Verification Subagent: checks standards compliance recursively) → [Report]
        v
[Step N Phase 5: Decide] ───────→ (Claude: decides next action)
                                   |
                         ┌─────────┼─────────┐
                         │         │         │
                    Next Step  Retry Step  Rollback

Legend:
═══════════════════════════════════════════════════════════════════
• This happens INSIDE each main workflow step
• Phase 1: Claude plans and assigns
• Phase 2: Execution Subagents perform work
• Phase 3: Claude reviews results
• Phase 4: Verification Subagents check standards compliance (mandatory for Step 1)
• Phase 5: Claude makes decision
• Each phase completes before next phase begins
═══════════════════════════════════════════════════════════════════
```

## 3. AGENT ARCHITECTURE & COMMUNICATION

### Three Agent Types

#### 1. Claude

- **Role**: Test modernization orchestrator and decision maker
- **Responsibilities**:
  - Analyze test file structure and identify refactoring needs
  - Create batches of test files for parallel processing
  - Assign refactoring work to execution subagents
  - Review refactoring reports and coverage metrics
  - Deploy mandatory compliance verification for Step 1 ensuring recursive standards checking
  - Make workflow progression decisions (next/retry/rollback)
- **Restrictions**:
  - Cannot read test file contents directly
  - Cannot execute refactorings
  - Can only list files and batch resources

#### 2. Execution Agents

- **Role**: Multiple parallel agents per workflow step, each handling one batch
- **Types**:
  - **Refactoring Agents (Step 1)**: Multiple agents operating in parallel, each performs analysis, planning, and refactoring for their batch of test files (≤10 files per batch)
  - **Fixture Optimization Agents (Step 2)**: Multiple agents operating in parallel, each handles fixture optimization and consolidation for their batch (≤10 fixtures/mocks per batch)
- **Responsibilities**:
  - Read and follow Testing Standards document
  - Execute ALL assigned tasks for their batch (analysis + execution + verification)
  - Report comprehensive results for their batch (<1k tokens)
- **Output**: Batch-specific status, task summary, and completion report with verification

### Report Token Limits

- **Each Batch Execution Agent**: Max 1000 tokens per batch report
- **Claude**: Max 200 tokens per decision

## 4. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Step 1: Refactor Test Structure
2. Step 2: Optimize Test Performance & Fixtures  
3. Step 3: Completion Confirmation

### Step 1: Refactor Test Structure

**Step Configuration**:

- **Purpose**: Refactor existing tests to conform to current standards and best practices while preserving test coverage and intent
- **Input**: Test Files/Directory from workflow inputs
- **Output**: Refactored tests with compliance report and coverage verification
- **Sub-workflow**: None
- **Parallel Execution**: Yes - can process multiple files in parallel

#### Step 1 Phase 1: Planning (Claude)

**What Claude Does**:

1. **Receive test file list** from workflow inputs
2. **List all test files** using ls command (do NOT read contents)
3. **Identify Testing Standards** to apply: `../../standards/quality/testing.md`
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on test files found
   - Limit each batch to max 10 test files
   - Assign one Refactoring Agent per batch for parallel execution
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare batch assignments** with specific file lists for each Refactoring Agent
7. **Queue all batches** for parallel execution by multiple Refactoring Agents

**OUTPUT from Planning**: Multiple batch task assignments as todos, ready for parallel dispatch

#### Step 1 Phase 2: Execution (Multiple Refactoring Agents)

**What Claude Sends to Refactoring Agents**:

In a single message, Claude spins up multiple Refactoring Agents to perform batch refactoring in parallel, up to **10** batches at a time.

- **[IMPORTANT]** When there are any issues reported, Claude must stop dispatching further agents until all issues have been rectified
- **[IMPORTANT]** Claude MUST ask all agents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each Refactoring Agent to perform the following steps with full detail:

    >>>
    **In ultra think mode, adopt the Test Refactoring Expert mindset**

    - You're a **Test Refactoring Expert** with deep expertise in test modernization who follows these technical principles:
      - **Batch Focus**: Process your assigned batch of test files (≤10 files) thoroughly
      - **Standards Compliance**: Apply all testing standards consistently across your batch
      - **Coverage Preservation**: Maintain 100% test coverage throughout refactoring
      - **Intent Preservation**: Never change test behavior or intent
      - **Verification Integration**: Self-verify all changes before reporting

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    **[CRITICAL]** You MUST read the testing standard AND all its referenced standards recursively. When testing.md references A and B, you MUST also read and apply those standards. Missing recursive standard checks is a common failure point.

    - ../../standards/quality/testing.md (Read this FIRST and identify all referenced standards)
    - Any additional standards referenced within the above standards (read recursively)

    **Assignment**
    You're assigned to refactor the following test files in Batch [X]:

    - [test file 1 from batch X]
    - [test file 2 from batch X]
    - [... up to 10 files maximum]

    **Steps**

    1. **Analysis Phase**: Read each test file in your batch to understand current patterns and identify violations
    2. **Planning Phase**: Create refactoring strategy for your batch focusing on AAA patterns, type safety, documentation and naming conventions
    3. **Execution Phase**: Apply all refactorings to meet testing standards while preserving test intent
    4. **Verification Phase**: Run tests with coverage to ensure 100% threshold met and standards compliance achieved

    **Report**
    **[IMPORTANT]** You're requested to return the following batch results:

    - Modified test files list with specific changes made
    - Coverage metrics verification (must maintain 100%)
    - Standards compliance status for your batch
    - Any issues encountered during refactoring

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Batch [X]: Updated Y tests in Z files with verification complete'
    modifications: ['test/file1.spec.ts', 'test/file2.spec.ts', ...]
    outputs:
      batch_info:
        batch_number: X
        files_processed: Z
        total_tests_updated: Y
      analysis:
        violations_found:
          aaa_pattern: X
          type_safety: Y
          mock_patterns: Z
        total_violations: N
      execution:
        refactorings_applied:
          aaa_pattern: X tests
          type_safety: Y instances
          mock_patterns: Z instances
        tests_preserved: true|false
      verification:
        coverage:
          threshold_met: true|false
          lines: X%
          branches: Y%
          functions: Z%
        standards_compliance:
          overall: pass|fail
          aaa_pattern: pass|fail
          type_safety: pass|fail
          naming_convention: pass|fail
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Step 1 Phase 3: Review (Claude)

**What Claude Does**:

1. **Use TodoRead** to check current batch statuses
2. **Collect all execution reports** from parallel Refactoring Agents
3. **Parse report statuses** (success/failure/partial) for each batch
4. **Use TodoWrite** to update batch statuses:
   - Mark successful batches as 'completed'
   - Mark failed batches as 'failed'
   - Keep partial success as 'in_progress' for retry
5. **Identify any failed batches** and group them by failure type
6. **Determine verification needs** based on:
   - Critical test modifications
   - Coverage threshold failures
7. **Compile review summary** with:
   - Batches needing retry
   - Overall progress status

#### Step 1 Phase 4: Verification (Subagents) - Mandatory

**When Claude Triggers Verification**: Always performed for Step 1 to ensure all test files comply with standards and all recursively referenced standards

**What Claude Sends to Verification Subagents**:

In a single message, Claude spins up Verification Subagents to check quality for ALL batches, up to **10** verification tasks at a time.

- **[IMPORTANT]** Verification is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** Claude MUST ask verification subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track verification tasks separately from execution tasks

Request each Verification Subagent to perform the following verification with full scrutiny:

    >>>
    **In ultra think mode, adopt the Test Standards Verification Specialist mindset**

    - You're a **Test Standards Verification Specialist** with expertise in quality assurance who follows these principles:
      - **Comprehensive Compliance**: Verify ALL standards are met, not just the primary testing standard
      - **Recursive Standards Review**: When a standard references other standards, verify compliance with ALL referenced standards
      - **Critical Analysis**: Identify any deviation from standards requirements
      - **Zero Tolerance**: Any standards violation must be flagged as a failure

    **Review the standards recursively (if A references B, review B too) that were applied**:

    **[CRITICAL]** You MUST verify compliance with the testing standard AND all its recursively referenced standards. The testing standard references A & B - you MUST check compliance with ALL of these.

    - ../../standards/quality/testing.md - Verify compliance with this standard and identify all its referenced standards
    - Any additional standards referenced within the above standards (verify recursively)

    **Verification Assignment**
    You're assigned to verify the following test files that were modified in Batch [X]:

    - [test file 1]:
      - [Summary of what was refactored in this file]
    - [test file 2]:
      - [Summary of what was refactored in this file]
    - ...

    **Verification Steps**

    1. **Read ALL Referenced Standards**: Read testing.md and identify ALL recursively referenced standards
    2. **Verify Primary Standards**: Check each test file against ALL requirements in testing.md
    3. **Verify Referenced Standards**: Check each test file against ALL requirements in the referenced standards
    4. **Check Recursive References**: Verify any standards referenced by typescript.md or documentation.md are also met
    5. **Report Compliance**: Provide detailed pass/fail for each standard and sub-standard

    **Report**
    **[IMPORTANT]** You're requested to verify and report:

    - Testing standards compliance status (../../standards/quality/testing.md)
    - Any additional recursively referenced standards compliance
    - Complete verification matrix for the batch

    **[IMPORTANT]** You MUST return the following verification report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Batch [X]: Verified Y test files against testing standards and all recursive references'
    checks:
      testing_standard: pass|fail
      typescript_standard: pass|fail
      documentation_standard: pass|fail
      recursive_standards_complete: pass|fail
      batch_verification_complete: pass|fail
    standards_matrix:
      - file: 'test/file1.spec.ts'
        testing_std: pass|fail
        typescript_std: pass|fail
        documentation_std: pass|fail
      - file: 'test/file2.spec.ts'
        testing_std: pass|fail
        typescript_std: pass|fail
        documentation_std: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Any standards violations found
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Step 1 Phase 5: Decision (Claude)

**What Claude Does**:

1. **Analyze all batch reports** (execution + mandatory verification for Step 1)
2. **Apply decision criteria**:
   - Review any critical batch failures
   - Review mandatory verification results for standards compliance
   - Consider verification recommendations (always available for Step 1)
3. **Select next action**:
   - **PROCEED**: All batches success or acceptable partial success → Move to Step 2
   - **RETRY**: Partial success with retriable batch failures → Create new batches for failed items
   - **ROLLBACK**: Critical failures or verification failed → Revert changes
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' batches as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all batches as 'failed' and add rollback todos
5. **Prepare transition**: Package all successful batch outputs for Step 2

### Step 2: Optimize Test Performance & Fixtures

**Step Configuration**:

- **Purpose**: Optimize test performance and consolidate fixtures for better reusability and type safety
- **Input**: Refactored test files from Step 1
- **Output**: Consolidated fixtures with proper organization and type safety
- **Sub-workflow**: None
- **Parallel Execution**: Yes - can process multiple fixture groups in parallel

#### Step 2 Phase 1: Planning (Claude)

**What Claude Does**:

1. **Receive refactored files** from Step 1
2. **Scan for fixture patterns** using grep (do NOT read full contents)
3. **Identify fixture consolidation opportunities**:
   - Duplicate fixture definitions across files
   - Scattered mock objects
   - Missing factory functions
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on fixture/mock patterns found
   - Limit each batch to max 10 related fixtures/mocks
   - Assign one Optimization Agent per batch for parallel execution
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare batch assignments** with specific fixture/mock lists for each Optimization Agent
7. **Queue all batches** for parallel execution by multiple Optimization Agents

**OUTPUT from Planning**: Multiple fixture batch assignments as todos, ready for parallel dispatch

#### Step 2 Phase 2: Execution (Multiple Optimization Agents)

**What Claude Sends to Optimization Agents**:

In a single message, Claude spins up multiple Optimization Agents to perform batch optimization in parallel, up to **10** batches at a time.

- **[IMPORTANT]** When there are any issues reported, Claude must stop dispatching further agents until all issues have been rectified
- **[IMPORTANT]** Claude MUST ask all agents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each Optimization Agent to perform the following steps with full detail:

    >>>
    **In ultra think mode, adopt the Fixture Optimization Specialist mindset**

    - You're a **Fixture Optimization Specialist** with deep expertise in test data management who follows these technical principles:
      - **Batch Focus**: Process your assigned batch of fixtures/mocks (≤10 items) thoroughly
      - **DRY Principle**: Eliminate duplicate fixture definitions within your batch
      - **Type Safety**: Ensure all fixtures use satisfies operator
      - **Organization**: Follow Testing Standards structure exactly
      - **Verification Integration**: Self-verify all changes before reporting

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - ../../standards/quality/testing.md#factory-functions-for-test-doubles
    - ../../standards/quality/testing.md#test-double-organization

    **Assignment**
    You're assigned to optimize the following fixtures/mocks in Batch [X]:

    - [fixture/mock pattern 1 from batch X]
    - [fixture/mock pattern 2 from batch X]
    - [... up to 10 fixtures/mocks maximum]

    **Steps**

    1. **Analysis Phase**: Identify all fixture definitions in your batch and find duplicates or similar patterns
    2. **Planning Phase**: Create consolidation strategy for your batch focusing on DRY principles and type safety
    3. **Execution Phase**: Create centralized fixture files, implement factory functions, and apply satisfies operator
    4. **Verification Phase**: Run tests to verify fixtures work correctly and 100% coverage maintained

    **Report**
    **[IMPORTANT]** You're requested to return the following batch results:

    - Created fixture/mock files with specific consolidations made
    - Type safety improvements applied to your batch
    - Standards compliance status for your batch
    - Any issues encountered during optimization

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Batch [X]: Consolidated Y fixtures/mocks with Z duplicates removed'
    modifications: ['spec/fixtures/batch-X.fixture.ts', 'spec/mocks/batch-X.mock.ts', ...]
    outputs:
      batch_info:
        batch_number: X
        fixtures_processed: Y
        duplicates_removed: Z
      fixtures_created:
        - file: 'spec/fixtures/batch-X.fixture.ts'
          fixtures: ['createUser', 'createAdminUser']
        - file: 'spec/mocks/batch-X.mock.ts'  
          mocks: ['mockApiClient', 'mockResponse']
      type_safety_added: N instances
      verification:
        coverage:
          threshold_met: true|false
          tests_passing: true|false
        standards_compliance:
          factory_patterns: pass|fail
          type_safety: pass|fail
          organization: pass|fail
          no_duplicates: pass|fail
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Step 2 Phase 3: Review (Claude)

**What Claude Does**:

1. **Use TodoRead** to check current batch statuses
2. **Collect all execution reports** from parallel Optimization Agents
3. **Parse report statuses** (success/failure/partial) for each batch
4. **Use TodoWrite** to update batch statuses:
   - Mark successful batches as 'completed'
   - Mark failed batches as 'failed'
   - Keep partial success as 'in_progress' for retry
5. **Identify any failed batches** and group them by failure type
6. **Determine verification needs** based on:
   - Critical fixture consolidation failures
   - Test failures after optimization
7. **Compile review summary** with:
   - Batches needing retry
   - Overall optimization progress

#### Step 2 Phase 4: Verification (Subagents) - Optional

**When Claude Triggers Verification**: Critical failures in fixture optimization or tests broken after consolidation

**What Claude Sends to Verification Subagents**:

[Verification follows standard template if needed for critical fixture failures]

#### Step 2 Phase 5: Decision (Claude)

**What Claude Does**:

1. **Analyze all batch reports** (execution + verification if performed)
2. **Apply decision criteria**:
   - Review any critical batch failures
   - Consider verification recommendations
3. **Select next action**:
   - **PROCEED**: All batches success or acceptable partial success → Move to Step 3
   - **RETRY**: Partial success with retriable batch failures → Create new batches for failed items
   - **ROLLBACK**: Critical failures or verification failed → Revert changes
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' batches as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all batches as 'failed' and add rollback todos
5. **Prepare transition**: Package all successful batch outputs for Step 3

### Step 3: Completion Confirmation

**Step Configuration**:

- **Purpose**: Perform final confirmation of workflow completion with direct Claude review
- **Input**: All outputs from Steps 1-2
- **Output**: Final test update summary with workflow completion confirmation
- **Sub-workflow**: None
- **Parallel Execution**: No - Claude performs direct review

#### Step 3: Direct Completion Review (Claude)

1. **Use TodoRead** to review all task statuses from Steps 1-2
2. **Compile final summary** from all batch reports:
   - Step 1 refactoring batch results with mandatory standards verification (including recursive standards checking)
   - Step 2 fixture optimization batch results with integrated verification
   - Aggregate statistics from all successful batches
3. **Validate workflow completion**:
   - All batches from both steps completed successfully
   - All batch tasks marked 'completed'
   - Coverage maintained at 100% (verified by each batch agent)
   - Standards compliance achieved (verified by each batch agent)
4. **Create final workflow summary** aggregating:
   - Total files processed across all batches
   - Total fixtures/mocks consolidated across all batches
   - Overall compliance status
   - Performance improvements achieved
5. **Use TodoWrite** to mark workflow as 'completed'

**Completion Checklist**:

- [ ] Step 1: All test refactoring batches completed with mandatory standards verification (including recursive standards)
- [ ] Step 2: All fixture optimization batches completed with integrated verification  
- [ ] All batch outputs produced and validated by batch agents
- [ ] Coverage maintained at 100% (verified by each batch)
- [ ] Standards compliance achieved (verified by each batch)
- [ ] No pending retry or rollback batch items
- [ ] Workflow marked as completed
