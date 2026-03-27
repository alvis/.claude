---
since: "TS 5.8"
min-es-target: "any"
module: "any"
---

## Detection

Computed property names (`[expr]`) in classes or object types where the expression is a `const` variable or `as const` literal

## Before

```typescript
// Prior to TS 5.8, computed property names were erased or inlined in .d.ts files

const NAME = "name" as const;
const AGE = "age" as const;

export class Person {
  [NAME] = "Alice";
  [AGE] = 30;
}

// Generated .d.ts (before TS 5.8) — lost the computed reference:
// export declare class Person {
//     name: string;    // inlined, loses connection to NAME
//     age: number;     // inlined, loses connection to AGE
// }
```

```typescript
const EventType = {
  Click: "click",
  Hover: "hover",
} as const;

export interface EventHandlers {
  [EventType.Click]: () => void;
  [EventType.Hover]: () => void;
}

// Generated .d.ts (before TS 5.8) — computed names erased or caused errors
```

## After

```typescript
// TS 5.8 preserves computed property names in declaration files

const NAME = "name" as const;
const AGE = "age" as const;

export class Person {
  [NAME] = "Alice";
  [AGE] = 30;
}

// Generated .d.ts (TS 5.8) — preserves computed property names:
// declare const NAME = "name";
// declare const AGE = "age";
// export declare class Person {
//     [NAME]: string;
//     [AGE]: number;
// }
```

```typescript
const EventType = {
  Click: "click",
  Hover: "hover",
} as const;

export interface EventHandlers {
  [EventType.Click]: () => void;
  [EventType.Hover]: () => void;
}

// Generated .d.ts (TS 5.8) — computed names preserved correctly
```

## Conditions

- No code changes needed; this is a declaration emit improvement in TS 5.8
- Improves accuracy of `.d.ts` files for libraries that use computed property names
- Particularly beneficial for library authors whose consumers depend on precise declaration files
- Only applies when the computed expression is a `const` variable, `as const` literal, or a dotted access on a `const` object
- Dynamic or non-const computed properties are still erased (since their value cannot be statically determined)
