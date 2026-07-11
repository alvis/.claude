---
name: plan-code
description: Generate DRAFT.md as a commit blueprint and PLAN.md as an execution roadmap from an approved proposal or specification. Use when planning implementations, defining atomic commits, documenting change proposals, or preparing a coding workflow with explicit verification and ownership boundaries.
model: opus
context: fork
agent: general-purpose
allowed-tools: Read, Glob, Grep, Bash, Write, Task, TodoWrite, AskUserQuestion, ExitPlanMode
argument-hint: "[--design=DESIGN.md] [--change=\"description\"]"
---

# Plan Code

Analyzes design proposals or existing specifications, generates a comprehensive DRAFT.md with copy-paste-ready commit blueprints, and produces a lightweight PLAN.md execution roadmap that transforms approved designs into actionable implementation plans with atomic, testable commits. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. When a proposal modifies an existing DRAFT.md or PLAN.md, the revised plan must read as a single coherent roadmap — not the prior plan with a "Proposed changes" appendix or a divergent second step list running in parallel beside the original.

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

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Load All Design Documents & Detect Proposals

1. **Validate Environment**:
   - Confirm working directory is a git repository
   - Parse --design argument (default: look in current directory)
   - Parse --change argument if provided

2. **Scan for Design Documents**:
   - Find DESIGN.md, REQUIREMENTS.md, DATA.md, UI.md, NOTES.md, REFERENCE.md
   - Read and parse each found document

3. **Scan for Proposals**:
   - Find `*_PROPOSED.md` files
   - Present summary and ask for approval

4. **Handle Proposal Detection**:
   - If approved: Proceed to Step 2
   - If no proposals: Skip to Step 3

### Step 2: Analyze Approved Proposal & Document Changes

1. **Compare Against Originals**
2. **Generate Change Documentation** (`*_CHANGE.md`)

### Step 3: Generate DRAFT.md

1. **Gather Implementation Context**
2. **Analyze Implementation Architecture**
3. **Assess Technology Stack**
4. **Check Code Quality and Issues**
5. **Review Tests and Coverage**
6. **Cross-Reference ALL Design Documents**
7. **Plan Atomic Commits**
8. **Write DRAFT.md** with:
   - File Structure showing commit associations
   - Commit Plan with copy-paste ready code
   - Each commit: atomic, testable, 100% coverage

**Commit Requirements Checklist** (every commit in DRAFT.md must satisfy):

- [ ] Self-contained (independently testable)
- [ ] 100% test coverage for its scope
- [ ] Clear separation of concerns from other commits
- [ ] Conventional commit format: `type(scope): description`
- [ ] Multiple commits per phase allowed
- [ ] Full file contents provided — copy-paste ready

### Step 4: Interactive Design Refinement

1. **Ask Clarifying Questions** via AskUserQuestion:
   - Each question offers 2–4 alternatives with clear rationales
   - Focus on areas where `--change` is proposed or design is ambiguous
   - Question categories:
     - **Architecture**: patterns, structure, modularity
     - **Technology**: libraries, frameworks, tools
     - **Implementation**: trade-offs between approaches
     - **Constraints**: performance, scalability, maintainability, edge cases
   - Example: "Which state management approach: Redux, Zustand, or Context API?"

2. **Update DRAFT.md Based on Answers** — adjust commit structure if architectural decisions change; document rationale in commit descriptions.

3. **User Review Cycle** — repeat follow-up questions via AskUserQuestion until the user is satisfied with the draft.

### Step 5: Present Draft for Review

1. **Generate Draft Summary**
2. **Request Approval**

### Step 6: Generate PLAN.md (on approval)

1. **Group Commits by Phase**
2. **Write PLAN.md** with:
   - Implementation Phases
   - Execution Order
   - Success Criteria

### Step 7: Subagent Review (Quality Gate)

1. **Spawn Review Subagent** via the Task tool, passing DRAFT.md, PLAN.md, and all design documents.

2. **Review Checklist** — the subagent must verify:
   - **Architecture Alignment**: plan matches DESIGN.md patterns and component relationships
   - **Requirements Coverage**: every REQUIREMENTS.md item has implementation AND tests
   - **Data Model Accuracy**: schemas match DATA.md exactly
   - **UI Components**: components match UI.md layout, behavior, styling
   - **Implementation Patterns**: follow NOTES.md guidelines and decisions
   - **Test Coverage**: no requirement gaps, no missing tests

3. **Action on Issues**: if issues found, update DRAFT.md / PLAN.md and re-run the checklist; otherwise proceed to Step 8.

### Step 8: Finalize Proposals

1. **Replace Proposals with Finals**
2. **Preserve Change Documentation**

### Step 9: Reporting

**Output Format**:

```
[OK] Command: plan-code $ARGUMENTS

## Summary

- Design source: [path]
- Proposals processed: [count]
- DRAFT.md: Created with [X] commits
- PLAN.md: Created with [Y] phases
- Quality Review: [PASSED]

## Files Created

- DRAFT.md: Implementation blueprint
- PLAN.md: Execution roadmap
- [*_CHANGE.md files]

## Commit Summary

1. `type(scope): description` - [X files]
2. `type(scope): description` - [Y files]

## Phases Overview

- Phase 1 (Foundation): [X] commits
- Phase 2 (Core): [Y] commits

## Next Steps

1. Review DRAFT.md for code accuracy
2. Review PLAN.md for execution order
3. Run `/takeover` to begin implementation
```

## 📝 Examples

### Basic Usage

```bash
/plan-code
# Scans for design documents
# Generates DRAFT.md with atomic commits
# Creates PLAN.md with phases
```

### With Design Path

```bash
/plan-code --design=docs/DESIGN.md
# Uses specific design file
```

### With Change Description

```bash
/plan-code --change="add authentication"
# Focuses on authentication-related changes
```

### With Proposals

```bash
/plan-code
# Finds DESIGN_PROPOSED.md
# Asks for approval
# If approved: Creates DRAFT.md, PLAN.md, DESIGN_CHANGE.md
```

### Error Cases

```bash
/plan-code
# Error: No design specification found
# Suggestion: Run '/spec-code' first

/plan-code --design=docs/DESIGN.md
# Error: Design too vague
# Suggestion: Add required sections
```
