---
since: "TS 5.4"
min-es-target: "any"
module: "any"
---

## Detection

`const narrowed = ` or `as string` inside closures -- extra const variables or type assertions used to work around lost narrowing in closures

## Before

```typescript
function processValue(getValue: () => string | number): void {
  let value: string | number = getValue();
  value = "hello";

  // workaround: copy to const so closure retains narrowing
  const narrowed = value;

  setTimeout(() => {
    // without the const workaround, value is string | number here
    console.log(narrowed.toUpperCase());
  }, 100);
}

function handleResult(result: { status: string; data?: string }): void {
  let data = result.data;
  data = "fallback";

  // workaround: type assertion in closure
  setTimeout(() => {
    console.log((data as string).toUpperCase());
  }, 100);
}
```

## After

```typescript
function processValue(getValue: () => string | number): void {
  let value: string | number = getValue();
  value = "hello";

  // TS 5.4 preserves narrowing after last assignment
  setTimeout(() => {
    // value is narrowed to string here -- no workaround needed
    console.log(value.toUpperCase());
  }, 100);
}

function handleResult(result: { status: string; data?: string }): void {
  let data = result.data;
  data = "fallback";

  // narrowing preserved -- data is string
  setTimeout(() => {
    console.log(data.toUpperCase());
  }, 100);
}
```

## Conditions

- Informational -- TS 5.4 automatically preserves narrowing in closures after the last assignment point
- Remove unnecessary `const` copies or type assertions that were used as narrowing workarounds
- Only applies when the variable is not reassigned after the closure is created
- If the variable is reassigned between the closure definition and execution, narrowing is still lost
