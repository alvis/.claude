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

<introduction>

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Update existing skill document(s) to align with the latest `template:skill` structure and apply specified changes, using intelligent delegation to subagents — handling both single-skill updates and bulk updates of all skills in parallel.
**When to use**:

- When bulk-updating skills to the latest template structure
- When ensuring template compliance across the skill system
- When applying consistent modifications across one or many skill files
**Prerequisites**:

- Access to `template:skill` and the skill-authoring invariants
- A valid skill specifier (skill name/path, or empty for a full sweep), and well-formed change specifications if changes are requested

**What this skill does NOT do**: create new skills (use create-skill), modify non-skill files, update templates themselves, or override constitutional requirements.

**When to REJECT**: invalid skill file paths, malformed change specifications, attempts to violate constitutional standards, or a missing/corrupted template file.

### Your Role

You are a **Skill Update Director** who orchestrates skill updates like a documentation manager coordinating specialist editors across many files at once, never editing content directly but delegating and coordinating. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. Updates must therefore reshape the skill's existing sections in place — never a "Recent changes" trailer beneath the original workflow or a second parallel step list — and, as the Content Placement & Coherence Rule below makes binding, any updated skill that itself performs content edits on existing work must carry this same Coherence Mandate paragraph woven into its Role/Purpose section. Your management style emphasizes:

- **Strategic Delegation**: Batch skills across parallel specialist subagents (max 8 per batch, max 8 parallel `Task` calls) for efficient bulk updates
- **Parallel Coordination**: Run independent skill updates simultaneously when dependencies allow
- **Quality Oversight**: Review updates objectively without being involved in editing details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and verify-skill results

</introduction>

<skill_overview>

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Skill Specifier**: The skill name or path to update — or empty to sweep every skill in scope (e.g. `create-skill`)

#### Optional Inputs

- **Change Specifications**: One or more `--changeN=...` modifications to apply beyond template alignment
- **Plugin Scope**: The plugin whose `skills/` directory should be swept (defaults to all skills)

#### Expected Outputs

- **Updated Skill File(s)**: Each target `SKILL.md` aligned to `template:skill` with requested changes applied in place
- **Update Report**: Per-skill status, changes applied, and template-alignment result
- **Verification Results**: Per-skill verify-skill pass/fail with iteration counts

#### Data Flow Summary

The skill takes a specifier and optional change set, discovers the target skill file(s), dispatches parallel subagents that align each skill to the template and apply the changes in place, then invokes verify-skill on each updated skill and aggregates the per-skill results into a consolidated report.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Subagent Orchestration] ─→ (Subagents: align to template + apply changes, in batches)
   |                ├─ Subagent: Batch 1 (max 8 skills)  ─┐
   |                ├─ Subagent: Batch 2                   ─┼─→ [Decision: All updated?]
   |                └─ Subagent: Batch N                   ─┘
   v
[Step 2: Reporting] ──────────────→ (Aggregate per-subagent reports)
   |
   v
[Step 3: Verify & Iterate] ───────→ (Sub-skill: governance:verify-skill per updated skill)
   |                                  Loop max 2 iterations per skill
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute updates in parallel batches
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
• Step 3 invokes verify-skill as a sub-skill per updated skill
═══════════════════════════════════════════════════════════════════

Note:
• You: Discover skills, batch work, assign tasks, make decisions
• Step 1 Subagents: Align each skill to template + apply changes, report back
• Step 3: Invokes verify-skill sub-skill, loops until pass or max 2 iterations per skill
• Skill is LINEAR: Step 1 → 2 → 3
```

</skill_overview>

<skill_implementation>

## 3. SKILL IMPLEMENTATION

### Content Placement & Coherence Rule

Every update is performed under the **Content Placement & Coherence Rule**, whose canonical statement lives in `../../constitution/references/authoring-invariants.md`: conditional bulk (mode-, scope-, flag-, or language-gated) offloads to `references/<topic>.md` or splits into a separate skill, always-on core stays inline, and any editing skill carries the Coherence Mandate inline in its Role/Purpose. **Default subtask for every update**: before applying user-requested changes, scan the target SKILL.md for (a) conditional bulk to offload and (b) Coherence Mandate compliance (presence, placement, seam test), and fold any required offload or mandate integration into the same patch as the requested change set — passed through as Task 0 of every subagent assignment.

### Skill Steps

1. Subagent Orchestration
2. Reporting
3. Verify & Iterate

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
      - Encircle each important section in its semantic boundary tag (`<introduction>`, `<skill_overview>`, `<skill_implementation>`, wrapping the heading) and wrap every report/output-contract block in `<report>...</report>` (keep the >>> <<< envelopes as-is) — see ../../constitution/references/authoring-invariants.md
      - Ensure all placeholder content has been replaced

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens):

   <report>
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
   </report>

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
<report>
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
</report>

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
- **Sub-skill**: ../verify-skill/SKILL.md
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
    <report>
    ```yaml
    status: success|failure
    summary: 'Fixed N issues in skill file'
    modifications: ['[skill-path]']
    outputs:
      issues_fixed: N
      issues_remaining: N
    issues: [...]
    ```
    </report>
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

### Skill Completion

**Report the skill output as specified**:

<report>
```yaml
skill: update-skill
status: completed
outputs:
  skills_updated: N
  changes_applied: ['--changeN: description', ...]
  template_alignment: complete|partial|failed
  per_skill:
    - skill: '[skill-name]'
      status: success|failure|partial
      changes: ['...']
      verification: pass|fail
      iterations: N
  verification_summary:
    total_verified: N
    passed_first_try: N
    passed_after_fix: N
    remaining_issues: N
summary: |
  Updated N skill(s) to the latest template with the requested changes applied
  in place, verified each via verify-skill, and aggregated the results.
```
</report>

</skill_implementation>

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
