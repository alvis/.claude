---
allowed-tools: Read, Write, MultiEdit, Glob, Task
argument-hint: <target> [--area=...] [--changes=...]
description: Update slash commands to latest standards with optionally specific area changes
---

# Update Commands

Update existing slash commands to follow current best practices and template structure. Parses $ARGUMENTS to identify both target commands and specific areas to change. Commands will be upgraded to the latest template with clean, comment-free output and change any content in relate to the specified changes. Intelligently extracts change requirements from arguments, adds missing sections from template, removes all comments, preserves custom functionality, and make sure all the changes are clearly reflected in the command file. Ultrathink mode.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Change command core functionality
- Delete custom sections or examples
- Modify commands in other directories
- Update non-markdown files

**When to REJECT:**

- Command doesn't exist
- Invalid target specification
- Non-markdown files specified
- For creating new commands (use create-command instead)
- When commands are already compliant
- For non-command markdown files

## 📊 Dynamic Context

- **[IMPORTANT]** At the start of the command, you must run the command to extract all the context below

### Project Context

- Workflows: !`find ~/.claude/constitutions/workflows "$(git rev-parse --show-toplevel)/constitutions/workflows" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`
- Standards: !`find ~/.claude/constitutions/standards "$(git rev-parse --show-toplevel)/constitutions/standards" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`

## 🔄 Workflow

### Phase 1: Planning

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract:
     - Target commands (all, specific, or namespace/*)
     - Specific areas to change (--area parameter)
     - Change descriptions (--changes parameter)
     - Implicit change requests from argument text
   - List commands to update with their specific changes
   - Determine order of operations

2. **Structure Analysis**
   - Compare with @templates/command.md
   - Identify missing sections
   - Map requested changes to template sections
   - Identify key custom content to preserve
   - Extract specific change areas from arguments

3. **Identify Applicable Workflows & Standards**
   - Check `constitutions/workflows/` for relevant processes
   - Review `constitutions/standards/` for applicable standards
   - Note: MUST follow any matching workflows

4. **Delegation Decision**
   - Identify if specialized agents should handle subtasks
   - List tasks suitable for parallel execution
   - Plan handoff points between agents

5. **Risk Assessment**
   - Identify potential failure points
   - Plan rollback strategies
   - Note destructive operations

### Phase 2: Execution

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
   - Apply standards from `constitutions/standards/`
   - Follow template structure
   - No instruction comments copied from the template
   - Ensure targeted changes align with standards

4. **Edge Case Handling**
   - Preserve custom useful content
   - Handle missing sections gracefully
   - Maintain backward compatibility

### Phase 3: Verification

1. **Quality Assurance**
   - Verify NO comments remain
   - Check markdown formatting and structure
   - Validate frontmatter syntax and completeness
   - Verify all requested changes implemented

2. **Side Effect Validation**
   - Core functionality preserved
   - Custom content maintained
   - Template compliance achieved

### Phase 4: Reporting

**Output Format:**

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

## Workflows Applied
- [Workflow name]: [Status]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]

## Next Steps (if applicable)
- [Required manual action]
- [Recommended follow-up]
```

## 📝 Examples

### Update All Commands

```bash
/update-command all
# Updates every command in .claude/commands/
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
