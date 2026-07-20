# Typography, color, and themes

## Reflex Fonts to Reject

These are the fonts that appear in every AI-generated mockup because they dominate training data, signalling "no decision was made." The ban is on reflex use as a display face; informed product-UI use (e.g., Inter for a dense data table) is allowed when justified. More opinionated typefaces (Space Grotesk, DM Sans, IBM Plex, Playfair Display, etc.) are legitimate design choices and are not banned.

Reject for display use: Inter, Roboto, system-ui, Open Sans, Lato, Montserrat, Poppins, Nunito, Raleway.

## Font Selection Procedure

1. Write three words that describe the brand (e.g., "precise, minimal, fast")
2. Name the three fonts you would reach for reflexively
3. Reject all three
4. Pick a typeface from a named foundry (Klim, Commercial Type, Colophon, Grilli Type, OH no Type, Village, etc.) or an open-source option with a clear personality that matches the brand words. Be able to explain why that specific typeface in one sentence

## Color System: OKLCH Rules

- Use OKLCH instead of HSL. OKLCH is perceptually uniform: equal numeric changes produce equal perceived changes across the spectrum
- Reduce chroma as lightness approaches the extremes. At 85% lightness a chroma around 0.08 is enough; pushing to 0.15 looks garish. At 15% lightness, tighten chroma similarly
- Tint neutrals toward the brand hue with a chroma of 0.005 to 0.01. Even this faint amount is perceptible and creates subconscious cohesion
- 60-30-10 is about visual weight, not pixel count. 60% neutral/surface, 30% secondary text and borders, 10% accent
- Never use gray text on a colored background. Use a shade of the background hue at reduced lightness instead

## Theme Matrix

Choose light or dark deliberately based on audience and context. Neither is a default.

| Context | Direction | Reason |
|---|---|---|
| Trading or analytics dashboard, night-shift use | Dark | High data density; reduced glare during long sessions |
| Children's reading or learning app | Light | Welcoming, low fatigue for eyes still developing contrast sensitivity |
| Enterprise SRE or observability tool | Dark | Operator context; dark surfaces read at a glance in low-light rooms |
| Weekend planning, recipes, journaling | Light | Ambient daytime use; light feels casual and approachable |
| Music player or media browser | Dark | Content-forward; dark surfaces recede and let media pop |
| Hospital or clinical patient portal | Light | Trust and legibility are paramount; clinical associations favor light |
| Vintage or artisanal brand site | Cream/warm light | Dark would clash with analog material references |

If the answer is not obvious from context, default to light. If both modes are needed, ship light first and layer dark-mode tokens on top.

## Absolute Bans

These patterns appear in the majority of AI-generated interfaces. Each has a specific rewrite.

| Pattern | Why | Rewrite |
|---|---|---|
| `border-left` or `border-right` wider than 1px as a section accent | The single most overused "design touch" in admin UIs; looks like a mistake beyond a hairline divider | Use a colored dot, short horizontal rule, background swatch, or typographic weight shift instead |
| `background-clip: text` gradient text | Decorative rather than meaningful; illegible when printed or in high-contrast mode | Use a solid brand color, tinted neutral, or typographic weight for emphasis |
| `backdrop-filter: blur` glassmorphism as the default card surface | Expensive on low-power devices; overused; layered-depth illusion breaks with a solid border | Use elevated surfaces via background color steps and `box-shadow` |
| Purple-to-blue gradients or cyan-on-dark accent systems | The canonical "AI design" color palette; communicates nothing about the brand | Pick a palette from brand words via the OKLCH rules above |
| `border-radius: 9999px` on containers and section cards | Pill radius on large containers looks bloated and unanchored; intended for small elements (pills, toggles, avatars) | Use the project's radius roles; containers get `--radius-card` or `--radius-modal` at most |
| Generic rounded-rect card with `box-shadow` as the default container | Template thinking; applies the same container to every content type | Default to cardless sections; only add card treatment when content type requires it |
| Modals as a lazy escape for overflow UI | Interrupts flow and breaks browser back navigation | Inline expand, detail panel, or dedicated route; modals only when the action truly requires focus-lock |
| `transition: all` or animating width/height/padding/margin | Forces layout recalculation on every frame | List exact properties; use `grid-template-rows: 0fr` to `1fr` for height reveals |
