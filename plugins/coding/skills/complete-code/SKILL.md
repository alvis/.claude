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

Completes all TODO-marked code in the specified area using a test-first approach. Scans for TODO, FIXME, and HACK comments, then implements the missing functionality while ensuring tests pass.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Create new features not mentioned in TODOs
- Refactor existing working code
- Modify configuration files
- Change project architecture

**When to REJECT**:

- No TODOs found in specified area
- Area path is invalid
- TODOs require external dependencies not installed
- TODOs involve security-sensitive operations without clear requirements

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Discovery

1. **Scan for TODOs**
   - Use Grep to find TODO, FIXME, HACK comments
   - Parse area argument from $ARGUMENTS
   - Classify by type and priority

2. **Analyze Dependencies**
   - Read files containing TODOs
   - Identify related test files
   - Map implementation dependencies

3. **Plan Completion Order**
   - Prioritize by dependency order
   - Group related TODOs
   - Estimate complexity

### Step 2: Test-First Implementation

1. **For Each TODO Group**:
   - Read existing tests
   - Write failing tests for missing functionality
   - Implement code to pass tests
   - Verify all tests pass

2. **Handle --test-only Flag**:
   - If set, only write tests without implementation
   - Mark implementation as ready for next phase

### Step 3: Validation

1. **Run Test Suite**
   - Execute all related tests
   - Verify 100% coverage for new code
   - Check for regressions

2. **Code Quality**
   - Run linting
   - Run type checking
   - Verify coding standards

### Step 4: Reporting

**Output Format**:

```
[✅/❌] Command: complete-code $ARGUMENTS

## Summary
- Area: [path]
- TODOs found: [count]
- TODOs completed: [count]
- Tests added: [count]
- Coverage: [percentage]

## Actions Taken
1. Discovered [N] TODOs in [area]
2. Created [M] tests
3. Implemented [K] functions
4. Verified all tests pass

## Completed TODOs
- [file:line] - [description]
- [file:line] - [description]

## Remaining TODOs (if any)
- [file:line] - [reason not completed]

## Next Steps
1. Review implementations
2. Run full test suite
3. Update documentation if needed
```

## 📝 Examples

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
