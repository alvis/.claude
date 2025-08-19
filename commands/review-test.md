---
allowed-tools: "Bash, Read, Grep, Glob, LS, TodoWrite, Task"

argument-hint: "[test specifier]"

description: "systematically analyze test files for improvement opportunities without modification"
---

# Review Test

Reviews and analyzes test files to identify coverage gaps, complexity reduction opportunities, fixture/mock optimizations, and improvement recommendations for the fix-test workflow. Uses comprehensive read-only analysis across multiple dimensions to assess test suite quality without making any code modifications.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Modify any test files or test code
- Write new tests or fix existing tests
- Run tests or execute test suites
- Install dependencies or update test configurations
- Make changes to application code under test

**When to REJECT:**

- Request to fix or modify test code (use `/fix-test` instead)
- Request to create new tests (use `/create-test` instead)
- Request to run tests or check test results (use appropriate test runners)
- Request to modify application code based on test analysis
- Request to implement recommended changes (analysis only)

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

### Step 1: Follow Review Test Workflow

- Execute @constitutions/workflows/quality/review-test.md with test specifier: $ARGUMENTS

### Step 2: Reporting

**Output Format:**

```
[✅/❌] Command: review-test $ARGUMENTS

## Summary
- Test files analyzed: [count]
- Coverage gaps identified: [count]  
- Complexity issues found: [count]
- Fixture optimizations identified: [count]
- Standards compliance: [PASS/FAIL/PARTIAL]

## Analysis Results
### Coverage Gap Analysis
- [Specific coverage gap findings]
- [Line/branch coverage recommendations]

### Test Complexity Analysis  
- [Complex test structure findings]
- [Refactoring opportunities identified]

### Fixture & Mock Optimization
- [Duplicate fixture findings]
- [Mock consolidation opportunities]

## Priority Recommendations
### High Priority
1. [Critical coverage gaps needing immediate attention]
2. [Major complexity issues affecting maintainability]

### Medium Priority  
1. [Fixture consolidation opportunities]
2. [Minor complexity improvements]

### Low Priority
1. [Nice-to-have optimizations]

## Workflows Applied
- Review Test Workflow: [Status]

## Next Steps
- Use `/fix-test` command to implement these recommendations
- Run test suite after fixes to validate improvements
- Consider additional test coverage for identified gaps

## Issues Found (if any)
- **Issue**: [Description]
  **Recommendation**: [Analysis finding or suggestion]
```

## 📝 Examples

### Simple Usage

```bash
/review-test
# Analyzes entire test suite for improvement opportunities
# Provides comprehensive coverage, complexity, and fixture analysis
```

### Specific File Analysis

```bash
/review-test "src/components/UserProfile.spec.ts"
# Analyzes single test file for all improvement dimensions
# Focuses analysis on UserProfile component tests only
```

### Directory-Scoped Analysis

```bash
/review-test "src/services/"
# Analyzes all test files in services directory
# Provides service-layer specific test quality assessment
```

### Functionality-Based Analysis

```bash
/review-test "authentication"
# Finds and analyzes all tests related to authentication
# Searches for auth-related test files and components
```

### Complex Usage with Coverage Focus

```bash
/review-test "src/utils/validation.spec.ts"
# Provides detailed analysis of validation utility tests
# Identifies specific test cases needed for full coverage
# Recommends fixture optimizations for validation scenarios
```

### Delegation Example

```bash
/review-test "src/api/"
# Automatically delegates analysis to:
#   - Coverage Gap Analyst: Identifies missing test cases
#   - Test Complexity Analyst: Reviews test structure (parallel)
#   - Fixture & Mock Analyst: Finds optimization opportunities (parallel)
#   - Consolidation: Prioritizes all recommendations
```

### Error Case Handling

```bash
/review-test "nonexistent-test.spec.ts"
# Error: Test file not found
# Suggestion: Check available test files with 'find . -name "*.spec.ts"'
# Alternative: Use '/review-test' without arguments to analyze all tests
```

### With Full Suite Analysis

```bash
/review-test
# Comprehensive analysis of entire test suite
# Identifies cross-file fixture duplication
# Provides project-wide test quality assessment
# Generates prioritized improvement roadmap
```
