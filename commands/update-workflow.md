---
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite
argument-hint: [workflow] [--change1="description" --change2="description" ...]
description: Update workflow(s) to latest standard template and make specified changes
---

# Update Workflow

Update workflow files to align with the latest standard template and apply specified changes using intelligent delegation to subagents. Handles both single workflow updates and bulk updates of all workflows in parallel.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Create new workflows (use create-workflow)
- Modify non-workflow files
- Update templates themselves
- Override constitutional requirements

**When to REJECT:**

- Invalid workflow file paths
- Malformed change specifications
- Attempting to violate constitutional standards
- Template file is missing or corrupted

## 📊 Dynamic Context

- **[IMPORTANT]** You must carefully remember all the context defined below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`
- Modified files: !`git diff --name-only`
- Staged files: !`git diff --cached --name-only`

### Project Context

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Template: !`ls templates/workflow.md 2>/dev/null || echo "Template not found"`

## 🔄 Steps

### Step 1: Extract Input

- Parse $ARGUMENTS to extract workflow name and change specifications
- Workflow: First argument (optional - if empty, update all workflows)
- --change[N]: Extract all change parameters (change1, change2, etc.)
- Validate workflow file exists if specified
- Count total workflows if updating all

### Step 2: Follow Update Workflow Workflow

- Execute @constitions/workflows/project/update-workflow.md

### Step 3 Reporting

- Report the result in the following format

```plaintext
[✅/❌] Command: $ARGUMENTS

## Summary
- Workflows updated: [count]
- Changes applied: [change specifications]
- Template alignment: [COMPLETE/PARTIAL/FAILED]

## Actions Taken
1. [Workflow file]: [Status] - [Changes applied]
2. [Workflow file]: [Status] - [Changes applied]

## Subagent Results
- Total agents deployed: [count]
- Successful updates: [count]
- Failed updates: [count] (if any)

## Template Alignment Applied
- Structure updates: [list]
- Section additions: [list]
- Format corrections: [list]

## Changes Applied
- --change1: [Status and details]
- --change2: [Status and details]

## Issues Found (if any)
- **Issue**: [Description]
  **Resolution**: [Applied fix or escalation]

## Next Steps (if applicable)
- Review updated workflows for accuracy
- Test workflow execution with sample scenarios
- Commit changes if satisfied with results
```

## 📝 Examples

### Update Single Workflow

```bash
/update-workflow "constitutions/workflows/coding/write-code-tdd.md"
# Updates specified workflow to match latest template
# Uses one ultrathink subagent for comprehensive analysis
```

### Update Single Workflow with Changes

```bash
/update-workflow "constitutions/workflows/backend/build-service.md" --change1="add Docker deployment step" --change2="include security scanning phase"
# Applies template alignment plus specified modifications
# Each change becomes a subtask (2a, 2b) in the workflow
```

### Update All Workflows

```bash
/update-workflow
# Discovers all workflow files in constitutions/workflows/
# Spawns parallel subagents to update each workflow
# Maintains consistency across entire workflow system
```

### Complex Multi-Change Update

```bash
/update-workflow "constitutions/workflows/quality/review-code.md" --change1="integrate AI-assisted review" --change2="add performance criteria" --change3="update approval requirements"
# Applies template + three specific changes
# Subagent creates tasks 1, 2a, 2b, 2c, 3 for comprehensive update
```

### Error Case Handling

```bash
/update-workflow "nonexistent-workflow.md"
# Error: Workflow file not found
# Suggestion: Check available workflows with 'find constitutions/workflows -name "*.md"'
# Alternative: Use '/update-workflow' without arguments to update all workflows
```

### Template Missing Error

```bash
/update-workflow "some-workflow.md"
# Error: Template templates/workflow.md not found
# Suggestion: Ensure template exists before updating workflows
# Action: Command aborts to prevent inconsistent updates
```
