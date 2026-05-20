---
name: css
description: >-
  Scaffold or maintain a project's root stylesheet (theme.css / globals.css /
  app.css) so it follows the CSS-only light / dark / system color-mode contract:
  `@layer theme`, `:root[data-theme]` overrides, and `prefers-color-scheme`
  resolution for system mode. CSS-only — no JavaScript is shipped by this skill.
  Triggers when: "add light/dark mode", "set up theme.css", "implement color
  modes", "scaffold CSS theme layer", "wire up dark mode CSS". Also use when
  migrating away from Tailwind `darkMode: 'class'`, removing JS-driven theme
  switching, or aligning an existing stylesheet with the `CSS-MODE-*` rules.
allowed-tools: Read, Edit, Write, Glob, Grep, Skill
---

# CSS Color-Mode Scaffold Skill

Sets up the canonical CSS-only light / dark / system color-mode layer on a project's root stylesheet. The skill never emits JavaScript: explicit overrides are a `data-theme` attribute the consumer toggles themselves; system mode is the absence of that attribute, resolved by `prefers-color-scheme`. Output is one edited or created CSS file plus a pointer to `references/runtime-toggle.md` for consumers who need a runtime switch.

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Produce or update a project's root stylesheet so it conforms to the four `CSS-MODE-*` rules in `plugin:web:standard:css` — canonical selectors, system mode via media queries, `@layer theme` placement with `color-scheme`, and the two-tier `--theme-*` → `--ui-*` token chain.

**When to use**:

- A project asks for light/dark mode and has no color-mode scaffold yet.
- An existing stylesheet uses `.dark` class toggling, Tailwind `darkMode: 'class'`, or JS-only switching and needs to migrate to the `:root[data-theme]` contract.
- Tokens exist but lack `color-scheme`, live outside `@layer theme`, or skip the tier-1/tier-2 split.

**Prerequisites**:

- A target project with at least one CSS entry point (`theme.css`, `globals.css`, `app.css`, `styles/index.css`, or equivalent). If none exists, the skill creates `theme.css` at the project root.
- Read access to `tailwind.config.{js,ts,mjs}` and `postcss.config.*` if they exist — needed to detect conflicting `darkMode: 'class'`.

### Your Role

You are a **CSS Theming Scaffold Author**. You make a single, careful edit to one root stylesheet and leave runtime concerns to the consumer.

- **Minimal footprint**: Touch one CSS file. Never write JS. Never modify components.
- **Preserve, don't overwrite**: Merge into existing tokens and `@layer theme` blocks; do not clobber the project's custom colors.
- **Surface conflicts**: When a competing pattern exists (Tailwind class darkMode, `.dark` selectors, JS hydration), stop and propose a migration plan before editing.
- **Rule-driven**: Re-read the produced CSS against `CSS-MODE-01..04` before declaring done.

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Project root**: Working directory containing the target codebase. Used to locate the root stylesheet via Glob.

#### Optional Inputs

- **Target stylesheet path**: Explicit path to the file to edit (e.g. `src/app/globals.css`). Skip the auto-detection step when supplied.
- **Extra UI tokens**: Additional semantic token roles the user wants paired (e.g. `--ui-muted`, `--ui-border`). Default: just `--ui-bg` and `--ui-fg`.

#### Expected Outputs

- **Edited or created CSS file**: One root stylesheet containing the canonical `@layer theme` block.
- **Compliance summary**: A short report listing each `CSS-MODE-*` rule and how the output satisfies it.
- **Consumer guidance handoff**: Path to `references/runtime-toggle.md` so the consumer can wire `data-theme` toggling if they want an explicit switch.

#### Data Flow Summary

The skill locates the root stylesheet, audits it for any existing color-mode pattern, plans a non-destructive merge against `references/theme.css.template`, writes the result, then verifies the four `CSS-MODE-*` rules by re-reading the file.

### Visual Overview

```plaintext
[START]
   |
   v
[Step 1: Locate root stylesheet]
   |   - Glob common entry points
   |   - Ask user if ambiguous
   v
[Step 2: Detect existing color-mode setup]
   |   - Grep for prefers-color-scheme, data-theme, .dark, darkMode
   v
[Step 3: Plan migration (if conflicts)]
   |   - List conflicts; propose swap; get confirmation
   v
[Step 4: Merge canonical @layer theme block]
   |   - Preserve custom tokens
   |   - Insert template from references/theme.css.template
   v
[Step 5: Hand consumer guidance]
   |   - Point at references/runtime-toggle.md
   v
[Step 6: Verify against CSS-MODE-01..04]
   |   - Re-read produced CSS
   v
[END]  -> emit compliance summary
```

## 3. SKILL IMPLEMENTATION

### Applied Standards

Read these recursively and apply throughout:

- `plugin:web:standard:css` — the four `CSS-MODE-*` rules (selector contract, system mode resolution, layer + color-scheme placement, two-tier token chain).
- `plugin:web:standard:theming` — composes with this skill when `@theme` (Tailwind v4.3) owns brand semantics; the `@layer theme` block from this skill owns the per-mode palette and active UI tokens.
- `plugin:coding:standard:naming` — `--theme-{mode}-{role}` and `--ui-{role}` token names, and `data-theme="light"|"dark"` attribute values, must follow naming conventions.

### Skill Steps

1. Locate or create the project's root stylesheet.
2. Detect existing color-mode setup.
3. Plan a migration when a conflicting pattern is found.
4. Write or merge the canonical `@layer theme` block.
5. Hand the consumer the runtime toggle recipe.
6. Verify the output against `CSS-MODE-01..04`.

### Step 1: Locate or Create the Root Stylesheet

**Step Configuration**:

- **Purpose**: Identify exactly one CSS file to edit.
- **Input**: Project root; optional explicit target path.
- **Output**: Absolute path to the target stylesheet (may be a new file).
- **Sub-skill**: _(none)_
- **Parallel Execution**: No.

**What You Do**:

1. If the user supplied an explicit target path, validate it exists and skip to Step 2.
2. Run Glob for candidates in this priority order, stopping at the first non-empty result:
   - `**/theme.css`
   - `**/globals.css`
   - `**/app.css`
   - `**/styles/index.css`
   - `src/**/*.css` (limit to entry-shaped names)
3. Exclude `node_modules`, `dist`, `build`, `.next`, `coverage` from results.
4. If multiple candidates remain, list them and ask the user which one is the root stylesheet. Do not guess.
5. If zero candidates exist, plan to create `theme.css` at the project root (or `src/theme.css` when a `src/` directory is present).

**Failure mode**: ambiguous root stylesheet — ask the user; never silently pick.

### Step 2: Detect Existing Color-Mode Setup

**Step Configuration**:

- **Purpose**: Establish what (if any) color-mode pattern is already in place so the merge is non-destructive.
- **Input**: Target stylesheet path; project root.
- **Output**: Audit findings: `{ hasMediaQuery, hasDataTheme, hasDarkClass, hasTailwindClassMode, hasLayerTheme, existingUiTokens }`.
- **Sub-skill**: _(none)_
- **Parallel Execution**: No.

**What You Do**:

1. Read the target stylesheet end-to-end.
2. Grep across the project for:
   - `prefers-color-scheme` — existing media-query branch.
   - `data-theme` — existing attribute selector (good).
   - `\.dark\b` — class-based dark mode (conflict).
   - `darkMode\s*:\s*['"]class['"]` in `tailwind.config.*` — Tailwind class mode (conflict).
   - `@layer\s+theme` — existing theme layer (merge target).
   - `--ui-` and `--theme-` prefixes — pre-existing tokens to preserve.
3. Record the findings; do not edit yet.

### Step 3: Plan Migration When Conflicts Exist

**Step Configuration**:

- **Purpose**: Get explicit user sign-off before changing a conflicting pattern.
- **Input**: Audit findings from Step 2.
- **Output**: Confirmed migration plan, or a clean greenfield plan.
- **Sub-skill**: _(none)_
- **Parallel Execution**: No.

**What You Do**:

1. If `hasDarkClass` or `hasTailwindClassMode` is true, list every occurrence and propose:
   - Replacing `.dark` selectors with `:root[data-theme="dark"]` equivalents.
   - Setting `darkMode: ['selector', '[data-theme="dark"]']` in Tailwind config (or removing the option entirely on Tailwind v4 where the new selector strategy is default).
   - Removing JS-driven `.dark` class toggling — point the consumer to `references/runtime-toggle.md` for the `data-theme` replacement.
2. Present the plan as a numbered diff summary and wait for user confirmation before proceeding to Step 4.
3. If no conflicts exist, state "no migration needed" and proceed.

**Failure mode**: Tailwind `darkMode: 'class'` already used → offer migration; do not silently rewrite.

### Step 4: Write or Merge the Canonical `@layer theme` Block

**Step Configuration**:

- **Purpose**: Produce a stylesheet that contains the canonical color-mode scaffold while preserving every custom token already present.
- **Input**: Target stylesheet path; audit findings; user-confirmed plan.
- **Output**: Edited or created CSS file.
- **Sub-skill**: _(none)_
- **Parallel Execution**: No.

**What You Do**:

1. Read `references/theme.css.template` (this skill's directory).
2. If the target file does not exist, write the template verbatim plus any user-requested extra `--ui-*` token pairs.
3. If `hasLayerTheme` is true, merge into the existing `@layer theme` block:
   - Keep all existing tokens in place.
   - Add the canonical `--theme-{light|dark}-{bg|fg}` raw palette under `:root` if missing.
   - Ensure each of the five mode branches sets `color-scheme` and aliases the active `--ui-*` tokens.
4. If `hasLayerTheme` is false but other content exists, append a new `@layer theme { … }` block at the top of the file (after any `@import` lines).
5. When the user requested extra `--ui-*` roles (e.g. `--ui-muted`), declare each in **all five** branches (`:root`, both `prefers-color-scheme` blocks, both `[data-theme]` selectors). Pair them with `--theme-light-{role}` and `--theme-dark-{role}` raw palette entries.
6. Use Edit for in-place merges; use Write only when creating a new file. Never delete existing custom tokens.

**Failure mode**: tokens declared in `:root` but missing from one of the mode branches → auto-add the missing alias rather than leaving a gap; the Step 6 verification will re-check this.

### Step 5: Hand Consumer Runtime Guidance

**Step Configuration**:

- **Purpose**: Tell the consumer how (and whether) to wire a runtime toggle.
- **Input**: Whether the project asked for an explicit toggle or system-only.
- **Output**: A short message pointing at `references/runtime-toggle.md`.
- **Sub-skill**: _(none)_
- **Parallel Execution**: No.

**What You Do**:

1. Report the absolute path to `plugins/web/skills/css/references/runtime-toggle.md`.
2. State that the skill itself emitted no JS — the CSS already resolves system mode via `prefers-color-scheme`.
3. If the consumer wants an explicit light/dark toggle, they paste the snippet from `runtime-toggle.md` into their `<head>` (or framework equivalent).

### Step 6: Verify Against `CSS-MODE-01..04`

**Step Configuration**:

- **Purpose**: Re-read the produced CSS and confirm each rule is satisfied before declaring success.
- **Input**: Edited target stylesheet.
- **Output**: Compliance summary attached to the skill report.
- **Sub-skill**: _(none)_
- **Parallel Execution**: No.

**What You Do**:

1. Read the target stylesheet fresh.
2. Walk each rule:
   - **`CSS-MODE-01` (Selector contract)** — confirm only `:root[data-theme="light"]` and `:root[data-theme="dark"]` are used for explicit overrides. Fail on `.dark`, `[data-mode]`, `[data-color-scheme]`.
   - **`CSS-MODE-02` (System mode resolution)** — confirm `:root:not([data-theme])` appears inside both `@media (prefers-color-scheme: light)` and `@media (prefers-color-scheme: dark)` blocks.
   - **`CSS-MODE-03` (Layer placement + `color-scheme`)** — confirm every branch lives inside `@layer theme` and sets `color-scheme: light` or `color-scheme: dark`.
   - **`CSS-MODE-04` (Two-tier token chain)** — confirm tier-1 `--theme-{light|dark}-{role}` tokens exist on `:root`, and every `--ui-{role}` token is aliased inside each of the five branches.
3. If any check fails, return to Step 4 and patch. Do not declare success with an open failure.

### Skill Completion

**Report the skill output as specified**:

```yaml
status: success|failure|partial
summary: 'Brief description of what was scaffolded or migrated'
edited_files:
  - <absolute path to root stylesheet>
created_files: []  # populated if the stylesheet did not exist
runtime_toggle_reference: <absolute path to references/runtime-toggle.md>
compliance:
  CSS-MODE-01: pass|fail   # selector contract
  CSS-MODE-02: pass|fail   # system mode resolution
  CSS-MODE-03: pass|fail   # @layer theme + color-scheme
  CSS-MODE-04: pass|fail   # two-tier token chain
migration_notes: []  # any conflicts addressed (e.g. removed .dark class toggling)
issues: []
```
