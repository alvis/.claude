---
since: "TS 5.7"
min-es-target: "any"
module: "nodenext or preserve"
---

## Detection

`from "\./[^"]+\.js"` or `from "\.\./[^"]+\.js"` in `.ts` source files

## Before

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext"
  }
}
```

```typescript
// src/index.ts — manually writing .js extensions for .ts sources
import { createUser } from "./services/user.js";
import { validateEmail } from "../utils/validation.js";
import type { Config } from "./types/config.js";

export { createUser, validateEmail };
export type { Config };
```

## After

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "rewriteRelativeImportExtensions": true
  }
}
```

```typescript
// src/index.ts — write .ts extensions, TS rewrites to .js in emit
import { createUser } from "./services/user.ts";
import { validateEmail } from "../utils/validation.ts";
import type { Config } from "./types/config.ts";

export { createUser, validateEmail };
export type { Config };
```

## Conditions

- Only rewrites relative imports (starting with `./` or `../`); bare specifiers and non-relative paths are never rewritten
- Rewrites `.ts` to `.js`, `.mts` to `.mjs`, `.cts` to `.cjs` (and corresponding `.d.ts` variants)
- Requires `--module nodenext` or `--module preserve`
- Does not rewrite extensions inside dynamic `import()` expression string literals
- Type-only imports are also rewritten in declaration output
- Simplifies the developer experience by allowing imports to match the actual source file extension
