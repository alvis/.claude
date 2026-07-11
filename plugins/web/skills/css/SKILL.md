---
name: css
description: Scaffold or maintain a project's root stylesheet using the CSS-only light, dark, and system color-mode contract. Use for theme.css, globals.css, or app.css setup, migration from class-driven dark mode, semantic token wiring, or color-mode corrections. Detect conflicts, obtain migration approval, preserve existing tokens, and edit CSS only.
argument-hint: "[project root or stylesheet] [--tokens=<roles>]"
allowed-tools: Read, Edit, Write, Glob, Grep, AskUserQuestion
---

# CSS color modes

Create or update exactly one root stylesheet so color modes satisfy `CSS-MODE-01..04`. This skill never writes JavaScript, application components, or an unapproved framework migration. A consumer may toggle `data-theme`; system mode is the absence of that attribute.

## Locate and classify

1. If an explicit stylesheet is supplied, validate that it is inside the target project. Otherwise search, in order, for `theme.css`, `globals.css`, `app.css`, `styles/index.css`, then entry-shaped `src/**/*.css`, excluding generated/vendor directories.
2. If multiple plausible roots remain, list them and ask which one owns global tokens. Do not guess. If none exists, propose `src/theme.css` when `src/` exists, otherwise `theme.css` at the root.
3. Read the complete target plus Tailwind/PostCSS configuration. Search project CSS/config/runtime source for `prefers-color-scheme`, `data-theme`, `.dark`, `[data-mode]`, `[data-color-scheme]`, `darkMode: 'class'`, `@layer theme`, `--theme-`, `--ui-`, and code that adds/removes theme classes.
4. Record detection state: chosen file, existing mode selectors, raw and semantic tokens, framework integration, conflicts, and whether creation or merge is proposed.

## Approval and non-destructive branch

If the project already uses `.dark`, a noncanonical attribute, Tailwind class mode, JS class toggling, duplicate theme layers, or incompatible token ownership, stop before editing. Present the exact occurrences and a bounded migration plan. Obtain explicit approval for every file beyond the selected stylesheet; without it, leave source untouched and return the plan.

If the existing contract is compatible, proceed without ceremony. Preserve custom colors, imports, layer order, comments that explain policy, unknown token roles, and framework directives. Never replace the entire stylesheet merely to match the template. Use `references/theme.css.template` as structural guidance and `references/runtime-toggle.md` as consumer handoff, both resolved from `${CLAUDE_SKILL_DIR}`.

## Write procedure

1. Create the proposed file only after its location is unambiguous. For an existing file, merge into its `@layer theme` block or insert a new block after imports and required framework directives.
2. Define tier-one `--theme-light-<role>` and `--theme-dark-<role>` source values once. Map them to tier-two `--ui-<role>` semantic values; add only requested or already-used roles.
3. Keep explicit overrides exactly at `:root[data-theme="light"]` and `:root[data-theme="dark"]`.
4. Keep system branches at `:root:not([data-theme])` inside both light and dark `prefers-color-scheme` queries.
5. Put every mode branch inside `@layer theme` and set the matching `color-scheme` value.
6. If runtime toggling is requested, point to `${CLAUDE_SKILL_DIR}/references/runtime-toggle.md`; do not implement the JavaScript here.

## CSS-MODE verification

Re-read the full resulting stylesheet and check each role across every branch:

- `CSS-MODE-01`: explicit selectors are only `:root[data-theme="light"]` and `:root[data-theme="dark"]`; fail on `.dark`, `[data-mode]`, or `[data-color-scheme]` in the owned contract.
- `CSS-MODE-02`: both system media queries contain `:root:not([data-theme])` and map all active roles.
- `CSS-MODE-03`: all mode declarations are inside `@layer theme` and every branch sets correct `color-scheme`.
- `CSS-MODE-04`: each `--ui-<role>` maps to complete light/dark tier-one tokens; no branch or role is missing.

Also verify balanced CSS syntax, imports/layers retained in legal order, and no non-approved files changed. If a check fails, correct the owned CSS and repeat; if correction requires an unapproved migration, stop partial and show the required diff.

Return status, stylesheet path, created/edited files, detection summary, approved migration actions, tokens preserved/added, per-rule `CSS-MODE` results, runtime-toggle reference, and unresolved conflicts.
