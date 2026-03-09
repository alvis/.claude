---
name: complete-code
description: Complete all TODO-marked code in specified area with test-first approach. Use when finishing incomplete implementations, converting TODO placeholders to working code, or completing test-driven development cycles.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task
argument-hint: <area> [--test-only]
---

# Complete Code Implementation

Completes all TODO-marked code in the specified area using a test-first approach (TDD Green Phase). Scans for TODO, FIXME, and HACK comments, then implements the missing functionality with minimal code to make tests pass. Corresponds to Step 2 (Implementation / Green Phase) of the TDD lifecycle.

## Purpose & Scope

**What this command does NOT do**:

- Create new features not mentioned in TODOs
- Refactor existing working code (use `/coding:refactor`)
- Modify configuration files
- Change project architecture

**When to REJECT**:

- No TODOs found in specified area
- Area path is invalid
- TODOs require external dependencies not installed
- TODOs involve security-sensitive operations without clear requirements

## Applicable Standards

When executing this skill, the following standards apply:

| Standard | Purpose |
|---|---|
| `documentation/write` | JSDoc and inline comments for new implementations |
| `function/write` | Function design, error handling, complexity |
| `observability/write` | Logging, metrics, and tracing for new code |
| `testing/write` | Test-first implementation, coverage requirements |
| `typescript/write` | Type safety, no `any`, proper generics |
| `universal/write` | General code authoring conventions |

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Discovery

1. **Scan for TODOs**
   - Use Grep to find TODO, FIXME, HACK comments in the area from $ARGUMENTS
   - Classify by type and priority
   - Determine if running as standalone or as part of composite (`--from-composite`)

2. **Analyze Dependencies**
   - Read files containing TODOs
   - Identify related test files
   - Map implementation dependencies

3. **Plan Completion Order**
   - Prioritize by dependency order
   - Group related TODOs
   - Estimate complexity

### Step 2: Test-First Implementation

Follow TDD Green Phase principles: write only enough code to make tests pass.

1. **For Each TODO Group**:
   - Read existing tests to understand expected behavior
   - Write failing tests for missing functionality (if tests do not exist yet)
   - Implement minimal code to pass tests
   - Replace TODO placeholders with simplest working implementation
   - Apply proper error handling per standards
   - Ensure type safety throughout
   - Run tests after each implementation increment to verify progress

2. **Handle --test-only Flag**:
   - If set, only write tests without implementation
   - Mark implementation as ready for next phase

3. **CODE DRAFTING PATTERNS** for any remaining incomplete sections:
   - Use `// TODO:` comments to mark sections still incomplete
   - For incomplete code where a return is expected:
     - Throw `new Error('IMPLEMENTATION: <description>')`
     - This prevents TypeScript type errors

### Step 3: Validation

1. **Run Test Suite**
   - Execute all related tests
   - Verify Green phase achievement (all tests passing)
   - Ensure no existing tests are broken
   - Confirm tests pass for correct reasons

2. **Code Quality**
   - Run linting via `npm run lint` or equivalent
   - Run type checking via `npx tsc --noEmit` or equivalent
   - Verify coding standards compliance

### Step 4: Reporting

**Output Format**:

```
[OK/FAIL] Command: complete-code $ARGUMENTS

## Summary
- Area: [path]
- TODOs found: [count]
- TODOs completed: [count]
- Tests added: [count]
- Tests passing: [count]

## Actions Taken
1. Discovered [N] TODOs in [area]
2. Created [M] tests
3. Implemented [K] functions
4. Verified all tests pass (Green phase)

## Completed TODOs
- [file:line] - [description]
- [file:line] - [description]

## Remaining TODOs (if any)
- [file:line] - [reason not completed]

## Validation Results
- Tests: PASS/FAIL ([X] passing, [Y] failing)
- Types: PASS/FAIL ([N] errors)
- Lint: PASS/FAIL ([N] warnings)

## Next Steps
1. Review implementations
2. Fix any remaining issues with /coding:fix
3. Refactor with /coding:refactor
```

## Examples

### Complete All TODOs in Area

```bash
/complete-code "src/services/"
# Finds and completes all TODOs in services directory
```

### Test-Only Mode

```bash
/complete-code "src/utils/" --test-only
# Only writes tests for TODOs, no implementation
```

### Single File

```bash
/complete-code "src/auth/login.ts"
# Completes TODOs in specific file
```

### Error Case

```bash
/complete-code "src/nonexistent/"
# Error: Path not found
# Suggestion: Check path exists with 'ls src/'
```
