---
since: "TS 5.7"
min-es-target: "ES2024"
module: "any"
---

## Detection

`new Promise\(\s*\(\s*res(olve)?\s*,\s*rej(ect)?\s*\)\s*=>` combined with outer `let resolve` or `let reject` variables

## Before

```typescript
// Deferred promise pattern — verbose and requires non-null assertions
function createDeferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

// Usage
const { promise, resolve, reject } = createDeferred<string>();
someCallback(() => resolve("done"));
anotherCallback((err) => reject(err));
await promise;
```

```typescript
// Inline deferred pattern — even more awkward
let resolve: (value: number) => void;
let reject: (reason?: unknown) => void;
const promise = new Promise<number>((res, rej) => {
  resolve = res;
  reject = rej;
});

setTimeout(() => resolve!(42), 1000);
const result = await promise;
```

## After

```typescript
// Built-in Promise.withResolvers — clean, no wrapper needed
const { promise, resolve, reject } = Promise.withResolvers<string>();
someCallback(() => resolve("done"));
anotherCallback((err) => reject(err));
await promise;
```

```typescript
// Inline usage — one-liner replaces the entire deferred pattern
const { promise, resolve, reject } = Promise.withResolvers<number>();

setTimeout(() => resolve(42), 1000);
const result = await promise;
```

## Conditions

- Requires `lib: ["ES2024"]` or higher in tsconfig (or `"ESNext"`)
- Runtime support: Node.js 22+, Chrome 119+, Firefox 121+, Safari 17.4+
- Returns `{ promise, resolve, reject }` with correct types — no non-null assertions needed
- Directly replaces any "deferred promise" utility function or inline pattern
- The generic type parameter `Promise.withResolvers<T>()` infers the resolution type
- If targeting older runtimes, a polyfill is needed; otherwise keep the manual pattern
