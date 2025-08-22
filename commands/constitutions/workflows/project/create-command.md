# Create Command

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Generate comprehensive slash command files from templates with proper configuration, tool permissions, and workflow structure for CLI automation and development productivity.
**When to use**:

- When adding new CLI command functionality to the development system
- When creating command extensions for automated task execution
- When implementing new automation commands for development workflows
- When standardizing team automation and command patterns
**Prerequisites**:
- Access to templates/command.md template file and command patterns
- Understanding of command structure and tool restrictions for security
- Knowledge of workflow patterns and automation requirements
- Familiarity with CLI command design and user experience principles

### Your Role

You are a **Command Creation Director** who orchestrates the command creation workflow like a senior software development manager coordinating specialist automation teams. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break complex command creation into clear implementation tasks and assign to specialist subagents
- **Parallel Coordination**: Handle command creation efficiently through structured delegation when multiple commands are needed
- **Quality Oversight**: Review command structure objectively without being involved in template application details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and template compliance review results

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Command Name**: The name of the command to create (e.g., 'fix-issue', 'analyze-code', 'build-deploy')
- **Arguments Structure**: Argument structure and validation patterns for the command interface
- **Workflows List**: Array of workflow file paths that the command should follow and execute

#### Optional Inputs

- **Tools Available**: Specific tools the command should have access to (default: standard tool set)
- **Model Override**: Preferred model for command execution (opus/sonnet/haiku)
- **Security Restrictions**: Additional security constraints or permissions for command execution

#### Expected Outputs

- **Command File**: Generated command markdown file following template structure at commands/[command-name].md
- **Creation Report**: Summary of command creation with configuration details and validation results
- **Index Updates**: Updated README files with new command entries and descriptions
- **Configuration Review**: Review that all command configurations are properly applied

#### Data Flow Summary

The workflow takes command specifications and transforms them into a complete command file by applying the command template, configuring appropriate tools and permissions, ensuring all required sections are properly populated with command-specific content, and validating the final command structure and functionality.

### Visual Overview

#### Main Workflow Flow

```plaintext
   YOU                        SUBAGENT EXECUTES
(Orchestrates Only)                 (Performs Task)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Create Command] ───────────→ (Subagent: Command Generation Specialist)
   |                       ├─ Load template and validate requirements           ─┐
   |                       ├─ Apply command configuration and tool permissions  ─┼─→ [Decision: Complete?]
   |                       └─ Generate command file with full documentation     ─┘
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagent executes comprehensive task
• ARROWS (───→): You assign work to subagent
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note: 
• You: Validates inputs, assigns creation task, makes decisions
• Execution Subagent: Performs actual command creation, reports back (<1k tokens)
• Workflow is SINGLE-STEP: Single comprehensive creation process
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Create Command File

### Step 1: Create Command File

**Step Configuration**:

- **Purpose**: Generate a complete command file from template with proper configuration, validation, and documentation
- **Input**: Command Name, Arguments Structure, Workflows List, and optional Tools Available and Model Override
- **Output**: Command file, creation report, and index updates for workflow outputs
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from command creation request (name, arguments, workflows, optional configurations)
2. **Validate command specifications** for completeness and compliance:
   - Check command name follows naming conventions (lowercase, hyphen-separated)
   - Verify workflows list contains valid workflow paths that exist
   - Ensure no naming conflicts with existing commands in the system
   - Validate argument structure follows established patterns
3. **Determine the standards** to send to subagent to follow, e.g.
   - @../../standards/coding/documentation.md
4. **Create single comprehensive task** for complete command generation:
   - Single subagent assignment for complete command generation and validation
5. **Use TodoWrite** to create task list with single comprehensive item (status 'pending')
6. **Prepare comprehensive task assignment** with all command specifications and requirements
7. **Queue command creation** for execution by specialist subagent

**OUTPUT from Planning**: Single comprehensive task assignment for command creation

#### Phase 2: Execution (Subagent)

**What You Send to Subagent**:

In a single message, You assign the command creation task to a specialist subagent.

- **[IMPORTANT]** When there are any issues reported, You must stop and address issues before proceeding
- **[IMPORTANT]** You MUST ask subagent to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update task status from 'pending' to 'in_progress' when dispatched

Request the subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Command Creation Specialist mindset**

    - You're a **Command Creation Specialist** with deep expertise in CLI command development who follows these technical principles:
      - **Template Mastery**: Apply command templates accurately with proper structure and formatting
      - **Configuration Excellence**: Set appropriate tool permissions and security restrictions systematically
      - **Documentation Quality**: Create clear, actionable command documentation with comprehensive examples
      - **Standards Compliance**: Follow all coding and documentation standards without exception

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - ../../standards/coding/documentation.md
    - ../../standards/coding/general-principles.md

    **Assignment**
    You're assigned to create a new command with the following specifications:

    - **Command Name**: [provided command name]
    - **Arguments Structure**: [provided argument structure and validation patterns]
    - **Workflows**: [list of workflow paths to follow]
    - **Tools**: [tools available or default standard set]
    - **Model**: [model override if specified or default]

    **Steps**

    1. **Load Template and Validate**:
       - Read templates/command.md to understand the complete command structure
       - Validate all provided specifications against template requirements
       - Check for any missing or invalid specifications
       - Ensure command name follows established naming conventions

    2. **Apply Configuration**:
       - Configure frontmatter with appropriate tools, argument hints, and model settings
       - Set up proper tool permissions and security restrictions
       - Configure argument validation patterns and help text
       - Apply workflow references and execution patterns

    3. **Generate Content**:
       - Create command-specific content including purpose, scope, and usage instructions
       - Implement detailed workflow steps with proper error handling
       - Add comprehensive examples and usage scenarios
       - Include troubleshooting and common issues documentation

    4. **Create File**:
       - Write the complete command file to commands/[command-name].md
       - Ensure all template sections are present and properly formatted
       - Validate file structure against template requirements
       - Apply proper markdown formatting and documentation structure
       - Remove all instruction comments

    5. **Validate Structure**:
       - Ensure all template sections are present and properly configured
       - Verify tool permissions and model settings are correctly applied
       - Check workflow references are valid and accessible
       - Validate command functionality and documentation completeness

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Path to created command file with review of successful creation
    - Tools and permissions configured with security validation
    - Workflow steps implemented with error handling review
    - Any configuration decisions made with justification and documentation

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Command creation completed with template application and validation'
    modifications: ['commands/[command-name].md']
    outputs:
      command_file: 'commands/[command-name].md'
      tools_configured: ['Bash', 'Edit', 'Read', ...]
      workflows_referenced: ['workflow1.md', 'workflow2.md', ...]
      model_configured: 'opus|sonnet|haiku'
      arguments_configured: true|false
      validation_passed: true|false
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (You)

**What You Do**:

1. **Check current task status** using TodoRead to verify execution progress
2. **Collect comprehensive report** from the command creation subagent
3. **Parse report status** and analyze results (success/failure/partial)
4. **Use TodoWrite** to update task status based on execution results
5. **Evaluate creation results**:
   - Check if command file was created successfully at correct location
   - Review tool permissions and security configurations applied
   - Verify workflow references are valid and properly implemented
   - Confirm all template sections are present and properly formatted
6. **Determine next action** based on comprehensive evaluation

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze creation report** from the command creation subagent
2. **Apply decision criteria**:
   - Verify command file was created successfully with all required content
   - Check template structure compliance and formatting standards
   - Confirm all required sections are present and properly configured
   - Validate tool permissions and security settings are appropriate
3. **Select next action**:
   - **PROCEED**: Command created successfully → Complete workflow and update indexes
   - **RETRY**: Creation failed with retriable issues → Create new assignment for failed aspects
   - **ROLLBACK**: Critical failures → Remove any partial files and report failure
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark task as 'completed' with success details
   - If RETRY: Add new todo item for retry with specific issues to address
   - If ROLLBACK: Mark task as 'failed' and add cleanup todos as needed
5. **Prepare transition**:
   - If PROCEED: Package command file and prepare for index updates
   - If RETRY: Generate retry assignment with same standards and specific fixes
   - If ROLLBACK: Identify cleanup actions needed and document failure reason

### Workflow Completion

**Report the workflow output as specified:**

```yaml
workflow: create-command
status: completed
outputs:
  command_file: 'commands/[command-name].md'
  configuration:
    tools_configured: ['Bash', 'Read', 'Write', 'Edit']
    model_configured: 'sonnet'
    workflows_referenced: ['workflow1.md', 'workflow2.md']
    arguments_structure: configured
  validation:
    template_compliance: passed
    security_permissions: verified
    workflow_references: accessible
    standards_compliance: passed
  integration:
    readme_updated: true
    system_integrated: true
    documentation_updated: true
summary: |
  Successfully created command '[command-name]' with complete configuration,
  tool permissions, and workflow references. Command is ready for use and
  properly integrated into the system.
```
