# TST-CORE-06: No Wrapper-Only Tests

## Intent

Do not test only that dependencies were called. Assert behavior and outcome.

## Fix

```typescript
expect(result).toEqual({ ok: true });
```

## Edge Cases

- When existing code matches prior violation patterns such as ❌ `expect(dep).toHaveBeenCalled()`, refactor before adding new behavior.

## Related

TST-CORE-01, TST-CORE-02, TST-CORE-03
