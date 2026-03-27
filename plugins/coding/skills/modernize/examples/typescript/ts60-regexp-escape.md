---
since: "TS 6.0"
min-es-target: "ES2025"
module: "any"
---

## Detection

`_.escapeRegExp(`
`.replace(/[.*+?^${}()|[\]\\]/g`
`escapeRegex(`
`escapeRegExp(`
custom functions that escape special regex characters

## Before

```typescript
// Hand-rolled regex escape — easy to get wrong
function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// Using lodash
import { escapeRegExp } from "lodash";

const userInput = "price is $9.99 (USD)";
const pattern = new RegExp(escapeRegExp(userInput), "gi");

// Building dynamic patterns with manual escaping
function buildSearchPattern(terms: string[]): RegExp {
  const escaped = terms.map((t) => escapeRegExp(t));
  return new RegExp(escaped.join("|"), "gi");
}
```

## After

```typescript
// Built-in — correct by definition
const userInput = "price is $9.99 (USD)";
const pattern = new RegExp(RegExp.escape(userInput), "gi");

// Building dynamic patterns — no utility needed
function buildSearchPattern(terms: string[]): RegExp {
  const escaped = terms.map((t) => RegExp.escape(t));
  return new RegExp(escaped.join("|"), "gi");
}
```

## Conditions

- Requires `lib: ["ES2025"]` or higher in tsconfig.json
- Available in Node 24+, Chrome 136+, Firefox 134+, Safari 18.2+
- Remove custom `escapeRegExp` / `escapeRegex` utility functions
- Remove `lodash.escaperegexp` or `_.escapeRegExp` usage
- Drop-in replacement — same semantics as the common hand-rolled version
