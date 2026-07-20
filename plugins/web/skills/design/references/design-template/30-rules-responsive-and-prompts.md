# Rules, responsive behavior, and prompts

## 7. Do's and Don'ts

### Do

1. Use `var(--ui-primary)` for all CTA buttons — never hardcode hex values
2. Maintain `4px` grid alignment — all spacing values are multiples of the base unit
3. Use the type scale levels exactly as defined — do not invent in-between sizes
4. Apply `var(--ui-shadow-*)` tokens for elevation — keep depth usage consistent
5. Use feedback tokens (`--ui-success`, `--ui-danger`) for status states
6. Set `border-radius: var(--radius-control)` on interactive elements for a cohesive feel
7. Animate with explicit properties (`transition: background-color 150ms ease`) for micro-interactions — keep it subtle
8. Provide visible `:focus` styles on every interactive element (keyboard accessibility)
9. Use `var(--ui-surface-sunken)` for nested or recessed content areas
10. Test every component at all breakpoints AND in both color modes before considering it complete

### Don't

1. Do not use more than {{2}} accent colors simultaneously in a single view
2. Do not set `font-size` below the Tiny level (`{{0.625rem}}`) — it fails readability
3. Do not use `box-shadow` values outside the `--ui-shadow-*` set
4. Do not mix `px` and `rem` for the same property in a single component
5. Do not rely on color alone to convey meaning — always pair with icon or text
6. Do not use more than {{3}} font weights on a single screen
7. Do not place interactive elements closer than `{{8px}}` to each other (touch target clearance)
8. Do not exceed `--space-12` for any single spacing value
9. Do not use `opacity` below `0.5` for disabled states — it becomes invisible on some displays
10. Do not reference `--theme-light-*` / `--theme-dark-*` from component CSS — tier-1 lives only in `@layer theme`

---

## 8. Responsive Behavior

### Breakpoints

| Name | Value | Target |
|---|---|---|
| sm | `{{640px}}` | Mobile landscape |
| md | `{{768px}}` | Tablets |
| lg | `{{1024px}}` | Small desktop / landscape tablet |
| xl | `{{1280px}}` | Desktop |
| 2xl | `{{1536px}}` | Wide desktop |

### Touch Targets

- Minimum interactive size: `{{44px}}` (WCAG 2.5.5 AAA)
- Minimum spacing between targets: `{{8px}}`
- Mobile CTAs: full-width below the sm breakpoint

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
/* Tier-2 color & surface tokens — components consume ONLY these */
var(--ui-bg)              var(--ui-surface)        var(--ui-surface-sunken)  var(--ui-overlay)
var(--ui-fg)              var(--ui-fg-muted)       var(--ui-fg-subtle)       var(--ui-fg-inverse)
var(--ui-primary)         var(--ui-primary-hover)  var(--ui-primary-active)  var(--ui-primary-subtle)
var(--ui-accent)          var(--ui-accent-hover)   var(--ui-accent-subtle)
var(--ui-border)          var(--ui-border-strong)  var(--ui-focus-ring)
var(--ui-success)         var(--ui-warning)        var(--ui-danger)          var(--ui-info)
var(--ui-success-subtle)  var(--ui-warning-subtle) var(--ui-danger-subtle)   var(--ui-info-subtle)

/* Mode-dependent shadows */
var(--ui-shadow-card)     var(--ui-shadow-raised)  var(--ui-shadow-overlay)

/* Primitives (mode-independent) */
var(--space-1) … var(--space-12)   /* 4px grid: 4 8 12 16 24 32 40 48 56 64 80 96 */
var(--radius-control) var(--radius-card) var(--radius-modal)  /* fully-round = 9999px literal */
var(--font-display) var(--font-body) var(--font-mono)
```

### Example Component Prompts

**Prompt 1 — Hero Section**:
> "Build a hero section with a Display XL heading in `var(--ui-fg)` set in `var(--font-display)`, a Body LG subtitle in `var(--ui-fg-muted)`, and a primary CTA button using `var(--ui-primary)` with `var(--radius-control)`. Add `var(--space-10)` vertical padding. On mobile, stack vertically and make the CTA full-width."

**Prompt 2 — Feature Card Grid**:
> "Create a 3-column grid of interactive cards (`var(--ui-surface)`, `var(--ui-shadow-card)`, `var(--radius-card)`). Each card has an icon, an H4 title, and Body SM description. On hover, lift to `var(--ui-shadow-raised)` with `translateY(-2px)`. Collapse to single column below the md breakpoint. Gap is `var(--space-5)`."

**Prompt 3 — Settings Form**:
> "Design a settings form on `var(--ui-surface-sunken)` with `var(--space-5)` padding and `var(--radius-card)` corners. Use the Input styling from the design system (focus ring with `var(--ui-primary-subtle)`). Group fields in sections with H5 headings. Place the Save button (primary variant) at the bottom-right. Show error states with `var(--ui-danger)` border and helper text."

---
