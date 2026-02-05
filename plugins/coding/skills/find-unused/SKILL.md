---
name: find-unused
description: Identify commented-out code, unused symbols, and unused test helpers using LSP-based analysis. Use when cleaning up dead code, finding orphaned functions, or optimizing codebase size.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Glob, Grep, Task
argument-hint: [path/to/scan] [--exclude=pattern]
---

# Find Unused Code

Analyzes codebase to identify commented-out code blocks, unused exports, unused functions, and unused test helpers. Uses parallel analysis agents for comprehensive coverage.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Delete any code (read-only analysis)
- Modify files
- Run tests
- Create new files

**When to REJECT**:

- Path doesn't exist
- Request to delete code (suggest manual review)
- Binary or non-code files targeted

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Setup Analysis

1. **Parse Arguments**
   - Extract path from $ARGUMENTS (default: current directory)
   - Parse --exclude patterns
   - Validate path exists

2. **Discover Files**
   - Use Glob to find source files
   - Filter by exclude patterns
   - Group by file type

### Step 2: Parallel Analysis

Launch three parallel analysis agents:

1. **Commented Code Agent**
   - Find multi-line comment blocks
   - Identify commented-out code patterns
   - Distinguish from documentation
   - Report locations and context

2. **Unused Exports Agent**
   - Find all exports in codebase
   - Trace import references
   - Identify unreferenced exports
   - Check for dynamic imports

3. **Unused Test Helpers Agent**
   - Find test utility functions
   - Check usage across test files
   - Identify orphaned fixtures
   - Report unused mocks

### Step 3: Consolidate Results

1. **Merge Findings**
   - Combine agent reports
   - Remove duplicates
   - Categorize by severity

2. **Prioritize**
   - High: Unused exports (potential dead code)
   - Medium: Commented code blocks
   - Low: Unused test helpers

### Step 4: Reporting

**Output Format**:

```
[✅] Command: find-unused $ARGUMENTS

## Summary
- Path scanned: [path]
- Files analyzed: [count]
- Commented blocks: [count]
- Unused exports: [count]
- Unused test helpers: [count]

## Findings

### 🔴 Unused Exports (High Priority)
- [file:line] `exportName` - No references found
- [file:line] `exportName` - Only internal use

### 🟡 Commented Code Blocks (Medium Priority)
- [file:line] - [N] lines of commented code
- [file:line] - [N] lines of commented code

### 🟢 Unused Test Helpers (Low Priority)
- [file:line] `helperName` - No test references
- [file:line] `fixtureName` - Unused fixture

## Recommendations
1. Review unused exports for potential removal
2. Delete or restore commented code blocks
3. Clean up unused test helpers

## Next Steps
- Review findings manually
- Remove confirmed dead code
- Update tests if needed
```

## 📝 Examples

### Scan Entire Project

```bash
/find-unused
# Analyzes all code in current directory
```

### Scan Specific Directory

```bash
/find-unused "src/services/"
# Focuses analysis on services directory
```

### Exclude Patterns

```bash
/find-unused "src/" --exclude="*.test.ts"
# Excludes test files from analysis
```

### Error Case

```bash
/find-unused "nonexistent/"
# Error: Path 'nonexistent/' does not exist
# Suggestion: Check path with 'ls' or use '.' for current directory
```
