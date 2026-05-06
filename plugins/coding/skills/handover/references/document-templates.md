# Handover Document Templates

Use these structures when generating or updating CONTEXT.md, NOTES.md, and PLAN.md in Step 6. All dates and timestamps must use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`. Generate timestamp with: `date -u +"%Y-%m-%dT%H:%M:%SZ"`.

## CONTEXT.md Structure

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

## NOTES.md Structure

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

## PLAN.md Structure

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
