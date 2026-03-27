---
since: "TS 5.0"
min-es-target: "any"
module: "any"
---

## Detection

`export * from` re-exporting modules that contain only type declarations

## Before

```typescript
// types.ts
export interface User {
  id: string;
  name: string;
}

export type Role = "admin" | "viewer" | "editor";

// index.ts — re-exports everything, but may emit runtime code
export * from "./types";
```

## After

```typescript
// types.ts
export interface User {
  id: string;
  name: string;
}

export type Role = "admin" | "viewer" | "editor";

// index.ts — guaranteed to be erased at runtime
export type * from "./types";
```

## Conditions

- Only use when the entire re-exported module contains exclusively type declarations (interfaces, type aliases, `declare` statements)
- Do not use if the module also exports runtime values (classes, functions, variables, enums)
- Particularly useful with `verbatimModuleSyntax` enabled, which enforces explicit type-only syntax
- Helps bundlers with tree-shaking by signaling that no runtime code is involved
