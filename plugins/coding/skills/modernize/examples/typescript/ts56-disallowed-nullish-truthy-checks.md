---
since: "TS 5.6"
min-es-target: "any"
module: "any"
---

## Detection

`if\s*\(\s*(new |Promise\.|\/|function)` -- conditionals that check always-truthy values like Promises, regex literals, functions, or object constructors

## Before

```typescript
// bug: Promise is always truthy, likely missing await
async function loadUser(id: string) {
  const user = fetch(`/api/users/${id}`).then((r) => r.json());
  if (user) {
    // always true -- user is a Promise, not the resolved value
    return user;
  }
  return null;
}

// bug: regex literal is always truthy
function validateEmail(email: string) {
  if (/^[^@]+@[^@]+$/) {
    // always true -- should be regex.test(email)
    return true;
  }
  return false;
}

// bug: function reference is always truthy
function processItems(items: string[], transform?: (s: string) => string) {
  if (transform) {
    // correct -- this is a valid check
  }
  if (Array.isArray) {
    // always true -- should be Array.isArray(items)
  }
}
```

## After

```typescript
// fix: await the Promise
async function loadUser(id: string) {
  const user = await fetch(`/api/users/${id}`).then((r) => r.json());
  if (user) {
    return user;
  }
  return null;
}

// fix: actually test the regex
function validateEmail(email: string) {
  if (/^[^@]+@[^@]+$/.test(email)) {
    return true;
  }
  return false;
}

// fix: call the function
function processItems(items: string[], transform?: (s: string) => string) {
  if (transform) {
    // correct -- transform could be undefined
  }
  if (Array.isArray(items)) {
    // correct -- now actually checking the value
  }
}
```

## Conditions

- Informational -- TS 5.6 now reports errors on checks that are always truthy or always nullish
- Common patterns caught: uncalled functions, un-awaited Promises, regex literals, object constructors
- Fix the underlying logic bug rather than suppressing the error
- Legitimate cases can use `Boolean(value)` or `!!value` to signal intentional truthiness checks
- Also catches always-nullish checks: `if (void someCall()) { ... }`
