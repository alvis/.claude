---
since: "TS 5.4"
min-es-target: "ES2024"
module: "any"
---

## Detection

`\.reduce\(.*acc\[` or `lodash.*groupBy` or `_.groupBy` -- manual reduce-based grouping or lodash groupBy calls

## Before

```typescript
interface Order {
  id: string;
  status: "pending" | "shipped" | "delivered";
  total: number;
}

const orders: Order[] = getOrders();

// manual reduce grouping
const grouped = orders.reduce<Record<string, Order[]>>((acc, order) => {
  const key = order.status;
  if (!acc[key]) {
    acc[key] = [];
  }
  acc[key].push(order);
  return acc;
}, {});

// or lodash
import { groupBy } from "lodash";
const grouped = groupBy(orders, (o) => o.status);
```

## After

```typescript
interface Order {
  id: string;
  status: "pending" | "shipped" | "delivered";
  total: number;
}

const orders: Order[] = getOrders();

const grouped = Object.groupBy(orders, (order) => order.status);
// type: Partial<Record<"pending" | "shipped" | "delivered", Order[]>>

// access requires optional chaining because keys are Partial
const pendingOrders = grouped["pending"] ?? [];
```

## Conditions

- Returns `Partial<Record<K, T[]>>` -- keys may be absent, so access requires nullish handling
- Requires `ES2024` in `lib` compiler option
- Runtime support: Node 21+, Chrome 117+, Firefox 119+, Safari 17.4+
- Removes lodash `groupBy` dependency when applicable
