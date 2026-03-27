---
since: "TS 6.0"
min-es-target: "ES2025"
module: "any"
---

## Detection

`Promise.resolve().then(() =>`
`new Promise((resolve, reject) => { try {`
wrapping synchronous functions in promise chains to catch thrown errors

## Before

```typescript
// Pattern 1: Promise.resolve().then — hides sync throws in microtask
function fetchConfig(path: string): Promise<Config> {
  return Promise.resolve().then(() => {
    const raw = readFileSync(path); // throws if missing
    return JSON.parse(raw);        // throws on bad JSON
  });
}

// Pattern 2: new Promise with try/catch boilerplate
function parseInput(input: string): Promise<Data> {
  return new Promise((resolve, reject) => {
    try {
      const data = JSON.parse(input);
      resolve(validate(data));
    } catch (e) {
      reject(e);
    }
  });
}

// Pattern 3: async wrapper just to catch sync throws
async function loadModule(name: string): Promise<Module> {
  const resolved = resolveModulePath(name); // might throw synchronously
  return await import(resolved);
}
```

## After

```typescript
// Clean — synchronous throws become rejected promises automatically
function fetchConfig(path: string): Promise<Config> {
  return Promise.try(() => {
    const raw = readFileSync(path);
    return JSON.parse(raw);
  });
}

// No boilerplate needed
function parseInput(input: string): Promise<Data> {
  return Promise.try(() => {
    const data = JSON.parse(input);
    return validate(data);
  });
}

// Works with async callbacks too
function loadModule(name: string): Promise<Module> {
  return Promise.try(async () => {
    const resolved = resolveModulePath(name);
    return await import(resolved);
  });
}
```

## Conditions

- Requires `lib: ["ES2025"]` or higher in tsconfig.json
- Catches synchronous throws and wraps them as rejected promises
- Accepts both sync and async callbacks
- Replaces `Promise.resolve().then(fn)` pattern — avoids unnecessary microtask deferral
- Replaces `new Promise` + `try/catch` boilerplate
- Not needed if the function is already `async` — `async` functions inherently catch sync throws
