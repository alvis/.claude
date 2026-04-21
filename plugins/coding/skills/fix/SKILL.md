---
name: fix
description: 'Fix failing code, tests, lint, or type errors with auto area detection. Triggers when: "fix the bug", "fix this error", "fix failing tests", "fix the lint errors", "fix type errors". Also use when: resolving TypeScript complaints, addressing PR review feedback, repairing broken CI. Examples: "fix the bug in parseDate", "the tests are failing, fix them", "fix these eslint warnings".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Edit, MultiEdit, Read, Write, Grep, Glob, Bash, Task, TodoWrite
argument-hint: [specifier] [--area=AREA] [--note=...] [--plan=PATH]
---

# Fix Code Issues

Intelligently fixes code and test issues based on error messages, failing tests, or review feedback. Automatically detects the area of concern and applies the appropriate fix workflow. Corresponds to Steps 3-4 (Fix Test Issues + Optimize Test Structure) of the TDD lifecycle.

## Purpose & Scope

**What this command does NOT do**:

- Add new features
- Refactor working code (use `/coding:refactor`)
- Change architecture
- Create new files (unless needed for fixes)

**When to REJECT**:

- No errors or issues found
- Request is for new feature development
- Changes would break existing functionality
- Fix requires external service changes

## Applicable Standards

When executing this skill, the following standards apply:

### For Test Correction (Step 3 -- Fix Issues)

| Standard | Purpose |
|---|---|
| `testing/scan` | Test quality, patterns, coverage analysis |
| `typescript/scan` | Type safety verification |
| `documentation/scan` | Documentation completeness check |

When a specific rule violation is detected, load its fix guidance from `testing/rules/<rule-id>.md`.

### For Fixture Optimization (Step 4 -- Optimize)

| Standard | Purpose |
|---|---|
| `universal/write` | General code authoring conventions |
| `typescript/write` | TypeScript patterns and type safety |
| `function/write` | Function design and complexity |
| `documentation/write` | Documentation for test utilities |
| `testing/write` | Test fixture and mock patterns |

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Diagnose Issues

1. **Parse Arguments**
   - Extract specifier (file, directory, or pattern) from $ARGUMENTS
   - Parse `--area` flag (test, lint, type, review)
   - Parse `--note` for specific guidance
   - Determine if running as standalone or as part of composite (`--from-composite`)

2. **Auto-Detect Area** (if not specified)
   - Run tests to check for failures
   - Run linter to check for violations
   - Run type check for TypeScript errors
   - Prioritize: tests > types > lint

3. **Gather Error Context**
   - Collect error messages
   - Identify affected files
   - Map error to code location

4. **Capture Plan Context (Post-Review in Plan Mode)**

   When this skill runs **after a `/coding:review` in the same session** (i.e. the triggering input is a review report, the argument includes review findings, or the conversation shows a prior review invocation), the plan that `/review` validated against MUST be pinned into the fix context so a subsequent `/coding:review` can be re-run against the identical contract.

   - **Detect the trigger** (no dedicated flag needed — existing Step 1 rules already infer this): input references a review report, YAML findings from `/review`, or `--note="...review..."`; OR the prior turn ran `/coding:review`.
   - **Resolve the plan source** (first match wins):
     1. Explicit path passed via `--plan=<path>` — always wins when provided.
     2. The **active plan-mode plan file** surfaced by the Claude Code harness for the current session (path provided by the harness; typically under `~/.claude/plans/`). This is the authoritative source when the session is in — or has just exited — plan mode. Do NOT hardcode this path; read it from the harness-provided session context.
     3. The `plan_source` echoed by the preceding review report, if one is present.
     4. **Repo-level fallback (requires confirmation)**: if none of the above resolves but a repo-level plan doc is discoverable (`PLAN.md`, `DRAFT.md`, or `DESIGN.md` at repo root or scope directory), use `AskUserQuestion` to ask the user whether to adopt one of them (or none). Do **not** silently adopt a repo plan when there is no plan-mode plan — a stale repo doc may not match what `/review` actually validated against.
     5. If neither a plan-mode plan nor a confirmed repo plan is available → record `plan_source: none_found` and treat the review report itself as the best-available contract.
   - **Inject into context**: read the resolved plan document in full and treat it as a first-class input alongside the error context. Echo its absolute path and a one-line digest into every fix subtask prompt so downstream agents remain aligned with the same contract.
   - **Preserve across iterations**: the plan path MUST be carried into the Step 6 report under `plan_source` so the follow-up `/coding:review` can be invoked with the same `--plan` argument and produce comparable drift verdicts.

### Step 2: Plan Fixes

1. **Critical Root Cause Analysis**
   - Read affected files and their test descriptions
   - Determine expected behavior from test descriptions and specification files
   - Analyze whether issues are in source code logic vs. test implementation
   - Check DESIGN.md and specification files for expected behavior hints
   - If uncertain about expected behavior, ask user for clarification

2. **Create Fix Plan**
   - List changes needed
   - Order by dependency
   - Estimate impact

### Step 3: Apply Test Fixes

Fix issues in test files including incorrect behavior, standards violations, and test-related problems while preserving test intent and correctness.

1. **For Batch Execution** (when >25 files affected):
   - Generate batches at runtime based on test files found
   - Limit each batch to max 10 test files
   - Process batches in parallel

2. **Execute Test Corrections**
   - Apply code modifications to fix test issues
   - Fix incorrect test behavior and logic (never modify tests just to make them pass)
   - Fix standards violations
   - Update tests if needed
   - Fix imports and references
   - **CRITICAL**: Only modify test files, mock files, and fixture files -- NEVER modify source code under test

3. **Handle Unused Code Errors**
   - Check design documentation first to verify if code is part of planned functionality
   - Check handover documentation to see if this is intentional incomplete implementation
   - If code is planned but not yet implemented: use `throw new Error('IMPLEMENTATION: ...')` pattern
   - Only remove code that is genuinely unnecessary

4. **Iterate Until Passing**
   - Re-run checks after each fix
   - Address new errors that emerge
   - Continue until clean

### Step 4: Optimize Test Fixtures (Conditional)

Fix issues in test fixtures and mocks, ensuring proper structure and organization while maintaining correctness. **Skip this step if no fixtures/mocks exist**.

1. **Identify Fixture Issues**
   - Incorrect fixture definitions or mock behavior
   - Type safety issues in fixtures/mocks
   - Organizational problems
   - Standards violations in test support files

2. **Apply Fixture Corrections**
   - Fix fixture/mock behavior and accuracy
   - Ensure fixtures represent realistic and valid test data
   - Apply proper organization patterns
   - **CRITICAL**: Only modify test fixtures, mock files, and test support files

3. **Verify Fixtures**
   - Run tests to verify fixtures work correctly
   - Maintain test accuracy after changes

### Step 5: Validate

1. **Run Full Checks**
   - Execute test suite via `npm run test` or equivalent
   - Run linter via `npm run lint` or equivalent
   - Run type checker
   - Verify no regressions

2. **Error Anthropology** (when failures occurred)
   - Root Cause: Why did this specific error occur?
   - Systemic Cause: Why did the process allow this error?
   - Belief Update: What assumptions proved wrong?
   - System Improvement: How to prevent this class of error?

### Step 6: Reporting

**Output Format**:

```
[OK/FAIL] Command: fix $ARGUMENTS

## Summary
- Area: [detected or specified area]
- Issues found: [count]
- Issues fixed: [count]
- Files modified: [count]
- Plan source: [absolute path to PLAN.md/DRAFT.md/DESIGN.md, or `none_found`] <!-- present only when triggered post-review under plan mode; re-run `/coding:review --plan=<path>` to verify -->
- Review re-run command: `/coding:review <scope> --plan=<plan_source>` <!-- omit if plan_source is none_found -->>

## Root Cause Analysis
- Expected behavior: [description]
- Root cause: [source_code_logic|test_implementation|requirements_unclear]
- Reasoning: [how expected behavior was determined]

## Issues Resolved
1. [file:line] - [issue description]
   Fix: [what was changed]
2. [file:line] - [issue description]
   Fix: [what was changed]

## Fixture Optimizations (if applicable)
- Fixtures processed: [count]
- Issues fixed: [count]
- Organization improvements: [count]

## Validation Results
- Tests: [PASS/FAIL] ([X] passing, [Y] failing)
- Types: [PASS/FAIL] ([N] errors)
- Lint: [PASS/FAIL] ([N] warnings)

## Next Steps
1. Review changes
2. Run full test suite
3. Refactor with /coding:refactor
4. Commit with /coding:commit
```

## Examples

### Auto-Detect and Fix

```bash
/fix
# Automatically detects issues and fixes them
```

### Fix Specific Area

```bash
/fix --area=test
# Focuses only on fixing test failures
```

### Fix Specific File

```bash
/fix "src/auth/login.ts"
# Fixes issues in specific file
```

### Fix with Guidance

```bash
/fix --area=lint --note="Focus on unused variables"
# Fixes lint issues with specific focus
```

### Fix from Review

```bash
/fix "src/utils/" --note="Address code review feedback: improve error handling"
# Applies specific improvements based on review notes
```

### Error Case

```bash
/fix "src/perfect-code.ts"
# No issues found in src/perfect-code.ts
# All checks passing -- nothing to fix
```
