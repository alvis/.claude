---
since: "TS 5.0"
min-es-target: "any"
module: "any"
---

## Detection

Enum members with computed initializers that were previously typed as `number` or `string` rather than literal types

## Before

```typescript
// before TS 5.0, computed enum members lost literal types
enum Permission {
  Read = 1 << 0,  // typed as `number`, not a literal
  Write = 1 << 1, // typed as `number`, not a literal
  Execute = 1 << 2,
}

// narrowing did not work on computed enum members
function check(p: Permission) {
  if (p === Permission.Read) {
    // p was still typed as Permission, not Permission.Read
  }
}
```

## After

```typescript
// TS 5.0+: all enums are union enums — every member gets a unique type
enum Permission {
  Read = 1 << 0,  // typed as Permission.Read
  Write = 1 << 1, // typed as Permission.Write
  Execute = 1 << 2,
}

// narrowing works on all enum members
function check(p: Permission) {
  if (p === Permission.Read) {
    p; // narrowed to Permission.Read
  }
}

// discriminated unions with enums work reliably
type Event =
  | { kind: Permission.Read; data: string }
  | { kind: Permission.Write; data: Buffer };
```

## Conditions

- This is an automatic compiler behavior change; no code modifications are required
- Be aware of potential breaking changes if code relied on enum members being widened to `number` (e.g., assigning arbitrary numbers to enum-typed variables)
- Exhaustiveness checks with `switch` statements now work correctly for all enums
