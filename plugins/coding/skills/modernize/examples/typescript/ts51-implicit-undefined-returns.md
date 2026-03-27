---
since: "TS 5.1"
min-es-target: "any"
module: "any"
---

## Detection

`return undefined;` in functions with explicit `: undefined` return type

## Before

```typescript
function processAndDiscard(items: string[]): undefined {
  items.forEach((item) => console.log(item));
  return undefined;
}

class EventBus {
  emit(event: string): undefined {
    this.listeners.get(event)?.forEach((fn) => fn());
    return undefined;
  }
}
```

## After

```typescript
function processAndDiscard(items: string[]): undefined {
  items.forEach((item) => console.log(item));
}

class EventBus {
  emit(event: string): undefined {
    this.listeners.get(event)?.forEach((fn) => fn());
  }
}
```

## Conditions

- Safe refactor with no runtime behavior change
- Only applies when the return type is explicitly annotated as `undefined`, not `void`
- Functions returning `void` already permitted implicit returns before TS 5.1
- Useful for callback signatures where the return type is explicitly `undefined` rather than `void`
