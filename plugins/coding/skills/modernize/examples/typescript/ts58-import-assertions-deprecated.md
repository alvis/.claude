---
since: "TS 5.8"
min-es-target: "any"
module: "nodenext"
---

## Detection

`assert\s*\{\s*type:\s*"json"\s*\}` in import statements

## Before

```typescript
// Import assertions using the deprecated `assert` keyword
import config from "./config.json" assert { type: "json" };
import translations from "../i18n/en.json" assert { type: "json" };

// Dynamic import with assert
const schema = await import("./schema.json", { assert: { type: "json" } });

// Re-export with assert
export { default as manifest } from "./manifest.json" assert { type: "json" };
```

## After

```typescript
// Import attributes using the `with` keyword
import config from "./config.json" with { type: "json" };
import translations from "../i18n/en.json" with { type: "json" };

// Dynamic import with `with`
const schema = await import("./schema.json", { with: { type: "json" } });

// Re-export with `with`
export { default as manifest } from "./manifest.json" with { type: "json" };
```

## Conditions

- `assert` was deprecated in TS 5.3 in favor of `with`; TS 5.8 makes `assert` an error under `--module nodenext`
- This is a direct keyword substitution: replace `assert` with `with` in all import/export statements
- Dynamic imports change from `{ assert: { type: "json" } }` to `{ with: { type: "json" } }`
- The `with` keyword follows the TC39 Import Attributes proposal (Stage 3, renamed from Import Assertions)
- Node.js 22+ supports `with { type: "json" }` natively
- If targeting older Node.js versions that only support `assert`, stay on an earlier TS module mode or keep `assert` with a non-nodenext module setting
