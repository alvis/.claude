---
since: "TS 5.3"
min-es-target: "any"
module: "any"
---

## Detection

Type assertions or extra type guards after `=== true` or `=== false` comparisons

## Before

```typescript
type Status = true | false | null | undefined;

function handleStatus(status: Status): string {
  if (status === true) {
    // Before TS 5.3: status still typed as Status, not narrowed to 'true'
    const confirmed: true = status as true; // manual assertion needed
    return "confirmed";
  }
  if (status === false) {
    const denied: false = status as false; // manual assertion needed
    return "denied";
  }
  return "unknown";
}

// Discriminated union with boolean discriminant
type Result =
  | { ok: true; data: string }
  | { ok: false; error: Error };

function process(result: Result): string {
  if (result.ok === true) {
    // Before TS 5.3: result not narrowed via boolean comparison
    return (result as { ok: true; data: string }).data;
  }
  return (result as { ok: false; error: Error }).error.message;
}
```

## After

```typescript
type Status = true | false | null | undefined;

function handleStatus(status: Status): string {
  if (status === true) {
    // TS 5.3+: status narrowed to 'true'
    const confirmed: true = status;
    return "confirmed";
  }
  if (status === false) {
    // TS 5.3+: status narrowed to 'false'
    const denied: false = status;
    return "denied";
  }
  // status narrowed to null | undefined
  return "unknown";
}

// Discriminated union narrowing via boolean comparison
type Result =
  | { ok: true; data: string }
  | { ok: false; error: Error };

function process(result: Result): string {
  if (result.ok === true) {
    // TS 5.3+: result narrowed to { ok: true; data: string }
    return result.data;
  }
  // result narrowed to { ok: false; error: Error }
  return result.error.message;
}
```

## Conditions

- TS 5.3 now narrows on direct `=== true` and `=== false` comparisons
- Useful when discriminating between literal `true`, `false`, and other falsy values (`null`, `undefined`, `0`, `""`)
- Truthy checks (`if (x)`) do not distinguish `true` from other truthy values — use `=== true` when precision matters
- After upgrading, remove manual type assertions that followed boolean equality checks
- Particularly valuable for discriminated unions with a boolean discriminant field
