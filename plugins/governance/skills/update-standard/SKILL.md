---
name: update-standard
description: Update standard(s) to latest template and apply specified changes. Use when bulk updating standards, aligning with template changes, or applying consistent modifications across the standards library.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [standard specifier] [--changes=...]
---

# Update Standard

Update standard directories to align with the latest three-tier standard templates and apply specified changes using intelligent delegation to subagents. Each standard is a directory containing `meta.md`, `scan.md`, `write.md`, and a `rules/` subdirectory. Handles both single standard updates and bulk updates of all standards in parallel.

## Purpose & Scope

**What this skill does NOT do**:

- Create new standards (use create-standard)
- Modify non-standard files
- Update templates themselves
- Override constitutional requirements

**When to REJECT**:

- Invalid standard directory paths
- Malformed change specifications
- Attempting to violate constitutional standards
- Template files (template:standard-meta, template:standard-scan, template:standard-write) are missing or corrupted

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.

- **If present**: Use **Team Mode** (Step 2A)
- **If absent**: Use **Subagent Mode** (Step 2B)

### Step 2A: Team Mode (Agent Teams enabled)

Lead Orchestrator coordinates updater (opus) and reviewer (haiku) teammates with batched update-review cycles and context-level pool management. For the full Phase 1–4 procedure (Lead rules, planning, team setup, update-review cycle, aggregation/cleanup) and the agent summary table, see `references/team-mode.md`.

### Step 2B: Subagent Mode (fallback)

Spawn parallel specialized subagents (max 3 standard directories per batch) — each ultrathinks, reads three tier templates + standard tier files, and applies changes. For full procedure (template validation, delegation, the verbatim subagent prompt with `>>> <<<` block, report YAML, and progress monitoring), see `references/subagent-mode.md`.

### Step 3: Reporting

**Output Format** (same for both modes):

```plaintext
[✅/❌] Command: $ARGUMENTS

## Summary
- Standards updated: [count]
- Changes applied: [change specifications]
- Template alignment: [COMPLETE/PARTIAL/FAILED]
- Execution mode: [team/subagent]

## Actions Taken
1. [Standard directory] (meta.md, scan.md, write.md): [Status] - [Changes applied]
2. [Standard directory] (meta.md, scan.md, write.md): [Status] - [Changes applied]

## Subagent Results (subagent mode) / Agent Lifecycle (team mode)
- Total agents deployed: [count]
- Successful updates: [count]
- Failed updates: [count] (if any)
- Agents reused (team mode only): [count]
- Agents retired (team mode only, context >= 50%): [count]

## Review Cycles (team mode only)
- Batch 1: [N] review rounds until both reviewers approved
- Batch 2: [N] review rounds until both reviewers approved
- ...

## Template Alignment Applied
- Structure updates: [list]
- Section additions: [list]
- Format corrections: [list]

## Changes Applied
- --change1: [Status and details]
- --change2: [Status and details]

## Issues Found (if any)
- **Issue**: [Description]
  **Resolution**: [Applied fix or escalation]

## Next Steps (if applicable)
- Review updated standards for accuracy
- Test standard execution with sample scenarios
- Commit changes if satisfied with results
```

## Examples

### Single Standard Update

```bash
/update-standard "typescript" --change1="Add OAuth 2.1 requirements" --change2="Update encryption standards"
# Updates typescript/ directory: meta.md, scan.md, write.md
# Compares meta.md vs template:standard-meta, scan.md vs template:standard-scan, write.md vs template:standard-write
# Agent applies changes to the appropriate tier file as separate tasks (2a, 2b)
# Ultrathink review for integrity and consistency across all three tiers
```

### Bulk Standard Updates (Team Mode)

```bash
/update-standard --change1="Update TypeScript to 5.0 requirements"
# With CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1:
#   Discovers all standard directories (those containing meta.md), creates update-standard-team:
#   - updater-1 (opus): Handles batch 1 (2 standard directories, 6 tier files)
#   - updater-2 (opus): Handles batch 2 (2 standard directories, 6 tier files, parallel)
#   Each updater reads all three tier templates and standard tier files, applies changes
#   Agents report context_level after completion:
#     - context < 50%: agent reused for next batch
#     - context >= 50%: agent retired, fresh replacement spawned
#   Team is cleaned up after all batches complete
```

### Bulk Standard Updates (Subagent Fallback)

```bash
/update-standard --change1="Update TypeScript to 5.0 requirements"
# Without agent teams enabled:
#   Updates ALL standard directories in parallel via subagents
#   Each subagent handles one standard directory (meta.md, scan.md, write.md)
#   Consistent change applied across entire standard library
```

### Template-Only Alignment

```bash
/update-standard "typescript"
# Aligns typescript/ directory with latest three-tier templates
# Checks meta.md vs template:standard-meta, scan.md vs template:standard-scan, write.md vs template:standard-write
# No additional changes, just structure updates
# Preserves all existing content and requirements
```

### Multiple Complex Changes

```bash
/update-standard "react-components" --change1="Add React 18 concurrent features" --change2="Update testing requirements for RTL" --change3="Add accessibility compliance"
# Each change applied to the appropriate tier file (2a, 2b, 2c)
# Agent ensures changes don't conflict across meta.md, scan.md, write.md
# Ultrathink mode verifies comprehensive integration
```

### Error Case Handling

```bash
/update-standard "nonexistent-standard"
# Error: Standard directory not found (no meta.md in the directory)
# Suggestion: Use Glob to find directories with meta.md under [plugin]/constitution/standards/
# Alternative: Check if directory was moved or renamed
```

### Bulk Update with Specific Changes

```bash
/update-standard --change1="Update Node.js to version 20" --change2="Add ESM import requirements"
# Spawns agents for all standard directories
# Only applies changes where relevant (backend, code standards)
# Skips changes for standard directories where not applicable
```
