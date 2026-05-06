# Step 2B: Subagent Mode (fallback)

This reference is consulted when Step 1 (Mode Selection) does NOT detect Agent Teams in the session context. Otherwise use Team Mode (`references/team-mode.md`).

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
   - Create batches (max 8 skill files per batch for subagent efficiency)
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

5. **Progress Monitoring**
   - Track completion status of each delegated skill
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates
