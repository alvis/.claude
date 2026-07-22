# Discover board — feature inventory

The definitive checklist for every board the discover skill generates. **Floor** features are
mandatory and validator-enforced; **Menu** features are proven options the generator reaches for
when the content calls for them. Consult this file before composing (workflow step 7) and again
at verification (step 8) — no generation may silently drop a Floor feature.

## A. Shell (floor)

- [ ] **Docbar**: document title (primary), product label (`<Product> · Discover`), `Generated reply ↓` quick link. No logo/docmark — the document title leads. `position: static` below the narrow-viewport breakpoint so a wrapped title never collides with content.
- [ ] **Docnav** (right rail, hidden on narrow viewports): section nav with scroll-spy active state; **live input counters** (decisions/accepted, notes); board-set list with per-board accent dots marking "you are here" when the board belongs to a set
- [ ] **Masthead**: eyebrow (glyph + `Question N of M — Topic · Product` position line), display `h1`, dek/lede with `.mono` inline refs, stat strip with color rails when the content carries counts
- [ ] **Footer**: sources with provenance, flagged live checks

## B. Theming (floor)

- [ ] Colors **only** via tokens: base `--ui-*` set + the board-theme overlay (whitelisted: board accent, `--ui-verdict-*`, `--ui-status-*`, `--ui-k-*` ramps with `-soft`/`-ink` variants)
- [ ] Every token defined for **light and dark**; `prefers-color-scheme` + `data-theme` override both directions
- [ ] Per-board accent so companion boards read as a themed set; ramps preferentially alias the shell's own palette families
- [ ] Contrast floor holds in both themes

## C. Interactive response capture (floor — the template's core value)

Per **card** (any card carrying a recommendation, verdict, or decision):
- [ ] **Choose between options when real alternatives exist** — never a bare Accept button in that case: render the option set as selectable cards, each with its reason, the recommended one badged; selection = the decision (keyboard `A` selects the recommended option)
- [ ] **Accept** for single-recommendation cards — visible button (plus keyboard `A` on card-stage boards); toggleable; state shown on the card and on its pip/index entry (✓)
- [ ] **Note per card** — visible button opening the note dialog; saved state shown on the button; editable/removable

Per **section**:
- [ ] Annotation trigger (`✎ Add note`) with the same dialog

Board level:
- [ ] Live counters in the docnav update on every accept/choice/note
- [ ] Exactly **one** generated-reply prompt host; the prompt **rebuilds live** from: accepted/overridden recommendations, option selections, per-card notes, per-section notes, and active filters
- [ ] Copy button with `aria-live` copied-status feedback

## D. Navigation & wayfinding (floor where the device is used)

- [ ] Section nav scroll-spy
- [ ] Filter chips: `aria-pressed`, show/hide or dim, counts where useful
- [ ] Pip index for card stages: state-aware (blocking = danger color, accepted/decided = ✓, filtered-out = dimmed)
- [ ] Keyboard: `←`/`→` between cards, `A` accept/choose-recommended, all controls focusable with visible focus
- [ ] `Generated reply ↓` docbar link

## E. Content devices (menu — reach for what the content calls for)

verdict/finding cards with semantic edge + pill · option card set with recommended badge ·
readiness meter (`n/5`) · provenance chips (observed / inferred / needs-live-query) · owner chips
with initials · severity tags · landing-map disposition rows · critical-path strip · risk-matrix
table · Prevent/Detect/Contain failure map · timeline rail with recheck triggers · scope-cuts
note · sign-off card · tl;dr block · glossary · entity card · flow strip · stat tiles ·
plain-English translation line · `file:line` source chips · data-driven card sets rendered from a
JSON array

## F. Engineering (floor)

- [ ] Fully self-contained: no external scripts/styles/fonts/images
- [ ] Data-driven rendering uses the `esc()` idiom; **no un-interpolated `${…}` literals** in emitted text
- [ ] A11y: `:focus-visible` states, `aria-pressed`/`aria-live`/roles, dialog semantics, `prefers-reduced-motion`
- [ ] Responsive: no horizontal body scroll; wide content scrolls in its own container; `tabular-nums` for aligned digits
- [ ] Weight discipline: target tens of KB, not hundreds

## G. Validation mapping

| Feature | Enforced by |
|---|---|
| Shell presence, single prompt host, annotatable sections | `scripts/test_html_templates.py` (floor assertions) |
| Token whitelist, dual-theme completeness, stray hex | `scripts/build_artifact.py` `_validate()` |
| `${…}` literal guard | `scripts/build_artifact.py` `_validate()` |
| Self-containment | `scripts/build_artifact.py` `_validate()` |
| Per-card capture + live prompt rebuild | golden examples (`examples/src/readiness-verdict-board/`, `examples/src/decision-browser/`) + this checklist at review |
