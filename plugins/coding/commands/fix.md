---
allowed-tools: Edit, MultiEdit, Read, Write, Grep, Glob, Bash, Task, TodoWrite

argument-hint: [specifier] [--area=AREA] [--note=...]

description: Fix code and test issues using intelligent area detection and workflow
---

# Fix

Fix code and test issues in specified files using intelligent area detection and the write-code workflow. Uses context from available project documentation, runs diagnostics, detects the type of fixes needed, and applies the appropriate workflow steps to resolve issues.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Create new features or functionality not related to fixing identified issues
- Modify code without understanding context and requirements
- Apply fixes that could break existing functionality without validation

**When to REJECT**:

- Specifier points to non-existent files or invalid patterns
- Conflicting area specifications that don't make sense together
- Request asks to create entirely new features rather than fix issues

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Context Discovery & Initial Diagnostics

#### Parse Specifier

**When specifier is provided:**

- Understand specifier type:
  - File paths: `src/components/Button.ts`
  - Glob patterns: `src/**/*.spec.ts`, `**/*.{ts,tsx}`
  - Package names: `@myapp/core`
  - Git references: `git diff`, `git diff HEAD~1`, `git diff main...HEAD`
  - Pull request: `pr` (uses current branch's changes)
  - Directories: `src/components/`
- Resolve specifier to concrete file list using Glob tool
- Validate that target files exist and are accessible

**When NO specifier is provided:**

1. **Locate Project Root:**
   - Search upward from current directory for project markers:
     - `package.json` (Node.js/TypeScript/JavaScript)
     - `Cargo.toml` (Rust)
     - `pyproject.toml` or `setup.py` (Python)
     - `go.mod` (Go)
     - `pom.xml` or `build.gradle` (Java/Kotlin)
     - Other language-specific project files
   - Use the directory containing the project file as root

2. **Detect Language and Infer File Patterns:**
   - Read project configuration file to determine language/stack
   - Auto-generate appropriate glob patterns based on detected language:

   **TypeScript/JavaScript (package.json):**
   - Source: `src/**/*.{ts,tsx,js,jsx}`, `lib/**/*.{ts,tsx,js,jsx}`
   - Tests: `**/*.spec.{ts,tsx,js,jsx}`, `**/*.test.{ts,tsx,js,jsx}`, `__tests__/**/*.{ts,tsx,js,jsx}`

   **Python (pyproject.toml, setup.py):**
   - Source: `**/*.py` (excluding `tests/`, `test_*.py`, `*_test.py`)
   - Tests: `tests/**/*.py`, `test_*.py`, `*_test.py`

   **Rust (Cargo.toml):**
   - Source: `src/**/*.rs`, `lib.rs`, `main.rs`
   - Tests: `tests/**/*.rs`

   **Go (go.mod):**
   - Source: `**/*.go` (excluding `*_test.go`)
   - Tests: `**/*_test.go`

   **Java/Kotlin (pom.xml, build.gradle):**
   - Source: `src/main/**/*.java`, `src/main/**/*.kt`
   - Tests: `src/test/**/*.java`, `src/test/**/*.kt`

3. **Resolve to Concrete File List:**
   - Apply inferred patterns using Glob tool
   - Combine source and test files into target list
   - Validate that files exist and are accessible

#### Discover Context and Handover Documentation

1. **Find All Markdown Files:**
   - Search project root for all markdown files: `**/*.md`
   - Exclude common non-context files: `node_modules/`, `README.md`, `CHANGELOG.md`, `LICENSE.md`

2. **Analyze Content to Identify Relevant Documents:**
   - Read each markdown file and analyze content for keywords/patterns:

   **Review/Findings Documents:**
   - Keywords: "review", "issues", "findings", "critical", "major", "minor", "violations"
   - Patterns: Issue lists, severity levels, file references with line numbers

   **Handover/Continuation Documents:**
   - Keywords: "handover", "takeover", "continuation", "work in progress", "WIP", "next steps"
   - Patterns: Task lists, pending work, blockers, decisions made

   **Context Documents:**
   - Keywords: "context", "current state", "progress", "status", "overview"
   - Patterns: Current implementation state, recent changes, decisions

   **Planning Documents:**
   - Keywords: "plan", "todo", "tasks", "implementation", "roadmap", "checklist"
   - Patterns: Numbered steps, task lists, requirements, milestones

   **Research/Investigation Documents:**
   - Keywords: "research", "investigation", "analysis", "findings", "options", "alternatives"
   - Patterns: Options compared, decisions rationale, technical investigations

3. **Extract Fix Requirements:**
   - From identified documents, extract:
     - Known issues and their locations (file paths, line numbers)
     - Required fixes and their priority/severity
     - Architectural constraints and requirements
     - Pending tasks related to discovered target files
     - Blockers or decisions that inform fix direction

4. **Prioritize Information:**
   - Recent documents (by modification time) have higher priority
   - Review findings take precedence for identifying what to fix
   - Handover notes provide critical context for work continuation
   - Multiple sources strengthen confidence in fix requirements

#### Run Initial Diagnostics

- Execute `get_project_overview` MCP tool to understand:
  - Current project state
- Execute `npx tsc --noEmit` to understand:
  - Compilation errors
  - Type checking issues
  - Overall code health
- Execute `npm run lint` to identify:
  - Linting violations
  - Code style issues
  - Potential bugs flagged by linter
- Collect diagnostic information:
  - Error types and locations
  - Warning patterns
  - Test failure information
  - Lint violation categories

### Step 2: Area Detection & Resolution Planning

#### Auto-Detect Area (if --area not provided)

Analyze diagnostics and context to determine what needs fixing:

1. **Check Test Status**:
   - If test failures found in specifier scope → include `test` area
   - If test files in specifier → include `test` area
   - Pattern: `*.spec.ts`, `*.spec.tsx`

2. **Check Lint Status**:
   - If lint errors found in specifier scope → include `lint` area
   - If lint warnings related to test files → include `test,lint`

3. **Check Context Files**:
   - If REVIEW.md exists:
     - Extract issue categories (critical, major, minor)
     - Map issues to areas (test issues → test, implementation issues → implementation)
   - If recent `/review` command detected → use same areas as review

4. **Check File Types**:
   - Test files (*.spec.ts,*.test.ts) → `test`
   - Fixture files (*.fixture.ts, fixtures/) → `fixtures`
   - Mock files (*.mock.ts, mocks/, **mocks**/) → `fixtures`
   - Implementation files (*.ts,*.tsx) → `implementation`

5. **Default Fallback**:
   - If no clear indicators → ask user to specify area
   - Provide detected issues to help user decide

#### Area to Workflow Step Mapping

Map detected/specified areas to write-code workflow steps:

- `test` → Resume From Step 3 (Fix Test Issues & Standards Compliance)
- `fixtures` → Resume From Step 4 (Optimize Test Structure & Fixtures)
- `implementation` → Resume From Step 2 (Implementation - Green Phase)
- `refactoring` → Resume From Step 5 (Refactoring & Documentation)
- `lint` → Applied throughout relevant steps
- Multiple areas → Start from earliest step, execute all relevant steps

#### Prepare Change Direction

Compile information from context discovery into Change Direction for workflow:

- Known issues from REVIEW.md
- Requirements from DESIGN.md and CONTEXT.md
- Specific fixes needed from diagnostics
- User-provided change description (if any)

### Step 3: Execute Write-Code Workflow

#### Workflow Configuration

Configure workflow:write-code execution with:

- **Resume From Step**: Determined by area mapping (earliest step if multiple areas)
- **Change Direction**: Compiled from context and diagnostics
- **Skip Steps**: Steps not needed based on area
  - Example: If area=test, skip Steps 0, 1, 2, 5
  - Example: If area=fixtures, skip Steps 0, 1, 2, 3, 5
  - Example: If area=implementation,test, skip Steps 0, 1, execute 2-3, skip 4-5

#### Delegate to Write-Code Workflow

<IMPORTANT>

**YOU MUST follow workflow:write-code to fix issues with subagents**

This command MUST NOT perform any fixes directly. Instead, you MUST:

1. **Delegate ALL fix execution to subagents** using the Task tool with workflow:write-code
2. **Follow workflow:write-code specifications exactly** as documented in the write-code workflow file
3. **Use the subagent orchestration patterns** specified in workflow:write-code:
   - Your role is orchestration and coordination ONLY
   - Subagents perform all actual fixing work
   - You analyze reports and make decisions
   - You NEVER execute fixes yourself

4. **Pass complete configuration** to the write-code workflow:
   - Feature Requirements: "Fix issues in [specifier]"
   - Implementation Scope: Concrete file list from specifier resolution
   - Resume From Step: Calculated step number based on area mapping
   - Change Direction: Compiled change information from context discovery
   - Skip Steps: Array of steps not needed for the detected areas

5. **Monitor and coordinate** workflow execution:
   - Receive reports from subagents executing write-code workflow
   - Make go/no-go decisions based on subagent reports
   - Handle failures by re-delegating with updated instructions
   - NEVER perform fixes directly even if subagents report issues

This ensures consistent quality, proper standards application, and adherence to established workflows.

</IMPORTANT>

Execute workflow:write-code using Task tool with all configuration parameters prepared in previous steps.

### Step 4: Validation & Reporting

#### Run Final Validation

After workflow completion:

1. **Execute Diagnostics**:
   - Run `lsp_get_diagnostics` or `ide__getDiagnostics` MCP tool
   - Run `npx tsc --noEmit` to verify type checking
   - Run `npm run lint` to verify linting compliance
   - Run `npm run test` to verify all tests pass

2. **Verify Fixes Applied**:
   - Compare initial diagnostics with final diagnostics
   - Confirm issues identified in Step 1 are resolved
   - Check that no new issues were introduced

3. **Check Context File Updates**:
   - If REVIEW.md existed, verify issues addressed
   - If PLAN.md existed, verify tasks completed
   - Update CONTEXT.md if it exists

#### Reporting

Output Format:

```
[✅/❌] Command: fix $ARGUMENTS

## Summary
- Files processed: [count]
- Areas addressed: [list]
- Issues fixed: [count]
- Workflow steps executed: [list]
- Validation results: [PASS/FAIL]

## Context Discovery
- Context files found: [REVIEW.md, DESIGN.md, ...]
- Issues extracted: [count]
- Initial diagnostics: [summary]

## Area Detection
- Detection method: [auto/manual]
- Detected areas: [list]
- Workflow steps: [step numbers]
- Change direction: [summary]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Workflows Applied
- write-code (Steps X-Y): [Status]

## Validation Results
- Type checking: [PASS/FAIL with details]
- Linting: [PASS/FAIL with details]
- Tests: [PASS/FAIL with test results]
- Issue resolution: [verified fixes]

## Issues Requiring Manual Intervention (if any)
- **Issue**: [Description]
  **Reason**: [Why auto-fix wasn't possible]
  **Recommendation**: [Suggested manual fix]
```

## 📝 Examples

### Simple Test Fix

```bash
/fix "src/components/Button.spec.ts"
# Auto-detects area=test based on .spec.ts pattern
# Reads context files if present
# Runs diagnostics to understand issues
# Executes write-code Step 3 only
# Reports test fixes applied
```

### Fix from Git Diff

```bash
/fix "git diff"
# Gets changed files from git diff
# Auto-detects areas based on file types and diagnostics
# Reads REVIEW.md if present from recent review
# Applies appropriate workflow steps
# Validates all changes
```

### Fix with Specific Area

```bash
/fix "src/api/**/*.ts" --area=implementation,test
# Explicitly specifies areas to address
# Reads context files for requirements
# Executes write-code Steps 2-3
# Validates implementation and tests
# Reports comprehensive results
```

### Fix Entire Package

```bash
/fix "@myapp/auth" --area=test,fixtures,refactoring
# Resolves package to file paths
# Executes write-code Steps 3-5
# Optimizes tests, fixtures, and refactors
# Comprehensive validation
```

### Fix from PR Review

```bash
/fix "pr"
# Gets files changed in current PR/branch
# Reads REVIEW.md from review findings
# Auto-detects areas from review issues
# Applies fixes based on review feedback
# Validates against review criteria
```

### Complex Pattern with Context

```bash
/fix "src/{components,utils}/**/*.{ts,tsx}" --area=implementation,test,lint
# Processes multiple directories and file types
# Reads REVIEW.md, DESIGN.md, CONTEXT.md for direction
# Runs comprehensive diagnostics
# Executes write-code Steps 2-3 with lint focus
# Reports detailed fix results
```

### Auto-Discovery: TypeScript Project

```bash
/fix
# Discovers package.json → identifies TypeScript project
# Auto-generates patterns:
#   - Source: src/**/*.{ts,tsx}
#   - Tests: **/*.spec.{ts,tsx}, **/*.test.{ts,tsx}
# Scans all *.md files in project
# Finds and analyzes: code-review-2024-01-15.md
#   → Contains review findings with severity levels
#   → Extracts 12 critical issues, 8 major issues
# Runs initial diagnostics (tsc, lint)
# Auto-detects areas: implementation, test, lint
# Executes write-code workflow Steps 2-3
# Validates all fixes applied successfully
```

### Auto-Discovery: Python Project

```bash
/fix
# Discovers pyproject.toml → identifies Python project
# Auto-generates patterns:
#   - Source: **/*.py (excluding tests)
#   - Tests: tests/**/*.py, test_*.py
# Scans markdown files
# Finds: handover-jan-2024.md, technical-notes.md
#   → Extracts work-in-progress items
#   → Identifies 5 pending bug fixes with file locations
# Runs diagnostics (mypy, pylint)
# Auto-detects areas from diagnostics and docs
# Applies appropriate fixes
# Reports completion with test results
```

### Auto-Discovery: Rust Project

```bash
/fix
# Discovers Cargo.toml → identifies Rust project
# Auto-generates patterns:
#   - Source: src/**/*.rs, lib.rs, main.rs
#   - Tests: tests/**/*.rs
# Scans for context documents
# Finds: IMPLEMENTATION_STATUS.md
#   → Contains known compiler warnings
#   → Lists clippy suggestions
# Runs cargo check and cargo clippy
# Fixes identified issues
# Validates with cargo test
```

### Auto-Discovery: No Context Docs

```bash
/fix
# Discovers package.json → TypeScript project
# Auto-generates file patterns
# No context markdown files found
# Falls back to diagnostic-driven approach:
#   - Runs get_project_overview
#   - Executes tsc --noEmit
#   - Runs npm run lint
# Identifies issues from diagnostics alone
# Auto-detects areas based on error types
# Applies fixes
# Validates resolution
```

### Error Case: Ambiguous Area

```bash
/fix "src/mixed-changes/**/*.ts"
# Runs diagnostics and finds multiple issue types
# Cannot auto-detect area with confidence
# Prompts user: "Found test, implementation, and lint issues. Please specify --area:
#   /fix "src/mixed-changes/**/*.ts" --area=implementation,test
#   /fix "src/mixed-changes/**/*.ts" --area=test,lint
# Shows breakdown of detected issues to help user decide
```

### Context-Aware Fix

```bash
# After running /review command that created REVIEW.md
/fix "src/api" --area=implementation
# Reads REVIEW.md automatically
# Extracts specific issues for src/api
# Uses review findings as Change Direction
# Applies fixes targeting review issues
# Validates fixes resolve review concerns
```

### Integration Pattern

```bash
# Complete workflow:

# 1. Review code and save results
/review "src/services" --format=yaml --verbose

# 2. Fix identified issues (auto-detects from REVIEW.md)
/fix "src/services"
# Auto-detects areas from REVIEW.md issues
# Applies appropriate fixes
# Validates resolution

# 3. Commit changes
/coding:commit
```
