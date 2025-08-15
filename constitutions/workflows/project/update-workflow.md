# Update Workflow

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Update and improve existing constitution workflow documents with updated template structure, ensuring the original workflow is preserved and improved in clarity
**When to use**: When workflows need updates due to process changes, template changes, tool updates, discovered edge cases, team feedback, or identified improvements that require comprehensive analysis and systematic implementation
**Prerequisites**: Access to workflow files, understanding of current template structure, knowledge of workflow purpose and context

### Claude Role

You are a **Workflow Evolution Orchestrator** who orchestrates the workflow like a symphony conductor ensuring each workflow document evolves harmoniously while preserving its original intent. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

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
     Claude                    SUBAGENTS EXECUTE
     (Orchestrates Only)                 (Perform Tasks)
            |                                   |
            v                                   v
[START]
   |
   v
[Step 1: Update Workflows] ───────────→ (Subagents: execute workflow updates in batches)
   |                           ├─ Analysis Subagent: Batch 1 (max 10 workflows)        ─┐
   |                           ├─ Analysis Subagent: Batch 2 (if >10 workflows)        ─┼─→ [Decision: Complete?]
   |                           └─ Analysis Subagent: Batch N (remaining workflows)     ─┘
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: Claude plans & orchestrates (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel
• ARROWS (───→): Claude assigns work to subagents
• DECISIONS: Claude decides based on subagent reports
═══════════════════════════════════════════════════════════════════
```

#### Workflow State Machine

##### Main Workflow States

```
[INIT] ──> [UPDATE_WORKFLOWS] ──> [COMPLETE]
                ↑  ↓
                └──┘
             (retry)
                ↓
            [FAILED]
```

##### Step Internal States (for the main UPDATE_WORKFLOWS step)

```
[PLANNING] ──> [EXECUTING] ──> [REPORTING] ──> [VERIFYING] ──> [DECIDING]
     ↑              ↓               ↓               ↓              ↓
     └──────────────┴───────────────┴───────────────┴──────────────┘
                            (retry/rollback paths)
```

### Dependencies & Patterns

#### Step Execution Pattern

```
     Claude                    SUBAGENTS EXECUTE
     (Orchestrates Only)                 (Perform Tasks)
            |                                   |
            v                                   v

[Phase 1: Plan] ─────────→ (Claude: analyzes and batches workflows)
        |
        v
[Phase 1: Assign] ───────→ (Claude: assigns to subagents)
        |                          |
        v                          v
[Phase 2: Execute] ──────→ (Execution Subagents: update workflows in parallel)
        |                   ├─ Workflow Update Subagent A (Batch 1)                    ─┐
        |                   ├─ Workflow Update Subagent B (Batch 2 if >10)             ─┼─→ [Reports]
        |                   └─ Workflow Update Subagent C (Batch N if needed)          ─┘
        v
[Phase 3: Review] ───────→ (Claude: reviews update reports)
        |
        v
[Phase 4: Verify?] ──────→ (Claude: decides if verification needed)
        |                          |
        |                          v
        |                    (Verification Subagent: checks quality) → [Report]
        v
[Phase 5: Decide] ───────→ (Claude: decides next action)
                                   |
                         ┌─────────┼─────────┐
                         │         │         │
                      Complete   Retry     Rollback
```

## 3. AGENT ARCHITECTURE & COMMUNICATION

### Three Agent Types

#### 1. Claude

- **Role**: Orchestrator and decision maker
- **Responsibilities**:
  - Identify workflows needing updates
  - Create batches of workflow files
  - Assign update tasks to execution subagents
  - Review update reports and change summaries
  - Decide if verification is needed
  - Make workflow completion decisions
- **Restrictions**:
  - Cannot read file contents directly
  - Cannot execute updates directly
  - Can only list/batch resources

#### 2. Execution Subagents

- **Role**: Workflow updaters
- **Responsibilities**:
  - Read assigned workflow files
  - Read template structure
  - Analyze structural differences
  - Apply template updates
  - Improve clarity while preserving intent
  - Report changes made (<1k tokens)
- **Output**: Status, changes summary, and updated workflow paths

#### 3. Verification Subagents

- **Role**: Quality assurance
- **Responsibilities**:
  - Verify template compliance
  - Check workflow completeness
  - Validate clarity improvements
  - Ensure original intent preserved
- **Output**: Pass/fail status with recommendations

### Report Token Limits

- **Execution Subagent**: Max 1000 tokens per report
- **Verification Subagent**: Max 500 tokens per report
- **Claude**: Max 200 tokens per decision

## 4. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Update Workflows

### Step 1: Update Workflows

**Step Configuration**:

- **Purpose**: Update existing workflows to match current template structure while improving clarity
- **Input**: Template path, optional workflow path, optional changes to make
- **Output**: List of updated workflow paths, change summary, verification report
- **Sub-workflow**: None
- **Parallel Execution**: Yes - multiple workflows can be updated in parallel batches

#### Phase 1: Planning (Claude)

**What Claude Does**:

1. **Receive inputs** including template path and optional specific workflow path
2. **List all workflow files** using find command in `constitutions/workflows/` directory
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

**What Claude Sends to Subagents**:

In a single message, the Claude spins up subagents to perform workflow updates in parallel, up to **5** batches at a time.

- **[IMPORTANT]** When there are any issues reported, the Claude must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** The Claude MUST ask all subagents to ultra think hard about preserving workflow intent
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **In ultra think mode, adopt the Workflow Evolution Specialist mindset**

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
       - Try to consoldate planning, execution and verification steps into 1 step
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

#### Phase 3: Review (Claude)

**What Claude Does**:

1. **Use TodoRead** to check current task statuses
2. **Collect all execution reports** from parallel subagents
3. **Parse report statuses** (success/failure/partial) for each batch
4. **Use TodoWrite** to update batch statuses:
   - Mark successful batches as 'completed'
   - Mark failed batches as 'failed'
   - Keep partial success as 'in_progress' for retry
5. **Identify any failed updates** and group them by failure type
6. **Determine verification needs** based on:
   - Major structural changes
   - Critical workflow modifications
   - Workflows affecting other workflows
7. **Compile review summary** with:
   - Total workflows updated
   - Failed updates needing retry
   - Verification requirements

#### Phase 4: Verification (Subagents) - Optional

**When Claude Triggers Verification**: Major structural changes, critical workflows, or when execution reports show potential issues

**What Claude Sends to Verification Subagents**:

In a single message, the Claude spins up verification subagents to check quality, up to **3** verification tasks at a time.

- **[IMPORTANT]** Verification is read-only - subagents must NOT modify any workflows
- **[IMPORTANT]** The Claude MUST ask verification subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track verification tasks separately from execution tasks

Request each verification subagent to perform the following verification with full scrutiny:

    >>>
    **In ultra think mode, adopt the Workflow Quality Auditor mindset**

    - You're a **Workflow Quality Auditor** with expertise in process documentation who follows these principles:
      - **Template Conformance**: Verify exact compliance with template structure
      - **Clarity Assessment**: Ensure improvements actually enhance understanding
      - **Intent Validation**: Confirm original workflow purpose remains intact
      - **Completeness Check**: Verify no critical information was lost

    **Review the standards that were applied**:

    - Template structure from [path to the workflow template]

    **Verification Assignment**
    You're assigned to verify the following workflows that were updated:

    - [workflow 1]:
      - [Summary of changes made]
    - [workflow 2]:
      - [Summary of changes made]
    - ...

    **Verification Steps**

    1. Read the workflow template
    2. Read each updated workflow file completely
    3. Compare structure against the template requirements
    4. Verify all required sections are present and properly formatted
    5. Check that original workflow intent is preserved
    6. Assess clarity improvements for effectiveness
    7. Validate all cross-references to standards and sub-workflows
    8. Check recursive standard reading requirement is clearly stated
    9. Check diagrams and state machines are correctly drawn
    10. Confirm Claude is restricted to orchestration only (no file reading)
    11. Check Execution subagents have clear input/output contracts
    12. Confirm final validation checklist exists in last step
    13. Verify no commentary tags are present
    14. Confirm content consistency without self-contradiction

    **Report**
    **[IMPORTANT]** You're requested to verify and report:

    - Template compliance status
    - Intent preservation confirmation
    - Clarity improvement effectiveness
    - Any missing or incorrect elements

    **[IMPORTANT]** You MUST return the following verification report (<500 tokens):

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

#### Phase 5: Decision (Claude)

**What Claude Does**:

1. **Analyze all reports** (execution + verification if performed)
2. **Apply decision criteria**:
   - All workflows updated successfully
   - Template compliance achieved
   - Original intent preserved
   - Clarity improvements effective
3. **Select next action**:
   - **PROCEED**: All success → Mark workflow complete
   - **RETRY**: Partial success → Create new batches for failed workflows
   - **ROLLBACK**: Critical failures → Revert changes using git
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all items as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare final output**:
   - List of all updated workflow paths
   - Comprehensive change summary
   - Any recommendations for further improvements

### Final Step: Completion Confirmation

**Step Configuration**:

- **Purpose**: Confirm successful workflow update completion and package final outputs
- **Input**: All update reports and verification results
- **Output**: Final list of updated workflows and comprehensive change report
- **Sub-workflow**: None
- **Parallel Execution**: No

**Completion Checklist**:

- [ ] All targeted workflows updated successfully
- [ ] Template compliance verified for all workflows
- [ ] Original workflow intent preserved in all cases
- [ ] Clarity improvements applied consistently
- [ ] All cross-references validated
- [ ] No pending retry or rollback items
- [ ] Final report generated with all changes documented
