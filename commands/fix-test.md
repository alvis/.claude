---
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task, TodoWrite

argument-hint: [test specifier] [--changes=description of specific changes needed]

description: Fix issues in test files and ensure standards compliance
---

# Fix Test

Fixes issues in test files including incorrect behavior, standards violations, type safety problems, and other test-related issues while preserving test intent and correctness. Focuses on fixing test behavior rather than making tests pass.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Modify source code under test to make failing tests pass  
- Create new tests from scratch
- Run test suites for general health checks
- Modify non-test files or production code

**When to REJECT:**

- Request asks to modify source code to fix failing tests
- User wants to create entirely new test files
- Request is about running tests rather than fixing existing test code
- Changes would compromise test correctness or intent

## 📊 Dynamic Context

- **[IMPORTANT]** At the start of the command, you MUST run the command to load all the context below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`
- Modified files: !`git diff --name-only`
- Staged files: !`git diff --cached --name-only`

### Project Context

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Follow Fix Test Workflow

- Execute @constitutions/workflows/coding/fix-test.md

### Step 2: Reporting

**Output Format:**

```text
[✅/❌] Command: fix-test $ARGUMENTS

## Summary
- Files modified: [count]
- Issues fixed: [count]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Workflows Applied
- Fix Test Workflow: [Status]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## 📝 Examples

### Simple Usage

```bash
/fix-test "user.spec.ts"
# Fixes issues in specific test file with standards compliance
```

### Directory-based Usage

```bash
/fix-test "src/components/"
# Fixes issues in all test files within the components directory
```

### Complex Usage with Changes

```bash
/fix-test "auth.spec.ts" --changes="Fix mock implementation and update assertion logic"
# Fixes specific test file with targeted changes described
```

### Multiple Files Usage

```bash
/fix-test "*.spec.ts"
# Fixes issues in all test files matching the pattern
```

### Error Case Handling

```bash
/fix-test "nonexistent.spec.ts"
# Error: Test file not found
# Suggestion: Check available test files with 'find . -name "*.spec.ts"'
# Alternative: Use '/fix-test "src/"' to scan directory for test files
```

### Complex Directory Structure

```bash
/fix-test "src/services/" --changes="Update mocks to match new API interface"
# Fixes all test files in services directory with specific focus on mock updates
# Automatically delegates to:
#   - Agent A: Handles test files batch 1 (≤10 files)
#   - Agent B: Handles test files batch 2 (≤10 files)
#   - Agent C: Handles fixture/mock corrections (after test fixes complete)
```

### Standards Compliance Fix

```bash
/fix-test "integration/"
# Fixes all test files in integration directory for full standards compliance
# Applies testing, TypeScript, and documentation standards
# Discovers and applies additional relevant standards automatically
```
