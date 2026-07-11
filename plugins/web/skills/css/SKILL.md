---
name: css
description: Scaffold or maintain a project's root stylesheet using the CSS-only light, dark, and system color-mode contract. Use for theme.css, globals.css, or app.css setup, migration from class-driven dark mode, semantic token wiring, or color-mode corrections. This skill edits CSS only and never ships JavaScript.
argument-hint: "[project root or stylesheet] [--tokens=<roles>]"
allowed-tools: Read, Edit, Write, Glob, Grep
---

# CSS color modes

Create or update one root stylesheet so color modes remain CSS-only and follow the web constitution's `CSS-MODE-*` rules. The consumer may toggle `data-theme`; this skill does not add a runtime controller or edit components.

## Inputs and boundaries

- Locate `theme.css`, `globals.css`, `app.css`, or an explicitly supplied stylesheet.
- Read existing tokens and Tailwind/PostCSS configuration when present.
- Preserve project colors and existing layers; reject ambiguous multiple entry points until the user selects one.
- Stop and report conflicts such as JS-only theme switching or unsupported selectors before editing.

## Workflow

1. Inspect the selected stylesheet and the project's existing color-mode selectors.
2. Use `references/theme.css.template` as the structural guide: keep tokens inside `@layer theme`, define `color-scheme`, provide `:root` defaults, and add `:root[data-theme="light"]`/`[data-theme="dark"]` overrides.
3. Preserve the two-tier token contract (`--theme-*` source values mapped to `--ui-*` semantic roles). Add only requested roles.
4. Re-read the complete stylesheet and compare each `CSS-MODE-*` rule. If a runtime toggle is needed, return `references/runtime-toggle.md` to the consumer instead of writing JavaScript.

## Completion

Report the edited stylesheet, tokens added or preserved, mode behavior, conflicts, and rule-by-rule verification. Leave runtime toggling and component changes to the application owner.
