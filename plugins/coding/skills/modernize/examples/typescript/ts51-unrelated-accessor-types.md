---
since: "TS 5.1"
min-es-target: "ES2015"
module: "any"
---

## Detection

`get` and `set` accessor pairs forced to share the same type despite accepting different input types

## Before

```typescript
class CSSUnit {
  #value: number;

  get size(): number {
    return this.#value;
  }

  // Before TS 5.1: setter type must match getter type
  set size(value: number) {
    // forced to parse externally before calling setter
    this.#value = value;
  }
}

// caller had to do conversion before setting
const unit = new CSSUnit();
unit.size = Number.parseFloat("42px");
```

## After

```typescript
class CSSUnit {
  #value: number;

  get size(): number {
    return this.#value;
  }

  // TS 5.1+: setter can accept a wider type than the getter returns
  set size(value: string | number | { valueOf(): number }) {
    if (typeof value === "string") {
      this.#value = Number.parseFloat(value);
    } else if (typeof value === "object") {
      this.#value = value.valueOf();
    } else {
      this.#value = value;
    }
  }
}

const unit = new CSSUnit();
unit.size = "42px"; // setter accepts string
const current: number = unit.size; // getter returns number
```

## Conditions

- The getter return type no longer needs to be assignable to the setter parameter type
- Useful for DOM-like APIs, serialization layers, and builder patterns
- Requires ES2015+ target for accessor emit (or `declare` in `.d.ts`)
- Interface and object literal accessors also support unrelated types
