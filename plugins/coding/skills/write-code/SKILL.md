---
name: write-code
description: Write production-ready code using full TDD lifecycle with design discovery, skeleton creation, implementation, test fixing, optimization, and refactoring. Use when implementing new features, writing new modules, or performing comprehensive code changes that need the complete development workflow.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite
argument-hint: <instruction> [--resume]
---

# Write Code

Orchestrates the complete TDD lifecycle (Steps 0-5) from the write-code workflow. Takes a feature instruction and drives it through design discovery, skeleton drafting, implementation, test fixing, optimization, and refactoring — producing production-ready, fully tested code.

## Purpose & Scope

**What this command does NOT do**:

- Create only a skeleton without implementation (use `/coding:draft-code`)
- Complete only TODO-marked placeholders (use `/coding:complete-code`)
- Fix only test/lint/type issues (use `/coding:fix`)
- Perform code review (use `/coding:review`)

**When to REJECT**:

- If the user only wants a scaffold/skeleton -> tell them to use `/coding:draft-code`
- If the user only wants to complete existing TODOs -> tell them to use `/coding:complete-code`
- If the user only wants to fix failing tests/lint/types -> tell them to use `/coding:fix`
- If the instruction is too vague to define acceptance criteria
- If the target project has no testing framework configured

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
     - Parse file substates from CONTEXT.md to determine which step to resume from:
       - Files with `need-draft` -> resume from Step 1
       - Files with `need-completion` -> resume from Step 2
       - Files with `need-fixing` -> resume from Step 3
       - Files with `need-refactoring` -> resume from Step 5
     - Extract change direction from PLAN.md next steps or NOTES.md open questions
     - Extract any steps to skip from completed phases in PLAN.md
     - If handover files are missing, reject with: "No handover files found. Create them first with `/coding:handover`"

### Step 2: Load and Execute Write-Code Workflow

1. **Load the Workflow**
   - Read the write-code workflow document:
     `/Users/alvis/.claude/plugins/cache/alvis/coding/2026-02-16/constitution/workflows/write-code.md`

2. **Prepare Workflow Inputs**
   - **Feature Requirements**: The parsed `<instruction>`
   - **Resume From Step**: Auto-detected step from handover (if `--resume`), otherwise 0
   - **Change Direction**: Extracted from handover docs (if `--resume`), otherwise none
   - **Skip Steps**: Derived from completed phases in handover (if `--resume`), otherwise none
   - **Interactive Mode**: true (if the client supports it)

3. **Execute the Workflow**
   - Follow the workflow document step by step, executing Steps 0 through 5:
     - **Step 0**: Design Direction Discovery
     - **Step 1**: Draft Code Skeleton & Test Structure
     - **Step 2**: Implementation (Green Phase)
     - **Step 3**: Fix Test Issues & Standards Compliance
     - **Step 4**: Optimize Test Structure & Fixtures
     - **Step 5**: Refactoring & Documentation
   - Skip any steps indicated by the resume analysis
   - Apply change direction at the appropriate step
   - Delegate implementation work to subagents as defined in the workflow

### Step 3: Reporting

**Output Format**:

```
[OK/FAIL] Command: write-code $ARGUMENTS

## Summary
- Instruction: [parsed instruction]
- Steps executed: [list of steps run]
- Steps skipped: [list of steps skipped, if any]
- Files created: [count]
- Files modified: [count]
- Tests passing: [count]
- Coverage: [percentage]

## Actions Taken
1. [Step 0] Design discovery: [brief summary]
2. [Step 1] Drafted skeleton: [files created]
3. [Step 2] Implemented: [functions/modules completed]
4. [Step 3] Fixed: [issues resolved]
5. [Step 4] Optimized: [fixtures/mocks improved]
6. [Step 5] Refactored: [quality improvements]

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
# Step 0: Discovers design patterns, existing auth code
# Step 1: Drafts types, service skeleton, test structure
# Step 2: Implements auth logic to pass tests
# Step 3: Fixes any test/lint/type issues
# Step 4: Optimizes test fixtures and mocks
# Step 5: Refactors for quality and adds docs
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
# Continues from the appropriate step
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
