---
name: update-workflow
description: Update workflow(s) to latest standard template and make specified changes. Use when bulk updating workflows, ensuring template compliance, or applying consistent modifications across workflow files.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite
argument-hint: [workflow specifier] [--changes=...]
---

# Update Workflow

Update workflow files to align with the latest standard template and apply specified changes using intelligent delegation to subagents. Handles both single workflow updates and bulk updates of all workflows in parallel.

## Purpose & Scope

**What this skill does NOT do**:

- Create new workflows (use create-workflow)
- Modify non-workflow files
- Update templates themselves
- Override constitutional requirements

**When to REJECT**:

- Invalid workflow file paths
- Malformed change specifications
- Attempting to violate constitutional standards
- Template file is missing or corrupted

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Extract Input

- Parse $ARGUMENTS to extract workflow name and change specifications
- Workflow: First argument (optional - if empty, update all workflows)
- --change[N]: Extract all change parameters (change1, change2, etc.)
- Validate workflow file exists if specified
- Count total workflows if updating all

### Step 2: Execution with Parallel Subagents

1. **Template Validation**
   - Verify template:workflow exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

2. **Discover Workflows**
   - Locate all workflow files in [plugin]/constitution/workflows/
   - Filter by specifier if provided
   - Build list of workflows to update

3. **Delegation**
   - Create parallel specialized subagents (one per workflow file) with:
     - Workflow file path
     - All change specifications
     - Detailed instructions
     - Request to ultrathink

4. **Subagent Task Specification**

   >>>
   **ultrathink: adopt the Workflow Update Specialist mindset**

   - You're a **Workflow Update Specialist** with deep expertise in process documentation who follows these principles:
     - **Template-First Approach**: Always compare against template before modification
     - **Process Preservation**: Maintain existing workflow logic and steps
     - **Structural Integrity**: Align with template structure while preserving content
     - **Professional Polish**: Deliver clean, consistent workflow documentation

   <IMPORTANT>
     You've to perform the task yourself. You CANNOT further delegate the work to another subagent
   </IMPORTANT>

   **Assignment**
   You're assigned to update workflow: [workflow name]

   **Workflow Specifications**:
   - **Workflow File**: [workflow file path]
   - **Template**: template:workflow
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Workflow**:
      - Read the workflow file completely
      - Identify existing steps, phases, and subagent instructions
      - Note any custom sections or unique process logic

   2. **Compare with Template**:
      - Read template:workflow for current structure
      - Identify missing sections from template
      - Identify sections that need structural updates
      - Map changes to specific template sections

   3. **Apply Updates**:
      - Task 1: Align workflow with template:workflow structure
      - Task 2a, 2b, 2c...: Apply each change specification as subtask
      - Task 3: Review workflow integrity and consistency throughout
      - Preserve all existing process logic and steps
      - Add any missing required sections from template
      - Update ASCII diagrams if structure changed

   4. **Clean & Finalize**:
      - Remove any outdated or deprecated content
      - Ensure consistent formatting throughout
      - Verify subagent instruction blocks follow >>> <<< format
      - Ensure all placeholder content has been replaced

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens):

   ```yaml
   status: success|failure|partial
   workflow: '[workflow-name]'
   summary: 'Brief description of changes applied'
   modifications:
     - section: '[section name]'
       change: '[what was changed]'
   template_compliance: true|false
   process_preserved: true|false
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```
   <<<

5. **Progress Monitoring**
   - Track completion status of each delegated workflow
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates

### Step 3: Verification

1. **Template Compliance Verification**
   - Verify each updated workflow follows template:workflow structure
   - Check all mandatory sections are present and properly formatted
   - Validate ASCII diagrams are properly formatted

2. **Change Application Verification**
   - Confirm all specified changes were applied correctly
   - Verify changes are reflected throughout the workflow file
   - Check for any conflicting or contradictory specifications

3. **Process Logic Validation**
   - Ensure workflow steps remain logically sound
   - Verify subagent instruction blocks are complete
   - Confirm input/output specifications are accurate

4. **Consistency Validation**
   - Run integrity checks on workflow structure
   - Verify internal consistency and logical flow
   - Confirm no broken references or missing dependencies

### Step 4: Reporting

**Output Format**:

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

## Examples

### Update Single Workflow

```bash
/update-workflow "write-code.md"
# Updates specified workflow to match latest template
# Uses one ultrathink subagent for comprehensive analysis
```

### Update Single Workflow with Changes

```bash
/update-workflow "build-service.md" --change1="add Docker deployment step" --change2="include security scanning phase"
# Applies template alignment plus specified modifications
# Each change becomes a subtask (2a, 2b) in the workflow
```

### Update All Workflows

```bash
/update-workflow
# Discovers all workflow files in [plugin]/constitution/workflows/
# Spawns parallel subagents to update each workflow
# Maintains consistency across entire workflow system
```

### Complex Multi-Change Update

```bash
/update-workflow "review-code.md" --change1="integrate AI-assisted review" --change2="add performance criteria" --change3="update approval requirements"
# Applies template + three specific changes
# Subagent creates tasks 1, 2a, 2b, 2c, 3 for comprehensive update
```

### Error Case Handling

```bash
/update-workflow "nonexistent-workflow.md"
# Error: Workflow file not found
# Suggestion: Check available workflows with 'find [plugin]/constitution/workflows -name "*.md"'
# Alternative: Use '/update-workflow' without arguments to update all workflows
```

### Template Missing Error

```bash
/update-workflow "some-workflow.md"
# Error: Template template:workflow not found
# Suggestion: Ensure template exists before updating workflows
# Action: Command aborts to prevent inconsistent updates
```
