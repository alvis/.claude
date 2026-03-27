# Component Design Patterns

Design patterns for specific component types. Load relevant sections when designing specific UI types.

## Universal States

Every component must handle these 5 states:

- **Loading**: skeleton/placeholder with stable height; prevent double-submit; show progress when wait is noticeable
- **Empty**: explain what "empty" means; provide next step (create/import/change filters)
- **Error**: what happened + why (if safe) + what to do; preserve user input
- **Success**: confirm outcome + provide next action (view, undo, share)
- **Permission**: explain why blocked + where to request access

## Affordance & Signifiers

- Primary actions use real buttons with verb labels (not "OK"/"Done")
- Icon-only reserved for universally-known actions (search/close/more/settings)
- Links have clear signifier (underline or strong hover/contrast), not color-only
- Custom clickable surfaces: `cursor: pointer` + visible focus style
- Card/list rows that open: hover state + chevron or "View" affordance
- Controls placed near what they affect; group controls with controlled content

## Lists (Table / Cards)

- One primary column/field; secondary details visually muted
- Consistent row height and alignment; no jagged columns
- Search/filter/sort before the list, not after
- Selected filters visible and removable
- High-frequency row actions visible; long-tail under "more" menu

## Detail Pages

- Clear page title matching the object
- Key facts near top; secondary info below or collapsed
- Actions grouped by intent (primary, secondary, destructive)
- Related items and history grouped and titled

## Forms

- Use defaults and reasonable prefill to reduce thinking
- Use presets when choices are complex
- Inline validation with format hints before submit
- Group fields by meaning with headings
- Consistent label position and style
- One primary submit action; disabled state + clear error placement

## Settings / Preferences

- Group by mental model (account, security, notifications, integrations, appearance)
- Clear label + short value explanation only if needed
- Destructive actions separated and labeled; never hidden among benign toggles

## Motion Patterns

- Each animation explains hierarchy or state change — not decoration
- Default vocabulary: fade → small translate+fade → tiny scale+fade for overlays
- Canvas/content area stays stable; only panels/overlays animate
- Same component type uses same motion pattern
- No layout jumps; use skeletons to keep layout stable while loading

## Dashboards

- Primary metric prominent; secondary metrics visually subordinate
- Filters and time range controls above data, not below
- Data visualizations labeled and accessible (not color-only)
- Loading state for each widget independently

## Copy Conventions

- Prefer verb labels for actions ("Save draft", "Send invite", not "Submit")
- Error messages: what happened + what to do (not error codes)
- Minimize copy; add text only when it prevents errors or increases trust
- Same concept = same word everywhere
