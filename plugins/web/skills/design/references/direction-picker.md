# Direction Board — Interactive Direction Picking

Mechanics for the direction board referenced by SKILL.md `<direction>`. The board is bespoke design work — each tile IS a miniature of its direction — so there is no rigid `.template.html`; the skeleton below guarantees structure, self-containment, and the choice UX while leaving the visuals to each candidate.

## 1. Purpose

The user picks a direction with their eyes, not from prose. Three to five candidate tiles, each showing the direction's palette, type, layout rhythm, and signature motion applied to the user's REAL content — then one AskUserQuestion battery captures the choice.

## 2. File Location & Constraints

- Path: `<session scratchpad>/design-directions/index.html`. Fallback if no scratchpad: `$TMPDIR/design-directions-<project-slug>/index.html`.
- ONE self-contained file: inline CSS only, no JS frameworks, no build step. Google Fonts `<link>` tags are allowed (the board is a throwaway local file), but every tile declares system-stack fallbacks so it still reads without network.

## 3. Per-Tile Required Contents

Every tile must contain ALL of:

- [ ] Direction name + one-line thesis
- [ ] Palette strip — 5–7 role-labeled swatches (primary, accent, surface, fg, border…), light row AND dark row
- [ ] Type specimen — display + body faces set in REAL project words, never lorem ipsum
- [ ] Mini hero mock (~480px tall) built from real project content in this direction's layout rhythm
- [ ] CSS-only motion demo of the signature micro-interaction — `:hover`/`:active` transitions plus ONE `@keyframes` entrance, honoring `prefers-reduced-motion`
- [ ] Footer line naming the anchor exemplar (facelift mode) or reference products, plus the 2–3 concrete visual properties borrowed (from direction question 2)

Candidates must differ on at least two of: palette strategy, display typeface, layout rhythm, motion language. A board of three near-identical tiles is a failed board.

## 4. Skeleton

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Design Directions — {project}</title>
  <!-- Google Fonts <link> tags for candidate faces; every tile declares system fallbacks -->
  <style>
    /* board chrome — deliberately plain so it never competes with the tiles */
    :root { --board-bg: #fafafa; --board-fg: #18181b; --board-border: #e4e4e7; }
    * { box-sizing: border-box; margin: 0; }
    body { background: var(--board-bg); color: var(--board-fg); font: 16px/1.6 system-ui, sans-serif; }
    header {
      position: sticky; top: 0; z-index: 10;
      display: flex; justify-content: space-between; align-items: baseline; gap: 16px;
      padding: 12px 24px; border-bottom: 1px solid var(--board-border);
      background: color-mix(in srgb, var(--board-bg) 88%, transparent); backdrop-filter: blur(8px);
    }
    .direction { padding: 48px 24px; border-bottom: 4px solid var(--board-border); }
    .direction h2 { font-size: 28px; }
    .direction .thesis { opacity: 0.7; margin-bottom: 24px; }
    .palette { display: flex; gap: 8px; margin-block: 16px; }
    .swatch {
      flex: 1; height: 56px; border-radius: 6px;
      display: grid; place-items: end start; padding: 6px; font: 11px/1 ui-monospace, monospace;
    }
    .exemplar { margin-top: 24px; font-size: 13px; opacity: 0.6; }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation: none !important; transition: none !important; }
    }
  </style>
</head>
<body>
  <header>
    <strong>Design directions — {project}</strong>
    <span>Review each direction, then answer the question in the chat.</span>
  </header>

  <!-- ONE <article> per candidate. Each tile carries its OWN mini-theme via scoped custom
       properties — the same token discipline the final theme will follow. -->
  <article class="direction" id="direction-1" style="
    --d-bg: {canvas}; --d-fg: {text}; --d-primary: {primary}; --d-accent: {accent};
    --d-font-display: {display face}, Georgia, serif;
    --d-font-body: {body face}, system-ui, sans-serif;
    background: var(--d-bg); color: var(--d-fg); font-family: var(--d-font-body);">
    <h2 style="font-family: var(--d-font-display)">1 · {direction name}</h2>
    <p class="thesis">{one-line thesis}</p>

    <div class="palette"><!-- 5–7 role-labeled swatches, e.g.: -->
      <div class="swatch" style="background: var(--d-primary); color: var(--d-bg)">primary</div>
      <!-- … repeat the full row with the dark-mode values beneath -->
    </div>

    <section class="specimen"><!-- display + body faces in REAL project words --></section>

    <section class="hero-mock"><!-- ~480px mini hero from REAL content in this direction's
      layout rhythm; signature micro-interaction as CSS-only :hover/:active transition
      + ONE @keyframes entrance --></section>

    <p class="exemplar">Anchor: {exemplar / reference products} · Signature: {2–3 concrete visual properties}</p>
  </article>

  <!-- direction-2, direction-3 … identical structure, each with its own mini-theme -->
</body>
</html>
```

## 5. Presentation Procedure

Present BOTH ways — remote users cannot see the local Chrome window:

1. `list_pages` → `new_page file://<absolute path>` → `take_screenshot`. Look at the screenshot: broken layout, missing fonts, or clipped tiles get fixed BEFORE the user sees the board.
2. `SendUserFile` with `files: [<path>]`, `display: render`, and a caption naming the candidates — when the tool is available.

## 6. Choice Capture

Single source of truth for the battery wording (SKILL.md `<direction>` points here). One `AskUserQuestion` call:

- **Q1 — "Which direction?"** One option per candidate: label = tile name, description = its one-line thesis + anchor. Plus a final option **"Mix and match (tell me which pieces)"**. Safe default: the reviewer-ranked top candidate, stated as such in its description.
- **Q2 (optional) — density/mood adjustment**: e.g. "Keep the density as shown / Airier / Denser" when the direction questions left room for doubt.

Mix-and-match loop: build ONE merged tile from the named pieces, append it to the board, re-present (§5), re-ask. Loop until an explicit pick.

Immediately after the pick, record into DESIGN.md §10 (Context & Decision Log): the chosen direction (3-line summary), every REJECTED candidate with a one-line reason, and any adjustment from Q2.

## 7. Cleanup

The board is a tmp artifact — never commit it. Keep the file alive until Phase 3 user sign-off (the user may want to glance back at the road not taken); after sign-off it can be deleted with the rest of the scratchpad.
