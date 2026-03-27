---
name: develop-nextjs
description: >-
  Debug Next.js apps using **next-browser CLI** (React components, Next.js routes, SSR,
  errors, screenshots, interactions) and **Chrome DevTools MCP** (DOM/styles, performance,
  Lighthouse, network, device emulation, JS debugging, storage). next-browser connects via
  CDP to a Chrome DevTools-launched browser.
argument-hint: "[debug instruction or URL]"
---

# Next.js Development & Debugging Skill

Debugs and inspects Next.js applications by combining **Chrome DevTools MCP** and **next-browser CLI**. Architecture: Chrome DevTools opens the browser page (foundation layer) → next-browser connects via CDP port on top of it → each tool handles what it's best at. Chrome DevTools provides browser-level instrumentation (DOM/styles, performance, Lighthouse, network, device emulation, JS debugging, storage); next-browser provides Next.js-aware introspection (React components, Next.js routes, SSR, errors, screenshots, user interactions).

## When to use

- Inspect DOM elements, computed styles, or accessibility tree
- Debug React component tree, props, or state
- Analyze console messages, errors, or warnings
- Profile performance (CPU, memory, traces)
- Run Lighthouse audits (performance, accessibility, SEO, best practices)
- Monitor network requests and responses
- Emulate mobile devices or custom viewports
- Capture screenshots or visual comparisons
- Inspect cookies, localStorage, sessionStorage
- Debug Next.js routes, server actions, or SSR behavior

## Environment Setup

1. **Start dev server** (if not running): `npm run dev` (or detect a running server on the expected port)
2. **Open browser via Chrome DevTools**: `navigate_page` to the target URL — this launches the controllable browser instance (foundation layer)
3. **Connect next-browser**: `next-browser open <url>` — connects via CDP port to the Chrome DevTools-launched browser
4. **Verify**: Both tools now share the same browser session

Chrome DevTools MCP is configured via the plugin's `mcp.json` and available automatically. The `next-browser` CLI must be installed globally or via `npx`.

## Task Classification & Routing

### Page Opening

- **Primary**: Chrome DevTools — `navigate_page`
- **Fallback**: next-browser — `open`, `goto` for subsequent navigation
- Chrome DevTools must open the page first (foundation layer); next-browser connects on top

### DOM & Styles

- **Primary**: Chrome DevTools — `evaluate_script`, `take_snapshot`
- **Fallback**: next-browser — `snapshot` for quick structural view
- Full programmatic DOM access + computed style inspection via Chrome DevTools

### React Components

- **Primary**: next-browser — `tree`, `tree <id>` (**exclusive**)
- Inspect component hierarchy, props, and state via next-browser's React-aware tree
- No Chrome DevTools equivalent for React-level introspection

### Console & Errors

- **Primary**: next-browser — `errors`, `logs`
- **Fallback**: Chrome DevTools — `list_console_messages` for raw console stream
- next-browser parses Next.js error overlay and provides structured output

### Performance

- **Primary**: Chrome DevTools — `performance_start_trace`, `performance_stop_trace`, `take_memory_snapshot` (**exclusive**)
- No next-browser equivalent

### Lighthouse

- **Primary**: Chrome DevTools — `lighthouse_audit` (**exclusive**)
- No next-browser equivalent

### Network

- **Primary**: Chrome DevTools — `list_network_requests`
- **Fallback**: next-browser — `network` for quick checks
- Chrome DevTools provides richer request/response detail

### Screenshots

- **Primary**: next-browser — `screenshot`, `preview`
- **Fallback**: Chrome DevTools — `take_screenshot` when already in a CDT workflow
- next-browser saves to file path and provides quick preview convenience

### Device Emulation

- **Primary**: Chrome DevTools — `emulate`, `resize_page`
- **Fallback**: next-browser — `viewport` for simple width/height
- Chrome DevTools provides named device profiles with UA, DPR, and screen dimensions

### User Interaction

- **Primary**: next-browser — `click`, `type` (selector-based, more reliable)
- **Fallback**: Chrome DevTools — `click`, `fill`, `drag`, `upload_file`, `handle_dialog` for advanced interactions
- Use Chrome DevTools for complex interactions: drag, file upload, dialog handling, checkboxes, dropdowns

### Storage

- **Primary**: Chrome DevTools — `evaluate_script` (JS access to localStorage, sessionStorage, cookies) (**exclusive**)
- No next-browser equivalent

### Next.js Specific

- **Routes**: next-browser — `routes`, `page`, `project` (**exclusive**)
- **Server actions**: next-browser — `action <id>` (**exclusive**)
- **SSR debugging**: next-browser — `ssr lock/unlock` (**exclusive**)
- No Chrome DevTools equivalent for these

### JS Debugging

- **Primary**: Chrome DevTools — breakpoints, stepping, `evaluate_script` (**exclusive**)
- No next-browser equivalent for JavaScript debugging

### Accessibility Tree

- **Either**: Chrome DevTools `take_snapshot` or next-browser `snapshot`
- Functionally equivalent — use whichever tool is already active in the current workflow

## Workflow

1. **Setup** — Start the dev server. Open the browser via Chrome DevTools `navigate_page` (foundation). Connect next-browser via CDP.
2. **Classify** — Parse the user's debug instruction. Map to a category from the routing table above.
3. **Execute** — Use the routing table to pick the correct primary tool for the category. Fall back to the secondary tool if the primary is unavailable or insufficient.
4. **Analyze** — Summarize findings. If code fixes are needed, provide file paths and specific changes.
5. **Iterate** — If the issue is not resolved, try the fallback tool or a different approach. Loop back to step 3.
6. **Complete** — When done, optionally close browser sessions: `next-browser close`.

## Design Quality Integration

**MANDATORY**: When this skill creates or modifies UI pages or components, it MUST integrate with the design and audit skills.

### Design First (Required for All UI Work)

When creating or modifying ANY visible page or component:
1. **Invoke the `design` skill** to handle all visual decisions — layout, color palette, typography, spacing, animations
2. The design skill owns visual excellence. It will iterate in a browser feedback loop until all 12 design categories score 10/10
3. Do not implement UI without running through the design skill first

### Audit at End (Required via Subagent)

After implementation is complete:
1. **Spawn a subagent** to run the `audit` skill on the affected URL/component
2. The audit skill checks compliance against `constitution/standards/design/scan.md`
3. Address all P0 findings before considering work complete
4. Address P1 findings when feasible
5. P2 findings are optional polish
6. Work is NOT done until the audit subagent confirms visual quality

### Design Standard Awareness

Reference `constitution/standards/design/write.md` for:
- Spacing scale (4px/8px grid system)
- Type scale (1.25 ratio)
- Color palette construction
- Component state requirements (loading/empty/error/success/permission)
- Token usage expectations

## Common Recipes

### "Why is this page slow?"

`performance_start_trace` — navigate to page — `performance_stop_trace` — `lighthouse_audit` — analyze results and recommend fixes. (Performance and Lighthouse are Chrome DevTools exclusive.)

### "This component isn't rendering correctly"

`tree` (next-browser) — find the component in the React tree — `tree <id>` to inspect props/state — `take_snapshot` (Chrome DevTools) for DOM structure — `evaluate_script` to check computed styles.

### "Check mobile layout"

`emulate` (Chrome DevTools, e.g., iPhone 14) — `screenshot` (next-browser) — `lighthouse_audit` with mobile preset — compare against desktop.

### "Debug API call failure"

`list_network_requests` (Chrome DevTools) — find the failed request — `errors` (next-browser) — correlate Next.js error details — inspect request/response payloads.

### "Inspect SSR behavior"

`ssr lock` (next-browser) — navigate to the page — `snapshot` (capture server-rendered output) — `ssr unlock` — compare with client-hydrated output.

## Reference Map

- **`references/chrome-devtools-tools.md`**: Chrome DevTools MCP tool reference (all available tools organized by category)
- **`references/next-browser-commands.md`**: next-browser CLI command reference (commands, flags, examples)
- **`references/tool-routing.md`**: Decision tree and common recipes for tool selection
