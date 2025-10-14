---
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead

argument-hint: [--files=CONTEXT.md,RESEARCH.md,PLAN.md]

description: Create/update detailed work handover notes for seamless continuation
---

# Work Handover Documentation

Generates comprehensive handover documentation capturing current project & work context across three complementary files: CONTEXT.md (status & decisions), RESEARCH.md (documentation & learnings), and PLAN.md (goals & tasks) for seamless project continuation without requiring prior context

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Does not perform git operations like commit, push, or branch management
- Does not execute project builds, tests, or deployments
- Does not analyze code quality or perform code reviews
- Does not modify any project files except the handover documents themselves
- Does not replace project management tools or issue tracking systems

**When to REJECT:**

- When file path argument points to non-markdown files
- When requested to perform git operations instead of documentation
- When asked to modify project source code
- When the working directory is not a git repository
- When user requests code analysis instead of handover documentation

## 📊 Dynamic Context

- **[IMPORTANT]** At the start of the command, you MUST run the command to load all the context below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`
- Modified files: !`git diff --name-only`
- Staged files: !`git diff --cached --name-only`
- Untracked files: !`git ls-files --others --exclude-standard`

### Project Context

- Workflows: !`find ~/.claude/constitutions/workflows "$(git rev-parse --show-toplevel)/constitutions/workflows" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g' | sort -u`
- Standards: !`find ~/.claude/constitutions/standards "$(git rev-parse --show-toplevel)/constitutions/standards" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g' | sort -u`

## 🔄 Workflow

ultrathink: Before performing any steps, deeply analyze the complete project context:

- **Project State Analysis**: Examine git status, recent commits, file changes to understand current work trajectory
- **Existing Work Review**: Read all current todos from TodoRead to understand ongoing tasks and their status
- **Context Discovery**: Identify background, goals, decisions from project docs and commit history
- **Pattern Recognition**: Detect architectural patterns, established conventions, recurring issues
- **Comprehensive Synthesis**: Integrate all gathered context into coherent handover documentation

Then perform the following steps:

### Step 1: Parse Arguments and Validate

- Extract the --files argument from $ARGUMENTS
- If no --files provided, use empty prefix (default files: CONTEXT.md, RESEARCH.md, PLAN.md)
- If --files=prefix provided, extract prefix (generates: prefix-CONTEXT.md, prefix-RESEARCH.md, prefix-PLAN.md)
- Validate that all three file paths will end with .md extension
- Verify the working directory is a git repository
- If validation fails, reject with clear error message

**File naming examples:**

- Default: `CONTEXT.md`, `RESEARCH.md`, `PLAN.md`

### Step 2: Discover Project Context

- Use TodoRead to retrieve all existing todos from the task tracker
- Organize todos by status for inclusion in PLAN.md:
- Preserve task relationships and dependencies if indicated in task content
- Note any context or patterns from task descriptions
- Run git commands to gather current state (branch, status, recent commits)
- Capture recent commit messages for context on what was done

### Step 3: Classify File Status

Classify each file into one of three categories with detailed substates:

- **✅ Completed**: Files that are committed and unchanged (not in git status output)
- **🚧 In Progress**: Files that are modified or staged (in git diff or git diff --cached), with substates:
  - `need-completion`: Files with TODO/FIXME comments indicating incomplete implementation
  - `need-fixing`: Files with test failures, errors, or HACK/WORKAROUND comments
  - `need-linting`: Files with linting/formatting issues or style violations
  - `need-refactoring`: Files with REFACTOR comments or code quality concerns
- **📋 Planned**: Untracked files or files mentioned in TODO comments, with substates:
  - `need-draft`: Untracked files or files with mostly TODOs requiring initial skeleton
  - `need-testing`: Files without corresponding test files or lacking test coverage

For each file, gather:

- File path and type
- Current status with substate (e.g., "🚧 need-completion", "📋 need-draft")
- Relevant TODO/FIXME/REFACTOR comments if present
- Brief description of what specifically needs to be done
- Any blockers or dependencies

### Step 4: Extract Key Information and Apply Intelligent Pruning

When updating existing handover files, apply intelligent pruning to keep documentation focused and actionable:

**Pruning Rules:**

- Keep only last 5 commits in "Recent Changes" (archive older commits to Historical Notes)
- Condense completed files into summary statements (e.g., "15 files completed" with top 3-5 listed)
- Rewrite sections exceeding 100 lines to focus on actionable items only
- Consolidate similar gotchas/decisions into single entries
- Remove detailed descriptions of completed tasks (keep file path + brief summary only)
- Archive verbose historical content to "Historical Notes" section at document bottom
- Remove outdated context that no longer affects current work

Search for and document (with pruning applied):

**For CONTEXT.md:**

- Background & context - why this work is being done (concise, actionable only; remove outdated context)
- Goals & objectives - current goals only (remove completed goals)
- Reference documents - active/relevant links only (remove stale links)
- Important decisions made - recent and impactful only (consolidate similar decisions)
- Architectural patterns used - current patterns only (remove deprecated patterns)
- Gotchas and workarounds - consolidate similar items
- Dependencies added or modified - recent changes only
- Configuration changes - current config only (remove historical config)

**For RESEARCH.md:**

- Documentation URLs - active references only (remove obsolete docs)
- Stack Overflow/GitHub issue links - still relevant only
- API documentation references - current API versions
- Problems encountered - consolidate similar problems
- Solutions applied - keep distinct solutions (merge duplicates)
- Exploration attempts - keep failures only if still relevant
- Insights and discoveries - merge similar insights
- Open questions - current questions only (remove answered)
- What approaches worked - distinct approaches only
- What approaches didn't work - keep if relevant to future work

**For PLAN.md:**

- Goals breakdown - current goals
- Task lists - incomplete tasks only, archive completed
- Phases/milestones - active phases (archive completed)
- Dependencies - current dependencies only
- Decisions made - impactful decisions only
- Risks identified - active risks only
- Success criteria - unmet criteria only
- Current todos - actionable items only
- Task progress - incomplete tasks focus
- Pending work items - prioritized items

### Step 5: Generate or Update Handover Documents

**First, generate current timestamp:**

- Execute: `date -u +"%Y-%m-%dT%H:%M:%SZ"` to get current ISO 8601 timestamp
- Store the result to use consistently across all documents
- Use this actual timestamp (not placeholders) for all "Last Updated", "Created", "Updated" fields

If the files exist:

- Read the existing content of each file
- Update the "Last Updated" timestamp with the actual current timestamp from `date` command
- Refresh dynamic sections (Current State, File Status, Recent Changes)
- Append new items where appropriate
- Preserve historical content

If the files don't exist:

- Create new documents with complete structure for all three files
- Use actual timestamp from `date` command for all timestamp fields

**CONTEXT.md Structure:**

Note: All dates and timestamps in CONTEXT.md must use ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
Generate timestamp with: `date -u +"%Y-%m-%dT%H:%M:%SZ"`

```markdown
# Work Handover - [Project Name]

**Last Updated**: [Use actual timestamp from `date -u +"%Y-%m-%dT%H:%M:%SZ"`]
**Current Branch**: [branch name]
**Working Directory**: [pwd]

## Background & Context

Why this work is being done - business context, problem being solved, user need.
Sources: README.md, DESIGN.md, commit messages, code comments.

## Goals & Objectives

What this work aims to achieve - specific outcomes and success criteria.
Include: completion targets, test coverage goals, deadlines if mentioned.

## Reference Documents

- Design docs, specifications, architecture docs
- Tickets, issues, PRs with links
- Related documentation or external resources

## Current State

Brief summary of where the work currently stands (2-3 sentences).

## File Status

### 🚧 In Progress
- `path/to/file.ts` (need-completion) - 3 TODOs remaining: logout, error handling, tests
- `path/to/file.ts` (need-fixing) - 2 failing tests, auth flow error
- `path/to/file.ts` (need-linting) - TypeScript strict mode violations
- `path/to/file.ts` (need-refactoring) - complexity reduction needed, extract utilities

### 📋 Planned
- `path/to/file.ts` (need-draft) - Modal component skeleton needed
- `path/to/file.ts` (need-testing) - Form component needs test coverage

### ✅ Completed
- 15 files completed (details archived to Historical Notes)
- Recent: Button.tsx, validation.ts, button.test.tsx

## Historical Notes (Archived)
[Older completed items details, commits beyond last 5, verbose descriptions...]

## Recent Changes

### [Date] - [Commit hash]
- Change description from commit message
- Key files affected

## Key Decisions & Patterns

- **Decision**: [what was decided]
  **Rationale**: [why it was decided]
  **Impact**: [what it affects]

## Gotchas & Workarounds

- **Issue**: [problem encountered]
  **Workaround**: [how it was handled]
  **Location**: [file:line]

## Dependencies & Configuration

- Package/library added: version and purpose
- Config changes: what and why

## Next Steps

1. [Immediate next action with context]
2. [Following action]
3. [Future consideration]

## Context for Continuation

Additional context needed to pick up this work:
- Background information
- Related documentation
- Testing considerations
```

**RESEARCH.md Structure:**

Note: All dates and timestamps in RESEARCH.md must use ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
Generate timestamp with: `date -u +"%Y-%m-%dT%H:%M:%SZ"`

```markdown
# Research Notes - [Project Name]

**Last Updated**: [Use actual timestamp from `date -u +"%Y-%m-%dT%H:%M:%SZ"`]
**Related Work**: [brief description from Background & Context]

## Documentation References

### Official Documentation
- [package/API]: [URL] - [what was learned/why consulted]

### Community Resources
- Stack Overflow: [URL] - [problem it solved]
- GitHub Issues: [URL] - [relevant discussion]
- Blog Posts: [URL] - [key insights]

## Problems & Solutions

### Problem: [Description]
**Encountered**: [when/where in codebase]
**Symptoms**: [what went wrong]
**Root Cause**: [why it happened, if known]
**Solution**: [how it was fixed]
**References**: [relevant links]

## Explorations

### What Worked
- [approach] - [why effective] - [where used]

### What Didn't Work
- [attempted approach] - [why failed] - [lesson learned]

## Key Insights

- [Important discovery]
- [Pattern identified]
- [Performance/security consideration]

## Open Questions

- [Unresolved question]
- [Uncertainty needing resolution]

## Quick Tips for Next Agent

- [Time-saving tip]
- [Common pitfall to avoid]
- [Best resource for understanding X]
```

**PLAN.md Structure:**

Note: All dates and timestamps in PLAN.md must use ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
Generate timestamp with: `date -u +"%Y-%m-%dT%H:%M:%SZ"`

```markdown
# Work Plan - [Project Name]

**Created**: [Use actual timestamp from `date -u +"%Y-%m-%dT%H:%M:%SZ"` on first creation, preserve on updates]
**Updated**: [Use actual timestamp from `date -u +"%Y-%m-%dT%H:%M:%SZ"`]
**Status**: [In Progress/Blocked/Complete]

## Goals & Objectives

### Primary Goal
[From Background & Context]

### Success Criteria
- [ ] [Measurable criterion from Goals & Objectives]
- [ ] [Another criterion]

## Task Breakdown

### Phase 1: [Phase Name] (Status: Completed/In Progress/Pending)
**Goal**: [What this achieves]

Tasks:
- [x] [Completed task from git commits or completed todos]
- [x] [Completed task from TodoRead marked completed]
- [ ] [In-progress task from modified files or in_progress todos]
- [ ] [In-progress task from TodoRead marked in_progress]
- [ ] [Planned task from TODO comments or pending todos]
- [ ] [Planned task from TodoRead marked pending]

### Phase 2: [Next phase...]

## Dependencies

### External
- [Package/service] - [what provides] - [status]

### Internal
- [File/module] needs [other file] first
- [Decision] needed before [task]

## Risks & Mitigation

### Risk: [From FIXME/HACK comments]
**Impact**: [High/Medium/Low]
**Mitigation**: [Strategy]

## Decision Log

### Decision: [What was decided]
**Date**: [Use actual timestamp from `date -u +"%Y-%m-%dT%H:%M:%SZ"` or extract from commit date]
**Rationale**: [why - from Key Decisions]
```

### Step 6: Reporting

**Output Format:**

```
[✅] Handover: $ARGUMENTS

## Summary
- Context file: [path to CONTEXT.md]
- Research file: [path to RESEARCH.md]
- Plan file: [path to PLAN.md]
- Files classified: [count]
- Completed: [count] | In Progress: [count] | Planned: [count]
- Research notes: [X refs, Y problems/solutions, Z insights]
- Plan tasks: [count] across [phases] phases
- Recent commits analyzed: [count]
- Todos incorporated: [count from TodoRead] ([completed]/[in_progress]/[pending])

## Document Sections

### CONTEXT.md
- Background & Context: ✓/X
- Goals & Objectives: ✓/X
- Reference Documents: ✓/X
- Current State: ✓/X
- File Status: ✓/X
- Recent Changes: ✓/X
- Key Decisions: ✓/X
- Next Steps: ✓/X

### RESEARCH.md
- Documentation References: ✓/X
- Problems & Solutions: ✓/X
- Explorations: ✓/X
- Key Insights: ✓/X
- Open Questions: ✓/X

### PLAN.md
- Goals & Success Criteria: ✓/X
- Task Breakdown: ✓/X
- Dependencies: ✓/X
- Timeline: ✓/X
- Risks & Mitigation: ✓/X

## File Status Breakdown
### ✅ Completed ([count])
[first 3 files...]

### 🚧 In Progress ([count])
[all in-progress files...]

### 📋 Planned ([count])
[all planned files...]

## Next Steps Identified
1. [immediate next action]
2. [following action]

## Notes
- [Any important observations]
- [Suggestions for continuation]
```

## 📝 Examples

### Simple Usage

```bash
/handover
# Creates 3 files with current project state:
# - CONTEXT.md: Status, files, decisions
# - RESEARCH.md: References, problems/solutions, insights
# - PLAN.md: Goals, tasks
```

### Custom File Prefix

```bash
/handover --files=sprint1
# Creates or updates:
# - sprint1-CONTEXT.md: Current status and decisions
# - sprint1-RESEARCH.md: Research and learnings
# - sprint1-PLAN.md: Goals and task breakdown
```

### Update Existing

```bash
/handover
# If files exist, updates them with:
# - New timestamp
# - Refreshed current state
# - Updated file classifications
# - New recent changes appended
```

### Error Case Handling

```bash
/handover --files=tasks.txt
# Error: Handover files must be markdown files (.md extension)
# Suggestion: Use '/handover --files=sprint1' or '/handover' for default

/handover
# Error: Not a git repository
# Suggestion: Initialize git with 'git init' or navigate to a git repository
```

### Three-File Workflow

After running /handover, three complementary files work together:

**1. Read CONTEXT.md first** → Understand current status

- What files are done/in-progress/planned
- Key decisions made
- Gotchas to watch out for

**2. Read RESEARCH.md second** → Learn from research

- Documentation already consulted
- Problems already solved
- What approaches worked/failed

**3. Read PLAN.md third** → Know the path forward

- Overall goals and success criteria
- Task breakdown by phase
- Dependencies

This trio provides complete project understanding for seamless continuation.

### Continuation Scenario

The /takeover command automatically reads all three handover files to provide complete project understanding for seamless continuation:

- **CONTEXT.md**: Current status verification, file states, decisions, and gotchas
- **RESEARCH.md**: Research insights to avoid re-work and failed approaches
- **PLAN.md**: Prioritized task list and clear path forward
