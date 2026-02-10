# Update Command

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Update existing command files to align with the command template and apply specified changes to command configuration and implementation
**When to use**: When commands need template alignment, when bulk updates are needed across multiple commands, when specific changes need to be applied across command files
**Prerequisites**: Access to template:command, understanding of command structure and metadata, knowledge of available tools and workflows

### Your Role

You are a **Command Update Director** who orchestrates the workflow like a CEO managing a large-scale update operation. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break complex work into parallel tasks when dealing with multiple commands (max 5 files per batch) and assign to the right specialist subagents
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously when dependencies allow
- **Quality Oversight**: Review work objectively without being involved in execution details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and verification results

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Target Commands**: Array of command file paths to update, or "ALL" to update all commands in the commands directory

#### Optional Inputs

- **Specific Changes**: Description of particular changes to apply beyond template alignment (e.g., add new tools, update workflows)
- **Areas to Update**: Specific sections to focus on (e.g., metadata, workflows, examples)

#### Expected Outputs

- **Updated Command Files**: All specified command files aligned with current template structure
- **Execution Report**: Summary of changes applied to each file
- **Compliance Status**: Pass/fail status for template compliance verification

#### Data Flow Summary

The workflow takes command file paths as input, analyzes current command files against the template, applies necessary updates through parallel subagent batches (max 5 files per batch), and produces updated command files that comply with the current template standards.

### Visual Overview

#### Main Workflow Flow

```plaintext
  YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Planning] ───────────→ (Subagents: analyze and batch files)
   |               ├─ Subagent A: Batch 1 (max 5 commands)                  ─┐
   |               ├─ Subagent B: Batch 2 (max 5 commands)                  ─┼─→ [Decision: What's next?]
   |               └─ Subagent N: Batch N (remaining commands)              ─┘
   v
[Step 2: Execution] ─────────→ (Subagents: update command files) → [Decision: What's next?]
   |
   v
[Step 3: Verification] ──────→ (Subagents: verify template compliance) → [Decision: What's next?]
   |
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
• You: Lists resources, batches work, assigns tasks, makes decisions
• Execution Subagents: Perform actual work, report back (<1k tokens)
• Verification Subagents: Check quality when needed (<500 tokens)
• Workflow is LINEAR: Step 1 → 2 → 3
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Step 1: Planning and File Selection
2. Step 2: Command Update Execution  
3. Step 3: Template Compliance Verification

### Step 1: Planning and File Selection

**Step Configuration**:

- **Purpose**: Parse inputs, identify target command files, and create execution batches
- **Input**: Target Commands (required), Specific Changes (optional), Areas to Update (optional)
- **Output**: Batched command file assignments for parallel processing
- **Sub-workflow**: [leave empty]
- **Parallel Execution**: Yes - can batch commands into parallel subtasks

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from workflow invocation
2. **List all command files** using find commands to locate .md files in commands directory
3. **Parse target selection**:
   - If "ALL": include all found command files
   - If specific paths: validate and filter to existing files
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on command files found
   - Limit each batch to max 5 command files
   - Assign one single subagent to perform all the tasks
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare task assignments** with template path and any specific change requirements
7. **Queue all batches** for parallel execution by subagents

**OUTPUT from Planning**: Task batch assignments as todos

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up subagents to perform subtasks in parallel, up to **5** subtasks at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Command Update Specialist mindset**

    - You're a **Command Update Specialist** with deep expertise in command template alignment who follows these technical principles:
      - **Template Mastery**: Understand and apply template structure and requirements precisely
      - **Content Preservation**: Maintain existing functionality while updating structure
      - **Quality Assurance**: Ensure all template sections are properly implemented

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - documentation.md
    - universal/write.md

    **Assignment**
    You're assigned with the following command files to update:

    - [command file 1]
    - [command file 2]
    - [command file 3]
    - [command file 4] 
    - [command file 5]

    **Template Reference**: template:command

    **Specific Changes**: [Any additional changes beyond template alignment]

    **Steps**

    1. **Read template file** to understand current structure and requirements
    2. **Read each assigned command file** to understand current implementation
    3. **Compare structure** against template to identify gaps and outdated sections
    4. **Update command metadata** (frontmatter) to match template format
    5. **Align content sections** with template structure while preserving functionality
    6. **Apply specific changes** if provided in assignment
    7. **Remove instruction comments** that begin with "INSTRUCTION:"
    8. **Validate workflow references** and tool specifications are current

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - List of command files processed
    - Summary of changes applied to each file
    - Any issues encountered during update process

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of command updates accomplished'
    modifications: ['command1.md', 'command2.md', ...] # command files that have been modified
    outputs:
      files_processed: 5
      template_compliance: true|false
      structure_updates: ['metadata', 'sections', 'examples']
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

In a single message, you spin up review subagents to check quality, up to **3** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the Template Compliance Auditor mindset**

    - You're a **Template Compliance Auditor** with expertise in command structure review who follows these principles:
      - **Standards Compliance**: Review strict adherence to template requirements
      - **Quality Assurance**: Check for completeness and consistency
      - **Risk Assessment**: Identify potential issues with command structure
      - **Review-Only Role**: You MUST NOT modify any resources - only report issues

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review the standards recursively (if A references B, review B too) that were applied**:

    - documentation.md - Verify compliance with documentation standards
    - universal/scan.md - Check adherence to coding principles

    **Review Assignment**
    You're assigned to review the following command files that were modified:

    - [command file 1]: Updated to align with current template
    - [command file 2]: Structure and metadata updated
    - [command file 3]: Template compliance applied
    - [command file 4]: Content sections aligned
    - [command file 5]: Instruction comments removed

    **Template Reference**: template:command

    **Review Steps**

    1. **Read template file** to understand compliance requirements
    2. **Read each modified command file** to assess current structure
    3. **Review frontmatter compliance** with template metadata format
    4. **Check section structure** matches template organization
    5. **Review content quality** and completeness
    6. **Confirm instruction comments** have been properly removed

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Template compliance status for each file
    - Structural completeness assessment
    - Any remaining issues or inconsistencies

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief verification summary of template compliance'
    checks:
      metadata_format: pass|fail
      section_structure: pass|fail
      content_quality: pass|fail
      instruction_removal: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + review)
2. **Apply decision criteria**:
   - Review any critical failures
   - Consider review recommendations
3. **Select next action**:
   - **PROCEED**: All success or acceptable partial success → Move to next step
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
   - **ROLLBACK**: Critical failures → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' items as 'completed'
   - If FIX ISSUES: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare transition**:
   - If PROCEED: Package outputs for next step
   - If FIX ISSUES: Generate retry batches with same standards
   - If ROLLBACK: Identify rollback actions needed

In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues.

### Step 2: Command Update Execution

**Step Configuration**:

- **Purpose**: Apply template updates and specific changes to command files
- **Input**: Receives from Step 1: Batched command file assignments
- **Output**: Updated command files with template compliance
- **Sub-workflow**: [leave empty]
- **Parallel Execution**: Yes - multiple batches processing simultaneously

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive batched assignments** from previous step
2. **Validate batch readiness** ensuring all command files are accessible
3. **Prepare update specifications** including template requirements and specific changes
4. **Use TodoWrite** to create detailed update tasks for each batch
5. **Queue execution batches** for parallel processing

**OUTPUT from Planning**: Ready-to-execute update task assignments

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up subagents to perform subtasks in parallel, up to **5** subtasks at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Command Template Implementer mindset**

    - You're a **Command Template Implementer** with deep expertise in command file structure who follows these technical principles:
      - **Precision Implementation**: Apply template changes exactly as specified
      - **Content Integration**: Merge existing content with new template structure seamlessly
      - **Quality Maintenance**: Preserve command functionality while updating format

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - documentation.md
    - universal/write.md

    **Assignment**
    You're assigned to implement template updates for these command files:

    - [command file 1]
    - [command file 2]
    - [command file 3]
    - [command file 4]
    - [command file 5]

    **Template Reference**: template:command
    **Specific Changes**: [Any additional modifications required]

    **Steps**

    1. **Apply template structure** to each command file systematically
    2. **Update frontmatter metadata** to match current template format
    3. **Implement section reorganization** according to template layout
    4. **Preserve existing functionality** while updating structure
    5. **Apply specific changes** as outlined in assignment
    6. **Remove all instruction comments** marked with "INSTRUCTION:"
    7. **Validate internal references** and ensure workflow paths are correct

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - List of successfully updated command files
    - Summary of template changes applied
    - Any challenges encountered during implementation

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of template implementation accomplished'
    modifications: ['command1.md', 'command2.md', ...] # command files that have been updated
    outputs:
      template_applied: true|false
      structure_updated: true|false
      metadata_formatted: true|false
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

In a single message, you spin up review subagents to check quality, up to **3** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the Command Quality Validator mindset**

    - You're a **Command Quality Validator** with expertise in template compliance assessment who follows these principles:
      - **Structural Integrity**: Review complete template implementation
      - **Functional Preservation**: Ensure command functionality remains intact
      - **Standard Adherence**: Check compliance with documentation standards
      - **Review-Only Role**: You MUST NOT modify any resources - only report issues

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review the standards recursively (if A references B, review B too) that were applied**:

    - documentation.md - Verify documentation compliance
    - universal/scan.md - Check implementation quality

    **Review Assignment**
    You're assigned to review the following command files that were updated:

    - [command file 1]: Template structure applied and validated
    - [command file 2]: Metadata and sections updated per template
    - [command file 3]: Content reorganized according to template
    - [command file 4]: Instruction comments removed and structure cleaned
    - [command file 5]: Specific changes applied and verified

    **Template Reference**: template:command

    **Review Steps**

    1. **Compare against template** to review structural compliance
    2. **Review metadata format** matches template frontmatter
    3. **Check section completeness** and proper organization
    4. **Review functionality preservation** of command features
    5. **Confirm instruction cleanup** with no remaining template markers

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Template compliance review results
    - Structural and functional quality assessment
    - Any remaining issues requiring attention

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief verification summary of command template implementation'
    checks:
      template_structure: pass|fail
      metadata_compliance: pass|fail
      functionality_preserved: pass|fail
      cleanup_complete: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + review)
2. **Apply decision criteria**:
   - Review any critical failures
   - Consider review recommendations
3. **Select next action**:
   - **PROCEED**: All success or acceptable partial success → Move to next step
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
   - **ROLLBACK**: Critical failures → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' items as 'completed'
   - If FIX ISSUES: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare transition**:
   - If PROCEED: Package outputs for workflow completion
   - If FIX ISSUES: Generate retry batches with same standards
   - If ROLLBACK: Identify rollback actions needed

In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues.

### Step 3: Template Compliance Verification

**Step Configuration**:

- **Purpose**: Final verification of template compliance across all updated command files
- **Input**: Receives from Step 2: Updated command files
- **Output**: Compliance status report and workflow completion confirmation
- **Sub-workflow**: [leave empty]
- **Parallel Execution**: Yes - can verify multiple files simultaneously

#### Phase 1: Planning (You)

**What You Do**:

1. **Collect all updated files** from previous step execution
2. **Prepare final verification checklist** based on template requirements
3. **Create verification batches** for parallel quality assessment
4. **Use TodoWrite** to create final verification tasks
5. **Queue verification subagents** for comprehensive compliance check

**OUTPUT from Planning**: Final verification task assignments

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up subagents to perform subtasks in parallel, up to **3** subtasks at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Final Compliance Auditor mindset**

    - You're a **Final Compliance Auditor** with deep expertise in template verification who follows these technical principles:
      - **Comprehensive Assessment**: Perform thorough compliance verification
      - **Quality Assurance**: Ensure all template requirements are met
      - **Standards Enforcement**: Verify adherence to all applicable standards

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - documentation.md
    - universal/scan.md

    **Assignment**
    You're assigned to perform final compliance verification for these updated command files:

    - [All command files that were updated in this workflow]

    **Template Reference**: template:command

    **Steps**

    1. **Read template thoroughly** to understand all compliance requirements
    2. **Review each updated command file** against template specifications
    3. **Verify complete structural alignment** with template sections
    4. **Check metadata consistency** and format compliance
    5. **Validate content quality** and documentation standards
    6. **Confirm no instruction comments** remain in final files
    7. **Generate comprehensive compliance report** for workflow completion

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Complete compliance status for all updated files
    - Summary of template alignment achievement
    - Final quality assessment and recommendations

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Final compliance verification results for all updated commands'
    modifications: [] # verification is read-only
    outputs:
      total_files_verified: [number]
      compliance_rate: [percentage]
      template_alignment: complete|partial|incomplete
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

In a single message, you spin up review subagents to check quality, up to **2** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the Workflow Quality Assessor mindset**

    - You're a **Workflow Quality Assessor** with expertise in final quality review who follows these principles:
      - **Comprehensive Review**: Assess overall workflow success and quality
      - **Risk Identification**: Identify any remaining compliance gaps
      - **Success Review**: Confirm workflow objectives have been achieved
      - **Review-Only Role**: You MUST NOT modify any resources - only report issues

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review the standards recursively (if A references B, review B too) that were applied**:

    - documentation.md - Final documentation compliance check
    - universal/scan.md - Overall quality validation

    **Review Assignment**
    You're assigned to review the overall success of the command update workflow:

    - Overall workflow completion status
    - Template compliance achievement across all files
    - Quality of updates applied to command files

    **Template Reference**: template:command

    **Review Steps**

    1. **Review workflow execution results** from all previous phases
    2. **Sample check updated files** for template compliance
    3. **Assess overall quality** of the update process
    4. **Review workflow objectives** have been achieved
    5. **Identify any remaining issues** requiring attention

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Overall workflow success assessment
    - Template compliance review
    - Quality of command file updates

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Final workflow quality assessment and success validation'
    checks:
      workflow_completion: pass|fail
      template_compliance: pass|fail
      update_quality: pass|fail
      objective_achievement: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + review)
2. **Apply decision criteria**:
   - Review any critical failures
   - Consider review recommendations
3. **Select next action**:
   - **PROCEED**: All success or acceptable partial success → Complete workflow successfully
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
   - **ROLLBACK**: Critical failures → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all remaining items as 'completed' and add workflow success
   - If FIX ISSUES: Add new todo items for correction tasks
   - If ROLLBACK: Mark workflow as 'failed' and add rollback todos
5. **Prepare final outputs**:
   - If PROCEED: Generate final success report with all updated files
   - If FIX ISSUES: Prepare correction instructions
   - If ROLLBACK: Document rollback actions and failure reasons

In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues.

### Workflow Completion

**Report the workflow output as specified**:

```yaml
updated_commands: ["path/to/command1.md", "path/to/command2.md", "..."]
change_summary:
  total_commands_processed: 5
  successfully_updated: 5
  template_compliance_achieved: true|false
  changes_applied:
    - "Updated metadata format"
    - "Added missing sections"
    - "Removed instruction comments"
    - "..."
verification_report:
  compliance_status: "pass|fail"
  template_alignment: "complete|partial|incomplete"
  issues_found: ["issue1", "issue2", "..."]
  warnings: ["warning1", "warning2", "..."]
failed_updates: 
  - file: "path/to/failed.md"
    reason: "description of failure"
workflow_status: "success|partial|failure"
summary: "Brief description of command update completion"
```
