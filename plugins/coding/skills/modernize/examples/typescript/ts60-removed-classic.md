---
since: "TS 6.0"
min-es-target: "any"
module: "any"
---

## Detection

`"moduleResolution": "classic"` in tsconfig.json

## Before

```jsonc
// tsconfig.json — classic module resolution
{
  "compilerOptions": {
    "module": "commonjs",
    "moduleResolution": "classic",
    "outDir": "./dist"
  }
}
```

```typescript
// classic resolution searches: ./module.ts, ./module/index.ts
// Does NOT look in node_modules — surprising behavior
import { helper } from "./utils";
import express from "express"; // may fail to resolve under classic
```

## After

```jsonc
// tsconfig.json — for Node.js projects
{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "outDir": "./dist"
  }
}
```

```jsonc
// tsconfig.json — for bundler-based projects (Vite, webpack, esbuild)
{
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "bundler",
    "outDir": "./dist"
  }
}
```

```typescript
// Both resolution strategies correctly resolve node_modules
import { helper } from "./utils.js"; // nodenext requires extensions
import express from "express";

// With bundler resolution, extensions are optional
import { helper } from "./utils";
import express from "express";
```

## Conditions

- `classic` module resolution is removed in TS 6.0
- Use `nodenext` for Node.js projects — requires file extensions in relative imports
- Use `bundler` for frontend or bundler-based projects — allows bare imports without extensions
- `nodenext` enforces stricter ESM/CJS interop rules; may require adding `.js` extensions to imports
- Test thoroughly after switching — resolution differences can surface missing or misresolved modules
