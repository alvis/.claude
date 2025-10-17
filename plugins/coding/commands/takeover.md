---
allowed-tools: Read, Glob, Grep, TodoWrite, Task, Bash

argument-hint: [--files=CONTEXT.md,RESEARCH.md,PLAN.md]

description: Parse handover notes and prepare for work continuation
---

# Work Takeover

Parses handover documentation (CONTEXT.md, RESEARCH.md, PLAN.md) left by previous agent and prepares actionable continuation plan with validated state, prioritized tasks, and critical context extraction from all three complementary files

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

- **Handover Analysis**: Thoroughly read and understand all three handover files (CONTEXT.md, RESEARCH.md, PLAN.md) to grasp the complete project state
- **State Verification**: Compare documented state with actual current state to identify discrepancies and changes
- **Context Integration**: Synthesize information from all three files into coherent understanding of goals, progress, and challenges
- **Task Planning**: Identify immediate priorities, dependencies, and continuation strategy based on PLAN.md and CONTEXT.md
- **Knowledge Transfer**: Extract all critical context (decisions, patterns, gotchas, research insights) needed for seamless continuation

Then perform the following steps:

### Step 1: Validate Handover Files and Discover Architecture

- Parse --files argument, default to "CONTEXT.md,RESEARCH.md,PLAN.md"
- Verify all three handover files exist at specified locations, reject if missing
- Discover architecture/design documentation files by using  Glob to find all .md files recursively in project for verification context

### Step 2: Read and Parse Handover Documents

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

### Step 3: Verify Current State

- Read discovered architecture/design/requirement files
- Compare with CONTEXT.md and PLAN.md for consistency
- Verify git state (branch, file status, commit history)
- Identify discrepancies between documented and actual state
- Report findings for inclusion in output

### Step 4: Extract Critical Information

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

### Step 5: Create Action Plan and Task List with Automated Delegation

Using TodoWrite, create task list from extracted information WITH delegation commands:

**Task Structure**:

```yaml
- content: "[action from PLAN.md or Next Steps]"
  activeForm: "[present continuous form]"
  status: "pending"
```

**Task Creation Strategy**:

- **PRIMARY SOURCE**: Use task breakdown from PLAN.md as the main source for task creation
- **SUPPLEMENTARY**: Add tasks based on file substates from CONTEXT.md (need-draft, need-completion, etc.)
- **ENRICHMENT**: Include research insights from RESEARCH.md as task context where relevant

**Delegation Mapping**: `need-draft` → write-code.md; `need-completion` → write-code.md; `need-testing` → create-test.md or fix-test.md; `need-linting` → lint.md; `need-fixing` → fix-test.md; `need-refactoring` → review-code.md

**File Grouping**: Group by state type (max 5 files/group), relationship (component + types), or dependency order (types → implementation → tests)

**Task Prioritization**: (1) Blocking issues/in-progress work, (2) File substates (need-draft → need-completion → need-fixing → need-linting → need-testing → need-refactoring), (3) Current phase tasks from PLAN.md, (4) Next steps from CONTEXT.md, (5) Next phase tasks

**Delegation Context**: For each task group, provide file paths/substates, relevant workflows/standards from Project Context, key decisions/patterns from CONTEXT.md, gotchas/workarounds, and research insights/tips from RESEARCH.md. Subagents must confirm standards/workflows followed in final report.

### Step 6: Present Continuation Summary

**Output Format**:

```text
[✅] Takeover: $ARGUMENTS

## Handover Summary
- Context file: [absolute path to CONTEXT.md]
- Research file: [absolute path to RESEARCH.md]
- Plan file: [absolute path to PLAN.md]
- Last Updated: [ISO timestamp from CONTEXT.md]
- Documented Branch: [branch from CONTEXT.md]

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

## Automated Delegation Plan

### Group 1: [Phase Name] ([count] files - [substate])
**Files**: [file1], [file2], [file3]
**Workflows (MUST Execute)**:
  - [specific workflow path]
  - [additional workflows if needed]
**Standards (MUST Follow)**:
  - [specific standard path]
  - [additional standards if needed]
**Context**: [Brief context from PLAN.md/CONTEXT.md]
**Dependencies**: [None or list dependencies]

### Group 2: [Phase Name] ([count] files - [substate])
**Files**: [file list]
**Workflows (MUST Execute)**:
  - [specific workflow path]
  - [additional workflow paths]
**Standards (MUST Follow)**:
  - [specific standard path]
  - [additional standards if needed]
**Context**: [Brief context with TODOs/issues to address]
**Research Tip**: [Relevant tip from RESEARCH.md]
**Dependencies**: [Dependencies from PLAN.md or CONTEXT.md]

### Group N: [Phase Name] ([count] files - [substate])
[... continue for all groups ...]

**Execution Order**: Group 1 → Group 2 → ... → Group N
**Total Groups**: [count]
**Total Files**: [count]
**Estimated Tasks**: [count]

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
✓ Action plan created with [count] tasks
✓ Delegation plan generated with [count] groups
✓ Task list written to todo

## Next Action
Execute Group 1 workflows for [substate] files: [file paths]

**Subagent Instructions (MANDATORY)**:
- MUST execute workflows: [specific workflow paths listed in Group 1]
- MUST follow standards: [specific standard paths from Project Context]
- MUST read architecture: [architecture file paths]
- MUST apply patterns: [relevant patterns from CONTEXT.md]
- MUST watch for: [relevant gotchas from CONTEXT.md]
- MUST use insights: [relevant insights from RESEARCH.md]
- MUST report: Confirm which workflows executed and standards followed

---

**Post-Execution**: Upon completion of delegated work, run `/handover` to automatically update documentation with latest state.
```

## 📝 Examples

### Simple Usage

```bash
/takeover
# Reads CONTEXT.md, RESEARCH.md, PLAN.md (defaults)
# Parses all handover sections from 3 complementary files
# Verifies current state matches documented state
# Integrates research insights and plan overview
# Creates action plan with prioritized tasks from PLAN.md
```

### Custom File Paths

```bash
/takeover --files=CONTEXT.md,RESEARCH.md,PLAN.md
# Explicitly specify all 3 handover files
# Same comprehensive parsing and verification
# Creates actionable continuation plan with full context
```

### Three-File Integration Workflow

```bash
# Agent A finishing work:
/handover
# Creates CONTEXT.md (state), RESEARCH.md (learnings), PLAN.md (strategy)

# Agent B taking over:
/takeover
# 1. Reads all 3 handover files
# 2. Generates delegation plan
# 3. Executes delegated work (via commands)
# 4. Automatically runs /handover to update docs with latest state
# Result: Work completed + updated handover for next agent
```

### Error Case

```bash
/takeover
# Error: One or more handover files not found
# Suggestion: Create handover first with `/handover` or check file location
```
