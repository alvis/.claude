---
since: "TS 5.2"
min-es-target: "ES2022"
module: "any"
---

## Detection

`reflect-metadata` import, `Reflect.getMetadata()`, `Reflect.defineMetadata()`, `Reflect.metadata()`

## Before

```typescript
import "reflect-metadata";

const INJECTABLE_KEY = "custom:injectable";
const INJECT_KEY = "custom:inject";

// Legacy experimental decorator with reflect-metadata
function Injectable(): ClassDecorator {
  return (target) => {
    Reflect.defineMetadata(INJECTABLE_KEY, true, target);
  };
}

function Inject(token: string): ParameterDecorator {
  return (target, _propertyKey, parameterIndex) => {
    const existing: Array<{ index: number; token: string }> =
      Reflect.getOwnMetadata(INJECT_KEY, target) ?? [];
    existing.push({ index: parameterIndex, token });
    Reflect.defineMetadata(INJECT_KEY, existing, target);
  };
}

@Injectable()
class UserService {
  constructor(@Inject("DB") private db: Database) {}
}

// Retrieve metadata
const isInjectable = Reflect.getMetadata(INJECTABLE_KEY, UserService); // true
const deps = Reflect.getMetadata(INJECT_KEY, UserService); // [{index: 0, token: "DB"}]
```

## After

```typescript
// No polyfill import needed — uses native TC39 decorator metadata

const INJECTABLE_KEY = "custom:injectable";
const INJECT_KEY = "custom:inject";

// TC39 decorator using context.metadata
function Injectable<T extends new (...args: any[]) => any>(
  target: T,
  context: ClassDecoratorContext<T>,
): void {
  context.metadata[INJECTABLE_KEY] = true;
}

function Inject(token: string) {
  return function (
    _target: undefined,
    context: ClassFieldDecoratorContext,
  ): void {
    const existing = (context.metadata[INJECT_KEY] as Array<{
      name: string | symbol;
      token: string;
    }>) ?? [];
    existing.push({ name: context.name, token });
    context.metadata[INJECT_KEY] = existing;
  };
}

@Injectable
class UserService {
  @Inject("DB") private db!: Database;
}

// Retrieve metadata via Symbol.metadata
const meta = UserService[Symbol.metadata]!;
const isInjectable = meta[INJECTABLE_KEY]; // true
const deps = meta[INJECT_KEY]; // [{name: "db", token: "DB"}]
```

## Conditions

- Requires TC39 stage 3 decorators, not legacy `experimentalDecorators`
- Remove `experimentalDecorators` and `emitDecoratorMetadata` from tsconfig when migrating
- Library ecosystem (e.g., TypeORM, NestJS) must support TC39 decorators before migrating
- `Symbol.metadata` may require a polyfill in some runtimes
- Decorator signatures differ between legacy and TC39 — this is not a drop-in replacement
