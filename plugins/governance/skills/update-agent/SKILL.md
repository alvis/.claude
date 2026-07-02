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

Updates agent files to align with the latest template structure and applies any specified changes while preserving unique agent characteristics. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. That standard is precisely how an agent's voice is preserved across updates: revised expertise, collaboration links, and template sections must be woven into the agent's existing prose so the file still reads as one continuous personality — never as the original agent with a "Recent updates" or "Additional capabilities" section bolted beneath it.

## Purpose & Scope

This skill systematically updates agent files to maintain consistency with the current template while preserving each agent's unique personality, expertise, collaboration networks, and base-context (`SD-`/`RP-`) assignments — the standards each agent preloads and the repo-derived context it resolves lazily, per `constitution/references/context-catalog.md`.

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
   - Read template:agent for latest agent structure — the frontmatter key surface (`name`, `description`, `color`,
     `model`, `effort`, `permissionMode`, `tools`, `disallowedTools`, `skills`, `mcpServers`, `hooks`, `memory`,
     `background`, `isolation`, `maxTurns`, `initialPrompt`) plus the base.md body sections (Base Context,
     Coordination Posture, Collaboration)
   - Before applying any frontmatter change, re-check the live Claude Code docs for the current valid frontmatter
     key surface — template:agent mirrors it at time of writing, but the live docs win on conflict; log any
     conflict found rather than silently trusting the template
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
   - Each delegated subagent picks `model`/`effort`/`permissionMode`/`memory`/`isolation` by running this
     checklist, not by copying whatever the file already had:
     - **model**: match to cognitive demand (haiku for deterministic/mechanical roles, sonnet for branching
       investigation, opus for judgment-heavy production, fable for adversarial/deep-reasoning review) — never
       default every role to the largest model
     - **effort**: set only for model families that support it; OMIT the key entirely when `model: haiku` (haiku
       does not support `effort`)
     - **permissionMode**: EXACTLY ONE of `default`/`acceptEdits`/`auto` — never `plan`, `bypassPermissions`, or
       `dontAsk` — chosen by the agent's launch scenario:
       - **main-session** or **spawned-subagent**: `auto` for opus/fable producers running unattended,
         `acceptEdits` for sonnet/haiku producers, `default` for critics (read-mostly, edit-prevention via
         `disallowedTools`/hooks/worktree instead)
       - **workflow-spawned** (dispatched inside a dynamic `Workflow` run): **always `acceptEdits`**, regardless
         of role — a workflow has no interactive fallback
       - **teammate** (member of a formed Agent Team): **inherits the lead's `permissionMode`** — do not set one
         independently on a teammate
     - **memory**: `user`/`project`/`local` only if this agent genuinely self-curates a persistent
       `.claude/agent-memory/<name>/MEMORY.md` across sessions; OMIT the key to disable — there is no
       `memory:none`
     - **isolation**: `worktree` only for agents that must not race the main working copy (adversarial red-team,
       parallel research); otherwise omit
   - Base-context assignment (the `SD-`/`RP-` subset in the agent's Base Context section) is re-verified against
     `constitution/references/context-catalog.md` on every update — an agent's role-scoped `SD-*` list and its
     lazily-resolved `RP-*` aliases are corrected to match the catalog, never left to drift from a prior edit

3. **Progress Monitoring**
   - Track completion status of each delegated agent
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates

#### Verification

1. **Template Compliance Verification**
   - Verify each updated agent follows template:agent structure
   - Check all mandatory sections are present and properly formatted, including Base Context (`SD-`/`RP-`
     assignments matching `constitution/references/context-catalog.md`), Coordination Posture, and Collaboration
   - Validate frontmatter and metadata consistency against the live-doc-checked key surface (only the valid keys
     listed in template:agent — reject any invented key), and confirm `permissionMode` matches the launch
     scenario the agent actually runs under

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
