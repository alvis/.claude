---
since: "TS 5.6"
min-es-target: "any"
module: "any"
---

## Detection

`import "` or `import '` -- side-effect-only imports that are not validated for existence

## Before

```typescript
// side-effect imports -- TS does not verify these paths by default
import "./styles.css";
import "./polyfills";
import "./stlyes.css"; // typo -- silently ignored, styles missing at runtime
import "server-only";
import "./register-hooks";
import "./analytics.js"; // file was deleted -- no error
```

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    // no verification of side-effect imports
  }
}
```

## After

```typescript
// all side-effect imports are now verified
import "./styles.css";
import "./polyfills";
// import "./stlyes.css";  // error: Cannot find module './stlyes.css'
import "server-only";
import "./register-hooks";
// import "./analytics.js"; // error: Cannot find module './analytics.js'
```

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "noUncheckedSideEffectImports": true
  }
}
```

```typescript
// for CSS and other non-JS modules, add type declarations
// global.d.ts
declare module "*.css" {
  const content: Record<string, string>;
  export default content;
}

declare module "*.svg" {
  const content: string;
  export default content;
}
```

## Conditions

- Enable `noUncheckedSideEffectImports` in tsconfig to opt in
- Side-effect imports (`import "module"`) will be resolved and checked for existence
- Requires type declarations for non-JS modules (CSS, SVG, images, etc.)
- Catches typos in import paths that would otherwise silently fail at runtime
- Also validates that the resolved module actually exists on disk
- Packages like `server-only` must be installed or declared
