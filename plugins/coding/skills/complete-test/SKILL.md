---
name: complete-test
description: 'Write comprehensive test suites reaching 100% coverage with minimal redundancy. Triggers when: "write tests for this", "add unit tests", "write test cases", "increase test coverage", "test this function". Also use when: filling coverage gaps, optimizing an existing test suite, adding tests before refactor. Examples: "write tests for src/parser.ts", "get this file to 100% coverage", "add unit tests for the auth module".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
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

You are a **Test Suite Orchestrator** who coordinates the complete test development lifecycle like a quality-focused testing director ensuring comprehensive coverage, minimal redundancy, and optimal test structure. You never execute testing tasks directly, only delegate and coordinate. Your management style emphasizes:

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
- **Max Parallel Batches**: Maximum concurrent subagents (default: 10)

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

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.

- **If present**: Use **Team Mode** — full team orchestration with persistent teammates and agent reuse (loaded from `references/team-mode.md` in Step 2)
- **If absent**: Use **Subagent Mode** — existing workflow via fire-and-forget subagents (loaded from `references/subagent-mode.md` in Step 2)


### Step 2: Execute selected mode

Load exactly ONE of the following references based on the decision in Step 1, then execute its workflow end-to-end before returning to Step 3.

- **Team Mode** (Agent Teams enabled): see `references/team-mode.md` for full Lead-Orchestrator workflow with persistent teammates, agent-pool reuse, and `context_level`-based lifecycle management across Phases 1-7.
- **Subagent Mode** (fallback): see `references/subagent-mode.md` for the fire-and-forget Task-subagent workflow with TodoWrite tracking across Steps 2B.1-2B.6.

Both modes execute the same six-phase workflow (baseline analysis → progressive test writing → redundancy removal → fix issues → restructure fixtures → final verification) and produce the Step 3 reporting payload below.


### Step 3: Reporting

**Output Format** (same for both modes):

```yaml
workflow: complete-test
status: completed|failed
execution_mode: team|subagent
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
  agent_lifecycle:  # Team mode only
    agents_spawned: N
    agents_reused: M
    agents_retired_context_50_plus: X
    analyst_reused_as_verifier: true|false
    planner_reused_as_structure_planner: true|false
    writer_reuse_count: N
    remover_reuse_count: M
    fixer_reuse_count: X
  workflow_summary: |
    Successfully created comprehensive test suite with 100% coverage for [N] source files.
    Created [M] tests through progressive writing with coverage verification.
    Removed [X] redundant tests while maintaining 100% coverage.
    Fixed [Y] test issues and ensured standards compliance.
    Restructured fixtures for improved organization and reusability.
    Final verification confirms production-ready test suite with grade [A/B/C/D/F].
    [Team mode only: Execution mode: team. Agents spawned: N, reused: M, retired: X.]
```
