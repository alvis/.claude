# Step 2A: Team Mode (Agent Teams enabled)

This reference is consulted when Step 1 (Mode Selection) detects `**Agent Teams**: enabled` in the session context. Otherwise use Subagent Mode (`references/subagent-mode.md`).

## Phase 1: Planning & Discovery (Lead)

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract:
     - Agent specifier (all, specific agent name, or pattern like `*frontend*`)
     - Change specifications (--changes parameter)
   - Validate agent files exist if specific agent specified
   - Count total agents if updating all

2. **Load Template Reference**
   - Read template:agent for latest agent structure
   - Identify template sections and required elements
   - Note any template updates since last agent refresh

3. **Locate Agents**
   - Discover all relevant agent files using Glob
   - Filter by specifier pattern if provided
   - Build list of agents to update

## Phase 2: Team Setup & Execution

1. **Create Team**
   - Use TeamCreate with name `update-agent-team`
   - Initialize agent pool registry to track active agents

2. **Template Validation**
   - Verify template:agent exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

3. **Spawn Agent Update Specialists**
   - Spawn specialized teammates (one per agent file) via Task tool with:
     - `team_name: "update-agent-team"`
     - `name: "updater-{N}"` (sequential naming)
     - `model: "opus"`
     - `agent_type: "general-purpose"`

4. **Create and Assign Tasks**
   - TaskCreate per agent file with full instructions including:
     - Agent file path
     - Template reference path (template:agent)
     - All change specifications from arguments
     - Detailed instructions for applying updates
   - TaskUpdate to set owner per teammate

## Phase 3: Work Cycle

1. **Agent Update Task Specification**

   Each Agent Update Specialist receives:

   >>>
   **ultrathink: adopt the Agent Update Specialist mindset**

   - You're an **Agent Update Specialist** with deep expertise in agent configuration who follows these principles:
     - **Template-First Approach**: Always compare against template before modification
     - **Personality Preservation**: Maintain unique agent characteristics and voice
     - **Structural Integrity**: Align with template structure while preserving customizations
     - **Professional Polish**: Deliver clean, consistent agent definitions

   <IMPORTANT>
     You've to perform the task yourself. You CANNOT further delegate the work to another subagent
   </IMPORTANT>

   **Assignment**
   You're assigned to update agent: [agent name]

   **Agent Specifications**:
   - **Agent File**: [agent file path]
   - **Template**: template:agent
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Agent**:
      - Read the agent file completely
      - Identify unique personality traits, expertise, and collaboration networks
      - Note any custom sections or configurations

   2. **Compare with Template**:
      - Read template:agent for current structure
      - Identify missing sections from template
      - Identify sections that need structural updates
      - Map changes to specific template sections

   3. **Apply Updates**:
      - Add any missing required sections from template
      - Update section formatting to match template
      - Apply specified changes from --changes parameter
      - Preserve all unique agent characteristics
      - Maintain collaboration networks and tool permissions

   4. **Clean & Finalize**:
      - Remove any outdated or deprecated sections
      - Ensure consistent formatting throughout
      - Verify agent definition is complete and valid

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens) via SendMessage to team-lead:

   ```yaml
   status: success|failure|partial
   agent: '[agent-name]'
   summary: 'Brief description of changes applied'
   modifications:
     - section: '[section name]'
       change: '[what was changed]'
   template_compliance: true|false
   personality_preserved: true|false
   context_level: '[calculated %]'  # (input_tokens / context_window_size) from real usage data
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```

   <<<

2. **Progress Monitoring**
   - Track completion status of each delegated agent file
   - Handle any teammate failures or escalations
   - Ensure constitutional compliance in all updates

## Phase 4: Aggregation & Cleanup

1. **Collect Results**
   - Use TaskGet to retrieve completion reports from all tasks
   - Aggregate results into final summary

2. **Shutdown Teammates**
   - Send shutdown requests to all teammates via SendMessage
   - Wait for shutdown acknowledgments

3. **Delete Team**
   - Use TeamDelete to clean up team resources
   - Proceed to Reporting

## Agent Summary

| Agent Type | Model | Role | Lifecycle |
|------------|-------|------|-----------|
| Agent Update Specialist | opus | Updates agent files with template alignment and changes | One per agent file; spawned for Phase 3, retired in Phase 4 |
