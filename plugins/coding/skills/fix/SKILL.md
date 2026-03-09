---
name: fix
description: Fix code and test issues using intelligent area detection and workflow. Use when resolving test failures, fixing linting errors, addressing type issues, or applying review feedback.
model: opus
context: fork
agent: general-purpose
allowed-tools: Edit, MultiEdit, Read, Write, Grep, Glob, Bash, Task, TodoWrite
argument-hint: [specifier] [--area=AREA] [--note=...]
---

# Fix Code Issues

Intelligently fixes code and test issues based on error messages, failing tests, or review feedback. Automatically detects the area of concern and applies the appropriate fix workflow. Corresponds to Steps 3-4 (Fix Test Issues + Optimize Test Structure) of the TDD lifecycle.

## Purpose & Scope

**What this command does NOT do**:

- Add new features
- Refactor working code (use `/coding:refactor`)
- Change architecture
- Create new files (unless needed for fixes)

**When to REJECT**:

- No errors or issues found
- Request is for new feature development
- Changes would break existing functionality
- Fix requires external service changes

## Applicable Standards

When executing this skill, the following standards apply:

### For Test Correction (Step 3 -- Fix Issues)

| Standard | Purpose |
|---|---|
| `testing/scan` | Test quality, patterns, coverage analysis |
| `typescript/scan` | Type safety verification |
| `documentation/scan` | Documentation completeness check |

When a specific rule violation is detected, load its fix guidance from `testing/rules/<rule-id>.md`.

### For Fixture Optimization (Step 4 -- Optimize)

| Standard | Purpose |
|---|---|
| `universal/write` | General code authoring conventions |
| `typescript/write` | TypeScript patterns and type safety |
| `function/write` | Function design and complexity |
| `documentation/write` | Documentation for test utilities |
| `testing/write` | Test fixture and mock patterns |

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Diagnose Issues

1. **Parse Arguments**
   - Extract specifier (file, directory, or pattern) from $ARGUMENTS
   - Parse `--area` flag (test, lint, type, review)
   - Parse `--note` for specific guidance
   - Determine if running as standalone or as part of composite (`--from-composite`)

2. **Auto-Detect Area** (if not specified)
   - Run tests to check for failures
   - Run linter to check for violations
   - Run type check for TypeScript errors
   - Prioritize: tests > types > lint

3. **Gather Error Context**
   - Collect error messages
   - Identify affected files
   - Map error to code location

### Step 2: Plan Fixes

1. **Critical Root Cause Analysis**
   - Read affected files and their test descriptions
   - Determine expected behavior from test descriptions and specification files
   - Analyze whether issues are in source code logic vs. test implementation
   - Check DESIGN.md and specification files for expected behavior hints
   - If uncertain about expected behavior, ask user for clarification

2. **Create Fix Plan**
   - List changes needed
   - Order by dependency
   - Estimate impact

### Step 3: Apply Test Fixes

Fix issues in test files including incorrect behavior, standards violations, and test-related problems while preserving test intent and correctness.

1. **For Batch Execution** (when >25 files affected):
   - Generate batches at runtime based on test files found
   - Limit each batch to max 10 test files
   - Process batches in parallel

2. **Execute Test Corrections**
   - Apply code modifications to fix test issues
   - Fix incorrect test behavior and logic (never modify tests just to make them pass)
   - Fix standards violations
   - Update tests if needed
   - Fix imports and references
   - **CRITICAL**: Only modify test files, mock files, and fixture files -- NEVER modify source code under test

3. **Handle Unused Code Errors**
   - Check design documentation first to verify if code is part of planned functionality
   - Check handover documentation to see if this is intentional incomplete implementation
   - If code is planned but not yet implemented: use `throw new Error('IMPLEMENTATION: ...')` pattern
   - Only remove code that is genuinely unnecessary

4. **Iterate Until Passing**
   - Re-run checks after each fix
   - Address new errors that emerge
   - Continue until clean

### Step 4: Optimize Test Fixtures (Conditional)

Fix issues in test fixtures and mocks, ensuring proper structure and organization while maintaining correctness. **Skip this step if no fixtures/mocks exist**.

1. **Identify Fixture Issues**
   - Incorrect fixture definitions or mock behavior
   - Type safety issues in fixtures/mocks
   - Organizational problems
   - Standards violations in test support files

2. **Apply Fixture Corrections**
   - Fix fixture/mock behavior and accuracy
   - Ensure fixtures represent realistic and valid test data
   - Apply proper organization patterns
   - **CRITICAL**: Only modify test fixtures, mock files, and test support files

3. **Verify Fixtures**
   - Run tests to verify fixtures work correctly
   - Maintain test accuracy after changes

### Step 5: Validate

1. **Run Full Checks**
   - Execute test suite via `npm run test` or equivalent
   - Run linter via `npm run lint` or equivalent
   - Run type checker
   - Verify no regressions

2. **Error Anthropology** (when failures occurred)
   - Root Cause: Why did this specific error occur?
   - Systemic Cause: Why did the process allow this error?
   - Belief Update: What assumptions proved wrong?
   - System Improvement: How to prevent this class of error?

### Step 6: Reporting

**Output Format**:

```
[OK/FAIL] Command: fix $ARGUMENTS

## Summary
- Area: [detected or specified area]
- Issues found: [count]
- Issues fixed: [count]
- Files modified: [count]

## Root Cause Analysis
- Expected behavior: [description]
- Root cause: [source_code_logic|test_implementation|requirements_unclear]
- Reasoning: [how expected behavior was determined]

## Issues Resolved
1. [file:line] - [issue description]
   Fix: [what was changed]
2. [file:line] - [issue description]
   Fix: [what was changed]

## Fixture Optimizations (if applicable)
- Fixtures processed: [count]
- Issues fixed: [count]
- Organization improvements: [count]

## Validation Results
- Tests: [PASS/FAIL] ([X] passing, [Y] failing)
- Types: [PASS/FAIL] ([N] errors)
- Lint: [PASS/FAIL] ([N] warnings)

## Next Steps
1. Review changes
2. Run full test suite
3. Refactor with /coding:refactor
4. Commit with /coding:commit
```

## Examples

### Auto-Detect and Fix

```bash
/fix
# Automatically detects issues and fixes them
```

### Fix Specific Area

```bash
/fix --area=test
# Focuses only on fixing test failures
```

### Fix Specific File

```bash
/fix "src/auth/login.ts"
# Fixes issues in specific file
```

### Fix with Guidance

```bash
/fix --area=lint --note="Focus on unused variables"
# Fixes lint issues with specific focus
```

### Fix from Review

```bash
/fix "src/utils/" --note="Address code review feedback: improve error handling"
# Applies specific improvements based on review notes
```

### Error Case

```bash
/fix "src/perfect-code.ts"
# No issues found in src/perfect-code.ts
# All checks passing -- nothing to fix
```
