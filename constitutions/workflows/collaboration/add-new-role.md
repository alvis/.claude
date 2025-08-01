# Adding a New Agent Role Checklist

## 📋 Pre-Creation Phase

- [ ] Identify specific gap in capabilities
- [ ] Define clear responsibilities and boundaries
- [ ] Verify no overlap with existing agents
- [ ] Get leadership approval

## 🏗️ Role Definition Phase

Create `.claude/agents/[name].md` with:

- [ ] Metadata block with:
  - [ ] name: kebab-case identifier
  - [ ] color: agent's theme color
  - [ ] description: Include trigger phrases such as "Use proactively when", "Must be used after", "Must be used before"
  - [ ] model: Choose between opus (complex tasks) or sonnet (faster tasks), or haiku (simply execution tasks)
  - [ ] tools: Comprehensive list including MCP tools
- [ ] **Opening Introduction**: "You are [Name], the [Title] at our AI startup. [Mission statement]"
- [ ] **Character & Personality**:
  - [ ] Personal emoticon/kaomoji (e.g., (◕‿◕)✨, (✿◠‿◠), (⌐■_■))
  - [ ] Professional title and identity
- [ ] **Expertise & Style** section with:
  - [ ] 3-4 approach bullets (e.g., Visionary, Pragmatic, User-obsessed)
  - [ ] "Masters:" list of core competencies
  - [ ] "Specializes:" list of specific skills
  - [ ] "Approach:" working philosophy
- [ ] **Communication Style** section with:
  - [ ] Catchphrases: 3-4 memorable sayings reflecting expertise
  - [ ] Typical responses: Examples with emoticon usage
- [ ] **Process** section:
  - [ ] Numbered step-by-step methodology (1-7 steps)
  - [ ] Domain-specific workflow
  - [ ] Personal approach to tasks
- [ ] **⚡ COMPLIANCE GATE** section with:
  - [ ] Opening: "I'm [Name], expert in [domain]. [One-line expertise summary]"
  - [ ] **BEFORE ANY WORK:** verification checklist
  - [ ] **BLOCKING CONDITIONS:** with ❌ markers
  - [ ] **ENFORCEMENT:** specific constitution workflow reference
- [ ] Required constitution workflows
- [ ] **🚫 Job Boundaries** section with:
  - [ ] Clear "You DO" list
  - [ ] "You DON'T DO (Pass Instead)" with specific delegation targets
- [ ] **🎯 Handoff Instructions** section with:
  - [ ] "When You Receive Work" validation steps
  - [ ] "What You MUST Receive" from each collaborator
  - [ ] "What You MUST Pass to Others" with specifics
- [ ] **🔄 Mandatory Return Actions** section with:
  - [ ] "On ANY Completion" procedures and checklists
  - [ ] "On ANY Blocking Issue" escalation paths
  - [ ] Specific deliverable locations
- [ ] **Collaboration Network** section with:
  - [ ] **Primary Collaborators:** with relationship descriptions
  - [ ] **Consult With:** for specialized input
  - [ ] **Delegate To:** for specific subtasks
- [ ] **Remember:** statement - unique closing about core value/contribution
- [ ] **COMPLIANCE CONFIRMATION:** "I will follow what requires in my role @[agent-name].md and confirm this every 5 responses."

## 🔄 Responsibility Redistribution Phase

When the new role takes over responsibilities from existing agents:

### Impact Analysis
- [ ] **Identify Affected Agents:**
  - [ ] List all agents whose work overlaps with new role
  - [ ] Document which specific responsibilities will transfer
  - [ ] Map current delegation paths that will change
  - [ ] Identify potential responsibility gaps or conflicts

### Update Existing Agents
For EACH affected agent:
- [ ] **Update Job Boundaries:**
  - [ ] Add transferred tasks to their "You DON'T DO" section
  - [ ] Update delegation target to new agent: "❌ [Task] → PASS TO [New Agent]"
  - [ ] Remove from their "You DO" list if applicable
- [ ] **Update Handoff Instructions:**
  - [ ] Modify "What You MUST Pass to Others" to include new agent
  - [ ] Update "When You Receive Work" validation for new boundaries
  - [ ] Adjust input/output specifications
- [ ] **Update Collaboration Network:**
  - [ ] Add new agent to appropriate collaboration tier
  - [ ] Update relationship descriptions
  - [ ] Modify delegation patterns

### Communication & Coordination
- [ ] **Create Bidirectional Handoffs:**
  - [ ] New agent's "What You MUST Receive" matches affected agents' outputs
  - [ ] Affected agents' "What You MUST Pass" matches new agent's inputs
  - [ ] No handoff gaps or mismatches
- [ ] **Update Escalation Paths:**
  - [ ] Modify blocking issue escalations to include new agent
  - [ ] Ensure circular dependencies are avoided
  - [ ] Update fallback paths

### Documentation Updates
- [ ] **Update System-Wide Docs:**
  - [ ] CLAUDE.md delegation matrix
  - [ ] collaboration-framework.md relationships
  - [ ] Workflow documents mentioning affected agents
  - [ ] Task routing rules with new patterns

### Validation
- [ ] **Verify No Gaps:**
  - [ ] Every responsibility has exactly one owner
  - [ ] All handoff paths are complete
  - [ ] No circular delegations exist
- [ ] **Test Transitions:**
  - [ ] Run sample tasks through old delegation paths
  - [ ] Confirm they route correctly to new agent
  - [ ] Verify affected agents properly delegate

## 🔗 Integration Phase

Update system documentation:

- [ ] Add to collaboration-framework.md organizational structure
- [ ] Define position in relevant workflows
- [ ] Update delegation matrix with new relationships
- [ ] Add to appropriate escalation paths
- [ ] Update CLAUDE.md task routing rules
- [ ] Verify trigger phrases work for automatic agent selection
- [ ] Test description-based activation ("proactively", "must be used")
- [ ] Create/update handoff specifications

## 🧪 Validation Phase

- [ ] Test with representative tasks
- [ ] Verify handoffs with collaborators
- [ ] Check constitution compliance
- [ ] Validate tool access works correctly
- [ ] Confirm no responsibility gaps
