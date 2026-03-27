---
since: "TS 5.4"
min-es-target: "ES2024"
module: "any"
---

## Detection

`new Map\(\)` followed by `.forEach` or `.reduce` patterns that build a grouped Map

## Before

```typescript
interface Product {
  name: string;
  category: { id: number; label: string };
  price: number;
}

const products: Product[] = getProducts();

// manual Map grouping with object keys
const grouped = new Map<{ id: number; label: string }, Product[]>();
for (const product of products) {
  const existing = [...grouped.entries()].find(
    ([key]) => key.id === product.category.id,
  );
  if (existing) {
    existing[1].push(product);
  } else {
    grouped.set(product.category, [product]);
  }
}
```

## After

```typescript
interface Product {
  name: string;
  category: { id: number; label: string };
  price: number;
}

const products: Product[] = getProducts();

// Map.groupBy preserves object key identity
const grouped = Map.groupBy(products, (product) => product.category);
// type: Map<{ id: number; label: string }, Product[]>

for (const [category, items] of grouped) {
  console.log(`${category.label}: ${items.length} products`);
}
```

## Conditions

- Returns `Map<K, T[]>` -- useful when keys are objects, symbols, or other non-string values
- Object keys are grouped by reference identity (same as `Map` behavior)
- Requires `ES2024` in `lib` compiler option
- Runtime support: Node 21+, Chrome 117+, Firefox 119+, Safari 17.4+
- Prefer `Object.groupBy` when keys are strings or numbers; prefer `Map.groupBy` for complex keys
