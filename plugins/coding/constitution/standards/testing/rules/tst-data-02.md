# TST-DATA-02: Assert Object/Array Structures as a Whole

## Intent

Use one structural assertion (`toEqual`, `objectContaining`) instead of many per-field assertions.

## Fix

**Before:**
```typescript
expect(result.id).toBe("1");
expect(result.email).toBe("a@b.c");
expect(result.name).toBe("User");
```

**After:**
```typescript
expect(result).toEqual(expect.objectContaining({ id: "u1" }));
```

## Assertion Preferences

- **`.toBe()`** for primitives and reference identity
- **`.toEqual()`** for deep comparisons (objects, arrays)
- **Inline throwing**: `expect(() => fn()).toThrow()`
- **Single assertion per structure**: Don't check fields one by one

## Object and Array Assertions

<IMPORTANT>
When asserting on objects or arrays, use a single assertion that validates the entire structure. Do NOT check individual fields or elements one by one.
</IMPORTANT>

**Object Assertions:**

```typescript
// ✅ CORRECT: single assertion with full object
expect(result).toEqual({
  mime: 'application/octet-stream',
  size: 0,
  lastModified: expect.any(Date),
});

// ✅ CORRECT: partial matching when only some fields matter
expect(result).toEqual(
  expect.objectContaining({
    mime: 'application/octet-stream',
    size: expect.any(Number),
  }),
);
```

**Array Assertions:**

```typescript
// ✅ CORRECT: single assertion with full array
expect(users).toEqual([
  { name: 'Alice', email: 'alice@example.com' },
  { name: 'Bob', email: 'bob@example.com' },
]);

// ✅ CORRECT: array with dynamic values
expect(users).toEqual([
  expect.objectContaining({ name: 'Alice' }),
  expect.objectContaining({ name: 'Bob' }),
]);
```

## Edge Cases

- When existing code matches prior violation patterns such as `expect(result.id).toBe("1")`, refactor before adding new behavior.

## Related

TST-DATA-01, TST-DATA-03, TST-DATA-04
