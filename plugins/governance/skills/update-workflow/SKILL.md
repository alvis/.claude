---
name: update-workflow
description: Update workflow(s) to latest standard template and make specified changes. Use when bulk updating workflows, ensuring template compliance, or applying consistent modifications across workflow files.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [workflow specifier] [--changes=...]
---

# Update Workflow

Update workflow files to align with the latest standard template and apply specified changes using intelligent delegation to subagents. Handles both single workflow updates and bulk updates of all workflows in parallel.

## Purpose & Scope

**What this skill does NOT do**:

- Create new workflows (use create-workflow)
- Modify non-workflow files
- Update templates themselves
- Override constitutional requirements

**When to REJECT**:

- Invalid workflow file paths
- Malformed change specifications
- Attempting to violate constitutional standards
- Template file is missing or corrupted

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.

- **If present**: Use **Team Mode** (Step 2A)
- **If absent**: Use **Subagent Mode** (Step 2B)

### Step 2A: Team Mode (Agent Teams enabled)

You are the **Lead Orchestrator**. Your role is strictly **orchestration** — you coordinate, delegate, and aggregate. You MUST NOT perform any workflow update work yourself.

**Lead Rules**:

- **DO**: Discover files, create batches, spawn teammates, manage lifecycle, aggregate results
- **DO NOT**: Read workflow files, apply changes, or update workflows yourself
- **NEVER**: Use the `Read` tool on any workflow file (paths containing `constitution/workflows/`). These are for teammates to read, not you.
- **ALWAYS**: Pass the full file paths of workflow and template files to teammates — they read and update the workflows, not you

#### Phase 1: Planning (Lead)

1. **Extract Input**
   - Parse $ARGUMENTS to extract workflow name and change specifications
   - Workflow: First argument (optional - if empty, update all workflows)
   - --change[N]: Extract all change parameters (change1, change2, etc.)
   - Validate workflow file exists if specified
   - Count total workflows if updating all

2. **Discover Template Path**
   - Identify the path to template:workflow (do NOT read it)
   - Pass this path as a string to teammates

3. **Discover Workflows**
   - Locate all workflow files in [plugin]/constitution/workflows/
   - Filter by specifier if provided
   - Build list of workflows to update
   - Create batches (max 2 workflows per batch for context efficiency)

#### Phase 2: Team Setup & Execution (Lead orchestrates)

1. **Create team**: `TeamCreate` with name `update-workflow-team`
2. **Concurrency limits**:
   - Max **4 updaters** active (working) at any time — if all 4 slots are occupied, queue remaining batches until an updater becomes idle or is retired
   - Max **2 reviewers** active (working) at any time — if both slots are occupied, queue review assignments until a reviewer becomes idle or is retired
3. **Initialize agent pool**: Lead maintains a registry tracking each agent's name, role, model, last-reported `context_level`, and status (`working` / `idle` / `retired`)
4. **Spawn or reuse updater teammates**: For each batch:
   - **Check pool** for an idle updater with `context_level` < 50%
   - **If found**: Reuse via `SendMessage` with new batch instructions
   - **If not found**: Spawn a fresh `updater-N` using **opus** model, type `general-purpose`
5. **Create update tasks**: `TaskCreate` per batch with full instructions including:
   - The full absolute paths to the workflow files and template file (as string values — teammates will read these files themselves)
   - All change specifications
   - Detailed update instructions (see Step 2B subagent specification for the instructions)
   - Expected YAML report format
   - **Instruction to report `context_level`** (calculated as `input_tokens / context_window_size × 100`, default context window: 200K tokens) in their completion message
   - **Instruction to WAIT for reviewer feedback** after completing updates — updaters must NOT self-claim new tasks until the lead confirms the batch is complete
   - Instruction that updaters CANNOT further delegate work
6. **Assign tasks**: `TaskUpdate` to set owner per updater

#### Phase 3: Update-Review Cycle (per batch, all batches in parallel)

After each updater completes their update task:

1. **Updater sends completion message** to lead with YAML report and `context_level` (calculated as `input_tokens / context_window_size × 100`). Updater then **waits** — it must NOT self-claim new tasks until the lead confirms the batch outcome.
2. **Lead records updater's `context_level`** but does NOT yet retire or reassign the updater — the updater may be needed for fixes.
3. **Lead assigns 2 reviewers** per completed batch:
   - **Check pool** for idle reviewers with `context_level` < 50% — reuse via `SendMessage`
   - **If not enough idle reviewers**: Spawn fresh `reviewer-N-a` and `reviewer-N-b`
   - All reviewers use **haiku** model, type `general-purpose`
4. **Lead creates review tasks** for each reviewer with these instructions:
   - Subject: "Review workflow update batch N (reviewer A/B)"
   - Description includes: the workflow file list that was updated, the full file paths to template and workflows (reviewers read these themselves), instruction to independently review for template compliance and change application quality, **instruction to report `context_level`** in their response
   - **The updater's name** (e.g., `updater-1`) so the reviewer knows where to send detailed findings
   - Reviewers work independently — they do NOT coordinate with each other
   - **Communication rules**:
     - Send **detailed findings directly to the updater** via `SendMessage` (full issue descriptions, file paths, sections, expected fixes)
     - Send only **pass/fail + `context_level`** to the lead (e.g., `status: approved, context_level: 30%` or `status: issues_found, context_level: 45%`)
5. **Reviewers review the updated workflows** and communicate:
   - **To the updater** (via `SendMessage`): Full issue details if issues found, or "approved, no issues" if compliant
   - **To the lead** (via `SendMessage`): Only `status: approved` or `status: issues_found`, plus `context_level: XX%`
6. **Lead updates reviewer pool** based on each reviewer's reported `context_level`:
   - If `context_level` < 50%: Mark reviewer as `idle` — available for reuse in future review rounds
   - If `context_level` >= 50%: Retire reviewer via shutdown request
7. **If either reviewer flags issues**:
   - **If updater `context_level` < 50%**: The updater already received detailed findings directly from reviewers — it fixes the issues, then reports back to lead with updated `context_level`. Lead assigns 2 reviewers again (reuse idle pool or spawn fresh). Repeat until both approve.
   - **If updater `context_level` >= 50%**: The updater sends a **self-retirement request** to the lead (requesting the lead to retire it and reassign the fix to a fresh agent). Lead retires the updater, spawns a fresh replacement, and forwards the updater's partial work context + reviewer findings to the new updater. The new updater fixes issues and the cycle continues.
8. **When both reviewers approve**: Lead marks the batch as fully completed. The updater is now eligible for new batches if `context_level` < 50%; otherwise the lead retires it.

```
Per-batch flow:

  updater-N ──[update]──> lead (YAML report + context_level)
                            │
                            │  updater WAITS (no self-claiming)
                            │
                            ├──[spawn/reuse]──> reviewer-N-a (haiku)
                            └──[spawn/reuse]──> reviewer-N-b (haiku)
                                      │
                            reviewers review independently
                                      │
                            ┌─────────┴─────────┐
                            │                   │
                      To updater (DM):     To lead:
                      detailed findings   pass/fail + context_level
                            │                   │
                            └─────────┬─────────┘
                                      │
                           lead updates reviewer pool
                             < 50% → mark idle for reuse
                             >= 50% → retire via shutdown
                                      │
                            Both approve? ──yes──> batch complete
                                 │                  └── updater: pool or retire
                                 │                      based on context_level
                                 no (either flags issues)
                                 │
                           ┌─────────┴─────────┐
                           │                   │
                     updater < 50%        updater >= 50%
                           │                   │
                     updater fixes        updater sends self-
                     (already has        retirement request
                     details from          to lead
                     reviewers)              │
                           │            lead retires updater,
                           │            spawns fresh replacement,
                           │            forwards context + findings
                           │                   │
                           └─────────┬─────────┘
                                     │
                           lead assigns 2 reviewers
                                     │
                                     └──> repeat until both approve
```

**Important**: All batches run this cycle in parallel. The lead orchestrates multiple update-review cycles concurrently.

**Concurrency**: Max 4 updaters and 2 reviewers active at any time. Lead queues excess work until slots free up.

#### Phase 4: Aggregation & Cleanup (Lead)

1. **Wait** for all batch updates to complete
2. **Collect results** via `TaskGet` for each completed batch
3. **Aggregate** all batch reports into final summary
4. **Shutdown** all remaining teammates via `SendMessage` shutdown requests
5. **Delete team** via `TeamDelete`
6. Proceed to Step 3: Reporting

#### Agent Summary

| Agent | Model | Role | Max Concurrent | Lifecycle |
|-------|-------|------|----------------|-----------|
| Lead (skill agent) | opus | Orchestration only | 1 | Entire workflow |
| `updater-N` | **opus** | Update workflows with template and changes | **4** | Spawned on demand; must **wait for reviewer approval**; **reused if `context_level` < 50%**; requests retirement if >= 50% and more fix work needed |
| `reviewer-N-a/b` | **haiku** | Independent compliance review | **2** | Spawned on demand; messages **detailed findings directly to updater**; reports **pass/fail + `context_level`** to lead; reused if < 50%, retired if >= 50% |

### Step 2B: Subagent Mode (fallback)

1. **Template Validation**
   - Verify template:workflow exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

2. **Discover Workflows**
   - Locate all workflow files in [plugin]/constitution/workflows/
   - Filter by specifier if provided
   - Build list of workflows to update

3. **Delegation**
   - Create batches (max 8 workflow files per batch for subagent efficiency)
   - Create parallel specialized subagents (one per batch) with:
     - Workflow file path
     - All change specifications
     - Detailed instructions
     - Request to ultrathink

4. **Subagent Task Specification**

   >>>
   **ultrathink: adopt the Workflow Update Specialist mindset**

   - You're a **Workflow Update Specialist** with deep expertise in process documentation who follows these principles:
     - **Template-First Approach**: Always compare against template before modification
     - **Process Preservation**: Maintain existing workflow logic and steps
     - **Structural Integrity**: Align with template structure while preserving content
     - **Professional Polish**: Deliver clean, consistent workflow documentation

   <IMPORTANT>
     You've to perform the task yourself. You CANNOT further delegate the work to another subagent
   </IMPORTANT>

   **Assignment**
   You're assigned to update workflow: [workflow name]

   **Workflow Specifications**:
   - **Workflow File**: [workflow file path]
   - **Template**: template:workflow
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Workflow**:
      - Read the workflow file completely
      - Identify existing steps, phases, and subagent instructions
      - Note any custom sections or unique process logic

   2. **Compare with Template**:
      - Read template:workflow for current structure
      - Identify missing sections from template
      - Identify sections that need structural updates
      - Map changes to specific template sections

   3. **Apply Updates**:
      - Task 1: Align workflow with template:workflow structure
      - Task 2a, 2b, 2c...: Apply each change specification as subtask
      - Task 3: Review workflow integrity and consistency throughout
      - Preserve all existing process logic and steps
      - Add any missing required sections from template
      - Update ASCII diagrams if structure changed

   4. **Clean & Finalize**:
      - Remove any outdated or deprecated content
      - Ensure consistent formatting throughout
      - Verify subagent instruction blocks follow >>> <<< format
      - Ensure all placeholder content has been replaced

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens):

   ```yaml
   status: success|failure|partial
   workflow: '[workflow-name]'
   summary: 'Brief description of changes applied'
   modifications:
     - section: '[section name]'
       change: '[what was changed]'
   template_compliance: true|false
   process_preserved: true|false
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```

   <<<

5. **Progress Monitoring**
   - Track completion status of each delegated workflow
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates

### Step 3: Reporting

**Output Format** (same for both modes):

```plaintext
[✅/❌] Command: $ARGUMENTS

## Summary
- Workflows updated: [count]
- Changes applied: [change specifications]
- Template alignment: [COMPLETE/PARTIAL/FAILED]
- Execution mode: [team/subagent]

## Actions Taken
1. [Workflow file]: [Status] - [Changes applied]
2. [Workflow file]: [Status] - [Changes applied]

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
- Review updated workflows for accuracy
- Test workflow execution with sample scenarios
- Commit changes if satisfied with results
```

## Examples

### Update Single Workflow

```bash
/update-workflow "write-code.md"
# Updates specified workflow to match latest template
# Uses one ultrathink subagent for comprehensive analysis
```

### Update Single Workflow with Changes

```bash
/update-workflow "build-service.md" --change1="add Docker deployment step" --change2="include security scanning phase"
# Applies template alignment plus specified modifications
# Each change becomes a subtask (2a, 2b) in the workflow
```

### Update All Workflows (Team Mode)

```bash
/update-workflow
# With CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1:
#   Discovers all workflow files, creates update-workflow-team:
#   - updater-1 (opus): Handles batch 1 (2 workflow files)
#   - updater-2 (opus): Handles batch 2 (2 workflow files, parallel)
#   Each updater reads template and workflows, applies updates
#   Agents report context_level after completion:
#     - context < 50%: agent reused for next batch
#     - context >= 50%: agent retired, fresh replacement spawned
#   Team is cleaned up after all batches complete
```

### Update All Workflows (Subagent Fallback)

```bash
/update-workflow
# Without agent teams enabled:
#   Discovers all workflow files in [plugin]/constitution/workflows/
#   Spawns parallel subagents to update each workflow
#   Maintains consistency across entire workflow system
```

### Complex Multi-Change Update

```bash
/update-workflow "review-code.md" --change1="integrate AI-assisted review" --change2="add performance criteria" --change3="update approval requirements"
# Applies template + three specific changes
# Subagent creates tasks 1, 2a, 2b, 2c, 3 for comprehensive update
```

### Error Case Handling

```bash
/update-workflow "nonexistent-workflow.md"
# Error: Workflow file not found
# Suggestion: Check available workflows with 'find [plugin]/constitution/workflows -name "*.md"'
# Alternative: Use '/update-workflow' without arguments to update all workflows
```

### Template Missing Error

```bash
/update-workflow "some-workflow.md"
# Error: Template template:workflow not found
# Suggestion: Ensure template exists before updating workflows
# Action: Command aborts to prevent inconsistent updates
```
