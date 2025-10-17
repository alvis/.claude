---
allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Task, AskUserQuestion, ExitPlanMode, mcp__plugin_coding_lsmcp__get_project_overview, mcp__plugin_coding_lsmcp__lsp_get_diagnostics

argument-hint: [--design=DESIGN.md] [--change="description"]

description: Refine design via Q&A, analyze gaps, plan implementation in handover format
---

# Plan Code

Analyzes design specifications (DESIGN.md and child pages) against current implementation state, asks clarifying questions to refine design proposals, and generates comprehensive handover documents (CONTEXT.md, NOTES.md, PLAN.md) with actionable implementation roadmap bridging design intent and reality.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not implement code or make changes to source files
- Does not modify original design specifications (creates \_PROPOSED and \_CHANGE files instead)
- Does not perform git operations like commit, push, or branch management
- Does not create new design specifications from scratch (use /spec-code for that)
- Does not execute builds, tests, or deployments
- Does not follow handover documents to execute tasks (use /takeover for that)
- Does not work in plan mode (creates files that require execution mode)

**When to REJECT**:

- When running in plan mode (user must exit plan mode first to create \_PROPOSED/\_CHANGE files)
- When no design specifications exist (run /spec-code first)
- When requesting code implementation instead of planning
- When asking to modify design specs directly instead of creating proposals
- When the working directory is not a git repository
- When design specs are too vague or incomplete to plan against
- When requesting task execution instead of planning

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Plan Mode Check

**Actions**:

1. **Check Execution Mode**:
   - Detect if running in plan mode
   - If in plan mode, REJECT the request immediately
   - Explain to user: "I cannot run /plan-code in plan mode because it requires creating and updating files (\_PROPOSED.md, \_CHANGE.md). Please exit plan mode first using /model or by approving a plan. I promise not to modify any code - only design and planning documents will be created."

2. **Validate Preconditions**:
   - Confirm working directory is a git repository
   - Check if design specifications exist (or will be analyzed)

### Step 2: Load and Validate Design Specifications

**Actions**:

1. **Parse Arguments**:
   - Extract --design argument (default: DESIGN.md in current directory)
   - Extract --change argument (optional description of what to change/add)
   - Validate design file exists and is readable

2. **Read Design Specifications**:
   - Read main DESIGN.md file
   - Check frontmatter for related_files list
   - Read all child page files mentioned in related_files:
     - REFERENCE.md (development reference and implementation detail)
     - REQUIREMENTS.md (functional and non-functional requirements)
     - NOTES.md (lessons learnt, researches and decisions archive)
     - UI.md (UI designs and component specs, if applicable)
     - DEPLOYMENT.md (deployment and infrastructure specs, if applicable)
   - Parse all design content into structured data

3. **Extract Design Intent**:
   - Identify target architecture and patterns
   - List all specified components and their responsibilities
   - Document required APIs and endpoints
   - Note UI requirements and component hierarchy (if applicable)
   - Extract technology stack requirements
   - Identify deployment and infrastructure needs (if applicable)
   - Capture non-functional requirements (performance, security, etc.)

4. **Validate Design Completeness**:
   - Check for missing critical sections
   - Identify ambiguous specifications
   - Note any design decisions that need clarification
   - If design is incomplete, suggest running /spec-code to update

### Step 3: Analyze Current Implementation State

**Actions**:

1. **Get Project Overview**:
   - Use mcp__plugin_coding_lsmcp__get_project_overview to understand codebase structure
   - Run git status to see current changes and branch
   - Check recent commits for context on ongoing work

2. **Analyze Implementation Architecture**:
   - Use Glob to scan project directory structure
   - Map actual file organization vs. designed architecture
   - Identify existing components and modules
   - Document current architectural patterns in use
   - Note deviations from design specifications

3. **Assess Technology Stack**:
   - Read package.json to identify installed dependencies
   - Compare actual stack vs. designed stack
   - Identify missing dependencies from design
   - Note any extra dependencies not in design
   - Check versions and compatibility

4. **Analyze Components and APIs**:
   - Use Grep to find component implementations
   - Search for API endpoint definitions
   - Map implemented components to designed components
   - Identify implemented but not designed components
   - Note missing components from design

5. **Check Code Quality and Issues**:
   - Use mcp__plugin_coding_lsmcp__lsp_get_diagnostics to find TypeScript errors
   - Use Grep to search for TODO, FIXME, HACK comments
   - Identify files with incomplete implementation
   - Note areas needing refactoring or improvement

6. **Review Tests and Coverage**:
   - Use Glob to find test files
   - Map tests to components
   - Identify components lacking test coverage
   - Note test failures or missing test scenarios

### Step 4: Interactive Design Refinement

**Actions**:

1. **Ask Clarifying Questions**:
   - Use AskUserQuestion tool to ask sequence of questions about the design
   - Focus on areas where change is proposed (--change argument) or design is ambiguous
   - Each question should offer 2-4 alternatives with clear rationales
   - Question categories to cover:
     - Architecture decisions (patterns, structure, modularity)
     - Technology choices (libraries, frameworks, tools)
     - Implementation approaches (trade-offs between options)
     - Design constraints (performance, scalability, maintainability)
     - Edge cases and error handling strategies

2. **Create Proposal Documents**:
   - Copy DESIGN.md → DESIGN_PROPOSED.md (in same directory as DESIGN.md)
   - Copy REFERENCE.md → REFERENCE_PROPOSED.md (if exists, in same directory)
   - Create DESIGN_CHANGE.md documenting all proposed changes from original to proposed
   - Create REFERENCE_CHANGE.md documenting reference changes (if REFERENCE.md exists)

3. **Update Proposals Based on Answers**:
   - Apply user answers to _PROPOSED files
   - Document rationale for each change in _CHANGE files
   - Include both what changed and why it changed
   - Mark question-answering tasks as completed in todo list

4. **User Review Cycle**:
   - Inform user to review \_PROPOSED and \_CHANGE files
   - Ask if user has questions or needs clarification on the proposals
   - If yes, ask follow-up questions using AskUserQuestion
   - Update \_PROPOSED and \_CHANGE files based on follow-up answers
   - Repeat until user is satisfied with proposals

5. **Mark Refinement Complete**:
   - Update todo list to show design refinement completed
   - Confirm with user that proposed design is ready for gap analysis

### Step 5: Identify Gaps and Discrepancies

**Actions**:

1. **Create Todo List**:
   - Use TodoWrite to track analysis progress
   - Track gap identification by category

2. **Map Design to Reality**:
   - Use DESIGN_PROPOSED.md (if exists) instead of DESIGN.md for comparison
   - Use REFERENCE_PROPOSED.md (if exists) instead of REFERENCE.md
   - For each design specification section:
     - Compare with actual implementation
     - Document what exists vs. what's proposed
     - Identify gaps: proposed but not implemented
     - Identify deviations: implemented differently than proposed
     - Note extras: implemented but not in proposed design

3. **Categorize Gaps**:
   - **Architecture gaps**: Structural differences between design and reality
   - **Component gaps**: Missing components or incomplete implementations
   - **API gaps**: Missing or incomplete endpoints
   - **UI gaps**: Missing screens, components, or incorrect implementations
   - **Technology gaps**: Missing dependencies or stack mismatches
   - **Testing gaps**: Missing tests or insufficient coverage
   - **Documentation gaps**: Missing or outdated docs
   - **Quality gaps**: Code quality issues, TODOs, technical debt

4. **Prioritize Gaps**:
   - Critical: Blocks core functionality or violates architecture
   - High: Required for complete feature implementation
   - Medium: Improves quality or user experience
   - Low: Nice-to-have or future enhancements

5. **Identify Dependencies**:
   - Note which gaps must be addressed first
   - Document blockers and prerequisites
   - Map task dependencies for sequencing

### Step 6: Generate Implementation Roadmap

**Actions**:

1. **Break Down Work into Phases**:
   - Phase 1: Foundation (architecture, core dependencies)
   - Phase 2: Core Implementation (essential components and APIs)
   - Phase 3: Integration (connecting components, data flow)
   - Phase 4: UI/UX (screens, components, styling)
   - Phase 5: Testing & Quality (tests, linting, refactoring)
   - Phase 6: Documentation & Deployment (docs, deployment setup)

2. **Create Task Breakdown**:
   - For each gap identified:
     - Create specific, actionable task
     - Assign to appropriate phase
     - Note dependencies and blockers
     - Estimate complexity (simple/moderate/complex)
     - Include acceptance criteria

3. **Document Decisions and Rationale**:
   - Note architectural decisions affecting implementation
   - Document trade-offs and constraints
   - Identify risks and mitigation strategies
   - Capture assumptions requiring validation

4. **Prepare Research Notes**:
   - Document design specs and references
   - Note areas requiring further research
   - Identify external resources needed
   - List questions needing clarification
   - Reference design changes from _CHANGE files in notes

### Step 7: Present Plan for Approval

**Actions**:

1. **Summarize Proposed Design Changes**:
   - Extract key changes from DESIGN_CHANGE.md
   - Highlight major architectural decisions from user Q&A
   - List technology choices and rationale
   - Note critical design decisions made

2. **Present Gap Analysis Summary**:
   - Show critical gaps that block implementation
   - Highlight high-priority tasks from roadmap
   - Explain dependencies and sequencing
   - Clarify risks and mitigation strategies

3. **Create Implementation Plan Summary**:
   - Summarize 6-phase roadmap with key deliverables
   - Show task breakdown with priorities
   - Explain decision rationale from design refinement
   - Include estimated complexity for major tasks

4. **Use ExitPlanMode Tool**:
   - Present complete implementation plan to user
   - Include design changes, gap analysis, and roadmap
   - Wait for user approval before proceeding
   - Format plan concisely with markdown

5. **Handle User Response**:
   - If approved: Proceed to Step 8 (Generate Handover Documents)
   - If rejected: Return to Step 4 for more design refinement
   - If questions raised: Clarify and re-present plan

### Step 8: Generate Handover Documents

**Actions**:

1. **Generate Current Timestamp**:
   - Execute: `date -u +"%Y-%m-%dT%H:%M:%SZ"` to get current ISO 8601 timestamp
   - Store the result to use consistently across all documents
   - Use this actual timestamp for all "Last Updated", "Created", "Updated" fields

2. **Write CONTEXT.md**:

   ```markdown
   # Implementation Handover - [Project Name]

   **Last Updated**: [ISO 8601 timestamp]
   **Current Branch**: [branch name]
   **Working Directory**: [pwd]
   **Design Specification**: [path to DESIGN_PROPOSED.md (or DESIGN.md if no proposal)]
   **Design Changes**: [path to DESIGN_CHANGE.md (if exists)]

   ## Background & Context

   [Extract from DESIGN_PROPOSED.md Background/Overview section]

   **Design Intent**: [Summary of what the proposed design specifies]

   **Design Evolution**: [Summary of changes from original to proposed design, from DESIGN_CHANGE.md]

   **Current State**: [Summary of current implementation status]

   ## Goals & Objectives

   **Design Goals**: [From DESIGN_PROPOSED.md goals and requirements]

   **Implementation Goals**: [What needs to be achieved to match proposed design]

   ## Reference Documents

   - Proposed Design: [path to DESIGN_PROPOSED.md]
   - Design Changes: [path to DESIGN_CHANGE.md]
   - Original Design: [path to DESIGN.md]
   - Proposed Reference: [path to REFERENCE_PROPOSED.md]
   - Reference Changes: [path to REFERENCE_CHANGE.md]
   - Original Reference: [path to REFERENCE.md]
   - Requirements Spec: [path to REQUIREMENTS.md]
   - Development Notes: [path to NOTES.md]
   - [UI Design Spec: path to UI.md]
   - [Deployment Spec: path to DEPLOYMENT.md]

   ## Current State

   **Architecture**: [Current vs. Designed]
   - Designed: [architecture from DESIGN.md]
   - Implemented: [actual architecture from analysis]
   - Status: [aligned/partial/divergent]

   **Technology Stack**: [Current vs. Designed]
   - Designed: [stack from DESIGN.md]
   - Implemented: [actual dependencies from package.json]
   - Gaps: [missing dependencies]
   - Extras: [additional dependencies not in design]

   **Components**: [X of Y implemented]
   - Implemented: [list of existing components]
   - Missing: [list of designed but not implemented]
   - Deviating: [list of implemented differently]

   **APIs/Endpoints**: [X of Y implemented]
   - Implemented: [list of existing endpoints]
   - Missing: [list from REFERENCE.md not found]

   **UI/Screens**: [X of Y implemented] (if applicable)
   - Implemented: [list of existing screens]
   - Missing: [list from UI.md not found]

   **Tests**: [coverage status]
   - Test files: [count]
   - Coverage gaps: [components without tests]

   ## File Status

   ### 🚧 In Progress
   [Files with TODOs, FIXMEs, incomplete implementation]
   - `path/to/file.ts` (need-completion) - [specific todos]
   - `path/to/file.ts` (need-fixing) - [issues found]
   - `path/to/file.ts` (need-linting) - [diagnostics]
   - `path/to/file.ts` (need-refactoring) - [quality issues]

   ### 📋 Planned
   [Files mentioned in design but not yet created]
   - `path/to/file.ts` (need-draft) - [component from REFERENCE.md]
   - `path/to/file.ts` (need-testing) - [missing test file]

   ### ✅ Completed
   [Files fully implemented and tested]
   - [list of completed files]

   ## Gap Analysis Summary

   ### Critical Gaps (Blockers)
   - [gap description] - [why critical] - [affects what]

   ### High Priority Gaps
   - [gap description] - [impact]

   ### Medium Priority Gaps
   - [gap description] - [impact]

   ### Low Priority Gaps
   - [gap description] - [impact]

   ## Key Decisions & Patterns

   **From Design**:
   - **Decision**: [from DESIGN.md decisions]
     **Status**: [implemented/pending/deviating]

   **Implementation Decisions Needed**:
   - **Decision**: [what needs to be decided]
     **Options**: [alternatives]
     **Impact**: [what it affects]

   ## Gotchas & Constraints

   **From Design**:
   - [constraints from DESIGN.md]

   **From Implementation**:
   - [discovered constraints or issues]

   ## Dependencies & Configuration

   **Required (from Design)**:
   - [package] [version] - [purpose] - [status: installed/missing]

   **Actual (from package.json)**:
   - [package] [version] - [in design: yes/no]

   **Configuration Changes Needed**:
   - [config change] - [reason from design]

   ## Next Steps

   1. [Immediate next action based on roadmap]
   2. [Following action from phase 1]
   3. [Next action in sequence]

   ## Context for Continuation

   **Design Understanding**:
   - [Key architectural concepts from design]
   - [Important patterns to follow]

   **Implementation Context**:
   - [Current work state]
   - [Recent changes]
   - [Blockers or challenges]
   ```

3. **Write NOTES.md**:

   ```markdown
   # Implementation Research - [Project Name]

   **Last Updated**: [ISO 8601 timestamp]
   **Related Work**: Implementing [project name] per design specifications

   ## Design Specification References

   ### Main Design Documents
   - DESIGN_PROPOSED.md: [path] - [proposed architecture, stack, goals]
   - DESIGN_CHANGE.md: [path] - [summary of changes from original design]
   - DESIGN.md: [path] - [original design for reference]

   ### Development Reference
   - REFERENCE_PROPOSED.md: [path] - [proposed development reference and implementation detail]
   - REFERENCE_CHANGE.md: [path] - [reference changes from original]
   - REFERENCE.md: [path] - [original reference for comparison]

   ### Requirements
   - REQUIREMENTS.md: [path] - [functional and non-functional requirements]

   ### Development Notes
   - NOTES.md: [path] - [lessons learnt, researches and decisions archive]

   ### UI Design (if applicable)
   - UI.md: [path] - [screens, components, styling]

   ### Deployment (if applicable)
   - DEPLOYMENT.md: [path] - [infrastructure, deployment process]

   ## Technology Stack Research

   ### From Design Specifications
   [For each technology in designed stack]
   - **[Technology]** ([version])
     - Purpose: [why specified in design]
     - Status: [installed/missing]
     - Documentation: [official docs URL]
     - Key features needed: [from REFERENCE.md or NOTES.md]

   ### Additional Research Needed
   - [Technology/concept]: [what needs research] - [why]

   ## Gap Analysis Findings

   ### Architecture Gaps
   **Gap**: [description]
   - **Design Intent**: [what DESIGN.md specifies]
   - **Current State**: [what exists]
   - **Discrepancy**: [the gap]
   - **Impact**: [why it matters]
   - **Solution**: [how to address]

   ### Component Gaps
   **Gap**: [component name from REFERENCE.md]
   - **Specification**: [from REFERENCE.md]
   - **Current State**: [not implemented/partial/different]
   - **What's Missing**: [specific details]
   - **Dependencies**: [what's needed first]

   ### API/Endpoint Gaps
   **Gap**: [endpoint from REFERENCE.md]
   - **Specification**: [method, path, request/response]
   - **Current State**: [missing/incomplete]
   - **Implementation Needs**: [what to build]

   ### Testing Gaps
   **Gap**: [component without tests]
   - **Test Requirements**: [from REQUIREMENTS.md if specified]
   - **Current Coverage**: [none/partial]
   - **Test Scenarios Needed**: [list]

   ## Implementation Patterns

   ### From Design Documentation
   - **Pattern**: [pattern specified in DESIGN.md]
     - **Purpose**: [why this pattern]
     - **How to Apply**: [from NOTES.md]
     - **Status**: [used/not used/partially used]

   ### Discovered in Codebase
   - **Pattern**: [pattern found in code]
     - **Alignment**: [matches/differs from design]
     - **Should Change**: [yes/no - rationale]

   ## Key Insights

   - **Design Completeness**: [how complete the design is]
   - **Implementation Maturity**: [how much is already done]
   - **Major Gaps**: [biggest discrepancies]
   - **Quick Wins**: [easy items to implement first]
   - **Complex Areas**: [challenging parts requiring more planning]

   ## Open Questions

   - [Design ambiguity requiring clarification]
   - [Implementation decision not covered in design]
   - [Technology choice needing validation]
   - [Architecture decision needing team input]

   ## Quick Tips for Implementation

   - Start with: [recommended starting point based on analysis]
   - Watch out for: [gotchas from design or code analysis]
   - Reference: [most useful design doc sections]
   - Testing strategy: [from REQUIREMENTS.md or gaps analysis]
   ```

4. **Write PLAN.md**:

   ```markdown
   # Implementation Plan - [Project Name]

   **Created**: [ISO 8601 timestamp]
   **Updated**: [ISO 8601 timestamp]
   **Status**: Planning
   **Design Base**: [path to DESIGN_PROPOSED.md]
   **Design Changes**: [path to DESIGN_CHANGE.md]

   ## Design Refinement Summary

   **Original Design**: [path to DESIGN.md]
   **Proposed Design**: [path to DESIGN_PROPOSED.md]

   **Key Changes** (from DESIGN_CHANGE.md):
   - [Change 1: description and rationale]
   - [Change 2: description and rationale]
   - [Change 3: description and rationale]

   **Design Decisions Made**:
   - [Decision 1: what was decided and why]
   - [Decision 2: what was decided and why]

   ## Goals & Objectives

   ### Primary Goal
   Implement [project name] according to proposed design specifications with focus on:
   - [key goal from DESIGN_PROPOSED.md]
   - [key goal from DESIGN_PROPOSED.md]

   ### Success Criteria
   - [ ] All components from REFERENCE_PROPOSED.md implemented and tested
   - [ ] Architecture matches DESIGN_PROPOSED.md specifications
   - [ ] All requirements from REQUIREMENTS.md satisfied
   - [ ] API endpoints from REFERENCE_PROPOSED.md fully functional
   - [ ] [UI matches UI.md specifications] (if applicable)
   - [ ] Code follows patterns from NOTES.md
   - [ ] Test coverage meets requirements
   - [ ] [Deployment per DEPLOYMENT.md] (if applicable)

   ## Task Breakdown

   ### Phase 1: Foundation (Status: Pending)
   **Goal**: Establish architectural foundation and core dependencies

   **Tasks**:
   - [ ] Install missing dependencies from design spec
     - Priority: Critical
     - Packages: [list from gap analysis]
     - Files affected: package.json
   - [ ] Set up project structure per DESIGN.md architecture
     - Priority: Critical
     - Create: [directories from architecture]
     - Rationale: [from DESIGN.md]
   - [ ] Configure build tools and linting
     - Priority: High
     - Per: NOTES.md guidelines
   - [ ] [Set up database/data layer per REFERENCE.md]
     - Priority: Critical (if applicable)
     - Schema: [from data models]

   ### Phase 2: Core Components (Status: Pending)
   **Goal**: Implement essential components and business logic

   **Tasks**:
   - [ ] Implement [Component A] from REFERENCE.md
     - Priority: Critical
     - Spec: [reference to REFERENCE.md section]
     - Dependencies: [what's needed first]
     - Acceptance: [from requirements]
   - [ ] Implement [Component B] from REFERENCE.md
     - Priority: High
     - Spec: [reference to REFERENCE.md section]
     - Dependencies: [Component A]
   - [ ] [Continue for each core component...]
   - [ ] Refactor [existing component] to match design
     - Priority: Medium
     - Current state: [deviation description]
     - Target state: [per REFERENCE.md]

   ### Phase 3: API Layer (Status: Pending)
   **Goal**: Implement all API endpoints per REFERENCE.md

   **Tasks**:
   - [ ] Implement [GET /endpoint] from REFERENCE.md
     - Priority: Critical
     - Request: [spec]
     - Response: [spec]
     - Validation: [requirements]
   - [ ] Implement [POST /endpoint] from REFERENCE.md
     - Priority: Critical
     - Request: [spec]
     - Response: [spec]
   - [ ] [Continue for each endpoint...]
   - [ ] Add authentication/authorization per DESIGN.md
     - Priority: Critical
     - Pattern: [from NOTES.md]

   ### Phase 4: UI Implementation (Status: Pending) (if applicable)
   **Goal**: Build user interface per UI.md specifications

   **Tasks**:
   - [ ] Implement [Screen/Page A] from UI.md
     - Priority: High
     - Components needed: [list]
     - Routes: [from UI.md]
   - [ ] Implement [Component X] from UI.md
     - Priority: High
     - Props: [from spec]
     - Styling: [approach from UI.md]
   - [ ] [Continue for each UI element...]
   - [ ] Implement navigation and routing
     - Priority: Medium
     - Per: UI.md navigation spec

   ### Phase 5: Testing & Quality (Status: Pending)
   **Goal**: Achieve test coverage and code quality per REQUIREMENTS.md

   **Tasks**:
   - [ ] Write tests for [Component A]
     - Priority: High
     - Coverage target: [from REQUIREMENTS.md]
     - Scenarios: [from requirements and edge cases]
   - [ ] Write integration tests for [API endpoints]
     - Priority: High
     - Test cases: [from REQUIREMENTS.md]
   - [ ] [Continue for each component...]
   - [ ] Fix linting issues and TODOs
     - Priority: Medium
     - Files: [from gap analysis]
   - [ ] Address code quality issues
     - Priority: Medium
     - Areas: [from diagnostics]

   ### Phase 6: Documentation & Deployment (Status: Pending)
   **Goal**: Complete documentation and deployment setup

   **Tasks**:
   - [ ] Document public APIs
     - Priority: Medium
     - Per: NOTES.md standards
   - [ ] [Set up deployment pipeline per DEPLOYMENT.md]
     - Priority: High (if applicable)
     - Infrastructure: [from DEPLOYMENT.md]
   - [ ] [Configure environments per DEPLOYMENT.md]
     - Priority: Medium (if applicable)
   - [ ] Update README and user docs
     - Priority: Low
     - Content: based on implementation

   ## Dependencies

   ### External Dependencies
   [From designed stack and gap analysis]
   - [Package] [version] - [provides what] - [status: installed/needed]

   ### Internal Dependencies
   [Task sequencing based on architecture]
   - [Component B] requires [Component A] completed first
   - [API endpoints] require [data layer] completed first
   - [UI screens] require [components] completed first
   - [Tests] require [implementation] completed first

   ### Design Clarifications Needed
   [From open questions]
   - [Question] - [blocks what task] - [who to ask]

   ## Risks & Mitigation

   ### Risk: Design Specification Incomplete
   **Impact**: Medium
   **Affected Tasks**: [tasks affected by ambiguity]
   **Mitigation**: Review design with team, run /spec-code to update design docs

   ### Risk: Technology Stack Mismatch
   **Impact**: High (if critical mismatch found)
   **Details**: [description of mismatch]
   **Mitigation**: [strategy to align or update design]

   ### Risk: [Other risks from gap analysis]
   **Impact**: [High/Medium/Low]
   **Mitigation**: [strategy]

   ## Decision Log

   ### Decision: Use Design Specifications as Source of Truth
   **Date**: [ISO 8601 timestamp]
   **Rationale**: All implementation should align with design docs; deviations require design updates
   **Impact**: All tasks reference design specs for acceptance criteria

   ### Decision: [Other key decisions made during planning]
   **Date**: [ISO 8601 timestamp]
   **Rationale**: [why]
   **Impact**: [what it affects]

   ## Progress Tracking

   **Overall Progress**: 0% (Planning Phase)

   **By Phase**:
   - Phase 1 (Foundation): 0% (0/X tasks)
   - Phase 2 (Core): 0% (0/X tasks)
   - Phase 3 (API): 0% (0/X tasks)
   - Phase 4 (UI): 0% (0/X tasks)
   - Phase 5 (Testing): 0% (0/X tasks)
   - Phase 6 (Docs/Deploy): 0% (0/X tasks)

   **Total Tasks**: [count] ([critical count] critical, [high count] high, [medium count] medium, [low count] low)
   ```

5. **Update Todo List**:
   - Mark handover document generation completed
   - Note files created: CONTEXT.md, NOTES.md, PLAN.md
   - Note proposal files created (if applicable): DESIGN_PROPOSED.md, DESIGN_CHANGE.md, etc.

### Step 9: Reporting

**Output Format**:

```text
[✅] Command: plan-code $ARGUMENTS

## Summary
- Design specification: [path to DESIGN_PROPOSED.md or DESIGN.md]
- Design changes documented: [path to DESIGN_CHANGE.md] (if created)
- Child specs analyzed: [count] ([filenames])
- Current implementation: [X% complete based on gap analysis]
- Gaps identified: [count] ([critical/high/medium/low breakdown])
- Proposal files created (if applicable):
  - DESIGN_PROPOSED.md: Refined design with user input
  - DESIGN_CHANGE.md: Summary of design changes
  - COMPONENTS_PROPOSED.md: Updated component specifications (if applicable)
  - COMPONENTS_CHANGE.md: Component changes summary (if applicable)
- Handover documents created:
  - CONTEXT.md: Implementation status and gap analysis
  - NOTES.md: Design specs and implementation research
  - PLAN.md: [X] tasks across [Y] phases

## Design Refinement Summary (if applicable)
- Questions asked: [count]
- Design iterations: [count]
- Key decisions made:
  - [Decision 1: description]
  - [Decision 2: description]
  - [Decision 3: description]
- Major changes from original design:
  - [Change 1: from DESIGN_CHANGE.md]
  - [Change 2: from DESIGN_CHANGE.md]

## Design Analysis
- Architecture: [designed architecture]
- Technology Stack: [designed stack]
- Components Specified: [count]
- APIs/Endpoints Specified: [count]
- UI Elements Specified: [count] (if applicable)
- Requirements: [count functional, count non-functional]

## Implementation Analysis
- Current Architecture: [actual architecture] - [aligned/partial/divergent]
- Current Stack: [actual dependencies]
- Components Implemented: [count] of [designed count]
- APIs Implemented: [count] of [designed count]
- UI Implemented: [count] of [designed count] (if applicable)
- Test Coverage: [percentage or count]
- Code Quality Issues: [count diagnostics, TODOs, FIXMEs]

## Gap Analysis
### Critical Gaps ([count])
- [gap 1]
- [gap 2]
- [gap 3]

### High Priority Gaps ([count])
- [gap 1]
- [gap 2]

### Medium Priority Gaps ([count])
- [gap summary]

### Low Priority Gaps ([count])
- [gap summary]

## Implementation Roadmap
- **Phase 1 (Foundation)**: [X] tasks - [key deliverables]
- **Phase 2 (Core)**: [X] tasks - [key deliverables]
- **Phase 3 (API)**: [X] tasks - [key deliverables]
- **Phase 4 (UI)**: [X] tasks - [key deliverables] (if applicable)
- **Phase 5 (Testing)**: [X] tasks - [key deliverables]
- **Phase 6 (Docs/Deploy)**: [X] tasks - [key deliverables]

**Total Tasks**: [count] ([critical], [high], [medium], [low])

## Handover Documents
- CONTEXT.md: ✓ (status, gaps, decisions)
- NOTES.md: ✓ (design specs, patterns, insights)
- PLAN.md: ✓ (roadmap, [X] tasks, dependencies)

## Next Steps
1. Review handover documents (CONTEXT.md, NOTES.md, PLAN.md)
2. Clarify design ambiguities if needed (run /spec-code to update)
3. Begin implementation with /takeover to auto-resume from PLAN.md
4. Start with Phase 1 tasks: [first critical task]

## Recommendations
- [Implementation strategy based on analysis]
- [Areas requiring design clarification]
- [Quick wins to build momentum]
- [Complex areas needing extra attention]
```

## 📝 Examples

### Basic Usage - Analyze Existing Design

```bash
/plan-code
# Step 1: Checks not in plan mode ✓
# Step 2: Analyzes DESIGN.md and child files
# Step 3: Analyzes current empty project (greenfield)
# Step 4: Asks clarifying questions about architecture, tech stack, patterns
#   Q: "Which state management approach should we use?"
#   Options: Redux, Context API, Zustand, MobX
#   User selects: Zustand
# Step 4: Creates DESIGN_PROPOSED.md with Zustand decision
# Step 4: Creates DESIGN_CHANGE.md documenting state management choice
# Step 4: User reviews proposals, approves
# Step 5: Identifies gaps (0% implementation)
# Step 6: Generates roadmap (6 phases)
# Step 7: Presents plan via ExitPlanMode, user approves
# Step 8: Creates CONTEXT.md showing 0% implementation
# Step 8: Creates NOTES.md with design specs and decisions
# Step 8: Builds PLAN.md with complete implementation roadmap
# Result: Full implementation plan with refined design
```

### Plan Mode Rejection

```bash
# User is in plan mode
/plan-code --change="add authentication"
# Step 1: Detects plan mode
# ❌ Error: Cannot run /plan-code in plan mode
# Message: "I cannot run /plan-code in plan mode because it requires creating
#           and updating files (_PROPOSED.md, _CHANGE.md). Please exit plan mode
#           first using /model or by approving a plan. I promise not to modify
#           any code - only design and planning documents will be created."
# Suggestion: Exit plan mode first, then re-run command
```

### Interactive Design Refinement

```bash
/plan-code --change="add caching layer with Redis"
# Step 1: Checks not in plan mode ✓
# Step 2: Loads DESIGN.md (current design without caching)
# Step 3: Analyzes current implementation (no caching present)
# Step 4: Asks clarifying questions:
#   Q1: "What should be the caching strategy?"
#       Options: Write-through, Write-back, Cache-aside, Read-through
#       User selects: Cache-aside
#   Q2: "Which data should be cached?"
#       Options: All API responses, User sessions only, Database queries, Computed results
#       User selects: Database queries, Computed results (multi-select)
#   Q3: "What should be the cache TTL strategy?"
#       Options: Fixed TTL for all, Per-resource TTL, Adaptive TTL, No expiration
#       User selects: Per-resource TTL
# Step 4: Creates DESIGN_PROPOSED.md adding Redis caching with cache-aside pattern
# Step 4: Creates COMPONENTS_PROPOSED.md adding CacheService component
# Step 4: Creates DESIGN_CHANGE.md documenting:
#   - Added Redis dependency
#   - Added cache-aside pattern
#   - Cache TTL strategy: per-resource
#   - Scope: database queries and computed results
# Step 4: Creates COMPONENTS_CHANGE.md documenting new CacheService
# Step 4: User reviews _PROPOSED files
# Step 4: User asks: "Should we cache API responses too?"
# Step 4: Follow-up question asked, updates files based on answer
# Step 5: Identifies gaps (Redis not installed, CacheService missing)
# Step 6: Generates roadmap with caching implementation tasks
# Step 7: Presents plan, user approves
# Step 8: Creates handover docs referencing proposed design
# Result: Complete plan for adding Redis caching with user-refined design
```

### Partially Implemented Project

```bash
/plan-code
# Step 1: Checks not in plan mode ✓
# Step 2: Reads DESIGN.md (specifies 8 components, 12 API endpoints)
# Step 3: Analyzes codebase (finds 3 components, 5 endpoints)
# Step 4: Asks questions about missing features:
#   Q: "Should we maintain the original architecture or refactor?"
#   User selects: Maintain original
#   Q: "Which missing components should be prioritized?"
#   User selects: Authentication, User Management (multi-select)
# Step 4: Creates _PROPOSED files with prioritization decisions
# Step 5: Gap Analysis:
#   - 5 components missing (2 high priority, 3 medium)
#   - 7 endpoints missing
#   - 2 components implemented differently
#   - 4 components missing tests
# Step 6: Builds roadmap prioritizing auth and user management
# Step 7: Presents plan, user approves
# Step 8: Generates CONTEXT.md with gap breakdown
# Step 8: Creates NOTES.md documenting deviations
# Step 8: Builds PLAN.md focusing on high-priority items first
```

### Project with Design-Reality Mismatch

```bash
/plan-code --design=docs/DESIGN.md
# Loads design from docs/DESIGN.md
# Design specifies: REST API with Express, PostgreSQL, React UI
# Actual code: REST API with Fastify, MongoDB, React UI
# Gap Analysis:
#   - Stack deviation: Fastify vs Express (minor)
#   - Stack deviation: MongoDB vs PostgreSQL (major)
#   - Architecture alignment: 80%
# CONTEXT.md documents deviations and impact
# NOTES.md notes why deviations occurred
# PLAN.md includes tasks to either:
#   - Update design to match reality, OR
#   - Migrate implementation to match design
# Recommends design update discussion
```

### Well-Aligned Implementation

```bash
/plan-code
# Analyzes design and implementation
# Findings:
#   - Architecture: 95% aligned
#   - Components: 10 of 10 implemented
#   - APIs: 15 of 15 implemented
#   - Tests: 8 of 10 components covered
# Gap Analysis:
#   - 2 components need tests (medium priority)
#   - Minor refactoring opportunities (low priority)
#   - Documentation incomplete (low priority)
# Generates minimal PLAN.md focusing on polish
# CONTEXT.md shows high completion status
# Recommends final testing and documentation phase
```

### Design Clarification Needed

```bash
/plan-code
# Reads DESIGN.md
# Finds ambiguous sections:
#   - Authentication method not specified
#   - Database schema incomplete
#   - Error handling strategy unclear
# CONTEXT.md lists ambiguities as blockers
# NOTES.md documents open questions
# PLAN.md includes Phase 0: Design Clarification
#   - Task: Update DESIGN.md with auth strategy
#   - Task: Complete database schema in REFERENCE.md
#   - Task: Add error handling to NOTES.md
# Recommends running /spec-code to update design first
```

### Complex Migration Scenario

```bash
/plan-code
# Design specifies: Microservices architecture
# Current state: Monolithic application
# Gap Analysis:
#   - Architecture: Complete restructuring needed
#   - Critical: Extract services from monolith
#   - High: Set up service communication
#   - High: Migrate data layer
# PLAN.md creates migration roadmap:
#   - Phase 1: Service boundaries and APIs
#   - Phase 2: Extract Service A (least dependent)
#   - Phase 3: Extract Service B
#   - Phase 4: Extract Service C
#   - Phase 5: Retire monolith
# NOTES.md documents migration patterns
# CONTEXT.md highlights migration risks
```

### After Design Update

```bash
# User previously ran: /spec-code "Add caching layer using Redis"
/plan-code
# Detects DESIGN.md was recently updated (via frontmatter last_edited_at)
# Loads updated design with Redis caching specification
# Analyzes current code: No Redis integration found
# Gap Analysis:
#   - New component: Redis cache service (critical)
#   - Updated component: API layer needs cache integration (high)
#   - New dependency: redis package (critical)
#   - Updated tests: Cache layer tests needed (high)
# PLAN.md focuses on implementing new caching layer
# CONTEXT.md explains caching addition context
# NOTES.md includes Redis documentation references
```

### Custom Design File Path

```bash
/plan-code --design=docs/specs/DESIGN.md --change="migrate to microservices"
# Step 1: Checks not in plan mode ✓
# Step 2: Loads design from docs/specs/DESIGN.md
# Step 3: Analyzes current monolithic implementation
# Step 4: Asks questions about microservices migration:
#   Q1: "Which service extraction strategy?"
#       Options: Big Bang, Strangler Fig, Parallel Run, Incremental
#       User selects: Strangler Fig
#   Q2: "Which services to extract first?"
#       Options lists service boundaries from analysis
#       User selects: User Service, Product Service
#   Q3: "How should services communicate?"
#       Options: REST, gRPC, Message Queue, Event Bus
#       User selects: gRPC for sync, Message Queue for async
# Step 4: Creates docs/specs/DESIGN_PROPOSED.md with microservices architecture
# Step 4: Creates docs/specs/DESIGN_CHANGE.md with migration strategy
# Step 5: Identifies massive architectural gaps
# Step 6: Generates multi-phase migration roadmap
# Step 7: Presents complex migration plan, user approves
# Step 8: Creates handover docs with migration context
# Result: Complete microservices migration plan
```

### Error - No Design Specification

```bash
/plan-code
# Step 1: Checks not in plan mode ✓
# Step 2: Error - Design specification not found
# Looked for: DESIGN.md in current directory
# Suggestion: Run '/spec-code "your project description"' to create design specifications first
# Alternative: Specify design file path with --design=path/to/DESIGN.md
```

### Error - Incomplete Design

```bash
/plan-code
# Warning: Design specification is incomplete or too vague
# Missing critical sections:
#   - Architecture not specified
#   - No components defined in REFERENCE.md
#   - Technology stack unclear
# Cannot create meaningful implementation plan without design details
# Suggestion: Run '/spec-code --sync-template' to update design with complete template structure
# Alternative: Manually complete design specification before running /plan-code
```

### Integration with /takeover

```bash
# Step 1: Plan the work with design refinement
/plan-code --change="add real-time notifications"
# Asks clarifying questions about notification approach
# Creates DESIGN_PROPOSED.md with WebSocket decision
# Creates DESIGN_CHANGE.md documenting changes
# Generates CONTEXT.md, NOTES.md, PLAN.md

# Step 2: Execute the plan
/takeover
# Automatically reads handover documents
# References DESIGN_PROPOSED.md for target architecture
# Reviews DESIGN_CHANGE.md for context on decisions
# Uses CONTEXT.md for gap awareness
# References NOTES.md for implementation patterns
# Executes tasks from PLAN.md Phase 1 in priority order
# Follows design decisions from refinement step
```
