---
since: "TS 5.5"
min-es-target: "any"
module: "any"
---

## Detection

`/.*[^\\]\[(?!.*\])` or regex patterns with common syntax errors -- unterminated character classes, invalid quantifiers, unescaped special characters

## Before

```typescript
// these regex errors were silently ignored before TS 5.5

// unterminated character class
const pattern1 = /hello[world/;

// nothing to repeat
const pattern2 = /foo{}/;

// invalid escape in unicode mode
const pattern3 = /\p{InvalidProperty}/u;

// unmatched parenthesis
const pattern4 = /((abc)/;

// invalid backreference
const pattern5 = /\1(abc)/;

// these would only fail at runtime -- no compile-time error
```

## After

```typescript
// TS 5.5 checks regex syntax at compile time

// error: Unterminated character class
// const pattern1 = /hello[world/;
const pattern1 = /hello\[world/; // escape the bracket

// error: Incomplete quantifier
// const pattern2 = /foo{}/;
const pattern2 = /foo\{\}/; // escape braces or use valid quantifier

// error: Unknown Unicode property
// const pattern3 = /\p{InvalidProperty}/u;
const pattern3 = /\p{Script=Latin}/u; // valid property

// error: Unterminated group
// const pattern4 = /((abc)/;
const pattern4 = /((abc))/; // close the group

// valid backreference (group defined before reference)
const pattern5 = /(abc)\1/;
```

## Conditions

- Informational -- no manual migration needed; TS 5.5 surfaces errors automatically
- May reveal previously hidden bugs in existing regex literals
- TS validates against the ECMAScript regex grammar including flag-dependent rules (e.g., `u` and `v` flags)
- `new RegExp(...)` with string arguments is NOT checked (patterns are only known at runtime)
- Fix any newly surfaced regex errors by correcting the pattern syntax
