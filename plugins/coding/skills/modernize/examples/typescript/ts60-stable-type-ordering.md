---
since: "TS 6.0"
min-es-target: "any"
module: "any"
---

## Detection

Non-deterministic union ordering in `.d.ts` files causing unnecessary git diffs between builds.
Flapping type order in generated declaration files.

## Before

```jsonc
// tsconfig.json — no stable ordering guarantee
{
  "compilerOptions": {
    "declaration": true,
    "outDir": "./dist"
  }
}
```

```typescript
// src/utils.ts
export function parse(input: string | number | boolean) {
  // ...
}
```

```typescript
// dist/utils.d.ts — first build
export declare function parse(input: string | number | boolean): void;

// dist/utils.d.ts — second build (same source, different order)
export declare function parse(input: number | string | boolean): void;

// git diff shows spurious changes, CI fails on declaration drift checks
```

## After

```jsonc
// tsconfig.json — deterministic declaration output
{
  "compilerOptions": {
    "declaration": true,
    "outDir": "./dist",
    "stableTypeOrdering": true
  }
}
```

```typescript
// dist/utils.d.ts — consistent across builds
export declare function parse(input: boolean | number | string): void;

// Union members are sorted deterministically — no more git churn
```

## Conditions

- Primarily useful for libraries that publish `.d.ts` files
- Eliminates spurious diffs in declaration files between builds
- Helps CI checks that verify declaration files are up-to-date
- No runtime impact — only affects emitted `.d.ts` output
- Safe to enable in all projects; no behavioral change to type checking
