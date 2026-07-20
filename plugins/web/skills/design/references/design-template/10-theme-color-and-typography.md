# {{PROJECT_NAME}} — {{DESIGN_TITLE}}

> {{ONE_SENTENCE_DESIGN_PHILOSOPHY}}

> **Status**: {{draft|approved|implemented|promoted|superseded}} · **Headline**: {{ONE_LINE_HEADLINE}} · **Owner**: {{OWNER}}

> **Work**: `{{WORK_ID}}` · **State**: `../state.md` · **Evidence**: `../evidence/design/{{DESIGN_SLUG}}/` · **Created**: {{ISO_8601}}

> **Provenance**: {{SOURCE_URLS_PATHS_REVISIONS_AND_PRIOR_DESIGN_REFS}}

> **Handoff contract**: Sections 10–13 are mandatory and current at every save point. Whole-work context and planning remain in `state.md`; this file owns design detail and visual decisions.

---

## 1. Visual Theme & Atmosphere

**Mood**: {{MOOD_DESCRIPTION — e.g., "Clean and confident with subtle warmth. Professional but approachable."}}

**Canvas**: The base canvas is `{{CANVAS_COLOR}}` in light mode and `{{CANVAS_COLOR_DARK}}` in dark mode. Content floats on elevated surfaces to create depth without visual noise.

**Accent Philosophy**: {{ACCENT_PHILOSOPHY — e.g., "A single vibrant primary color is used sparingly for CTAs and active states. Accents support without competing. The palette stays calm — accents earn attention by being rare."}}

**Visual Language**: {{VISUAL_LANGUAGE — e.g., "Rounded corners, generous whitespace, and subtle shadows. Motion is restrained and purposeful — elements ease in, never bounce."}}

---

## 2. Color Palette & Roles

Two-tier mode tokens (CSS-MODE-04): components consume **tier-2 `--ui-<role>` only**. Each tier-2 token is fed by a `--theme-light-<role>` / `--theme-dark-<role>` tier-1 pair living inside `@layer theme`, scaffolded by the `web:css` skill — never referenced from component CSS. The Light/Dark columns below are the tier-1 values.

> Legacy token migration: `--color-primary`→`--ui-primary` · `--color-secondary`→`--ui-accent` · `--surface-canvas`→`--ui-bg` · `--surface-primary`→`--ui-surface` · `--surface-secondary`→`--ui-surface-sunken` · `--surface-overlay`→`--ui-overlay` · `--text-primary`→`--ui-fg` · `--text-secondary`→`--ui-fg-muted` · `--text-tertiary`→`--ui-fg-subtle` · `--text-inverse`→`--ui-fg-inverse` · `--border-default`→`--ui-border` · `--border-strong`→`--ui-border-strong` · `--border-focus`→`--ui-focus-ring` · `--color-error*`→`--ui-danger*` · `--shadow-1..4`→`--ui-shadow-card|raised|overlay` · `--radius-sm/md/lg/xl`→`--radius-control|card|modal` · `--space-2xs..3xl`→`--space-1..12`.

### Primary & Accent

| Tier-2 Token (components use this) | Role | Tier-1 Light (`--theme-light-<role>`) | Tier-1 Dark (`--theme-dark-<role>`) |
|---|---|---|---|
| `--ui-primary` | Primary brand / CTAs | `{{#6366f1}}` | `{{#818cf8}}` |
| `--ui-primary-hover` | Primary hover state | `{{#4f46e5}}` | `{{#a5b4fc}}` |
| `--ui-primary-active` | Primary pressed state | `{{#4338ca}}` | `{{#c7d2fe}}` |
| `--ui-primary-subtle` | Primary tinted backgrounds | `{{#eef2ff}}` | `{{#1e1b4b}}` |
| `--ui-accent` | Secondary actions / accents | `{{#06b6d4}}` | `{{#22d3ee}}` |
| `--ui-accent-hover` | Accent hover state | `{{#0891b2}}` | `{{#67e8f9}}` |
| `--ui-accent-subtle` | Accent tinted backgrounds | `{{#ecfeff}}` | `{{#164e63}}` |

### Surfaces

| Tier-2 Token (components use this) | Role | Tier-1 Light (`--theme-light-<role>`) | Tier-1 Dark (`--theme-dark-<role>`) |
|---|---|---|---|
| `--ui-bg` | Page background | `{{#ffffff}}` | `{{#0a0a0a}}` |
| `--ui-surface` | Card / panel background | `{{#ffffff}}` | `{{#141414}}` |
| `--ui-surface-sunken` | Nested / recessed areas | `{{#f9fafb}}` | `{{#1a1a1a}}` |
| `--ui-overlay` | Modal / dropdown backdrop | `{{rgba(0,0,0,0.5)}}` | `{{rgba(0,0,0,0.7)}}` |

### Text & Borders

| Tier-2 Token (components use this) | Role | Tier-1 Light (`--theme-light-<role>`) | Tier-1 Dark (`--theme-dark-<role>`) |
|---|---|---|---|
| `--ui-fg` | Headings, body text | `{{#111827}}` | `{{#f9fafb}}` |
| `--ui-fg-muted` | Supporting text | `{{#6b7280}}` | `{{#9ca3af}}` |
| `--ui-fg-subtle` | Placeholder, disabled | `{{#9ca3af}}` | `{{#6b7280}}` |
| `--ui-fg-inverse` | Text on primary color | `{{#ffffff}}` | `{{#ffffff}}` |
| `--ui-border` | Default borders | `{{#e5e7eb}}` | `{{#2a2a2a}}` |
| `--ui-border-strong` | Emphasized borders | `{{#d1d5db}}` | `{{#404040}}` |
| `--ui-focus-ring` | Focus ring color | `{{#6366f1}}` | `{{#818cf8}}` |

### Feedback

| Tier-2 Token (components use this) | Role | Tier-1 Light (`--theme-light-<role>`) | Tier-1 Dark (`--theme-dark-<role>`) |
|---|---|---|---|
| `--ui-success` | Positive / confirmed | `{{#16a34a}}` | `{{#4ade80}}` |
| `--ui-success-subtle` | Success background | `{{#f0fdf4}}` | `{{#052e16}}` |
| `--ui-warning` | Caution / attention | `{{#d97706}}` | `{{#fbbf24}}` |
| `--ui-warning-subtle` | Warning background | `{{#fffbeb}}` | `{{#422006}}` |
| `--ui-danger` | Destructive / invalid | `{{#dc2626}}` | `{{#f87171}}` |
| `--ui-danger-subtle` | Danger background | `{{#fef2f2}}` | `{{#450a0a}}` |
| `--ui-info` | Informational | `{{#2563eb}}` | `{{#60a5fa}}` |
| `--ui-info-subtle` | Info background | `{{#eff6ff}}` | `{{#172554}}` |

---

## 3. Typography Rules

| Token | Value | Usage |
|---|---|---|
| `--font-display` | `{{FONT_DISPLAY — e.g., "'Space Grotesk', -apple-system, sans-serif"}}` | Headings, hero display |
| `--font-body` | `{{FONT_BODY — e.g., "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"}}` | Body copy, UI text |
| `--font-mono` | `{{MONO_FONT — e.g., "'JetBrains Mono', ui-monospace, monospace"}}` | Code, tabular data |

**Scale Ratio**: {{SCALE_RATIO — e.g., 1.25 (Major Third)}}

The type scale is documented as a table — no per-level size tokens (`--text-body-lg` would violate WT-VARIANT-01). Mint a role type token (e.g. `--text-display`, `--text-eyebrow`) only where element defaults or utilities cannot express the role.

| Level | Size | Weight | Line Height | Letter Spacing | Usage |
|---|---|---|---|---|---|
| Display XL | `{{3.5rem}}` | `{{800}}` | `{{1.1}}` | `{{-0.03em}}` | Hero headlines |
| Display | `{{3rem}}` | `{{800}}` | `{{1.1}}` | `{{-0.025em}}` | Page hero |
| H1 | `{{2.25rem}}` | `{{700}}` | `{{1.2}}` | `{{-0.02em}}` | Page titles |
| H2 | `{{1.875rem}}` | `{{700}}` | `{{1.25}}` | `{{-0.015em}}` | Section headings |
| H3 | `{{1.5rem}}` | `{{600}}` | `{{1.3}}` | `{{-0.01em}}` | Subsection headings |
| H4 | `{{1.25rem}}` | `{{600}}` | `{{1.35}}` | `{{-0.005em}}` | Card titles |
| H5 | `{{1.125rem}}` | `{{600}}` | `{{1.4}}` | `{{0}}` | Sub-headers |
| H6 | `{{1rem}}` | `{{600}}` | `{{1.4}}` | `{{0}}` | Labels, captions |
| Body LG | `{{1.125rem}}` | `{{400}}` | `{{1.6}}` | `{{0}}` | Lead paragraphs |
| Body | `{{1rem}}` | `{{400}}` | `{{1.6}}` | `{{0}}` | Default body text |
| Body SM | `{{0.875rem}}` | `{{400}}` | `{{1.5}}` | `{{0.005em}}` | Secondary text |
| Caption | `{{0.75rem}}` | `{{500}}` | `{{1.4}}` | `{{0.01em}}` | Captions, meta |
| Tiny | `{{0.625rem}}` | `{{500}}` | `{{1.4}}` | `{{0.02em}}` | Badges, fine print |

---
