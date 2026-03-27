---
since: "TS 5.7"
min-es-target: "any"
module: "nodenext"
---

## Detection

`import .+ from ".+\.json"` without `with { type: "json" }`, or `require\(.+\.json"\)`

## Before

```typescript
// Unvalidated JSON import — no type attribute
import data from "./config.json";

// Using require for JSON
const pkg = require("./package.json");

// Named imports from JSON without attribute
import { version, name } from "./package.json";
```

## After

```typescript
// Validated JSON import with type attribute — TS verifies the import is JSON
import data from "./config.json" with { type: "json" };

// Named imports with type attribute
import { version, name } from "./package.json" with { type: "json" };

// Dynamic import with type attribute
const pkg = await import("./package.json", { with: { type: "json" } });
```

## Conditions

- Requires `--module nodenext`; under this mode, JSON imports without `with { type: "json" }` produce an error
- The `with` attribute tells both the runtime and TypeScript that the module is JSON, enabling proper type validation
- Default imports receive the type of the entire JSON object; named imports extract specific top-level keys
- `resolveJsonModule` must be enabled (it is implied by `nodenext`)
- Dynamic `import()` uses the options bag syntax: `import("...", { with: { type: "json" } })`
- Does not apply to non-relative JSON imports from `node_modules` (those follow the package's own export conditions)
