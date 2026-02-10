---
name: update-agent
description: Update agent files to align with template and apply specified changes. Use when modernizing agent definitions, batch updating agent configurations, or ensuring template compliance across agents.
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Write, MultiEdit, Edit, Bash, Grep, Glob, TodoWrite, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [agent specifier] [--changes=...]
---

# Update Agent

Updates agent files to align with the latest template structure and applies any specified changes while preserving unique agent characteristics.

## Purpose & Scope

This skill systematically updates agent files to maintain consistency with the current template while preserving each agent's unique personality, expertise, and collaboration networks.

**What this skill does NOT do**:

- Create new agent files (use `/create-agent` instead)
- Delete or remove agent files
- Modify agent core personality or expertise areas
- Change agent role assignments without explicit instruction

**When to REJECT**:

- No agents exist in the `/agents` directory
- Template file `template:agent` is missing or invalid
- Request to modify protected agent characteristics without justification
- Agent files are locked or in active use by running processes

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.

- **If present**: Use **Team Mode** (Step 2A)
- **If absent**: Use **Subagent Mode** (Step 2B)

### Step 2A: Team Mode (Agent Teams enabled)

#### Phase 1: Planning & Discovery (Lead)

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract:
     - Agent specifier (all, specific agent name, or pattern like `*frontend*`)
     - Change specifications (--changes parameter)
   - Validate agent files exist if specific agent specified
   - Count total agents if updating all

2. **Load Template Reference**
   - Read template:agent for latest agent structure
   - Identify template sections and required elements
   - Note any template updates since last agent refresh

3. **Locate Agents**
   - Discover all relevant agent files using Glob
   - Filter by specifier pattern if provided
   - Build list of agents to update

#### Phase 2: Team Setup & Execution

1. **Create Team**
   - Use TeamCreate with name `update-agent-team`
   - Initialize agent pool registry to track active agents

2. **Template Validation**
   - Verify template:agent exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

3. **Spawn Agent Update Specialists**
   - Spawn specialized teammates (one per agent file) via Task tool with:
     - `team_name: "update-agent-team"`
     - `name: "updater-{N}"` (sequential naming)
     - `model: "opus"`
     - `agent_type: "general-purpose"`

4. **Create and Assign Tasks**
   - TaskCreate per agent file with full instructions including:
     - Agent file path
     - Template reference path (template:agent)
     - All change specifications from arguments
     - Detailed instructions for applying updates
   - TaskUpdate to set owner per teammate

#### Phase 3: Work Cycle

1. **Agent Update Task Specification**

   Each Agent Update Specialist receives:

   >>>
   **ultrathink: adopt the Agent Update Specialist mindset**

   - You're an **Agent Update Specialist** with deep expertise in agent configuration who follows these principles:
     - **Template-First Approach**: Always compare against template before modification
     - **Personality Preservation**: Maintain unique agent characteristics and voice
     - **Structural Integrity**: Align with template structure while preserving customizations
     - **Professional Polish**: Deliver clean, consistent agent definitions

   <IMPORTANT>
     You've to perform the task yourself. You CANNOT further delegate the work to another subagent
   </IMPORTANT>

   **Assignment**
   You're assigned to update agent: [agent name]

   **Agent Specifications**:
   - **Agent File**: [agent file path]
   - **Template**: template:agent
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Agent**:
      - Read the agent file completely
      - Identify unique personality traits, expertise, and collaboration networks
      - Note any custom sections or configurations

   2. **Compare with Template**:
      - Read template:agent for current structure
      - Identify missing sections from template
      - Identify sections that need structural updates
      - Map changes to specific template sections

   3. **Apply Updates**:
      - Add any missing required sections from template
      - Update section formatting to match template
      - Apply specified changes from --changes parameter
      - Preserve all unique agent characteristics
      - Maintain collaboration networks and tool permissions

   4. **Clean & Finalize**:
      - Remove any outdated or deprecated sections
      - Ensure consistent formatting throughout
      - Verify agent definition is complete and valid

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens) via SendMessage to team-lead:

   ```yaml
   status: success|failure|partial
   agent: '[agent-name]'
   summary: 'Brief description of changes applied'
   modifications:
     - section: '[section name]'
       change: '[what was changed]'
   template_compliance: true|false
   personality_preserved: true|false
   context_level: '[calculated %]'  # (input_tokens / context_window_size) from real usage data
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```

   <<<

2. **Progress Monitoring**
   - Track completion status of each delegated agent file
   - Handle any teammate failures or escalations
   - Ensure constitutional compliance in all updates

#### Phase 4: Aggregation & Cleanup

1. **Collect Results**
   - Use TaskGet to retrieve completion reports from all tasks
   - Aggregate results into final summary

2. **Shutdown Teammates**
   - Send shutdown requests to all teammates via SendMessage
   - Wait for shutdown acknowledgments

3. **Delete Team**
   - Use TeamDelete to clean up team resources
   - Proceed to Reporting

#### Agent Summary

| Agent Type | Model | Role | Lifecycle |
|------------|-------|------|-----------|
| Agent Update Specialist | opus | Updates agent files with template alignment and changes | One per agent file; spawned for Phase 3, retired in Phase 4 |

### Step 2B: Subagent Mode (fallback)

When Agent Teams are not available, execute the existing workflow:

### Planning & Discovery

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract:
     - Agent specifier (all, specific agent name, or pattern like `*frontend*`)
     - Change specifications (--changes parameter)
   - Validate agent files exist if specific agent specified
   - Count total agents if updating all

2. **Load Template Reference**
   - Read template:agent for latest agent structure
   - Identify template sections and required elements
   - Note any template updates since last agent refresh

3. **Locate Agents**
   - Discover all relevant agent files using Glob
   - Filter by specifier pattern if provided
   - Build list of agents to update

### Execution with Parallel Subagents

1. **Template Validation**
   - Verify template:agent exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

2. **Delegation**
   - Create parallel specialized subagents (one per agent file) with:
     - Agent file path
     - All change specifications
     - Detailed instructions
     - Request to ultrathink

3. **Progress Monitoring**
   - Track completion status of each delegated agent
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates

### Verification

1. **Template Compliance Verification**
   - Verify each updated agent follows template:agent structure
   - Check all mandatory sections are present and properly formatted
   - Validate frontmatter and metadata consistency

2. **Change Application Verification**
   - Confirm all specified changes were applied correctly
   - Verify changes are reflected throughout the agent file
   - Check for any conflicting or contradictory specifications

3. **Personality Preservation Check**
   - Ensure unique agent characteristics remain intact
   - Verify collaboration networks are preserved
   - Confirm expertise areas unchanged (unless explicitly modified)

### Reporting

**Output Format**:

```
[✅/❌] Command: update-agent $ARGUMENTS

## Summary
- Execution mode: [team/subagent]
- Agents processed: [count/total]
- Successfully updated: [count]
- Failed updates: [count]
- Template compliance: [PASS/FAIL]

## Actions Taken
1. [Batch processing of agents with results]
2. [Template alignment changes applied]
3. [Custom changes applied (if any)]

## Workflows Applied (subagent mode)
- Update Agent Workflow: [Status]

## Teammate Results (team mode only)
- Total agents deployed: [count]
- Successful updates: [count]
- Failed updates: [count] (if any)

## Updated Agents
- [agent-name]: [Status] - [Changes applied]
- [agent-name]: [Status] - [Changes applied]

## Issues Found (if any)
- **Agent**: [agent-name]
  **Issue**: [Description of problem]
  **Resolution**: [Applied fix or manual intervention needed]
```

## Examples

### Update All Agents (Team Mode)

```bash
/update-agent
# With CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1:
# - Creates update-agent-team
# - Spawns parallel Agent Update Specialists (one per agent file)
# - Each specialist updates agent with template alignment
# - Preserves unique characteristics while ensuring template compliance
# - Reports execution mode: team
```

### Update All Agents (Subagent Mode)

```bash
/update-agent
# Without agent teams:
# - Uses traditional subagent delegation
# - Updates all agents in /agents directory to latest template
# - Reports execution mode: subagent
```

### Update Specific Agent

```bash
/update-agent "priya-sharma"
# Updates only the priya-sharma agent file
# Aligns with template while preserving role-specific content
```

### Update with Pattern Matching

```bash
/update-agent "*frontend*"
# Updates all agents with 'frontend' in their filename
# Useful for updating agents with similar roles or expertise
```

### Update with Custom Changes

```bash
/update-agent --change="Add new security compliance gate"
# Updates all agents and applies additional changes
# Template alignment plus specified modifications
```

### Update Specific Agent with Changes

```bash
/update-agent "james-mitchell" --change="Update collaboration network to include new DevOps role"
# Updates specific agent with both template alignment and custom changes
# Preserves agent identity while making requested modifications
```

### Batch Update by Category

```bash
/update-agent "*-engineer*" --change="Update tool permissions for new security standards"
# Updates all engineer-type agents with security updates
# Efficient for role-based mass updates
```

### Error Case Handling

```bash
/update-agent "non-existent-agent"
# Error: Agent file not found
# Suggestion: Use 'ls agents/' to see available agents
# Alternative: Use '/update-agent' to update all agents
```

### Template Validation

```bash
/update-agent --verify
# Validates all agents against current template without making changes
# Reports compliance status and suggests improvements
```
