---
since: "TS 5.3"
min-es-target: "ES2015"
module: "any"
---

## Detection

Type assertions after `instanceof` checks on classes with `static [Symbol.hasInstance]`

## Before

```typescript
class PositiveNumber {
  static [Symbol.hasInstance](value: unknown): value is PositiveNumber {
    return typeof value === "number" && value > 0;
  }

  constructor(public readonly value: number) {
    if (value <= 0) throw new RangeError("Must be positive");
  }
}

function process(input: unknown): string {
  if (input instanceof PositiveNumber) {
    // Before TS 5.3: 'input' was not narrowed despite Symbol.hasInstance
    const num = input as PositiveNumber; // manual assertion required
    return `Positive: ${num.value}`;
  }
  return "not positive";
}

// Also affected custom type guards via instanceof
class SafeString {
  static [Symbol.hasInstance](value: unknown): value is string {
    return typeof value === "string" && value.length < 1000;
  }
}

function handle(data: unknown): number {
  if (data instanceof SafeString) {
    // Before TS 5.3: data not narrowed to string
    return (data as string).length;
  }
  return 0;
}
```

## After

```typescript
class PositiveNumber {
  static [Symbol.hasInstance](value: unknown): value is PositiveNumber {
    return typeof value === "number" && value > 0;
  }

  constructor(public readonly value: number) {
    if (value <= 0) throw new RangeError("Must be positive");
  }
}

function process(input: unknown): string {
  if (input instanceof PositiveNumber) {
    // TS 5.3+: 'input' narrowed to PositiveNumber via Symbol.hasInstance
    return `Positive: ${input.value}`;
  }
  return "not positive";
}

class SafeString {
  static [Symbol.hasInstance](value: unknown): value is string {
    return typeof value === "string" && value.length < 1000;
  }
}

function handle(data: unknown): number {
  if (data instanceof SafeString) {
    // TS 5.3+: data narrowed to string via Symbol.hasInstance return type
    return data.length;
  }
  return 0;
}
```

## Conditions

- Informational improvement in TS 5.3 — no syntax change required
- After upgrading to TS 5.3, audit `instanceof` checks on classes with `static [Symbol.hasInstance]` and remove unnecessary type assertions
- The `Symbol.hasInstance` method must have a type predicate return type (`value is T`) for narrowing to apply
- Requires ES2015+ for `Symbol.hasInstance` support
