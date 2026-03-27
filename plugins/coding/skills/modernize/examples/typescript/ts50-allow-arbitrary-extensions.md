---
since: "TS 5.0"
min-es-target: "any"
module: "any"
---

## Detection

Ambient module declarations for non-JS file extensions (`declare module '*.css'`, `declare module '*.svg'`, etc.)

## Before

```typescript
// global.d.ts — one catch-all declaration for all .css imports
declare module "*.css" {
  const classes: Record<string, string>;
  export default classes;
}

// component.ts — no per-file type safety
import styles from "./button.css";
// styles is Record<string, string> for every .css file, even if keys differ
```

## After

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "allowArbitraryExtensions": true
  }
}
```

```typescript
// button.d.css.ts — co-located declaration specific to button.css
declare const classes: {
  readonly container: string;
  readonly primary: string;
  readonly disabled: string;
};
export default classes;

// component.ts — precise types per file
import styles from "./button.css";
// styles.container, styles.primary, styles.disabled are known
// styles.nonexistent is a type error
```

## Conditions

- Requires creating a `.d.{ext}.ts` file next to each non-JS import (e.g., `button.d.css.ts` for `button.css`)
- Provides per-file type safety instead of a single global ambient declaration
- Tools like `typed-css-modules` or `vite-plugin-css-modules-dts` can auto-generate these declaration files
- The global ambient declaration approach still works; this is an opt-in improvement for stricter type safety
