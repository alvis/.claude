---
since: "TS 5.9"
min-es-target: "any"
module: "node20"
---

## Detection

`"module": "nodenext"` in tsconfig.json when project targets Node.js 20 specifically

## Before

```jsonc
// tsconfig.json — using nodenext which tracks latest Node.js behavior
{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "target": "ES2022"
  }
}
```

```jsonc
// package.json
{
  "engines": {
    "node": ">=20"
  }
}
```

```typescript
// Under nodenext, TS might allow features like require() of ESM
// (Node.js 22+) which would fail at runtime on Node.js 20
const mod = require("esm-only-package");
// ^^ This works on Node.js 22+ but throws on Node.js 20
```

## After

```jsonc
// tsconfig.json — locked to Node.js 20 module semantics
{
  "compilerOptions": {
    "module": "node20",
    "moduleResolution": "node20",
    "target": "ES2022"
  }
}
```

```jsonc
// package.json
{
  "engines": {
    "node": ">=20"
  }
}
```

```typescript
// TS will now error on module features not available in Node.js 20
// require() of ESM is correctly flagged as unsupported
const mod = await import("esm-only-package");
// ^^ Must use dynamic import for ESM packages on Node.js 20
```

## Conditions

- Use when the project explicitly supports Node.js 20 as its minimum version
- `--module node20` implies `--moduleResolution node20`; set them together
- Provides the same stability guarantee as `--module node18`: module semantics are frozen to what Node.js 20 supports
- `nodenext` always tracks the latest stable Node.js version, which can permit features unavailable on Node.js 20 (e.g., synchronous `require()` of ESM from Node.js 22)
- When the project upgrades its minimum Node.js version, update `module` to match (e.g., `node22`, `nodenext`)
- Does not affect runtime behavior; this is a compile-time guard against using unsupported module features
