---
name: update-skill
description: Update skill(s) to latest standard template and make specified changes. Use when bulk updating skills, ensuring template compliance, or applying consistent modifications across skill files.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [skill specifier] [--changes=...]
---

# Update Skill

Update skill files to align with the latest standard template and apply specified changes using intelligent delegation to subagents. Handles both single skill updates and bulk updates of all skills in parallel.

## Purpose & Scope

**What this skill does NOT do**:

- Create new skills (use create-skill)
- Modify non-skill files
- Update templates themselves
- Override constitutional requirements

**When to REJECT**:

- Invalid skill file paths
- Malformed change specifications
- Attempting to violate constitutional standards
- Template file is missing or corrupted

## Content Placement Rule

> **SKILL.md must contain only the always-on core workflow — the path every invocation walks.**
>
> 1. **Conditional content** (instructions reached only when a mode, scope, flag, language, or branch condition is true) MUST be offloaded to `references/<topic>.md` and referenced from SKILL.md by a one-line pointer (e.g. `For two-way merge mode, see references/two-way-merge.md`).
> 2. **Bulky AND conditional** content (>~50 lines, branch-only) MUST be offloaded. If the conditional branch is itself a coherent independently-triggerable workflow, **split it into a separate skill** instead.
> 3. **Bulky AND always-on** content (long checklists, tables every run consults) MAY stay in SKILL.md if every invocation uses it; offload only if it is genuinely optional.
> 4. **Non-bulky conditional** content (short `if X then do Y` lines) MAY stay inline.
>
> Rationale: SKILL.md is loaded on every invocation; references are loaded on demand. Inline conditional bulk is paid for by every run that never enters the branch.

**Default subtask for every update**: Before applying user-requested changes, scan SKILL.md for conditional bulk and propose offloads as part of the patch. Include the offload moves alongside the requested change set.

## Workflow

ultrathink: you'd perform the following steps

**Skill Steps**:

1. Mode Selection
2. Execution (Team or Subagent mode)
3. Reporting
4. Verify & Iterate

```
[Step 1: Mode Selection]
   |
   v
[Step 2: Execution] ─→ (Team Mode 2A or Subagent Mode 2B)
   |
   v
[Step 3: Reporting]
   |
   v
[Step 4: Verify & Iterate] ─→ (Sub-skill: governance:verify-skill per updated skill)
   |                           Loop max 2 iterations per skill
   v
[END]
```

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.

- **If present**: Use **Team Mode** (Step 2A)
- **If absent**: Use **Subagent Mode** (Step 2B)

### Step 2A: Team Mode (Agent Teams enabled)

Lead Orchestrator coordinates updater (opus) and reviewer (haiku) teammates with batched update-review cycles and context-level pool management. For the full Phase 1–4 procedure (Lead rules, planning, team setup, update-review cycle, aggregation/cleanup) and the agent summary table, see `references/team-mode.md`.

The default Content Placement Rule subtask above applies — pass it through to updaters as Task 0 of every batch.

### Step 2B: Subagent Mode (fallback)

Spawn parallel subagents (max 8 skills per batch) — each ultrathinks, reads template + skill files, and applies changes. The default Content Placement Rule subtask above applies — pass it through as Task 0 of every subagent assignment. For full procedure (template validation, discovery, delegation, the verbatim subagent prompt with `>>> <<<` block, report YAML, and progress monitoring), see `references/subagent-mode.md`.

### Step 3: Reporting

**Output Format** (same for both modes):

```plaintext
[pass/fail] Command: $ARGUMENTS

## Summary
- Skills updated: [count]
- Changes applied: [change specifications]
- Template alignment: [COMPLETE/PARTIAL/FAILED]
- Execution mode: [team/subagent]

## Actions Taken
1. [Skill file]: [Status] - [Changes applied]
2. [Skill file]: [Status] - [Changes applied]

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

## Verification Results (Step 4)
```yaml
verification:
  total_verified: N
  passed_first_try: N
  passed_after_fix: N
  remaining_issues: N
  per_skill:
    - skill: '[skill-name]'
      status: pass|fail
      iterations: N
```

## Next Steps (if applicable)
- Review updated skills for accuracy
- Test skill execution with sample scenarios
- Commit changes if satisfied with results
```

### Step 4: Verify & Iterate

**Step Configuration**:

- **Purpose**: Invoke verify-skill on each updated skill to ensure template compliance and quality
- **Input**: List of updated skill file paths from Step 2/3
- **Output**: Per-skill verification results, potentially improved skill files
- **Sub-skill**: /Users/alvis/Repositories/.claude/plugins/governance/skills/verify-skill/SKILL.md
- **Parallel Execution**: Yes — verify each updated skill independently

#### Execute Verify Sub-Skill (You)

For each updated skill file in the batch:

1. Use Read tool to load the sub-skill file at the path above
2. Invoke verify-skill with these parameters:
   - **skill_path**: [updated SKILL.md path]
   - **mode**: `structural` (default for update-skill — focus on template/formatting compliance)
   - **fix**: `true`
3. Evaluate verify-skill results:
   - **IF pass** → Mark skill as verified
   - **IF fail with suggestions** → Spawn fix subagent with suggestions, re-verify
   - **Max 2 iterations** per skill (update-skill is a batch operation, keep bounded)
   - **IF 2 failures** → Record remaining issues, continue to next skill
4. Use TodoWrite to track verification progress per skill

**Fix Subagent Instructions** (when verify-skill reports issues):

    >>>
    **ultrathink: adopt the Skill Repair Specialist mindset**

    - You're a **Skill Repair Specialist** who fixes skill document issues:
      - **Precision Fixes**: Address only the specific issues reported
      - **Minimal Changes**: Don't rewrite sections that pass validation
      - **Quality Preservation**: Maintain overall document quality while fixing issues

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Assignment**: Fix the following issues in skill file at [skill_path]

    **Issues to Fix**:
    [List of issues from verify-skill report]

    **Suggestions**:
    [List of suggestions from verify-skill report]

    **Steps**
    1. Read the skill file
    2. For each reported issue, apply the suggested fix
    3. Verify the fix doesn't break other sections
    4. Save the updated file

    **Report**
    ```yaml
    status: success|failure
    summary: 'Fixed N issues in skill file'
    modifications: ['[skill-path]']
    outputs:
      issues_fixed: N
      issues_remaining: N
    issues: [...]
    ```
    <<<

#### Aggregate Verification Results (You)

After all skills have been verified:

1. Collect verification reports for all updated skills
2. Compile aggregate summary:
   - Total skills verified
   - Skills passing on first try
   - Skills requiring fix iterations
   - Skills with remaining issues
3. Include in final report from Step 3

## Examples

### Update Single Skill

```bash
/update-skill "create-skill"
# Updates specified skill to match latest template
# Uses one ultrathink subagent for comprehensive analysis
```

### Update Single Skill with Changes

```bash
/update-skill "create-skill" --change1="add parallel execution support" --change2="include security scanning phase"
# Applies template alignment plus specified modifications
# Each change becomes a subtask (2a, 2b) in the skill
```

### Update All Skills (Team Mode)

```bash
/update-skill
# With CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1:
#   Discovers all skill files, creates update-skill-team:
#   - updater-1 (opus): Handles batch 1 (2 skill files)
#   - updater-2 (opus): Handles batch 2 (2 skill files, parallel)
#   Each updater reads template and skills, applies updates
#   Agents report context_level after completion:
#     - context < 50%: agent reused for next batch
#     - context >= 50%: agent retired, fresh replacement spawned
#   Team is cleaned up after all batches complete
```

### Update All Skills (Subagent Fallback)

```bash
/update-skill
# Without agent teams enabled:
#   Discovers all skill files in [plugin]/skills/
#   Spawns parallel subagents to update each skill
#   Maintains consistency across entire skill system
```

### Complex Multi-Change Update

```bash
/update-skill "review-code" --change1="integrate AI-assisted review" --change2="add performance criteria" --change3="update approval requirements"
# Applies template + three specific changes
# Subagent creates tasks 1, 2a, 2b, 2c, 3 for comprehensive update
```

### Error Case Handling

```bash
/update-skill "nonexistent-skill"
# Error: Skill file not found
# Suggestion: Check available skills with 'find [plugin]/skills -name "SKILL.md"'
# Alternative: Use '/update-skill' without arguments to update all skills
```

### Template Missing Error

```bash
/update-skill "some-skill"
# Error: Template template:skill not found
# Suggestion: Ensure template exists before updating skills
# Action: Command aborts to prevent inconsistent updates
```
