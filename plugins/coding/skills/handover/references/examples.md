# Handover Examples

## Simple Usage

```bash
/handover
# Creates 3 files with current project state:
# - CONTEXT.md: Status, files, decisions
# - NOTES.md: Implementation issues encountered
# - PLAN.md: Goals, tasks
```

## Custom File Prefix

```bash
/handover sprint1
# Creates or updates:
# - sprint1-CONTEXT.md: Current status and decisions
# - sprint1-NOTES.md: Implementation insights and solutions
# - sprint1-PLAN.md: Goals and task breakdown
```

## Update Existing

```bash
/handover
# If files exist, updates them with:
# - New timestamp
# - Refreshed current state
# - Updated file classifications
# - New recent changes appended
```

## Error Case Handling

```bash
/handover sprint1/phase
# Error: Invalid prefix format (contains slashes)
# Suggestion: Use simple prefix like 'sprint1' or '/handover' for default

/handover
# Error: Not a git repository
# Suggestion: Initialize git with 'git init' or navigate to a git repository
```

## Three-File Workflow

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

## Continuation Scenario

The /takeover command automatically reads all three handover files to provide complete project understanding for seamless continuation:

- **CONTEXT.md**: Current status verification, file states, decisions, and gotchas
- **NOTES.md**: Implementation insights and solutions to avoid re-discovering issues
- **PLAN.md**: Prioritized task list and clear path forward
