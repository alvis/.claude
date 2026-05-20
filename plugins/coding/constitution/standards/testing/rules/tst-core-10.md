# TST-CORE-10: No Tests Over Constant Data

## Intent

A test must exercise behavior. Asserting the literal contents of a frozen constant export (`Set`/`Map`/`Record`/array/scalar/`RegExp`) adds no coverage — it only fires when the constant and the test are edited in opposite directions, which is a change-detector, not a behavior check. Express compile-time shape via TypeScript types (`satisfies`, `as const`) in the source, not runtime assertions in tests.

## Fix

First determine whether the constant has any consumer:

- **Has a consumer** → delete the test; test the consumer function instead
  (example below).
- **No consumer** → the constant itself is dead code. Delete the constant,
  not only the test (see `GEN-DESN-04`).

If shape correctness matters at compile time, encode it next to the constant:

```typescript
const _check = SUPPORTED_MIME_TYPES satisfies ReadonlySet<MimeType>;
```

If callers depend on the constant, test the *consumer* function that uses it instead:

```typescript
describe("fn:validateUpload", () => {
  it("should reject files whose mime type is unsupported", () => {
    expect(() => validateUpload({ mime: "application/x-msdownload" })).toThrow();
  });
});
```

## Edge Cases

- A snapshot of a *generated* constant (e.g. exported from a `.gen.ts` file produced by a build step) is allowed only when the test exercises the **generator function**, not the static export.
- Type-level checks (`satisfies`, `as const`) belong in source files, never in `*.spec.ts`.
- A barrel re-export identity assertion (`expect(barrel.UserService).toBe(UserService)`)
  is the same change-detector pathology — it tests the module system, not
  behavior. Barrel files are ignore-marked (`TST-COVR-01`); never write
  re-export tests.

## Related

TST-CORE-04, TST-CORE-05, TST-CORE-07, TST-COVR-04, GEN-DESN-04
