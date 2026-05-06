---
name: update-skill
description: Update skill(s) to latest standard template and make specified changes. Use when bulk updating skills, ensuring template compliance, or applying consistent modifications across skill files.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite
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

1. Subagent Orchestration
2. Reporting
3. Verify & Iterate

```
[Step 1: Subagent Orchestration]
   |
   v
[Step 2: Reporting]
   |
   v
[Step 3: Verify & Iterate] ─→ (Sub-skill: governance:verify-skill per updated skill)
   |                           Loop max 2 iterations per skill
   v
[END]
```

### Step 1: Subagent Orchestration

Spawn parallel subagents (max 8 skills per batch, max 8 parallel `Task` calls per dispatch) — each ultrathinks, reads template + skill files, and applies changes. The default Content Placement Rule subtask above applies — pass it through as Task 0 of every subagent assignment.

1. **Template Validation**
   - Verify template:skill exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

2. **Discover Skills**
   - Locate all skill directories in [plugin]/skills/
   - Each skill directory contains a SKILL.md file
   - Filter by specifier if provided
   - Build list of skills to update

3. **Delegation**
   - Create batches (max 8 skill files per batch for subagent efficiency, max 8 parallel `Task` calls per dispatch)
   - Create parallel specialized subagents (one per batch) with:
     - Skill file path
     - All change specifications
     - Detailed instructions
     - Request to ultrathink

4. **Subagent Task Specification**

   >>>
   **ultrathink: adopt the Skill Update Specialist mindset**

   - You're a **Skill Update Specialist** with deep expertise in process documentation who follows these principles:
     - **Template-First Approach**: Always compare against template before modification
     - **Process Preservation**: Maintain existing skill logic and steps
     - **Structural Integrity**: Align with template structure while preserving content
     - **Professional Polish**: Deliver clean, consistent skill documentation

   <IMPORTANT>
     You've to perform the task yourself. You CANNOT further delegate the work to another subagent
   </IMPORTANT>

   **Assignment**
   You're assigned to update skill: [skill name]

   **Skill Specifications**:
   - **Skill File**: [skill file path]
   - **Template**: template:skill
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Skill**:
      - Read the skill file completely
      - Identify existing steps, phases, and subagent instructions
      - Note any custom sections or unique process logic

   2. **Compare with Template**:
      - Read template:skill for current structure
      - Identify missing sections from template
      - Identify sections that need structural updates
      - Map changes to specific template sections

   3. **Apply Updates**:
      - Task 0 (default, always run): Scan SKILL.md for conditional bulk per the **Content Placement Rule** in SKILL.md. Propose offloads to `references/<topic>.md` (or splitting into a separate skill for coherent independently-triggerable workflows) as part of this patch. Apply approved offloads before user-requested changes so subsequent edits land in the correct file.
      - Task 1: Align skill with template:skill structure
      - Task 2a, 2b, 2c...: Apply each change specification as subtask
      - Task 3: Review skill integrity and consistency throughout
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
   skill: '[skill-name]'
   summary: 'Brief description of changes applied'
   modifications:
     - section: '[section name]'
       change: '[what was changed]'
   template_compliance: true|false
   process_preserved: true|false
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```

   <<<

5. **Progress Monitoring & Aggregation**
   - Track completion status of each delegated skill
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates
   - Aggregate per-subagent YAML reports into the final Step 2 report

### Step 2: Reporting

**Output Format**:

```plaintext
[pass/fail] Command: $ARGUMENTS

## Summary
- Skills updated: [count]
- Changes applied: [change specifications]
- Template alignment: [COMPLETE/PARTIAL/FAILED]

## Actions Taken
1. [Skill file]: [Status] - [Changes applied]
2. [Skill file]: [Status] - [Changes applied]

## Subagent Results
- Total subagents deployed: [count]
- Successful updates: [count]
- Failed updates: [count] (if any)

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

## Verification Results (Step 3)
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

### Step 3: Verify & Iterate

**Step Configuration**:

- **Purpose**: Invoke verify-skill on each updated skill to ensure template compliance and quality
- **Input**: List of updated skill file paths from Step 1/2
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
3. Include in final report from Step 2

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

### Update All Skills

```bash
/update-skill
# Discovers all skill files in [plugin]/skills/
# Spawns parallel subagents (max 8 skills per batch, max 8 parallel Task calls)
# Maintains consistency across entire skill system
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
