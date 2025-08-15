# [Workflow Title]

<!-- INSTRUCTION: Replace [Workflow Title] with a clear, action-oriented title (e.g., 'Build Service', 'Review Code', 'Publish Blog Posts') -->

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: [Describe the primary goal and outcome of this workflow]
**When to use**: [Specify exact scenarios and triggers for using this workflow]
**Prerequisites**: [List required conditions or knowledge needed before starting]

<!-- INSTRUCTION: 
- Purpose should be 1-2 sentences describing what gets accomplished
- When to use should list 2-3 specific trigger scenarios
- Prerequisites should include environment setup, dependencies, and prior knowledge
-->

### Your Role

<!-- INSTRUCTION: Define the management persona that orchestrates without executing -->

You are a **[Management Title]** who orchestrates the workflow like a [metaphor, e.g., orchestra conductor, CEO, project director]. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break complex work into parallel tasks if necessary (e.g. > 10 resources) and assign to the right specialist subagents
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously when dependencies allow
- **Quality Oversight**: Review work objectively without being involved in execution details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and verification results

<!-- INSTRUCTION: 
- Choose a management role (e.g., 'Workflow Orchestrator', 'Team Leader', 'Project Director')
- Use CEO/conductor/director metaphors to emphasize orchestration over execution
- List 3-5 management principles focused on delegation and coordination
- Emphasize that management NEVER executes, only orchestrates
-->

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

<!-- INSTRUCTION: Define what this workflow needs as input and what it produces as output -->

#### Required Inputs

<!-- INSTRUCTION: List all mandatory (could be none) inputs the workflow needs to function -->

- **[Input Name 1]**: [Description of what this input is and where it comes from]
- **[Input Name 2]**: [Description and validation requirements]
- **[Input Name 3]**: [Description, source, and any constraints]

<!-- EXAMPLE:
- **Repository URL**: GitHub repository URL to be analyzed
- **Standards List**: Array of standard file paths to apply
-->

#### Optional Inputs

<!-- INSTRUCTION: List inputs that enhance the workflow but aren't required -->

- **[Optional Input 1]**: [Description and default value if not provided]
- **[Optional Input 2]**: [Description and when it's useful]

<!-- EXAMPLE:
- **Target Branch**: Branch name to review (default: main)
-->

#### Expected Outputs

<!-- INSTRUCTION: Define all deliverables this workflow produces -->

- **[Output Name 1]**: [Description of what gets produced and its purpose]
- **[Output Name 2]**: [Description and how it can be used downstream]
- **[Output Name 3]**: [Description and success criteria]

<!-- EXAMPLE:
- **Review Report**: Comprehensive review document with findings and recommendations
- **Modified Files List**: Array of file paths that were updated
- **Compliance Status**: Pass/fail status for each standard applied
- **Action Items**: List of required follow-up tasks
-->

#### Data Flow Summary

<!-- INSTRUCTION: Brief description of how inputs transform into outputs through the workflow -->

[Describe in 2-3 sentences how the workflow takes the inputs and produces the outputs, highlighting key transformations or decision points]

### Visual Overview

#### Main Workflow Flow

<!-- INSTRUCTION: Create an ASCII diagram showing the complete workflow with all main steps, decision points, and potential branches. Include START and END nodes. -->

```plaintext
<!-- EXAMPLE: Your workflow can have any number of steps (1 to N) -->

  YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: ...] ───────────→ (Subagents: execute the unconnected tasks in batches)
   |               ├─ Subagent A: Batch 1                                   ─┐
   |               ├─ Subagent A: Batch 2 (only for > 10 resources)         ─┼─→ [Decision: What's next?]
   |               └─ Subagent A: Batch N (another set of max 10 resources) ─┘
   v
[Step 2: ...] ───────────→ (Subagents: execute more tasks) → [Decision: What's next?]
   |
   v
[Step 3: ...] ───────────→ (Complex: invoke sub-workflow)
   |
   v
   ⋮  
   ⋮  (More steps as needed)
   ⋮
   v
[Step N: ...] ───────────→ (Back to main workflow) → [Decision: What's next?]
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
• Workflow is LINEAR: Step 1 → 2 → 3 → ... → N
```

## 3. WORKFLOW IMPLEMENTATION

<!-- INSTRUCTION: 
This section is a TEMPLATE. Copy and modify the steps below for your specific workflow.
- List all main workflow steps first
- Define relevant standards to assign to subagents (can be none)
- Then detail each step using the provided template
- Each step internally follows the 5-phase execution pattern
- Add as many steps as needed

IMPORTANT TODO TRACKING:
- You MUST use TodoWrite/TodoRead throughout workflow
- At Step level: Track overall workflow progress (Step 1, Step 2, etc.)
- At Phase level: Track batch execution within each step
- TodoWrite when: Creating tasks, updating statuses, adding retries
- TodoRead when: Checking progress, reviewing statuses
-->

### Workflow Steps

<!-- INSTRUCTION: Replace with your actual workflow steps -->

1. [Step 1 Name: e.g., 'Gather Resource List']
2. [Step 2 Name: e.g., 'Tranform Resources']
...
N. [Step N Name: Add more as needed]

<!-- INSTRUCTION: 
- Each step listed above will be detailed below using the step template
- Steps can invoke sub-workflows by expanding to substeps (3.1, 3.2, etc.)
- Identify parallelization opportunities for batch processing or large number of standards to follow
-->

### Step N: [Step Name]

<!-- INSTRUCTION: Copy this entire step template for each step in your workflow -->

**Step Configuration**:

- **Purpose**: [What this step accomplishes]
- **Input**: [Maps to workflow inputs or receives from Step X: specific field names and data structure]
- **Output**: [Produces for workflow outputs or provides to Step Y: specific field names and structure]
- **Sub-workflow**: [path/to/sub-workflow.md or leave empty if none]
- **Parallel Execution**: [Yes/No - can this task spin up subtasks running in parallel]

<!-- INSTRUCTION: 
- You should use TodoWrite at step start to track workflow progress
- Check if Sub-workflow path exists and follow appropriate path below
-->

<!-- if sub-workflow is given -->

#### Execute [...] Workflow (You)

When you reaches this step and sees sub-workflow path:

1. Use Read tool to load the sub-workflow file
2. Parse the sub-workflow to identify its steps
3. Dynamically expand step to N.1, N.2, N.3... from the sub-workflow content
4. Use todo to track the status of each step
5. Executes each step as instructed in the sub-workflow
6. After all sub-workflow steps are complete, continue to the next step

<!-- /if sub-workflow is given -->

<!-- if no sub-workflow is given -->

#### Phase N: Planning (You)

<!-- INSTRUCTION: you plans the work -->

**What You Do**:

1. **Receive inputs** from previous step or external sources
2. **List all related resources** using ls/find commands (do NOT read file contents) if not clear from the input
3. **Determine the standards** to send to subagents to follow
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on resources found
   - Limit each batch to max 10 resources
   - Assign one single subagent to perform all the tasks
5. **Use TodoWrite** to create task list from all batches (each batch = one todo item with status 'pending')
6. **Prepare task assignments** and instructions to be given to subagents
7. **Queue all batches** for parallel execution by subagents

**OUTPUT from Planning**: Task batch assignments as todos

#### Phase 2: Execution (Subagents)

<!-- INSTRUCTION: 
You sends this exact message template to subagents.
- Choose execution expert (e.g., 'Senior Engineer', 'Backend Architect')
- List 3-5 technical principles for execution excellence
- Dispatch up to [X] subagents in parallel (typically 5-10)
- Decide a list of relevant standards to follow (can be none)
-->

**What You Send to Subagents**:

In a single message, you spin up subagents to perform subtasks in parallel, up to **[X]** subtasks at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

<!-- INSTRUCTION: 
- Omit the `Read the following assigned standards` section below if no standard is required
-->

    >>>
    **In ultrathink mode, adopt the [Expert Title] mindset**

    - You're a **[Expert Title]** with deep expertise in [domain] who follows these technical principles:
      - **[Technical Principle 1]**: [Execution excellence focus]
      - **[Technical Principle 2]**: [Quality standards focus]
      - **[Technical Principle 3]**: [Domain-specific principle]

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - [path/to/standard-1.md]
    - [path/to/standard-2.md]
    - ...

    **Assignment**
    You're assigned with the following resources:

    - [resource 1]
    - [resource 2]
    - ...

    **Steps**

    1. [Specific action 1 - e.g., 'Read each resource file to understand current implementation']
    2. [Specific action 2 - e.g., 'Apply security standards to identify vulnerabilities']
    3. ...

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - [information 1 - e.g., 'List of modified resources']
    - [information 2 - e.g., 'Security issues found and fixed']
    - ...

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of what was accomplished'
    modifications: ['resource 2', ...] # resources that have been modified
    outputs:
      [field1]: ...
      [field2]: ...
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Verification (Subagents)

<!-- INSTRUCTION: 
- Omit this phase completely if the output of step 2 are deterministic (e.g. looking for id or compution result)
- Choose verification expert (e.g., 'Quality Assurance Lead', 'Security Auditor')
- Dispatch verification after critical changes or when execution reports show issues
- Usually 1-3 verification subagents running in parallel
-->

In a single message, you spin up verification subagents to check quality, up to **[Y]** verification tasks at a time.

- **[IMPORTANT]** Verification is read-only - subagents must NOT modify any resources
- **[IMPORTANT]** You MUST ask verification subagents to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to track verification tasks separately from execution tasks

Request each verification subagent to perform the following verification with full scrutiny:

<!-- INSTRUCTION: 
- Omit the `Read the following assigned standards` section below if no standard is required
-->

    >>>
    **In ultrathink mode, adopt the [Verification Expert Title] mindset**

    - You're a **[Verification Expert Title]** with expertise in [verification domain] who follows these principles:
      - **[Verification Principle 1]**: [Quality assurance focus]
      - **[Verification Principle 2]**: [Standards compliance focus]
      - **[Verification Principle 3]**: [Risk assessment focus]

    **Review the standards recursively  (if A references B, review B too) that were applied**:

    - [path/to/standard-1.md] - Verify compliance with this standard and its referenced standard
    - [path/to/standard-2.md] - Check all requirements are met
    - ...

    **Verification Assignment**
    You're assigned to verify the following resources that were modified:

    - [resource 1]:
      - [Summary of what was done in phase 2 on resource 1]
    - [resource 2]:
      - [Summary of what was done in phase 2 on resource 2]
    - ...

    **Verification Steps**

    1. [Verification action 1 - e.g., 'Read modified resources to understand changes']
    2. [Verification action 2 - e.g., 'Check compliance with each assigned standard']
    3. ...

    **Report**
    **[IMPORTANT]** You're requested to verify and report:

    - [Verification item 1 - e.g., 'Security compliance status']
    - [Verification item 2 - e.g., 'Functional correctness']
    - ...

    **[IMPORTANT]** You MUST return the following verification report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief verification summary'
    checks:
      [criterion1]: pass|fail
      [criterion2]: pass|fail
      ...
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

<!-- INSTRUCTION: You decide next action -->

**What You Do**:

1. **Analyze all reports** (execution + verification if performed)
2. **Apply decision criteria**:
   - Review any critical failures
   - Consider verification recommendations
3. **Select next action**:
   - **PROCEED**: All success or acceptable partial success → Move to next step
   - **RETRY**: Partial success with retriable failures → Create new batches for failed items
   - **ROLLBACK**: Critical failures or verification failed → Revert changes and go to previous step
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' items as 'completed'
   - If RETRY: Add new todo items for retry batches
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare transition**:
   - If PROCEED: Package outputs for next step
   - If RETRY: Generate retry batches with same standards
   - If ROLLBACK: Identify rollback actions needed

<!-- /if no sub-workflow is given -->

### Step N + 1: [Step Name]

<!-- INSTRUCTION: Continue adding steps as needed, each following the Step N template -->