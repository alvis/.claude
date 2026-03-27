---
since: "TS 5.5"
min-es-target: "any"
module: "any"
---

## Detection

`const .* = .*\[.*\];?\s*(if|switch)\s*\(typeof` -- extracting indexed access into a temp variable before narrowing

## Before

```typescript
interface Config {
  [key: string]: string | number | boolean | undefined;
}

function processConfig(config: Config, key: string): void {
  // must extract to a temp variable for narrowing to work
  const value = config[key];
  if (typeof value === "string") {
    console.log(value.toUpperCase()); // value is string
  }
}

interface EventMap {
  click: { x: number; y: number } | undefined;
  keypress: { key: string } | undefined;
}

function handleEvent<K extends keyof EventMap>(
  events: EventMap,
  name: K,
): void {
  const event = events[name];
  if (event !== undefined) {
    console.log(event); // event is narrowed
  }
}
```

## After

```typescript
interface Config {
  [key: string]: string | number | boolean | undefined;
}

function processConfig(config: Config, key: string): void {
  // direct indexed access narrowing -- no temp variable needed
  if (typeof config[key] === "string") {
    console.log(config[key].toUpperCase()); // config[key] is string
  }
}

interface EventMap {
  click: { x: number; y: number } | undefined;
  keypress: { key: string } | undefined;
}

function handleEvent<K extends keyof EventMap>(
  events: EventMap,
  name: K,
): void {
  if (events[name] !== undefined) {
    console.log(events[name]); // events[name] is narrowed
  }
}
```

## Conditions

- Only works when the index expression is a constant: `const` variable, literal, or `readonly` property
- `let` variables as keys do not qualify because they could be reassigned between check and access
- The object itself must not be reassigned between the check and the access
- Temp variables are still preferable when the same indexed access is used many times (avoids repeated lookups)
