---
since: "TS 5.8"
min-es-target: "any"
module: "any"
---

## Detection

Ternary or conditional returns where one branch has type `any` and the function has an explicit return type annotation

## Before

```typescript
// Prior to TS 5.8, the `any` from one branch contaminated the entire return,
// so TS did not report an error even though the return type is `string`.

function getUserName(user: Record<string, any>): string {
  // user.name is `any`, and `any` flowed through the whole ternary
  return user.name ? user.name : 42;
  //                              ^^ no error before TS 5.8!
}

function getLabel(data: any, fallback: number): string {
  return data.label ?? fallback;
  //                    ^^^^^^^^ `fallback` is `number`, not `string`
  // but `data.label` is `any`, so the whole expression was `any`
}
```

## After

```typescript
// TS 5.8 checks each branch independently against the return type.
// The `any` branch is still allowed, but non-`any` branches must match.

function getUserName(user: Record<string, any>): string {
  // TS 5.8 error: Type 'number' is not assignable to type 'string'.
  // Fix by ensuring all non-any branches return the correct type.
  return user.name ? user.name : "unknown";
  //                              ^^^^^^^^^ now returns string
}

function getLabel(data: any, fallback: string): string {
  return data.label ?? fallback;
  //                    ^^^^^^^^ changed to string to match return type
}
```

## Conditions

- TS 5.8 checks each branch of a conditional/ternary return independently against the declared return type
- Branches that are `any`-typed still pass (since `any` is assignable to everything), but non-`any` branches must be compatible
- This may surface new errors in existing code that previously compiled due to `any` contamination
- Fix by correcting the non-`any` branches to match the return type, or by properly typing the `any` sources
- No runtime behavior changes; this is a stricter type-checking improvement
- Most commonly triggered when accessing properties on `any`-typed objects or using `Record<string, any>`
