---
name: refactor
description: Refactor implementation for quality and maintainability with comprehensive documentation. Use when improving code structure, enhancing readability, applying naming conventions, adding JSDoc, or performing final quality validation.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task
argument-hint: <area> [--focus=naming|structure|docs|all]
---

# Refactor Code

Refactors implementation for quality and maintainability without changing functionality. Improves code structure, enhances readability, applies proper naming conventions, adds comprehensive JSDoc documentation, and performs final quality validation ensuring all tests continue to pass.

## Purpose & Scope

**What this command does NOT do**:

- Change functionality or behavior of existing code
- Add new features or business logic
- Fix failing tests (use `/coding:fix` instead)
- Create new test cases
- Modify project configuration

**When to REJECT**:

- Request is for new feature development (use `/coding:write-code`)
- Request is to fix bugs or failing tests (use `/coding:fix`)
- Area path is invalid or no files found
- Code has failing tests (fix tests first before refactoring)

## Applicable Standards

When executing this skill, the following standards apply:

| Standard | Purpose |
|---|---|
| `universal/write` | General code authoring conventions |
| `typescript/write` | TypeScript patterns and type safety |
| `function/write` | Function design, signatures, and complexity |
| `documentation/write` | JSDoc, inline comments, usage examples |
| `naming/write` | Naming conventions for variables, functions, files |

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Analyze Current State

1. **Parse Arguments**
   - Extract area path from $ARGUMENTS
   - Parse `--focus` flag (naming, structure, docs, all; default: all)
   - Determine if running as standalone or as part of composite (`--from-composite`)

2. **Pre-flight Check**
   - Run existing tests to confirm they all pass before refactoring
   - If any tests fail, reject with guidance to use `/coding:fix` first
   - Read files in the target area to understand current structure

3. **Identify Refactoring Opportunities**
   - Code structure improvements (extract functions, reduce complexity)
   - Readability enhancements (clearer variable names, better flow)
   - Naming convention violations
   - Missing or incomplete JSDoc documentation
   - Inline comment gaps for complex logic
   - Pattern inconsistencies with the rest of the codebase

### Step 2: Refactor Implementation

1. **Improve Code Structure**
   - Apply proper design patterns following standards
   - Reduce function complexity where possible
   - Extract reusable utilities and helpers
   - Ensure code follows all established patterns in the codebase
   - Run tests continuously to ensure no functionality is broken

2. **Enhance Readability**
   - Apply proper naming conventions per naming standards
   - Improve code flow and logical grouping
   - Simplify complex expressions
   - Remove dead code and unnecessary comments

### Step 3: Add Documentation

1. **Add JSDoc Comments**
   - Document all public functions, classes, and interfaces
   - Include parameter descriptions, return types, and behavior
   - Add `@example` blocks where appropriate
   - Follow documentation standards for format and content

2. **Add Inline Comments**
   - Explain complex algorithms and non-obvious logic
   - Document "why" decisions, not "what" the code does
   - Add TODO/FIXME markers for known limitations (if any)

### Step 4: Validate Quality

1. **Run Full Test Suite**
   - Execute all related tests to verify no regressions
   - Confirm coverage is maintained at expected levels

2. **Run Quality Checks**
   - Execute linting to ensure standards compliance
   - Run type checker to verify TypeScript correctness
   - Verify all quality gates pass

3. **Final Assessment**
   - Confirm refactoring improved code quality metrics
   - Verify documentation completeness
   - Ensure production readiness

### Step 5: Reporting

**Output Format**:

```
[OK/FAIL] Command: refactor $ARGUMENTS

## Summary
- Area: [path]
- Focus: [naming|structure|docs|all]
- Files refactored: [count]
- Documentation added: [count] JSDoc blocks
- Quality improvements: [list]

## Actions Taken
1. Refactored [N] files for [improvements]
2. Added [M] JSDoc documentation blocks
3. Applied naming convention fixes to [K] identifiers
4. Verified all tests still pass

## Quality Results
- Tests: PASS ([X] passing, [Y] coverage)
- Types: PASS ([N] errors)
- Lint: PASS ([N] warnings)

## Improvements Applied
- [file:line] - [improvement description]
- [file:line] - [improvement description]

## Next Steps
1. Review refactored code
2. Run full test suite
3. Commit with /coding:commit
```

## Examples

### Refactor All Aspects

```bash
/refactor "src/services/auth/"
# Improves structure, naming, and documentation
# Runs tests continuously to verify no regressions
```

### Focus on Documentation

```bash
/refactor "src/utils/" --focus=docs
# Adds JSDoc to all public functions
# Adds inline comments for complex logic
```

### Focus on Naming

```bash
/refactor "src/models/" --focus=naming
# Applies naming convention standards
# Renames variables, functions, and files
```

### Error Case

```bash
/refactor "src/broken-tests/"
# Error: 3 tests failing in target area
# Fix tests first with /coding:fix, then refactor
```
