---
since: "TS 6.0"
min-es-target: "any"
module: "any"
---

## Detection

`"outFile"` in tsconfig.json

## Before

```jsonc
// tsconfig.json — concatenation-based output
{
  "compilerOptions": {
    "module": "system",
    "outFile": "./dist/bundle.js",
    "target": "ES2020"
  }
}
```

```typescript
// Files were concatenated in dependency order by tsc
// src/utils.ts
namespace App {
  export function greet(name: string) {
    return `Hello, ${name}`;
  }
}

// src/main.ts
namespace App {
  console.log(greet("world"));
}

// Output: single dist/bundle.js with both files concatenated
```

## After

```jsonc
// tsconfig.json — emit individual files, let a bundler combine them
{
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "bundler",
    "outDir": "./dist",
    "target": "ES2020"
  }
}
```

```typescript
// src/utils.ts — use standard ES modules
export function greet(name: string) {
  return `Hello, ${name}`;
}

// src/main.ts
import { greet } from "./utils.js";

console.log(greet("world"));
```

```javascript
// esbuild.config.mjs — bundler handles concatenation
import { build } from "esbuild";

await build({
  entryPoints: ["./dist/main.js"],
  bundle: true,
  outfile: "./dist/bundle.js",
  format: "esm",
});
```

## Conditions

- `--outFile` is removed in TS 6.0 — the compiler will error on this option
- Migrate namespace-based concatenation to ES module imports/exports
- Use a bundler (esbuild, webpack, rollup, vite) for single-file output
- Projects using `outFile` with `module: "system"` or `module: "amd"` must also migrate module format
- Consider this an opportunity to adopt standard ES modules throughout
