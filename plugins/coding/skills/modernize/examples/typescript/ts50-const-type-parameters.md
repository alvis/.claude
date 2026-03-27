---
since: "TS 5.0"
min-es-target: "any"
module: "any"
---

## Detection

`as const` assertions at generic function call sites

## Before

```typescript
declare function createRoute<T>(config: T): T;

// callers must add `as const` to preserve literal types
const route = createRoute({
  path: "/users",
  method: "GET",
  params: ["id", "name"],
} as const);
// route.method is "GET", route.params is readonly ["id", "name"]
```

## After

```typescript
declare function createRoute<const T>(config: T): T;

// callers get literal inference automatically
const route = createRoute({
  path: "/users",
  method: "GET",
  params: ["id", "name"],
});
// route.method is "GET", route.params is readonly ["id", "name"]
```

## Conditions

- Only beneficial when callers currently need `as const` to get narrow literal types from a generic function
- The `const` modifier goes on the type parameter declaration, not on the call site
- Existing `as const` call sites continue to work but become redundant and can be removed
- Does not affect runtime behavior; this is purely a type-level change
