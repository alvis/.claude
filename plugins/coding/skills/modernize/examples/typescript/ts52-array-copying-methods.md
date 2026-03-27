---
since: "TS 5.2"
min-es-target: "ES2023"
module: "any"
---

## Detection

`[...arr].sort(`, `[...arr].reverse()`, `arr.slice().sort(`, manual splice-and-copy patterns

## Before

```typescript
const scores = [85, 92, 78, 95, 88];

// Spread-copy then sort
const ranked = [...scores].sort((a, b) => b - a);

// Spread-copy then reverse
const reversed = [...scores].reverse();

// Manual copy-then-splice to replace an element
const updated = [...scores];
updated.splice(2, 1, 100);

// Manual copy to replace at index
const replaced = [...scores];
replaced[2] = 100;

// Chaining requires intermediate copies
const topThree = [...scores]
  .sort((a, b) => b - a)
  .slice(0, 3);
```

## After

```typescript
const scores = [85, 92, 78, 95, 88];

// toSorted — returns a new sorted array
const ranked = scores.toSorted((a, b) => b - a);

// toReversed — returns a new reversed array
const reversed = scores.toReversed();

// toSpliced — returns a new array with splice applied
const updated = scores.toSpliced(2, 1, 100);

// with — returns a new array with element replaced at index
const replaced = scores.with(2, 100);

// Chainable without intermediate copies
const topThree = scores
  .toSorted((a, b) => b - a)
  .slice(0, 3);

// Original array is never mutated
console.log(scores); // [85, 92, 78, 95, 88]
```

## Conditions

- Requires `target: "ES2023"` or `lib: ["ES2023"]` in tsconfig
- Available in Node.js 20+, Chrome 110+, Firefox 115+, Safari 16+
- `toSorted`, `toReversed`, `toSpliced` mirror their mutating counterparts (`sort`, `reverse`, `splice`)
- `with(index, value)` is the non-mutating equivalent of bracket assignment
- These methods also work on `TypedArray` (except `toSpliced` and `with` for typed arrays uses `with` only)
