---
since: "TS 5.3"
min-es-target: "any"
module: "esnext or nodenext"
---

## Detection

`assert { type:` in import or re-export statements

## Before

```typescript
// Import assertion syntax (deprecated)
import config from "./config.json" assert { type: "json" };
import styles from "./theme.css" assert { type: "css" };

// Dynamic import with assert
const data = await import("./data.json", {
  assert: { type: "json" },
});

// Re-export with assert
export { default as schema } from "./schema.json" assert { type: "json" };
```

## After

```typescript
// Import attribute syntax (TC39 standard)
import config from "./config.json" with { type: "json" };
import styles from "./theme.css" with { type: "css" };

// Dynamic import with 'with'
const data = await import("./data.json", {
  with: { type: "json" },
});

// Re-export with 'with'
export { default as schema } from "./schema.json" with { type: "json" };
```

## Conditions

- `assert` syntax is deprecated in the TC39 proposal; `with` is the standardized keyword
- Requires `module: "esnext"` or `module: "nodenext"` in tsconfig
- Node.js 21+ supports `with` syntax natively; Node.js 18-20 only support `assert`
- Bundlers (Webpack 5.93+, Vite 5+, esbuild) have varying levels of support — verify before migrating
- Both `assert` and `with` may coexist during transition, but prefer `with` for new code
