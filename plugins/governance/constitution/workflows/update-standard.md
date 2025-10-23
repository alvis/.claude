# Update Standard

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Update multiple standard documentation files to add new patterns, clarify requirements, or expand coverage while maintaining consistency and preserving all valid existing content across the standards system.
**When to use**: When AI needs to modify standard files in [plugin]/constitution/standards/ to add content, fix issues, enhance documentation, or fill gaps while maintaining template compliance across multiple standards.
**Prerequisites**: Understanding of standards system structure, clear requirements for what needs changing, familiarity with template:standard template structure.

### Your Role

You are a **Standards Evolution Director** who orchestrates the multi-standard maintenance process like a technical documentation curator ensuring continuous improvement while preserving valuable existing content. You never execute editing tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break standard updates into parallel batches with specialized enhancement teams (max 5 standards per subagent)
- **Parallel Coordination**: Run multiple subagents simultaneously when dependencies allow for efficient processing
- **Quality Oversight**: Ensure updates improve standards without breaking existing functionality through comprehensive review
- **Template Compliance**: Ensure all updated standards strictly follow the template:standard template structure

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

None

#### Optional Inputs

- **Scope of Standard Files**: Either specific paths or function type (e.g., "backend", "frontend", "testing", "naming") to filter which standards to update (default: all standard files if unspecified)
- **Things to Change**: Specific changes, additions, or enhancements needed across the selected standards (default: template compliance improvements)

#### Expected Outputs

- **Updated Standard Files**: Enhanced standards with new content while preserving existing valid material
- **Change Documentation**: Summary of all modifications made across all standards with rationale
- **Template Compliance Report**: Confirmation that all updates maintain template consistency
- **Batch Processing Summary**: Details of how standards were processed in parallel batches

#### Data Flow Summary

The workflow takes optional scope criteria and change requirements, identifies relevant standard files, processes them in parallel batches through specialized subagents (max 5 standards per agent), and ensures all updates maintain template compliance while preserving existing valid content.

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
[Step 1: Update Standards] ──────→ Phase 1: Planning (You identify standard files to update)
   |                                 |
   |                                 v
   |                              Phase 2: Execution (Subagents update standards in parallel)
   |                                 ├─ Subagent A: Batch 1 (≤5 standards)     ─┐
   |                                 ├─ Subagent B: Batch 2 (≤5 standards)     ─┼─→ [Decision: Quality OK?]
   |                                 └─ Subagent N: Batch N (≤5 standards)     ─┘
   |                                 |
   |                                 v
   |                              Phase 3: Review (Subagents verify template compliance)
   |                                 ├─ Review Agent A: Batch 1 (≤5 standards) ─┐
   |                                 ├─ Review Agent B: Batch 2 (≤5 standards) ─┼─→ [Decision: Proceed?]
   |                                 └─ Review Agent N: Batch N (≤5 standards) ─┘
   |                                 |
   |                                 v
   |                              Phase 4: Decision (You decide next action)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel batches (max 5 standards each)
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note: 
• You: Lists standard files, batches work, assigns tasks, makes decisions
• Execution Subagents: Update standards following template:standard (<1k tokens)
• Review Subagents: Check template compliance and quality (<500 tokens)  
• Workflow is SINGLE STEP with 4 PHASES: Planning → Execution → Review → Decision
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Update Standards

### Step 1: Update Standards

**Step Configuration**:

- **Purpose**: Update multiple standard files in parallel batches while ensuring template compliance and content consistency
- **Input**: Scope of standard files, Things to change from workflow inputs
- **Output**: Updated standard files, change documentation, template compliance report, batch processing summary
- **Sub-workflow**: None
- **Parallel Execution**: Yes

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from external sources (optional scope and things to change)
2. **List all standard files to update** using find commands in [plugin]/constitution/standards/ (do NOT read file contents):
   - If scope specified: Filter by path pattern or function type (backend, frontend, testing, naming, etc.)
   - If scope not specified: Include all standard files in [plugin]/constitution/standards/
3. **Determine templates and standards** to send to subagents:
   - template:standard (template file to follow for structure)
   - documentation.md (for documentation quality)
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on standard files found
   - Limit each batch to max 5 standard files
   - Assign one single subagent to perform updates on all standards in their batch
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare task assignments** with template:standard compliance requirements
7. **Queue all batches** for parallel execution by subagents

**OUTPUT from Planning**: Standard file batch assignments as todos

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up subagents to perform standard updates in parallel, up to **10** subtasks at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about template compliance and content consistency
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Standards Enhancement Specialist mindset**

    - You're a **Standards Enhancement Specialist** with deep expertise in technical documentation who follows these technical principles:
      - **Template Compliance**: Ensure every updated standard follows the template:standard structure exactly
      - **Content Consistency**: Make updated standard files fluid, clear, and consistent with the template
      - **Quality Enhancement**: Improve readability and understanding without changing core meaning
      - **Preservation Excellence**: Keep existing valid content intact while enhancing organization

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Use the following template file** (this is a template to follow, not a standard to follow):

    - template:standard - Follow this template structure exactly for all standard file updates

    **Assignment**
    You're assigned with the following standard files to update (max 5 files):

    - [standard file 1]
    - [standard file 2]
    - [standard file 3]
    - [standard file 4] 
    - [standard file 5]

    **Steps**

    1. Read and analyze each assigned standard file:
       - Read the entire existing standard file content
       - Compare current structure against template:standard template
       - Identify content that needs reorganization for template compliance
       - Note sections that need enhancement or clarification based on "Things to Change" input
    2. Apply requested changes while ensuring template compliance:
       - Implement specific changes requested in "Things to Change" input (if provided)
       - Re-order content to match template:standard structure exactly
       - Ensure all required template sections are present and properly filled
       - Make content fluid and clear while maintaining original intent
    3. Update each standard file with enhanced content:
       - Preserve all existing valid content while improving organization
       - Ensure consistency with template:standard template structure
       - Maintain logical flow and readability throughout the document
       - Save updated files back to their original locations

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - List of standard files successfully updated with template compliance
    - Summary of changes made to each standard file
    - Template compliance verification for each file
    - Any issues encountered during the update process

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of standard updates completion'
    modifications: ['path/to/standard1.md', 'path/to/standard2.md', ...]
    outputs:
      updated_standards: ['file1', 'file2', ...]
      template_compliance: true|false
      changes_summary: 'Summary of changes made'
      preserved_content: true|false
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

**What You Send to Review Subagents**:

In a single message, you spin up review subagents to check update quality, up to **10** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical about template compliance
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the Template Compliance Reviewer mindset**

    - You're a **Template Compliance Reviewer** with expertise in documentation standards who follows these principles:
      - **Template Compliance**: Verify every updated standard strictly follows template:standard structure
      - **Content Quality**: Ensure updates improve clarity while preserving essential information
      - **Consistency Check**: Confirm all standards maintain uniform formatting and organization
      - **Review-Only Role**: You MUST NOT modify any resources - only report compliance issues

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review against the following template** (this is a template to verify compliance with):

    - template:standard - Verify all updated standards follow this template structure exactly

    **Review Assignment**
    You're assigned to review the following updated standard files (max 5 files):

    - [standard file 1]:
      - Summary of changes made during phase 2
    - [standard file 2]:
      - Summary of changes made during phase 2
    - [standard file 3]:
      - Summary of changes made during phase 2
    - [standard file 4]:
      - Summary of changes made during phase 2
    - [standard file 5]:
      - Summary of changes made during phase 2

    **Review Steps**

    1. Read each updated standard file to verify template compliance
    2. Check that all required sections from template:standard are present
    3. Verify content is properly organized and flows logically
    4. Confirm existing valid content was preserved during updates

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Template compliance status for each updated standard file
    - Content quality and organization assessment
    - Preservation of existing valid content verification
    - Any critical issues that need immediate attention

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief verification summary of updated standards'
    checks:
      template_compliance: pass|fail
      content_quality: pass|fail
      content_preservation: pass|fail
      organization_flow: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + review)
2. **Apply decision criteria**:
   - Review template compliance status and content quality
   - Consider preservation of existing content and organization flow
3. **Select next action**:
   - **PROCEED**: All standards successfully updated and reviewed → Complete workflow successfully
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
   - **ROLLBACK**: Critical template compliance failures → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → repeat until no more issues
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' items as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare completion**: Package final results for workflow output

In phase 4, you (the management) must decide whether to reask subagents in phase 2 to fix any issues found by subagents in phase 3, and repeat until no more issues remain.

### Workflow Completion

**Report the workflow output as specified**:

```yaml
updated_standard_files: ["path/to/standard1.md", "path/to/standard2.md", "..."]
change_documentation:
  modifications_per_file:
    "standard1.md": ["change1", "change2", "..."]
    "standard2.md": ["change1", "change2", "..."]
  content_preserved: true|false
  rationale: "explanation of batch processing approach"
  date_updated: "YYYY-MM-DD"
template_compliance_report:
  compliance_status: "compliant|partial|non_compliant" 
  template_used: "template:standard"
  compliant_files: ["file1", "file2", "..."]
  non_compliant_files: ["file3", "file4", "..."]
batch_processing_summary:
  total_batches: N
  standards_per_batch: "≤5"
  execution_subagents: N
  review_subagents: N
  retry_count: N
workflow_status: "success|partial|failure"
summary: "Brief description of multi-standard update completion"
```
