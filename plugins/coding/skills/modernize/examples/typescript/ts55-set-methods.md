---
since: "TS 5.5"
min-es-target: "ES2025"
module: "any"
---

## Detection

`new Set\(\[\.\.\.` or `.filter(.*\.has\(` or manual set operation loops -- spread-and-filter patterns for set operations

## Before

```typescript
const admins = new Set(["alice", "bob", "charlie"]);
const online = new Set(["bob", "dave", "eve"]);

// intersection
const onlineAdmins = new Set([...admins].filter((x) => online.has(x)));

// union
const allUsers = new Set([...admins, ...online]);

// difference
const offlineAdmins = new Set([...admins].filter((x) => !online.has(x)));

// symmetric difference
const exclusive = new Set(
  [...admins, ...online].filter(
    (x) => !admins.has(x) || !online.has(x),
  ),
);

// subset check
const isSubset = [...admins].every((x) => online.has(x));

// disjoint check
const isDisjoint = ![...admins].some((x) => online.has(x));
```

## After

```typescript
const admins = new Set(["alice", "bob", "charlie"]);
const online = new Set(["bob", "dave", "eve"]);

// intersection -- elements in both sets
const onlineAdmins = admins.intersection(online);
// Set {"bob"}

// union -- elements in either set
const allUsers = admins.union(online);
// Set {"alice", "bob", "charlie", "dave", "eve"}

// difference -- elements in admins but not online
const offlineAdmins = admins.difference(online);
// Set {"alice", "charlie"}

// symmetric difference -- elements in one but not both
const exclusive = admins.symmetricDifference(online);
// Set {"alice", "charlie", "dave", "eve"}

// subset check
const isSubset = admins.isSubsetOf(online); // false

// superset check
const isSuperset = online.isSupersetOf(admins); // false

// disjoint check
const isDisjoint = admins.isDisjointFrom(online); // false
```

## Conditions

- Requires `ES2025` or `ESNext` in `lib` compiler option
- Runtime support: Node 22+, Chrome 122+, Firefox 127+, Safari 17+
- Methods accept any `Set`-like iterable with a `has()` method and `size` property
- Returns a new `Set` -- does not mutate the original
- Significantly more readable and performant than spread-and-filter patterns for large sets
