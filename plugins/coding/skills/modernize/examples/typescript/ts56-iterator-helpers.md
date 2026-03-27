---
since: "TS 5.6"
min-es-target: "ES2025"
module: "any"
---

## Detection

`\[\.\.\..*\]\.(map|filter|slice|find)` or `Array\.from\(.*\)\.(map|filter)` -- spreading iterators into arrays just to use array methods

## Before

```typescript
// materializes entire array in memory before processing
function* fibonacci(): Generator<number> {
  let a = 0,
    b = 1;
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}

// spread into array -- infinite generator would hang!
// must manually limit first
function getEvenFibs(count: number): number[] {
  const results: number[] = [];
  for (const n of fibonacci()) {
    if (n % 2 === 0) {
      results.push(n);
    }
    if (results.length >= count) break;
  }
  return results;
}

// processing a large file line by line
function processLines(lines: Iterable<string>): string[] {
  return [...lines]
    .filter((line) => line.trim().length > 0)
    .map((line) => line.toUpperCase())
    .slice(0, 100);
}
```

## After

```typescript
function* fibonacci(): Generator<number> {
  let a = 0,
    b = 1;
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}

// lazy evaluation -- never materializes the full sequence
function getEvenFibs(count: number): number[] {
  return Iterator.from(fibonacci())
    .filter((n) => n % 2 === 0)
    .take(count)
    .toArray();
}

// lazy pipeline -- processes only what is needed
function processLines(lines: Iterable<string>): string[] {
  return Iterator.from(lines)
    .filter((line) => line.trim().length > 0)
    .map((line) => line.toUpperCase())
    .take(100)
    .toArray();
}

// additional helpers
Iterator.from(entries)
  .drop(5) // skip first 5
  .forEach((entry) => console.log(entry)); // terminal operation
```

## Conditions

- Requires `ES2025` or `ESNext` in `lib` compiler option
- Runtime support: Node 22+, Chrome 122+, Firefox 131+
- Lazy evaluation -- elements are processed one at a time through the pipeline
- Ideal for large or infinite sequences where materializing an array is wasteful or impossible
- `Iterator.from()` wraps any iterable or iterator into a helper-enabled iterator
- Available methods: `.map()`, `.filter()`, `.take()`, `.drop()`, `.flatMap()`, `.reduce()`, `.forEach()`, `.some()`, `.every()`, `.find()`, `.toArray()`
