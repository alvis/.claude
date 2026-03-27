---
since: "TS 5.7"
min-es-target: "any"
module: "nodenext"
---

## Detection

`require\("[^"]+\.js"\)` in `.ts` or `.cts` files when the resolved module is a `.ts` file

## Before

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "module": "nodenext",
    "allowImportingTsExtensions": true,
    "noEmit": true
  }
}
```

```typescript
// src/index.cts — require() with .js extension even though source is .ts
const { createUser } = require("./services/user.js");
const { validateEmail } = require("../utils/validation.js");

// Prior to TS 5.7, --allowImportingTsExtensions only worked with import statements
// import { createUser } from "./services/user.ts"; // worked
// require("./services/user.ts") // did NOT work
```

## After

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "module": "nodenext",
    "allowImportingTsExtensions": true,
    "noEmit": true
  }
}
```

```typescript
// src/index.cts — require() now works with .ts extensions too
const { createUser } = require("./services/user.ts");
const { validateEmail } = require("../utils/validation.ts");

// Both import and require now support .ts extensions consistently
import { parseConfig } from "./config/parser.ts";
```

## Conditions

- Requires `--allowImportingTsExtensions` combined with either `--noEmit` or `--emitDeclarationOnly`
- Prior to TS 5.7, `--allowImportingTsExtensions` only affected `import` statements; `require()` calls still needed `.js` extensions
- Primarily useful in non-emitting setups such as projects using a bundler or runtime that handles TypeScript directly (ts-node, tsx, Bun, Deno)
- Only applies to relative `require()` calls; bare specifiers are resolved through `node_modules` as usual
- Can be combined with `--rewriteRelativeImportExtensions` if emit is also desired
