---
since: "TS 5.4"
min-es-target: "any"
module: "any"
---

## Detection

`function.*<.*extends.*>.*\(.*:.*\1.*,.*:.*\1` -- generic functions where multiple parameters reference the same type parameter, and one parameter should not influence inference

## Before

```typescript
function createFSM<S extends string>(
  init: S,
  transitions: Record<S, S[]>,
): { state: S; next: (event: S) => void } {
  let state = init;
  return {
    state,
    next: (event) => {
      const allowed = transitions[state];
      if (allowed.includes(event)) {
        state = event;
      }
    },
  };
}

// transitions parameter widens S to include "invalid"
const fsm = createFSM("idle", {
  idle: ["running"],
  running: ["idle", "stopped"],
  stopped: ["idle"],
  invalid: ["idle"], // no error -- "invalid" widens S
});
```

## After

```typescript
function createFSM<S extends string>(
  init: S,
  transitions: Record<NoInfer<S>, NoInfer<S>[]>,
): { state: S; next: (event: S) => void } {
  let state = init;
  return {
    state,
    next: (event) => {
      const allowed = transitions[state];
      if (allowed.includes(event)) {
        state = event;
      }
    },
  };
}

// S is inferred only from init, transitions cannot widen it
const fsm = createFSM("idle", {
  idle: ["running"],
  running: ["idle", "stopped"],
  stopped: ["idle"],
  invalid: ["idle"], // error: "invalid" is not assignable to "idle" | "running" | "stopped"
});
```

## Conditions

- Use when a generic parameter should be inferred from only some of the function arguments
- Replaces workarounds using overloads or extra generic parameters to prevent unwanted inference
- `NoInfer<T>` is a built-in utility type -- no import required
