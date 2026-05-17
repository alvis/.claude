---
name: update-command
description: Update slash commands to latest standards with optional specific area changes. Use when modernizing existing commands, applying template updates, or standardizing command structure.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite
argument-hint: [command specifier] [--changes=...]
---

# Update Commands

Update existing slash commands to follow current best practices and template structure. Parses $ARGUMENTS to identify both target commands and specific areas to change, upgrades commands to the latest template with clean, comment-free output, intelligently extracts change requirements, adds missing sections from template, removes all comments, preserves custom functionality, and ensures all changes are clearly reflected in the command file. Ultrathink mode. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. Change requests must therefore reshape the existing sections in place: a "Behavior change" addendum at the bottom of a command file, or a parallel "Updated workflow" block sitting beside the original workflow, is precisely the failure mode this skill must refuse to produce.

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

### Step 1: Subagent Orchestration

Spawn parallel specialized subagents (max 8 parallel `Task` calls per dispatch) to execute the workflow against `template:command` — apply template alignment, change requests, standards enforcement, and verify quality before reporting.

#### Planning

1. **Skill Compliance**
   - MUST follow skills identified in Phase 1
   - If no skill exists, follow project conventions
   - Reference specific skill files when applicable

2. **Primary Implementation**
   - Apply specific area changes from parsed arguments
   - Add missing sections from template
   - Update targeted sections per change requests
   - Reorganize content to match structure
   - Migrate existing content appropriately
   - Update the content such that the changes are clearly reflected

3. **Standards Enforcement**
   - Apply standards from `[plugin]/constitution/standards/`
   - Follow template structure
   - No instruction comments copied from the template
   - Ensure targeted changes align with standards

4. **Edge Case Handling**
   - Preserve custom useful content
   - Handle missing sections gracefully
   - Maintain backward compatibility

#### Verification

1. **Quality Assurance**
   - Verify NO comments remain
   - Check markdown formatting and structure
   - Validate frontmatter syntax and completeness
   - Verify all requested changes implemented

2. **Side Effect Validation**
   - Core functionality preserved
   - Custom content maintained
   - Template compliance achieved

#### Aggregation

- Track completion status of each delegated command
- Handle any subagent failures or escalations
- Aggregate per-subagent results into the final Step 2 report

### Step 2: Reporting

**Output Format**:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Files modified: [count]
- Commands updated: [count/total]
- Specific areas changed: [list]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Subagent Results
- Total subagents deployed: [count]
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

### Update All Commands

```bash
/update-command all
# Spawns parallel subagents (max 8 parallel Task calls)
# Updates every command in .claude/commands/ via subagent delegation
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
