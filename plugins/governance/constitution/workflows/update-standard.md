# Update Standard

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Update multiple standard directories to add new patterns, clarify requirements, or expand coverage while maintaining consistency and preserving all valid existing content across the standards system.
**When to use**: When AI needs to modify standard directories in [plugin]/constitution/standards/ to add content, fix issues, enhance documentation, or fill gaps while maintaining template compliance across multiple standards. Each standard is a directory containing `meta.md`, `scan.md`, `write.md`, and a `rules/` subdirectory.
**Prerequisites**: Understanding of standards system structure, clear requirements for what needs changing, familiarity with the three-tier standard template structure: template:standard-meta, template:standard-scan, template:standard-write.

### Your Role

You are a **Standards Evolution Director** who orchestrates the multi-standard maintenance process like a technical documentation curator ensuring continuous improvement while preserving valuable existing content. You never execute editing tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break standard updates into parallel batches with specialized enhancement teams (max 2-3 directories per subagent)
- **Parallel Coordination**: Run multiple subagents simultaneously when dependencies allow for efficient processing
- **Quality Oversight**: Ensure updates improve standards without breaking existing functionality through comprehensive review
- **Template Compliance**: Ensure all updated standards strictly follow the three-tier template structure (template:standard-meta, template:standard-scan, template:standard-write)

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

None

#### Optional Inputs

- **Scope of Standard Directories**: Either specific paths or function type (e.g., "backend", "frontend", "testing", "naming") to filter which standard directories to update (default: all standard directories if unspecified)
- **Things to Change**: Specific changes, additions, or enhancements needed across the selected standards (default: template compliance improvements)

#### Expected Outputs

- **Updated Standard Directories**: Enhanced standards (meta.md, scan.md, write.md per directory) with new content while preserving existing valid material
- **Change Documentation**: Summary of all modifications made across all standards with rationale
- **Template Compliance Report**: Confirmation that all updates maintain three-tier template consistency
- **Batch Processing Summary**: Details of how standard directories were processed in parallel batches

#### Data Flow Summary

The workflow takes optional scope criteria and change requirements, identifies relevant standard directories (each containing meta.md, scan.md, write.md), processes them in parallel batches through specialized subagents (max 2-3 directories per agent), and ensures all updates maintain three-tier template compliance while preserving existing valid content.

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
[Step 1: Update Standards] ──────→ Phase 1: Planning (You identify standard directories to update)
   |                                 |
   |                                 v
   |                              Phase 2: Execution (Subagents update standard directories in parallel)
   |                                 ├─ Subagent A: Batch 1 (≤3 directories)   ─┐
   |                                 ├─ Subagent B: Batch 2 (≤3 directories)   ─┼─→ [Decision: Quality OK?]
   |                                 └─ Subagent N: Batch N (≤3 directories)   ─┘
   |                                 |
   |                                 v
   |                              Phase 3: Review (Subagents verify three-tier template compliance)
   |                                 ├─ Review Agent A: Batch 1 (≤3 directories) ─┐
   |                                 ├─ Review Agent B: Batch 2 (≤3 directories) ─┼─→ [Decision: Proceed?]
   |                                 └─ Review Agent N: Batch N (≤3 directories) ─┘
   |                                 |
   |                                 v
   |                              Phase 4: Decision (You decide next action)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel batches (max 3 directories each)
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note: 
• You: Lists standard directories, batches work, assigns tasks, makes decisions
• Execution Subagents: Update standard directories following template:standard-meta, template:standard-scan, template:standard-write (<1k tokens)
• Review Subagents: Check three-tier template compliance and quality (<500 tokens)
• Workflow is SINGLE STEP with 4 PHASES: Planning → Execution → Review → Decision
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Update Standards

### Step 1: Update Standards

**Step Configuration**:

- **Purpose**: Update multiple standard directories in parallel batches while ensuring three-tier template compliance and content consistency
- **Input**: Scope of standard directories, Things to change from workflow inputs
- **Output**: Updated standard directories (meta.md, scan.md, write.md), change documentation, template compliance report, batch processing summary
- **Sub-workflow**: None
- **Parallel Execution**: Yes

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from external sources (optional scope and things to change)
2. **List all standard directories to update** by finding directories under [plugin]/constitution/standards/ that contain `meta.md` (do NOT read file contents):
   - Discovery: find directories containing `meta.md` — each such directory is a standard unit containing `meta.md`, `scan.md`, `write.md`, and a `rules/` subdirectory
   - If scope specified: Filter by directory name or function type (backend, frontend, testing, naming, etc.)
   - If scope not specified: Include all standard directories in [plugin]/constitution/standards/
   - Each directory is batched as a single unit (not individual files)
3. **Determine templates and standards** to send to subagents:
   - template:standard-meta (template for meta.md structure)
   - template:standard-scan (template for scan.md structure)
   - template:standard-write (template for write.md structure)
   - documentation.md (for documentation quality)
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on standard directories found
   - Limit each batch to max 2-3 standard directories (each directory = 3 tier files, so max 6-9 files per batch for context efficiency)
   - Assign one single subagent to perform updates on all standards in their batch
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare task assignments** with three-tier template compliance requirements (template:standard-meta, template:standard-scan, template:standard-write)
7. **Queue all batches** for parallel execution by subagents

**OUTPUT from Planning**: Standard directory batch assignments as todos

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
      - **Template Compliance**: Ensure every updated standard directory follows the three-tier template structure exactly (meta.md → template:standard-meta, scan.md → template:standard-scan, write.md → template:standard-write)
      - **Content Consistency**: Make updated standard tier files fluid, clear, and consistent with their respective templates
      - **Quality Enhancement**: Improve readability and understanding without changing core meaning
      - **Preservation Excellence**: Keep existing valid content intact while enhancing organization

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Use the following template files** (these are templates to follow, not standards to follow):

    - template:standard-meta - Follow this template structure for meta.md files
    - template:standard-scan - Follow this template structure for scan.md files
    - template:standard-write - Follow this template structure for write.md files

    **Assignment**
    You're assigned with the following standard directories to update (max 3 directories):

    - [standard directory 1] (meta.md, scan.md, write.md)
    - [standard directory 2] (meta.md, scan.md, write.md)
    - [standard directory 3] (meta.md, scan.md, write.md)

    **Steps**

    1. Read and analyze each assigned standard directory:
       - Read all three tier files (meta.md, scan.md, write.md) in the directory
       - Compare meta.md against template:standard-meta
       - Compare scan.md against template:standard-scan
       - Compare write.md against template:standard-write
       - Identify content that needs reorganization for template compliance in each tier file
       - Note sections that need enhancement or clarification based on "Things to Change" input
    2. Apply requested changes while ensuring template compliance:
       - Implement specific changes requested in "Things to Change" input (if provided)
       - Apply updates to the correct tier file based on what's changing (metadata changes → meta.md, scanning rules → scan.md, writing guidance → write.md)
       - Ensure each tier file matches its corresponding template structure exactly
       - Ensure all required template sections are present and properly filled in each tier
       - Make content fluid and clear while maintaining original intent
    3. Save all three tier files back to their original locations:
       - Preserve all existing valid content while improving organization
       - Ensure consistency of meta.md with template:standard-meta
       - Ensure consistency of scan.md with template:standard-scan
       - Ensure consistency of write.md with template:standard-write
       - Maintain logical flow and readability throughout each document

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - List of standard directories successfully updated with three-tier template compliance
    - Summary of changes made to each tier file (meta.md, scan.md, write.md) per directory
    - Template compliance verification for each tier file against its respective template
    - Any issues encountered during the update process

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of standard updates completion'
    modifications: ['path/to/standard-dir1/meta.md', 'path/to/standard-dir1/scan.md', 'path/to/standard-dir1/write.md', ...]
    outputs:
      updated_directories: ['standard-dir1', 'standard-dir2', ...]
      tier_compliance:
        meta: true|false   # compliance with template:standard-meta
        scan: true|false   # compliance with template:standard-scan
        write: true|false  # compliance with template:standard-write
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
      - **Template Compliance**: Verify every updated standard directory strictly follows the three-tier template structure (meta.md → template:standard-meta, scan.md → template:standard-scan, write.md → template:standard-write)
      - **Content Quality**: Ensure updates improve clarity while preserving essential information
      - **Consistency Check**: Confirm all standard tier files maintain uniform formatting and organization
      - **Review-Only Role**: You MUST NOT modify any resources - only report compliance issues

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review against the following templates** (these are templates to verify compliance with):

    - template:standard-meta - Verify all meta.md files follow this template structure exactly
    - template:standard-scan - Verify all scan.md files follow this template structure exactly
    - template:standard-write - Verify all write.md files follow this template structure exactly

    **Review Assignment**
    You're assigned to review the following updated standard directories (max 3 directories):

    - [standard directory 1] (meta.md, scan.md, write.md):
      - Summary of changes made during phase 2
    - [standard directory 2] (meta.md, scan.md, write.md):
      - Summary of changes made during phase 2
    - [standard directory 3] (meta.md, scan.md, write.md):
      - Summary of changes made during phase 2

    **Review Steps**

    1. Read each tier file (meta.md, scan.md, write.md) in each updated standard directory
    2. Check meta.md against template:standard-meta, scan.md against template:standard-scan, write.md against template:standard-write
    3. Verify content is properly organized and flows logically within each tier file
    4. Confirm existing valid content was preserved during updates

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Template compliance status for each tier file (meta.md, scan.md, write.md) per directory
    - Content quality and organization assessment for each tier
    - Preservation of existing valid content verification
    - Any critical issues that need immediate attention

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief verification summary of updated standard directories'
    checks:
      meta_template_compliance: pass|fail   # meta.md vs template:standard-meta
      scan_template_compliance: pass|fail   # scan.md vs template:standard-scan
      write_template_compliance: pass|fail  # write.md vs template:standard-write
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
updated_standard_directories:
  - directory: "path/to/standard1/"
    files: ["meta.md", "scan.md", "write.md"]
  - directory: "path/to/standard2/"
    files: ["meta.md", "scan.md", "write.md"]
change_documentation:
  modifications_per_directory:
    "standard1":
      meta: ["change1", "change2", "..."]
      scan: ["change1", "..."]
      write: ["change1", "..."]
    "standard2":
      meta: ["change1", "..."]
      scan: ["change1", "..."]
      write: ["change1", "..."]
  content_preserved: true|false
  rationale: "explanation of batch processing approach"
  date_updated: "YYYY-MM-DD"
template_compliance_report:
  compliance_status: "compliant|partial|non_compliant"
  templates_used:
    - "template:standard-meta"
    - "template:standard-scan"
    - "template:standard-write"
  compliant_directories: ["dir1", "dir2", "..."]
  non_compliant_directories: ["dir3", "dir4", "..."]
batch_processing_summary:
  total_batches: N
  directories_per_batch: "≤3"
  execution_subagents: N
  review_subagents: N
  retry_count: N
workflow_status: "success|partial|failure"
summary: "Brief description of multi-standard update completion"
```
