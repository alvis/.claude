---
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion

argument-hint: "[specifier] [--area=test|documentation|code-quality|security|style|all] [--format=yaml|json|markdown] [--verbose]"

description: Comprehensive code review with context-aware scope selection
---

# review

Performs comprehensive code review of specified files, directories, PRs, or patterns against established coding standards and best practices. This command intelligently adapts review scope based on context and delegates to specialized agents for thorough coverage across quality dimensions (test, documentation, code-quality, security, style).

The `<specifier>` can identify files through multiple methods: file paths, directory paths, glob patterns (`**/*.spec.ts`), package names (`@myapp/auth`), PR numbers (`PR#123`), git ranges (`HEAD~3..HEAD`), or be omitted for full codebase review.

The review output is designed to be consumed by the /fix-code command for automated issue resolution.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not modify or fix any code (use /fix-code for remediation)
- Does not run tests or builds (focuses on static analysis)
- Does not handle deployment or infrastructure reviews

**When to REJECT**:

- When asked to fix issues (redirect to /fix-code command)
- When specifier points to binary or non-code files exclusively
- When requesting review of external dependencies or node_modules

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Context Detection & Scope Selection

**Detect execution environment**:
- Check if CI/non-interactive mode (no user interaction available)
- Check if interactive mode (user can respond to prompts)

**Resolve specifier** (if provided):

The `<specifier>` argument identifies which files to review through multiple methods:

1. **File paths**: Direct path to specific file(s) - `src/auth/auth.service.ts`
2. **Directory paths**: Review all code files in directory - `src/api/`
3. **Glob patterns**: Pattern matching - `**/*.spec.ts`, `src/**/*.{ts,tsx}`
4. **Package names**: Find all imports/usage - `@myapp/auth`, `lodash`
5. **PR numbers**: Review PR changes - `PR#123`
6. **Git ranges**: Review commits - `HEAD~3..HEAD`
7. **Command output**: Dynamic file lists - `$(git diff --cached --name-only)`
8. **Omitted**: Review entire codebase or auto-detect from current context

**Determine default scope based on context**:

1. If `--area` parameter provided → Use specified scope(s)
2. If specifier includes test files (`**/*.spec.ts`, `**/*.test.ts`) → Default to `test` scope
3. If specifier includes documentation files (`**/*.md`, `**/README*`) → Default to `documentation` scope
4. If working in interactive mode and no clear context → Ask user via AskUserQuestion (multiSelect):
   - Options: test, documentation, code-quality, security, style, all
   - Default: all
5. If in CI mode and no scope specified → Default to `all`

### Step 2: Follow Review Workflow

Execute the review workflow (workflow:review) with the following parameters:
- Selected scopes from Step 1
- File specifier: Resolved specifier from Step 1
- Format: --format parameter (default: yaml)
- Verbose: --verbose flag

The review workflow will:
1. Discover and categorize files
2. Execute parallel reviews across selected scopes
3. Aggregate findings into REVIEW.md
4. Generate summary report

### Step 3: Reporting

**Output Format**:

**If CI/Non-Interactive Mode**:
```markdown
# Code Review Report

**Generated**: [timestamp]
**Review Scopes**: [scopes reviewed]
**Overall Status**: [PASS|PASS_WITH_SUGGESTIONS|REQUIRES_CHANGES|FAIL]

## Summary

- **Total Files Reviewed**: [N]
- **Total Issues Found**: [N]
  - Critical: [N]
  - High: [N]
  - Medium: [N]
  - Low: [N]

## Findings by File

[Full detailed findings with file:line references]

## Conclusion

[Overall assessment]
```

**If Interactive Mode**:
```
📊 Code Review Complete

✅ REVIEW.md generated successfully

📁 Files Reviewed: [N]
🔍 Total Issues: [N] (Critical: [N], High: [N], Medium: [N], Low: [N])

🎯 Issues by Scope:
  • test: [N] issues
  • code-quality: [N] issues
  • security: [N] issues
  • documentation: [N] issues
  • style: [N] issues

⚠️ Critical Actions Required:
1. [First critical issue - file:line]
2. [Second critical issue - file:line]

📄 Full details saved to: REVIEW.md
```

## 📝 Examples

### Context-Aware Review (Auto-Detect)

```bash
/review
# Detects current context:
#   - If in test files → Reviews test scope
#   - If in docs → Reviews documentation scope
#   - Otherwise → Asks user or defaults to all
```

### Single Scope Review

```bash
/review --area=test
# Reviews only test quality, coverage, and complexity
# Delegates to Testing Quality Analyst
```

### Multiple Scope Review

```bash
/review "src/api/" --area=security,code-quality
# Reviews API directory for security vulnerabilities and code quality
# Runs security and code-quality analysts in parallel
```

### Pattern-Based Review

```bash
/review "src/api/**/*.spec.ts" --area=test
# Reviews only API test files using glob pattern
# Limits file discovery to specified pattern
```

### Pull Request Review

```bash
/review "PR#123" --area=all
# Reviews all files changed in pull request 123
# Comprehensive review across all quality dimensions
```

### Directory Review with Verbose Output

```bash
/review "src/auth/" --verbose --format=markdown
# Reviews authentication directory with detailed explanations
# Outputs in human-readable markdown format
```

### Package-Based Review

```bash
/review "@myapp/auth" --area=security,code-quality
# Reviews all files that import/use the auth package
# Focuses on security and code quality in auth-related code
```

### CI Mode Example

```bash
/review --area=all --format=markdown
# In CI environment:
#   - Outputs full REVIEW.md content to console
#   - No interactive prompts
#   - Exits with non-zero code if critical issues found
```

### Interactive Mode Example

```bash
/review "src/"
# In interactive environment:
#   - May prompt for scope selection if unclear
#   - Outputs summary to console
#   - Writes full details to REVIEW.md file
#   - User-friendly formatting
```

### Glob Pattern Review

```bash
/review "src/services/**/auth*.ts" --area=security
# Reviews only auth-related files within services directory
# Focuses on security vulnerabilities using glob pattern
```

### Documentation Review

```bash
/review "src/**/*.ts" --area=documentation
# Reviews JSDoc/TSDoc coverage in all TypeScript source files
# Identifies missing or incomplete documentation
```

### Git-Based Review

```bash
/review "HEAD~3..HEAD" --area=all
# Reviews changes in last 3 commits
# Comprehensive analysis of recent changes
```

### Pre-Commit Review

```bash
/review "$(git diff --cached --name-only)" --area=test,code-quality
# Reviews only staged files
# Perfect for pre-commit hook integration
# Focuses on test and code quality
```

### Multiple File Types Review

```bash
/review "**/*.{ts,tsx,js,jsx}" --area=code-quality,style
# Reviews all TypeScript and JavaScript files
# Focuses on code quality and style compliance
```

### Format Options

```bash
/review "src/" --format=yaml  # Machine-readable YAML for /fix-code
/review "src/" --format=json  # JSON format for CI/CD integration
/review "src/" --format=markdown  # Human-readable for PR comments
```

### Error Handling

```bash
/review "nonexistent/path"
# Error: Path not found
# Suggestion: Check path exists with 'ls nonexistent/'
# Alternative: Use glob patterns like '/review "**/*"' or '/review' for full codebase

/review --area=invalid
# Error: Invalid scope 'invalid'
# Valid scopes: test, documentation, code-quality, security, style, all
# Example: /review --area=test,code-quality

/review "unknown-package"
# Warning: Package 'unknown-package' not found in imports
# Suggestion: Check package name or use file path instead
# Alternative: Use '/review "src/**/*"' to review source directory
```
