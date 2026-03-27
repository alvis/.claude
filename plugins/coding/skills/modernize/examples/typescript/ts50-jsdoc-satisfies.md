---
since: "TS 5.0"
min-es-target: "any"
module: "any"
---

## Detection

`@type` JSDoc annotations in JavaScript files (with `checkJs` or `allowJs`) that lose type specificity

## Before

```javascript
/** @typedef {{ name: string; handler: () => void; shortcut?: string }} Command */

/** @type {Record<string, Command>} */
const commands = {
  open: {
    name: "Open File",
    handler: () => openDialog(),
    shortcut: "Ctrl+O",
  },
  save: {
    name: "Save File",
    handler: () => saveFile(),
    shortcut: "Ctrl+S",
  },
};

// Problem: key type is widened to `string` — no autocomplete
// commands["nonexistent"] does not produce a type error
const keys = Object.keys(commands); // string[]
```

## After

```javascript
/** @typedef {{ name: string; handler: () => void; shortcut?: string }} Command */

/** @satisfies {Record<string, Command>} */
const commands = {
  open: {
    name: "Open File",
    handler: () => openDialog(),
    shortcut: "Ctrl+O",
  },
  save: {
    name: "Save File",
    handler: () => saveFile(),
    shortcut: "Ctrl+S",
  },
};

// keys are preserved as "open" | "save"
commands.open.shortcut; // string | undefined — validated but narrow
commands.save.name; // "Save File" — literal type preserved
```

## Conditions

- Only applies to JavaScript files using JSDoc type checking (`checkJs: true` or `// @ts-check`)
- Not relevant for `.ts` files, which use the `satisfies` operator directly (available since TS 4.9)
- `@satisfies` validates the value against the target type while preserving the inferred narrow type, unlike `@type` which widens to the annotated type
