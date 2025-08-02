# Pure Functions and Immutability Standards

_Additional standards for functional programming patterns beyond basic pure function principles_

## Core Principles

See `functions.md` for basic pure function principles. This document covers additional immutability patterns.

## Immutability Patterns

### Default to Immutable

- **Use `const` by default**
- **Favor immutable operations** - spread operators, map, filter, reduce
- **Avoid mutation** unless there's a clear performance benefit

```typescript
// ✅ Good: Immutable operations
const updated = { ...original, age: 31 };
const doubled = items.map(x => x * 2);
const withExtra = [...items, newItem];

// ❌ Bad: Mutations
user.age = 31;
numbers.push(4);
items.sort(); // Use [...items].sort() instead
```

## Function Parameter Rules

### Never Mutate Parameters

```typescript
// ❌ Bad: Mutating parameters
function processUser(user: User): User {
  user.status = 'processed'; // Never mutate inputs!
  return user;
}

// ✅ Good: Return new object
function processUser(user: User): User {
  return { ...user, status: 'processed' };
}
```

## When Mutation is Acceptable

### Local Mutation for Performance

Mutation is acceptable when the variable is **scoped within a function**:

```typescript
// ✅ Acceptable: Local mutation for performance
function processLargeDataset(data: readonly number[]): number[] {
  const result: number[] = [];
  for (const item of data) {
    if (item > 0) result.push(item * 2); // Local mutation OK
  }
  return result;
}
```

## Side Effect Management

### Segregate Side Effects

Keep pure business logic separate from side effects:

```typescript
// Pure business logic
function calculateTotal(order: Order): number {
  return order.items.reduce((sum, item) => sum + item.price, 0);
}

// Side effects in outer layer
async function processOrder(order: Order): Promise<void> {
  const total = calculateTotal(order);    // Pure
  await saveOrder(order.id, total);       // Side effect
}
```

## Text Joining Pattern

For multi-line text generation, use array join:

```typescript
// ✅ Good: Array join pattern
const lines = [
  'Header',
  `Name: ${user.name}`,
  `Email: ${user.email}`,
];
return lines.join('\n');

// ❌ Bad: String concatenation
let text = 'Header\n';
text += `Name: ${user.name}\n`;
```


## Key Principles

1. **Never mutate function parameters**
2. **Use `const` by default**
3. **Keep side effects at application edges**
4. **Allow local mutation for performance**
5. **Use array join for multi-line text**