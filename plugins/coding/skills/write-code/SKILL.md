---
name: write-code
description: 'Write production-ready code end-to-end via a full TDD lifecycle (design, skeleton, implement, test, refactor). Triggers when: "write a function", "implement this feature", "build a new module", "add a feature". Also use when: starting a new component from scratch, turning a spec or ticket into working code, creating a CLI or API endpoint with tests. Examples: "write a function that parses dates", "implement user authentication", "build a rate limiter module".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: <instruction> [--resume]
---

# Write Code

Orchestrates the complete TDD lifecycle by composing atomic skills into a sequential pipeline. Takes a feature instruction and drives it through project setup, design discovery, skeleton drafting, implementation, test fixing, optimization, and refactoring -- producing production-ready, fully tested code.

## Purpose & Scope

**What this command does NOT do**:

- Create only a skeleton without implementation (use `/coding:draft-code`)
- Complete only TODO-marked placeholders (use `/coding:complete-code`)
- Fix only test/lint/type issues (use `/coding:fix`)
- Refactor without the full lifecycle (use `/coding:refactor`)
- Perform code review (use `/coding:review`)

**When to REJECT**:

- If the user only wants a scaffold/skeleton -> tell them to use `/coding:draft-code`
- If the user only wants to complete existing TODOs -> tell them to use `/coding:complete-code`
- If the user only wants to fix failing tests/lint/types -> tell them to use `/coding:fix`
- If the instruction is too vague to define acceptance criteria
- If the target project has no testing framework configured

## Composition Structure

This is a **composite skill** that orchestrates the following atomic skills in sequence. Each child skill runs in `context: fork` and receives the `--from-composite` flag to suppress redundant confirmation gates.

```
write-code (this orchestrator)
  |
  |-- 1. Skill: coding:setup-project   (conditional: only if no project exists)
  |-- 2. Skill: coding:draft-code      (Steps 0-1: design discovery + skeleton)
  |-- 3. Skill: coding:complete-code   (Step 2: implementation / green phase)
  |-- 4. Skill: coding:fix             (Steps 3-4: fix issues + optimize fixtures)
  |-- 5. Skill: coding:refactor        (Step 5: refactor + documentation)
```

### State Handover Between Steps

State is passed between child skills via handover documents (CONTEXT.md, NOTES.md, PLAN.md). Each child skill reads these documents for context and updates them upon completion.

### Resume Support

When `--resume` is provided, the orchestrator reads handover documents to determine which step to resume from:
- Files with `need-draft` -> resume from `coding:draft-code`
- Files with `need-completion` -> resume from `coding:complete-code`
- Files with `need-fixing` -> resume from `coding:fix`
- Files with `need-refactoring` -> resume from `coding:refactor`

### Composite Convention

When calling child skills, this orchestrator passes `--from-composite` as an argument. Child skills receiving this flag suppress their own confirmation gates and trust the orchestrator to handle user interaction.

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Parse Arguments

1. **Extract Instruction**
   - Parse `<instruction>` from $ARGUMENTS
   - Identify feature requirements, scope, and acceptance criteria
   - If instruction is ambiguous, ask for clarification before proceeding

2. **Detect Resume Mode**
   - Check if `--resume` flag is present in $ARGUMENTS
   - If `--resume`:
     - Search for handover documents (CONTEXT.md, NOTES.md, PLAN.md) in the working directory
     - Parse file substates from CONTEXT.md to determine which skill to resume from
     - Extract change direction from PLAN.md next steps or NOTES.md open questions
     - If handover files are missing, reject with: "No handover files found. Create them first with `/coding:handover`"

### Step 2: Conditional Project Setup

Check if the target project has essential structure (package.json, source directories, test framework).

- **If project is NOT set up**: Invoke `coding:setup-project` with the target path and `--from-composite`
- **If project IS set up**: Skip this step

### Step 3: Draft Code Skeleton (design + skeleton)

Invoke `coding:draft-code` with the parsed instruction and `--from-composite`.

This skill handles:
- Design direction discovery (searching for DESIGN.md, handover docs)
- Code skeleton creation with TODO placeholders
- Test structure creation with describe.todo/it.todo patterns
- TypeScript and lint validation of the skeleton

**Interactive gate**: After this skill completes, present the user with options:
1. Proceed to implementation
2. Request changes to the skeleton (re-run draft-code with change direction)
3. Resume from a different step
4. Pause and create handover documentation

### Step 4: Implementation (green phase)

Invoke `coding:complete-code` with the target area and `--from-composite`.

This skill handles:
- Replacing TODO placeholders with minimal working implementations
- TDD Green phase: implementing just enough code to make tests pass
- Continuous test execution to verify progress

**Interactive gate**: After this skill completes, present the user with options:
1. Proceed to fixing
2. Request changes to implementation (re-run complete-code with direction)
3. Resume from a different step
4. Pause and create handover documentation

### Step 5: Fix Issues and Optimize (fix + optimize)

Invoke `coding:fix` with the target area and `--from-composite`.

This skill handles:
- Fixing test issues and standards compliance
- Critical root cause analysis for test failures
- Optimizing test fixtures and mocks
- Batch processing for large file sets (>25 files)

**Interactive gate**: After this skill completes, present the user with options:
1. Proceed to refactoring
2. Request changes to fixes (re-run fix with specific notes)
3. Resume from a different step
4. Pause and create handover documentation

### Step 6: Refactor and Document

Invoke `coding:refactor` with the target area and `--from-composite`.

This skill handles:
- Code structure improvements without changing functionality
- Naming convention enforcement
- Comprehensive JSDoc documentation
- Final quality validation (tests, lint, types, coverage)

**Interactive gate**: After this skill completes, present the user with options:
1. Complete the workflow
2. Request changes to refactoring (re-run refactor with focus)
3. Resume from a different step
4. Pause and create handover documentation

### Step 7: Reporting

**Output Format**:

```
[OK/FAIL] Command: write-code $ARGUMENTS

## Summary
- Instruction: [parsed instruction]
- Steps executed: [list of skills run]
- Steps skipped: [list of skills skipped, if any]
- Files created: [count]
- Files modified: [count]
- Tests passing: [count]
- Coverage: [percentage]

## Actions Taken
1. [setup-project] Project setup: [brief summary or "skipped"]
2. [draft-code] Drafted skeleton: [files created]
3. [complete-code] Implemented: [functions/modules completed]
4. [fix] Fixed: [issues resolved, fixtures optimized]
5. [refactor] Refactored: [quality improvements, docs added]

## Validation Results
- Tests: PASS/FAIL ([X] passing, [Y] failing)
- Types: PASS/FAIL ([N] errors)
- Lint: PASS/FAIL ([N] warnings)
- Coverage: [percentage]

## Next Steps
1. [Follow-up action if any]
2. [Commit with /coding:commit]
```

## Examples

### Implement a New Feature

```bash
/write-code "Create user authentication service with login, logout, and token refresh"
# Runs full TDD lifecycle:
# 1. setup-project (if needed)
# 2. draft-code: Discovers design, drafts types, service skeleton, test structure
# 3. complete-code: Implements auth logic to pass tests
# 4. fix: Fixes any test/lint/type issues, optimizes fixtures
# 5. refactor: Refactors for quality and adds documentation
```

### Implement from Design Spec

```bash
/write-code "Implement the payment processing module per DESIGN.md"
# Reads DESIGN.md for requirements, then runs full cycle
```

### Resume Interrupted Work

```bash
/write-code "Continue implementing the notification system" --resume
# Reads CONTEXT.md, NOTES.md, PLAN.md
# Auto-detects resume point from file substates
# Continues from the appropriate skill
```

### Error Cases

```bash
/write-code "thing"
# Error: Instruction too vague to define acceptance criteria
# Suggestion: Provide specific requirements like
#   "Create validation helpers for user input with email, phone, and URL validators"

/write-code "Fix the failing tests"
# Rejected: For fixing issues only, use /coding:fix instead

/write-code "Create a skeleton for the API"
# Rejected: For scaffolding only, use /coding:draft-code instead
```
