---
allowed-tools: Task, Read, Grep, Glob, LS, TodoWrite
argument-hint: [--path=<directory-or-file>]
description: Update test files in batches to match testing standards using parallel subagents
---

# Update Test Files

Update test files in batch of 10 files (grouped by project, type of test, then file paths), use subagents running in parallel to ensure the test files are in the right format specified by the testing standard. Use the specified workflow to perform the update. Always start with fixture files, then mock files, then test files with optional --path=$ARGUMENTS to scope the update.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Modify non-test files (source code, configuration)
- Create new test files from scratch
- Delete existing test coverage
- Change test logic or assertions

**When to REJECT:**

- No test files found in specified path
- Test files already fully compliant
- Destructive changes requested
- Missing test standards documentation

## 📊 Dynamic Context

- **[IMPORTANT]** You must carefully remember all the context defined below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`

### Project Context

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`

## 🔄 Workflows

### Step 1: Follow Update Test Workflow

- Execute @constitions/workflows/coding/update-test.md

### Step 2: Reporting

**Output Format:**

```
[✅/❌] Command: update-test $ARGUMENTS

## Summary
- Test files updated: [count]
- Batches processed: [count]
- Standards compliance: [PASS/FAIL]
- Test results: [pass/total]

## Batch Results
### Fixtures ([count] files)
- Batch 1: [files] - [status]
- Batch 2: [files] - [status]

### Mocks ([count] files)
- Batch 1: [files] - [status]

### Tests ([count] files)
- Batch 1: [files] - [status]

## Standards Applied
- Testing Standard: [version]
- Update Workflow: coding/update-test.md

## Issues Found (if any)
- **File**: [path]
  **Issue**: [Description]
  **Fix**: [Applied fix]

## Next Steps
- Run full test suite to verify
- Review updated test files
- Commit changes if satisfied
```

## 📝 Examples

### Update All Tests in Current Directory

```bash
/update-test
# Finds all test files recursively
# Processes in batches of 10
# Updates to match testing standards
```

### Update Tests in Specific Directory

```bash
/update-test --path="src/components"
# Updates only component tests
# Maintains component test patterns
# Preserves existing coverage
```

### Update Single Project Tests

```bash
/update-test --path="packages/api"
# Focuses on API package tests
# Groups by test type (unit/integration)
# Applies API-specific test patterns
```

### Batch Processing Example

```bash
/update-test --path="spec"
# Found 35 test files:
#   - 5 fixture files → 1 batch
#   - 8 mock files → 1 batch  
#   - 22 test files → 3 batches
# Spawning 5 parallel subagents...
```

### Error Case Handling

```bash
/update-test --path="non-existent"
# Error: No test files found in path
# Suggestion: Check path or use --path="src" for source tests
```
