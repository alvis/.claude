---
name: update-agent
description: Update one or more existing agent definitions to the current template or an explicit change request while preserving each role's useful expertise, triggers, context assignments, and collaboration links. Use for agent maintenance or migration; use create-agent when no suitable agent exists.
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Write, Edit, Glob, Grep
argument-hint: "<agent path, name, or glob> [--changes=...]"
---

# Update agent

Update selected existing agents only. An empty selector is not permission to update every agent.

## Inputs and boundaries

- Required explicit agent path, name, or glob.
- Optional changes to frontmatter, triggers, context links, or role guidance.
- Read `../../constitution/templates/agent.md` and each selected agent's source files before editing.
- Preserve unique role expertise and `initialPrompt`; do not create, delete, or silently change protected characteristics.

Reject an unresolved selector, missing template, malformed source, or request to create a new role.

## Workflow

1. Resolve the selector to an exact file list and record the requested end state.
2. Compare each `base.md` and `frontmatter/claude.json` with the live template and real callers. Fold approved changes into existing sections; remove superseded wording instead of appending an update log.
3. Delegate independent batches only when they are large enough to justify it. Give each worker exact paths, boundaries, and acceptance checks.
4. Validate trigger ownership, context references, JSON/frontmatter, required `initialPrompt`, and compatibility with neighboring agents. Run strict Claude validation and repository policy checks.
5. Report selected files, preserved behavior, changed fields, validation evidence, and unresolved ambiguity.

## Completion

No selected agent is complete until its stitched output validates and its trigger surface remains distinct. Keep the document concise; personas, diagrams, and fixed-phase ceremony are not required.
