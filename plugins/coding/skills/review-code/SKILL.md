---
name: review-code
description: 'MUST RUN after implementing any code. Spawns review subagents (test, security, code-quality, docs, style) to audit against the plan, siblings, redundancy, and correctness. Triggers when: "review this code", "review my PR", "audit this file", "check the code quality", "review for security". Also use when: finishing an implementation, validating test coverage, pre-merge checks. Examples: "review src/auth", "review the pull request", "audit this module for security issues".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [specifier] [--area=test|documentation|code-quality|security|style|all]
enforcement: mandatory-post-implementation
orchestration: subagent-spawning
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

## 🛑 Core Review Mandates (apply to EVERY scope, EVERY mode)

These mandates override tone and brevity. Reviewers MUST enforce them on every file examined.

1. **Plan Adherence (MANDATORY)**: Treat the approved plan (PLAN.md, DRAFT.md, DESIGN.md, PR description, or linked spec) as the contract. For every changed file:
   - Map each change back to a specific planned item.
   - Flag any deviation, addition, or omission as a **drift** finding.
   - For each drift, require a documented justification (commit message, PR comment, or inline rationale). If no solid reason is present → severity **critical**. A "good reason" means: a constraint discovered during implementation, a correctness fix, or explicit user/reviewer approval — NOT convenience, scope creep, or "while I was here" cleanup.
   - If no plan exists, the reviewer MUST state this explicitly and treat the PR description / commit messages as the best-available contract.

2. **Redundancy is a Defect** (human-detectable only — linters handle the mechanical cases): Aggressively flag code that does not need to exist. Focus on what ESLint / knip / `tsc` CANNOT see:
   - Defensive checks for conditions that cannot occur (trust internal invariants).
   - Wrapper functions that add no behaviour over what they wrap.
   - Duplicate logic that could reuse an existing helper.
   - Comments that restate what well-named code already says.
   - Backwards-compat shims, feature flags, or fallbacks for hypothetical futures.
   - Over-generalised abstractions with a single caller.
   Every redundant construct is a finding — severity **high** minimum when in production paths. **DO NOT** flag dead branches, unused imports, unused exports, unused parameters, or unreachable code — the linter/knip step owns those.

3. **Sibling Consistency (MANDATORY)**: Before approving any function, class, method (including internal/private ones), or module, search the codebase for siblings serving a similar role — e.g. adapters, mappers, repositories, handlers, clients, formatters, validators. For each match, verify:
   - **Naming**: follows the same verb/noun convention as its siblings (`fetchX` vs `getX`, `toDTO` vs `serialize`).
   - **Parameter shape**: same argument order, same positional vs options-object style, same optional/required split.
   - **Return shape**: same envelope (raw vs `{ data, error }`, sync vs Promise, throwing vs Result).
   - **Logic flow**: same error-handling discipline, same logging posture, same retry/cache behaviour.
   Any divergence without documented justification → severity **high** (critical if it risks silent behavioural surprise in a shared interface like an adapter set). Consistency reduces cognitive load and bug surface — treat new outliers as defects.

4. **Zero Tolerance for Semantic Error**: Treat the code as production-critical. There is NO room for:
   - Incorrect control flow, off-by-ones, wrong operators, swapped arguments.
   - Silent failure modes (swallowed errors, ignored return values).
   - Race conditions, unhandled async rejections, leaked resources.
   - Missing validation at system boundaries (user input, external APIs).
   - Logic that merely *looks* right — reviewers must trace it and prove it.
   Every plausible failure path must be called out. "Probably fine" is not acceptable.

5. **Delegate Mechanical Checks to Tooling**: Reviewers MUST NOT spend effort on anything a linter, compiler, or static analyzer already enforces. Assume `npm run lint`, `tsc --noEmit`, and `knip` run in the pipeline. SKIP these entirely:
   - Type mismatches, missing annotations, unknown properties, signature violations (→ `tsc`).
   - Unused imports, unused variables/exports, unreachable code, dead branches (→ ESLint / knip).
   - Formatting, quote style, semicolons, import ordering (→ Prettier / ESLint).
   Focus human-review bandwidth on semantics, intent, plan fidelity, sibling consistency, and non-mechanical redundancy.

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
     - **Core Review Mandates** (plan adherence, non-mechanical redundancy, sibling consistency across adapters/mappers/etc., zero-tolerance semantics, delegate mechanical checks to lint/tsc/knip) — see top of skill
     - Path to the approved plan document (PLAN.md/DRAFT.md/DESIGN.md/PR description) for drift checking
     - File paths to analyze (NOT file contents)
     - Standard file paths to consult (e.g., `/absolute/path/to/standards/testing.md`)
     - Expected report format (YAML with findings, metrics, context_level, plan_drifts)
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

You are a **Review Orchestrator**. You coordinate code review to improve both the code and the system. You never modify code directly, only delegate analysis and consolidate learning. Your approach emphasizes:

- **Strategic Delegation**: Assign review with clear mission, constraints, success metrics
- **Parallel Coordination**: Run specialized agents autonomously and simultaneously
- **Learning Orientation**: Consolidate findings into REVIEW.md plus systemic improvements
- **Visible Reasoning**: Reviewers explain why issues matter, not just what's wrong
- **Truth Over Ego**: Findings are data for system upgrades, not criticism
- **Scope Management**: Adapt depth based on user-selected areas of focus

#### Standards Applied

The review skill applies the following standards (all references use format `standard:<name>`):

| Scope | Standards |
|-------|-----------|
| All scopes (baseline) | `code-review`, `universal/scan` |
| test | `testing/scan` |
| documentation | `documentation/scan` |
| code-quality | `code-review`, `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan` |
| security | `universal/scan`, `code-review` |
| style | `typescript/scan`, `naming/scan` |

#### Phase 1: Planning (You)

**Context Detection & Scope Selection**: Use the same scope selection logic as Team Mode (Step 2A Phase 1) -- detect execution environment, resolve specifier, determine default scope, discover files, and categorize them by type.

**File filtering by scope**:

- test: test files + source files
- documentation: source + doc files + test files
- code-quality: source files + test files
- security: source files (especially auth/, api/, services/)
- style: source + test files

Prepare file lists for each selected scope.

#### Phase 2: Execution (Subagents via Task Tool)

Dispatch up to 5 scope review tasks in parallel using the Task tool, one for each selected scope.

- **All agents must operate in READ-ONLY mode** -- no code modifications
- **Agents must report issues with exact file:line references**, function names
- Each agent receives its scope-specific standards and file list

**For TEST Scope** (if selected):

Task tool with `subagent_type: "coding:ava-thompson-testing-evangelist"`

Prompt the agent as a **Testing Quality Analyst** performing comprehensive read-only test analysis. Include standards: `testing/scan`, `universal/scan`, `code-review`. The agent performs:

1. **Coverage Analysis**: Run coverage tools, identify uncovered lines/branches/statements, specify exact file:line locations, recommend specific test cases
2. **Test Quality Analysis**: Analyze structure and organization, identify complex setups, check arrange-act-assert patterns, find unnecessary or redundant tests
3. **Fixtures & Mocks Analysis**: Find duplicate fixture patterns, identify centralizable mocks, recommend consolidation strategies

Report format (YAML, <2000 tokens): `scope`, `status`, `summary`, `files_analyzed`, `findings` (each with `file`, `line`, `severity`, `category`, `issue`, `current_state`, `recommendation`), `metrics` (coverage_line, coverage_branch, coverage_statement, total_issues, critical_issues, high_issues).

**For DOCUMENTATION Scope** (if selected):

Task tool with `subagent_type: "general-purpose"`

Prompt the agent as a **Documentation Quality Analyst** performing read-only documentation review. Include standard: `documentation/scan`. The agent checks:

1. JSDoc/TSDoc completeness for all exported functions, classes, interfaces
2. Inline comments for complex logic
3. README accuracy and completeness
4. API documentation if applicable
5. Example usage and code samples
6. Type definitions documentation

Report format (YAML, <2000 tokens): `scope`, `status`, `summary`, `files_analyzed`, `findings` (each with `file`, `line`, `function`, `severity`, `category`, `issue`, `recommendation`), `metrics` (functions_documented, classes_documented, interfaces_documented, total_issues).

**For CODE-QUALITY Scope** (if selected):

Task tool with `subagent_type: "coding:marcus-williams-code-quality"`

Prompt the agent as a **Code Quality Analyst** performing read-only code quality review. The agent MUST apply the Core Review Mandates (Plan Adherence, Redundancy, Sibling Consistency, Zero Tolerance, Delegate Mechanical Checks) defined at the top of this skill. Include standards: `code-review`, `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan`. The agent performs:

0. **Plan Adherence Check (MANDATORY FIRST STEP)**: Locate the approved plan (PLAN.md, DRAFT.md, DESIGN.md, linked spec, or PR description). For each changed file, map every change to a planned item. Flag drifts (additions, deviations, omissions). For each drift, evaluate whether a solid documented justification exists (commit message, PR comment, inline rationale). Drift without justification → severity **critical**. Drift with weak justification (convenience, scope creep) → severity **high**. If no plan is available, state this and use PR description as best-available contract.
1. **Sibling Consistency Check (MANDATORY)**: For every function, class, method (INCLUDING internal/private members), and module, Grep the codebase for siblings of similar role (adapters, mappers, repositories, handlers, clients, formatters, validators, etc.). Compare naming conventions, parameter shape (order, options-object vs positional, optional/required split), return shape (envelope style, sync vs async, throw vs Result), and internal logic pattern (error handling, logging, retry/cache). Any unjustified divergence → severity **high** (**critical** for adapter-sets or other shared-interface families where inconsistency causes silent behavioural surprise).
2. **Non-Mechanical Redundancy**: Scan for redundancy that linters CANNOT detect — defensive checks for impossible conditions, wrapper functions with no added behaviour, duplicate logic ignoring an existing helper, comments restating code, backwards-compat shims, speculative fallbacks, over-generalised abstractions with a single caller. Every genuine redundancy is a finding (high+ in production paths). DO NOT flag dead branches, unused imports/exports, unreachable code — those belong to the `style` scope / linter.
3. **Semantic Correctness (Zero Tolerance)**: Trace every non-trivial control flow. Flag off-by-ones, swapped arguments, wrong operators, silent failures, swallowed errors, unhandled rejections, race conditions, leaked resources, missing boundary validation. "Probably fine" is not acceptable — prove correctness or flag it.
4. **Code Structure**: Organization, modularity, separation of concerns
5. **Naming Conventions**: Compliance with naming standards (beyond lint rules — domain-appropriate, sibling-aligned names)
6. **Complexity**: Functions/methods needing refactoring
7. **DRY Violations**: Code duplication (where linters miss the semantic overlap)
8. **Error Handling**: Error handling patterns and logging
9. **Performance**: Performance concerns
10. **Accessibility**: Accessibility issues (if applicable)
11. **Architecture**: Architectural patterns and design decisions

**DO NOT** re-check what tooling already enforces — skip type errors (→ `tsc`), unused imports/vars/exports, unreachable code, dead branches (→ ESLint / knip), and formatting (→ Prettier). The `style` scope and CI lint step own these. Spend bandwidth on semantics, intent, sibling fit, and plan fidelity.

Report format (YAML, <2000 tokens): `scope`, `status`, `summary`, `files_analyzed`, `typescript_project`, `plan_source` (path to plan doc or "none_found"), `plan_drifts_found`, `sibling_families_checked` (list of role families scanned, e.g. "adapters", "mappers"), `findings` (each with `file`, `line`, `severity`, `category` (include `plan-drift`, `sibling-inconsistency`, `redundancy`, `semantic-error` as valid categories), `issue`, `current_state`, `sibling_reference` (for consistency findings: file:line of the divergent sibling), `recommendation`, `plan_justification` (for drift findings: present/weak/missing)), `metrics` (complexity_score, duplication_percentage, plan_drifts, unjustified_drifts, sibling_inconsistencies, total_issues, critical_issues, high_issues).

**For SECURITY Scope** (if selected):

Task tool with `subagent_type: "coding:nina-petrov-security-champion"`

Prompt the agent as a **Security Analyst** performing read-only security review. Include standards: `universal/scan`, `code-review`. The agent checks:

1. **Injection Vulnerabilities**: SQL injection, XSS, command injection
2. **Authentication/Authorization**: Auth implementation review
3. **Input Validation**: Input sanitization and validation
4. **Sensitive Data**: Exposed secrets, logging sensitive data
5. **Dependencies**: Known vulnerabilities
6. **CORS & Headers**: Security headers configuration
7. **Crypto**: Proper encryption usage

Report format (YAML, <2000 tokens): `scope`, `status`, `summary`, `files_analyzed`, `findings` (each with `file`, `line`, `function`, `severity`, `category`, `issue`, `current_state`, `recommendation`, `attack_vector`), `metrics` (security_score, critical_vulnerabilities, high_vulnerabilities, total_issues).

**For STYLE Scope** (if selected):

Task tool with `subagent_type: "general-purpose"`

Prompt the agent as a **Style & Linting Analyst** performing read-only style review. Include standards: `typescript/scan`, `naming/scan`. The agent performs:

1. Identify project package.json files (project and monorepo levels)
2. Extract linting scripts (lint, lint:fix, eslint, prettier)
3. Execute linting scripts and capture output
4. Parse linter output for file:line references
5. Report all linting issues found
6. Check naming convention compliance

Report format (YAML, <2000 tokens): `scope`, `status`, `summary`, `files_analyzed`, `linting_scripts_executed`, `findings` (each with `file`, `line`, `severity`, `category`, `issue`, `rule`, `recommendation`), `metrics` (total_lint_errors, total_lint_warnings, naming_violations, total_issues).

#### Phase 3: Aggregation & Report Generation (You)

1. **Collect all reports** from Task tool executions. If any agent reports failure, log the issue and note incomplete analysis.
2. **Group findings by file path**. Within each file, sort by:
   - Primary: Line number (ascending)
   - Secondary: Severity (critical > high > medium > low)
   - Tertiary: Scope (test > code-quality > security > documentation > style)
3. **Calculate aggregate metrics**: total files reviewed, findings by severity, findings by scope, findings by category.
4. **Systemic Pattern Analysis**:
   - **Recurring Issues**: Identify patterns across files (e.g., "5 files lack input validation")
   - **Root Causes**: What systemic gaps allow these issues?
   - **Process Gaps**: Why did existing process not catch this?
   - **System Improvements**: Specific actions to prevent recurrence
   - **Learning Assets**: Document patterns for team reference
5. **Determine overall status**:
   - Any critical issues: **FAIL**
   - High issues but no critical: **REQUIRES_CHANGES**
   - Only medium/low issues: **PASS_WITH_SUGGESTIONS**
   - No issues: **PASS**
6. **Generate REVIEW.md** with findings grouped by file, sorted by line, including: summary metrics, findings by file (each with line, severity, scope, issue, current state, recommendation, impact, action required), systemic improvements section (patterns, root causes, process changes, learning assets), and conclusion.
7. **Write REVIEW.md** to project root or specified location.

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
/review-code --area=security
# Team mode:
#   - Creates review-team
#   - Spawns security-reviewer (nina-petrov-security-champion, opus)
#   - Single specialist performs thorough security analysis
#   - Reports context level for potential reuse
```

#### Multi-Scope Review with Cross-Review (Team Mode)

```bash
/review-code "src/api/" --area=security,code-quality
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
/review-code --area=test
# Reviews only test quality, coverage, and complexity
# Delegates to Testing Quality Analyst
```

### Multiple Scope Review

```bash
/review-code "src/api/" --area=security,code-quality
# Reviews API directory for security vulnerabilities and code quality
# Runs security and code-quality analysts in parallel
```

### Pattern-Based Review

```bash
/review-code "src/api/**/*.spec.ts" --area=test
# Reviews only API test files using glob pattern
# Limits file discovery to specified pattern
```

### Pull Request Review

```bash
/review-code "PR#123" --area=all
# Reviews all files changed in pull request 123
# Comprehensive review across all quality dimensions
```

### Directory Review with Verbose Output

```bash
/review-code "src/auth/" --verbose --format=markdown
# Reviews authentication directory with detailed explanations
# Outputs in human-readable markdown format
```

### Package-Based Review

```bash
/review-code "@myapp/auth" --area=security,code-quality
# Reviews all files that import/use the auth package
# Focuses on security and code quality in auth-related code
```

### CI Mode Example

```bash
/review-code --area=all --format=markdown
# In CI environment:
#   - Outputs full REVIEW.md content to console
#   - No interactive prompts
#   - Exits with non-zero code if critical issues found
```

### Interactive Mode Example

```bash
/review-code "src/"
# In interactive environment:
#   - May prompt for scope selection if unclear
#   - Outputs summary to console
#   - Writes full details to REVIEW.md file
#   - User-friendly formatting
```

### Glob Pattern Review

```bash
/review-code "src/services/**/auth*.ts" --area=security
# Reviews only auth-related files within services directory
# Focuses on security vulnerabilities using glob pattern
```

### Documentation Review

```bash
/review-code "src/**/*.ts" --area=documentation
# Reviews JSDoc/TSDoc coverage in all TypeScript source files
# Identifies missing or incomplete documentation
```

### Git-Based Review

```bash
/review-code "HEAD~3..HEAD" --area=all
# Reviews changes in last 3 commits
# Comprehensive analysis of recent changes
```

### Pre-Commit Review

```bash
/review-code "$(git diff --cached --name-only)" --area=test,code-quality
# Reviews only staged files
# Perfect for pre-commit hook integration
# Focuses on test and code quality
```

### Multiple File Types Review

```bash
/review-code "**/*.{ts,tsx,js,jsx}" --area=code-quality,style
# Reviews all TypeScript and JavaScript files
# Focuses on code quality and style compliance
```

### Format Options

```bash
/review-code "src/" --format=yaml  # Machine-readable YAML for /fix-code
/review-code "src/" --format=json  # JSON format for CI/CD integration
/review-code "src/" --format=markdown  # Human-readable for PR comments
```

### Team Mode Output Example

```bash
/review-code "src/api/" --area=all
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
/review-code "nonexistent/path"
# Error: Path not found
# Suggestion: Check path exists with 'ls nonexistent/'
# Alternative: Use glob patterns like '/review-code "**/*"' or '/review' for full codebase

/review-code --area=invalid
# Error: Invalid scope 'invalid'
# Valid scopes: test, documentation, code-quality, security, style, all
# Example: /review-code --area=test,code-quality

/review-code "unknown-package"
# Warning: Package 'unknown-package' not found in imports
# Suggestion: Check package name or use file path instead
# Alternative: Use '/review-code "src/**/*"' to review source directory
```
