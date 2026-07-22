# Free-form vs template output — comparison notes (2026-07-22)

Findings from diffing eight artifacts: three template-generated Prospector boards, three free-form
("v1") Prospector boards, and two free-form amino exemplars. This file doubles as a regression
checklist: any template change should preserve the strengths listed on both sides.

## Provenance

| Set | Artifacts | Notes |
|---|---|---|
| Template output ("v2") | Prospector current-state / blind-spots / readiness (artifact ids `dbf6cd98`, `878eea8c`, `efcf6ea2`) | Verified byte-identical CSS to `assets/html/discovery.css` — pure pipeline output, no bespoke layer |
| Free-form ("v1") | Same three boards, earlier generation (distinct frame builds, ~50 min apart) | 8–14× smaller (36–64 KB vs 504–534 KB), framework-free |
| Free-form exemplars | "amino-ui overhaul — regroup dashboard" (`284393a3`), "Amino Desktop Rebuild — Questions to Answer" (`2a9f8157`) | 49.6 / 59.1 KB, data-driven |
| Approved marriage demos | readiness board (`0d374551`), decision browser (`367d0714`) | Built this session on the real shell tokens; the design targets for the template changes |

## What the template already did well (keep)

- Structured scaffold: board-hub companion nav, stat-strip, evidence ledger, response plan,
  generated-reply prompt host, section nav, annotation runtime.
- Token discipline: single token source, dark parity, provenance chips, severity ramp.
- No interpolation bugs (the free-form blind-spots board leaked raw `${f.*}` literals).

## What the free-form boards did better (now folded into the template)

1. **Domain-semantic token ramps**, dual-mode: verdict (`go/stop/caution/probe/done`), status
   (`complete/active/planned/blocked`), per-category (`k-governance/k-runtime/…`).
2. **Per-board accent theming** — companion boards read as a themed set, not one neutral gray.
3. **Editorial masthead**: glyph eyebrow + "Question N of M — Topic · Product" position line +
   dek standfirst + `.mono` inline refs.
4. **Decision-first cards**: id/category/blocking/severity tags → question → Evidence →
   *options with reasons and a badged recommendation* (or a Recommend box when there is no real
   alternative) → Why it bites → plain-English translation → owner + `file:line` source chips.
5. **Focused interaction**: filter chips (`aria-pressed`), pip jump-index (blocking = danger,
   accepted/decided = ✓, filtered = dimmed), ←/→ keyboard nav, one-card-at-a-time stage,
   collapsible priority bands, explicit theme toggle.
6. **Data-driven rendering** from a JS array through an `esc()` helper — consistency + weight.
7. **Weight discipline**: the same message in tens of KB, not hundreds.

## Defects observed in free-form output (validator now guards)

- Un-interpolated `${…}` template literals rendered as visible text.
- No annotation/notes capture, no generated-reply integration, no live counters (the template's
  core interactive contract) — restored as the per-card capture floor in `references/features.md`.

## Mobile findings (from user review of the demos)

- A fixed docbar collides with content when the title wraps on narrow viewports → docbar is
  `position: static` below the narrow breakpoint.
- The docmark logo earns no space in the docbar → removed; the document title leads.
- A bare Accept button is wrong when real alternatives exist → option set with reasons and a
  badged recommendation; the selection is the decision.

## Where the full captures live

The raw captured HTML (several hundred KB per board) is intentionally **not** committed. The
approved demos are committed as golden examples (`examples/src/readiness-verdict-board/`,
`examples/src/decision-browser/`); the artifact ids above locate every capture on claude.ai.
