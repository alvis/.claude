---
name: handover
description: Create/update detailed work handover notes for seamless continuation. Use when pausing work, switching contexts, documenting progress, or enabling another developer to continue your work.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion
argument-hint: [prefix]
---

# Work Handover Documentation

Generates comprehensive handover documentation capturing current project & work context across three complementary files: CONTEXT.md (status & decisions), NOTES.md (implementation insights & solutions), and PLAN.md (goals & tasks) for seamless project continuation without requiring prior context

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not perform git operations like commit, push, or branch management
- Does not execute project builds, tests, or deployments
- Does not analyze code quality or perform code reviews
- Does not modify any project files except the handover documents themselves
- Does not replace project management tools or issue tracking systems

**When to REJECT**:

- When file path argument points to non-markdown files
- When requested to perform git operations instead of documentation
- When asked to modify project source code
- When the working directory is not a git repository
- When user requests code analysis instead of handover documentation

- Untracked files: !`git ls-files --others --exclude-standard`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 0: Analyze Project Context

Before performing handover documentation, deeply analyze the complete project context:

- **Project State Analysis**: Examine git status, recent commits, file changes to understand current work trajectory
- **Existing Work Review**: Read all current todos from TodoRead to understand ongoing tasks and their status
- **Context Discovery**: Identify background, goals, decisions from project docs and commit history
- **Pattern Recognition**: Detect architectural patterns, established conventions, recurring issues
- **Comprehensive Synthesis**: Integrate all gathered context into coherent handover documentation

### Step 1: Parse Arguments and Validate

- Extract the optional prefix argument from $ARGUMENTS
- If no prefix provided, use empty prefix (default files: CONTEXT.md, NOTES.md, PLAN.md)
- If prefix provided, construct file names: [prefix]-CONTEXT.md, [prefix]-NOTES.md, [prefix]-PLAN.md
- Validate prefix format (no slashes, no extensions)
- Verify the working directory is a git repository
- If validation fails, reject with clear error message

**File naming examples**:

- Default: `CONTEXT.md`, `NOTES.md`, `PLAN.md`
- With prefix: `sprint1-CONTEXT.md`, `sprint1-NOTES.md`, `sprint1-PLAN.md`

### Step 2: Discover Project Context

- Use TodoRead to retrieve all existing todos from the task tracker
- Organize todos by status for inclusion in PLAN.md:
- Preserve task relationships and dependencies if indicated in task content
- Note any context or patterns from task descriptions
- Run git commands to gather current state (branch, status, recent commits)
- Capture recent commit messages for context on what was done

### Step 3: Classify File Status

Classify each file into one of three categories with detailed substates:

- **✅ Completed**: Files that are committed and unchanged (not in git status output)
- **🚧 In Progress**: Files that are modified or staged (in git diff or git diff --cached), with substates:
  - `need-completion`: Files with TODO/FIXME comments indicating incomplete implementation
  - `need-fixing`: Files with test failures, errors, or HACK/WORKAROUND comments
  - `need-linting`: Files with linting/formatting issues or style violations
  - `need-refactoring`: Files with REFACTOR comments or code quality concerns
- **📋 Planned**: Untracked files or files mentioned in TODO comments, with substates:
  - `need-draft`: Untracked files or files with mostly TODOs requiring initial skeleton
  - `need-testing`: Files without corresponding test files or lacking test coverage

For each file, gather:

- File path and type
- Current status with substate (e.g., "🚧 need-completion", "📋 need-draft")
- Relevant TODO/FIXME/REFACTOR comments if present
- Brief description of what specifically needs to be done
- Any blockers or dependencies

### Step 4: Extract Key Information and Apply Intelligent Pruning

When updating existing handover files, apply intelligent pruning to keep documentation focused and actionable:

**Pruning Rules**:

- **Proactive Content Removal**: When writing to handover docs, the agent MUST proactively remove any content that is not useful for future execution phases, including:
  - Outdated context that no longer affects current work
  - Resolved issues and their detailed resolution steps (keep only lessons learned)
  - Detailed descriptions of completed tasks (keep file path + brief summary only)
  - Stale references to deprecated patterns or removed dependencies
  - Historical discussions that don't inform current decisions
  - Verbose background information that can be condensed
- Keep only last 5 commits in "Recent Changes" (archive older commits to Historical Notes)
- Condense completed files into summary statements (e.g., "15 files completed" with top 3-5 listed)
- Rewrite sections exceeding 100 lines to focus on actionable items only
- Consolidate similar gotchas/decisions into single entries
- Remove detailed descriptions of completed tasks (keep file path + brief summary only)
- Archive verbose historical content to "Historical Notes" section at document bottom
- Remove outdated context that no longer affects current work

Search for and document (with pruning applied):

**For CONTEXT.md**:

- Background & context - why this work is being done (concise, actionable only; remove outdated context)
- Goals & objectives - current goals only (remove completed goals)
- Reference documents - active/relevant links only (remove stale links)
- Important decisions made - recent and impactful only (consolidate similar decisions)
- Architectural patterns used - current patterns only (remove deprecated patterns)
- Gotchas and workarounds - consolidate similar items
- Dependencies added or modified - recent changes only
- Configuration changes - current config only (remove historical config)

**For NOTES.md**:

- **Implementation Issues**: Problems encountered during implementation that required multiple tool calls to resolve
- Solutions applied - keep distinct solutions for issues faced (merge duplicates)
- Exploration attempts - keep failures only if relevant to understanding current state
- Key discoveries - document insights from actual implementation challenges
- Workarounds - document any temporary workarounds that might be needed
- Dependencies & gotchas - issues that took time to discover and understand
- Keep entries concise and actionable - only document what was learned through doing

**For PLAN.md**:

- Goals breakdown - current goals
- Task lists - incomplete tasks only, archive completed
- Phases/milestones - active phases (archive completed)
- Dependencies - current dependencies only
- Decisions made - impactful decisions only
- Risks identified - active risks only
- Success criteria - unmet criteria only
- Current todos - actionable items only
- Task progress - incomplete tasks focus
- Pending work items - prioritized items

### Step 5: Consult User on Key Decisions

Before documenting handover content, identify decision points from Steps 0-4 (TODOs, pending architecture/tech/scope/config choices) and consult the user via AskUserQuestion. NEVER make architectural, technical, or strategic decisions without user consultation. See `references/decision-consultation.md` for the full decision-identification, categorization, consultation, and outcome-processing procedure (including the mandatory "Perform research" / "Defer decision" options and worked example).

### Step 6: Generate or Update Handover Documents

**First, generate current timestamp**:

- Execute: `date -u +"%Y-%m-%dT%H:%M:%SZ"` to get current ISO 8601 timestamp
- Store the result to use consistently across all documents
- Use this actual timestamp (not placeholders) for all "Last Updated", "Created", "Updated" fields

**Then, prepare decision-based content from Step 5**:

Before generating/updating documents, organize all decision outcomes from Step 5:

- **Finalized Decisions**: List of decisions made with rationale and alternatives considered
- **Deferred Decisions**: List of decisions deferred with context for future resolution
- **Research Files**: List of generated research files with their topics
- **Decision-Driven Tasks**: New tasks resulting from finalized decisions
- **Blocked Tasks**: Tasks that cannot proceed due to deferred decisions

**Apply Pruning Principles**: Before updating or creating files, remember to proactively remove any content that is not useful for future execution phases (see Step 4 pruning rules). This ensures handover documentation remains focused and actionable.

If the files exist:

- Read the existing content of each file
- Update the "Last Updated" timestamp with the actual current timestamp from `date` command
- Refresh dynamic sections (Current State, File Status, Recent Changes)
- **Integrate decision outcomes from Step 5**:
  - Add finalized decisions to CONTEXT.md "Key Decisions & Patterns"
  - Add deferred decisions to NOTES.md "Open Questions"
  - Update PLAN.md with decision-driven tasks and blocked tasks
  - Reference research files in NOTES.md
- Append new items where appropriate
- Preserve historical content

If the files don't exist:

- Create new documents with complete structure for all three files
- Use actual timestamp from `date` command for all timestamp fields
- **Include decision outcomes from Step 5** in initial content

**Document Templates**: Use the CONTEXT.md, NOTES.md, and PLAN.md structures defined in `references/document-templates.md`. All timestamps must use ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`) generated via `date -u +"%Y-%m-%dT%H:%M:%SZ"`.

### Step 7: Reporting

Emit the final summary using the format in `references/output-format.md` (covers file paths, classification counts, decisions consulted, plan updates, research files, document-section checklist, and next steps).

## 📝 Examples

See `references/examples.md` for usage variants (default invocation, custom prefix, updating existing files, error cases) and the three-file workflow / takeover continuation scenario.
