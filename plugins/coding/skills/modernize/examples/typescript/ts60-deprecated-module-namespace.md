---
since: "TS 6.0"
min-es-target: "any"
module: "any"
---

## Detection

`module ` followed by an identifier and `{` (namespace declaration using `module` keyword)
`module` keyword used outside of `declare module` augmentations

## Before

```typescript
// Using 'module' keyword for namespace — deprecated in TS 6.0
module MyApp {
  export interface Config {
    apiUrl: string;
    timeout: number;
  }

  export function initialize(config: Config) {
    console.log(`Connecting to ${config.apiUrl}`);
  }
}

// Nested modules
module MyApp.Utils {
  export function debounce<T extends (...args: unknown[]) => void>(
    fn: T,
    ms: number,
  ): T {
    let timer: ReturnType<typeof setTimeout>;
    return ((...args: unknown[]) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), ms);
    }) as T;
  }
}

// Usage
const config: MyApp.Config = { apiUrl: "https://api.example.com", timeout: 5000 };
MyApp.initialize(config);
```

## After

```typescript
// Using 'namespace' keyword — the correct syntax
namespace MyApp {
  export interface Config {
    apiUrl: string;
    timeout: number;
  }

  export function initialize(config: Config) {
    console.log(`Connecting to ${config.apiUrl}`);
  }
}

// Nested namespaces
namespace MyApp.Utils {
  export function debounce<T extends (...args: unknown[]) => void>(
    fn: T,
    ms: number,
  ): T {
    let timer: ReturnType<typeof setTimeout>;
    return ((...args: unknown[]) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), ms);
    }) as T;
  }
}

// Usage unchanged
const config: MyApp.Config = { apiUrl: "https://api.example.com", timeout: 5000 };
MyApp.initialize(config);
```

## Conditions

- The `module` keyword for namespace declarations is deprecated in TS 6.0
- Replace `module Foo {` with `namespace Foo {` — semantically identical
- `declare module "..."` for ambient module declarations is NOT affected
- `declare module` for module augmentation is NOT affected
- This is a keyword-only change — no behavioral or structural differences
- Consider migrating namespaces to ES modules for new code
