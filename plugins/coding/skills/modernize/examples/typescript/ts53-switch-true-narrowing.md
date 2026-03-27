---
since: "TS 5.3"
min-es-target: "any"
module: "any"
---

## Detection

`if/else if` chains with `typeof`, `instanceof`, or discriminant checks that could use `switch (true)`

## Before

```typescript
function formatValue(value: string | number | boolean | Date): string {
  if (typeof value === "string") {
    return value.toUpperCase();
  } else if (typeof value === "number") {
    return value.toFixed(2);
  } else if (typeof value === "boolean") {
    return value ? "yes" : "no";
  } else if (value instanceof Date) {
    return value.toISOString();
  } else {
    const _exhaustive: never = value;
    throw new Error(`Unhandled: ${_exhaustive}`);
  }
}

// Complex range checks with repeated narrowing
function classify(score: number): string {
  if (score >= 90) {
    return "excellent";
  } else if (score >= 70) {
    return "good";
  } else if (score >= 50) {
    return "fair";
  } else {
    return "poor";
  }
}
```

## After

```typescript
function formatValue(value: string | number | boolean | Date): string {
  switch (true) {
    case typeof value === "string":
      return value.toUpperCase(); // value narrowed to string
    case typeof value === "number":
      return value.toFixed(2); // value narrowed to number
    case typeof value === "boolean":
      return value ? "yes" : "no"; // value narrowed to boolean
    case value instanceof Date:
      return value.toISOString(); // value narrowed to Date
    default: {
      const _exhaustive: never = value;
      throw new Error(`Unhandled: ${_exhaustive}`);
    }
  }
}

// Range checks read cleanly as a switch table
function classify(score: number): string {
  switch (true) {
    case score >= 90:
      return "excellent";
    case score >= 70:
      return "good";
    case score >= 50:
      return "fair";
    default:
      return "poor";
  }
}
```

## Conditions

- TS 5.3 now narrows types inside `switch (true)` case clauses — previously the type was not narrowed
- Not a required migration — this is a stylistic option for readability
- Particularly useful when there are many branches or a mix of `typeof`, `instanceof`, and predicate checks
- Exhaustiveness checking with `never` in the `default` branch works correctly
- Ensure all cases use `break` or `return` to avoid fallthrough unless intentional
