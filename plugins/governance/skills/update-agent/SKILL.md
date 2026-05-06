---
name: update-agent
description: Update agent files to align with template and apply specified changes. Use when modernizing agent definitions, batch updating agent configurations, or ensuring template compliance across agents.
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Write, MultiEdit, Edit, Bash, Grep, Glob, TodoWrite
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

### Step 1: Subagent Orchestration

Spawn parallel specialized subagents (one per agent file, max 8 parallel `Task` calls per dispatch) — each ultrathinks, reads `template:agent` and the agent file, and applies updates.

#### Planning & Discovery

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

#### Execution with Parallel Subagents

1. **Template Validation**
   - Verify template:agent exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

2. **Delegation**
   - Create parallel specialized subagents (one per agent file, max 8 parallel `Task` calls per dispatch) with:
     - Agent file path
     - All change specifications
     - Detailed instructions
     - Request to ultrathink

3. **Progress Monitoring**
   - Track completion status of each delegated agent
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates

#### Verification

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

#### Aggregation

- Aggregate per-subagent results into the final Step 2 report

### Step 2: Reporting

**Output Format**:

```
[✅/❌] Command: update-agent $ARGUMENTS

## Summary
- Agents processed: [count/total]
- Successfully updated: [count]
- Failed updates: [count]
- Template compliance: [PASS/FAIL]

## Actions Taken
1. [Batch processing of agents with results]
2. [Template alignment changes applied]
3. [Custom changes applied (if any)]

## Subagent Results
- Total subagents deployed: [count]
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

### Update All Agents

```bash
/update-agent
# Spawns parallel subagents (one per agent file, max 8 parallel Task calls)
# Updates all agents in /agents directory to latest template
```

### Update Specific Agent

```bash
/update-agent "james-mitchell"
# Updates only the james-mitchell agent file
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
