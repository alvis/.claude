---
allowed-tools: Edit, MultiEdit, Read, Write, Grep, Glob, Bash, Task, TodoWrite

argument-hint: [specifier] [--area=AREA]

description: Fix code and test issues using intelligent area detection and workflow
---

# Fix

Fix code and test issues in specified files using intelligent area detection and the write-code workflow. Automatically discovers context from documentation, runs diagnostics, detects the type of fixes needed, and applies the appropriate workflow steps to resolve issues.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Create new features or functionality not related to fixing identified issues
- Proceed without a specifier to identify target files
- Modify code without understanding context and requirements
- Apply fixes that could break existing functionality without validation

**When to REJECT**:

- No specifier provided for target code location
- Specifier points to non-existent files or invalid patterns
- Conflicting area specifications that don't make sense together
- Request asks to create entirely new features rather than fix issues

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Context Discovery & Initial Diagnostics

#### Parse Specifier

- Understand specifier type:
  - File paths: `src/components/Button.ts`
  - Glob patterns: `src/**/*.spec.ts`, `**/*.{ts,tsx}`
  - Package names: `@myapp/core`
  - Git references: `git diff`, `git diff HEAD~1`, `git diff main...HEAD`
  - Pull request: `pr` (uses current branch's changes)
  - Directories: `src/components/`
- Resolve specifier to concrete file list using Glob tool
- Validate that target files exist and are accessible

#### Read Context Files

- Check for and read if present (using Read tool):
  - REVIEW.md - Recent code review findings and issues
  - DESIGN.md - Design specifications and architectural direction
  - CONTEXT.md - Current work context and progress
  - PLAN.md - Implementation plan and pending tasks
  - RESEARCH.md - Research findings and decisions
- Extract relevant information:
  - Known issues and their locations
  - Required fixes and their priority
  - Architectural constraints
  - Pending tasks related to target files

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

### Error Case: No Specifier

```bash
/fix
# Error: Missing specifier parameter
# Suggestion: Provide target files, pattern, or git reference:
#   /fix "src/components/Button.ts"
#   /fix "git diff"
#   /fix "pr"
# Alternative: Use '/review' first to identify issues, then fix them
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
