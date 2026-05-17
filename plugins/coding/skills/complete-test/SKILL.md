---
name: complete-test
description: 'Write comprehensive test suites reaching 100% coverage with minimal redundancy. Triggers when: "write tests for this", "add unit tests", "write test cases", "increase test coverage", "test this function". Also use when: filling coverage gaps, optimizing an existing test suite, adding tests before refactor. Examples: "write tests for src/parser.ts", "get this file to 100% coverage", "add unit tests for the auth module".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep
---

# Complete Test

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Achieve 100% test coverage for source code using progressive test writing with coverage verification, redundant test removal, test issue fixing, fixture restructuring, and final verification.

**When to use**:

- Creating comprehensive test suites for existing source code
- Achieving 100% test coverage with minimal redundant tests
- Optimizing existing test suites for efficiency and maintainability
- Following test-driven development for new features with coverage verification

**Prerequisites**:

- Source code files to test are implemented
- Testing framework configured (Vitest)
- Coverage tooling enabled (v8 provider)
- Testing, TypeScript, and Documentation standards available
- Package manager scripts configured (`npm run test`, `npm run coverage`)

### Your Role

You are a **Test Suite Orchestrator** who coordinates the complete test development lifecycle like a quality-focused testing director ensuring comprehensive coverage, minimal redundancy, and optimal test structure, never executing testing tasks directly but delegating and coordinating. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. That principle is exactly why redundancy elimination and fixture optimization sit at the core of this workflow: new specs must extend the existing `describe`/`it` shape and reuse current fixtures, never accrete a second parallel suite or a "tests-v2" file beside the original. Your management style emphasizes:

- **Strategic Delegation**: Break test creation into batched parallel tasks with single subagents handling 2-5 source files
- **Progressive Verification**: Each test must prove its value through immediate coverage verification
- **Parallel Coordination**: Maximize efficiency through parallel batch execution
- **Quality Oversight**: Ensure adherence to testing standards and coverage requirements
- **Redundancy Elimination**: Use Plan subagent to identify and remove unnecessary tests
- **Fixture Optimization**: Consolidate and restructure test doubles using Plan subagent recommendations

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Source Files**: List of source code files that need test coverage
- **Target Coverage**: Coverage percentage goal (default: 100%)

#### Optional Inputs

- **Existing Tests**: Path to existing test files (default: discover automatically using Glob)
- **Batch Size**: Number of source files per batch (default: 2-5, max 500 lines total)
- **Standards Paths**: Paths to testing/meta.md, testing/write.md, testing/scan.md, typescript.md, documentation.md (default: standard plugin paths)
- **Max Parallel Batches**: Maximum concurrent subagents (default: 8)

#### Expected Outputs

- **Test Files**: Complete test suite with 100% coverage for all source files
- **Coverage Report**: Final coverage metrics (line, branch, statement, function all at 100%)
- **Redundancy Report**: List of redundant tests removed with reasons
- **Fixture Structure**: Consolidated and organized fixtures/mocks
- **Compliance Report**: Standards compliance verification
- **Efficiency Metrics**: Tests per source file, coverage per test ratio, test suite execution time

#### Data Flow Summary

The workflow takes source files and creates comprehensive test coverage through six steps: (1) initial coverage analysis, (2) progressive test writing in batches with coverage verification per test, (3) redundant test removal using Plan subagent, (4) test issue fixing and standards compliance, (5) fixture restructuring using Plan subagent, (6) final verification via subtask.

### Visual Overview

#### Main Workflow Flow

```plaintext
  YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Initial Coverage Analysis] ──→ (Single subagent: baseline coverage)
   |                                    │ • Run coverage on existing tests
   |                                    │ • Identify uncovered files/lines
   |                                    └─ Report baseline metrics
   v
[Step 2: Progressive Test Writing] ───→ (Batch execution: 2-5 files per batch)
   |                                    │ • Create batches (max 500 lines)
   |               ├─ Batch 1: Subagent (files 1-3)                    ─┐
   |               ├─ Batch 2: Subagent (files 4-6)                    ─┤
   |               ├─ Batch 3: Subagent (files 7-9)                    ─┼→ [Parallel Execution]
   |               └─ Batch N: Subagent (files X-Y)                    ─┘
   |                                    │ Each subagent:
   |                                    │ • Write test → verify coverage
   |                                    │ • Keep if improves, delete if not
   |                                    │ • Repeat until 100% for batch
   |                                    └─ Report: tests created, coverage
   v
[Step 3: Remove Redundant Tests] ─────→ (Plan + Execute pattern)
   |                                    │ Phase 1: Plan subagent
   |                                    │ • Analyze all tests
   |                                    │ • Identify potential redundancy
   |                                    │ • Create removal strategy
   |                                    │
   |                                    │ Phase 2: Parallel execution
   |               ├─ Task 1: Subagent (test group 1)                  ─┐
   |               ├─ Task 2: Subagent (test group 2)                  ─┤
   |               └─ Task N: Subagent (test group N)                  ─┘
   |                                    │ Each subagent:
   |                                    │ • Try remove test
   |                                    │ • Verify coverage maintained
   |                                    │ • If drop → keep, else → remove
   |                                    └─ Report: tests removed
   v
[Step 4: Fix Test Issues] ────────────→ (Batch execution if >25 files)
   |                                    │ • Fix standards violations
   |                                    │ • Correct test logic
   |                                    │ • Ensure all pass
   |                                    └─ Report: issues fixed
   v
[Step 5: Restructure Fixtures] ───────→ (Plan + Execute pattern)
   |                                    │ Phase 1: Plan subagent
   |                                    │ • Analyze fixtures/mocks
   |                                    │ • Identify consolidation opportunities
   |                                    │ • Create restructuring plan
   |                                    │
   |                                    │ Phase 2: Execute plan
   |                                    │ • Apply restructuring
   |                                    │ • Consolidate duplicates
   |                                    │ • Clean unused files
   |                                    └─ Report: structure improved
   v
[Step 6: Final Verification] ─────────→ (Single subtask)
   |                                    │ • Verify 100% coverage
   |                                    │ • All tests passing
   |                                    │ • Standards compliance
   |                                    │ • Efficiency metrics
   |                                    └─ Report: final validation
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks
• ARROWS (───→): You assign work to subagents
• BATCHES: Step 2 uses dynamic batching (2-5 files, 500 lines max)
• PLAN PATTERN: Steps 3 & 5 use Plan subagent then execute
• PARALLEL: Multiple batches/tasks run simultaneously
═══════════════════════════════════════════════════════════════════

Note:
• Step 1: Single subagent for baseline
• Step 2: CORE - batched progressive test writing (2-5 files per batch)
• Step 3: Plan subagent + parallel removal execution
• Step 4: Batched fixing (if >25 files)
• Step 5: Plan subagent + execution
• Step 6: Subtask delegation for final checks
```

## 3. WORKFLOW IMPLEMENTATION

### Step 1: Subagent Orchestration

You are the orchestrator. Drive the workflow end-to-end via fire-and-forget `Task` subagents with TodoWrite-based status tracking. The workflow has six sub-steps. Dispatch a maximum of **8 parallel `Task` subagents** at any time. After each sub-step, aggregate the returned reports before moving on.

#### Sub-Step 1.1: Initial Coverage Analysis

**Purpose**: Establish baseline coverage and identify all uncovered source code.
**Parallelism**: Single subagent (no parallelism).

**Planning (You)**:

1. Receive the source files list from workflow inputs.
2. Discover existing test files using the Glob tool (do NOT use `find` in bash). Patterns: `**/*.spec.{ts,tsx}` or `**/*.test.{ts,tsx}`.
3. Determine the standards to send: `testing/meta.md` + `testing/write.md`, `typescript/write.md`.
4. Use TodoWrite to create a single todo for the coverage analysis (status: `pending`).
5. Update the todo to `in_progress` when dispatched.

**Dispatch (Task tool, single subagent)**:

Request the subagent to perform the following with full detail:

    >>>
    **ultrathink: adopt the Coverage Analysis Expert mindset**

    - You're a **Coverage Analysis Expert** with deep expertise in test coverage measurement who follows these technical principles:
      - **Comprehensive Analysis**: Identify every uncovered line, branch, and statement
      - **Baseline Establishment**: Create accurate baseline metrics for tracking progress
      - **Tool Proficiency**: Execute coverage tools correctly and parse output accurately
      - **Detailed Reporting**: Provide file-by-file coverage breakdown

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - testing/meta.md + testing/write.md
    - typescript.md

    **Assignment**
    You're assigned to analyze baseline test coverage for the provided source files.

    **Steps**

    1. **Discover test configuration**:
       - Locate vitest.config.ts or equivalent
       - Verify coverage provider is configured (v8)
       - Check for excluded patterns
    2. **Run existing tests** (if any exist):
       - Execute `npm run test` or equivalent
       - Note any failing tests
    3. **Generate coverage report**:
       - Execute `npm run coverage` or `vitest --coverage`
       - Parse coverage output (JSON and HTML reports)
       - Extract line, branch, statement, function coverage
    4. **Identify uncovered code**:
       - List all uncovered files (0% coverage)
       - For partially covered files: list uncovered line ranges, list uncovered branches, note functions without coverage
    5. **Create baseline metrics**:
       - Total lines: covered vs uncovered
       - Total branches: covered vs uncovered
       - Total functions: covered vs uncovered
       - File-by-file coverage percentage

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Baseline coverage analysis complete'
    modifications: []
    outputs:
      baseline_coverage:
        overall:
          lines: 'X%'
          branches: 'Y%'
          statements: 'Z%'
          functions: 'W%'
        per_file:
          - file: 'src/auth/service.ts'
            lines: 'X%'
            uncovered_lines: [45-52, 89, 123-145]
            uncovered_branches: [67, 89]
        uncovered_files: ['src/users/controller.ts', ...]
        partially_covered_files: ['src/auth/service.ts', ...]
      existing_tests:
        test_file_count: N
        failing_tests: M
    issues: ['issue1', ...]
    ```
    <<<

**Decision (You)**: Verify the baseline metrics are present and accurate. Mark the todo `completed`. Use the report to plan batching for Sub-Step 1.2.

#### Sub-Step 1.2: Progressive Test Writing with Coverage Verification

**Purpose**: Write tests progressively for batches of source files, verifying coverage after each test, keeping only tests that improve coverage until 100% achieved per batch.
**Parallelism**: Yes — multiple batches run in parallel, **max 8 concurrent**.

**KEY INNOVATION**: Each subagent owns 2-5 source files (max 500 lines total) and writes tests one at a time, verifying coverage after each test, deleting tests that don't improve coverage.

**Planning (You)**:

1. List all source files needing coverage (0% or <100%) from Sub-Step 1.1.
2. Read source files via the Read tool to determine line counts.
3. Create dynamic batches:
   - Batch size: 2-5 source files per batch.
   - Line limit: max 500 source lines per batch.
   - Algorithm: start with the first uncovered file, add files until 5 files OR 500 lines is reached, create the batch, move to the next set, repeat until all files are assigned.
4. Standards to send to all subagents: `testing/meta.md` + `testing/write.md` (REQUIRED), `typescript/write.md` (REQUIRED), `documentation/write.md` (REQUIRED).
5. Use TodoWrite to create one todo per batch (`pending`).
6. Queue all batches for parallel execution, dispatching at most 8 at a time. Update each todo to `in_progress` on dispatch.

**Batching example**:

```plaintext
Source files:
  - auth/service.ts (120 lines)
  - auth/controller.ts (180 lines)
  - users/service.ts (150 lines)
  - users/controller.ts (200 lines)
  - posts/service.ts (100 lines)
  - posts/controller.ts (300 lines)

Batches created:
  Batch 1: auth/service.ts, auth/controller.ts, users/service.ts (450 lines, 3 files)
  Batch 2: users/controller.ts, posts/service.ts (300 lines, 2 files)
  Batch 3: posts/controller.ts (300 lines, 1 file)
```

**Dispatch (Task tool, parallel batches)**:

In a single message, spin up Test Writing Agents — at most 8 concurrent. Each subagent owns its ENTIRE batch.

    >>>
    **ultrathink: adopt the Progressive Test Writing Expert mindset**

    - You're a **Progressive Test Writing Expert** with deep expertise in coverage-driven test development who follows these technical principles:
      - **Batch Ownership**: You own this entire batch - write tests for ALL assigned source files until ALL reach 100% coverage
      - **Progressive Writing**: Write ONE test at a time, verify coverage, decide keep/delete
      - **Coverage Verification**: Run coverage after EVERY single test to verify improvement
      - **Minimal Testing**: Delete any test that doesn't add measurable coverage
      - **Standards Compliance**: Follow testing/write.md, typescript.md, documentation.md throughout
      - **Complete Coverage**: Continue until ALL files in your batch reach 100% coverage

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
      You are responsible for achieving 100% coverage for ALL source files in your batch.
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - testing/meta.md + testing/write.md (Coverage-Driven Test Development Workflow section is CRITICAL)
    - typescript/write.md
    - documentation/write.md

    **Assignment**
    You're assigned Batch [X] with the following source files (total: [N] lines):

    - [source file 1 - L lines]
    - [source file 2 - M lines]
    - [... 2-5 files maximum, max 500 lines total]

    **Your Goal**: Achieve 100% coverage for ALL files in this batch using progressive test writing.

    **Steps - CRITICAL WORKFLOW**

    **FOR EACH source file in your batch, repeat this entire workflow:**

    1. **Initial Coverage Check**:
       - Run: `vitest --coverage spec/path/to/file.spec.ts`
       - Note current coverage and first uncovered line/branch.

    2. **Progressive Test Writing Loop** (repeat until 100% coverage):
       a. Write ONE test targeting a specific uncovered line/branch (AAA pattern, proper TS types, follow standards).
       b. Run coverage verification: `vitest --coverage spec/path/to/file.spec.ts`. Parse new coverage.
       c. Decision:
          - If coverage increased (even by 1 line): KEEP the test, continue to next uncovered line/branch.
          - If coverage stayed the same: DELETE the test immediately, log "Test provided no coverage value", write a different test.
       d. If 100% reached → next file in batch; else → repeat 2a.

    3. **Batch Completion Verification**: run coverage for ALL test files together; verify every source file in the batch is at 100%; count total tests created vs deleted; calculate coverage efficiency.

    4. **Standards Compliance Check**: `npm run lint` on all created test files; verify testing/write.md compliance; fix TypeScript errors; ensure documentation.

    **CRITICAL REMINDERS**:
    - Write tests one at a time with immediate coverage verification.
    - Delete any test that doesn't improve coverage.
    - Continue until ALL files in your batch reach 100%.
    - Follow testing/write.md (especially Zero Redundancy Rule).

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Batch [X]: Achieved 100% coverage for [N] files with [M] tests'
    modifications: ['spec/auth/service.spec.ts', ...]
    outputs:
      batch_info:
        batch_number: X
        source_files_count: N
        total_source_lines: M
      coverage_per_file:
        - file: 'src/auth/service.ts'
          test_file: 'spec/auth/service.spec.ts'
          coverage: { lines: '100%', branches: '100%', statements: '100%', functions: '100%' }
          tests_created: 25
          tests_kept: 18
          tests_deleted: 7
      batch_summary:
        total_tests_created: 55
        total_tests_kept: 40
        total_tests_deleted: 15
        coverage_efficiency: '2.5% per test'
      standards_compliance:
        testing_standard: pass|fail
        typescript_standard: pass|fail
        documentation_standard: pass|fail
      verification:
        all_files_100_percent: true|false
        all_tests_passing: true|false
        lint_check: pass|fail
    issues: ['issue1', ...]
    ```
    <<<

**Decision (You)**: Aggregate all batch reports. Verify every batch reports 100% coverage. If any batch is partial/failed, create new retry batches for the incomplete files (still capped at 8 concurrent) and dispatch again. Mark completed batches in TodoWrite. Aggregate totals: tests created, kept vs deleted, overall coverage efficiency, files at 100%.

#### Sub-Step 1.3: Remove Redundant Tests

**Purpose**: Identify and remove redundant tests that don't add unique coverage value while maintaining 100% coverage.
**Parallelism**: Phase 2 uses parallel removal — **max 8 concurrent**.

**CRITICAL RULE — Source File Scoped Coverage**:

- Each test file mirrors exactly one source file (e.g., `src/auth/service.ts` → `spec/auth/service.spec.ts`).
- Coverage is verified per-source-file: `npm run coverage -- <spec/path/to/file.spec.ts>`.
- A test is redundant ONLY IF it does NOT contribute to its mirrored source file's coverage.
- Tests that contribute to the mirrored source file's coverage MUST be kept, even if globally redundant.
- Goal: 100% coverage per mirrored source file, not just overall.

**Phase A — Plan with a Plan Subagent**:

Use TodoWrite to create a planning todo. Dispatch a Plan subagent via the Task tool with `subagent_type="Plan"`:

    >>>
    **ultrathink: adopt the Test Redundancy Analyst mindset**

    - You're a **Test Redundancy Analyst** who follows:
      - **Coverage Analysis**: Understand which tests cover which code paths
      - **Redundancy Detection**: Identify tests that duplicate coverage without adding value
      - **Behavioral Distinctness**: Tests covering the same lines may verify different behavioral aspects and must be kept separate
      - **Strategic Planning**: Removal strategy preserves 100% coverage
      - **Risk Assessment**: Flag tests that appear redundant but may be essential

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read** testing/meta.md + testing/scan.md (Zero Redundancy Rule and Minimal Testing Principle).

    **Assignment**: analyze all test files and identify potential redundant tests.

    **Analysis Steps**:

    1. Read all test files created in Sub-Step 1.2.
    2. For each test, determine: lines covered, branches exercised, unique behavior verified.
    3. Identify redundancy patterns (coverage scoped to mirrored source file and feature):
       - Same logic, different data values, that don't add coverage AND don't verify distinct behaviors.
       - Same lines AND same behavioral aspect as other tests.
       - Artificial scenarios that don't contribute to source file coverage or behavioral documentation.
       - Wrapper-function tests that don't add unique coverage or behavioral insight.
       - NOTE: A test is NOT redundant if it contributes to its mirrored source file even if it overlaps with tests for other source files.
       - CRITICAL: Tests that verify different behavioral aspects must be kept separate even if they cover the same code paths.
    4. Create removal candidates list — group tests by file, mark each as `safe_to_remove` | `uncertain` | `keep`, provide removal strategy.
    5. Create removal tasks — group candidates into tasks (max 10 tests per task), specify removal order (least risky first).

    **Report**: tests analyzed, redundancy candidates grouped by file, removal tasks with specific test names, risk assessment, coverage preservation likelihood. Provide a comprehensive plan the orchestrator can dispatch in parallel.
    <<<

Receive the plan, parse removal tasks, create a todo per task in TodoWrite.

**Phase B — Parallel Removal Execution**:

Dispatch Test Removal Agents in a single message — at most 8 concurrent. Each subagent attempts to remove specific tests and verifies coverage; if coverage drops, it restores the test.

    >>>
    **ultrathink: adopt the Surgical Test Removal Expert mindset**

    - You're a **Surgical Test Removal Expert** who follows:
      - **Coverage Preservation**: 100% coverage must be maintained
      - **Careful Removal**: Remove one test at a time, verify immediately
      - **Rollback Ready**: Restore test if coverage drops
      - **Verification Focus**: Coverage reports guide all decisions

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Assignment**
    Removal Task [X] — attempt to remove the following tests:
    - Test: '[name]' at line [N] in [test file] — Reason: [...] — Risk: [low|medium]
    - [... up to 10 tests per task]

    **FOR EACH test in your assignment**:

    1. Pre-removal coverage check (SCOPED TO MIRRORED SOURCE FILE):
       - Run: `npm run coverage -- spec/path/to/file.spec.ts`
       - Note current coverage for the mirrored source file (must be 100%).
    2. Remove the single test (delete or comment out the block, save).
    3. Post-removal coverage verification (mirrored source file): re-run coverage and compare.
    4. Decision:
       - If mirrored source coverage maintained at 100%: KEEP REMOVED, continue.
       - If mirrored source coverage dropped (even 1%): RESTORE test immediately, mark `essential`.
       - Tests that seem globally redundant but contribute to their mirrored source file MUST be kept.
       - Before removing, verify the test does NOT document a unique behavioral aspect (different semantic concept, different invariant, important edge case). If YES → `essential` and keep.
    5. Move to the next test.

    **Report (<1000 tokens)**:

    ```yaml
    status: success|failure|partial
    summary: 'Removal Task [X]: Removed [N] redundant tests, restored [M] essential tests'
    modifications: ['spec/auth/service.spec.ts', ...]
    outputs:
      task_info: { task_id: X, tests_attempted: 10, tests_removed: 7, tests_restored: 3 }
      removal_details:
        - test_name: 'should calculate tax for $100'
          mirrored_source_file: 'src/billing/tax.ts'
          action: 'removed'
          source_coverage_before: '100%'
          source_coverage_after: '100%'
          outcome: 'success - did not contribute to mirrored source file'
      final_coverage_per_source_file:
        lines: '100%'
        branches: '100%'
        statements: '100%'
        functions: '100%'
      verification:
        mirrored_source_coverage_maintained: true|false
        all_tests_passing: true|false
    issues: ['issue1']
    ```
    <<<

**Decision (You)**: Aggregate removal reports. Verify 100% coverage maintained across mirrored source files. Calculate redundancy metrics (total removed, total kept-as-essential, redundancy %). Update todos.

#### Sub-Step 1.4: Fix Test Issues & Standards Compliance

**Purpose**: Fix any issues in test files and ensure complete standards compliance.
**Parallelism**: If >25 test files, batch — **max 8 concurrent** (10 files per batch).

**Planning (You)**:

1. List all test files via Glob (do NOT use `find` in bash).
2. Batching: ≤25 files → single subagent; >25 files → batches of 10 files each.
3. Standards: `testing/meta.md` + `testing/write.md`, `typescript/write.md`, `documentation/write.md`.
4. Use TodoWrite to create one todo per batch.

**Dispatch (Task tool)**:

Spin up Test Issue Fixing Agents in one message — at most 8 concurrent if batching.

    >>>
    **ultrathink: adopt the Test Standards Enforcer mindset**

    - You're a **Test Standards Enforcer** who follows:
      - **Standards Mastery**: Apply all testing, TypeScript, and documentation standards thoroughly
      - **Issue Correction**: Fix logic errors, type issues, and standards violations
      - **Preservation Focus**: Maintain test intent and coverage while fixing
      - **Quality Assurance**: Verify all fixes through testing and linting

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read** testing/meta.md + testing/write.md, typescript/write.md, documentation/write.md.

    **Assignment**: fix issues in the following test files:
    - [test file 1]
    - [... up to 10 files per batch]

    **Steps**:

    1. **Analysis**: read each test file; identify standards violations; note logic errors or incorrect behavior.
    2. **Issue Fixing**: fix TypeScript errors (no `any`); apply AAA pattern; ensure proper test naming; add missing documentation; correct test logic.
    3. **Verification**: `npm run test`; `npm run lint`; `npx tsc --noEmit`; verify coverage maintained at 100%.

    **Report (<1000 tokens)**:

    ```yaml
    status: success|failure|partial
    summary: 'Fixed [N] issues across [M] test files'
    modifications: ['spec/auth/service.spec.ts', ...]
    outputs:
      issues_fixed:
        type_errors: N
        logic_errors: M
        standards_violations: X
        documentation_missing: Y
      verification:
        all_tests_passing: true|false
        lint_check: pass|fail
        type_check: pass|fail
        coverage_maintained: '100%'
      standards_compliance:
        testing_standard: pass|fail
        typescript_standard: pass|fail
        documentation_standard: pass|fail
    issues: ['issue1']
    ```
    <<<

**Decision (You)**: Aggregate reports. If issues remain, retry. Update todos.

#### Sub-Step 1.5: Restructure Fixtures & Test Doubles

**Purpose**: Consolidate duplicate fixtures, improve organization, remove unused test support files.
**Parallelism**: Phase B may use parallel execution per the plan — **max 8 concurrent**.

**Phase A — Plan with a Plan Subagent**:

Use TodoWrite to create a planning todo. Dispatch a Plan subagent via the Task tool with `subagent_type="Plan"`:

    >>>
    **ultrathink: adopt the Test Structure Architect mindset**

    - You're a **Test Structure Architect** who follows:
      - **Pattern Recognition**: Identify duplicate fixture patterns
      - **Organization Design**: Create logical fixture structure
      - **Reusability Focus**: Maximize fixture reuse across tests
      - **Cleanup Awareness**: Identify unused fixtures and mocks

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read** testing/write.md (Test Double Organization section), typescript/write.md, documentation/write.md.

    **Assignment**: analyze all fixtures, mocks, and test support files; create a restructuring plan.

    **Analysis Steps**:

    1. Discover all test support files: `spec/fixtures/**/*.ts`, `spec/mocks/**/*.ts`, inline fixtures/mocks in test files.
    2. Identify duplication patterns: similar fixture data across files, repeated mock configurations, inline fixtures that could be shared.
    3. Analyze organization: directory structure, naming consistency, type safety compliance.
    4. Find unused files: fixtures not imported by any test, mocks defined but never used, factory functions without references.
    5. Create restructuring plan: consolidation opportunities (which to merge), organization improvements, deletion candidates, migration strategy.

    **Report**: comprehensive restructuring plan the orchestrator can use to execute fixture consolidation and organization improvements.
    <<<

Receive the plan, create execution todos.

**Phase B — Execute Restructuring**:

Dispatch 1 subagent (simple plan) or multiple subagents (complex plan) — at most 8 concurrent.

    >>>
    **ultrathink: adopt the Test Refactoring Specialist mindset**

    - You're a **Test Refactoring Specialist** who follows:
      - **Safe Refactoring**: Preserve test functionality while restructuring
      - **Type Safety**: Maintain TypeScript compliance throughout
      - **Incremental Changes**: Apply changes step-by-step with verification
      - **Testing Focus**: Verify tests pass after each change

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read** testing/write.md, typescript/write.md, documentation/write.md.

    **Assignment**: execute the restructuring plan provided.

    **Steps**:

    1. Create new shared fixture/mock files as specified.
    2. Migrate fixtures/mocks from old locations to new shared files.
    3. Update imports in all test files using migrated fixtures/mocks.
    4. Remove old fixture definitions (inline or in old files).
    5. Delete unused files identified in plan.
    6. Verify tests after each major change: `npm run test`; ensure all tests pass; fix broken imports.
    7. Type check: `npx tsc --noEmit`; fix TS errors.
    8. Lint check: `npm run lint`; fix linting issues.

    **Report (<1000 tokens)**:

    ```yaml
    status: success|failure|partial
    summary: 'Restructuring complete - created [N] shared files, migrated [M] fixtures'
    modifications: ['spec/fixtures/user.fixture.ts', ...]
    outputs:
      restructuring_summary:
        shared_files_created: N
        fixtures_consolidated: M
        mocks_consolidated: X
        unused_files_deleted: Y
        test_files_updated: Z
      created_files:
        - file: 'spec/fixtures/user.fixture.ts'
          exports: ['createUser', 'createAdminUser']
          consolidates: ['spec/auth/fixtures.ts', 'spec/users/fixtures.ts']
      deleted_files:
        - 'spec/fixtures/old-format.fixture.ts'
      verification:
        all_tests_passing: true|false
        type_check: pass|fail
        lint_check: pass|fail
        imports_valid: true|false
    issues: ['issue1']
    ```
    <<<

**Decision (You)**: Aggregate restructuring reports; verify tests still pass; confirm organization improved. Update todos.

#### Sub-Step 1.6: Final Verification

**Purpose**: Perform comprehensive final verification of the entire test suite.
**Parallelism**: Single subtask delegation.

Dispatch one Task subagent for independent validation:

    >>>
    **ultrathink: adopt the Quality Assurance Validator mindset**

    - You're a **Quality Assurance Validator** performing final verification with:
      - **Independent Validation**: Verify all claims independently
      - **Comprehensive Checking**: Test all aspects (coverage, passing, standards, efficiency)
      - **Metrics Focus**: Provide concrete numbers and measurements
      - **Pass/Fail Authority**: Make final determination on test suite quality

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read** testing/write.md, typescript/write.md, documentation/write.md.

    **Verification Steps**:

    1. **Coverage Verification**: `npm run coverage` or `vitest --coverage`; extract final metrics (line/branch/statement/function must all be 100%); verify NO uncovered code remains.
    2. **Test Execution Verification**: `npm run test`; verify ALL tests pass; count total tests; note execution time; check for flaky tests.
    3. **Standards Compliance Verification**: `npm run lint` (no errors); `npx tsc --noEmit` (no type errors); manually review test structure (AAA pattern, proper naming, JSDoc, no `any`).
    4. **Efficiency Metrics**: total source files, total test files, total tests, average tests per source file, coverage per test ratio, test suite execution time. Assess minimality (Minimal Testing Principle), fixture organization, redundancy elimination.
    5. **Final Quality Assessment**: overall grade A/B/C/D/F; production readiness yes/no; blockers; recommendations.

    **Report**: comprehensive final verification report with pass/fail verdict and quality assessment.
    <<<

**Decision (You)**: Receive the verification report. PASS → workflow complete. FAIL → identify blockers; if fixable, return to the appropriate sub-step; if critical, report failure with details. Mark workflow complete in TodoWrite.

### Step 2: Reporting

**Output Format**:

```yaml
workflow: complete-test
status: completed|failed
outputs:
  step_1_baseline:
    initial_coverage: 'X%'
    uncovered_files: N
    analysis_status: completed
  step_2_progressive_writing:
    batches_executed: N
    source_files_covered: M
    tests_created: X
    tests_kept: Y
    tests_deleted: Z
    final_coverage: '100%'
    writing_status: completed
  step_3_redundancy_removal:
    redundancy_candidates_identified: N
    tests_removed: M
    tests_kept_essential: X
    coverage_maintained: '100%'
    removal_status: completed
  step_4_issue_fixing:
    test_files_fixed: N
    issues_resolved: M
    standards_compliance: 'pass'
    fixing_status: completed
  step_5_fixture_restructuring:
    shared_fixtures_created: N
    fixtures_consolidated: M
    unused_files_deleted: X
    restructuring_status: completed
  step_6_final_verification:
    coverage_verified: '100%'
    all_tests_passing: true
    standards_compliant: true
    efficiency_grade: 'A|B|C|D|F'
    production_ready: true|false
    verification_status: pass|fail
  final_metrics:
    total_source_files: N
    total_test_files: M
    total_tests: X
    coverage_percentage: '100%'
    tests_per_source_file: Y
    redundancy_eliminated: Z
    test_suite_execution_time: 'W seconds'
  workflow_summary: |
    Successfully created comprehensive test suite with 100% coverage for [N] source files.
    Created [M] tests through progressive writing with coverage verification.
    Removed [X] redundant tests while maintaining 100% coverage.
    Fixed [Y] test issues and ensured standards compliance.
    Restructured fixtures for improved organization and reusability.
    Final verification confirms production-ready test suite with grade [A/B/C/D/F].
```
