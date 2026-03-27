# Tool Routing -- Decision Tree

## Quick Decision

| # | Category | Primary | Why | Fallback |
|---|----------|---------|-----|----------|
| 1 | Page Opening | Chrome DevTools `navigate_page` | Foundation — must open page first | next-browser `open`/`goto` for subsequent nav |
| 2 | DOM & Styles | Chrome DevTools `evaluate_script`, `take_snapshot` | Full programmatic DOM + computed style access | next-browser `snapshot` for quick structural view |
| 3 | React Components | next-browser `tree`, `tree <id>` | **Exclusive** — purpose-built React tree inspection | -- |
| 4 | Console & Errors | next-browser `errors`, `logs` | Next.js error overlay parsing, structured output | Chrome DevTools `list_console_messages` for raw stream |
| 5 | Performance | Chrome DevTools `performance_*_trace`, `take_memory_snapshot` | **Exclusive** — no NB equivalent | -- |
| 6 | Lighthouse | Chrome DevTools `lighthouse_audit` | **Exclusive** — no NB equivalent | -- |
| 7 | Network | Chrome DevTools `list_network_requests` | Richer request/response detail | next-browser `network` for quick checks |
| 8 | Screenshots | next-browser `screenshot`, `preview` | File path save, quick preview convenience | Chrome DevTools `take_screenshot` when already in CDT workflow |
| 9 | Device Emulation | Chrome DevTools `emulate` | Named device profiles with UA, DPR, screen dims | next-browser `viewport` for simple width/height |
| 10 | User Interaction | next-browser `click`, `type` | Selector-based = more reliable than coordinates | Chrome DevTools for advanced: drag, upload, dialog |
| 11 | Storage | Chrome DevTools `evaluate_script` | **Exclusive** — no NB storage commands | -- |
| 12 | Next.js Specific | next-browser `routes`, `page`, `project`, `action`, `ssr` | **Exclusive** — no CDT equivalent | -- |
| 13 | JS Debugging | Chrome DevTools breakpoints, stepping | **Exclusive** — no NB equivalent | -- |
| 14 | Accessibility Tree | Either (`snapshot` / `take_snapshot`) | Functionally equivalent | Use whichever is active |

**Summary**: next-browser is primary for 4 categories (React, Console/Errors, Screenshots, User Interaction basics) + 1 exclusive (Next.js Specific). Chrome DevTools is primary for 6 categories (Page Opening, DOM/Styles, Network, Device Emulation, Storage, JS Debugging) + 3 exclusive (Performance, Lighthouse, JS Debugging). 1 shared (A11y Tree).

## When to Use Both

- **Layout debugging**: `take_snapshot` (CDT, DOM) + `tree` (NB, React) — correlate DOM structure with component hierarchy
- **Performance investigation**: `performance_*_trace` (CDT) + `routes` (NB) — identify slow routes then profile them
- **Error debugging**: `errors` (NB, structured) + `list_console_messages` (CDT, raw stream) — Next.js errors first, then full console
- **Visual regression**: `emulate` (CDT, device profile) + `screenshot` (NB, file save) — set device then capture

## Common Multi-Step Recipes

### Page Performance Audit
1. Chrome DevTools `navigate_page` — open the page (foundation)
2. `lighthouse_audit` (CDT) — get overall scores
3. `performance_start_trace` → navigate → `performance_stop_trace` (CDT) — detailed trace
4. `list_network_requests` (CDT) — find slow/large requests
5. `routes` (NB) — check if route is statically optimized

### Component Debugging
1. `tree` (NB) — find the component in React tree
2. `tree <id>` (NB) — inspect props and state
3. `take_snapshot` (CDT) — check rendered DOM
4. `evaluate_script` (CDT) — test state changes or call methods
5. `errors` (NB) — check for Next.js warnings/errors

### Mobile Responsiveness Check
1. `emulate("iPhone 14")` (CDT) — set mobile device profile
2. `screenshot` (NB) — capture mobile view to file
3. `lighthouse_audit` (CDT) — check mobile performance/a11y
4. `resize_page(1920, 1080)` (CDT) — switch to desktop
5. `screenshot` (NB) — capture desktop view for comparison

### SSR vs CSR Comparison
1. `ssr lock` (NB) — freeze server-rendered state
2. `snapshot` (NB) — capture SSR accessibility tree
3. `ssr unlock` (NB) — allow client hydration
4. `snapshot` (NB) — capture hydrated state
5. Compare the two snapshots for hydration mismatches

### User Interaction Testing
1. Chrome DevTools `navigate_page` — open the page
2. `click` (NB) — click elements by selector
3. `type` (NB) — fill text inputs by selector
4. `screenshot` (NB) — capture result
5. For advanced (drag, file upload, dialog): use Chrome DevTools equivalents
