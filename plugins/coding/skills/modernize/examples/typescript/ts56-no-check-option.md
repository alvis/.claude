---
since: "TS 5.6"
min-es-target: "any"
module: "any"
---

## Detection

`tsc && tsc --emitDeclarationOnly` or slow CI build scripts running full type checking when only emit is needed

## Before

```jsonc
// package.json -- CI build script
{
  "scripts": {
    "build": "tsc",
    "build:declarations": "tsc --emitDeclarationOnly",
    "typecheck": "tsc --noEmit",
    "ci": "npm run typecheck && npm run build"
  }
}
```

```yaml
# CI pipeline -- type checking and emit are coupled
steps:
  - name: Build
    run: npm run build  # full type check + emit (~45s)
  - name: Test
    run: npm test
```

## After

```jsonc
// package.json -- separated type checking from emit
{
  "scripts": {
    "build": "tsc --noCheck",
    "typecheck": "tsc --noEmit",
    "ci": "npm run build & npm run typecheck && wait"
  }
}
```

```yaml
# CI pipeline -- type checking and emit run in parallel
steps:
  - name: Build and Typecheck
    run: |
      tsc --noCheck &          # emit JS/declarations (~15s)
      tsc --noEmit &           # type check only (~30s)
      wait                     # wait for both
  - name: Test
    run: npm test
```

## Conditions

- `--noCheck` skips type checking and only performs emit (JS output, declaration files, source maps)
- Must still run full `tsc` or `tsc --noEmit` separately for type safety
- Useful for CI pipelines where emit and type checking can run in parallel
- Reduces wall-clock build time by parallelizing independent steps
- Not a substitute for type checking -- always run a full check before merging
- Compatible with `--declaration`, `--declarationMap`, and `--sourceMap` flags
