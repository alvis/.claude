# TST-CORE-09: Assert Log Output via `mock.calls`

## Intent

When a unit's observable behavior includes writing to a logger, the test MUST capture the logger as a typed `vi.fn<LogFn>()` (or `{ info: vi.fn<Logger['info']>(), ... } satisfies Partial<Logger>`) and assert the **full call sequence** via `expect(log.mock.calls).toEqual([...])`. This replaces scattered `toHaveBeenCalledWith(...)` assertions and makes log output a structural contract.

Applies when:

- The logger is the primary observable effect (CLI tools, background workers, audit paths).
- The test covers a "complicated" flow — multi-step, async, or with branch-specific messages.
- The log sequence encodes ordering guarantees (e.g., "connected" before "ready").

## Banned Patterns

```typescript
// ❌ Asserting logs field-by-field (violates TST-DATA-02 too)
expect(log).toHaveBeenCalledWith('connected');
expect(log).toHaveBeenCalledWith('ready');
expect(log).toHaveBeenCalledTimes(2);

// ❌ Only asserting count — ignores content
expect(log).toHaveBeenCalledTimes(2);

// ❌ Untyped mock drops compile-time signature check
const log = vi.fn();
```

## Correct Patterns

```typescript
import type { Log } from '#logger';

const log = vi.fn<Log>();

it('should log connect then ready in order', async () => {
  await start({ log });

  expect(log.mock.calls).toEqual([
    ['connected', { host: 'localhost' }],
    ['ready'],
  ]);
});
```

For structured loggers:

```typescript
import type { Logger } from '#logger';

const logger = {
  info: vi.fn<Logger['info']>(),
  error: vi.fn<Logger['error']>(),
} satisfies Partial<Logger>;

it('should emit info then error on partial failure', async () => {
  await process({ logger });

  expect(logger.info.mock.calls).toEqual([['started', { batch: 1 }]]);
  expect(logger.error.mock.calls).toEqual([
    ['item failed', { id: 'x', reason: 'timeout' }],
  ]);
});
```

## Edge Cases

- Logs that are incidental (debug traces not specified by the contract) need not be asserted — do not lock in noise.
- If order is irrelevant, use `expect(log.mock.calls).toEqual(expect.arrayContaining([...]))`.
- Level-specific assertions: assert each method's `.mock.calls` separately rather than merging.
- **Log type source**: prefer the SUT's exported `Log` / `Logger` type. A local `type Log = (msg: string, meta?: object) => void` alias is acceptable **only** when the SUT does not export one; do not define a local alias to bypass importing the real type.

## Related

TST-CORE-06, TST-DATA-02, TST-MOCK-05, TST-MOCK-16
