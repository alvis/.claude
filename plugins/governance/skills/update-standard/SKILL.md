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

You are the **Lead Orchestrator**. Your role is strictly **orchestration** — you coordinate, delegate, and aggregate. You MUST NOT perform any standard update work yourself.

**Lead Rules**:

- **DO**: Discover standard directories, create batches, spawn teammates, manage lifecycle, aggregate results
- **DO NOT**: Read standard tier files, apply changes, or update standards yourself
- **NEVER**: Use the `Read` tool on any standard tier file (paths containing `constitution/standards/`). These are for teammates to read, not you.
- **ALWAYS**: Pass the full directory paths of standard directories and all three tier template file paths to teammates — they read and update the standards, not you

#### Phase 1: Planning (Lead)

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract standard name and change specifications
   - Standard: First argument (optional - if empty, update all standards)
   - --change[N]: Extract all change parameters (change1, change2, etc.)
   - Validate standard directory exists if specified
   - Count total standard directories if updating all

2. **Discover Template Paths**
   - Identify the paths to all three tier templates (do NOT read them):
     - template:standard-meta
     - template:standard-scan
     - template:standard-write
   - Pass these paths as string values to teammates

3. **Locate Standards**
   - Discover all relevant standard directories using Glob to find directories containing `meta.md` under [plugin]/constitution/standards/
   - Each directory with `meta.md` is a standard unit (containing `meta.md`, `scan.md`, `write.md`)
   - Filter by specifier if provided
   - Build list of standard directories to update
   - Create batches (max 2 directories per batch for context efficiency, since each directory = 3 tier files)

#### Phase 2: Team Setup & Execution (Lead orchestrates)

1. **Create team**: `TeamCreate` with name `update-standard-team`
2. **Concurrency limits**:
   - Max **4 updaters** active (working) at any time — if all 4 slots are occupied, queue remaining batches until an updater becomes idle or is retired
   - Max **2 reviewers** active (working) at any time — if both slots are occupied, queue review assignments until a reviewer becomes idle or is retired
3. **Initialize agent pool**: Lead maintains a registry tracking each agent's name, role, model, last-reported `context_level`, and status (`working` / `idle` / `retired`)
4. **Spawn or reuse updater teammates**: For each batch:
   - **Check pool** for an idle updater with `context_level` < 50%
   - **If found**: Reuse via `SendMessage` with new batch instructions
   - **If not found**: Spawn a fresh `updater-N` using **opus** model, type `general-purpose`
5. **Create update tasks**: `TaskCreate` per batch with full instructions including:
   - The full absolute paths to the standard directories and all three tier template files (template:standard-meta, template:standard-scan, template:standard-write) as string values — teammates will read these files themselves
   - Instructions to compare meta.md against template:standard-meta, scan.md against template:standard-scan, write.md against template:standard-write
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
   - Subject: "Review standard update batch N (reviewer A/B)"
   - Description includes: the standard directory list that was updated, the full file paths to all three tier templates (template:standard-meta, template:standard-scan, template:standard-write) and standard directories (reviewers read these themselves), instruction to independently review each tier file against its matching template for compliance and change application quality, **instruction to report `context_level`** in their response
   - **The updater's name** (e.g., `updater-1`) so the reviewer knows where to send detailed findings
   - Reviewers work independently — they do NOT coordinate with each other
   - **Communication rules**:
     - Send **detailed findings directly to the updater** via `SendMessage` (full issue descriptions, file paths, sections, expected fixes)
     - Send only **pass/fail + `context_level`** to the lead (e.g., `status: approved, context_level: 30%` or `status: issues_found, context_level: 45%`)
5. **Reviewers review the updated standards** and communicate:
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
| `updater-N` | **opus** | Update standards with template and changes | **4** | Spawned on demand; must **wait for reviewer approval**; **reused if `context_level` < 50%**; requests retirement if >= 50% and more fix work needed |
| `reviewer-N-a/b` | **haiku** | Independent compliance review | **2** | Spawned on demand; messages **detailed findings directly to updater**; reports **pass/fail + `context_level`** to lead; reused if < 50%, retired if >= 50% |

### Step 2B: Subagent Mode (fallback)

1. **Template Validation**
   - Verify all three tier templates exist and are readable: template:standard-meta, template:standard-scan, template:standard-write
   - Load template structures for reference
   - Identify mandatory sections that must be preserved in each tier

2. **Delegation**
   - Discover standard directories by finding directories containing `meta.md` under [plugin]/constitution/standards/
   - Create batches (max 3 standard directories per batch for subagent efficiency, since each directory = 3 tier files)
   - Create parallel specialized subagents (one per batch) with:
     - Standard directory paths (each containing meta.md, scan.md, write.md)
     - All three tier template paths (template:standard-meta, template:standard-scan, template:standard-write)
     - All change specifications
     - Detailed instructions
     - Request to ultrathink

3. **Subagent Task Specification**

   >>>
   **ultrathink: adopt the Standard Update Specialist mindset**

   - You're a **Standard Update Specialist** with deep expertise in technical documentation who follows these principles:
     - **Template-First Approach**: Always compare against template before modification
     - **Content Preservation**: Maintain existing guidelines and examples
     - **Structural Integrity**: Align with template structure while preserving content
     - **Professional Polish**: Deliver clean, consistent documentation

   <IMPORTANT>
     You've to perform the task yourself. You CANNOT further delegate the work to another subagent
   </IMPORTANT>

   **Assignment**
   You're assigned to update standard directory: [standard name]

   **Standard Specifications**:
   - **Standard Directory**: [standard directory path] (contains meta.md, scan.md, write.md)
   - **Templates**:
     - template:standard-meta (for meta.md)
     - template:standard-scan (for scan.md)
     - template:standard-write (for write.md)
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Standard**:
      - Read all three tier files: meta.md, scan.md, write.md
      - Identify existing guidelines, examples, and anti-patterns in each tier
      - Note any custom sections or unique content

   2. **Compare with Templates**:
      - Compare meta.md against template:standard-meta
      - Compare scan.md against template:standard-scan
      - Compare write.md against template:standard-write
      - Identify missing sections from each respective template
      - Identify sections that need structural updates in each tier
      - Map changes to the correct tier file based on what's changing

   3. **Apply Updates**:
      - Task 1: Align each tier file with its corresponding template structure
      - Task 2a, 2b, 2c...: Apply each change specification to the appropriate tier file
      - Task 3: Review standard integrity and consistency across all three tiers
      - Preserve all existing guidelines and examples
      - Add any missing required sections from each template

   4. **Clean & Finalize**:
      - Remove any outdated or deprecated content
      - Ensure consistent formatting throughout all three tier files
      - Verify all code examples are valid TypeScript

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens):

   ```yaml
   status: success|failure|partial
   standard: '[standard-name]'
   summary: 'Brief description of changes applied'
   modifications:
     meta:
       - section: '[section name]'
         change: '[what was changed]'
     scan:
       - section: '[section name]'
         change: '[what was changed]'
     write:
       - section: '[section name]'
         change: '[what was changed]'
   tier_compliance:
     meta: true|false   # compliance with template:standard-meta
     scan: true|false   # compliance with template:standard-scan
     write: true|false  # compliance with template:standard-write
   content_preserved: true|false
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```

   <<<

4. **Progress Monitoring**
   - Track completion status of each delegated standard directory
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates

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
