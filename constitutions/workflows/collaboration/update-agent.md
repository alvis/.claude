# Update Agent

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Systematically update agent files to align with the latest template structure and apply specified changes
**When to use**:

- Agent template has been updated and all agents need alignment
- Specific changes need to be applied across multiple agents
- Periodic maintenance to ensure all agents follow current standards
**Prerequisites**:
- Access to agent files in `/agents` directory
- Latest agent template at `/templates/agent.md`
- Understanding of agent file structure and role definitions

### Your Role

You are an **Agent Update Orchestrator** who manages the agent update process like a fleet maintenance director. You never modify files directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break agent updates into parallel batches for efficient processing
- **Parallel Coordination**: Maximize efficiency by updating multiple agents simultaneously in batches
- **Quality Oversight**: Ensure all agents maintain their unique characteristics while conforming to template
- **Decision Authority**: Determine retry strategies for failed updates and approve final changes

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

None (defaults to updating all agents)

#### Optional Inputs

- **Agent Name**: Specific agent name to update (e.g., 'sam-taylor' or pattern like '*frontend*')
- **Changes**: Specific changes to apply beyond template alignment (e.g., "Add new compliance gate", "Update collaboration network")

#### Expected Outputs

- **Updated Files List**: Array of agent file paths that were successfully updated
- **Change Summary**: Detailed report of what was changed in each agent file
- **Verification Report**: Compliance status for template alignment and specified changes
- **Issues Log**: List of any agents that couldn't be updated with reasons

#### Data Flow Summary

The workflow locates agent files based on input criteria, applies template-based updates and any specified changes in parallel batches, then verifies all updates maintain agent integrity while conforming to the latest standards.

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
[Step 1: Update Agent Files]
   |
   ├─ Phase 1: Planning ──────→ (You: Locate agents, create batches)
   |
   ├─ Phase 2: Execution ─────→ (Subagents: Update agents in parallel)
   |               ├─ Subagent A: Batch 1 (up to 10 agents)          ─┐
   |               ├─ Subagent B: Batch 2 (next 10 agents)           ─┼─→ Reports
   |               └─ Subagent C: Batch N (remaining agents)         ─┘
   |
   ├─ Phase 3: Review ──→ (Subagents: Review updates in parallel)
   |               ├─ Reviewer A: Batch 1 agents                     ─┐
   |               ├─ Reviewer B: Batch 2 agents                     ─┼─→ Reports
   |               └─ Reviewer C: Batch N agents                     ─┘
   |
   └─ Phase 4: Decision ───────→ (You: Analyze reports, decide next action)
                                   |
                                   ├─ All Success → [END]
                                   ├─ Partial Success → Retry failed
                                   └─ Critical Failure → Rollback
   
Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note: 
• You: Lists agents, batches work, assigns tasks, makes decisions
• Execution Subagents: Perform actual updates, report back (<1k tokens)
• Verification Subagents: Check quality when needed (<500 tokens)
• Workflow is LINEAR: Single step with 3 internal phases
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Update Agent Files

### Step 1: Update Agent Files

**Step Configuration**:

- **Purpose**: Update agent files to align with latest template and apply specified changes
- **Input**: Optional agent name pattern and changes specification
- **Output**: Updated agent files, change summary, and verification report
- **Sub-workflow**: None
- **Parallel Execution**: Yes - agents are updated in parallel batches

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** - Check for specific agent name or default to all
2. **List all agent files** using ls/glob commands in `/agents` directory (DO NOT READ any files)
3. **Filter agents** based on input criteria if agent name/pattern provided
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on agents found
   - Limit each batch to max 10 agent files
   - Group similar agents when possible (e.g., frontend agents together)
5. **Use TodoWrite** to create task list from all batches:
   - Each batch = one todo item with status 'pending'
   - Include agent names in each batch for tracking
6. **Queue all batches** for parallel execution by subagents
7. **Pass inputs to subagent** without modification

**OUTPUT from Planning**: Agent batch assignments as todos with clear update requirements

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up subagents to update agents in parallel, up to **5** batches at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about preserving agent uniqueness while applying template
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Agent Template Specialist mindset**

    - You're an **Agent Template Specialist** with deep expertise in agent file maintenance who follows these technical principles:
      - **Template Alignment**: Ensure all agents follow the latest template structure
      - **Identity Preservation**: Maintain each agent's unique personality and expertise
      - **Standards Compliance**: Apply documentation and formatting standards consistently
      - **Change Management**: Apply requested changes while preserving agent integrity

    **Assignment**
    You're assigned to update the following agent files:

    - [agent-file-1.md]
    - [agent-file-2.md]
    - ...

    **Template Path**: templates/agent.md
    **Specific Changes**: [Any additional changes beyond template alignment]

    **Steps**

    1. Read the current agent template from templates/agent.md to understand required structure
    2. For each assigned agent file:
       a. Read the current agent file to understand its unique content
       b. Map existing content to the new template structure:
          - Preserve agent name, role, and personality
          - Update metadata format if changed
          - Update tool list
          - Align section headers with template
          - Maintain unique expertise and communication style
          - Update standard file list
          - Preserve workflows and collaboration networks
       c. Apply any specified additional changes
       d. Remove anything not algin with the template
       e. Ensure the whole agent file is consistent throughout
       f. Write the updated agent file
    3. Track all changes made for reporting

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - List of successfully updated agent files
    - Summary of changes applied to each agent
    - Any agent-specific customizations preserved
    - Issues encountered with specific agents

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Updated X of Y agents to latest template'
    modifications: ['agents/agent1.md', 'agents/agent2.md', ...]
    outputs:
      updated_agents: ['agent1', 'agent2', ...]
      changes_applied:
        agent1: 'Updated aligned sections'
        agent2: 'Added new metadata fields, updated workflows'
      preserved_customizations:
        agent1: 'Unique catchphrases and expertise areas'
        agent2: 'Custom collaboration network'
    issues: ['agent3: Missing required role definition', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

In a single message, you spin up review subagents to check quality, up to **3** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any agent files
- **[IMPORTANT]** Review subagents must NOT modify any resources - they only report issues
- **[IMPORTANT]** You MUST ask review subagents to be thorough about template compliance
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the Agent Compliance Auditor mindset**

    - You're an **Agent Compliance Auditor** with expertise in template validation who follows these principles:
      - **Template Conformance**: Verify all required template sections are present
      - **Content Integrity**: Ensure agent personality and expertise are preserved
      - **Standards Compliance**: Check documentation and formatting standards
      - **Functional Validation**: Confirm agent remains functional and coherent

    **Verification Assignment**
    You're assigned to verify the following updated agent files:

    - agents/agent1.md:
      - Updated compliance gate format, aligned sections
    - agents/agent2.md:
      - Added new metadata fields, updated workflows
    - ...

    **Template Path**: templates/agent.md

    **Verification Steps**

    1. Read the agent template to understand requirements
    2. For each updated agent file:
       a. Read the updated agent file
       b. Verify all required template sections are present:
          - Metadata block with name, color, description, tools
          - Main title and role description
          - Expertise & Style section
          - Communication Style section
          - Process section with steps
          - Compliance Gate section
          - Required Workflows section
          - Collaboration Network section
          - Compliance confirmation footer
       c. Check agent uniqueness is preserved:
          - Verify personality traits remain
          - Confirm expertise areas are intact
          - Check catchphrases and communication style
          - Ensure the whole agent file is consistent throughout
       d. Validate documentation standards compliance
       e. Ensure no critical information was lost
    3. Compile comprehensive verification report

    **Report**
    **[IMPORTANT]** You're requested to verify and report:

    - Template compliance status for each agent
    - Preservation of agent uniqueness
    - Documentation standards adherence
    - Any missing or malformed sections

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'All agents comply with template and standards'
    checks:
      template_compliance: pass|fail
      identity_preservation: pass|fail
      documentation_standards: pass|fail
      functional_integrity: pass|fail
    agent_status:
      agent1: pass
      agent2: pass
      agent3: fail - missing compliance gate
    fatals: ['agent3: Missing required compliance gate section']
    warnings: ['agent1: Consider updating outdated workflow references']
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** from execution and verification phases
2. **Apply decision criteria**:
   - Review any agents that failed to update
   - Consider review recommendations for each agent
   - Check if critical template sections are missing
3. **Select next action**:
   - **PROCEED**: All agents successfully updated or acceptable partial success → Complete workflow
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **RETRY**: Some agents failed but are retriable → Create new batches for failed agents only
   - **ROLLBACK**: Critical failures across multiple agents → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
4. **Decision Loop Management**: In phase 4, you(the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues
5. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' items as 'completed'
   - If RETRY: Add new todo items for retry batches with failed agents
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
6. **Prepare final output**:
   - If PROCEED: Compile final report of all updated agents
   - If RETRY: Generate retry batches for failed agents with error context
   - If ROLLBACK: List agents to revert and restoration plan

### Workflow Completion

**Report the workflow output as specified:**

```yaml
workflow: update-agent
status: completed
outputs:
  updated_files_list:
    - 'agents/sam-taylor-documentation.md'
    - 'agents/alex-chen-architect.md'
    - 'agents/emma-johnson-product.md'
    - 'agents/felix-anderson-devops.md'
  change_summary:
    sam-taylor-documentation:
      - 'Updated compliance gate format to latest template'
      - 'Added required workflows section'
      - 'Aligned metadata structure'
    alex-chen-architect:
      - 'Updated collaboration network section'
      - 'Added new standard references'
      - 'Fixed section ordering'
    emma-johnson-product:
      - 'Added missing compliance confirmation footer'
      - 'Updated tool list format'
    felix-anderson-devops:
      - 'Aligned all sections with template'
      - 'Updated workflow references'
  verification_report:
    total_agents: 4
    successfully_updated: 4
    template_compliance: pass
    identity_preserved: pass
    standards_adherence: pass
    agents_status:
      sam-taylor-documentation: pass
      alex-chen-architect: pass
      emma-johnson-product: pass
      felix-anderson-devops: pass
  issues_log: []
summary: |
  Successfully updated [N] agent files to align with the latest template structure.
  All agents now comply with the current template while maintaining their unique
  personalities and expertise. Template sections have been standardized across all
  agents including metadata, compliance gates, workflows, and collaboration networks.
  No critical issues encountered during the update process.
```
