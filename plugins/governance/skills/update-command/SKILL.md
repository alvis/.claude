---
name: update-command
description: Update slash commands to latest standards with optional specific area changes. Use when modernizing existing commands, applying template updates, or standardizing command structure.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [command specifier] [--changes=...]
---

# Update Commands

Update existing slash commands to follow current best practices and template structure. Parses $ARGUMENTS to identify both target commands and specific areas to change. Commands will be upgraded to the latest template with clean, comment-free output and change any content in relate to the specified changes. Intelligently extracts change requirements from arguments, adds missing sections from template, removes all comments, preserves custom functionality, and make sure all the changes are clearly reflected in the command file. Ultrathink mode.

## Purpose & Scope

**What this command does NOT do**:

- Change command core functionality
- Delete custom sections or examples
- Modify commands in other directories
- Update non-markdown files

**When to REJECT**:

- Command doesn't exist
- Invalid target specification
- Non-markdown files specified
- For creating new commands (use create-command instead)
- When commands are already compliant
- For non-command markdown files

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.

- **If present**: Use **Team Mode** (Step 2A)
- **If absent**: Use **Subagent Mode** (Step 2B)

### Step 2A: Team Mode (Agent Teams enabled)

Lead Orchestrator coordinates Command Update Specialist teammates (opus) to update command files in parallel against template:command. For the full Phase 1–4 procedure (planning, team setup, work cycle with verbatim subagent prompt, aggregation/cleanup) and the agent summary table, see `references/team-mode.md`.

### Step 2B: Subagent Mode (fallback)

Execute the existing workflow with parallel subagents — apply template alignment, change requests, standards enforcement, and verify quality before reporting. For full procedure (planning steps, verification of QA and side effects), see `references/subagent-mode.md`.

### Reporting

**Output Format**:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Execution mode: [team/subagent]
- Files modified: [count]
- Commands updated: [count/total]
- Specific areas changed: [list]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Skills Applied (subagent mode)
- [Skill name]: [Status]

## Teammate Results (team mode only)
- Total agents deployed: [count]
- Successful updates: [count]
- Failed updates: [count] (if any)

## Updated Commands
- [command-name]: [Status] - [Changes applied]
- [command-name]: [Status] - [Changes applied]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]

## Next Steps (if applicable)
- [Required manual action]
- [Recommended follow-up]
```

## Examples

### Update All Commands (Team Mode)

```bash
/update-command all
# With CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1:
# - Creates update-command-team
# - Spawns parallel Command Update Specialists (one per command)
# - Each specialist updates command with template alignment
# - Aggregates results and reports execution mode: team
```

### Update All Commands (Subagent Mode)

```bash
/update-command all
# Without agent teams:
# - Uses traditional subagent delegation
# - Updates every command in .claude/commands/
# - Reports execution mode: subagent
```

### Update Specific Command

```bash
/update-command fix-issue
# Updates only fix-issue.md
```

### Update with Specific Area

```bash
/update-command "update-command" --area="argument parsing"
# Updates update-command.md focusing on argument parsing section
```

### Update with Change Description

```bash
/update-command "create-component" --changes="include TypeScript types in examples"
# Updates create-component.md to add TypeScript types to examples
```

### Update Namespace

```bash
/update-command "dev/*"
# Updates all commands in dev/ subdirectory
```

### Selective Update with Areas

```bash
/update-command "analyze-code review-pr" --area="workflow phase 2"
# Updates specific commands focusing on execution phase
```

### Complex Update Request

```bash
/update-command "commit" --changes="include git hooks validation in workflow"
# Intelligently parses to update commit.md adding git hooks to workflow
```

### Error Case Handling

```bash
/update-command "invalid-target"
# Error: Target not found
# Suggestion: Check available commands with 'ls .claude/commands/'
# Alternative: Use '/update-command all' to update all commands
```
