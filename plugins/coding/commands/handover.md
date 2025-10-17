---
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion

argument-hint: [prefix]

description: Create/update detailed work handover notes for seamless continuation
---

# Work Handover Documentation

Generates comprehensive handover documentation capturing current project & work context across three complementary files: CONTEXT.md (status & decisions), NOTES.md (implementation insights & solutions), and PLAN.md (goals & tasks) for seamless project continuation without requiring prior context

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not perform git operations like commit, push, or branch management
- Does not execute project builds, tests, or deployments
- Does not analyze code quality or perform code reviews
- Does not modify any project files except the handover documents themselves
- Does not replace project management tools or issue tracking systems

**When to REJECT**:

- When file path argument points to non-markdown files
- When requested to perform git operations instead of documentation
- When asked to modify project source code
- When the working directory is not a git repository
- When user requests code analysis instead of handover documentation

- Untracked files: !`git ls-files --others --exclude-standard`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 0: Analyze Project Context

Before performing handover documentation, deeply analyze the complete project context:

- **Project State Analysis**: Examine git status, recent commits, file changes to understand current work trajectory
- **Existing Work Review**: Read all current todos from TodoRead to understand ongoing tasks and their status
- **Context Discovery**: Identify background, goals, decisions from project docs and commit history
- **Pattern Recognition**: Detect architectural patterns, established conventions, recurring issues
- **Comprehensive Synthesis**: Integrate all gathered context into coherent handover documentation

### Step 1: Parse Arguments and Validate

- Extract the optional prefix argument from $ARGUMENTS
- If no prefix provided, use empty prefix (default files: CONTEXT.md, NOTES.md, PLAN.md)
- If prefix provided, construct file names: [prefix]-CONTEXT.md, [prefix]-NOTES.md, [prefix]-PLAN.md
- Validate prefix format (no slashes, no extensions)
- Verify the working directory is a git repository
- If validation fails, reject with clear error message

**File naming examples**:

- Default: `CONTEXT.md`, `NOTES.md`, `PLAN.md`
- With prefix: `sprint1-CONTEXT.md`, `sprint1-NOTES.md`, `sprint1-PLAN.md`

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

**Pruning Rules**:

- **Proactive Content Removal**: When writing to handover docs, the agent MUST proactively remove any content that is not useful for future execution phases, including:
  - Outdated context that no longer affects current work
  - Resolved issues and their detailed resolution steps (keep only lessons learned)
  - Detailed descriptions of completed tasks (keep file path + brief summary only)
  - Stale references to deprecated patterns or removed dependencies
  - Historical discussions that don't inform current decisions
  - Verbose background information that can be condensed
- Keep only last 5 commits in "Recent Changes" (archive older commits to Historical Notes)
- Condense completed files into summary statements (e.g., "15 files completed" with top 3-5 listed)
- Rewrite sections exceeding 100 lines to focus on actionable items only
- Consolidate similar gotchas/decisions into single entries
- Remove detailed descriptions of completed tasks (keep file path + brief summary only)
- Archive verbose historical content to "Historical Notes" section at document bottom
- Remove outdated context that no longer affects current work

Search for and document (with pruning applied):

**For CONTEXT.md**:

- Background & context - why this work is being done (concise, actionable only; remove outdated context)
- Goals & objectives - current goals only (remove completed goals)
- Reference documents - active/relevant links only (remove stale links)
- Important decisions made - recent and impactful only (consolidate similar decisions)
- Architectural patterns used - current patterns only (remove deprecated patterns)
- Gotchas and workarounds - consolidate similar items
- Dependencies added or modified - recent changes only
- Configuration changes - current config only (remove historical config)

**For NOTES.md**:

- **Implementation Issues**: Problems encountered during implementation that required multiple tool calls to resolve
- Solutions applied - keep distinct solutions for issues faced (merge duplicates)
- Exploration attempts - keep failures only if relevant to understanding current state
- Key discoveries - document insights from actual implementation challenges
- Workarounds - document any temporary workarounds that might be needed
- Dependencies & gotchas - issues that took time to discover and understand
- Keep entries concise and actionable - only document what was learned through doing

**For PLAN.md**:

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

### Step 5: Consult User on Key Decisions

Before documenting any information in the handover files, identify and consult the user on all high-level decisions that require user input. You MUST NOT make architectural, technical, or strategic decisions without user consultation.

**Actions**:

1. **Identify Decision Points**:
   - Review all gathered context from Steps 0-4
   - Extract any technical choices mentioned in:
     - TODO comments requiring decisions (e.g., "TODO: decide between Redis vs Memcached")
     - Architecture patterns pending selection
     - Library/framework choices not yet finalized
     - Implementation approaches with multiple valid options
     - Feature scope or priority decisions
     - Configuration or deployment strategy choices
   - Identify any assumptions you would make without user input

2. **Categorize Decisions**:
   - **Architectural Decisions**: System design patterns, component structure, data flow
   - **Technology Choices**: Libraries, frameworks, tools, services
   - **Implementation Approaches**: Algorithm choices, optimization strategies, design patterns
   - **Scope Decisions**: Feature prioritization, MVP boundaries, phasing
   - **Configuration**: Environment setup, deployment strategies, scaling approaches

3. **Consult User with AskUserQuestion**:
   - For EACH identified decision:
     - Present the decision clearly with context
     - Provide 3-5 viable options with brief pros/cons
     - ALWAYS include these TWO special options:
       - **"Defer decision"** - Document as open question in handover
       - **"Perform research"** - Launch deep research subagent, save results
     - Use AskUserQuestion tool with format:

       ```
       Decision: [Clear statement of what needs to be decided]
       Context: [Why this decision matters, from project analysis]

       Options:
       1. [Option 1] - [Brief rationale and trade-offs]
       2. [Option 2] - [Brief rationale and trade-offs]
       3. [Option 3] - [Brief rationale and trade-offs]
       4. Perform research - Launch deep research on this topic
       5. Defer decision - Document as open question in handover
       ```

   - Record user's choice for each decision
   - Handle user selections appropriately

4. **Process Decision Outcomes**:

   **For finalized decisions:**
   - Store decision with rationale for CONTEXT.md "Key Decisions & Patterns" section
   - Note technical choices for CONTEXT.md "Dependencies & Configuration" section
   - Prepare implementation tasks for PLAN.md

   **For "Perform research" selections:**
   - Launch Task tool with subagent_type="general-purpose" for deep research
   - Provide comprehensive research prompt including:
     - Decision context and importance
     - Key questions to answer
     - Trade-offs to explore
     - Best practices to identify
   - Save research output as `research-[topic-slug].md` in working directory
   - Add to PLAN.md: "📊 **RESEARCH AVAILABLE**: Review research-[topic].md and decide on [topic]"
   - Reference research file in NOTES.md under "Open Questions" section

   **For "Defer decision" selections:**
   - Mark for inclusion in NOTES.md "Open Questions" section
   - Prepare for PLAN.md: "⚠️ **DECISION REQUIRED**: [Topic] - See NOTES.md Open Questions"
   - Identify tasks blocked by this decision

5. **Handle Multiple Decisions**:
   - If 5+ decisions identified, prioritize:
     - Critical architectural decisions first
     - Technology choices affecting multiple components
     - Decisions blocking immediate next steps
     - Lower priority decisions can be batched or deferred
   - Group related decisions together when presenting to user
   - Process decisions sequentially to allow informed choices

**Example Decision Consultation**:

```
Decision: Caching Strategy for User Sessions
Context: Analysis shows 3 TODO comments about session management.
System has high read load (from git commit messages mentioning performance).

Options:
1. Redis - Industry standard, persistent, supports clustering (requires Redis setup)
2. Memcached - Simpler, faster for pure caching (loses data on restart)
3. In-memory with Node - No external deps (doesn't scale across instances)
4. Perform research - Launch deep research on caching strategies
5. Defer decision - Document as open question, use simple approach for now

[If user selects option 1: Redis]
→ Store in decisions: "Use Redis for session caching - provides persistence and clustering"
→ Prepare for CONTEXT.md: "Key Decisions & Patterns" and "Dependencies & Configuration"
→ Prepare for PLAN.md: "Set up Redis for session caching"

[If user selects "Perform research"]
→ Launch research agent on "session caching strategies for high-load Node.js applications"
→ Save results to research-session-caching.md
→ Prepare for PLAN.md: "📊 Review research-session-caching.md and decide on caching strategy"
→ Prepare for NOTES.md: Link to research file in "Open Questions"

[If user selects "Defer decision"]
→ Prepare for NOTES.md: "Open Questions - Session Caching Strategy: Redis vs Memcached vs in-memory"
→ Prepare for PLAN.md: "⚠️ DECISION REQUIRED: Session caching strategy - See NOTES.md"
→ Identify blocked tasks: "Implement session persistence - ⏸️ Blocked by caching decision"
```

**Important Notes**:

- NEVER skip this step even if "decisions seem obvious"
- ALWAYS provide both "Perform research" and "Defer decision" options
- If user is unavailable/non-responsive, treat ALL decisions as "Deferred"
- Prefer asking 3-4 focused questions over making assumptions
- Document both the decision AND the alternatives considered
- For research requests, ensure comprehensive investigation and save results

### Step 6: Generate or Update Handover Documents

**First, generate current timestamp**:

- Execute: `date -u +"%Y-%m-%dT%H:%M:%SZ"` to get current ISO 8601 timestamp
- Store the result to use consistently across all documents
- Use this actual timestamp (not placeholders) for all "Last Updated", "Created", "Updated" fields

**Then, prepare decision-based content from Step 5**:

Before generating/updating documents, organize all decision outcomes from Step 5:

- **Finalized Decisions**: List of decisions made with rationale and alternatives considered
- **Deferred Decisions**: List of decisions deferred with context for future resolution
- **Research Files**: List of generated research files with their topics
- **Decision-Driven Tasks**: New tasks resulting from finalized decisions
- **Blocked Tasks**: Tasks that cannot proceed due to deferred decisions

**Apply Pruning Principles**: Before updating or creating files, remember to proactively remove any content that is not useful for future execution phases (see Step 4 pruning rules). This ensures handover documentation remains focused and actionable.

If the files exist:

- Read the existing content of each file
- Update the "Last Updated" timestamp with the actual current timestamp from `date` command
- Refresh dynamic sections (Current State, File Status, Recent Changes)
- **Integrate decision outcomes from Step 5**:
  - Add finalized decisions to CONTEXT.md "Key Decisions & Patterns"
  - Add deferred decisions to NOTES.md "Open Questions"
  - Update PLAN.md with decision-driven tasks and blocked tasks
  - Reference research files in NOTES.md
- Append new items where appropriate
- Preserve historical content

If the files don't exist:

- Create new documents with complete structure for all three files
- Use actual timestamp from `date` command for all timestamp fields
- **Include decision outcomes from Step 5** in initial content

**CONTEXT.md Structure**:

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

- **Decision**: [what was decided - from Step 5 finalized decisions OR from code/commits]
  **Rationale**: [why it was decided - include alternatives considered from Step 5]
  **Impact**: [what it affects]
  **Alternatives Considered**: [options that were evaluated but not chosen - from Step 5]

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

**NOTES.md Structure**:

Note: All dates and timestamps in NOTES.md must use ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
Generate timestamp with: `date -u +"%Y-%m-%dT%H:%M:%SZ"`

```markdown
# Implementation Notes - [Project Name]

**Last Updated**: [Use actual timestamp from `date -u +"%Y-%m-%dT%H:%M:%SZ"`]
**Purpose**: Document issues encountered during implementation that required multiple tool calls to resolve

## Implementation Issues Resolved

### Issue: [Description]
**Problem**: [What went wrong, when encountered]
**Symptoms**: [How it manifested]
**Root Cause**: [Why it happened, if discovered]
**Solution**: [How it was fixed - what multiple steps/tool calls were needed]
**Lessons Learned**: [Key insight for future similar issues]

### Issue: [Another implementation challenge]
...

## Quick Workarounds

- [Temporary solution for common issue] - [why needed]
- [Dependency/gotcha discovered] - [how it affects work]

## Open Questions

- [Unresolved question - from Step 5 deferred decisions OR from code/comments]
- [Uncertainty needing resolution]
- **[Decision Topic]**: [Context and options to consider - from Step 5 deferred decisions]
  - Research available: [Link to research-[topic].md if "Perform research" was selected]

## Quick Tips for Next Agent

- [Time-saving tip from implementation challenges]
- [Gotcha to watch out for]
- [Effective approach that worked]
```

**PLAN.md Structure**:

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
- [ ] [Decision-driven task from Step 5 finalized decisions]
- [ ] ⏸️ [Blocked task] - Blocked by [decision from Step 5]

### Decisions & Research

- ⚠️ **DECISION REQUIRED**: [Topic from Step 5 deferred decisions] - See NOTES.md Open Questions
- 📊 **RESEARCH AVAILABLE**: Review research-[topic].md and decide on [topic from Step 5 "Perform research" selections]

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

### Step 7: Reporting

**Output Format**:

```
[✅] Handover: $ARGUMENTS

## Summary
- Context file: [path to CONTEXT.md]
- Notes file: [path to NOTES.md]
- Plan file: [path to PLAN.md]
- Files classified: [count]
- Completed: [count] | In Progress: [count] | Planned: [count]
- Implementation notes: [X issues resolved, Y workarounds, Z tips]
- Plan tasks: [count] across [phases] phases
- Recent commits analyzed: [count]
- Todos incorporated: [count from TodoRead] ([completed]/[in_progress]/[pending])
- **Decisions consulted: [count identified] ([finalized]/[deferred]/[researched])**
- **Plan updates: [count decision-driven tasks added], [count blocked tasks identified]**
- **Research files generated: [count] - [list of research-[topic].md files]**

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

### NOTES.md
- Implementation Issues: ✓/X
- Quick Workarounds: ✓/X
- Open Questions: ✓/X
- Quick Tips: ✓/X

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
# - NOTES.md: Implementation issues encountered
# - PLAN.md: Goals, tasks
```

### Custom File Prefix

```bash
/handover sprint1
# Creates or updates:
# - sprint1-CONTEXT.md: Current status and decisions
# - sprint1-NOTES.md: Implementation insights and solutions
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
/handover sprint1/phase
# Error: Invalid prefix format (contains slashes)
# Suggestion: Use simple prefix like 'sprint1' or '/handover' for default

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

**2. Read NOTES.md second** → Learn from implementation

- Issues encountered and how they were solved
- Workarounds for common gotchas
- Quick tips discovered during implementation

**3. Read PLAN.md third** → Know the path forward

- Overall goals and success criteria
- Task breakdown by phase
- Dependencies

This trio provides complete project understanding for seamless continuation.

### Continuation Scenario

The /takeover command automatically reads all three handover files to provide complete project understanding for seamless continuation:

- **CONTEXT.md**: Current status verification, file states, decisions, and gotchas
- **NOTES.md**: Implementation insights and solutions to avoid re-discovering issues
- **PLAN.md**: Prioritized task list and clear path forward
