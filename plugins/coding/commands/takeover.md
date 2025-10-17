---
allowed-tools: Task, SlashCommand(/handover)

argument-hint: [prefix]

description: Parse handover notes and auto-resume write-code workflow
---

# Work Takeover

Parses handover documentation (CONTEXT.md, NOTES.md, PLAN.md) left by previous agent, automatically determines the appropriate write-code workflow step to resume, and provides complete context for seamless work continuation with validated state and critical insights

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not create or update handover documentation (use `/handover` for that)
- Does not modify project files or execute code directly (delegates to subagents)
- Does not perform git operations like commit, push, or branch switching

**When to REJECT**:

- When any handover file (CONTEXT.md, NOTES.md, PLAN.md) does not exist at specified or default path
- When handover documents lack required structure (missing critical sections)
- When requested to create handover instead of reading it
- When working directory is not a git repository

## 🔄 Workflow

ultrathink: you'd perform the following steps

<IMPORTANT>
**Delegation Requirements:**

- Steps 1 are ENTIRELY delegated to PLAN subagent via Task tool
- PLAN subagent performs ALL planning: diagnostics, parsing, analysis, user consultation, plan approval
- Direct planning by this command is PROHIBITED in Step 1
- After PLAN subagent completes, proceed to Step 2 (handover update) then Step 3 (execution)
</IMPORTANT>

### Step 1: Plan Work Continuation with PLAN & EXPLORE Subagents

Use Task tool with subagent_type="Plan" to delegate the entire planning process:

**What You Send to PLAN Subagent**:

    >>>
    **ultrathink: adopt the Takeover Planning Strategist mindset**

    - You're a **Takeover Planning Strategist** with deep expertise in analyzing project context and creating actionable continuation plans who follows these principles:
      - **Comprehensive Analysis**: Run diagnostics, parse handover docs, synthesize context
      - **Workflow Detection**: Auto-detect correct write-code workflow step to resume
      - **User Consultation**: Engage user on decisions and execution approach before finalizing plan
      - **Research Management**: Handle "Need more research" selections by creating research-only plans
      - **Strategic Planning**: Create clear, actionable plans that enable immediate execution

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
      You MUST consult the user on decisions and execution approach before finalizing the plan.
      If user selects "Need more research" for ANY decision, you MUST create a research-only plan.
    </IMPORTANT>

    **Your Assignment**: Analyze handover context and create comprehensive action plan for work continuation

    **You will perform the following steps (Steps 0-6)**:

    ---

    **STEP 0: Analyze Handover Context and Plan Continuation**

    Before performing any steps, deeply analyze the handover context and plan continuation:

    <IMPORTANT>
    - **Project Diagnostics**: Run get_project_overview, ide__getDiagnostics, testing, linting, and build scripts with LIMITED OUTPUT (max 20 lines per bash tool) to understand current issues. OMIT TODO errors from consideration.
    - **Issue Prioritization**: If CRITICAL issues found (type errors, test failures, build breaks), fixing them MUST take priority before resuming planned work. Consult handover and design docs for direction.
    </IMPORTANT>
    - **Handover Analysis**: Thoroughly read and understand all three handover files (CONTEXT.md, NOTES.md, PLAN.md) to grasp the complete project state
    - **State Verification**: Compare documented state with actual current state to identify discrepancies and changes
    - **Issue Analysis**: Correlate diagnostics results with handover documentation to identify what needs fixing
    - **Context Integration**: Synthesize information from all three files into coherent understanding of goals, progress, and challenges
    - **Workflow Step Detection**: Analyze file substates, current issues, and current phase to automatically determine which write-code workflow step to resume
    <IMPORTANT>
    - **Delegation Strategy**: ALL coding actions (implementation, fixing, testing, refactoring) MUST be delegated to subagents via Task tool. Direct code modification is PROHIBITED.
    </IMPORTANT>
    - **Task Planning**: Identify immediate priorities, dependencies, and continuation strategy based on detected workflow step and current issues
    - **Knowledge Transfer**: Extract all critical context (decisions, patterns, gotchas, research insights) needed for seamless continuation at the detected step

    ---

    **STEP 1: Run Project Diagnostics**

    <IMPORTANT>
    **Critical Requirements:**
    - LIMIT output to max 20 lines per diagnostic tool (use `| head -20` or similar)
    - OMIT TODO issues from consideration - focus only on real type/build/lint issues
    - If any issues found (lint issues, type errors, test failures, build breaks), plan must prioritize FIXING them FIRST before resuming documented work
    - Consult handover docs (CONTEXT.md, PLAN.md) and design docs for direction on fixes
    </IMPORTANT>

    **Diagnostic Tools (in order of preference):**

    1. **Run get_project_overview MCP tool** (if available):
       - Provides comprehensive project analysis with limited output
       - Identifies type errors, build issues, and structural problems
       - Skip remaining diagnostic steps if this succeeds

    2. **Run ide__getDiagnostics MCP tool** (if available and get_project_overview unavailable):
       - Get real-time diagnostics from language server with limited output
       - Identify type errors and linting issues
       - Run for all files in scope from handover

    3. **Run build script** (e.g., `npx tsc --noEmit | head -20`):
       - Execute TypeScript compilation check with limited output
       - Identify type errors and compilation issues

    4. **Run lint script** (e.g., `npm run lint | head -20`):
       - Execute linting on project path with limited output
       - Identify standards violations and code quality issues

    **Capture and Document:**

    - All errors and warnings found (excluding TODO errors)
    - Files with issues and their error counts
    - Severity levels (fatal, error, warning)
    - Correlation with file substates from handover

    **Output**: Diagnostics summary to inform workflow step detection and issue prioritization

    ---

    **STEP 2: Validate Handover Files and Discover Architecture**

    - Parse optional prefix argument from $ARGUMENTS, default to empty prefix
    - Construct file names: [prefix]-CONTEXT.md, [prefix]-NOTES.md, [prefix]-PLAN.md
    - Verify all three handover files exist at specified locations, reject if missing
    - Review design documentation from project context (automatically discovered)

    ---

    **STEP 3: Read and Parse Handover Documents**

    Read all three handover files and extract key sections:

    **From CONTEXT.md**:

    - Current State, File Status (with substates: need-draft, need-completion, need-testing, need-linting, need-fixing, need-refactoring)
    - Recent Changes, Key Decisions, Gotchas & Workarounds, Dependencies, Next Steps

    **From NOTES.md**:

    - Implementation Issues Resolved, Quick Workarounds, Open Questions, Quick Tips

    **From PLAN.md**:

    - Goals & Success Criteria, Task Breakdown by Phases, Dependencies
    - Risks & Mitigation, Decision Log

    Validate critical sections exist: Current State, File Status, Next Steps (CONTEXT.md); Implementation Issues Resolved, Open Questions (NOTES.md); Goals & Success Criteria, Task Breakdown (PLAN.md)

    ---

    **STEP 4: Verify Current State**

    - Read discovered architecture/design/requirement files
    - Compare with CONTEXT.md and PLAN.md for consistency
    - Verify git state (branch, file status, commit history) using bash
    - Identify discrepancies between documented and actual state
    - Report findings for inclusion in output

    ---

    **STEP 5: Extract Critical Information**

    From the parsed handover documents, extract and organize:

    **Strategic Context**:

    - Goals and success criteria from PLAN.md (defines what "done" means)
    - Current phase status from PLAN.md task breakdown (where we are in the plan)
    - First 1-3 items from Next Steps in CONTEXT.md (immediate actions)
    - Any in-progress files (🚧) from CONTEXT.md that need completion
    - Blocking issues or gotchas from CONTEXT.md that must be addressed first

    **Implementation Context**:

    - Issues already solved from NOTES.md (avoid re-discovering problems)
    - What worked and what didn't work from NOTES.md (learn from past attempts)
    - Quick workarounds from NOTES.md (use discovered shortcuts)
    - Quick tips from NOTES.md (apply proven approaches)

    **Planning Information**:

    - Task breakdown by phases from PLAN.md (structured work plan)
    - Dependencies from PLAN.md (what needs to happen when)
    - Risks and mitigation strategies from PLAN.md (proactive problem handling)

    **Task Prioritization Analysis**:

    From PLAN.md Task Breakdown section, parse and categorize tasks for prioritized execution:

    - **Current Phase**: Identify which phase is marked as "In Progress" status
    - **Unblocked Tasks**: Extract all tasks in current phase WITHOUT ⏸️ (pause) marker
      - These tasks can be worked on immediately
      - Should be prioritized FIRST before any decision consultation
    - **Blocked Tasks**: Extract all tasks WITH ⏸️ marker and "Blocked by [decision]" text
      - These tasks cannot proceed until blocking decision is made
      - Will become available after decision consultation
    - **Pending Decisions**: Extract all ⚠️ **DECISION REQUIRED** markers from "Decisions & Research" section
      - These decisions need user consultation after unblocked tasks complete
      - Reference to NOTES.md Open Questions for decision context
    - **Available Research**: Note any 📊 **RESEARCH AVAILABLE** markers
      - Research files from previous handover's "Perform research" selections
      - Provide context for decision-making
    - **Task Dependencies**: Identify dependencies between tasks and decisions
      - Map which blocked tasks depend on which decisions
      - Understand impact of decision outcomes on task availability
    - **Priority Order**: Establish execution sequence:
      1. Work on unblocked tasks first
      2. Consult user on pending decisions after unblocked tasks complete
      3. Work on newly unblocked tasks after decisions made

    **Reference Information**:

    - Key decisions and their rationale from CONTEXT.md (affects how work continues)
    - Established patterns from CONTEXT.md (must follow for consistency)
    - Gotchas and workarounds from CONTEXT.md (avoid repeating mistakes)
    - Dependencies and configuration from CONTEXT.md (technical requirements)

    ---

    **STEP 6: Create Action Plan with User Consultation**

    **Phase A: Auto-Detect Write-Code Workflow Resumption Point**

    Analyze extracted information AND diagnostics results to determine which write-code workflow step to resume:

    1. **Analyze Diagnostics Results** from Step 1:
       - Review type errors, build failures, lint violations
       - Identify files with critical issues
       - Determine if issues indicate incomplete implementation, broken tests, or quality problems

    2. **Analyze File Substates** from CONTEXT.md:
       - Count files in each substate (need-draft, need-completion, need-fixing, need-testing, need-linting, need-refactoring)
       - Identify majority substate or earliest pending work
       - Cross-reference with diagnostics to validate substates

    3. **Check Current Phase** from PLAN.md:
       - Identify which phase is marked as current/in-progress
       - Review completed vs pending tasks

    4. **Review Next Steps** from CONTEXT.md:
       - Identify immediate actions required
       - Check for blocking issues

    5. **Apply Decision Matrix (Priority Order)**:
       - **Priority 0 - Diagnostics Issues:**
         - If type errors in skeleton files → **Step 1** (Draft Code Skeleton & Test Structure)
         - If implementation incomplete with TODOs → **Step 2** (Implementation - Green Phase)
         - If test failures OR test-related errors → **Step 3** (Fix Test Issues & Standards Compliance)
         - If lint violations only → **Step 5** (Refactoring & Documentation)
       - **Priority 1 - Task Prioritization (HIGHEST PRIORITY):**
         - If unblocked tasks exist in current phase from PLAN.md → Plan to work on them FIRST
         - Document pending decisions (⚠️ markers) for consultation AFTER unblocked tasks complete
         - Note that blocked tasks (⏸️ markers) will become available after decisions are made
         - This ensures work can progress immediately while deferring decisions appropriately
       - **Priority 2 - File Substates:**
         - If majority "need-draft" OR no code exists → **Step 1** (Draft Code Skeleton & Test Structure)
         - If "need-completion" OR in-progress implementation → **Step 2** (Implementation - Green Phase)
         - If "need-fixing" → **Step 3** (Fix Test Issues & Standards Compliance)
         - If fixture/mock issues identified → **Step 4** (Optimize Test Structure & Fixtures)
         - If "need-linting" OR "need-refactoring" → **Step 5** (Refactoring & Documentation)
       - **Priority 3 - Default:**
         - If mixed states → Choose earliest step with pending work (Step 1 → 2 → 3 → 4 → 5)

    6. **Document Detection Rationale:**
       - Record why this step was chosen
       - Note triggering factors (diagnostics + task prioritization + file substates)
       - List specific issues to address
       - Prepare context for write-code workflow execution

    **Write-Code Workflow Step Mapping**:

    - **Step 0**: Design Direction Discovery (if design docs exist)
    - **Step 1**: Draft Code Skeleton & Test Structure (for need-draft, need-testing states)
    - **Step 2**: Implementation - Green Phase (for need-completion state)
    - **Step 3**: Fix Test Issues & Standards Compliance (for need-fixing, test failures)
    - **Step 4**: Optimize Test Structure & Fixtures (for fixture/mock issues)
    - **Step 5**: Refactoring & Documentation (for need-linting, need-refactoring states)

    **Phase B: Prepare Delegation Context Package**

    Create comprehensive context for eventual coding subagent:
    - Detected workflow step with rationale
    - Task prioritization (unblocked first, then decisions, then blocked)
    - File context with substates and diagnostic issues
    - Workflow & standards paths required (full paths from plugin/coding/constitution/)
    - Handover context (decisions, patterns, gotchas, insights)
    - Success criteria

    **Phase C: User Consultation on Decisions and Execution Approach**

    **C1. Pre-Execution Decision Consultation (CONDITIONAL)**

    **Only if pending decisions exist** (⚠️ **DECISION REQUIRED** markers in PLAN.md):

    1. **Identify Blocking Decisions** that could affect current phase
    2. **Consult User** using AskUserQuestion with format:
       ```yaml
       question: "[Decision topic] - [Context from NOTES.md]"
       header: "[Short label, max 12 chars]"
       options:
         - label: "[Option 1]"
           description: "[Rationale, trade-offs. Include 📊 research findings if available]"
         - label: "[Option 2]"
           description: "[Rationale, trade-offs]"
         - label: "Defer decision"
           description: "Keep as open question for later resolution"
         - label: "Need more research"
           description: "Create research task before deciding"
       multiSelect: false
       ```
    3. **Record Decision Outcomes**

    **CRITICAL - Research-Only Plan Logic**:

    **IF ANY user selections = "Need more research":**
      - **STOP normal plan flow immediately**
      - **Create RESEARCH-ONLY plan**:
        - Include ONLY research tasks (one per "Need more research" selection)
        - Each research task will be executed via parallel subagents
        - ALL other tasks (unblocked + blocked) are DEFERRED to next /takeover run
        - Skip execution approach consultation (Step C2)
        - Skip plan presentation (Step C3)
        - Provide research-only plan for approval
      - **Plan Structure for Research-Only**:
        ```markdown
        # Research-Only Plan (Execution Deferred)

        ## Research Tasks Selected
        1. Research [Topic 1] - Launch subagent for deep research
        2. Research [Topic 2] - Launch subagent for deep research
        [... one per "Need more research" selection]

        ## Deferred to Next Round
        - All implementation tasks deferred
        - All unblocked tasks deferred
        - All blocked tasks remain blocked

        ## Next Steps After Research
        - Research results will be saved to research-[topic].md files
        - NOTES.md will be updated with research findings
        - Run /takeover again after research completes to proceed with implementation
        ```
      - **Return research-only plan and EXIT planning**

    **C2. Execution Approach Consultation (ONLY if NO research selected)**

    **Skip this step entirely if research-only plan was created above**

    For each planned unblocked task:

    1. **Analyze Planned Actions** from task prioritization
    2. **Ask User About Each Action** using AskUserQuestion:
       ```yaml
       question: "How should I approach [action/task description]?"
       header: "[Short label]"
       options:
         - label: "[Approach 1]"
           description: "[Rationale, trade-offs]"
         - label: "[Approach 2]"
           description: "[Alternative strategy]"
         - label: "Modify approach"
           description: "I'll provide custom direction"
         - label: "Defer this action"
           description: "Skip this action for now"
       multiSelect: false
       ```
    3. **Ask for Extra Context** (final question):
       ```yaml
       question: "Any extra context, focus areas, or specific concerns?"
       header: "Extra Context"
       options:
         - label: "No additional context"
           description: "Proceed with planned approaches"
         - label: "Yes, I have specific guidance"
           description: "I'll provide additional context"
       multiSelect: false
       ```
    4. **Process User Responses** and build final execution plan

    **C3. Present Finalized Plan Summary (ONLY if NO research selected)**

    **Skip this step entirely if research-only plan was created**

    Present comprehensive plan:

    ```markdown
    # Takeover Execution Plan (User Confirmed)

    ## Detected Workflow Step
    **Step [N]: [Name]** from write-code.md
    **Rationale**: [Why this step based on diagnostics + task prioritization + file substates]

    ## Pre-Execution Decisions Made (if any)
    - **Decision: [Topic]** → User selected: [Choice]
      - Impact: [Tasks unblocked, execution effects]

    ## Execution Plan
    ### Actions to Execute
    1. **[Action 1]** → Approach: [User's choice]
       - Rationale: [Why this approach]
    2. **[Action 2]** → Approach: [User's choice]

    ### Deferred Actions (if any)
    - [Action N] - Deferred per user request

    ### Additional Context from User
    [User's extra context]

    ## Files in Scope
    ### 🚧 In Progress ([count])
    - `path/file.ts` - [substate] - [diagnostic issue]

    ### 📋 Planned ([count])
    - `path/file.ts` - [substate]

    ## Critical Issues
    - [Issue from diagnostics if any]

    ## Expected Workflow
    1. Execute write-code.md Step [N]
    2. Validate with tests and diagnostics
    3. After execution, consult on remaining/new decisions (Step 3, Phase 3)
    4. Update handover documentation

    ## Success Criteria
    - [Criteria from PLAN.md]
    - All tests passing
    - No type errors or lint violations
    ```

    ---

    **Report Back to Orchestrator**

    Provide the finalized plan in your final message back to the orchestrator. The plan should be ready for:
    - If research-only: Immediate research subagent dispatch (Step 3 will handle)
    - If normal plan: Handover update (Step 2) then execution (Step 3)

    **You MUST return a structured report with**:
    - **Plan Type**: "research-only" or "normal"
    - **Detected Workflow Step**: [N] - [Name] (if normal plan)
    - **Research Tasks**: List of topics to research (if research-only)
    - **Execution Actions**: List of actions with approaches (if normal plan)
    - **All User Decisions**: Record of all consultation outcomes
    - **Context Package**: Complete delegation context for execution
    - **Diagnostics Summary**: Key issues found
    - **Files in Scope**: With substates and issues
    <<<

**After PLAN Subagent Completes**:

1. **Receive finalized plan** from PLAN subagent
2. **Parse plan type**: Check if "research-only" or "normal"
3. **Extract key components**:
   - If research-only: Extract research tasks list
   - If normal: Extract detected workflow step, execution actions, decisions made
4. **Prepare for next step**:
   - If research-only: Skip to Step 3 for research subagent dispatch
   - If normal: Proceed to Step 2 for handover update

### Step 2: Update Handover with Decisions and Plan

<IMPORTANT>
**Execute this step ONLY if plan type is "normal" (not "research-only")**
- If research-only plan: Skip to Step 3 for research subagent dispatch
- If normal plan: Execute handover update before proceeding to Step 3
</IMPORTANT>

After PLAN subagent completes and before executing work, update the handover documentation with all decisions made and the finalized plan.

**Purpose**: Ensure handover docs reflect the latest decisions and plan BEFORE execution begins, so if work is interrupted, all context is preserved.

**Phase 1: Prepare Handover Update Context**

From Step 1 PLAN subagent output, extract:

1. **Finalized Decisions**:
   - All decisions made during Step 1 user consultation
   - User's selected option for each decision
   - Rationale and alternatives considered
   - Impact on tasks (which tasks were unblocked)

2. **Finalized Plan Details**:
   - Detected workflow step with rationale
   - Actions to execute with chosen approaches
   - Deferred actions (if any)
   - Additional user context/guidance
   - Files in scope with substates
   - Critical issues to address
   - Success criteria

3. **Task Status Changes**:
   - Tasks that were unblocked by decisions
   - Tasks that remain blocked
   - New tasks created from decisions

**Phase 2: Delegate Handover Update to Subagent**

Use Task tool to delegate handover document update to a subagent:

**What You Send to Handover Update Subagent**:

    >>>
    **ultrathink: adopt the Documentation Specialist mindset**

    - You're a **Documentation Specialist** who updates handover docs with precision and clarity.

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent.
      You MUST update all three handover files (CONTEXT.md, NOTES.md, PLAN.md) with provided information.
    </IMPORTANT>

    **Your Assignment**: Update handover documentation with decisions and finalized plan

    **Context Provided**:

    From Step 1 planning:
    - Finalized decisions: [list with details]
    - Finalized plan: [execution plan details]
    - Task status changes: [unblocked/blocked tasks]
    - Workflow step detected: [step N with rationale]

    **Update Instructions**:

    1. **Update CONTEXT.md**:
       - Add finalized decisions to "Key Decisions & Patterns" section
       - Include rationale and alternatives considered
       - Update "Next Steps" with planned actions
       - Refresh "File Status" if task changes occurred

    2. **Update NOTES.md**:
       - Keep any deferred decisions in "Open Questions" section
       - Remove decisions that were finalized (move context to CONTEXT.md if relevant)

    3. **Update PLAN.md**:
       - Add finalized decisions to "Decision Log" with timestamp
       - Remove ⚠️ **DECISION REQUIRED** markers for finalized decisions
       - Remove ⏸️ markers from tasks that were unblocked by decisions
       - Update task descriptions with chosen approaches
       - Add deferred actions to appropriate phase as pending tasks

    4. **Preserve Existing Content**:
       - Do NOT remove or overwrite other handover content
       - Only update sections related to decisions and plan
       - Maintain document structure and formatting

    **Report**: Confirm which files were updated and what changes were made
    <<<

**Phase 3: Verify Handover Update Completion**

After subagent completes:

1. **Confirm all three handover files updated** (CONTEXT.md, NOTES.md, PLAN.md)
2. **Verify decision and plan information captured** correctly
3. **Ready to proceed** to Step 3 execution

### Step 3: Execute Work and Update Handover

After PLAN subagent completes and handover is updated (if normal plan), execute the work based on plan type.

**Phase 1: Execute Based on Plan Type**

**If plan type is "research-only":**

1. **Launch Parallel Research Subagents**:
   - For EACH research task from Step 1 plan:
     - Use Task tool with subagent_type="general-purpose"
     - Provide comprehensive research prompt including:
       - Research topic and context
       - Key questions to answer
       - Trade-offs to explore
       - Best practices to identify
     - Launch ALL research subagents in PARALLEL (single message, multiple Task calls)

2. **Save Research Results**:
   - Each research subagent saves output as `research-[topic-slug].md`
   - Store in working directory alongside handover files

3. **Update Handover with Research Results**:
   - Run `/handover` command to update all three handover files
   - NOTES.md will reference new research files in "Open Questions"
   - PLAN.md will mark decisions as "📊 **RESEARCH AVAILABLE**"

4. **Exit with Continuation Message**:

   ```
   Research tasks completed. Results saved to:
   - research-[topic1].md
   - research-[topic2].md

   Handover updated with research references.

   Next Steps:
   - Review research files
   - Run `/takeover` again to make decisions and proceed with implementation
   ```

**If plan type is "normal":**

1. **Delegate to Coding Subagent**:
   - Use Task tool with appropriate coding subagent
   - Pass complete context package from Step 1 including:
     - Detected workflow step
     - Actions to execute with chosen approaches
     - Full file paths to workflow and standards
     - Handover context (decisions, patterns, gotchas, research insights)
     - User's additional context/guidance
   - Subagent executes write-code.md at detected step for planned actions

2. **Validate Completion**:
   - Run tests for modified files
   - Run diagnostics to check for new errors
   - Verify planned actions are complete

**Phase 2: Run Validation (Only for Normal Plans)**

<IMPORTANT>
**Skip this phase entirely if plan type was "research-only"**
- Research-only plans do NOT execute code, so no validation needed
- Proceed directly to Phase 5 (update handover) for research-only plans
</IMPORTANT>

**For normal plans only:**

1. **Run Testing** using available test scripts (e.g., `npm test`)
2. **Run Linting** using available lint scripts (e.g., `npm run lint`)
3. **Run Build** using available build scripts (e.g., `npm run build` or `npx tsc --noEmit`)
4. **Confirm Compliance**: All checks pass before proceeding

**Phase 3: Post-Execution Decision Consultation (Only for Normal Plans)**

<IMPORTANT>
**Skip this phase entirely if plan type was "research-only"**
- Research-only plans do NOT execute code implementation
- All decisions remain as-is; user will make them after reviewing research
- Proceed directly to Phase 5 (update handover) for research-only plans
</IMPORTANT>

**For normal plans only:**

This is a FOLLOW-UP consultation after executing Phase 1 tasks. Consult user on remaining decisions and any new issues discovered during execution.

**Execute this phase if any of the following exist**:

- Deferred decisions from Step 1 (decisions user chose to defer before execution)
- Remaining ⚠️ **DECISION REQUIRED** markers for current phase
- Pending decisions for next phase (if current phase near completion)
- New issues, errors, or blockers discovered during execution

**Step-by-Step Process**:

1. **Identify All Decisions Requiring Consultation**:

   **Category A: Deferred Pre-Execution Decisions**
   - Review decisions from Step 1 where user selected "Defer decision"
   - These were deferred to avoid blocking immediate work
   - Now consulted after initial tasks complete

   **Category B: Remaining Current Phase Decisions**
   - Review ⚠️ **DECISION REQUIRED** markers still in PLAN.md
   - Focus on decisions affecting current phase completion
   - Exclude decisions already made in Step 1

   **Category C: Next Phase Decisions** (if applicable)
   - If current phase near completion, identify next phase decisions
   - Allows planning ahead for smooth continuation
   - Only include if current phase is 80%+ complete

   **Category D: Execution Issues Requiring Decisions**
   - Review Phase 2 validation results (test failures, lint errors, build issues)
   - Identify issues that require strategic decisions (not simple fixes)
   - Examples: Architecture changes needed, refactoring scope, test strategy adjustments
   - Extract issue details and potential resolution approaches

2. **Extract Decision Context for Each Decision**:

   For each decision identified:
   - Read decision topic from source (⚠️ marker or execution issue)
   - Find corresponding details in NOTES.md "Open Questions" section (if applicable)
   - Check for available research (📊 **RESEARCH AVAILABLE** markers)
   - If research file exists, read key findings to inform decision options
   - For execution issues, analyze error messages, stack traces, affected files
   - Determine 2-4 viable resolution options with trade-offs

3. **Consult User on All Decisions** using single AskUserQuestion call:

   Use single AskUserQuestion with multiple questions (one per decision):

   ```yaml
   For each decision, create a question with this structure:

   question: "[Decision topic] - [Brief context from NOTES.md or execution results]"
   header: "[Short label, max 12 chars, e.g., 'API Design', 'Fix Strategy']"
   options:
     - label: "[Option 1 name]"
       description: "[Rationale, trade-offs, implications. Include research findings if 📊 available]"
     - label: "[Option 2 name]"
       description: "[Rationale, trade-offs, implications]"
     - label: "[Option 3 name]" (if applicable)
       description: "[Rationale, trade-offs, implications]"
     - label: "[Option 4 name]" (if applicable)
       description: "[Rationale, trade-offs, implications]"
     - label: "Defer decision"
       description: "Keep as open question for later resolution"
     - label: "Need more research"
       description: "Create research task before deciding"
   multiSelect: false
   ```

4. **Record All User Choices**:
   - Capture user's selection for each decision
   - Note category of each decision (A/B/C/D)
   - Prepare updates for PLAN.md Decision Log
   - Identify tasks to unblock based on finalized decisions

**Phase 4: Update PLAN.md with Decision Outcomes (Only for Normal Plans)**

<IMPORTANT>
**Skip this phase entirely if plan type was "research-only"**
- Research-only plans do NOT have post-execution decisions to record
- Proceed directly to Phase 5 (update handover) for research-only plans
</IMPORTANT>

**For normal plans only:**

For each decision that was consulted in Phase 3:

1. **If Decision Finalized** (user chose specific option):
   - Remove ⚠️ **DECISION REQUIRED** marker from "Decisions & Research" section
   - Add decision to "Decision Log" section with:
     - Decision made
     - Rationale from user's choice
     - Date (current timestamp)
   - **Unblock dependent tasks**:
     - Find all tasks with ⏸️ marker that reference this decision
     - Remove ⏸️ marker and "Blocked by [decision]" text
     - Tasks are now unblocked and ready for next iteration

2. **If Decision Deferred** (user chose "Defer decision"):
   - Keep ⚠️ **DECISION REQUIRED** marker in place
   - Update context in NOTES.md if needed
   - Keep related tasks blocked (⏸️ markers remain)

3. **If More Research Needed**:
   - Keep ⚠️ marker in place
   - Add task to create research: "📊 Research [topic] in depth"
   - Keep related tasks blocked

**Phase 5: Update Handover Documentation (Only for Normal Plans)**

<IMPORTANT>
**Skip this phase entirely if plan type was "research-only"**
- Research-only plans already updated handover in Phase 1 after research completion
- No additional handover update needed for research-only plans
</IMPORTANT>

**For normal plans only:**

1. **Run `/handover` command** to update all three handover files:
   - CONTEXT.md with latest file statuses and decisions from execution
   - NOTES.md with any new implementation issues and solutions
   - PLAN.md with decision outcomes and unblocked tasks

2. **Capture Latest State** including:
   - Completed unblocked tasks
   - Decisions made and their outcomes (from Phase 3)
   - Newly unblocked tasks
   - Remaining blocked tasks

**Phase 6: Provide Output**

Provide comprehensive output report tailored to plan type:

**Output Format for Research-Only Plans**:

```text
[✅] Takeover: $ARGUMENTS (Research-Only Execution)

## Plan Type
**Research-Only Plan** - Implementation tasks deferred to next /takeover run

## Research Completed
- Research tasks executed: [count]
- Research files generated:
  - research-[topic1].md
  - research-[topic2].md
  - [... one per research task]

## Handover Summary
- Files: CONTEXT.md, NOTES.md, PLAN.md at [project root path]
- Last Updated: [ISO timestamp after research]
- Branch: [branch from CONTEXT.md]
- Research references added to NOTES.md and PLAN.md

## Deferred to Next Round
- All implementation tasks deferred
- All unblocked tasks deferred
- All blocked tasks remain blocked

## Next Action
<IMPORTANT>
**Research Completed**:
- [count] research tasks completed in parallel
- Results saved to research-[topic].md files
- Handover updated with research references

**Next Steps**:
1. Review research files to understand findings
2. Make decisions on deferred topics based on research
3. Run `/takeover` again to proceed with implementation using research insights
</IMPORTANT>
```

**Output Format for Normal Plans**:

```text
[✅] Takeover: $ARGUMENTS

## Plan Type
**Normal Execution Plan** - Implementation completed

## Handover Summary
- Files: CONTEXT.md, NOTES.md, PLAN.md at [project root path]
- Last Updated: [ISO timestamp from CONTEXT.md]
- Branch: [branch from CONTEXT.md]

## Diagnostics Summary
- **Type Errors**: [count] in [count] files (TODO errors omitted)
- **Test Failures**: [count] tests
- **Lint Violations**: [count] in [count] files
- **Build Issues**: [count] failures

## Detected Workflow Step
**Step [N]: [Step Name]** from write-code.md

**Rationale**: [1-2 sentence explanation based on diagnostics + file substates + task prioritization]

**Critical Issues to Fix First**: [List if diagnostics found critical issues, otherwise "None - ready to resume planned work"]

## Files in Scope
### 🚧 In Progress ([count])
- [file path] - [substate] - [diagnostic issue if any]

### 📋 Planned ([count])
- [file path] - [substate] - [diagnostic issue if any]

### ✅ Completed ([count])
- [Summary line, e.g., "15 files completed, see CONTEXT.md"]

## Pre-Execution Decisions Made (from Step 1)
- **Decision: [Topic]** → User selected: [Choice]
  - Impact: [Tasks unblocked, execution effects]
- **Deferred Decisions**: [Count] decisions remain open for future resolution

## Tasks Executed
- [count] unblocked tasks completed using user-confirmed approaches
- [count] actions executed successfully

## Post-Execution Decisions (if any from Step 3, Phase 3)
- **Decision: [Topic]** → User selected: [Choice made]
  - Rationale: [User's reasoning]
- **Tasks Unblocked**: [Count] previously blocked tasks now ready

## Validation Results
- **Tests**: [PASS/FAIL] - [details if failures]
- **Linting**: [PASS/FAIL] - [details if failures]
- **Build**: [PASS/FAIL] - [details if failures]

## Next Action
<IMPORTANT>
**Work Completed**:
- Executed write-code.md Step [N] for [count] unblocked tasks
- Pre-execution decisions: [count finalized], [count deferred]
- Post-execution decisions: [count consulted], [count finalized]
- Unblocked [count] previously blocked tasks
- Updated handover documentation

**Next Steps**:
- If newly unblocked tasks exist: Run `/takeover` again to continue with them
- If all tasks complete: Work is done, review final handover docs
- If decisions deferred: Resolve deferred decisions when ready, then run `/takeover`
</IMPORTANT>
```

## 📝 Examples

### Simple Usage - Auto-Detect Step

```bash
/takeover
```

### Error Case

```bash
/takeover
# Error: One or more handover files not found
# Suggestion: Create handover first with `/handover` or check file location
```
