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

#### Phase 1: Planning (Lead)

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract:
     - Target commands (all, specific, or namespace/*)
     - Specific areas to change (--area parameter)
     - Change descriptions (--changes parameter)
     - Implicit change requests from argument text
   - List commands to update with their specific changes
   - Determine order of operations

2. **Structure Analysis**
   - Compare with template:command
   - Identify missing sections
   - Map requested changes to template sections
   - Identify key custom content to preserve
   - Extract specific change areas from arguments

3. **Identify Applicable Workflows & Standards**
   - Check `[plugin]/constitution/workflows/` for relevant processes
   - Review `[plugin]/constitution/standards/` for applicable standards
   - Note: MUST follow any matching workflows

4. **Delegation Decision**
   - Identify if specialized agents should handle subtasks
   - List tasks suitable for parallel execution
   - Plan handoff points between agents

5. **Risk Assessment**
   - Identify potential failure points
   - Plan rollback strategies
   - Note destructive operations

#### Phase 2: Team Setup & Execution

1. **Create Team**
   - Use TeamCreate with name `update-command-team`
   - Initialize agent pool registry to track active agents

2. **Spawn Command Update Specialists**
   - Spawn specialized teammates (one per command file) via Task tool with:
     - `team_name: "update-command-team"`
     - `name: "updater-{N}"` (sequential naming)
     - `model: "opus"`
     - `agent_type: "general-purpose"`

3. **Create and Assign Tasks**
   - TaskCreate per command file with full instructions including:
     - Command file path
     - Template reference path
     - All change specifications from arguments
     - Detailed instructions for applying updates
   - TaskUpdate to set owner per teammate

#### Phase 3: Work Cycle

1. **Subagent Task Specification**

   Each Command Update Specialist receives:

   >>>
   **ultrathink: adopt the Command Update Specialist mindset**

   - You're a **Command Update Specialist** with deep expertise in command structure who follows these principles:
     - **Template-First Approach**: Always compare against template before modification
     - **Content Preservation**: Maintain existing examples and workflows
     - **Structural Integrity**: Align with template structure while preserving functionality
     - **Professional Polish**: Deliver clean, consistent documentation

   <IMPORTANT>
     You've to perform the task yourself. You CANNOT further delegate the work to another subagent
   </IMPORTANT>

   **Assignment**
   You're assigned to update command: [command name]

   **Command Specifications**:
   - **Command File**: [command file path]
   - **Template**: template:command
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Command**:
      - Read the command file completely
      - Identify existing workflows, examples, and custom content
      - Note any unique sections or functionality

   2. **Compare with Template**:
      - Read template:command for current structure
      - Identify missing sections from template
      - Identify sections that need structural updates
      - Map changes to specific template sections

   3. **Apply Updates**:
      - Add any missing required sections from template
      - Update targeted sections per change requests
      - Reorganize content to match template structure
      - Preserve all existing custom functionality
      - Remove all instruction comments from template

   4. **Clean & Finalize**:
      - Verify NO comments remain
      - Ensure consistent markdown formatting
      - Validate frontmatter syntax and completeness
      - Verify all requested changes clearly reflected

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens) via SendMessage to team-lead:

   ```yaml
   status: success|failure|partial
   command: '[command-name]'
   summary: 'Brief description of changes applied'
   modifications:
     - section: '[section name]'
       change: '[what was changed]'
   template_compliance: true|false
   functionality_preserved: true|false
   context_level: '[calculated %]'  # (input_tokens / context_window_size) from real usage data
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```

   <<<

2. **Progress Monitoring**
   - Track completion status of each delegated command
   - Handle any teammate failures or escalations
   - Ensure template compliance and standards enforcement in all updates

#### Phase 4: Aggregation & Cleanup

1. **Collect Results**
   - Use TaskGet to retrieve completion reports from all tasks
   - Aggregate results into final summary

2. **Shutdown Teammates**
   - Send shutdown requests to all teammates via SendMessage
   - Wait for shutdown acknowledgments

3. **Delete Team**
   - Use TeamDelete to clean up team resources
   - Proceed to Reporting

#### Agent Summary

| Agent Type | Model | Role | Lifecycle |
|------------|-------|------|-----------|
| Command Update Specialist | opus | Updates command files with template alignment and changes | One per command file; spawned for Phase 3, retired in Phase 4 |

### Step 2B: Subagent Mode (fallback)

When Agent Teams are not available, execute the existing workflow:

### Planning

1. **Workflow Compliance**
   - MUST follow workflows identified in Phase 1
   - If no workflow exists, follow project conventions
   - Reference specific workflow files when applicable

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

### Verification

1. **Quality Assurance**
   - Verify NO comments remain
   - Check markdown formatting and structure
   - Validate frontmatter syntax and completeness
   - Verify all requested changes implemented

2. **Side Effect Validation**
   - Core functionality preserved
   - Custom content maintained
   - Template compliance achieved

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

## Workflows Applied (subagent mode)
- [Workflow name]: [Status]

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
