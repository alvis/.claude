---
allowed-tools: Read, Glob, Grep, TodoWrite, Task, Bash, SlashCommand(/handover)

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

<IMPORTANT>
- **Project Diagnostics**: Run get_project_overview, ide__getDiagnostics, testing, linting, and build scripts with LIMITED OUTPUT (max 20 lines per bash tool) to understand current issues. OMIT TODO errors from consideration.
- **Issue Prioritization**: If CRITICAL issues found (type errors, test failures, build breaks), fixing them MUST take priority before resuming planned work. Consult handover and design docs for direction.
</IMPORTANT>
- **Handover Analysis**: Thoroughly read and understand all three handover files (CONTEXT.md, RESEARCH.md, PLAN.md) to grasp the complete project state
- **State Verification**: Compare documented state with actual current state to identify discrepancies and changes
- **Issue Analysis**: Correlate diagnostics results with handover documentation to identify what needs fixing
- **Context Integration**: Synthesize information from all three files into coherent understanding of goals, progress, and challenges
- **Workflow Step Detection**: Analyze file substates, current issues, and current phase to automatically determine which write-code workflow step to resume
<IMPORTANT>
- **Delegation Strategy**: ALL coding actions (implementation, fixing, testing, refactoring) MUST be delegated to subagents via Task tool. Direct code modification is PROHIBITED.
</IMPORTANT>
- **Task Planning**: Identify immediate priorities, dependencies, and continuation strategy based on detected workflow step and current issues
- **Knowledge Transfer**: Extract all critical context (decisions, patterns, gotchas, research insights) needed for seamless continuation at the detected step

Then perform the following steps:

### Step 1: Run Project Diagnostics

<IMPORTANT>
**Critical Requirements:**
- LIMIT output to max 20 lines per diagnostic tool (use `| head -20` or similar)
- OMIT TODO issues from consideration - focus only on real type/build/lint issues
- If any issues found (lint issues, type errors, test failures, build breaks), plan must prioritize FIXING them FIRST before resuming documented work
- Consult handover docs (CONTEXT.md, PLAN.md) and design docs for direction on fixes
</IMPORTANT>

**Diagnostic Tools (in order of preference):**

1. **Run get_project_overview MCP tool** (if available):
   - Provides comprehensive project analysis with limited output
   - Identifies type errors, build issues, and structural problems
   - Skip remaining diagnostic steps if this succeeds

2. **Run ide__getDiagnostics MCP tool** (if available and get_project_overview unavailable):
   - Get real-time diagnostics from language server with limited output
   - Identify type errors and linting issues
   - Run for all files in scope from handover

3. **Run build script** (e.g., `npx tsc --noEmit | head -20`):
   - Execute TypeScript compilation check with limited output
   - Identify type errors and compilation issues

4. **Run lint script** (e.g., `npm run lint | head -20`):
   - Execute linting on project path with limited output
   - Identify standards violations and code quality issues

**Capture and Document:**

- All errors and warnings found (excluding TODO errors)
- Files with issues and their error counts
- Severity levels (fatal, error, warning)
- Correlation with file substates from handover

**Output**: Diagnostics summary to inform workflow step detection and issue prioritization

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

**Strategic Context**:

- Goals and success criteria from PLAN.md (defines what "done" means)
- Current phase status from PLAN.md task breakdown (where we are in the plan)
- First 1-3 items from Next Steps in CONTEXT.md (immediate actions)
- Any in-progress files (🚧) from CONTEXT.md that need completion
- Blocking issues or gotchas from CONTEXT.md that must be addressed first

**Research Context**:

- Problems already solved from RESEARCH.md (avoid duplicating work)
- What worked and what didn't work from RESEARCH.md explorations (learn from past attempts)
- Key insights from RESEARCH.md (apply proven learnings)
- Quick tips from RESEARCH.md (use discovered shortcuts and best practices)

**Planning Information**:

- Task breakdown by phases from PLAN.md (structured work plan)
- Dependencies from PLAN.md (what needs to happen when)
- Risks and mitigation strategies from PLAN.md (proactive problem handling)

**Reference Information**:

- Key decisions and their rationale from CONTEXT.md (affects how work continues)
- Established patterns from CONTEXT.md (must follow for consistency)
- Gotchas and workarounds from CONTEXT.md (avoid repeating mistakes)
- Dependencies and configuration from CONTEXT.md (technical requirements)

### Step 6: Create Action Plan for Delegation

<IMPORTANT>
**Delegation Requirements:**
- ALL coding actions (implementation, fixing, testing, refactoring, linting) MUST be delegated to subagents via Task tool
- Direct code modification by this command is PROHIBITED
- When delegating, MUST pass full file paths of relevant workflow and standard files to subagent
- Subagent must be given complete context: detected step, file substates, diagnostics issues, handover insights
</IMPORTANT>

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

**Part B: Prepare Delegation Context**

Using TodoWrite, create task list based on detected write-code workflow step:
Prepare comprehensive context package for subagent delegation:

**Context Package Contents**:

1. **Detected Workflow Step**:
   - Step number and name from write-code.md
   - Detection rationale (diagnostics + file substates)
   - Expected outcomes for this step

2. **File Context**:
   - Files in scope with their substates
   - Diagnostic issues per file (excluding TODO errors)
   - Dependency relationships

3. **Workflow & Standards**:
   - Full path to write-code.md workflow file
   - Full paths to required standards files for detected step
   - Specific step instructions from workflow

4. **Handover Context**:
   - Key decisions from CONTEXT.md
   - Established patterns to follow
   - Known gotchas and workarounds
   - Research insights from RESEARCH.md
   - Quick tips applicable to detected step

5. **Success Criteria**:
   - Relevant criteria from PLAN.md
   - Validation requirements

**Write-Code Workflow Step Mapping**:

- **Step 0**: Design Direction Discovery (if design docs exist)
- **Step 1**: Draft Code Skeleton & Test Structure (for need-draft, need-testing states)
- **Step 2**: Implementation - Green Phase (for need-completion state)
- **Step 3**: Fix Test Issues & Standards Compliance (for need-fixing, test failures)
- **Step 4**: Optimize Test Structure & Fixtures (for fixture/mock issues)
- **Step 5**: Refactoring & Documentation (for need-linting, need-refactoring states)

**Delegation Preparation**: Format context for Task tool invocation with appropriate subagent (coding agent)

### Step 7: Update Handover & Report

<IMPORTANT>
**FIRST ACTION: Run `/handover` command to update handover documentation with current state before showing output.**
</IMPORTANT>

After updating handover, use a subtask to run testing, linting and building scripts again to confirm compliance, then provide concise output:

**Output Format**:

```text
[✅] Takeover: $ARGUMENTS

## Handover Summary
- Files: CONTEXT.md, RESEARCH.md, PLAN.md at [project root path]
- Last Updated: [ISO timestamp from CONTEXT.md]
- Branch: [branch from CONTEXT.md]

## Diagnostics Summary
- **Type Errors**: [count] in [count] files (TODO errors omitted)
- **Test Failures**: [count] tests
- **Lint Violations**: [count] in [count] files
- **Build Issues**: [count] failures

## Detected Workflow Step
**Step [N]: [Step Name]** from write-code.md

**Rationale**: [1-2 sentence explanation based on diagnostics + file substates]

**Critical Issues to Fix First**: [List if diagnostics found critical issues, otherwise "None - ready to resume planned work"]

## Files in Scope
### 🚧 In Progress ([count])
- [file path] - [substate] - [diagnostic issue if any]

### 📋 Planned ([count])
- [file path] - [substate] - [diagnostic issue if any]

### ✅ Completed ([count])
- [Summary line, e.g., "15 files completed, see CONTEXT.md"]

## Next Action
<IMPORTANT>
**Delegate to subagent**: Execute write-code.md Step [N] with following context:
- Workflow: `/Users/alvis/.../write-code.md`
- Standards: [list required standard file paths]
- Files: [list files with substates]
- Key decisions from CONTEXT.md: [1-2 critical decisions]
- Research insights: [1-2 applicable tips from RESEARCH.md]
- Success criteria: [relevant criteria from PLAN.md]
</IMPORTANT>

**After subagent completes**: Run `/handover` again to update documentation.
```

## 📝 Examples

### Simple Usage - Auto-Detect Step

```bash
/takeover
# Step 1: Runs diagnostics (limited output) - finds 12 type errors, 3 test failures
# Step 2-3: Reads handover files (CONTEXT, RESEARCH, PLAN)
# Step 4-5: Analyzes state and extracts critical info
# Step 6: Auto-detects Step 3 (Fix Test Issues) - test failures + need-fixing states
# Step 7: Runs /handover first, then shows concise output with delegation instructions
# Result: Concise report with next action to delegate to subagent
```

### Error Case

```bash
/takeover
# Error: One or more handover files not found
# Suggestion: Create handover first with `/handover` or check file location
```
