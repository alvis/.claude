---
since: "TS 5.7"
min-es-target: "any"
module: "any"
---

## Detection

`let \w+: [^=;]+;` followed by conditional assignment and usage before all paths assign

## Before

```typescript
function processUser(isAdmin: boolean) {
  let role: string;

  if (isAdmin) {
    role = "admin";
  }

  // TS 5.7 error: Variable 'role' is used before being assigned.
  console.log(`User role: ${role}`);
}

function loadConfig(env: string) {
  let dbHost: string;
  let dbPort: number;

  if (env === "production") {
    dbHost = "prod-db.example.com";
    dbPort = 5432;
  } else if (env === "staging") {
    dbHost = "staging-db.example.com";
    dbPort = 5433;
  }
  // no else branch — variables may be uninitialized

  // TS 5.7 error on both: used before assigned
  return { host: dbHost, port: dbPort };
}
```

## After

```typescript
// Option 1: Include `undefined` in the type and handle it
function processUser(isAdmin: boolean) {
  let role: string | undefined;

  if (isAdmin) {
    role = "admin";
  }

  console.log(`User role: ${role ?? "guest"}`);
}

// Option 2: Ensure all code paths assign the variable
function loadConfig(env: string) {
  let dbHost: string;
  let dbPort: number;

  if (env === "production") {
    dbHost = "prod-db.example.com";
    dbPort = 5432;
  } else if (env === "staging") {
    dbHost = "staging-db.example.com";
    dbPort = 5433;
  } else {
    dbHost = "localhost";
    dbPort = 5432;
  }

  return { host: dbHost, port: dbPort };
}
```

## Conditions

- TS 5.7 performs stricter control flow analysis for variables declared with `let` that are used before being assigned in all code paths
- Fix by either adding `| undefined` to the type and handling the `undefined` case, or ensuring every code path assigns the variable
- Variables declared with `const` are not affected since they require an initializer
- This is a type-checking strictness improvement, not a syntax change; no runtime behavior changes
