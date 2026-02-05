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

Intelligently fixes code and test issues based on error messages, failing tests, or review feedback. Automatically detects the area of concern and applies the appropriate fix workflow.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Add new features
- Refactor working code
- Change architecture
- Create new files (unless needed for fixes)

**When to REJECT**:

- No errors or issues found
- Request is for new feature development
- Changes would break existing functionality
- Fix requires external service changes

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Diagnose Issues

1. **Parse Arguments**
   - Extract specifier (file, directory, or pattern)
   - Parse --area flag (test, lint, type, review)
   - Parse --note for specific guidance

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

1. **Analyze Root Cause**
   - Read affected files
   - Understand error context
   - Identify fix approach

2. **Create Fix Plan**
   - List changes needed
   - Order by dependency
   - Estimate impact

### Step 3: Apply Fixes

1. **Execute Changes**
   - Apply code modifications
   - Update tests if needed
   - Fix imports and references

2. **Iterate Until Passing**
   - Re-run checks after each fix
   - Address new errors that emerge
   - Continue until clean

### Step 4: Validate

1. **Run Full Checks**
   - Execute test suite
   - Run linter
   - Run type checker
   - Verify no regressions

### Step 5: Reporting

**Output Format**:

```
[✅/❌] Command: fix $ARGUMENTS

## Summary
- Area: [detected or specified area]
- Issues found: [count]
- Issues fixed: [count]
- Files modified: [count]

## Issues Resolved
1. [file:line] - [issue description]
   Fix: [what was changed]
2. [file:line] - [issue description]
   Fix: [what was changed]

## Validation Results
- Tests: [PASS/FAIL] ([X] passing, [Y] failing)
- Types: [PASS/FAIL] ([N] errors)
- Lint: [PASS/FAIL] ([N] warnings)

## Next Steps
1. Review changes
2. Run full test suite
3. Commit fixes
```

## 📝 Examples

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
# All checks passing - nothing to fix
```
