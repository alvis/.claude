---
name: takeover
description: Parse handover notes and auto-resume write-code workflow. Use when continuing interrupted work, resuming from handover documents, or picking up another developer's task.
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Glob, Grep
argument-hint: [prefix]
---

# Work Takeover

Parses handover documentation (CONTEXT.md, NOTES.md, PLAN.md) left by previous agent, automatically determines the appropriate write-code workflow step to resume, and provides complete context for seamless work continuation.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not create or update handover documentation (use `/coding:handover` for that)
- Does not modify project files or execute code directly (delegates to subagents)
- Does not perform git operations like commit, push, or branch switching

**When to REJECT**:

- When any handover file (CONTEXT.md, NOTES.md, PLAN.md) does not exist at specified or default path
- When handover documents lack required structure (missing critical sections)
- When requested to create handover instead of reading it
- When working directory is not a git repository

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Plan Work Continuation

1. **Validate Handover Files**
   - Parse optional prefix argument from $ARGUMENTS
   - Construct file names: [prefix]-CONTEXT.md, [prefix]-NOTES.md, [prefix]-PLAN.md
   - Verify all three handover files exist

2. **Run Diagnostics**
   - Execute project overview to understand current issues
   - Run type checking to find TypeScript errors
   - Run linting to find code quality issues
   - Identify critical blockers

3. **Parse Handover Documents**
   - Extract current state from CONTEXT.md
   - Extract implementation notes from NOTES.md
   - Extract task breakdown from PLAN.md

4. **Auto-Detect Workflow Step**
   - Analyze file substates (need-draft, need-completion, need-fixing, etc.)
   - Check current phase status
   - Determine appropriate write-code workflow step to resume

5. **Consult User on Decisions**
   - Present any pending decisions from PLAN.md
   - Get user input on approach
   - Record decisions for execution

### Step 2: Update Handover

- Update CONTEXT.md with decisions made
- Update PLAN.md with unblocked tasks
- Remove decision markers for resolved items

### Step 3: Execute Work

1. **Delegate to Coding Subagent**
   - Pass complete context package
   - Include detected workflow step
   - Include user decisions and guidance

2. **Validate Completion**
   - Run tests for modified files
   - Run diagnostics to check for new errors
   - Verify planned actions complete

3. **Update Handover Documentation**
   - Run `/coding:handover` to update files
   - Capture latest state

### Step 4: Reporting

**Output Format**:

```
[✅] Takeover: $ARGUMENTS

## Handover Summary
- Files: CONTEXT.md, NOTES.md, PLAN.md at [path]
- Last Updated: [timestamp]
- Branch: [branch name]

## Diagnostics Summary
- Type Errors: [count]
- Test Failures: [count]
- Lint Violations: [count]

## Detected Workflow Step
**Step [N]: [Step Name]** from write-code.md
**Rationale**: [explanation]

## Files in Scope
### 🚧 In Progress ([count])
- [file path] - [substate]

### 📋 Planned ([count])
- [file path] - [substate]

## Tasks Executed
- [count] tasks completed
- [count] actions executed

## Next Action
[What to do next]
```

## 📝 Examples

### Simple Usage

```bash
/takeover
# Reads default handover files (CONTEXT.md, NOTES.md, PLAN.md)
# Auto-detects workflow step
# Continues work
```

### With Prefix

```bash
/takeover sprint1
# Reads sprint1-CONTEXT.md, sprint1-NOTES.md, sprint1-PLAN.md
# Continues sprint-specific work
```

### Error Case

```bash
/takeover
# Error: One or more handover files not found
# Suggestion: Create handover first with `/coding:handover`
```
