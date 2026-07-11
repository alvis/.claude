---
name: react
description: Use when creating, editing, reviewing, or routing work involving React, JSX, hooks, components, accessibility behavior, project structure, tests, or Storybook stories; this router selects React standards while Coding owns generic execution.
model: sonnet
allowed-tools: Read, Glob, Grep, Skill
---

# React Standards Router

Load only the React standards relevant to the current work. This skill supplies context and routes work; it does not create implementation teams or duplicate another skill's workflow.

## Standards

Standards live under `${CLAUDE_PLUGIN_ROOT}/constitution/standards/`:

- `accessibility`: semantics, keyboard access, ARIA, focus, forms, and screen readers.
- `components`: component boundaries, props, state, naming, and performance.
- `hooks`: dependencies, cleanup, stable references, return shapes, and composition.
- `project-structure`: placement, feature boundaries, and promotion paths.
- `storybook`: story naming, coverage, controls, interactions, and purity.

Read `write.md` before authoring and `scan.md` when reviewing. Read an individual rule only after its scan identifies a candidate violation.

## Routing

- Mechanical enforcement across one or more eligible files: use `react:lint`.
- Feature or bug implementation: use `coding:write-code` with the applicable React standards.
- Generic semantic review: use `coding:review-code` with the applicable React standards.
- Visual design or runtime diagnosis may be recommended through an optional web skill if available; otherwise state the recommendation without invoking it.

When the task is React linting, route to `react:lint`; never route it through generic lint first.
