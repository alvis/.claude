---
name: review
description: Comprehensive code review with context-aware scope selection. Use when reviewing pull requests, auditing code quality, checking security concerns, or validating test coverage.
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [specifier] [--area=test|documentation|code-quality|security|style|all]
---

# Code Review

Performs comprehensive code review of specified files, directories, PRs, or patterns against established coding standards and best practices. Intelligently adapts review scope based on context and delegates to specialized agents for thorough coverage.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not modify or fix any code (use /fix for remediation)
- Does not run tests or builds (focuses on static analysis)
- Does not handle deployment or infrastructure reviews

**When to REJECT**:

- When asked to fix issues (redirect to /fix command)
- When specifier points to binary or non-code files exclusively
- When requesting review of external dependencies or node_modules

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.

- **If present**: Use **Team Mode** (Step 2A)
- **If absent**: Use **Subagent Mode** (Step 2B)

### Step 2A: Team Mode (Agent Teams enabled)

#### Phase 1: Planning & Scope Selection (Lead)

**Context Detection & Scope Selection**:

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

**File Discovery**:

Use Glob/Grep to discover files matching the specifier. Categorize by type:

- Source: *.ts,*.tsx
- Tests: *.spec.ts,*.spec.tsx
- Docs: *.md, README
- Config: *.json,*.yaml

Filter files by selected scopes (pass file paths to teammates, not file contents).

#### Phase 2: Team Setup & Execution

1. **Create team**: `TeamCreate` with name `review-team`

2. **Initialize agent pool registry** tracking:
   - Name (agent identifier)
   - Role (reviewer type: test, security, code-quality, documentation, style)
   - Model (opus for specialized, haiku for general)
   - Context Level (%)
   - Status (working, idle, retired)

3. **Spawn specialized reviewer teammates** (one per selected scope):

   For each selected scope, spawn appropriate agent:

   - **test scope**: `Task` with `team_name="review-team"`, `name="test-reviewer"`, `subagent_type="coding:ava-thompson-testing-evangelist"`, `model="opus"`
   - **security scope**: `Task` with `team_name="review-team"`, `name="security-reviewer"`, `subagent_type="coding:nina-petrov-security-champion"`, `model="opus"`
   - **code-quality scope**: `Task` with `team_name="review-team"`, `name="quality-reviewer"`, `subagent_type="coding:marcus-williams-code-quality"`, `model="opus"`
   - **documentation scope**: `Task` with `team_name="review-team"`, `name="docs-reviewer"`, `subagent_type="general-purpose"`, `model="opus"`
   - **style scope**: `Task` with `team_name="review-team"`, `name="style-reviewer"`, `subagent_type="general-purpose"`, `model="opus"`

4. **Create review tasks**: `TaskCreate` for each scope with:
   - Subject: "Review [scope] (e.g., test, security)"
   - Description: Full instructions including:
     - File paths to analyze (NOT file contents)
     - Standard file paths to consult (e.g., `/absolute/path/to/standards/testing.md`)
     - Expected report format (YAML with findings, metrics, context_level)
     - Instruction to calculate and report `context_level` from token usage

5. **Assign ownership**: `TaskUpdate` to set owner for each task to corresponding reviewer

#### Phase 3: Review Cycle

1. **Wait for completion messages** from all reviewers via `SendMessage`

2. **Track context levels**: Each reviewer reports their `context_level` calculated as:
   - `context_level = (input_tokens / context_window_size) × 100`
   - Based on real token usage from conversation metadata

3. **Update agent pool registry** with reported context levels

4. **Collect review reports** via `TaskGet` for each completed task

5. **Optional: Cross-scope review round** (if multiple critical issues found):
   - Check agent pool for idle reviewers with `context_level < 50%`
   - If eligible reviewers exist → Reuse via `SendMessage` with cross-scope review task
   - If not → Spawn fresh reviewers with appropriate specialization
   - Task: Check for conflicts or interactions between scope findings
   - Wait for cross-review completion messages

#### Phase 4: Aggregation & Cleanup

1. **Aggregate findings**:
   - Group by file path
   - Sort by line number within each file
   - Calculate metrics across all scopes

2. **Generate REVIEW.md**:
   - Detailed findings by file
   - Summary metrics
   - Critical actions required
   - Systemic improvement recommendations
   - Agent lifecycle statistics (agents spawned, reused, retired)

3. **Shutdown teammates**:
   - Send `SendMessage` with type `shutdown_request` to all active teammates
   - Wait for shutdown confirmations

4. **Cleanup**: `TeamDelete` to remove team

5. **Report**:
   - Display summary to user
   - Note execution mode: team
   - Include agent lifecycle stats (spawned, reused, retired by context level)

#### Agent Summary

| Role | Agent Type | Model | Lifecycle |
|------|------------|-------|-----------|
| Test Reviewer | `coding:ava-thompson-testing-evangelist` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Security Reviewer | `coding:nina-petrov-security-champion` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Quality Reviewer | `coding:marcus-williams-code-quality` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Docs Reviewer | `general-purpose` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Style Reviewer | `general-purpose` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |

**Context-aware reuse policy**: Reviewers with reported `context_level < 50%` are eligible for reuse in optional cross-scope review rounds. Reviewers with `context_level >= 50%` are retired and replaced with fresh agents if additional review rounds are needed.

### Step 2B: Subagent Mode (fallback)

Execute workflows:review with the selected scopes and file specifier.

The workflow will perform subagent-based review as before.

### Step 3: Reporting

**Output Format** (both modes):

**Common fields**:

- Execution mode: [team|subagent]
- Review scopes: [list of scopes reviewed]
- Overall status: [PASS|PASS_WITH_SUGGESTIONS|REQUIRES_CHANGES|FAIL]
- Files reviewed: [N]
- Total issues: [N] by severity
- Issues by scope

**Team mode additional fields**:

- Agent lifecycle stats:
  - Total agents spawned: [N]
  - Agents reused: [N]
  - Agents retired: [N]
  - Average context level at completion: [X%]

**Output format**:

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

### Team Mode Examples (Agent Teams enabled)

#### Context-Aware Review with Team Coordination

```bash
/review
# Team mode behavior:
#   - Creates review-team
#   - Spawns specialized reviewers for all scopes in parallel
#   - Tracks context levels for potential reuse
#   - Aggregates findings from all teammates
#   - Reports agent lifecycle stats
```

#### Single Scope Review (Team Mode)

```bash
/review --area=security
# Team mode:
#   - Creates review-team
#   - Spawns security-reviewer (nina-petrov-security-champion, opus)
#   - Single specialist performs thorough security analysis
#   - Reports context level for potential reuse
```

#### Multi-Scope Review with Cross-Review (Team Mode)

```bash
/review "src/api/" --area=security,code-quality
# Team mode:
#   - Spawns security-reviewer and quality-reviewer in parallel
#   - Both analyze API directory independently
#   - If critical issues found, may trigger cross-scope review round
#   - Reuses low-context agents for cross-review if available
```

### Subagent Mode Examples (Fallback)

#### Context-Aware Review (Auto-Detect)

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

### Team Mode Output Example

```bash
/review "src/api/" --area=all
# Output (Team Mode):
#
# 📊 Code Review Complete (Team Mode)
#
# ✅ REVIEW.md generated successfully
#
# 📁 Files Reviewed: 42
# 🔍 Total Issues: 87 (Critical: 5, High: 15, Medium: 32, Low: 35)
#
# 🎯 Issues by Scope:
#   • test: 18 issues
#   • code-quality: 22 issues
#   • security: 12 issues
#   • documentation: 20 issues
#   • style: 15 issues
#
# 👥 Agent Lifecycle:
#   • Total agents spawned: 5
#   • Agents reused: 2 (for cross-scope review)
#   • Agents retired: 3 (context >= 50%)
#   • Average context level: 38%
#
# ⚠️ Critical Actions Required:
# 1. src/api/auth.controller.ts:89 - SQL injection vulnerability
# 2. src/api/users.controller.ts:145 - Sensitive data exposure
# 3. src/api/payments.controller.ts:203 - Missing input validation
#
# 📄 Full details saved to: REVIEW.md
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
