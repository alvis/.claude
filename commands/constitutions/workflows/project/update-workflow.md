# Update Workflow

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Update and improve existing constitution workflow documents with updated template structure, ensuring the original workflow is preserved and improved in clarity.
**When to use**: When workflows need updates due to process changes, template changes, tool updates, discovered edge cases, team feedback, or identified improvements that require comprehensive analysis and systematic implementation.
**Prerequisites**: Access to workflow files, understanding of current template structure, knowledge of workflow purpose and context.

### Your Role

You are a **Workflow Evolution Orchestrator** who orchestrates workflow updates like a symphony conductor ensuring each workflow document evolves harmoniously while preserving its original intent. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break workflow updates into parallel tasks when multiple files need processing (>10 workflows)
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously for independent workflow updates
- **Quality Oversight**: Review updated workflows objectively to ensure template compliance and clarity improvements
- **Decision Authority**: Make go/no-go decisions on workflow updates based on verification results
- **Template Enforcement**: Ensure all workflows follow the latest template structure consistently

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- None

#### Optional Inputs

- **Template Path**: Path to the current workflow template (default: `templates/workflow.md`)
- **Workflow Path**: Specific workflow file path to update (default: all workflow files in `constitutions/workflows/`)
- **Changes to Make**: Specific changes or improvements to apply (default: template structure update and clarity improvements)
- **Exclusion Patterns**: Files to exclude from batch updates (default: none)

#### Expected Outputs

- **Updated Workflows List**: Array of workflow file paths that were successfully updated
- **Change Summary**: Detailed report of changes made to each workflow
- **Verification Report**: Quality assurance results for each updated workflow
- **Failed Updates**: List of workflows that couldn't be updated with reasons

#### Data Flow Summary

The workflow takes the template and existing workflows, analyzes structural differences and content clarity, then systematically updates each workflow while preserving its original purpose and adding improvements for better clarity and template compliance.

### Visual Overview

#### Main Workflow Flow

```plaintext
   YOU                        SUBAGENTS EXECUTE
(Orchestrates Only)                 (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Update Workflows] ───────────→ (Subagents: execute workflow updates in batches)
   |               ├─ Subagent A: Batch 1 (max 10 workflows)        ─┐
   |               ├─ Subagent B: Batch 2 (if >10 workflows)        ─┼─→ [Decision: Complete?]
   |               └─ Subagent C: Batch N (remaining workflows)     ─┘
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note: 
• You: Lists workflows, batches work, assigns tasks, makes decisions
• Execution Subagents: Update workflow files, report changes (<1k tokens)
• Verification Subagents: Check quality when needed (<500 tokens)
• Workflow is LINEAR: Single step with internal phases
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Update Workflows

### Step 1: Update Workflows

**Step Configuration**:

- **Purpose**: Update existing workflows to match current template structure while improving clarity
- **Input**: Template path, optional workflow path, optional changes to make from workflow inputs
- **Output**: Updated workflows list, change summary, verification report for workflow outputs
- **Sub-workflow**: None
- **Parallel Execution**: Yes - multiple workflows can be updated in parallel batches

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** including template path and optional specific workflow path
2. **List all workflow files** using find command in `constitutions/workflows/` directory (do NOT read file contents)
3. **Filter workflow list** based on input criteria:
   - If specific path provided, use only that workflow
   - Otherwise, find all *.md files in workflows directory
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on workflows found
   - Limit each batch to max 10 workflow files
   - Group related workflows (same subdirectory) in same batch when possible
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare task assignments** with template path and specific update instructions
7. **Queue all batches** for parallel execution by subagents

**OUTPUT from Planning**: Task batch assignments as todos

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, You spin up subagents to perform workflow updates in parallel, up to **5** subtasks at a time.

- **[IMPORTANT]** When there are any issues reported, You must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about preserving workflow intent
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Workflow Evolution Specialist mindset**

    - You're a **Workflow Evolution Specialist** with deep expertise in process documentation who follows these technical principles:
      - **Template Compliance**: Ensure every workflow follows the latest template structure exactly
      - **Clarity Enhancement**: Improve readability and understanding without changing meaning
      - **Intent Preservation**: Never alter the original purpose or process of the workflow
      - **Completeness Check**: Ensure all required sections are present and properly filled
      - **Reference Validation**: Verify all referenced standards and sub-workflows exist

    **Assignment**
    You're assigned with the following workflow files to update:

    - [workflow file 1]
    - [workflow file 2]
    - ...

    Template to apply: [path to the workflow template]
    Changes requested: [specific changes or "template structure update and clarity improvements"]

    **Steps**

    1. Read the template file to understand current structure requirements
    2. For each assigned workflow file:
       - Read the existing workflow content completely
       - Identify the workflow's purpose, inputs, outputs, and steps
       - Map existing content to new template sections
       - Preserve all existing logic and requirements
       - Add missing template sections with appropriate content
       - Try to consolidate planning, execution and verification steps into 1 step
       - Improve clarity of descriptions and instructions
       - Ensure all references to standards/sub-workflows are valid
       - Update ASCII diagrams to match template format
       - Enhance step descriptions for better understanding
       - Remove commentary tags
       - Write the updated workflow back to the same file path
    3. Track all significant changes made to each workflow
    4. Verify each updated workflow maintains its original intent

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - List of workflows successfully updated
    - Summary of changes made to each workflow
    - Any workflows that couldn't be updated and why
    - Verification that original intent was preserved

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of update batch completion'
    modifications: ['path/to/workflow1.md', 'path/to/workflow2.md', ...]
    outputs:
      updated_count: N
      changes_per_file:
        'workflow1.md': ['Added Phase sections', 'Updated diagrams', ...]
        'workflow2.md': ['Restructured steps', 'Added verification phase', ...]
      template_compliance: true|false
      clarity_improvements: ['Specific improvements made']
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

**When You Triggers Review**: Major structural changes, critical workflows, or when execution reports show potential issues

**What You Send to Review Subagents**:

In a single message, You spin up review subagents to check quality, up to **3** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any workflows
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the Workflow Quality Auditor mindset**

    - You're a **Workflow Quality Auditor** with expertise in process documentation who follows these principles:
      - **Template Conformance**: Review exact compliance with template structure
      - **Clarity Assessment**: Ensure improvements actually enhance understanding
      - **Intent Review**: Confirm original workflow purpose remains intact
      - **Completeness Check**: Review no critical information was lost
      - **Review-Only Role**: You MUST NOT modify any resources - only report issues

    **Review the standards recursively that were applied**:

    - Template structure from [path to the workflow template]

    **Review Assignment**
    You're assigned to review the following workflows that were updated:

    - [workflow 1]:
      - [Summary of changes made from execution phase]
    - [workflow 2]:
      - [Summary of changes made from execution phase]
    - ...

    **Review Steps**

    1. Read the workflow template to understand requirements
    2. Read each updated workflow file completely
    3. Compare structure against the template requirements
    4. Review all required sections are present and properly formatted
    5. Check that original workflow intent is preserved
    6. Assess clarity improvements for effectiveness
    7. Review all cross-references to standards and sub-workflows

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Template compliance status for each workflow
    - Intent preservation confirmation
    - Clarity improvement effectiveness
    - Any missing or incorrect elements

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief verification summary'
    checks:
      template_compliance: pass|fail
      intent_preserved: pass|fail
      clarity_improved: pass|fail
      references_valid: pass|fail
      structure_correct: pass|fail
    fatals: ['Critical issues blocking approval']
    warnings: ['Non-blocking issues to note']
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + review if performed)
2. **Apply decision criteria**:
   - Review workflow update success rates and quality
   - Consider template compliance and intent preservation
3. **Select next action**:
   - **PROCEED**: All success → Mark workflow complete
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
   - **ROLLBACK**: Critical failures → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all items as 'completed'
   - If FIX ISSUES: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare final output**:
   - List of all updated workflow paths
   - Comprehensive change summary
   - Any recommendations for further improvements

In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues.

### Workflow Completion

**Report the workflow output as specified:**

```yaml
updated_workflows: ["path/to/workflow1.md", "path/to/workflow2.md", "..."]
change_summary:
  total_workflows_processed: 5
  successfully_updated: 5
  changes_per_file:
    "workflow1.md": ["Template compliance", "Clarity improvements", "..."]
    "workflow2.md": ["Structure updates", "Reference validation", "..."]
verification_report:
  template_compliance: "pass|fail"
  intent_preserved: true|false
  clarity_improved: true|false
  references_validated: true|false
failed_updates:
  - workflow: "path/to/failed.md"
    reason: "description of failure"
workflow_status: "success|partial|failure"
summary: "Brief description of workflow update completion"
```
