---
allowed-tools: Task, Read, Write, MultiEdit, Edit, Bash, Grep, Glob, TodoWrite

argument-hint: [agent specifier] [--changes=...]

description: update agent files to align them with template and apply specified changes
---

# Update Agent

Updates agent files to align with the latest template structure and applies any specified changes while preserving unique agent characteristics.

## 🎯 Purpose & Scope

This command systematically updates agent files to maintain consistency with the current template while preserving each agent's unique personality, expertise, and collaboration networks.

**What this command does NOT do:**

- Create new agent files (use `/create-agent` instead)
- Delete or remove agent files
- Modify agent core personality or expertise areas
- Change agent role assignments without explicit instruction

**When to REJECT:**

- No agents exist in the `/agents` directory
- Template file `/templates/agent.md` is missing or invalid
- Request to modify protected agent characteristics without justification
- Agent files are locked or in active use by running processes

## 📊 Dynamic Context

- **[IMPORTANT]** At the start of the command, you must run the command to extract all the context below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`
- Modified files: !`git diff --name-only`
- Staged files: !`git diff --cached --name-only`

### Project Context

- Workflows: !`find ~/.claude/constitutions/workflows "$(git rev-parse --show-toplevel)/constitutions/workflows" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`
- Standards: !`find ~/.claude/constitutions/standards "$(git rev-parse --show-toplevel)/constitutions/standards" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`

### Agent Context

- Existing agents: !`find agents/ -name '*.md' -type f 2>/dev/null | sort || echo "No agents found"`
- Agent template: !`ls templates/agent.md 2>/dev/null || echo "Template not found"`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Follow Update Agent Workflow

- Execute @constitutions/workflows/project/update-agent.md

### Step 2: Reporting

**Output Format:**

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

## Workflows Applied
- Update Agent Workflow: [Status]

## Updated Agents
- [agent-name]: [Changes applied]
- [agent-name]: [Changes applied]

## Issues Found (if any)
- **Agent**: [agent-name]
  **Issue**: [Description of problem]
  **Resolution**: [Applied fix or manual intervention needed]
```

## 📝 Examples

### Update All Agents

```bash
/update-agent
# Updates all agents in /agents directory to latest template
# Preserves unique characteristics while ensuring template compliance
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
