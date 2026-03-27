---
since: "TS 6.0"
min-es-target: "any"
module: "any"
---

## Detection

`"module": "amd"` in tsconfig.json
`"module": "umd"` in tsconfig.json
`"module": "system"` in tsconfig.json

## Before

```jsonc
// tsconfig.json — AMD module format
{
  "compilerOptions": {
    "module": "amd",
    "outFile": "./dist/bundle.js",
    "target": "ES2020"
  }
}
```

```jsonc
// tsconfig.json — UMD module format
{
  "compilerOptions": {
    "module": "umd",
    "outDir": "./dist",
    "target": "ES2020"
  }
}
```

```jsonc
// tsconfig.json — SystemJS module format
{
  "compilerOptions": {
    "module": "system",
    "outFile": "./dist/app.js",
    "target": "ES2020"
  }
}
```

```typescript
// Source compiled by tsc into AMD/UMD/SystemJS wrappers
import { logger } from "./logger";
import express from "express";

export function startServer(port: number) {
  const app = express();
  logger.info(`Starting on port ${port}`);
  app.listen(port);
}
```

## After

```jsonc
// tsconfig.json — for Node.js (supports both ESM and CJS)
{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "outDir": "./dist",
    "target": "ES2020"
  }
}
```

```jsonc
// tsconfig.json — for bundler-based projects
{
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "bundler",
    "outDir": "./dist",
    "target": "ES2020"
  }
}
```

```jsonc
// tsconfig.json — for CJS-only environments
{
  "compilerOptions": {
    "module": "commonjs",
    "moduleResolution": "node",
    "outDir": "./dist",
    "target": "ES2020"
  }
}
```

```javascript
// For AMD/UMD output, use a bundler step after tsc
// rollup.config.mjs
export default {
  input: "./dist/main.js",
  output: [
    { file: "./dist/bundle.amd.js", format: "amd" },
    { file: "./dist/bundle.umd.js", format: "umd", name: "MyLib" },
  ],
};
```

## Conditions

- AMD, UMD, and SystemJS module formats are removed in TS 6.0
- Supported `module` values: `nodenext`, `esnext`, `commonjs`, `es2015`, `es2020`, `es2022`, `node16`
- For libraries that need UMD output, use TypeScript with `module: "esnext"` and Rollup/webpack to produce UMD bundles
- Projects using `outFile` with AMD/SystemJS must also migrate away from `outFile`
- `nodenext` is recommended for Node.js projects; `esnext` or `bundler` resolution for frontend
