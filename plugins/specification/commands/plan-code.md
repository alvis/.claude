---
allowed-tools: Read, Glob, Grep, Bash, Write, Task, TodoWrite, AskUserQuestion, ExitPlanMode

argument-hint: [--design=DESIGN.md] [--change="description"]

description: Generate DRAFT.md (commit blueprint) and PLAN.md (execution roadmap) from proposals
---

# Plan Code

Analyzes design proposals or existing specifications, generates comprehensive DRAFT.md with copy-paste ready commit blueprints, and creates lightweight PLAN.md execution roadmap. Transforms approved designs into actionable implementation plans with atomic, testable commits.

## Purpose & Scope

**What this command does NOT do**:

- Does not implement code or make changes to source files
- Does not execute git commits, push, or branch management
- Does not create new design specifications from scratch (use /spec-code for that)
- Does not execute builds, tests, or deployments
- Does not follow plans to execute tasks (use /takeover for that)
- Does not modify original design files directly

**When to REJECT**:

- When no design specifications exist (run /spec-code first)
- When requesting code implementation instead of planning
- When asking to execute commits from DRAFT.md (use /takeover for that)
- When the working directory is not a git repository
- When design specs are too vague or incomplete to plan against

**Plan Mode Behavior**:

This command can operate partially in plan mode:
- **Allowed in plan mode**: Loading design docs, analysis, AskUserQuestion clarifications, presenting summaries
- **Blocked in plan mode**: Writing DRAFT.md, *_CHANGE.md, PLAN.md, or finalizing proposals

When a write action is needed in plan mode, inform the user:
"I've completed the analysis and design refinement. To write [DRAFT.md/*_CHANGE.md/PLAN.md], please exit plan mode first. You can do this by approving the plan or using /model."

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Load All Design Documents & Detect Proposals

**Actions**:

1. **Validate Environment**:
   - Confirm working directory is a git repository
   - Parse --design argument (default: look in current directory)
   - Parse --change argument if provided (description of what to change/add)
   - Use TodoWrite to create initial todo list for workflow tracking

2. **Scan for Design Documents**:
   - Use Glob to find all design documents in the project:
     - **DESIGN.md** - Main design specification (architecture, components, patterns)
     - **REQUIREMENTS.md** - Functional and non-functional requirements
     - **DATA.md** - Data models, schemas, database design
     - **UI.md** - UI specifications, component designs, layouts
     - **NOTES.md** - Implementation notes, decisions, context
     - **REFERENCE.md** - API specifications, technical reference
     - **Any other `*.md`** design docs in the project directory
   - Read and parse each found document for later cross-referencing

3. **Scan for Proposals**:
   - Use Glob to find `*_PROPOSED.md` files in project directory
   - Check for DESIGN_PROPOSED.md, UI_PROPOSED.md, REFERENCE_PROPOSED.md, etc.

4. **Handle Proposal Detection**:
   - **If proposals found**:
     - Present summary of all `*_PROPOSED.md` files discovered
     - List key changes in each proposal
     - Ask user: "Is this proposal approved for implementation planning?"
     - If approved: Proceed to Step 2
     - If not approved: Exit with guidance to refine proposals first
   - **If no proposals found**:
     - Inform user: "No `*_PROPOSED.md` files found. Using original design files directly."
     - Skip to Step 3 (Generate DRAFT.md)

### Step 2: Analyze Approved Proposal & Document Changes

**Actions** (only if `*_PROPOSED.md` files exist):

1. **Read Proposal Files**:
   - Read each `*_PROPOSED.md` file found
   - Parse structure, sections, and content

2. **Compare Against Originals**:
   - For each proposal, find corresponding original file:
     - DESIGN_PROPOSED.md → DESIGN.md
     - UI_PROPOSED.md → UI.md
     - REFERENCE_PROPOSED.md → REFERENCE.md
   - Read original files for comparison

3. **Check Plan Mode Before Writing**:
   - If in plan mode:
     - Present the change analysis verbally (what sections were added, modified, removed)
     - Inform user: "To persist *_CHANGE.md files, please exit plan mode first."
     - Pause workflow until user exits plan mode
   - If not in plan mode: Proceed to write files

4. **Generate Change Documentation**:
   - Create `*_CHANGE.md` for each proposal documenting:
     - Sections added
     - Sections modified (with before/after)
     - Sections removed
     - Key architectural decisions changed
     - Technology additions or removals
   - Format changes clearly for human review

### Step 3: Generate DRAFT.md

**Actions**:

1. **Gather Implementation Context**:
   - Use mcp__plugin_coding_lsmcp__get_project_overview for codebase structure
   - Use Glob to scan current file structure
   - Read relevant design files (proposals if exist, originals otherwise)
   - Analyze technology stack from package.json or equivalent
   - Use TodoWrite to track analysis progress

2. **Analyze Implementation Architecture**:
   - Map actual file organization vs. designed architecture
   - Identify existing components and modules
   - Document current architectural patterns in use
   - Note deviations from design specifications

3. **Assess Technology Stack**:
   - Read package.json to identify installed dependencies
   - Compare actual stack vs. designed stack
   - Identify missing dependencies from design
   - Note any extra dependencies not in design

4. **Check Code Quality and Issues**:
   - Use mcp__plugin_coding_lsmcp__lsp_get_diagnostics to find TypeScript errors
   - Use Grep to search for TODO, FIXME, HACK comments
   - Identify files with incomplete implementation
   - Note areas needing refactoring or improvement

5. **Review Tests and Coverage**:
   - Use Glob to find test files
   - Map tests to components
   - Identify components lacking test coverage

6. **Cross-Reference ALL Design Documents**:
   - **DESIGN.md** - Cross-reference for architecture patterns, component relationships, and system design
   - **REQUIREMENTS.md** - Ensure all functional requirements have corresponding implementations and tests
   - **DATA.md** - Use for data model implementations, schema definitions, and database operations
   - **UI.md** - Reference for component specifications, layouts, and UI behavior
   - **NOTES.md** - Follow implementation patterns, decisions, and context guidelines
   - **REFERENCE.md** - Use for API specifications, endpoint definitions, and technical contracts

7. **Plan Atomic Commits**:
   - Break implementation into self-contained, atomic commits
   - Each commit must be:
     - Independently testable
     - Single responsibility
     - Complete with 100% test coverage for its scope
   - Order commits by dependency (foundations first)

8. **Write DRAFT.md**:

   ```markdown
   # Implementation Draft - [Project Name]

   **Created**: [ISO 8601 timestamp]
   **Design Source**: [path to DESIGN_PROPOSED.md or DESIGN.md]
   **Change Log**: [path to *_CHANGE.md files if exist]

   ## File Structure

   Final project structure after all commits are applied.
   Files are sorted by type (directories first), then alphabetically.
   Each entry shows which commit(s) create or modify it.

   ```

   project/
   ├── src/
   │   ├── components/
   │   │   ├── Button.tsx           # (#1)
   │   │   ├── Card.tsx             # (#2)
   │   │   └── index.ts             # (#1, #2)
   │   ├── hooks/
   │   │   └── useAuth.ts           # (#3)
   │   ├── services/
   │   │   ├── api.ts               # (#1)
   │   │   └── auth.ts              # (#3)
   │   └── index.ts                 # (#1)
   ├── tests/
   │   ├── Button.test.tsx          # (#1)
   │   ├── Card.test.tsx            # (#2)
   │   └── useAuth.test.ts          # (#3)
   ├── package.json                 # (#1)
   └── tsconfig.json                # (#1)

   ```

   ## Commit Plan

   Each commit is atomic, self-contained, and independently testable.
   Copy-paste the code blocks directly into your files.

   ### Commit 1: `feat(core): initialize project with base configuration`

   - **Scope**: Project foundation
   - **Description**: Sets up project structure, configuration files, and core dependencies

   **Files**:

   ```

   new: package.json
   new: tsconfig.json
   new: src/index.ts
   new: src/services/api.ts
   new: src/components/Button.tsx
   new: src/components/index.ts
   new: tests/Button.test.tsx

   ```

   - `package.json` (new)
     ```json
     {
       "name": "project-name",
       "version": "1.0.0",
       "dependencies": {
         "react": "^18.2.0"
       }
     }
     ```

   - `tsconfig.json` (new)

     ```json
     {
       "compilerOptions": {
         "target": "ES2020",
         "module": "ESNext",
         "strict": true
       }
     }
     ```

   - `src/index.ts` (new)

     ```typescript
     export * from './components';
     export * from './services/api';
     ```

   - `src/services/api.ts` (new)

     ```typescript
     export class ApiService {
       private baseUrl: string;

       constructor(baseUrl: string) {
         this.baseUrl = baseUrl;
       }

       async get<T>(endpoint: string): Promise<T> {
         const response = await fetch(`${this.baseUrl}${endpoint}`);
         return response.json();
       }
     }
     ```

   - `src/components/Button.tsx` (new)

     ```tsx
     import React from 'react';

     interface ButtonProps {
       label: string;
       onClick: () => void;
     }

     export const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
       return <button onClick={onClick}>{label}</button>;
     };
     ```

   - `src/components/index.ts` (new)

     ```typescript
     export { Button } from './Button';
     ```

   - `tests/Button.test.tsx` (new)

     ```tsx
     import { render, fireEvent } from '@testing-library/react';
     import { Button } from '../src/components/Button';

     describe('Button', () => {
       it('renders with label', () => {
         const { getByText } = render(<Button label="Click me" onClick={() => {}} />);
         expect(getByText('Click me')).toBeInTheDocument();
       });

       it('calls onClick when clicked', () => {
         const handleClick = jest.fn();
         const { getByText } = render(<Button label="Click" onClick={handleClick} />);
         fireEvent.click(getByText('Click'));
         expect(handleClick).toHaveBeenCalledTimes(1);
       });
     });
     ```

   ---

   ### Commit 2: `feat(ui): add Card component with styling`

   - **Scope**: UI components
   - **Description**: Adds reusable Card component for content containers

   **Files**:

   ```
   new: src/components/Card.tsx
   modified: src/components/index.ts
   new: tests/Card.test.tsx
   ```

   - `src/components/Card.tsx` (new)

     ```tsx
     import React from 'react';

     interface CardProps {
       title: string;
       children: React.ReactNode;
     }

     export const Card: React.FC<CardProps> = ({ title, children }) => {
       return (
         <div className="card">
           <h2>{title}</h2>
           <div className="card-content">{children}</div>
         </div>
       );
     };
     ```

   - `src/components/index.ts` (modified)

     ```typescript
     export { Button } from './Button';
     export { Card } from './Card';
     ```

   - `tests/Card.test.tsx` (new)

     ```tsx
     import { render } from '@testing-library/react';
     import { Card } from '../src/components/Card';

     describe('Card', () => {
       it('renders title and children', () => {
         const { getByText } = render(
           <Card title="Test Card">
             <p>Card content</p>
           </Card>
         );
         expect(getByText('Test Card')).toBeInTheDocument();
         expect(getByText('Card content')).toBeInTheDocument();
       });
     });
     ```

   ---

   ### Commit 3: `feat(auth): add authentication hook and service`

   - **Scope**: Authentication
   - **Description**: Implements useAuth hook and auth service for user authentication

   **Files**:

   ```
   new: src/hooks/useAuth.ts
   new: src/services/auth.ts
   new: tests/useAuth.test.ts
   ```

   [Continue with full file contents for each commit...]

   ---

   ## Notes

   - All commits follow conventional commit format
   - Each commit includes complete test coverage
   - Files can be copy-pasted directly - no placeholders or TODOs
   - Run tests after each commit to verify: `npm test`

   ```

9. **Check Plan Mode Before Writing**:
   - If in plan mode:
     - Present the draft plan verbally (commit summaries, file structure overview)
     - Inform user: "To persist DRAFT.md, please exit plan mode first."
     - Pause workflow until user exits plan mode
   - If not in plan mode: Write DRAFT.md to disk

10. **Commit Requirements Checklist**:
   - Each commit is self-contained (independently testable)
   - Each commit has 100% test coverage for its scope
   - Clear separation of concerns between commits
   - Conventional commit format: `type(scope): description`
   - Multiple commits per implementation phase allowed
   - Full file contents provided - copy-paste ready

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

2. **Update DRAFT.md Based on Answers**:
   - Apply user answers to DRAFT.md commit plan
   - Adjust commit structure if architectural decisions change
   - Document rationale for each decision in commit descriptions
   - Use TodoWrite to mark question-answering tasks as completed

3. **User Review Cycle**:
   - Inform user to review updated DRAFT.md
   - Ask if user has questions or needs clarification
   - If yes, ask follow-up questions using AskUserQuestion
   - Update DRAFT.md based on follow-up answers
   - Repeat until user is satisfied with the draft

4. **Mark Refinement Complete**:
   - Use TodoWrite to update todo list showing design refinement completed
   - Confirm with user that DRAFT.md is ready for final review

### Step 5: Present Draft for Review

**Actions**:

1. **Generate Draft Summary**:
   - List all commit messages in order
   - Show total commit count
   - Summarize key files and their commit associations
   - Highlight any dependencies between commits

2. **Present to User**:
   - Display commit plan summary:

     ```
     ## Draft Summary

     **Total Commits**: X
     **Files Created**: Y
     **Files Modified**: Z

     ### Commits:
     1. `feat(core): initialize project` - X files
     2. `feat(ui): add Card component` - Y files
     3. `feat(auth): add authentication` - Z files
     ...

     ### Key Dependencies:
     - Commit 2 depends on Commit 1 (uses base config)
     - Commit 3 depends on Commit 1 (uses API service)
     ```

3. **Request Approval**:
   - Ask user: "Approve this draft to generate PLAN.md?"
   - If approved: Proceed to Step 6
   - If changes requested: Update DRAFT.md and re-present

### Step 6: Generate PLAN.md (on approval)

**Actions**:

1. **Group Commits by Phase**:
   - Analyze commit dependencies
   - Group related commits into logical phases
   - Typical phases: Foundation, Core, Features, Integration, Testing, Polish

2. **Write PLAN.md**:

   ```markdown
   # Implementation Plan - [Project Name]

   **Created**: [ISO 8601 timestamp]
   **Draft Reference**: DRAFT.md
   **Status**: Ready for Implementation

   ## Implementation Phases

   Commits are grouped by logical phase. Execute in order.

   ### Phase 1: Foundation

   - Commit 1: `feat(core): initialize project with base configuration` → See DRAFT.md#commit-1
   - Commit 2: `chore(deps): add required dependencies` → See DRAFT.md#commit-2

   ### Phase 2: Core Components

   - Commit 3: `feat(ui): add Button component` → See DRAFT.md#commit-3
   - Commit 4: `feat(ui): add Card component` → See DRAFT.md#commit-4
   - Commit 5: `feat(ui): add Form components` → See DRAFT.md#commit-5

   ### Phase 3: Services & Logic

   - Commit 6: `feat(api): implement API service` → See DRAFT.md#commit-6
   - Commit 7: `feat(auth): add authentication service` → See DRAFT.md#commit-7

   ### Phase 4: Integration

   - Commit 8: `feat(app): integrate components with services` → See DRAFT.md#commit-8
   - Commit 9: `feat(routes): add routing configuration` → See DRAFT.md#commit-9

   ### Phase 5: Testing & Polish

   - Commit 10: `test(integration): add integration tests` → See DRAFT.md#commit-10
   - Commit 11: `docs(readme): update documentation` → See DRAFT.md#commit-11

   ## Execution Order

   Linear execution with dependencies noted.

   1. `feat(core): initialize project` (no dependencies)
   2. `chore(deps): add dependencies` (requires #1)
   3. `feat(ui): add Button` (requires #1)
   4. `feat(ui): add Card` (requires #1)
   5. `feat(ui): add Form` (requires #3)
   6. `feat(api): implement API` (requires #1, #2)
   7. `feat(auth): add auth` (requires #6)
   8. `feat(app): integrate` (requires #3-7)
   9. `feat(routes): add routing` (requires #8)
   10. `test(integration): integration tests` (requires #8)
   11. `docs(readme): documentation` (requires all above)

   ## Success Criteria

   Implementation is complete when:

   - [ ] All commits from DRAFT.md are applied
   - [ ] All tests pass (`npm test`)
   - [ ] No TypeScript errors (`npm run type-check`)
   - [ ] Linting passes (`npm run lint`)
   - [ ] Application runs successfully (`npm run dev`)
   - [ ] All design requirements from [DESIGN.md/DESIGN_PROPOSED.md] are met
   ```

3. **Check Plan Mode Before Writing**:
   - If in plan mode:
     - Present the execution roadmap verbally (phases, commit order, success criteria)
     - Inform user: "To persist PLAN.md, please exit plan mode first."
     - Pause workflow until user exits plan mode
   - If not in plan mode: Write PLAN.md to disk

4. **Save PLAN.md**:
   - Write to project root or specified location
   - Ensure markdown formatting is clean

### Step 7: Subagent Review (Quality Gate)

**Actions**:

1. **Spawn Review Subagent**:
   - Use the Task tool to spawn a review subagent
   - Pass DRAFT.md, PLAN.md, and all design documents to the subagent
   - Use TodoWrite to track subagent review progress

2. **Review Checklist**:
   The subagent must verify:
   - **Architecture Alignment**: Plan aligns with DESIGN.md architecture patterns and component relationships
   - **Requirements Coverage**: All functional requirements from REQUIREMENTS.md have corresponding implementations AND tests
   - **Data Model Accuracy**: Data models and schemas match DATA.md specifications exactly
   - **UI Component Match**: UI components match UI.md specifications for layout, behavior, and styling
   - **Implementation Patterns**: Implementation patterns follow NOTES.md guidelines and decisions
   - **Test Coverage**: No requirement gaps or missing test coverage for any feature

3. **Review Output**:
   - Generate a review report documenting:
     - Items that pass verification
     - Issues found with specific references to design documents
     - Missing coverage areas
     - Recommendations for fixes

4. **Action on Issues**:
   - **If issues found**:
     - Update DRAFT.md to address gaps
     - Update PLAN.md if phase structure needs adjustment
     - Re-run review checklist to verify fixes
   - **If no issues**:
     - Proceed to Step 8 (Finalize Proposals)

### Step 8: Finalize Proposals

**Actions** (only if `*_PROPOSED.md` files existed):

1. **Check Plan Mode Before Finalizing**:
   - If in plan mode:
     - Present summary of files to be finalized
     - Inform user: "To finalize proposals (rename *_PROPOSED.md files), please exit plan mode first."
     - Pause workflow until user exits plan mode
   - If not in plan mode: Proceed with finalization

2. **Replace Proposals with Finals**:
   - For each `*_PROPOSED.md` file:
     - Copy content to target file (e.g., DESIGN_PROPOSED.md → DESIGN.md)
     - Confirm replacement with user
     - Remove `*_PROPOSED.md` file after successful copy

3. **Preserve Change Documentation**:
   - Keep all `*_CHANGE.md` files for historical reference
   - These document the evolution of the design

4. **Skip if No Proposals**:
   - If Step 1 found no proposals, skip this step entirely

### Step 9: Reporting

**Output Format**:

```
[OK] Command: plan-code $ARGUMENTS

## Summary

- Design source: [path to design file used]
- Proposals processed: [count or "none"]
- Change docs created: [list of *_CHANGE.md files or "none"]
- DRAFT.md: Created with [X] commits
- PLAN.md: Created with [Y] phases
- Quality Review: [PASSED/ISSUES FOUND AND RESOLVED]

## Files Created

- DRAFT.md: Implementation blueprint with [X] atomic commits
- PLAN.md: Execution roadmap with [Y] phases
- [*_CHANGE.md files if created]

## Commit Summary

1. `type(scope): description` - [X files]
2. `type(scope): description` - [Y files]
3. `type(scope): description` - [Z files]
...

## Phases Overview

- Phase 1 (Foundation): [X] commits
- Phase 2 (Core): [Y] commits
- Phase 3 (Features): [Z] commits
...

## Quality Review Summary

- Architecture alignment: [PASS/FIXED]
- Requirements coverage: [PASS/FIXED]
- Data model accuracy: [PASS/FIXED]
- UI component match: [PASS/FIXED]
- Implementation patterns: [PASS/FIXED]
- Test coverage: [PASS/FIXED]

## Next Steps

1. Review DRAFT.md for code accuracy
2. Review PLAN.md for execution order
3. Run `/takeover` to begin implementation
4. Execute commits in order, copy-pasting from DRAFT.md
```

## Examples

### Basic Usage - No Proposals Found (9-Step Workflow)

```bash
/plan-code
# Step 1: Scans for design documents - finds DESIGN.md, REQUIREMENTS.md, DATA.md
# Step 1: Creates initial todo list with TodoWrite for workflow tracking
# Step 1: Scans for *_PROPOSED.md files - none found
# Step 1: "No proposals found. Using original design files directly."
# Step 3: Reads all design docs, cross-references for completeness
# Step 3: Uses TodoWrite to track analysis progress
# Step 3: Generates DRAFT.md with 8 atomic commits
# Step 4: Uses AskUserQuestion to ask clarifying questions about design
#   - "Which state management approach: Redux, Zustand, or Context API?"
#   - "Should authentication use JWT or session-based?"
# Step 4: Updates DRAFT.md based on user answers
# Step 4: Uses TodoWrite to mark refinement tasks completed
# Step 5: Presents draft summary
#   - 8 commits across Foundation, Core, Features phases
#   - 24 files to create, 3 to modify
#   - User approves draft
# Step 6: Generates PLAN.md with 4 phases
# Step 7: Subagent reviews plan quality
#   - Uses TodoWrite to track review progress
#   - Verifies all REQUIREMENTS.md items have tests
#   - Confirms architecture matches DESIGN.md
#   - Review passes
# Step 8: Skipped (no proposals)
# Step 9: Reports success
#
# Output:
#   project/
#   ├── DRAFT.md    # 8 commits with full code
#   └── PLAN.md     # 4-phase execution roadmap
```

### With Approved Proposals (9-Step Workflow with Design Refinement)

```bash
/plan-code
# Step 1: Loads DESIGN.md, REQUIREMENTS.md, DATA.md, UI.md, NOTES.md
# Step 1: Creates todo list with TodoWrite
# Step 1: Finds DESIGN_PROPOSED.md and UI_PROPOSED.md
# Step 1: Presents summary:
#   "Found 2 proposals:
#    - DESIGN_PROPOSED.md: Adds Redis caching layer
#    - UI_PROPOSED.md: New dashboard components
#    Is this proposal approved?"
# User: "Yes, approved"
# Step 2: Compares proposals against originals
# Step 2: Creates DESIGN_CHANGE.md documenting:
#   - Added: Redis caching section
#   - Modified: Architecture diagram
#   - Added: Cache invalidation strategy
# Step 2: Creates UI_CHANGE.md documenting:
#   - Added: Dashboard component specs
#   - Modified: Navigation structure
# Step 3: Generates DRAFT.md with 12 commits
#   - Cross-references DATA.md for cache schema
#   - Cross-references REQUIREMENTS.md for feature coverage
# Step 4: Uses AskUserQuestion for design refinement
#   - "Redis deployment: self-hosted or managed service?"
#   - "Dashboard polling interval: 5s, 15s, or 30s?"
# Step 4: Updates DRAFT.md with refined decisions
# Step 5: Presents draft, user approves
# Step 6: Generates PLAN.md with 5 phases
# Step 7: Subagent reviews with TodoWrite tracking:
#   - Finds missing test for requirement REQ-042
#   - Updates DRAFT.md to add test
#   - Re-reviews, passes
# Step 8: Replaces DESIGN_PROPOSED.md → DESIGN.md
# Step 8: Replaces UI_PROPOSED.md → UI.md
# Step 8: Keeps DESIGN_CHANGE.md, UI_CHANGE.md
# Step 9: Reports success with quality review summary
#
# Output:
#   project/
#   ├── DESIGN.md         # Updated from proposal
#   ├── UI.md             # Updated from proposal
#   ├── DESIGN_CHANGE.md  # Change documentation
#   ├── UI_CHANGE.md      # Change documentation
#   ├── DRAFT.md          # 12 commits with full code
#   └── PLAN.md           # 5-phase execution roadmap
```

### Custom Design Path with Change Description

```bash
/plan-code --design=docs/specs/DESIGN.md --change="add authentication"
# Step 1: Creates todo list with TodoWrite
# Step 1: Scans docs/specs/ for all design documents
# Step 1: Loads DESIGN.md, REQUIREMENTS.md, REFERENCE.md from docs/specs/
# Step 1: Scans for proposals - none found
# Step 1: Using docs/specs/DESIGN.md directly
# Step 3: Reads design, focuses on authentication requirements
# Step 3: Cross-references REFERENCE.md for auth API specs
# Step 3: Generates DRAFT.md with auth-focused commits:
#   - Commit 1: feat(auth): add auth service
#   - Commit 2: feat(auth): add login component
#   - Commit 3: feat(auth): add protected routes
#   - Commit 4: test(auth): add auth tests
# Step 4: Uses AskUserQuestion for auth-specific refinement
#   - "Authentication method: OAuth2, JWT, or API keys?"
#   - "Session storage: cookies, localStorage, or memory?"
# Step 4: Updates DRAFT.md based on answers
# Step 5: Presents auth implementation draft
# Step 6: Generates PLAN.md focused on auth phase
# Step 7: Subagent verifies auth requirements coverage
# Step 9: Reports success
```

### Proposal Not Approved

```bash
/plan-code
# Step 1: Finds DESIGN_PROPOSED.md
# Step 1: "Found proposal: DESIGN_PROPOSED.md
#          Changes: Migrate from REST to GraphQL
#          Is this proposal approved?"
# User: "No, need to reconsider the GraphQL migration"
# Command exits with message:
#   "Proposal not approved. Please refine the proposal in
#    DESIGN_PROPOSED.md and run /plan-code again when ready."
```

### Draft Revision Requested

```bash
/plan-code
# Steps 1-3 complete, DRAFT.md generated
# Step 4: Uses AskUserQuestion for design refinement
# Step 5: Presents draft with 6 commits
# User: "Split commit 3 into smaller pieces"
# Step 5: Updates DRAFT.md:
#   - Original Commit 3 split into 3a, 3b, 3c
#   - Re-presents draft with 8 commits
# User: "Approved"
# Step 6: Generates PLAN.md
# Step 7: Subagent reviews updated plan
# Step 9: Reports success with 8 commits
```

### Running in Plan Mode

```bash
/plan-code
# Step 1: Loads all design documents - works in plan mode
# Step 1: Creates todo list, scans for DESIGN.md, REQUIREMENTS.md, etc.
# Step 1: Detects DESIGN_PROPOSED.md, asks for approval - works
# Step 2: Analyzes proposal, compares with original
# Step 2: Plan mode detected - presents changes verbally:
#   "Changes in DESIGN_PROPOSED.md:
#    - Added: Redis caching section
#    - Modified: Architecture diagram
#    - Removed: Legacy sync approach
#    To persist DESIGN_CHANGE.md, please exit plan mode first."
# User exits plan mode (approves plan or uses /model)
# Step 2: Writes DESIGN_CHANGE.md
# Step 3: Generates DRAFT.md with 8 commits
# Step 4: Asks clarifying questions via AskUserQuestion
# Step 5: Presents draft summary, user approves
# Step 6: Generates PLAN.md
# Step 7: Subagent reviews
# Step 8: Finalizes proposals
# Step 9: Reports success
```

### Error - No Design Specification

```bash
/plan-code
# Step 1: Scans for design documents - none found
# Step 1: Scans for proposals - none found
# Step 1: Looks for DESIGN.md - not found
# Error: "No design specification found.
#         Looked for: DESIGN.md, REQUIREMENTS.md, DATA.md, UI.md, NOTES.md, REFERENCE.md
#         Suggestion: Run '/spec-code' to create design specifications first
#         Alternative: Specify path with --design=path/to/DESIGN.md"
```

### Error - Design Too Vague

```bash
/plan-code --design=docs/DESIGN.md
# Step 1: No proposals, using docs/DESIGN.md
# Step 3: Reads DESIGN.md - insufficient detail
# Error: "Design specification too vague for implementation planning.
#         Missing: Component specifications, API definitions, data models
#         Suggestion: Run '/spec-code --sync-template' to add required sections
#         Cannot generate meaningful commit blueprint without implementation details."
```

### Integration with /takeover

```bash
# Step 1: Generate implementation plan (9-step workflow)
/plan-code
# Creates DRAFT.md with 10 commits
# Creates PLAN.md with 4 phases

# Step 2: Execute the plan
/takeover
# Reads PLAN.md for execution order
# References DRAFT.md for code to copy-paste
# Executes commits in sequence:
#   - Creates files from Commit 1
#   - Runs tests to verify
#   - Commits with message from DRAFT.md
#   - Proceeds to Commit 2
#   - ... continues through all commits
```

### Large Project with Multiple Phases (Full 9-Step Workflow)

```bash
/plan-code
# Step 1: Loads all design documents (DESIGN.md, REQUIREMENTS.md, DATA.md, UI.md, NOTES.md, REFERENCE.md)
# Step 1: Creates comprehensive todo list with TodoWrite
# Step 1: Finds DESIGN_PROPOSED.md (major refactor)
# Step 1: User approves
# Step 2: Creates DESIGN_CHANGE.md (extensive changes)
# Step 3: Generates DRAFT.md with 25 commits across:
#   - Foundation: 3 commits
#   - Data Layer: 5 commits
#   - Business Logic: 7 commits
#   - API Layer: 4 commits
#   - UI Components: 4 commits
#   - Integration: 2 commits
# Step 4: Uses AskUserQuestion for comprehensive design refinement:
#   - "Database: PostgreSQL with Prisma or MongoDB with Mongoose?"
#   - "API style: REST, GraphQL, or tRPC?"
#   - "State management: Redux Toolkit or Zustand?"
#   - "Testing strategy: Jest + RTL or Vitest + Testing Library?"
# Step 4: Updates DRAFT.md based on all decisions
# Step 4: Uses TodoWrite to mark refinement complete
# Step 5: Presents summary:
#   "25 commits planned across 6 phases
#    52 new files, 12 modified files
#    Estimated implementation: significant
#    Approve draft?"
# User: "Approved"
# Step 6: PLAN.md with 6 phases, clear dependencies
# Step 7: Subagent performs comprehensive review:
#   - Uses TodoWrite to track review items
#   - Checks all 47 requirements from REQUIREMENTS.md
#   - Verifies data models against DATA.md
#   - Confirms UI specs match UI.md
#   - Identifies 2 missing tests, updates DRAFT.md
#   - Re-reviews, all checks pass
# Step 8: Finalizes DESIGN.md from proposal
# Step 9: Reports with full breakdown and quality summary
#
# Output includes clear execution path
# /takeover can systematically execute each commit
```
