---
since: "TS 5.0"
min-es-target: "ES2022"
module: "any"
---

## Detection

`"experimentalDecorators": true` in tsconfig.json

## Before

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

```typescript
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

function log(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor,
) {
  const original = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    return original.apply(this, args);
  };
}

@sealed
class UserService {
  @log
  findUser(id: string) {
    return { id, name: "Alice" };
  }
}
```

## After

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    // no experimentalDecorators flag needed
  }
}
```

```typescript
type ClassDecorator = (
  target: new (...args: any[]) => any,
  context: ClassDecoratorContext,
) => void;

const sealed: ClassDecorator = (target, _context) => {
  Object.seal(target);
  Object.seal(target.prototype);
};

function log<This, Args extends any[], Return>(
  target: (this: This, ...args: Args) => Return,
  context: ClassMethodDecoratorContext<
    This,
    (this: This, ...args: Args) => Return
  >,
) {
  return function (this: This, ...args: Args): Return {
    console.log(`Calling ${String(context.name)} with`, args);
    return target.apply(this, args);
  };
}

@sealed
class UserService {
  @log
  findUser(id: string) {
    return { id, name: "Alice" };
  }
}
```

## Conditions

- All decorator libraries used in the project must support TC39 stage 3 decorators (check NestJS, TypeORM, MobX, etc. for compatibility)
- Cannot mix experimental and TC39 decorators in the same project
- `emitDecoratorMetadata` is not supported with TC39 decorators; projects relying on `reflect-metadata` (e.g., NestJS, TypeORM) may need to wait for library support
- TC39 decorator signature differs from the experimental one: method decorators receive `(target, context)` instead of `(target, propertyKey, descriptor)`
