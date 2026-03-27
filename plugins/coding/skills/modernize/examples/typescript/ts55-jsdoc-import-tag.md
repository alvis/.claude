---
since: "TS 5.5"
min-es-target: "any"
module: "any"
---

## Detection

`@typedef.*import\(` -- JSDoc `@typedef` with inline `import()` expressions for type imports in `.js` files

## Before

```javascript
// utils.js -- JavaScript file with JSDoc types

/** @typedef {import("./types").Config} Config */
/** @typedef {import("./types").User} User */
/** @typedef {import("express").Request} Request */
/** @typedef {import("express").Response} Response */

/**
 * @param {Config} config
 * @param {Request} req
 * @returns {User}
 */
function handleRequest(config, req) {
  // ...
}
```

## After

```javascript
// utils.js -- JavaScript file with JSDoc types

/** @import { Config, User } from "./types" */
/** @import { Request, Response } from "express" */

/**
 * @param {Config} config
 * @param {Request} req
 * @returns {User}
 */
function handleRequest(config, req) {
  // ...
}
```

## Conditions

- Only applies to JavaScript files (`.js`, `.mjs`, `.cjs`) using JSDoc for type checking
- Multiple types from the same module can be combined in a single `@import` tag
- Supports `type` qualifier: `/** @import { type Config } from "./types" */`
- The `@import` tag is erased at runtime -- it exists only for type checking
- Requires TypeScript 5.5+ for the language server and type checker to recognize the tag
