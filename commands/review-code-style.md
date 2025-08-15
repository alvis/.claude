---
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task
argument-hint: [specific-file] [--fix] [--all] [--standard=name]
description: Checks and auto-fixes code style issues in staged/modified files using project standards
---

# Check Code Style

Automatically checks and corrects code style issues in modified files according to project coding standards. Uses $ARGUMENTS to target specific files or apply additional options.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Modify committed files (only staged/unstaged)
- Fix complex refactoring issues
- Change application logic
- Modify test files unless explicitly included
- Update dependencies or configurations

**When to REJECT:**

- No modified files to check
- Build is currently failing for non-style reasons
- Uncommitted merge conflicts exist
- Working on a protected branch

## 📊 Dynamic Context

### System State

- Current branch: !`git branch --show-current`
- Modified files: !`git diff --name-only`
- Staged files: !`git diff --cached --name-only`
- TypeScript files: !`git diff --name-only --diff-filter=ACMR | grep -E '\.(ts|tsx)$' | head -10 || echo "None"`

### Project Context

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`

## 🔄 Workflow

### Phase 1: Planning

0. **Context Retrieval**
   - Retrieve and print all context defined in "Dynamic Context" section

1. **Analyze Requirements**
   - Parse $ARGUMENTS for specific files or options
   - Identify target files (staged/unstaged/specific)
   - Determine fix vs report-only mode

2. **File Selection**:
   - Get list of staged files
   - Get list of unstaged files
   - Filter for code files (`.ts`, `.tsx`, `.js`, `.jsx`)
   - If more than 10 files, batch grouping them according to their project than file types (e.g. react vs ordinary typescript file) and project type (e.g. backend vs frontend), 10 files max per group
   - IMPORTANT: DO NOT READ the files, infer the file content by its path only

3. **Script Selection**:
   - Identify the relevant project meta files such as the project's package.json and monorepo's package.json
   - Determine the most relevant linging scripts defined in the meta files to each file group (perfer project script over monorepo script)
   - IMPORTANT: DO NOT READ any config files (e.g. eslint.config.ts)

4. **Identify Applicable Workflows & Standards**
   - IMPORTANT: From the project context, by file names (not content), determine which code review related workflows and standards to follow

5. **Delegation**
   - Identify the subagents which can perform the main quality check task
   - Identify any supporting test runner agent
   - For each batch group, identify the relevant workflows, standards, and scripts.

### Phase 2: Execution

1. **Primary Implementation**:
   - Launch the most suitable agents in parallel to review each batch group with the following input
     - IMPORTANT: The workflow and standards to follow
     - Scripts can be used to assist the check
     - Whether the agent should auto fix any issues
     - List of files to check

2. **Standards Enforcement**:
   - Run linting checks on the specified files
   - Capture outputs for reporting

3. **Edge Case Handling**
   - Auto fix files with syntax errors gracefully
   - Skip binary or generated files
   - Preserve intentional style exceptions

### Phase 3: Verification

1. **Automated Testing**
   - Run the linting script defined in the project to check all files
   - Check affected test files still pass
   - If failing, request an agent to correct the issues found

2. **Quality Assurance**
   - Confirm all issues resolved
   - Validate formatting consistency

3. **Side Effect Validation**
   - Ensure no logic changes introduced
   - Verify imports still resolve
   - Check no unintended file modifications

### Phase 4: Reporting

**Output Format**

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Files modified: [count]
- Auto-fixes applied: [count]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Workflows Applied
- Code Review Workflow: [Status]
- TypeScript Standards: [Status]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]

## Next Steps (if applicable)
- [Required manual action]
- [Recommended follow-up]
```

## 📝 Examples

### Check All Modified Files

```bash
/review-code-style
# Checks and auto-fixes all staged and unstaged files
```

### Check Specific File

```bash
/review-code-style "src/components/Button.tsx"
# Checks only the specified file
```

### Report Only Mode

```bash
/review-code-style --report-only
# Shows issues without applying fixes
```

### Fix All Including Tests

```bash
/review-code-style --all --include-tests
# Includes test files in style checking
```

### Delegation Example

```bash
/review-code-style
# Automatically delegates to:
#   - marcus-williams-code-quality: Comprehensive style review
#   - test-runner: Validation after fixes (if needed)
```

### Error Case Handling

```bash
/review-code-style "non-existent.ts"
# Error: File not found
# Suggestion: Check available files with 'git status'
# Alternative: Use '/review-code-style' without arguments for all modified files
```

### With Specific Standards

```bash
/review-code-style --standard="strict-typescript"
# Applies stricter TypeScript checking rules
```
