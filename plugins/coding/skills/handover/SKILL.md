---
name: handover
description: Persist CONTEXT.md, NOTES.md, and PLAN.md for later continuation of coding work. Use when pausing implementation or transferring repository state; this skill records the current session and does not create or execute a cross-domain plan.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion
argument-hint: "[prefix]"
---

# Work Handover Documentation

Persist `CONTEXT.md`, `NOTES.md`, and `PLAN.md` so the next worker can
continue without sharing the current session context. `coding:takeover` owns
resuming work from these documents.

## Boundaries

- Use for: recording session state — background, file status, decisions,
  implementation insights, and remaining tasks — into the three handover
  documents when pausing or transferring work.
- Do not use for: git operations (commit, push, branch management), builds,
  tests, deployments, code review or analysis, or modifying any project file
  other than the handover documents; it does not replace project-management
  or issue-tracking tools.

## Inputs

- **Required**: none — defaults to `CONTEXT.md`, `NOTES.md`, and `PLAN.md` in
  the working directory.
- **Optional**: a prefix argument producing `<prefix>-CONTEXT.md`,
  `<prefix>-NOTES.md`, and `<prefix>-PLAN.md` (e.g. `sprint1-CONTEXT.md`);
  reject prefixes containing slashes or file extensions.
- **Prerequisites**: the working directory is a git repository.

## Workflow

1. **Analyze project context.** Validate the prefix and git repository per
   Inputs, rejecting invalid input with a clear message. Retrieve all todos
   via TodoRead, preserving status, relationships, and patterns noted in task
   content. Gather git state: current branch, `git status`, staged and
   unstaged diffs, untracked files (`git ls-files --others
   --exclude-standard`), and recent commit messages. Identify background,
   goals, decisions, architectural patterns, and conventions from project
   docs and commit history.
2. **Classify every changed or planned file** into three categories with
   substates, recording per file: path, status with substate, relevant
   TODO/FIXME/REFACTOR comments, what specifically remains, and blockers.
   - Completed: committed and unchanged (absent from git status).
   - In progress: modified or staged — substate `need-completion`
     (TODO/FIXME comments), `need-fixing` (test failures, errors, or
     HACK/WORKAROUND comments), `need-linting` (style violations), or
     `need-refactoring` (REFACTOR comments or quality concerns).
   - Planned: untracked or referenced in TODO comments — substate
     `need-draft` (skeleton required) or `need-testing` (no test coverage).
3. **Extract content and prune.** Map content to documents — CONTEXT.md:
   background and goals, active reference documents, impactful decisions,
   current architectural patterns, gotchas and workarounds, dependency and
   configuration changes, accepted assumptions and their recheck triggers;
   NOTES.md: implementation issues and the solutions applied, provenance-labeled
   discoveries, deviations, workarounds still needed, pending decisions,
   invalidated plan steps, hard-won gotchas, and only what was learned through
   doing; PLAN.md: goal breakdown, incomplete tasks, active phases, current
   dependencies, active risks, unmet success criteria, and evidence that
   requires a pivot. When updating existing files, proactively remove content
   useless to future execution: outdated context, resolved issues (keep the lesson
   only), details of completed tasks (keep path plus one-line summary), stale
   references, and verbose history — archive it under a "Historical Notes"
   section at the document bottom. Keep only the last 5 commits under "Recent
   Changes", condense completed files into a summary with the top 3-5 listed,
   rewrite any section exceeding 100 lines down to actionable items, and
   consolidate similar gotchas and decisions into single entries.
4. **Consult the user on open decisions** found in steps 1-3 (pending
   architecture, technology, scope, or configuration choices) via
   AskUserQuestion — never make architectural, technical, or strategic
   decisions unilaterally. Follow
   [references/decision-consultation.md](references/decision-consultation.md)
   for identification, categorization, the mandatory "Perform research" and
   "Defer decision" options, and outcome processing.
5. **Write the documents.** Generate one timestamp via
   `date -u +"%Y-%m-%dT%H:%M:%SZ"` and use it for every "Last Updated",
   "Created", and "Updated" field — never placeholders. Update existing files
   in place: refresh dynamic sections (Current State, File Status, Recent
   Changes), preserve historical content, and integrate decision outcomes —
   finalized decisions with rationale into CONTEXT.md "Key Decisions &
   Patterns", accepted assumptions with recheck triggers into CONTEXT.md,
   deferred decisions into NOTES.md "Pending Decisions", research files and
   deviations referenced from NOTES.md, and decision-driven, blocked, or
   invalidated tasks plus pivot signals into PLAN.md. Create missing files from
   the structures in
   [references/document-templates.md](references/document-templates.md).
6. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- All three documents exist under the requested names and follow the
  template structure.
- Every timestamp is a real ISO 8601 value from the `date` command.
- Each decision identified in step 4 was consulted, and its outcome landed in
  the correct document section.
- Accepted assumptions name their evidence and recheck triggers; deviations and
  invalidated plan steps are preserved, and every pivot signal has an affected
  phase or task.
- No project file outside the handover documents was modified.

## Completion

Emit the summary defined in
[references/output-format.md](references/output-format.md): file paths,
classification counts, decisions consulted with outcomes, plan updates,
research files, the document-section checklist, and next steps. See
[references/examples.md](references/examples.md) for usage variants (default,
custom prefix, updates, error cases) and the takeover continuation scenario.
