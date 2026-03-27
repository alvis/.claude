---
since: "TS 5.2"
min-es-target: "ES2022"
module: "any"
---

## Detection

`try { ... } finally { *.close() }` or `try { ... } finally { *.dispose() }` resource cleanup patterns

## Before

```typescript
// Synchronous resource cleanup
function readConfig(path: string): Config {
  const handle = openFile(path);
  try {
    const content = handle.read();
    return JSON.parse(content) as Config;
  } finally {
    handle.close();
  }
}

// Async resource cleanup
async function queryDatabase(sql: string): Promise<Row[]> {
  const connection = await pool.getConnection();
  try {
    const results = await connection.query(sql);
    return results.rows;
  } finally {
    await connection.release();
  }
}

// Nested resources — try/finally stacking
async function transferData(src: string, dest: string): Promise<void> {
  const reader = await openReader(src);
  try {
    const writer = await openWriter(dest);
    try {
      await pipeline(reader, writer);
    } finally {
      await writer.close();
    }
  } finally {
    await reader.close();
  }
}
```

## After

```typescript
// Synchronous: using with Symbol.dispose
function readConfig(path: string): Config {
  using handle = openFile(path); // disposed at block exit
  const content = handle.read();
  return JSON.parse(content) as Config;
}

// Async: await using with Symbol.asyncDispose
async function queryDatabase(sql: string): Promise<Row[]> {
  await using connection = await pool.getConnection();
  const results = await connection.query(sql);
  return results.rows;
}

// Nested resources — flat and readable
async function transferData(src: string, dest: string): Promise<void> {
  await using reader = await openReader(src);
  await using writer = await openWriter(dest);
  await pipeline(reader, writer);
  // writer disposed first, then reader (reverse declaration order)
}

// Making a class disposable
class TempFile implements Disposable {
  #path: string;

  constructor(path: string) {
    this.#path = path;
  }

  [Symbol.dispose](): void {
    fs.unlinkSync(this.#path);
  }
}
```

## Conditions

- Resource must implement `[Symbol.dispose]()` for `using` or `[Symbol.asyncDispose]()` for `await using`
- Requires `lib: ["esnext"]` or `lib: ["esnext.disposable"]` for the symbol type definitions
- May require a polyfill for `Symbol.dispose` / `Symbol.asyncDispose` in runtimes without native support
- Disposal happens in reverse declaration order, matching RAII semantics
- Do not apply when the resource lacks a `Disposable` or `AsyncDisposable` interface
