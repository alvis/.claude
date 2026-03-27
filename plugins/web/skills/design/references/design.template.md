# {{PROJECT_NAME}} Design System

> {{ONE_SENTENCE_DESIGN_PHILOSOPHY}}

---

## 1. Visual Theme & Atmosphere

**Mood**: {{MOOD_DESCRIPTION — e.g., "Clean and confident with subtle warmth. Professional but approachable."}}

**Canvas**: The base canvas is `{{CANVAS_COLOR}}` in light mode and `{{CANVAS_COLOR_DARK}}` in dark mode. Content floats on elevated surfaces to create depth without visual noise.

**Accent Philosophy**: {{ACCENT_PHILOSOPHY — e.g., "A single vibrant primary color is used sparingly for CTAs and active states. Secondary colors support without competing. The palette stays calm — accents earn attention by being rare."}}

**Visual Language**: {{VISUAL_LANGUAGE — e.g., "Rounded corners, generous whitespace, and subtle shadows. Motion is restrained and purposeful — elements ease in, never bounce."}}

---

## 2. Color Palette & Roles

### Primary & Secondary

| Token Name | Role | Light Value | Dark Value |
|---|---|---|---|
| `--color-primary` | Primary brand / CTAs | `{{#6366f1}}` | `{{#818cf8}}` |
| `--color-primary-hover` | Primary hover state | `{{#4f46e5}}` | `{{#a5b4fc}}` |
| `--color-primary-active` | Primary pressed state | `{{#4338ca}}` | `{{#c7d2fe}}` |
| `--color-primary-subtle` | Primary tinted backgrounds | `{{#eef2ff}}` | `{{#1e1b4b}}` |
| `--color-secondary` | Secondary actions / accents | `{{#06b6d4}}` | `{{#22d3ee}}` |
| `--color-secondary-hover` | Secondary hover state | `{{#0891b2}}` | `{{#67e8f9}}` |
| `--color-secondary-subtle` | Secondary tinted backgrounds | `{{#ecfeff}}` | `{{#164e63}}` |

### Surfaces

| Token Name | Role | Light Value | Dark Value |
|---|---|---|---|
| `--surface-canvas` | Page background | `{{#ffffff}}` | `{{#0a0a0a}}` |
| `--surface-primary` | Card / panel background | `{{#ffffff}}` | `{{#141414}}` |
| `--surface-secondary` | Nested / recessed areas | `{{#f9fafb}}` | `{{#1a1a1a}}` |
| `--surface-tertiary` | Deeply nested / sidebar | `{{#f3f4f6}}` | `{{#262626}}` |
| `--surface-overlay` | Modal / dropdown backdrop | `{{rgba(0,0,0,0.5)}}` | `{{rgba(0,0,0,0.7)}}` |

### Neutrals

| Token Name | Role | Light Value | Dark Value |
|---|---|---|---|
| `--text-primary` | Headings, body text | `{{#111827}}` | `{{#f9fafb}}` |
| `--text-secondary` | Supporting text | `{{#6b7280}}` | `{{#9ca3af}}` |
| `--text-tertiary` | Placeholder, disabled | `{{#9ca3af}}` | `{{#6b7280}}` |
| `--text-inverse` | Text on primary color | `{{#ffffff}}` | `{{#ffffff}}` |
| `--border-default` | Default borders | `{{#e5e7eb}}` | `{{#2a2a2a}}` |
| `--border-strong` | Emphasized borders | `{{#d1d5db}}` | `{{#404040}}` |
| `--border-focus` | Focus ring color | `{{#6366f1}}` | `{{#818cf8}}` |

### Semantic

| Token Name | Role | Light Value | Dark Value |
|---|---|---|---|
| `--color-success` | Positive / confirmed | `{{#16a34a}}` | `{{#4ade80}}` |
| `--color-success-subtle` | Success background | `{{#f0fdf4}}` | `{{#052e16}}` |
| `--color-warning` | Caution / attention | `{{#d97706}}` | `{{#fbbf24}}` |
| `--color-warning-subtle` | Warning background | `{{#fffbeb}}` | `{{#422006}}` |
| `--color-error` | Destructive / invalid | `{{#dc2626}}` | `{{#f87171}}` |
| `--color-error-subtle` | Error background | `{{#fef2f2}}` | `{{#450a0a}}` |
| `--color-info` | Informational | `{{#2563eb}}` | `{{#60a5fa}}` |
| `--color-info-subtle` | Info background | `{{#eff6ff}}` | `{{#172554}}` |

---

## 3. Typography Rules

**Font Family**: `{{FONT_FAMILY — e.g., "'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif"}}`

**Mono Font**: `{{MONO_FONT — e.g., "'JetBrains Mono', 'Fira Code', monospace"}}`

**Scale Ratio**: {{SCALE_RATIO — e.g., 1.25 (Major Third)}}

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

## 4. Component Stylings

### Buttons

**Base**: `padding: {{0.625rem 1.25rem}}; border-radius: var(--radius-md); font-weight: 600; font-size: 0.875rem; transition: all 150ms ease;`

| Variant | Background | Text | Border |
|---|---|---|---|
| Primary | `var(--color-primary)` | `var(--text-inverse)` | none |
| Secondary | `transparent` | `var(--color-primary)` | `1px solid var(--color-primary)` |
| Ghost | `transparent` | `var(--text-primary)` | none |
| Danger | `var(--color-error)` | `var(--text-inverse)` | none |

**Interactive States**:

| State | Transform | Notes |
|---|---|---|
| Hover | Lighten bg 8%, `translateY(-1px)`, add subtle shadow | Cursor pointer |
| Active | Darken bg 4%, `translateY(0)`, remove shadow | Instant feedback |
| Disabled | `opacity: 0.5; cursor: not-allowed;` | No pointer events |
| Focus | `box-shadow: 0 0 0 3px var(--border-focus) / 0.3` | Always visible ring |

### Cards

| Variant | Background | Border | Shadow | Hover |
|---|---|---|---|---|
| Default | `var(--surface-primary)` | `1px solid var(--border-default)` | `var(--shadow-1)` | -- |
| Elevated | `var(--surface-primary)` | none | `var(--shadow-2)` | -- |
| Interactive | `var(--surface-primary)` | `1px solid var(--border-default)` | `var(--shadow-1)` | `var(--shadow-2)`, `translateY(-2px)` |

### Inputs

**Base**: `padding: {{0.625rem 0.75rem}}; border-radius: var(--radius-md); font-size: 1rem; border: 1px solid var(--border-default); transition: border-color 150ms ease, box-shadow 150ms ease;`

| State | Border | Shadow | Label |
|---|---|---|---|
| Default | `var(--border-default)` | none | `var(--text-secondary)` |
| Focus | `var(--color-primary)` | `0 0 0 3px var(--color-primary-subtle)` | `var(--color-primary)` |
| Error | `var(--color-error)` | `0 0 0 3px var(--color-error-subtle)` | `var(--color-error)` |
| Disabled | `var(--border-default)` | none | `var(--text-tertiary)`, bg `var(--surface-secondary)` |

### Navigation

- **Top bar**: `height: {{3.5rem}}; background: var(--surface-primary); border-bottom: 1px solid var(--border-default); backdrop-filter: blur(12px);`
- **Active item**: `color: var(--color-primary); font-weight: 600;` with bottom indicator (`2px solid var(--color-primary)`)
- **Mobile**: Hamburger menu at `{{768px}}` breakpoint, slide-in drawer from left

### Images

- **Border radius**: `var(--radius-lg)` for standalone images, `var(--radius-md)` for cards
- **Aspect ratio**: Use `aspect-ratio: {{16/9}}` for hero, `{{1/1}}` for avatars, `{{4/3}}` for cards
- **Loading**: Skeleton placeholder with `var(--surface-secondary)` background and shimmer animation
- **Object fit**: `object-fit: cover` for fills, `object-fit: contain` for logos

---

## 5. Layout Principles

**Base Unit**: `{{4px}}`

**Max Content Width**: `{{1280px}}`

### Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `--space-2xs` | `{{0.25rem}}` (4px) | Inline icon gaps |
| `--space-xs` | `{{0.5rem}}` (8px) | Tight element gaps |
| `--space-sm` | `{{0.75rem}}` (12px) | Form field gaps |
| `--space-md` | `{{1rem}}` (16px) | Default component padding |
| `--space-lg` | `{{1.5rem}}` (24px) | Card padding, section gaps |
| `--space-xl` | `{{2rem}}` (32px) | Between sections |
| `--space-2xl` | `{{3rem}}` (48px) | Page-level vertical rhythm |
| `--space-3xl` | `{{4rem}}` (64px) | Hero / major section breaks |

### Border Radius Scale

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `{{0.25rem}}` | Badges, small chips |
| `--radius-md` | `{{0.5rem}}` | Buttons, inputs, small cards |
| `--radius-lg` | `{{0.75rem}}` | Cards, panels, modals |
| `--radius-xl` | `{{1rem}}` | Hero cards, feature blocks |
| `--radius-full` | `9999px` | Avatars, pills, toggles |

### Grid System

- **Columns**: `{{12}}`
- **Column gap**: `var(--space-lg)`
- **Row gap**: `var(--space-lg)`
- **Container padding**: `var(--space-md)` (mobile), `var(--space-xl)` (desktop)

---

## 6. Depth & Elevation

| Level | Token | CSS Value | Usage |
|---|---|---|---|
| 0 | `--shadow-0` | `none` | Flat elements, inline content |
| 1 | `--shadow-1` | `{{0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)}}` | Cards, subtle lift |
| 2 | `--shadow-2` | `{{0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)}}` | Hovered cards, dropdowns |
| 3 | `--shadow-3` | `{{0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)}}` | Modals, popovers |
| 4 | `--shadow-4` | `{{0 20px 25px rgba(0,0,0,0.1), 0 8px 10px rgba(0,0,0,0.04)}}` | Toast notifications, floating panels |

---

## 7. Do's and Don'ts

### Do

1. Use `var(--color-primary)` for all CTA buttons — never hardcode hex values
2. Maintain `{{4px}}` grid alignment — all spacing values are multiples of the base unit
3. Use the type scale levels exactly as defined — do not invent in-between sizes
4. Apply `var(--shadow-*)` tokens for elevation — keep depth usage consistent
5. Use semantic color tokens (`--color-success`, `--color-error`) for feedback states
6. Set `border-radius: var(--radius-md)` on interactive elements for a cohesive feel
7. Animate with `transition: all 150ms ease` for micro-interactions — keep it subtle
8. Provide visible `:focus` styles on every interactive element (keyboard accessibility)
9. Use `var(--surface-secondary)` for nested or recessed content areas
10. Test every component at all breakpoints before considering it complete

### Don't

1. Do not use more than {{2}} accent colors simultaneously in a single view
2. Do not set `font-size` below `var(--text-tiny)` ({{0.625rem}}) — it fails readability
3. Do not use `box-shadow` values outside the shadow token scale
4. Do not mix `px` and `rem` for the same property in a single component
5. Do not rely on color alone to convey meaning — always pair with icon or text
6. Do not use more than {{3}} font weights on a single screen
7. Do not place interactive elements closer than `{{8px}}` to each other (touch target clearance)
8. Do not exceed the `--space-3xl` token for any single spacing value
9. Do not use `opacity` below `0.5` for disabled states — it becomes invisible on some displays
10. Do not nest elevated cards inside elevated cards — flatten the hierarchy

---

## 8. Responsive Behavior

### Breakpoints

| Token | Value | Target |
|---|---|---|
| `--bp-sm` | `{{640px}}` | Mobile landscape |
| `--bp-md` | `{{768px}}` | Tablets |
| `--bp-lg` | `{{1024px}}` | Small desktop / landscape tablet |
| `--bp-xl` | `{{1280px}}` | Desktop |
| `--bp-2xl` | `{{1536px}}` | Wide desktop |

### Touch Targets

- Minimum interactive size: `{{44px}}` (WCAG 2.5.5 AAA)
- Minimum spacing between targets: `{{8px}}`
- Mobile CTAs: full-width at `< --bp-sm`

### Collapsing Strategy

| Component | Desktop | Tablet | Mobile |
|---|---|---|---|
| Navigation | Horizontal top bar | Horizontal top bar | Hamburger + drawer |
| Grid | {{12}} columns | {{8}} columns | {{4}} columns (or single stack) |
| Sidebar | Visible | Collapsible panel | Hidden, triggered by icon |
| Cards | {{3}}-column grid | {{2}}-column grid | Single stack |
| Tables | Full table | Horizontally scrollable | Card-per-row layout |
| Modals | Centered dialog | Centered dialog | Full-screen sheet |

---

## 9. Agent Prompt Guide

### CSS Variable Quick-Reference

```css
/* Colors */
var(--color-primary)          var(--color-secondary)
var(--color-primary-hover)    var(--color-secondary-hover)
var(--color-primary-subtle)   var(--color-secondary-subtle)
var(--color-success)          var(--color-warning)
var(--color-error)            var(--color-info)

/* Surfaces */
var(--surface-canvas)         var(--surface-primary)
var(--surface-secondary)      var(--surface-tertiary)

/* Text */
var(--text-primary)           var(--text-secondary)
var(--text-tertiary)          var(--text-inverse)

/* Borders */
var(--border-default)         var(--border-strong)
var(--border-focus)

/* Spacing */
var(--space-2xs) var(--space-xs) var(--space-sm) var(--space-md)
var(--space-lg)  var(--space-xl) var(--space-2xl) var(--space-3xl)

/* Radius */
var(--radius-sm) var(--radius-md) var(--radius-lg) var(--radius-xl) var(--radius-full)

/* Shadows */
var(--shadow-0) var(--shadow-1) var(--shadow-2) var(--shadow-3) var(--shadow-4)
```

### Example Component Prompts

**Prompt 1 — Hero Section**:
> "Build a hero section with a Display XL heading in `var(--text-primary)`, a Body LG subtitle in `var(--text-secondary)`, and a primary CTA button using `var(--color-primary)` with `var(--radius-md)`. Add `var(--space-3xl)` vertical padding. On mobile, stack vertically and make the CTA full-width."

**Prompt 2 — Feature Card Grid**:
> "Create a 3-column grid of interactive cards (`var(--surface-primary)`, `var(--shadow-1)`, `var(--radius-lg)`). Each card has an icon, an H4 title, and Body SM description. On hover, lift to `var(--shadow-2)` with `translateY(-2px)`. Collapse to single column below `var(--bp-md)`. Gap is `var(--space-lg)`."

**Prompt 3 — Settings Form**:
> "Design a settings form on `var(--surface-secondary)` with `var(--space-lg)` padding and `var(--radius-lg)` corners. Use the Input styling from the design system (focus ring with `var(--color-primary-subtle)`). Group fields in sections with H5 headings. Place the Save button (primary variant) at the bottom-right. Show error states with `var(--color-error)` border and helper text."
