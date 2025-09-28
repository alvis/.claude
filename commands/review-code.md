---
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch

argument-hint: <specifier> [--verbose] [--format=yaml|json|markdown]

description: Comprehensive code review against all standards and best practices
---

# review-code

Performs comprehensive code review of specified files, directories, PRs, or patterns against all established coding standards and best practices. This command delegates to 4 parallel specialist agents to ensure thorough coverage across quality, testing, documentation, and security domains.

The review output is designed to be consumed by the fix-code command for automated issue resolution.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Does not modify or fix any code (use fix-code for remediation)
- Does not run tests or builds (focuses on static analysis)
- Does not handle deployment or infrastructure reviews

**When to REJECT:**

- When asked to fix issues (redirect to fix-code command)
- When specifier points to binary or non-code files exclusively
- When requesting review of external dependencies or node_modules

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

### Step 1: Follow Code Review Workflow

- Execute @constitutions/workflows/quality/review-code.md

### Step 2: Reporting

**Output Format:**

```yaml
code_review:
  review_type: "[files|directory|pr|pattern]"
  identifier: "$ARGUMENTS"
  status: "[pass|requires_changes|fail]"
  
  critical_issues:
    - category: "security|quality|testing|documentation"
      description: "Detailed description of the issue"
      file: "path/to/file"
      line: 123  # if applicable
      recommendation: "Specific fix instruction"
      
  major_issues:
    - category: "security|quality|testing|documentation"
      description: "Detailed description of the issue"
      file: "path/to/file"
      line: 45   # if applicable
      recommendation: "Specific fix instruction"
      
  minor_issues:
    - category: "security|quality|testing|documentation"
      description: "Minor improvement needed"
      file: "path/to/file"
      recommendation: "Improvement suggestion"
      
  suggestions:
    - category: "performance|maintainability|style"
      description: "Optional enhancement"
      file: "path/to/file"
      recommendation: "Enhancement details"
      
  metrics:
    test_coverage: "85%"
    documentation_coverage: "92%"
    complexity_score: "A"
    security_score: "A-"
    files_reviewed: 12
    issues_found: 6
    
  agent_reports:
    code_quality:
      status: "[pass|warning|fail]"
      issues_found: 3
    testing:
      status: "[pass|warning|fail]"  
      issues_found: 1
    documentation:
      status: "[pass|warning|fail]"
      issues_found: 2
    security:
      status: "[pass|warning|fail]"
      issues_found: 0
```

## 📝 Examples

### Single File Review

```bash
/review-code "src/components/Button.tsx"
# Reviews specific file against all standards
# Output: YAML report with file-specific issues
```

### Directory Review

```bash
/review-code "src/api/" --verbose
# Reviews all code files in api directory
# Verbose output includes detailed explanations
```

### Pull Request Review

```bash
/review-code "PR#123"
# Reviews all files changed in pull request 123
# Automatically detects changed files from git diff
```

### Pattern-Based Review

```bash
/review-code "**/*.test.ts" --format=json
# Reviews all test files matching pattern
# Output in JSON format for integration
```

### Comprehensive Review

```bash
/review-code "." --verbose
# Reviews entire codebase
# Delegates to 4 parallel agents:
#   - Code Quality Agent: Standards compliance, complexity
#   - Testing Agent: Coverage analysis, test quality  
#   - Documentation Agent: JSDoc, comments, README
#   - Security Agent: Vulnerabilities, best practices
```

### Git-Based Review

```bash
/review-code "HEAD~3..HEAD"
# Reviews changes in last 3 commits
# Uses git diff to identify modified files
```

### Specific File Types

```bash
/review-code "src/**/*.{ts,tsx,js,jsx}"
# Reviews only TypeScript/JavaScript files
# Skips configuration and documentation files
```

### Pre-Commit Review

```bash
/review-code "$(git diff --cached --name-only)"
# Reviews only staged files
# Perfect for pre-commit hook integration
```

### Format Options

```bash
/review-code "src/" --format=markdown
# Outputs human-readable markdown report
# Useful for documentation or PR comments

/review-code "src/" --format=yaml  # default
# Machine-readable YAML for fix-code consumption

/review-code "src/" --format=json
# JSON format for CI/CD integration
```

### Error Handling

```bash
/review-code "nonexistent/path"
# Error: Path not found
# Suggestion: Check path exists with 'ls nonexistent/'
# Alternative: Use glob patterns like '/review-code "**/*"'

/review-code "*.pdf"
# Warning: No code files found in selection
# Suggestion: Use code file patterns like '*.ts' or '*.js'
```