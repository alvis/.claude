# next-browser CLI -- Command Reference

## Lifecycle
- `next-browser open <url>` -- open browser and navigate to URL
- `next-browser close` -- close browser session
- `next-browser status` -- show connection status

## Navigation
- `next-browser goto <url>` -- navigate to URL
- `next-browser back` -- go back
- `next-browser forward` -- go forward
- `next-browser reload` -- reload page

## Inspection
- `next-browser snapshot` -- capture accessibility tree
- `next-browser screenshot [path]` -- capture screenshot
- `next-browser preview` -- quick visual preview
- `next-browser tree` -- show React component tree
- `next-browser tree <id>` -- inspect specific component (props, state)
- `next-browser errors` -- show Next.js error overlay messages
- `next-browser logs` -- show console output

## Interaction
- `next-browser click <selector>` -- click element
- `next-browser type <selector> <text>` -- type into element
- `next-browser viewport <width> <height>` -- set viewport size
- `next-browser network` -- show network requests

## Next.js Specific
- `next-browser routes` -- list all Next.js routes
- `next-browser page [path]` -- inspect page metadata and data fetching
- `next-browser project` -- show Next.js project info (version, config)
- `next-browser action <id>` -- inspect server action by ID
- `next-browser ssr lock` -- lock SSR (prevent re-renders during inspection)
- `next-browser ssr unlock` -- unlock SSR (resume normal rendering)
