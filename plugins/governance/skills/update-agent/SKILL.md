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

Lead Orchestrator coordinates Agent Update Specialist teammates (opus) to update agent files in parallel against template:agent. For the full Phase 1–4 procedure (planning, team setup, work cycle with verbatim subagent prompt, aggregation/cleanup) and the agent summary table, see `references/team-mode.md`.

### Step 2B: Subagent Mode (fallback)

Spawn parallel specialized subagents (one per agent file) — each ultrathinks, reads template:agent and the agent file, and applies updates. For full procedure (planning, delegation, progress monitoring, verification of template compliance, change application, and personality preservation), see `references/subagent-mode.md`.

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

## Skills Applied (subagent mode)
- Update Agent Skill: [Status]

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
