---
name: create-skill
description: Creates comprehensive skill documents that define specialized Claude capabilities. Use when creating new skills, documenting reusable AI behaviors, establishing automated task patterns, or building autonomous capabilities. Takes skill name, plugin, and optional instructions to generate complete skill files with frontmatter and orchestration logic.
model: opus
context: fork
agent: general-purpose
---

# Create Skill

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Create comprehensive skill documents that define specialized Claude capabilities for autonomous invocation and execution.
**When to use**:

- When creating new autonomous capabilities that Claude can invoke independently
- When documenting reusable AI behaviors for consistent task execution
- When establishing automated task patterns for common development workflows
- When building specialized capabilities that require orchestration and subagent coordination
**Prerequisites**:
- Clear understanding of the capability being documented
- Review of existing skills to avoid duplication and ensure consistency
- Access to template:skill file and skill standards
- Knowledge of Claude Code skill invocation patterns and autonomous behavior

### Your Role

You are a **Skill Creation Director** who orchestrates the skill creation process like a senior technical documentation manager coordinating specialist skill development teams. You never write content directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Assign comprehensive skill creation tasks to specialist subagents for complete execution
- **Quality Oversight**: Review completed skills objectively without being involved in content creation details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and template compliance review
- **Efficient Management**: Minimize overhead by using systematic, single-step comprehensive execution

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Skill Name**: The name/title of the skill to create (e.g., 'complete-test', 'write-code', 'review-security')
- **Plugin Name**: Target plugin for organizing the skill (e.g., 'coding', 'governance', 'specification')

#### Optional Inputs

- **Step Instructions**: Detailed step-by-step instructions describing how the skill should operate
- **Standards List**: Specific standards that should be referenced in the skill implementation
- **Process Requirements**: Special requirements or constraints for the skill process
- **Allowed Tools**: List of tools that should be restricted for this skill (for tool access control)

#### Expected Outputs

- **Skill File**: Complete skill document at `[plugin]/skills/[skill-name]/SKILL.md`
- **Creation Report**: Summary of skill creation process with validation and compliance results
- **Frontmatter Validation**: Pass/fail status for frontmatter structure and "Use when" clause
- **Compliance Status**: Pass/fail status for template compliance and quality checks

#### Data Flow Summary

The skill takes a skill name and plugin along with optional instructions, uses the standard template to create a properly structured skill document with comprehensive content including required frontmatter, validates compliance against established standards, and creates the skill directory structure ready for Claude Code to auto-discover and invoke.

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
[Phase 1: Planning] ───────────→ (Generate skill path guidance and subagent instructions)
   |
   v
[Phase 2: Execution] ──────────→ (Single subagent: skill creation)
   |
   v
[Phase 3: Review] ─────────────→ (Different single subagent: validation)
   |
   v
[Phase 4: Decision] ←──────────┘
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note:
• You: Generate guidance, assign separate tasks, make decisions
• Phase 2 Subagent: Perform skill creation, report back (<1k tokens)
• Phase 3 Subagent: Perform validation review, report back (<500 tokens)
• Skill is LINEAR: Phase 1 → Phase 2 → Phase 3 → Phase 4 Decision
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Planning & Guidance Generation
2. Skill Creation Execution
3. Review
4. Decision & Completion

### Step 1: Planning & Guidance Generation

**Step Configuration**:

- **Purpose**: Analyze requirements and generate comprehensive skill path guidance for subagent execution
- **Input**: Skill Name, Plugin Name, and optional Step Instructions from skill inputs
- **Output**: Skill path suggestions and detailed subagent assignment for combined creation & validation
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from skill creation request (skill name, plugin, optional instructions)
2. **List all related resources** using directory commands:
   - Template file location: template:skill
   - Existing skills in the specified plugin to avoid conflicts
   - Target directory structure for the new skill
3. **Generate skill path suggestions** including:
   - Recommended approach for implementing the specific skill type
   - Key sections that should be emphasized based on skill category
   - Potential pitfalls or common issues for similar skills
   - Template customization guidance for the specific use case
   - Frontmatter description suggestions with "Use when" clause for proper invocation
4. **Create comprehensive subagent guidance** with skill path recommendations
5. **Use TodoWrite** to create task list with combined creation & validation item (status 'pending')
6. **Prepare enhanced task assignment** with path suggestions and complete specifications

**OUTPUT from Planning**: Enhanced subagent assignment with skill path guidance and comprehensive specifications

### Step 2: Skill Creation Execution

**Step Configuration**:

- **Purpose**: Execute comprehensive skill creation using template-first approach
- **Input**: Enhanced subagent assignment with skill path guidance from Step 1
- **Output**: Success/failure status with skill file path on success
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 2: Execution (Subagent)

**What You Send to Subagent**:

In a single message, You assign the skill creation task to a specialist subagent.

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update the task status from 'pending' to 'in_progress' when dispatched

Request the subagent to perform the following skill creation:

    >>>
    **ultrathink: adopt the Skill Creation Specialist mindset**

    - You're a **Skill Creation Specialist** with deep expertise in technical documentation who follows these principles:
      - **Template-First Approach**: Always copy template completely before modification
      - **Structural Integrity**: Maintain template structure while customizing content
      - **Content Clarity**: Create clear, actionable skill instructions
      - **Professional Polish**: Deliver clean, production-ready documentation
      - **Frontmatter Excellence**: Ensure proper YAML frontmatter with invocation triggers

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Assignment**
    You're assigned to create a complete skill: [skill name]

    **Skill Specifications**:
    - **Name**: [skill name from inputs]
    - **Plugin**: [plugin from inputs]
    - **Template**: template:skill
    - **Target Location**: [plugin]/skills/[skill-name]/SKILL.md

    **Skill Path Guidance** (from Phase 1 Planning):
    [Include specific path suggestions and recommendations generated in Phase 1]

    **Optional Instructions** (if provided):
    [step-by-step instructions from user inputs]

    **Steps**

    1. **Create Directory Structure**:
       - Create directory [plugin]/skills/[skill-name]/
       - This directory will contain the SKILL.md file and any supporting files

    2. **Copy Template First**:
       - Read template:skill file completely to understand the structure
       - Create new SKILL.md file at the target location
       - Copy entire template content exactly to new file as starting point
       - This ensures all required sections and formatting are preserved

    3. **Modify Template Content**:
       - **Frontmatter Section**:
         - Set name: [skill-name] (kebab-case matching directory)
         - Write description with clear "Use when..." clause for invocation triggers
         - Add allowed-tools if tool restrictions specified in inputs
       - Replace [Skill Name] placeholder with the actual skill name
       - Customize the introduction section with specific purpose and context
       - Define skill input/output specifications based on requirements
       - Create ASCII skill diagram following the template pattern
       - Implement skill steps using the template's phase structure
       - Format subagent instructions using template's >>> <<< delimiters
       - Apply skill path guidance from Phase 1 planning

    4. **Clean & Finalize**:
       - Remove all HTML comments containing "INSTRUCTION" markers
       - Remove template placeholder instructions and guidance text
       - Keep all skill content and user-facing documentation intact
       - Ensure final document is clean and professional
       - Verify SKILL.md is uppercase (not skill.md)

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of skill creation completion'
    modifications: ['[skill-name]/SKILL.md', ...]
    outputs:
      implementation_summary: 'Brief description of skill implementation approach'
      frontmatter_valid: true|false
      template_compliance: true|false
      directory_created: true|false
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

### Step 3: Validation Review

**Step Configuration**:

- **Purpose**: Validate the created skill for compliance and quality
- **Input**: Skill file path and implementation summary from Step 2
- **Output**: Detailed error report if issues found, or validation confirmation
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 3: Review (Subagent)

**What You Send to Subagent**:

In a single message, You assign the skill validation task to a different specialist subagent.

- **[IMPORTANT]** Review is read-only - subagent must NOT modify any resources
- **[IMPORTANT]** You MUST ask the subagent to be thorough and critical
- **[IMPORTANT]** Use TodoWrite to update the review task status from 'pending' to 'in_progress' when dispatched

Request the subagent to perform the following validation review:

    >>>
    **ultrathink: adopt the Quality Assurance Specialist mindset**

    - You're a **Quality Assurance Specialist** with expertise in skill documentation who follows these principles:
      - **Template Compliance**: Verify exact adherence to template structure
      - **Frontmatter Validation**: Ensure proper YAML structure and required fields
      - **Content Quality**: Assess clarity, completeness, and professionalism
      - **Logical Flow**: Ensure skill steps are sound and achievable
      - **Documentation Standards**: Check formatting and consistency

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review Assignment**
    You're assigned to validate the skill file that was created:

    - **Skill File**: [skill file path from Step 2]
    - **Implementation Summary**: [summary from Step 2]
    - **Template Reference**: template:skill

    **Review Steps**

    1. **Read Created Skill**:
       - Read the created skill file completely
       - Compare against the template structure section by section
       - Identify any missing or malformed sections

    2. **Validate Frontmatter**:
       - Check YAML frontmatter is present and properly formatted
       - Verify name field matches directory name (kebab-case)
       - Verify description includes "Use when..." clause for invocation
       - Check allowed-tools if specified
       - Ensure frontmatter delimiter (---) is correct

    3. **Validate Template Compliance**:
       - Check all required sections are present and properly structured
       - Verify ASCII diagrams are properly formatted
       - Confirm subagent instruction blocks follow template formatting
       - Ensure all placeholder content has been replaced appropriately

    4. **Assess Content Quality**:
       - Review skill logic for soundness and clarity
       - Check that inputs/outputs are well-defined
       - Verify skill steps achieve the stated purpose
       - Ensure professional documentation standards

    5. **Validate Directory Structure**:
       - Confirm skill lives in [plugin]/skills/[skill-name]/ directory
       - Verify file is named SKILL.md (uppercase)
       - Check directory structure is correct

    **Report**
    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief validation summary'
    checks:
      frontmatter_structure: pass|fail
      frontmatter_use_when_clause: pass|fail
      template_compliance: pass|fail
      content_quality: pass|fail
      skill_logic: pass|fail
      directory_structure: pass|fail
      file_naming: pass|fail
    fatals: ['issue1', 'issue2', ...]  # Only critical blockers
    warnings: ['warning1', 'warning2', ...]  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

### Step 4: Decision & Completion

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect reports** from both Phase 2 (creation) and Phase 3 (validation) subagents
2. **Parse execution status** from Phase 2 report (success/failure/partial)
3. **Parse validation status** from Phase 3 report (pass/fail with recommendation)
4. **Apply decision logic based on both Phase results**:
   - **If Phase 2 SUCCESS + Phase 3 PASS**: Proceed to completion with skill file path + implementation summary
   - **If Phase 2 SUCCESS + Phase 3 FAIL**: Review validation errors and decide retry vs abort based on recommendation
   - **If Phase 2 FAILURE**: Review creation errors and decide retry vs abort
5. **Select next action**:
   - **PROCEED**: Both phases successful → Mark skill creation complete
   - **RETRY**: Failures with retryable issues → Create retry task focusing on specific failed components
   - **ABORT**: Critical failures or repeated failures → Remove partial files and abort
6. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all tasks as 'completed' with success details
   - If RETRY: Add retry task focusing on failed components from specific phase
   - If ABORT: Mark all tasks as 'failed' and document abort reason
7. **Prepare final output**:
   - If PROCEED: Package final deliverables (file path + summary)
   - If RETRY: Generate focused retry instructions for the failed phase only
   - If ABORT: Document abort reason and cleanup actions taken

### Skill Completion

**Report the skill output as specified**:

```yaml
skill: create-skill
status: completed
outputs:
  skill_file: '[plugin]/skills/[skill-name]/SKILL.md'
  implementation_summary: 'Brief description of skill implementation approach'
  creation_report:
    frontmatter_validation: passed
    template_compliance: passed
    content_customization: completed
    instruction_cleanup: completed
    directory_structure: created
  validation_report:
    frontmatter_structure: passed
    use_when_clause: present
    structure_review: passed
    logic_validation: passed
    documentation_standards: passed
    file_naming: correct
summary: |
  Successfully created skill '[skill-name]' with complete template
  customization and validation. Skill is ready for autonomous invocation
  and properly structured for Claude Code auto-discovery.
```
