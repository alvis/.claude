# Create Workflow

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Create a new constitution workflow document that defines repeatable processes and procedures for consistent task execution across the team
**When to use**: When establishing new processes, documenting recurring tasks, standardizing team procedures, or capturing best practices for specific operations
**Prerequisites**:

- Understanding of the process being documented
- Review of existing workflows to avoid duplication
- Access to templates/workflow.md file

### Management Role

You are a **Workflow Creation Director** who orchestrates the workflow creation process like a publishing editor coordinating a team of writers. You never write content directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break workflow creation into parallel documentation tasks when multiple sections can be written independently
- **Parallel Coordination**: Maximize efficiency by running multiple documentation subagents simultaneously for different workflow sections
- **Quality Oversight**: Review workflow structure and content objectively without writing details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and template compliance
- **Template Adherence**: Ensure strict compliance with the workflow template structure

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Workflow Name**: The name/title of the workflow to create (e.g., 'Build Service', 'Review Code')

#### Optional Inputs

- **Step Instructions**: Step-by-step instructions describing how the workflow should operate
- **Standards List**: Specific standards that should be referenced in the workflow
- **Category**: Category for the workflow (e.g., 'backend', 'frontend', 'quality', 'project')

#### Expected Outputs

- **Workflow File**: Complete workflow document at `constitutions/workflows/[category]/[workflow-name].md`
- **Creation Report**: Summary of workflow creation process and validation results
- **Index Updates**: Updated README files with new workflow listed
- **Compliance Status**: Pass/fail status for template compliance checks

#### Data Flow Summary

The workflow takes a workflow name and optional instructions, uses the template to create a properly structured workflow document, validates compliance, and updates all relevant indexes to register the new workflow in the constitution system.

### Visual Overview

#### Main Workflow Flow

```plaintext
     MANAGEMENT AGENT                    SUBAGENTS EXECUTE
     (Orchestrates Only)                 (Perform Tasks)
            |                                   |
            v                                   v
[START]
   |
   v
[Step 1: Analyze Need] ───────────→ (Subagents Execute)
   |                                 ├─ Research Agent: Check existing workflows
   |                                 └─ Analysis Agent: Validate uniqueness
   v
[Step 2: Create Structure] ──────→ (Subagent: Copy template, create file)
   |
   v
[Step 3: Define Content] ────────→ (Subagents Execute in Parallel)
   |                                ├─ Content Agent A: Write introduction
   |                                ├─ Content Agent B: Define steps
   |                                └─ Content Agent C: Add standards
   v
[Step 4: Validate Compliance] ───→ (Verification Agent: Check template compliance)
   |
   v
[Step 5: Remove AI Instructions] → (Cleanup Agent: Remove AI comments)
   |
   v
[Step 6: Update Indexes] ────────→ (Subagents Execute in Parallel)
   |                                ├─ Index Agent A: Update main README
   |                                └─ Index Agent B: Update category README
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: Management Agent plans & orchestrates (no execution)
• RIGHT SIDE: Subagents execute tasks, some in parallel
• ARROWS (───→): Management assigns work to subagents
• DECISIONS: Management agent decides based on subagent reports
• Workflow is LINEAR: Step 1 → 2 → 3 → 4 → 5 → 6
═══════════════════════════════════════════════════════════════════
```

#### Workflow State Machine

##### Main Workflow States

```plaintext
[INIT] ──> [ANALYZE] ──> [CREATE] ──> [CONTENT] ──> [VALIDATE] ──> [CLEAN] ──> [INDEX] ──> [COMPLETE]
              ↑  ↓         ↑  ↓        ↑  ↓          ↑  ↓         ↑  ↓       ↑  ↓
              └──┘         └──┘        └──┘          └──┘         └──┘       └──┘
           (retry)      (retry)     (retry)      (retry)      (retry)    (retry)
              ↓            ↓           ↓             ↓            ↓          ↓
          [FAILED]     [FAILED]    [FAILED]     [FAILED]     [FAILED]   [FAILED]
```

##### Step Internal States (for EACH main step)

```plaintext
[PLANNING] ──> [EXECUTING] ──> [REPORTING] ──> [VERIFYING] ──> [DECIDING]
     ↑              ↓               ↓               ↓              ↓
     └──────────────┴───────────────┴───────────────┴──────────────┘
                            (retry/rollback paths)
```

### Dependencies & Patterns

#### Step Execution Pattern

```plaintext
     MANAGEMENT AGENT                    SUBAGENTS EXECUTE
     (Orchestrates Only)                 (Perform Tasks)
            |                                   |
            v                                   v

[Step N Phase 1: Plan] ─────────→ (Management Agent: analyzes requirements)
        |
        v
[Step N Phase 2: Execute] ──────→ (Execution Subagents: work in parallel when possible)
        |                     ├─ Execution Subagent A            ─┐
        |                     ├─ Execution Subagent B (Optional) ─┼─→ [Reports]
        |                     └─ Execution Subagent C (Optional) ─┘
        v
[Step N Phase 3: Review] ───────→ (Management Agent: reviews reports)
        |
        v
[Step N Phase 4: Verify?] ──────→ (Management Agent: decides if verification needed)
        |                          |
        |                          v
        |                    (Verification Subagent: checks quality) → [Report]
        v
[Step N Phase 5: Decide] ───────→ (Management Agent: decides next action)
                                   |
                         ┌─────────┼─────────┐
                         │         │         │
                    Next Step  Retry Step  Rollback

Legend:
═══════════════════════════════════════════════════════════════════
• This happens INSIDE each main workflow step
• Phase 1: Management Agent plans and assigns
• Phase 2: Execution Subagents perform work
• Phase 3: Management Agent reviews results
• Phase 4: Verification Subagents check quality (if needed)
• Phase 5: Management Agent makes decision
• Each phase completes before next phase begins
═══════════════════════════════════════════════════════════════════
```

## 3. AGENT ARCHITECTURE & COMMUNICATION

### Three Agent Types

#### 1. Management Agent

- **Role**: Orchestrator and decision maker
- **Responsibilities**:
  - Plan task decomposition
  - Assign work to execution subagents
  - Review execution reports
  - Decide if verification needed
  - Make linear workflow decisions (next/retry/rollback)
- **Restrictions**:
  - Cannot read file contents
  - Cannot execute tasks directly
  - Can only list/batch resources

#### 2. Execution Subagents

- **Role**: Task performers
- **Responsibilities**:
  - Receive specific task from management
  - Adopt assigned expert mindset
  - Read and follow all assigned standards recursively
  - Execute assigned work
  - Report results (<1k tokens)
- **Output**: Status, summary, and requested deliverables

#### 3. Verification Subagents

- **Role**: Quality assurance
- **Responsibilities**:
  - Verify execution subagent work
  - Check against requirements
  - Report pass/fail with details
- **Output**: Pass/fail status with recommendations

### Report Token Limits

- **Execution Subagent**: Max 1000 tokens per report
- **Verification Subagent**: Max 500 tokens per report
- **Management Agent**: Max 200 tokens per decision

## 4. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Analyze Need
2. Create Structure
3. Define Content
4. Validate Compliance
5. Remove AI Instructions
6. Update Indexes

### Step 1: Analyze Need

**Step Configuration**:

- **Purpose**: Validate need for new workflow and identify appropriate category
- **Input**: Workflow name and optional instructions
- **Output**: Analysis confirming need, category selection, no overlap with existing
- **Sub-workflow**: None
- **Parallel Execution**: Yes - check multiple directories simultaneously

#### Phase 1: Planning (Management Agent)

**What Management Agent Does**:

1. **Receive inputs** (workflow name, optional instructions)
2. **List existing workflows** in all category directories
3. **Identify category** based on workflow name or default to 'project'
4. **Create analysis tasks**:
   - Check for name conflicts
   - Validate category appropriateness
   - Assess workflow scope
5. **Use TodoWrite** to track analysis tasks
6. **Queue tasks** for parallel execution

**OUTPUT from Planning**: Analysis task assignments

**Task Assignment Matrix** (dynamically generated):

| Batch ID | Subagent Type | Resources | Standards | Expected Outcome |
|----------|---------------|-----------|-----------|------------------|
| batch_1  | ResearchAgent | existing workflows | Documentation | Overlap analysis |
| batch_2  | AnalysisAgent | workflow name | Naming conventions | Validation complete |

#### Phase 2: Execution (Execution Subagents)

**What Management Agent Sends to Subagents**:

In a single message, the management agent spins up subagents to analyze the need, up to **2** subagents at a time.

- **[IMPORTANT]** When there are any issues reported, the management agent must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** The management agent MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **Adopt the Workflow Analyst mindset**

    - You're a **Workflow Analyst** with expertise in process documentation who follows these principles:
      - **Uniqueness Verification**: Ensure no duplicate or overlapping workflows exist
      - **Category Alignment**: Validate correct category placement
      - **Scope Assessment**: Confirm workflow scope is appropriate

    **Read the following assigned standards** and follow them recursively:

    - `constitutions/standards/code/documentation.md`
    - `constitutions/standards/code/general-principles.md`

    **Assignment**
    You're assigned to analyze the need for workflow: [workflow name]

    **Steps**

    1. List and review existing workflows in the [category] directory
    2. Check for name conflicts or functional overlaps
    3. Validate the workflow name follows naming conventions
    4. Assess if the scope warrants a new workflow
    5. Recommend category placement

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Name availability status
    - List of any overlapping workflows
    - Recommended category placement
    - Scope appropriateness assessment

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Analysis of workflow need'
    modifications: []
    outputs:
      name_available: true|false
      overlapping_workflows: ['workflow1.md', 'workflow2.md', ...]
      recommended_category: 'backend|frontend|quality|project|...'
      scope_appropriate: true|false
    issues: ['name conflict with existing-workflow.md', ...]
    ```
    <<<

#### Phase 3: Review (Management Agent)

**What Management Agent Does**:

1. **Use TodoRead** to check current task statuses
2. **Collect analysis reports** from subagents
3. **Parse report statuses** (success/failure/partial)
4. **Use TodoWrite** to update batch statuses
5. **Evaluate findings**:
   - Check if name is available
   - Review any overlapping workflows
   - Confirm category selection
6. **Determine next action** based on analysis

#### Phase 4: Verification (Verification Subagents) - Optional

**When Management Triggers Verification**: Only if potential overlaps are found

#### Phase 5: Decision (Management Agent)

**What Management Agent Does**:

1. **Analyze all reports**
2. **Apply decision criteria**:
   - Name must be available
   - No significant overlaps
   - Scope is appropriate
3. **Select next action**:
   - **PROCEED**: Continue to Step 2
   - **ABORT**: Stop if overlap found or name taken
   - **RETRY**: If analysis incomplete
4. **Use TodoWrite** to update final status
5. **Log decision rationale**

### Step 2: Create Structure

**Step Configuration**:

- **Purpose**: Create initial workflow file from template
- **Input**: Category selection, workflow name from Step 1
- **Output**: Initial workflow file with basic structure
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (Management Agent)

**What Management Agent Does**:

1. **Identify target location**: `constitutions/workflows/[category]/[workflow-name].md`
2. **Verify template exists** at `templates/workflow.md`
3. **Create file creation task**
4. **Use TodoWrite** to track task
5. **Prepare creation instructions**

#### Phase 2: Execution (Execution Subagents)

**What Management Agent Sends to Subagents**:

Request the subagent to perform the following file creation:

    >>>
    **Adopt the Workflow Creator mindset**

    - You're a **Workflow Creator** who follows these principles:
      - **Template Adherence**: Copy template structure exactly
      - **Metadata Accuracy**: Set correct workflow title and metadata
      - **File Organization**: Place in correct directory

    **Assignment**
    Create new workflow file: [workflow-name].md

    **Template**: `templates/workflow.md`
    **Target**: `constitutions/workflows/[category]/[workflow-name].md`

    **Steps**

    1. Read the workflow template file
    2. Copy template content to new location
    3. Replace placeholder title with actual workflow name
    4. Update the INSTRUCTION comment at top with workflow purpose
    5. Save file to target location

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure
    summary: 'Created workflow file from template'
    modifications: ['constitutions/workflows/[category]/[workflow-name].md']
    outputs:
      file_path: 'constitutions/workflows/[category]/[workflow-name].md'
      sections_present: ['introduction', 'overview', 'architecture', 'implementation']
    issues: []
    ```
    <<<

#### Phase 3-5: Review, Verify, Decide

Standard phases to confirm file creation and proceed.

### Step 3: Define Content

**Step Configuration**:

- **Purpose**: Populate all workflow sections with content
- **Input**: Workflow file path from Step 2, optional step instructions
- **Output**: Complete workflow with all sections filled
- **Sub-workflow**: None
- **Parallel Execution**: Yes - multiple sections can be written simultaneously

#### Phase 1: Planning (Management Agent)

**What Management Agent Does**:

1. **Identify sections to populate**:
   - Introduction (purpose, when to use, prerequisites)
   - Visual overview (workflow diagram, state machine)
   - Step definitions (based on provided instructions)
   - Standards references
2. **Create content batches** for parallel writing
3. **Assign relevant standards** for each section
4. **Use TodoWrite** to track content tasks
5. **Queue batches** for parallel execution

**Task Assignment Matrix**:

| Batch ID | Subagent Type | Section | Standards | Expected Outcome |
|----------|---------------|---------|-----------|------------------|
| batch_1  | ContentAgent | Introduction | Documentation | Purpose and context defined |
| batch_2  | ContentAgent | Steps 1-3 | General principles | Initial steps documented |
| batch_3  | ContentAgent | Steps 4-6 | General principles | Final steps documented |
| batch_4  | ContentAgent | Visual diagrams | Template | Diagrams created |

#### Phase 2: Execution (Execution Subagents)

**What Management Agent Sends to Subagents**:

In a single message, spin up content subagents to write sections in parallel, up to **3** subagents at a time.

Request each subagent to perform the following content creation:

    >>>
    **Adopt the Workflow Documentation Expert mindset**

    - You're a **Workflow Documentation Expert** who follows these principles:
      - **Clarity First**: Write clear, actionable documentation
      - **Template Compliance**: Follow the exact template structure
      - **Practical Examples**: Include concrete examples for each step
      - **5-Phase Pattern**: Ensure each step follows the 5-phase execution pattern

    **Assignment**
    Write content for section: [section name]
    
    **Workflow Instructions** (if provided):
    [step-by-step instructions from user]

    **Steps**

    1. Read the current workflow file
    2. Understand the section requirements from template
    3. Write detailed content for assigned section:
       - For steps: Include all 5 phases (Planning, Execution, Review, Verification, Decision)
       - For introduction: Define purpose, when to use, prerequisites
       - For visual overview: Create ASCII diagrams with proper formatting
       - For standards: List all applicable standards with links
    4. Include specific examples and clear instructions
    5. Ensure >>> <<< blocks for subagent messages
    6. Update the workflow file with new content

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Content written for [section]'
    modifications: ['workflow-file.md']
    outputs:
      section_completed: '[section name]'
      subsections_added: ['phase 1', 'phase 2', ...]
      examples_included: true|false
      word_count: 500
    issues: ['unclear instruction for step 3', ...]
    ```
    <<<

#### Phase 3-5: Review, Verify, Decide

Standard phases to review content completeness and quality.

### Step 4: Validate Compliance

**Step Configuration**:

- **Purpose**: Verify strict template compliance and quality standards
- **Input**: Complete workflow file from Step 3
- **Output**: Compliance validation report
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (Management Agent)

**What Management Agent Does**:

1. **Create comprehensive checklist** from template requirements
2. **Identify all compliance points** to verify
3. **Assign verification task**
4. **Use TodoWrite** to track validation

#### Phase 2: Execution (Execution Subagents)

Request the subagent to perform comprehensive validation:

    >>>
    **Adopt the Template Compliance Auditor mindset**

    - You're a **Template Compliance Auditor** who follows these principles:
      - **Strict Validation**: Check every template requirement
      - **Structural Integrity**: Verify all sections present and correct
      - **Pattern Compliance**: Ensure 5-phase pattern in all steps
      - **Quality Standards**: Validate documentation quality

    **Assignment**
    Validate workflow compliance: [workflow-name].md

    **Template**: `templates/workflow.md`

    **Steps**

    1. Read the completed workflow file
    2. Read the template for comparison
    3. Check Template Compliance Checklist:
       
       **Structural Requirements**:
       - Main workflow steps clearly defined (business logic, not execution pattern)
       - Each step includes 5-phase internal execution pattern
       - ASCII workflow diagram with START and END nodes
       - Step dependency map in YAML format (if applicable)
       - Sub-workflow integration points identified (if applicable)
       
       **Agent Architecture**:
       - Three agent types clearly differentiated
       - Management agent restricted to orchestration only
       - Execution subagents have clear contracts
       - Verification subagents have pass/fail criteria
       - Parallel execution opportunities identified
       
       **Communication Protocols**:
       - Token limits specified (Execution: 1k, Verification: 500, Management: 200)
       
       **Workflow Control Flow**:
       - Decision gates after each step
       - Retry logic with limits
       - Rollback procedures documented
       - State machine diagrams present
       
       **Quality Assurance**:
       - Standards references included
       - Recursive reading requirement stated
       - Final validation checklist present

    4. Document any violations or missing elements
    5. Assess overall compliance level

    **Report**
    **[IMPORTANT]** You MUST return the following verification report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Template compliance validation results'
    checks:
      structural_requirements:
        main_workflow_steps: pass|fail
        five_phase_pattern: pass|fail
        ascii_diagrams: pass|fail
        step_dependencies: pass|fail|n/a
        sub_workflow_points: pass|fail|n/a
      agent_architecture:
        three_agent_types: pass|fail
        management_restrictions: pass|fail
        execution_contracts: pass|fail
        verification_criteria: pass|fail
        parallel_execution: pass|fail
      communication_protocols:
        token_limits: pass|fail
      workflow_control:
        decision_gates: pass|fail
        retry_logic: pass|fail
        rollback_procedures: pass|fail
        state_machines: pass|fail
      quality_assurance:
        standards_references: pass|fail
        recursive_reading: pass|fail
        final_checklist: pass|fail
    critical_issues: ['missing retry logic in step 3', ...]
    warnings: ['minor formatting issue', ...]
    recommendation: proceed|fix|restart
    ```
    <<<

#### Phase 3-5: Review, Verify, Decide

Review validation results and determine if fixes are needed.

### Step 5: Remove AI Instructions

**Step Configuration**:

- **Purpose**: Remove AI instruction comments from the finalized workflow
- **Input**: Validated workflow file from Step 4
- **Output**: Clean workflow file without AI instructions
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (Management Agent)

**What Management Agent Does**:

1. **Identify cleanup task** for AI instruction removal
2. **Create removal instructions**
3. **Use TodoWrite** to track cleanup

#### Phase 2: Execution (Execution Subagents)

Request the subagent to clean the workflow:

    >>>
    **Adopt the Workflow Cleanup Specialist mindset**

    - You're a **Workflow Cleanup Specialist** who follows these principles:
      - **Precision Removal**: Remove only AI instructions
      - **Content Preservation**: Keep all workflow content intact
      - **Comment Handling**: Preserve non-AI comments

    **Assignment**
    Remove AI instructions from: [workflow-name].md

    **Steps**

    1. Read the validated workflow file
    2. Identify all AI instruction comments:
       - HTML comments containing "INSTRUCTION"
       - Template placeholder instructions
       - Example markers to be removed
    3. Remove identified AI instructions while preserving:
       - All workflow content
       - User-facing comments
       - Code blocks and examples
    4. Save the cleaned workflow

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure
    summary: 'AI instructions removed from workflow'
    modifications: ['workflow-file.md']
    outputs:
      instructions_removed: 15
      content_preserved: true
      file_cleaned: true
    issues: []
    ```
    <<<

### Step 6: Update Indexes

**Step Configuration**:

- **Purpose**: Update workflow indexes and references
- **Input**: Clean workflow file path from Step 5
- **Output**: Updated README files with new workflow listed
- **Sub-workflow**: None
- **Parallel Execution**: Yes - update multiple indexes simultaneously

#### Phase 1: Planning (Management Agent)

**What Management Agent Does**:

1. **Identify indexes to update**:
   - Main workflows README
   - Category-specific README
2. **Create update tasks** for each index
3. **Use TodoWrite** to track updates

#### Phase 2: Execution (Execution Subagents)

In a single message, spin up index subagents in parallel, up to **2** subagents at a time:

    >>>
    **Adopt the Index Maintainer mindset**

    - You're an **Index Maintainer** who follows these principles:
      - **Consistent Formatting**: Maintain existing index format
      - **Alphabetical Order**: Keep entries sorted
      - **Link Accuracy**: Ensure correct relative paths

    **Assignment**
    Update index: [README path]
    Add workflow: [workflow-name]

    **Steps**

    1. Read the current README/index file
    2. Locate the appropriate section for workflow listing
    3. Add new workflow entry:
       - Title with link to workflow file
       - Brief description of purpose
       - Maintain alphabetical order
    4. Update the file with new entry

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure
    summary: 'Index updated with new workflow'
    modifications: ['[README path]']
    outputs:
      index_file: '[README path]'
      entry_added: '[workflow-name]'
      position: 'Added at position 5 of 12'
    issues: []
    ```
    <<<

### Final Step: Completion Confirmation

**Step Configuration**:

- **Purpose**: Confirm successful workflow creation and all deliverables
- **Input**: All outputs from previous steps
- **Output**: Final deliverables and creation report
- **Sub-workflow**: None
- **Parallel Execution**: No

**Completion Checklist**:

- [ ] All main workflow steps completed successfully
- [ ] Workflow passes template compliance validation
- [ ] AI instructions removed from final version
- [ ] All indexes updated with new workflow
- [ ] No overlap with existing workflows confirmed
- [ ] File saved in correct category directory

### Template Compliance Checklist

#### Structural Requirements

- [x] Main workflow steps clearly defined (business logic, not execution pattern)
- [x] Each step includes 5-phase internal execution pattern
- [x] ASCII workflow diagram with START and END nodes
- [x] Step dependency map in YAML format
- [x] Sub-workflow integration points identified (if applicable)

#### Agent Architecture

- [x] Three agent types clearly differentiated (Management, Execution, Verification)
- [x] Management agent restricted to orchestration only (no file reading)
- [x] Execution subagents have clear input/output contracts
- [x] Verification subagents have defined pass/fail criteria
- [x] Parallel execution opportunities identified and documented

#### Communication Protocols

- [x] All reports specified under token limits (Execution: 1k, Verification: 500, Management: 200)

#### Workflow Control Flow

- [x] Decision gates after each step with linear flow logic (next/retry/rollback)
- [x] Retry logic with maximum attempt limits (typically 3)
- [x] Rollback procedures for failure scenarios
- [x] State machine diagrams for both main workflow and step internals

#### Quality Assurance

- [x] Standards references included in Section 4 for Management Agent to assign to subagents
- [x] Recursive standard reading requirement clearly stated
- [x] Final validation checklist in last step
