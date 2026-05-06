# Step 2B: Subagent Mode (fallback)

This reference is consulted when Step 1 (Mode Selection) does NOT detect Agent Teams in the session context. Otherwise use Team Mode (`references/team-mode.md`).

When Agent Teams are not available, execute the existing workflow:

## Planning & Discovery

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

## Execution with Parallel Subagents

1. **Template Validation**
   - Verify template:agent exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

2. **Delegation**
   - Create parallel specialized subagents (one per agent file) with:
     - Agent file path
     - All change specifications
     - Detailed instructions
     - Request to ultrathink

3. **Progress Monitoring**
   - Track completion status of each delegated agent
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates

## Verification

1. **Template Compliance Verification**
   - Verify each updated agent follows template:agent structure
   - Check all mandatory sections are present and properly formatted
   - Validate frontmatter and metadata consistency

2. **Change Application Verification**
   - Confirm all specified changes were applied correctly
   - Verify changes are reflected throughout the agent file
   - Check for any conflicting or contradictory specifications

3. **Personality Preservation Check**
   - Ensure unique agent characteristics remain intact
   - Verify collaboration networks are preserved
   - Confirm expertise areas unchanged (unless explicitly modified)
