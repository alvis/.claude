# Components, layout, and depth

## 4. Component Stylings

### Buttons

**Base**: `padding: {{0.625rem 1.25rem}}; border-radius: var(--radius-control); font-weight: 600; font-size: 0.875rem; transition: background-color 150ms ease, box-shadow 150ms ease, transform 150ms ease;`

| Variant | Background | Text | Border |
|---|---|---|---|
| Primary | `var(--ui-primary)` | `var(--ui-fg-inverse)` | none |
| Secondary | `transparent` | `var(--ui-primary)` | `1px solid var(--ui-primary)` |
| Ghost | `transparent` | `var(--ui-fg)` | none |
| Danger | `var(--ui-danger)` | `var(--ui-fg-inverse)` | none |

**Interactive States**:

| State | Treatment | Notes |
|---|---|---|
| Hover | Switch to the variant's hover token (e.g. `var(--ui-primary-hover)`), `translateY(-1px)`, add subtle shadow | Cursor pointer |
| Active | Switch to the active token (e.g. `var(--ui-primary-active)`), `translateY(0)`, remove shadow | Instant feedback |
| Disabled | `opacity: 0.5; cursor: not-allowed;` | No pointer events |
| Focus | `box-shadow: 0 0 0 3px color-mix(in srgb, var(--ui-focus-ring) 30%, transparent)` | Always visible ring |

### Cards

| Variant | Background | Border | Shadow | Hover |
|---|---|---|---|---|
| Default | `var(--ui-surface)` | `1px solid var(--ui-border)` | `var(--ui-shadow-card)` | -- |
| Elevated | `var(--ui-surface)` | none | `var(--ui-shadow-raised)` | -- |
| Interactive | `var(--ui-surface)` | `1px solid var(--ui-border)` | `var(--ui-shadow-card)` | `var(--ui-shadow-raised)`, `translateY(-2px)` |

### Inputs

**Base**: `padding: {{0.625rem 0.75rem}}; border-radius: var(--radius-control); font-size: 1rem; border: 1px solid var(--ui-border); transition: border-color 150ms ease, box-shadow 150ms ease;`

| State | Border | Shadow | Label |
|---|---|---|---|
| Default | `var(--ui-border)` | none | `var(--ui-fg-muted)` |
| Focus | `var(--ui-primary)` | `0 0 0 3px var(--ui-primary-subtle)` | `var(--ui-primary)` |
| Error | `var(--ui-danger)` | `0 0 0 3px var(--ui-danger-subtle)` | `var(--ui-danger)` |
| Disabled | `var(--ui-border)` | none | `var(--ui-fg-subtle)`, bg `var(--ui-surface-sunken)` |

### Navigation

- **Top bar**: `height: {{3.5rem}}; background: var(--ui-surface); border-bottom: 1px solid var(--ui-border); backdrop-filter: blur(12px);`
- **Active item**: `color: var(--ui-primary); font-weight: 600;` with bottom indicator (`2px solid var(--ui-primary)`)
- **Mobile**: Hamburger menu at `{{768px}}` breakpoint, slide-in drawer from left

### Images

- **Border radius**: `var(--radius-card)` for standalone images, `var(--radius-control)` for images inside cards
- **Aspect ratio**: Use `aspect-ratio: {{16/9}}` for hero, `{{1/1}}` for avatars, `{{4/3}}` for cards
- **Loading**: Skeleton placeholder with `var(--ui-surface-sunken)` background and shimmer animation
- **Object fit**: `object-fit: cover` for fills, `object-fit: contain` for logos

### Motion, Transitions & Separators

The World-Class Element Checklist spec for this project (values follow [Motion Specifics](../design-reference/30-motion-and-separators.md#motion-specifics); picks come from the connective-tissue board):

- **Page transition**: {{STYLE — e.g., "View Transitions API crossfade + 8px upward drift, 240ms cubic-bezier(0.16, 1, 0.3, 1)"}}
- **Scroll-reveal language**: {{TRIGGER, DISTANCE, STAGGER — e.g., "IntersectionObserver at 20% visibility; opacity 0→1 + translateY(16px)→0; 90ms stagger per chunk; once-only"}}
- **Signature micro-interaction**: {{FROM_DIRECTION_QUESTION_5 — e.g., "CTA magnetic hover: 4px cursor-follow + scale(1.02)"}}
- **Reduced motion**: {{BEHAVIOR — e.g., "reveals become instant opacity fades; page transition falls back to plain crossfade; parallax disabled"}}

**Section separators** (every boundary deliberate; no two consecutive boundaries repeat):

| Boundary | Treatment |
|---|---|
| {{Hero → Features}} | {{e.g., "gradient fade from hero canvas into `--ui-surface-sunken`"}} |
| {{Features → Social proof}} | {{e.g., "full-bleed color band with overlap: cards break the boundary by −32px"}} |

**Hover & focus treatments** (every interactive element class):

| Element class | Hover | `:focus-visible` |
|---|---|---|
| {{Links}} | {{e.g., "underline grows in 150ms from left"}} | {{e.g., "2px `--ui-focus-ring` outline, 2px offset"}} |
| {{Cards}} | {{e.g., "`--ui-shadow-raised` + translateY(-2px)"}} | {{same ring on the card surface}} |
| {{Images}} | {{e.g., "scale(1.03) inside overflow-hidden frame, 300ms"}} | {{ring on the wrapping link}} |

**Dynamic-region states**: {{PER REGION — loading/skeleton, empty, error designs, e.g., "testimonial wall: shimmer skeleton rows; empty → quote CTA; error → muted retry inline"}}

---

## 5. Layout Principles

**Base Unit**: `4px`

**Max Content Width**: `{{1280px}}`

### Spacing Scale

Fixed 4px-grid primitives (mode-independent, plain `:root` tokens):

| Token | Value | Usage |
|---|---|---|
| `--space-1` | `0.25rem` (4px) | Inline icon gaps |
| `--space-2` | `0.5rem` (8px) | Tight element gaps |
| `--space-3` | `0.75rem` (12px) | Form field gaps |
| `--space-4` | `1rem` (16px) | Default component padding |
| `--space-5` | `1.5rem` (24px) | Card padding, section gaps |
| `--space-6` | `2rem` (32px) | Between sections |
| `--space-7` | `2.5rem` (40px) | Large component separation |
| `--space-8` | `3rem` (48px) | Page-level vertical rhythm |
| `--space-9` | `3.5rem` (56px) | Major block separation |
| `--space-10` | `4rem` (64px) | Hero / major section breaks |
| `--space-11` | `5rem` (80px) | Oversized section breaks |
| `--space-12` | `6rem` (96px) | Maximum single spacing value |

### Border Radius Roles

Role-named tokens only (WT-VARIANT-01) — names express what the radius is FOR, never its size:

| Token | Value | Usage |
|---|---|---|
| `--radius-control` | `{{0.5rem}}` | Buttons, inputs, selects, chips |
| `--radius-card` | `{{0.75rem}}` | Cards, panels, standalone images |
| `--radius-modal` | `{{1rem}}` | Modals, sheets, large surfaces |

Fully-round elements (avatars, pills, toggles) use the `9999px` literal — a shape constant, not a theme decision, so it is never a token.

### Grid System

- **Columns**: `{{12}}`
- **Column gap**: `var(--space-5)`
- **Row gap**: `var(--space-5)`
- **Container padding**: `var(--space-4)` (mobile), `var(--space-6)` (desktop)

---

## 6. Depth & Elevation

Shadows are mode-dependent — they go through the two-tier chain like colors. Dark-mode values use light-overlay stepping (semi-transparent white rings/washes), because drop shadows are nearly invisible on dark surfaces (see [Surfaces](../design-reference/10-foundations-and-quality.md#surfaces)).

| Tier-2 Token | Role | Tier-1 Light | Tier-1 Dark |
|---|---|---|---|
| `--ui-shadow-card` | Cards, subtle lift | `{{0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)}}` | `{{0 0 0 1px rgba(255,255,255,0.05)}}` |
| `--ui-shadow-raised` | Hovered cards, dropdowns | `{{0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)}}` | `{{0 0 0 1px rgba(255,255,255,0.08)}}` |
| `--ui-shadow-overlay` | Modals, popovers, floating panels | `{{0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)}}` | `{{0 0 0 1px rgba(255,255,255,0.10), 0 10px 15px rgba(0,0,0,0.5)}}` |

Flat elements simply omit `box-shadow` — there is no "level 0" token.

---
