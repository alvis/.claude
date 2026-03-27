---
since: "TS 5.8"
min-es-target: "any"
module: "node18"
---

## Detection

`"module": "nodenext"` in tsconfig.json when project targets Node.js 18 specifically

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
    "node": ">=18"
  }
}
```

```typescript
// Code might accidentally use features only available in Node.js 20+
// and TS wouldn't warn about it under nodenext
```

## After

```jsonc
// tsconfig.json — locked to Node.js 18 module semantics
{
  "compilerOptions": {
    "module": "node18",
    "moduleResolution": "node18",
    "target": "ES2022"
  }
}
```

```jsonc
// package.json
{
  "engines": {
    "node": ">=18"
  }
}
```

```typescript
// TS will now error if code uses module features not available in Node.js 18
// e.g., require() of ESM (Node.js 22+) would be flagged
```

## Conditions

- Use when the project explicitly supports Node.js 18 and should not rely on newer module behavior
- `--module node18` implies `--moduleResolution node18`; they should be set together
- `nodenext` always tracks the latest stable Node.js version's behavior, which can silently allow features unavailable in older runtimes
- `node18` provides a stable contract: the module resolution and semantics are frozen to what Node.js 18 supports
- When the project upgrades its minimum Node.js version, update `module` accordingly (e.g., `node20`, `nodenext`)
- Does not affect runtime behavior; this is a compile-time check to prevent using unsupported module features
