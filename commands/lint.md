---
allowed-tools: Bash, Task, Read, Glob, Edit, Grep

argument-hint: [specifier] - File path, directory, or pattern to lint

description: Apply coding standards and linting to specified code areas
---

# Linting

Apply documentation, TypeScript, and error-handling standards to ensure consistent code quality across the specified files.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- does not modify configuration files (tsconfig.json, eslintrc, etc.)
- does not install or update linting packages
- does not create new linting rules or configurations
- does not process binary files or non-code assets
- does not modify gitignored or vendor files

**When to REJECT:**

- target is a configuration file that shouldn't be linted
- no valid source files found in the specified area
- target is outside the project directory
- files are already fully compliant with all standards

## 📊 Dynamic Context

- **[IMPORTANT]** At the start of the command, you MUST run the command to load all the context below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Working directory: !`pwd`
- Modified files: !`git diff --name-only`

### Project Context

- Workflows: !`find ~/.claude/constitutions/workflows "$(git rev-parse --show-toplevel)/constitutions/workflows" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`
- Standards: !`find ~/.claude/constitutions/standards "$(git rev-parse --show-toplevel)/constitutions/standards" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Follow Linting Workflow

- Execute @../constitutions/workflows/quality/lint.md

### Step 2: Reporting

**Output Format:**

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Files modified: [count]
- Standards compliance: [PASS/FAIL]
- Linting status: [all_pass/some_fail]

## Actions Taken
1. Added/updated JSDoc comments in [X] files
2. Reordered functions in [Y] files  
3. Standardized error messages in [Z] files
4. Fixed logging formats in [W] files

## Workflows Applied
- Linting workflow: [Status]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## 📝 Examples

### Simple Usage

```bash
/linting "src/utils/helper.ts"
# applies standards and linting to a single file
```

### Complex Usage with Directory

```bash
/linting "src/components/"
# processes all TypeScript and JavaScript files in the components directory
```

### Pattern-Based Linting

```bash
/linting "**/*.test.ts"
# lints all test files across the entire project
```

### Current Directory

```bash
/linting "."
# lints all source files in the current directory and subdirectories
```

### Error Case Handling

```bash
/linting "node_modules/"
# Error: Cannot lint vendor/dependency files
# Suggestion: Target source code directories instead
# Alternative: Use '/linting "src/"' for source files
```

### Large-Scale Processing

```bash
/linting "src/"
# Automatically delegates to multiple subagents:
#   - Agent A: Handles src/components (20 files)
#   - Agent B: Handles src/utils (15 files) (parallel)
#   - Agent C: Handles src/services (18 files) (parallel)
#   - Summary Agent: Compiles results after all complete
```
