---
since: "TS 5.2"
min-es-target: "ES2023"
module: "any"
---

## Detection

`new WeakMap` with throwaway object literals (`{}`) used as keys when a symbol would be more semantic

## Before

```typescript
// Using empty objects as WeakMap keys for private/associated data
const internalState = new WeakMap<object, { count: number }>();

// Throwaway objects as opaque tokens
const CACHE_KEY = {};
const SESSION_KEY = {};

internalState.set(CACHE_KEY, { count: 0 });
internalState.set(SESSION_KEY, { count: 0 });

// Problem: keys are anonymous, no descriptive identity
console.log(CACHE_KEY); // {}
console.log(SESSION_KEY); // {}

// Also applies to WeakSet and WeakRef
const processed = new WeakSet<object>();
processed.add(CACHE_KEY);
```

## After

```typescript
// Symbols as WeakMap keys — descriptive and lightweight
const internalState = new WeakMap<symbol, { count: number }>();

const CACHE_KEY = Symbol("cache");
const SESSION_KEY = Symbol("session");

internalState.set(CACHE_KEY, { count: 0 });
internalState.set(SESSION_KEY, { count: 0 });

// Keys are self-documenting
console.log(CACHE_KEY); // Symbol(cache)
console.log(SESSION_KEY); // Symbol(session)

// Also works with WeakSet and WeakRef
const processed = new WeakSet<symbol>();
processed.add(CACHE_KEY);
```

## Conditions

- Only non-registered symbols are valid — `Symbol("desc")` works, `Symbol.for("global")` does not
- `Symbol.for()` symbols are globally shared and never garbage collected, so they are rejected as WeakMap keys
- Requires ES2023 runtime support for symbol-keyed weak collections
- Requires `target: "ES2023"` or `lib: ["ES2023"]` in tsconfig
- Migrate only when the key's sole purpose is identity — if the key object carries data, keep it as an object
