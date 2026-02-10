# TST-CORE-04: Each Test Must Add Unique Value

## Intent

A test is valid only if it adds a new behavior path, branch, or meaningful edge case.

## Fix

```typescript
it("should return empty list", () => {});
```

## Edge Cases

- When existing code matches prior violation patterns such as ❌ `it("same case #2", fn)`, refactor before adding new behavior.

## Related

TST-CORE-01, TST-CORE-02, TST-CORE-03
