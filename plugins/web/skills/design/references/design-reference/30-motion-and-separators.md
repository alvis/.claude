# Motion and separators

## Motion Specifics

| Property | Value | Notes |
|---|---|---|
| Entrance duration | 200-400ms | Ease-out (decelerate into rest position) |
| Exit duration | 150-250ms | Ease-in (accelerate out of view); shorter and softer than entrance |
| Easing (entrance) | `cubic-bezier(0.16, 1, 0.3, 1)` | Exponential ease-out; no bounce or elastic |
| Easing (exit) | `ease-in` or `cubic-bezier(0.4, 0, 1, 1)` | Quick departure |
| Max motion types per page | 2-3 | More than 3 distinct motion patterns creates visual noise |
| Stagger delay | ~80-100ms per element | Titles at ~80ms per word, content chunks at ~100ms |
| Icon swap | 120ms cross-fade | `opacity` + subtle `scale(0.9)` to `scale(1)`; no rotation unless semantically meaningful |
| Height reveal | `grid-template-rows: 0fr` to `1fr` | Avoids the `height: auto` animation trap |
| Page transition | ≤300ms | View Transitions API or equivalent; crossfade / shared-element morph / directional slide — one style per site, with a reduced-motion fallback |
| Scroll reveal | translate ≤24px, stagger 80-100ms | Trigger at ~20% visibility; once-only (never re-animate on scroll-up); opacity + translate (+ optional `blur(4px)→0`) |
| Animate only | `transform`, `opacity`, `filter` | Every other property triggers layout or paint |

No bounce or elastic easing. Real objects decelerate smoothly. Do not use `transition: all` even as a prototype shortcut.

## Motion Libraries — GSAP & Three.js

Reach for a JS motion library only when the locked direction needs what CSS and the View Transitions API cannot express: scroll-*scrubbed* timelines (progress-driven, not merely triggered), pinned sequences, or real-time 3D. Entrances, hovers, toggles, and trigger-once reveals stay on CSS + IntersectionObserver — a library there is weight without payoff. A library is something the design writes *against*, not a new capability that relaxes the rules: the perf budgets, the 2–3-motion-types cap, the `transform`/`opacity`/`filter`-only rule, and `prefers-reduced-motion` all still bind. Current APIs only — no pre-2024 patterns.

### GSAP + ScrollTrigger

| Rule | Why |
|---|---|
| Scope every animation in `gsap.context(() => {…}, scopeEl)` and call `ctx.revert()` on teardown/unmount | Tweens and triggers left alive across a route change leak memory and double-bind on return — a console-error and jank source the perf gate catches |
| Branch reduced vs full motion with `gsap.matchMedia()` keyed on `(prefers-reduced-motion: reduce)`, never a bare `if` | matchMedia tears the wrong-branch animations down automatically when the query flips; a hand-rolled `if` leaves them registered |
| `ScrollTrigger.kill()`/`.revert()` on every trigger you create; `ScrollTrigger.refresh()` after async content shifts layout | Orphan triggers fire against stale positions → CLS and reveals in the wrong place |
| Scrub `transform`/`opacity` only — never `width`, `height`, `top` | Same layout/paint rule as Motion Specifics; scrubbed layout props blow the "no >50ms long task" budget frame after frame |
| The reduced-motion branch is the *calm* composition, not a dead one | Meets the reduced-motion craft bar: a static, deliberate state, not a disabled afterthought |

### Three.js / WebGL

| Rule | Why |
|---|---|
| Lazy-load and code-split the 3D bundle; keep it off the critical path | A WebGL hero that blocks first paint fails LCP ≤2.5s outright |
| Cap `renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5–2))` | Uncapped DPR on retina/mobile quadruples fragment work → dropped frames |
| Pause the `requestAnimationFrame` loop when the canvas is offscreen (IntersectionObserver) and on `visibilitychange` | A loop running behind the fold or in a hidden tab burns battery and INP for nothing |
| `dispose()` every geometry, material, texture, and the renderer on teardown | GPU resources are not garbage-collected — this is the #1 Three.js leak |
| Prefer WebGPU/TSL with a WebGL fallback; ship a **static** fallback (poster image / CSS) when WebGL is unavailable OR reduced-motion is set | The 3D is an enhancement over an accessible baseline, never the baseline itself |

Both libraries: motion and 3D layer over a working, accessible baseline — core content and navigation never depend on the library running.

## Section Separator Vocabulary

Every boundary between page sections is a design decision. Boards and final pages pick each boundary's treatment from this menu — "plain whitespace" is a legitimate pick, but it must be stated, never defaulted into. No two consecutive boundaries repeat the same treatment (the variety rule applies to joins, not just layouts).

| Treatment | When to use |
|---|---|
| Whitespace scale-shift | Quiet editorial rhythm; jump the section gap a full step (e.g., `--space-8` → `--space-12`) so the pause itself reads as the divider |
| Hairline rule | Dense, structured content; a 1px `--ui-border` line, often inset from the edges to feel typographic |
| Color band / background shift | Signal a change of register (proof, pricing); adjacent section canvases step by ≥4% lightness or switch to a tinted surface |
| Angled clip-path | Energetic, brand-forward pages; keep one consistent angle site-wide (2–6°) and never alternate directions per boundary |
| Curve / wave | Softer brands; ONE gentle curve, not a repeating wave pattern — and at most one curved boundary style per page |
| Overlap & negative margin | Hero-to-content or card-to-band joins; the next section's lead element breaks the boundary by 24–48px for depth |
| Gradient fade | Atmospheric/textured canvases; fade one canvas into the next over 80–160px instead of a hard edge |
| Full-bleed image band | Chaptering long pages; an edge-to-edge visual (with contrast-safe treatment) acts as the divider |
| Marquee / ticker divider | Playful or fashion-adjacent directions; a single-line scrolling strip (logos, keywords) — honors `prefers-reduced-motion` by pausing |
