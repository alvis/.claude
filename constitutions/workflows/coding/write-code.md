# Write Code

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Implement any feature using Test-Driven Development practices by first creating tests through the create-test workflow, then implementing and refactoring code with comprehensive quality gates.
**When to use**: Every time you write new code, modify existing functionality, or add features requiring implementation.
**Prerequisites**: Testing framework configured, requirements understood, development environment ready, Testing Standards reviewed, interface definitions for intended features.

### Your Role

You are a **TDD Implementation Director** who orchestrates the test-driven development process like a quality-focused development manager ensuring comprehensive testing and clean implementation. You never execute coding tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break TDD cycle into systematic phases with specialized development teams
- **Parallel Coordination**: Run test planning and implementation preparation simultaneously when dependencies allow
- **Quality Oversight**: Ensure strict adherence to Red-Green-Refactor cycle and Testing Standards
- **Testing Authority**: Make go/no-go decisions on implementation readiness based on test coverage and quality validation

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Feature Requirements**: Specific functionality or feature that needs to be implemented
- **Implementation Scope**: Clear definition of what needs to be built with acceptance criteria
- **Interface Definition**: Specifications of intended interfaces and APIs to implement
- **Intended Behavior**: Description of expected behavior and usage examples for TDD test creation

#### Optional Inputs

- **Existing Code Context**: Related existing functionality and patterns (default: discover during analysis)
- **Testing Strategy**: Specific testing approaches or coverage requirements (default: follow Testing Standards)
- **Quality Requirements**: Specific quality gates or standards to meet (default: all standard quality checks)
- **Integration Requirements**: Dependencies or integration points to consider (default: identify during planning)

#### Expected Outputs

- **Test Suite**: Comprehensive tests following TDD principles with 100% coverage
- **Implementation Code**: Clean, tested implementation that passes all quality gates
- **Quality Validation**: Confirmation that all quality checks pass including linting and type checking
- **Documentation**: Code documentation and implementation notes following standards

#### Data Flow Summary

The workflow takes feature requirements and systematically implements them using the Red-Green-Refactor TDD cycle, creating comprehensive tests first, then minimal implementation, followed by refactoring with continuous quality validation.

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
[Step 1: Test Creation (Red Phase)] ─→ (Sub-workflow: create-test in TDD mode)
   |                                    │
   └──→ create-test workflow ──────────┤ (TDD mode execution)
   |                                    │
   v                                    v
[Step 2: Implementation & Refactoring] ─→ (4-Phase Execution)
   |                                    │
   ├─ Phase 1: Planning ───────────────┤ (You orchestrate)
   ├─ Phase 2: Execution ──────────────┤ (1 subagent max)
   ├─ Phase 3: Review ─────────────────┤ (1 subagent max)
   └─ Phase 4: Decision ───────────────┘ (You decide)
       ↑                    │
       └────────────────────┘ (Loop if needed)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Sub-workflow and single subagents per phase
• ARROWS (───→): You assign work to subagents or sub-workflows
• LOOP: Phase 4 returns to Phase 2 if fixes needed
═══════════════════════════════════════════════════════════════════

Note: 
• You: Orchestrates TDD workflow, assigns tasks, makes decisions
• Step 1: Delegates test creation to create-test sub-workflow
• Step 2: Single subagent execution per phase (Green & Refactor combined)
• Workflow is LINEAR: Step 1 → Step 2 (following TDD principles)
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Test Creation and Red Phase (Sub-workflow)
2. Implementation and Refactoring (Green & Refactor Phases Combined)

### Step 1: Test Creation and Red Phase (Sub-workflow)

**Step Configuration**:

- **Purpose**: Create comprehensive tests for intended features using TDD approach through the create-test workflow
- **Input**: Feature Requirements, Implementation Scope, Interface Definition, Intended Behavior from workflow inputs
- **Output**: Complete test suite, Red phase verification, test structure for Step 2
- **Sub-workflow**: constitutions/workflows/coding/create-test.md
- **Parallel Execution**: No - delegated to sub-workflow

#### Execute Create-Test Workflow (You)

When you reach this step and see sub-workflow path:

1. Use Read tool to load the sub-workflow file
2. Parse the sub-workflow to identify its steps
3. Dynamically expand step to 1.1, 1.2, 1.3... from the sub-workflow content
4. Use todo to track the status of each step
5. Execute each step as instructed in the sub-workflow with TDD mode parameters:
   - **Test Mode**: "tdd" (for test-driven development)
   - **Interface Definition**: Provided interface specifications and API contracts
   - **Intended Behavior**: Expected behavior descriptions and usage examples
6. After all sub-workflow steps are complete, continue to Step 2

**Key Parameters for Create-Test Workflow**:

- Set Test Mode to "tdd" for test-driven development approach
- Provide Interface Definition with intended APIs and method signatures
- Include Intended Behavior with expected functionality and usage examples
- Ensure test creation follows TDD Red phase principles (tests fail initially)

### Step 2: Implementation and Refactoring (Green & Refactor Phases Combined)

**Step Configuration**:

- **Purpose**: Implement minimal code to make tests pass, then refactor for quality and maintainability while keeping all tests passing
- **Input**: Test suite, failing tests, Red phase verification from Step 1
- **Output**: Complete implementation, refactored code, quality validation, TDD cycle completion
- **Sub-workflow**: None
- **Parallel Execution**: No - single subagent per phase

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from Step 1 (test suite, failing tests, Red phase verification)
2. **List all related resources** for implementation patterns, refactoring guidelines, and quality standards
3. **Determine the standards** to send to subagents (all coding standards, documentation requirements, TDD principles)
4. **Create task assignment** following these rules:
   - Generate single comprehensive task covering implementation and refactoring
   - Include both Green phase (minimal implementation) and Refactor phase (quality improvement)
   - Assign single subagent to perform complete implementation cycle
5. **Use TodoWrite** to create task for combined implementation and refactoring
6. **Prepare task assignment** with test guidance, implementation requirements, and refactoring guidelines
7. **Queue single comprehensive task** for execution

**OUTPUT from Planning**: Combined implementation and refactoring task assignment as todo

#### Phase 2: Execution (Single Subagent)

**What You Send to Subagent**:

In a single message, you spin up **1** subagent to perform both implementation and refactoring.

- **[IMPORTANT]** When there are any issues reported, you must analyze and provide feedback for fixes
- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about TDD principles and comprehensive quality implementation
- **[IMPORTANT]** Use TodoWrite to update task status from 'pending' to 'in_progress' when dispatched

Request the subagent to perform the following steps with full detail:

      >>>
      **ultrathink: adopt the TDD Implementation & Refactoring Master mindset**

      - You're a **TDD Implementation & Refactoring Master** with deep expertise in complete TDD cycle execution who follows these technical principles:
      - **Minimal Implementation First**: Write only enough code to make tests pass (Green phase)
      - **Quality Refactoring Second**: Improve code structure and maintainability without changing functionality
      - **Standards Mastery**: Apply all coding standards for production-quality code
      - **Test-Protected Development**: Ensure all tests continue to pass throughout both phases

      **Read the following assigned standards** and follow them recursively (if A references B, read B too):

      - constitutions/standards/coding/general-principles.md
      - constitutions/standards/coding/error-handling-logging.md
      - constitutions/standards/coding/typescript.md
      - constitutions/standards/coding/functions.md
      - constitutions/standards/coding/documentation.md
      - constitutions/standards/coding/testing.md
      - constitutions/standards/coding/naming/files.md

      **Assignment**
      You're assigned to complete the full TDD implementation cycle:

      - Minimal code implementation to satisfy failing tests (Green Phase)
      - Code refactoring and quality improvement (Refactor Phase)
      - Documentation addition and final quality validation

      **Steps**

      **GREEN PHASE - Minimal Implementation:**
      1. Implement minimal code to make tests pass:
         - Write simplest possible implementation that satisfies test requirements
         - Focus only on making failing tests pass, avoid adding extra features
         - Follow function design standards for structure and TypeScript patterns
         - Implement proper error handling as specified by tests
         - Ensure type safety and compliance with TypeScript standards
      2. Execute tests and verify Green phase:
         - Run all tests to ensure they now pass (Green phase achieved)
         - Verify no existing tests are broken by new implementation
         - Confirm test coverage remains at 100% for implemented functionality
         - Validate that tests pass for the right reasons (correct implementation)

      **REFACTOR PHASE - Quality Improvement:**
      3. Refactor implementation for quality and maintainability:
         - Improve code structure following general principles and naming standards
         - Enhance readability and maintainability without changing functionality
         - Apply proper naming conventions for functions, variables, and types
         - Ensure code follows all established coding standards patterns
         - Run tests continuously to ensure no functionality is broken during refactoring
      4. Add comprehensive documentation and comments:
         - Add JSDoc comments following documentation standards
         - Include inline comments for complex logic or business rules
         - Document function parameters, return types, and behavior
         - Add usage examples where appropriate per documentation guidelines
      5. Perform final quality validation:
         - Run complete test suite to verify all tests still pass
         - Execute linting and type checking to ensure standards compliance
         - Verify code coverage remains at 100% after refactoring
         - Confirm final implementation meets all quality gates

      **Report**
      **[IMPORTANT]** You're requested to return the following:

      - Green phase completion with minimal implementation and test satisfaction
      - Refactor phase completion with quality improvements and test preservation
      - Documentation addition and standards compliance enhancement
      - Overall TDD cycle completion and production readiness

      **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

      ```yaml
      status: success|failure|partial
      summary: 'Brief description of complete TDD implementation and refactoring'
      modifications: ['implementation-files-created', 'refactoring-applied', 'documentation-added']
      outputs:
      green_phase:
         implementation_completed: ...
         tests_passing: ...
         minimal_verification: ...
      refactor_phase:
         refactoring_completed: ...
         documentation_added: ...
         quality_validation: ...
      tdd_cycle_completion: ...
      issues: ['issue1', 'issue2', ...]  # only if problems encountered
      ```
      <<<

#### Phase 3: Review (Single Subagent)

**What You Send to Review Subagent**:

In a single message, you spin up **1** review subagent to check complete implementation and refactoring quality.

- **[IMPORTANT]** Review is read-only - subagent must NOT modify any resources
- **[IMPORTANT]** You MUST ask review subagent to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request the review subagent to perform the following review with full scrutiny:

      >>>
      ultrathink: adopt the TDD Cycle Validator mindset

      - You're a **TDD Cycle Validator** with expertise in complete TDD implementation review who follows these principles:
      - **Green Phase Validation**: Ensure minimal implementation satisfies all tests
      - **Refactor Phase Validation**: Verify quality improvements without functionality changes
      - **Standards Enforcement**: Confirm implementation follows all coding standards
      - **Quality Assessment**: Ensure production readiness and maintainability

      **Review the standards recursively that were applied**:

      - constitutions/standards/coding/general-principles.md - Check general coding principles
      - constitutions/standards/coding/functions.md - Check function design compliance
      - constitutions/standards/coding/typescript.md - Verify TypeScript standards
      - constitutions/standards/coding/documentation.md - Check documentation quality
      - constitutions/standards/coding/testing.md - Validate testing approach

      **Review Assignment**
      You're assigned to review the complete TDD implementation results:

      - Green phase implementation and test satisfaction
      - Refactor phase quality improvements and standards compliance
      - Overall TDD cycle completion and production readiness

      #### Review Steps

      1. Review Green phase implementation:
         - Verify minimal implementation satisfies all failing tests
         - Check that all tests now pass without breaking existing functionality
         - Validate implementation follows TDD minimal approach
      2. Review Refactor phase improvements:
         - Verify code structure and quality improvements
         - Check that functionality remains unchanged after refactoring
         - Validate continuous test passing during refactoring
      3. Check standards compliance and documentation:
         - Review compliance with all assigned coding standards
         - Validate documentation quality and completeness
         - Assess overall code quality and maintainability
      4. Assess TDD cycle completion and production readiness:
         - Confirm complete Red-Green-Refactor cycle execution
         - Validate final implementation meets all quality gates
         - Assess overall production readiness

      **Report**
      **[IMPORTANT]** You're requested to verify and report:

      - Green phase implementation quality and test satisfaction
      - Refactor phase improvements and standards compliance
      - Documentation completeness and quality validation
      - Overall TDD cycle completion and production readiness

      **[IMPORTANT]** You MUST return the following review report (<500 tokens):

      ```yaml
      status: pass|fail
      summary: 'Brief verification summary of complete TDD implementation'
      checks:
      green_phase_implementation: pass|fail
      refactor_phase_quality: pass|fail
      standards_compliance: pass|fail
      documentation_quality: pass|fail
      tdd_cycle_completion: pass|fail
      production_readiness: pass|fail
      fatals: ['issue1', 'issue2', ...]  # Only critical blockers
      warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
      recommendation: proceed|retry|rollback
      ```
      <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (implementation + refactoring + review)
2. **Apply decision criteria**:
   - Review Green phase completion and test satisfaction
   - Review Refactor phase quality improvements and standards compliance
   - Consider documentation completeness and overall production readiness
3. **Select next action**:
   - **PROCEED**: Complete TDD cycle successful → Complete workflow successfully
   - **FIX ISSUES**: Partial success with minor issues → Create new task for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical failures → Revert changes → Create new task for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark task as 'completed' and workflow as complete
   - If RETRY: Add new todo items for retry tasks
   - If ROLLBACK: Mark task as 'failed' and add rollback todos
5. **Prepare completion**: Package final implementation results for workflow output

### Workflow Completion

**Report the workflow output as specified:**

```yaml
workflow: write-code
status: completed
outputs:
  test_suite:
    files_created: ['src/component.spec.ts', 'src/utils.spec.ts']
    coverage_percentage: 100
    tests_count: 25
    red_phase_verified: true
  implementation_code:
    files_created: ['src/component.ts', 'src/utils.ts']
    green_phase_verified: true
    standards_compliant: true
  quality_validation:
    linting_passed: true
    type_checking_passed: true
    all_tests_passing: true
  documentation:
    jsdoc_added: true
    usage_examples: true
    standards_met: true
  tdd_cycle:
    red_phase: completed
    green_phase: completed
    refactor_phase: completed
    cycle_verified: true
summary: |
  Successfully implemented [Feature Name] using TDD methodology. Created comprehensive
  test suite with 100% coverage, implemented minimal working code, and refactored
  for quality. All phases of Red-Green-Refactor cycle completed successfully.
```
