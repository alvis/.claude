---
allowed-tools: Read, Glob, Grep, TodoWrite, Task, Bash

argument-hint: [--files=CONTEXT.md,RESEARCH.md,PLAN.md]

description: Parse handover notes and auto-resume write-code workflow
---

# Work Takeover

Parses handover documentation (CONTEXT.md, RESEARCH.md, PLAN.md) left by previous agent, automatically determines the appropriate write-code workflow step to resume, and provides complete context for seamless work continuation with validated state and critical insights

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not create or update handover documentation (use `/handover` for that)
- Does not modify project files or execute code
- Does not perform git operations like commit, push, or branch switching

**When to REJECT**:

- When any handover file (CONTEXT.md, RESEARCH.md, PLAN.md) does not exist at specified or default path
- When handover documents lack required structure (missing critical sections)
- When requested to create handover instead of reading it
- When working directory is not a git repository



## 🔄 Workflow

ultrathink: Before performing any steps, deeply analyze the handover context and plan continuation:

- **Project Diagnostics**: Run get_project_overview and ide__getDiagnostics to understand current build/type/lint issues
- **Handover Analysis**: Thoroughly read and understand all three handover files (CONTEXT.md, RESEARCH.md, PLAN.md) to grasp the complete project state
- **State Verification**: Compare documented state with actual current state to identify discrepancies and changes
- **Issue Analysis**: Correlate diagnostics results with handover documentation to identify what needs fixing
- **Context Integration**: Synthesize information from all three files into coherent understanding of goals, progress, and challenges
- **Workflow Step Detection**: Analyze file substates, current issues, and current phase to automatically determine which write-code workflow step to resume
- **Task Planning**: Identify immediate priorities, dependencies, and continuation strategy based on detected workflow step and current issues
- **Knowledge Transfer**: Extract all critical context (decisions, patterns, gotchas, research insights) needed for seamless continuation at the detected step

Then perform the following steps:

### Step 1: Run Project Diagnostics

**Diagnostic Tools (in order of preference):**

1. **Run get_project_overview MCP tool** (if available):
   - Provides comprehensive project analysis
   - Identifies type errors, build issues, and structural problems
   - Skip remaining diagnostic steps if this succeeds

2. **Run ide__getDiagnostics MCP tool** (if available and get_project_overview unavailable):
   - Get real-time diagnostics from language server
   - Identify type errors and linting issues
   - Run for all files in scope from handover

3. **Run npm run lint** (if MCP tools unavailable):
   - Execute linting on project path
   - Identify standards violations and code quality issues
   - Use `npm run lint -- <path>` for targeted linting

**Capture and Document:**
- All errors and warnings found
- Files with issues and their error counts
- Severity levels (fatal, error, warning)
- Correlation with file substates from handover

**Output**: Diagnostics summary to inform workflow step detection

### Step 2: Validate Handover Files and Discover Architecture

- Parse --files argument, default to "CONTEXT.md,RESEARCH.md,PLAN.md"
- Verify all three handover files exist at specified locations, reject if missing
- Discover architecture/design documentation files by using  Glob to find all .md files recursively in project for verification context

### Step 3: Read and Parse Handover Documents

Read all three handover files and extract key sections:

**From CONTEXT.md**:

- Current State, File Status (with substates: need-draft, need-completion, need-testing, need-linting, need-fixing, need-refactoring)
- Recent Changes, Key Decisions, Gotchas & Workarounds, Dependencies, Next Steps

**From RESEARCH.md**:

- Documentation References, Problems & Solutions, Explorations (what worked/didn't work)
- Key Insights, Open Questions, Quick Tips

**From PLAN.md**:

- Goals & Success Criteria, Task Breakdown by Phases, Dependencies
- Risks & Mitigation, Decision Log

Validate critical sections exist: Current State, File Status, Next Steps (CONTEXT.md); Problems & Solutions, Key Insights (RESEARCH.md); Goals & Success Criteria, Task Breakdown (PLAN.md)

### Step 4: Verify Current State

- Read discovered architecture/design/requirement files
- Compare with CONTEXT.md and PLAN.md for consistency
- Verify git state (branch, file status, commit history)
- Identify discrepancies between documented and actual state
- Report findings for inclusion in output

### Step 5: Extract Critical Information

From the parsed handover documents, extract and organize:

**Priority 1 - Strategic Context**:

- Goals and success criteria from PLAN.md (defines what "done" means)
- Current phase status from PLAN.md task breakdown (where we are in the plan)
- First 1-3 items from Next Steps in CONTEXT.md (immediate actions)
- Any in-progress files (🚧) from CONTEXT.md that need completion
- Blocking issues or gotchas from CONTEXT.md that must be addressed first

**Priority 2 - Research Context**:

- Problems already solved from RESEARCH.md (avoid duplicating work)
- What worked and what didn't work from RESEARCH.md explorations (learn from past attempts)
- Key insights from RESEARCH.md (apply proven learnings)
- Quick tips from RESEARCH.md (use discovered shortcuts and best practices)

**Priority 3 - Planning Information**:

- Task breakdown by phases from PLAN.md (structured work plan)
- Dependencies from PLAN.md (what needs to happen when)
- Risks and mitigation strategies from PLAN.md (proactive problem handling)

**Priority 4 - Reference Information**:

- Key decisions and their rationale from CONTEXT.md (affects how work continues)
- Established patterns from CONTEXT.md (must follow for consistency)
- Gotchas and workarounds from CONTEXT.md (avoid repeating mistakes)
- Dependencies and configuration from CONTEXT.md (technical requirements)

### Step 6: Determine Write-Code Workflow Step and Create Action Plan

**Part A: Auto-Detect Write-Code Workflow Resumption Point**

Analyze extracted information AND diagnostics results to determine which write-code workflow step to resume:

**Step Detection Logic:**

1. **Analyze Diagnostics Results** from Step 1:
   - Review type errors, build failures, lint violations
   - Identify files with critical issues
   - Determine if issues indicate incomplete implementation, broken tests, or quality problems

2. **Analyze File Substates** from CONTEXT.md File Status:
   - Count files in each substate (need-draft, need-completion, need-fixing, need-testing, need-linting, need-refactoring)
   - Identify majority substate or earliest pending work
   - Cross-reference with diagnostics to validate substates

3. **Check Current Phase** from PLAN.md:
   - Identify which phase is marked as current/in-progress
   - Review completed vs pending tasks

4. **Review Next Steps** from CONTEXT.md:
   - Identify immediate actions required
   - Check for blocking issues

5. **Apply Decision Matrix (Priority Order):**
   - **Priority 1 - Diagnostics Issues:**
     - If type errors in skeleton files → **Step 1** (Draft Code Skeleton & Test Structure)
     - If implementation incomplete with TODOs → **Step 2** (Implementation - Green Phase)
     - If test failures OR test-related errors → **Step 3** (Fix Test Issues & Standards Compliance)
     - If lint violations only → **Step 5** (Refactoring & Documentation)
   - **Priority 2 - File Substates:**
     - If majority "need-draft" OR no code exists → **Step 1** (Draft Code Skeleton & Test Structure)
     - If "need-completion" OR in-progress implementation → **Step 2** (Implementation - Green Phase)
     - If "need-fixing" → **Step 3** (Fix Test Issues & Standards Compliance)
     - If fixture/mock issues identified → **Step 4** (Optimize Test Structure & Fixtures)
     - If "need-linting" OR "need-refactoring" → **Step 5** (Refactoring & Documentation)
   - **Priority 3 - Default:**
     - If mixed states → Choose earliest step with pending work (Step 1 → 2 → 3 → 4 → 5)

6. **Document Detection Rationale:**
   - Record why this step was chosen
   - Note triggering factors (diagnostics + file states)
   - List specific issues to address
   - Prepare context for write-code workflow execution

**Part B: Create Task List**

Using TodoWrite, create task list based on detected write-code workflow step:

**Task Structure**:

```yaml
- content: "[action from PLAN.md or Next Steps]"
  activeForm: "[present continuous form]"
  status: "pending"
```

**Task Creation Strategy**:

- **PRIMARY**: Execute detected write-code workflow step with all relevant files
- **CONTEXT**: Provide complete handover context (decisions, insights, patterns, gotchas)
- **STANDARDS**: Reference write-code.md workflow file path explicitly
- **ENRICHMENT**: Include research insights from RESEARCH.md as step context

**Write-Code Workflow Step Mapping**:

- **Step 0**: Design Direction Discovery (if design docs exist)
- **Step 1**: Draft Code Skeleton & Test Structure (for need-draft, need-testing states)
- **Step 2**: Implementation - Green Phase (for need-completion state)
- **Step 3**: Fix Test Issues & Standards Compliance (for need-fixing, test failures)
- **Step 4**: Optimize Test Structure & Fixtures (for fixture/mock issues)
- **Step 5**: Refactoring & Documentation (for need-linting, need-refactoring states)

**File Grouping**: Group by state type (max 5 files/group), relationship (component + types), or dependency order (types → implementation → tests)

**Task Prioritization**: (1) Blocking issues/in-progress work, (2) File substates (need-draft → need-completion → need-fixing → need-linting → need-testing → need-refactoring), (3) Current phase tasks from PLAN.md, (4) Next steps from CONTEXT.md, (5) Next phase tasks

**Workflow Context Preparation**: Gather all context for write-code workflow execution:
- File paths and their substates for step-specific processing
- Relevant workflows and standards from Project Context
- Key decisions and established patterns from CONTEXT.md
- Known gotchas and workarounds to avoid repeating mistakes
- Research insights and quick tips from RESEARCH.md applicable to detected step
- Success criteria from PLAN.md to guide validation

### Step 7: Present Continuation Summary

**Output Format**:

```text
[✅] Takeover: $ARGUMENTS

## Handover Summary
- Context file: [absolute path to CONTEXT.md]
- Research file: [absolute path to RESEARCH.md]
- Plan file: [absolute path to PLAN.md]
- Last Updated: [ISO timestamp from CONTEXT.md]
- Documented Branch: [branch from CONTEXT.md]

## Project Diagnostics
### Tool Used
[get_project_overview | ide__getDiagnostics | npm run lint]

### Issues Found
- **Type Errors**: [count] errors in [count] files
- **Build Failures**: [count] failures
- **Lint Violations**: [count] violations in [count] files
- **Test Failures**: [count] failing tests

### Critical Files with Issues
- [file path]: [error count] errors ([error types])
- [file path]: [error count] errors ([error types])

### Issue Categories
- **Incomplete Implementation**: [count] files with TODO/IMPLEMENTATION errors
- **Type Safety**: [count] files with type errors
- **Standards Compliance**: [count] files with lint violations
- **Test Issues**: [count] files with test failures

## State Verification
### ✅ Verified
- Current branch matches: [branch name]
- [count] completed files confirmed clean
- [count] in-progress files confirmed modified

### ⚠️ Discrepancies (if any)
- Branch mismatch: documented=[branch], actual=[branch]
- New modifications not in handover: [files]
- Documented in-progress files now clean: [files]

## Plan Overview
### Primary Goal
[primary goal from PLAN.md Goals & Success Criteria]

### Current Phase
[current phase name] - [phase status/progress]

### Success Criteria
- [ ] [criterion 1 from PLAN.md]
- [ ] [criterion 2 from PLAN.md]
- [ ] [criterion 3 from PLAN.md]

## Write-Code Workflow Continuation

### Auto-Detected Resume Point
**Step [N]: [Step Name from write-code.md]**

### Detection Rationale
- **Diagnostics Analysis**: [X type errors, Y test failures, Z lint violations]
- **File States Analysis**: [X files need-draft, Y files need-completion, Z files need-fixing]
- **Current Phase**: [Phase name and status from PLAN.md]
- **Triggering Factors**: [Primary reason this step was selected - diagnostics issue or file substate]
- **Priority Consideration**: [Why this step takes priority - diagnostics-driven or substate-driven]
- **Issues to Address**: [Specific diagnostic issues that will be resolved in this step]

### Step-Specific Context

**What Has Been Completed:**
- [Summary of completed work from CONTEXT.md]
- [Key milestones achieved]

**What Remains for This Step:**
- [Specific actions required for detected step]
- [Files to be processed in this step]
- [Expected outcomes from this step]

**Key Decisions to Apply:**
- [Decision 1 from CONTEXT.md relevant to this step]
- [Decision 2 from CONTEXT.md relevant to this step]

**Research Insights to Use:**
- [Insight 1 from RESEARCH.md applicable to this step]
- [Tip 1 from RESEARCH.md Quick Tips]

**Known Issues to Watch:**
- [Gotcha 1 from CONTEXT.md]
- [Workaround to apply]

### Continuation Instructions

**Workflow File**: `/Users/alvis/Repositories/.claude/plugins/coding/constitution/workflows/write-code.md`

**Execute**: Start write-code workflow at Step [N]

**Actions for Step [N]**:
1. [Specific action 1 for this step from write-code.md]
2. [Specific action 2 for this step from write-code.md]
3. [Specific action 3 for this step from write-code.md]

**Required Standards** (from write-code.md Step [N]):
- [standard 1 path]
- [standard 2 path]
- [standard 3 path]

**Files in Scope**:
- [file 1] - [substate] - [specific work needed]
- [file 2] - [substate] - [specific work needed]

**Expected Output**:
[What this step should produce per write-code.md]

## Research Insights Summary
### Problems Solved
- [problem description] → [solution approach] at [location/file]
- [problem description] → [solution approach] at [location/file]

### Key Learnings
- ✅ What Worked: [approach that worked and why]
- ❌ What Didn't Work: [approach that failed and why]

### Quick Tips
- [tip from RESEARCH.md quick tips]
- [tip from RESEARCH.md quick tips]

## Critical Context
### Key Decisions
1. [decision] - [rationale] - affects [impact]
2. [decision] - [rationale] - affects [impact]

### Established Patterns
- [pattern description and where it's used]
- [pattern description and where it's used]

### Known Gotchas
- [issue] at [location] - workaround: [solution]
- [issue] at [location] - workaround: [solution]

## File Status with Work Required

### 🚧 In Progress ([count] files)
- [file path] ([substate: need-completion/need-fixing/need-linting/need-refactoring]) - [specific work required]
- [file path] ([substate]) - [specific work required]

### 📋 Planned ([count] files)
- [file path] ([substate: need-draft/need-testing]) - [specific work required]

### ✅ Completed ([count] files)
- [count] files completed (details in CONTEXT.md Historical Notes)
- Recent: [first 3-5 files...]

## Workflow Execution Plan

### Detected Workflow
**write-code.md** - Comprehensive TDD implementation workflow

### Starting Point
**Step [N]: [Step Name]**

### File Processing Strategy
- **Total Files**: [count] files requiring attention
- **Primary Substate**: [most common substate]
- **Processing Approach**: [Sequential/Batched based on write-code.md step requirements]

### Workflow Progression
After completing Step [N], the write-code workflow will automatically progress through remaining steps:
- [List of subsequent steps if applicable]
- Each step includes built-in quality gates and validation
- Interactive handover points enabled for user feedback

## Task Breakdown from Plan
### Phase 1: [phase name] ([status])
1. [task from PLAN.md]
2. [task from PLAN.md]

### Phase 2: [phase name] ([status])
3. [task from PLAN.md]
4. [task from PLAN.md]

## Action Plan Created
### Priority 1 - Immediate ([count] tasks from current phase)
1. [task from PLAN.md current phase]
2. [task from PLAN.md current phase]

### Priority 2 - Following ([count] tasks from next phase)
3. [task from PLAN.md next phase]
4. [task from PLAN.md next phase]

### Priority 3 - Future ([count] tasks)
5. [task from later phases or CONTEXT.md]

## Dependencies
### External Dependencies
- [package/config] - [version/purpose]

### Internal Dependencies
- [file/component] - [dependency relationship]

## Ready to Continue
✓ Handover parsed successfully (3 files)
✓ State verification complete
✓ Research insights extracted
✓ Plan overview integrated
✓ Write-code workflow step auto-detected: Step [N]
✓ Step-specific context prepared
✓ Continuation instructions ready

## Next Action: Resume Write-Code Workflow

**Execute write-code workflow starting at Step [N]: [Step Name]**

### Current Work Context
- **Primary Goal**: [goal from PLAN.md]
- **Current State**: [brief state summary from CONTEXT.md]
- **Diagnostics Summary**: [X type errors, Y test failures, Z lint violations]
- **Files in Scope**: [list of files with their substates and diagnostic issues]
- **Detected Step**: Step [N] based on [diagnostics + triggering factor]

### Step [N] Execution Requirements

**Workflow File Path**:
`/Users/alvis/Repositories/.claude/plugins/coding/constitution/workflows/write-code.md`

**Specific Actions for This Step**:
1. [Action 1 from write-code.md Step N]
2. [Action 2 from write-code.md Step N]
3. [Action 3 from write-code.md Step N]

**Required Standards** (per write-code.md Step [N]):
- [Standard 1 path]
- [Standard 2 path]
- [Standard 3 path]

**Expected Output**:
[What Step N should produce per write-code.md]

### Context to Apply During Execution

**Key Decisions** (from CONTEXT.md):
- [Decision 1 affecting this step]
- [Decision 2 affecting this step]

**Established Patterns** (from CONTEXT.md):
- [Pattern 1 to follow]
- [Pattern 2 to follow]

**Research Insights** (from RESEARCH.md):
- [Insight 1 applicable to this step]
- [Quick tip 1 for this step]

**Known Gotchas** (from CONTEXT.md):
- [Gotcha 1] - Workaround: [solution]
- [Gotcha 2] - Workaround: [solution]

**Success Criteria** (from PLAN.md):
- [Criterion 1 relevant to this step]
- [Criterion 2 relevant to this step]

---

**Post-Execution**: Upon completion of delegated work, run `/handover` to automatically update documentation with latest state.
```

## 📝 Examples

### Simple Usage - Auto-Detect Step

```bash
/takeover
# Step 1: Runs get_project_overview - finds 15 type errors, 3 test failures
# Step 2-3: Reads CONTEXT.md, RESEARCH.md, PLAN.md
# Step 4-5: Analyzes file substates and current phase
# Step 6: Auto-detects: Resume at write-code Step 3 (Fix Test Issues)
#         Rationale: Test failures in diagnostics + "need-fixing" substates
# Step 7: Provides complete context and continuation instructions
# Result: Ready to execute write-code.md Step 3 with diagnostics + handover context
```

### Scenario: Need Draft (Step 1 Detection)

```bash
/takeover
# Diagnostics: No significant errors (project clean or minimal setup)
# File States: 5 files with "need-draft" substate
# Current Phase: "Implementation" phase just started
# Auto-detects: Resume at write-code Step 1 (Draft Code Skeleton & Test Structure)
# Detection: Substate-driven (no code exists, need to draft skeleton)
# Context provided:
#   - Design specifications from discovered DESIGN.md
#   - Interface requirements from PLAN.md
#   - Patterns to follow from CONTEXT.md
# Next: Execute write-code.md Step 1 to create skeleton and test structure
```

### Scenario: Need Completion (Step 2 Detection)

```bash
/takeover
# Diagnostics: 8 "IMPLEMENTATION: ..." errors (TODO placeholders throwing errors)
# File States: 3 files with "need-completion" substate
# Current State: Code skeleton exists with TODOs
# Auto-detects: Resume at write-code Step 2 (Implementation - Green Phase)
# Detection: Diagnostics-driven (incomplete implementation errors match substates)
# Context provided:
#   - Existing skeleton structure
#   - Test suite awaiting implementation
#   - Error handling patterns from CONTEXT.md
#   - Specific TODOs identified from diagnostics
# Next: Execute write-code.md Step 2 to implement minimal working code
```

### Scenario: Test Failures (Step 3 Detection)

```bash
/takeover
# Diagnostics: 12 test failures across 7 files + 5 type errors in test files
# File States: 7 files with "need-fixing" substate
# Current State: Tests failing, implementation done
# Auto-detects: Resume at write-code Step 3 (Fix Test Issues & Standards Compliance)
# Detection: Diagnostics-driven (test failures are primary trigger)
# Context provided:
#   - Specific test failures from diagnostics
#   - Test failure patterns from CONTEXT.md
#   - Standards violations identified in diagnostics
#   - Solutions from RESEARCH.md for similar failures
# Issues to address: 12 test failures + 5 type errors
# Next: Execute write-code.md Step 3 to fix tests and ensure compliance
```

### Scenario: Need Refactoring (Step 5 Detection)

```bash
/takeover
# Diagnostics: 23 lint violations (no type/test errors)
# File States: 4 files with "need-refactoring" and "need-linting" substates
# Current State: Implementation complete, tests passing
# Auto-detects: Resume at write-code Step 5 (Refactoring & Documentation)
# Detection: Diagnostics-driven (lint violations only = quality/style issues)
# Context provided:
#   - Specific lint violations from diagnostics
#   - Code quality improvements needed
#   - Documentation standards from RESEARCH.md
#   - Refactoring patterns from CONTEXT.md
# Issues to address: 23 lint violations across 4 files
# Next: Execute write-code.md Step 5 for quality improvements
```

### Scenario: Diagnostics-Driven Priority (Mixed States)

```bash
/takeover
# Diagnostics: 15 test failures + 3 type errors + 8 lint violations
# File States: Mixed (2 need-completion, 5 need-fixing, 3 need-linting)
# Current State: Some implementation incomplete, tests failing, quality issues
# Auto-detects: Resume at write-code Step 3 (Fix Test Issues & Standards Compliance)
# Detection: Diagnostics-driven (test failures take priority over other issues)
# Rationale: Fix failing tests first before refactoring or completing implementation
# Context provided:
#   - Test failures are blocking progress (highest priority)
#   - Type errors in test files need fixing
#   - Lint violations can be addressed in Step 5 later
# Issues to address: 15 test failures + 3 type errors (lint deferred)
# Next: Execute write-code.md Step 3, then loop back for Step 2/5 if needed
```

### Custom File Paths

```bash
/takeover --files=CONTEXT.md,RESEARCH.md,PLAN.md
# Explicitly specify all 3 handover files
# Runs diagnostics + analyzes handover state
# Auto-detects workflow step based on diagnostics + file analysis
# Provides complete continuation context with issue details
```

### Complete Workflow Cycle

```bash
# Agent A finishing work:
/handover
# Creates CONTEXT.md (state), RESEARCH.md (learnings), PLAN.md (strategy)

# Agent B taking over:
/takeover
# 1. Runs project diagnostics (get_project_overview or ide__getDiagnostics)
# 2. Reads all 3 handover files (CONTEXT.md, RESEARCH.md, PLAN.md)
# 3. Correlates diagnostics with file substates
# 4. Auto-detects write-code workflow step based on diagnostics + substates
#    Example: 12 test failures → Step 3 (Fix Test Issues)
# 5. Provides complete context: diagnostics + handover insights
# 6. Execute write-code.md starting at detected step with full context
# 7. Upon completion, run /handover to update docs with latest state
# Result: Seamless work continuation with diagnostics-informed workflow resumption
```

### Error Case

```bash
/takeover
# Error: One or more handover files not found
# Suggestion: Create handover first with `/handover` or check file location
```
