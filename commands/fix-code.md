---
allowed-tools: Edit, MultiEdit, Read, Write, Grep, Glob, Bash, Task

argument-hint: <specifier> [--issues=<yaml-file-or-inline>]

description: Fix code issues identified by review-code command automatically
---

# Fix Code

Fix specified code based on issues identified by review-code command. This command systematically applies fixes for critical, major, and minor issues while maintaining code quality and running validation after each category of fixes.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Create new features or functionality not related to fixing identified issues
- Modify code without specific issues to address
- Proceed without both specifier and issues parameters
- Apply fixes that could break existing functionality without validation

**When to REJECT:**

- No specifier provided for target code location
- No issues provided from review-code output or YAML format
- Issues format doesn't match expected review-code YAML structure
- Specifier points to non-existent files or invalid paths

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

- Workflows: !`find ~/.claude/constitutions/workflows "$(git rev-parse --show-toplevel)/constitutions/workflows" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`
- Standards: !`find ~/.claude/constitutions/standards "$(git rev-parse --show-toplevel)/constitutions/standards" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Input Validation and Parsing

- **[CRITICAL]** Validate that both specifier and issues are provided
- If missing specifier: Stop and ask for target code location (file paths, directories, or glob patterns)
- If missing issues: Stop and ask for YAML issues from review-code output or file path
- Parse and validate YAML issues format matches review-code structure:
  ```yaml
  code_review:
    critical_issues: [...]
    major_issues: [...]
    minor_issues: [...]
    suggestions: [...]
  ```
- Verify specifier targets exist and are accessible
- Create backup of target files before starting fixes

### Step 2: Follow Write Code Workflow (Adapted for Fixing)

- Execute @constitutions/workflows/coding/write-code.md with fixing context:
  - Adapt TDD approach for fixing: Create tests for expected behavior after fixes
  - Focus implementation on addressing identified issues rather than new features
  - Ensure refactoring maintains existing functionality while resolving issues
  - Apply standards compliance as part of fixing process

### Step 3: Priority-Based Fix Application

- Apply fixes in priority order using Task delegation:
  1. **Critical Issues First**: Address security, compilation errors, runtime failures
  2. **Major Issues Second**: Fix logic errors, performance problems, maintainability issues
  3. **Minor Issues Third**: Address style violations, naming conventions, minor improvements
  4. **Suggestions Last**: Apply recommendations if time and scope allow

### Step 4: Continuous Validation and Testing

- Run validation after each priority category:
  - Execute linting and type checking using Bash
  - Run existing tests to ensure no regressions
  - Verify fixes actually resolve reported issues
  - Document fixes that couldn't be auto-applied

### Step 5: Reporting

**Output Format:**

```
[✅/❌] Command: fix-code $ARGUMENTS

## Summary
- Issues analyzed: [critical/major/minor/suggestions counts]
- Issues fixed: [count by priority]
- Issues requiring manual intervention: [count]
- Files modified: [count] 
- Validation results: [PASS/FAIL]

## Actions Taken
1. Critical issues fixed: [list with results]
2. Major issues fixed: [list with results]  
3. Minor issues fixed: [list with results]
4. Suggestions applied: [list with results]

## Workflows Applied
- constitutions/workflows/coding/write-code.md: [Status]

## Validation Results
- Linting: [PASS/FAIL with details]
- Type checking: [PASS/FAIL with details]
- Tests: [PASS/FAIL with test results]
- Issue resolution: [verified fixes]

## Issues Requiring Manual Intervention (if any)
- **Issue**: [Description from YAML]
  **Category**: [critical/major/minor/suggestion]  
  **Reason**: [Why auto-fix wasn't possible]
  **Recommendation**: [Suggested manual fix]
```

## 📝 Examples

### Direct Integration with review-code Output

```bash
/fix-code "src/components/**/*.ts" --issues="
code_review:
  critical_issues:
    - file: 'src/components/Button.ts'
      line: 15
      issue: 'Potential null pointer dereference'
      severity: 'critical'
  major_issues:
    - file: 'src/components/Modal.ts'  
      line: 42
      issue: 'Memory leak in event listener'
      severity: 'major'
  minor_issues:
    - file: 'src/components/Input.ts'
      line: 8
      issue: 'Variable name not following camelCase convention'
      severity: 'minor'
"
# Applies fixes in priority order: critical → major → minor
# Runs validation after each category
# Reports successful fixes and manual intervention needs
```

### Using Saved YAML File from review-code

```bash
/fix-code "src/utils" --issues="review-results.yaml"
# Reads YAML file from review-code output
# Processes all issues found in utils directory
# Maintains same priority-based fixing approach
```

### Single File Target with Inline Issues

```bash
/fix-code "src/auth/validator.ts" --issues="
code_review:
  critical_issues:
    - file: 'src/auth/validator.ts'
      line: 23
      issue: 'SQL injection vulnerability in user query'
      severity: 'critical'
      fix_suggestion: 'Use parameterized queries instead of string concatenation'
"
# Focuses fixes on single file
# Addresses critical security issue with suggested approach
```

### Error Case: Missing Required Parameters

```bash
/fix-code "src/components"
# Error: Missing --issues parameter
# Suggestion: Provide issues from review-code output:
#   /fix-code "src/components" --issues="review-output.yaml"
# Alternative: Use inline YAML format with --issues="yaml-content"
```

### Complex Multi-Priority Fix Session

```bash
/fix-code "**/*.{ts,tsx}" --issues="full-review.yaml"
# Processes entire TypeScript codebase
# Automatically delegates fixes by priority:
#   - Agent A: Critical security and compilation fixes
#   - Agent B: Major logic and performance fixes (after A completes)
#   - Agent C: Minor style and convention fixes (after B completes)  
#   - Agent D: Verification and final validation (after C completes)
```

### Integration Pattern with Saved review-code Session

```bash
# First: Review code and save results
/review-code "src/api" --output="api-review.yaml"

# Then: Apply fixes from saved results  
/fix-code "src/api" --issues="api-review.yaml"
# Uses previously identified issues
# Maintains traceability between review and fixes
# Allows for fix planning and preparation between steps
```