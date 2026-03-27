---
since: "TS 5.0"
min-es-target: "any"
module: "any"
---

## Detection

`"importsNotUsedAsValues"` or `"preserveValueImports"` in tsconfig.json

## Before

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "importsNotUsedAsValues": "error",
    "preserveValueImports": true
  }
}
```

```typescript
// ambiguous — is User a type or a value?
import { User, createUser } from "./user";

type Admin = User & { role: "admin" };
```

## After

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "verbatimModuleSyntax": true
  }
}
```

```typescript
// explicit — types and values are visually distinct
import type { User } from "./user";
import { createUser } from "./user";

type Admin = User & { role: "admin" };
```

## Conditions

- Replaces both `importsNotUsedAsValues` and `preserveValueImports`, which are deprecated in TS 5.0 and become errors in TS 5.5
- All type-only imports must use `import type` syntax; the compiler will error on type imports without the `type` keyword
- In CommonJS files (`.cts`), `import` statements must be written as `import ... = require(...)` since `verbatimModuleSyntax` preserves import syntax exactly as written
- Review all imports in the codebase before enabling; automated codefixes are available via `tsc --fixAll`
