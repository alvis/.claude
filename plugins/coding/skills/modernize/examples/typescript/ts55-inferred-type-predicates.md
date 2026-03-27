---
since: "TS 5.5"
min-es-target: "any"
module: "any"
---

## Detection

`): .* is ` -- explicit type predicate annotations on simple guard functions

## Before

```typescript
// explicit type predicate on a simple guard
function isNonNullable<T>(value: T): value is NonNullable<T> {
  return value != null;
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

function hasId(obj: object): obj is { id: string } {
  return "id" in obj;
}

// explicit predicate in filter callbacks
const names: (string | null | undefined)[] = getNames();
const validNames = names.filter(
  (name): name is string => name != null,
);

const mixed: (string | number)[] = getValues();
const strings = mixed.filter(
  (value): value is string => typeof value === "string",
);
```

## After

```typescript
// TS 5.5 infers the type predicate automatically
function isNonNullable<T>(value: T) {
  return value != null;
}

function isString(value: unknown) {
  return typeof value === "string";
}

function hasId(obj: object) {
  return "id" in obj;
}

// inferred predicates work in filter callbacks too
const names: (string | null | undefined)[] = getNames();
const validNames = names.filter((name) => name != null);
// type: string[]

const mixed: (string | number)[] = getValues();
const strings = mixed.filter((value) => typeof value === "string");
// type: string[]
```

## Conditions

- Only remove explicit predicates when TS 5.5 can infer the same predicate
- Complex guards with multiple conditions or side effects may still need explicit annotations
- TS infers predicates for functions with a single return statement that narrows the parameter
- Boolean returning methods with `this` narrowing are also inferred (e.g., class type guards)
- If unsure, remove the annotation and verify that downstream code still compiles
