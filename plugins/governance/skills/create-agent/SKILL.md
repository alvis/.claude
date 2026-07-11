---
name: create-agent
description: Create a new specialist agent from the repository agent template as base.md plus frontmatter/claude.json. Use when adding a distinct role, trigger surface, or delegation capability that existing agents do not own. Confirm model, effort, and permission settings before authoring unless explicit overrides are supplied.
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Write, Edit, Glob, Grep, AskUserQuestion
argument-hint: "<role description> [--model=...] [--effort=...] [--permission=...] [--yes]"
---

# Create agent

Create one new agent definition. Keep the role distinct from existing agents; `update-agent` owns changes to existing definitions.

## Inputs

- Required role description or proposed name.
- Optional `--model`, `--effort`, `--permission`, and `--yes` overrides.
- Read `../../constitution/templates/agent.md`, `../../constitution/references/context-catalog.md`, and the current agent directory before writing.

Reject an unclear role, a duplicate capability, an invalid name, or a missing template. Do not modify existing agents.

## Workflow

1. Inspect neighboring agents and resolve the kebab-case name, positive trigger description, owned outcome, exclusions, and context assignments.
2. Recommend model, effort, and permission settings from the role. Ask for confirmation unless an override or `--yes` is present; record the decision.
3. Delegate the two-file authoring task with the exact paths and requirements. The author writes `agents/<name>/base.md` and `agents/<name>/frontmatter/claude.json`; no generated file should contain placeholders or unrelated workflow policy.
4. Validate JSON/frontmatter, required `initialPrompt`, trigger boundaries, context references, and template shape. If validation fails, send only the reported corrections back to the author and re-check.
5. Report files, settings, trigger examples, validation commands, and any unresolved concern.

## Completion

The new agent is complete only when both source files exist, the role is non-overlapping, and the stitched output passes the repository validator. Keep the base body focused on the agent's role; do not add personas, diagrams, or phase ceremony.
