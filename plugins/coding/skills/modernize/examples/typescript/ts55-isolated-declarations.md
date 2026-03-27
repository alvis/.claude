---
since: "TS 5.5"
min-es-target: "any"
module: "any"
---

## Detection

`export (function|const|class)` without explicit return type or type annotation -- exported declarations missing types needed for parallel `.d.ts` emit

## Before

```typescript
// exported functions without explicit return types
export function createUser(name: string, email: string) {
  return {
    id: crypto.randomUUID(),
    name,
    email,
    createdAt: new Date(),
  };
}

export const parseConfig = (raw: string) => {
  const parsed = JSON.parse(raw);
  return { ...parsed, version: parsed.version ?? 1 };
};

export class UserService {
  // return type inferred -- requires whole-program analysis for .d.ts
  getUser(id: string) {
    return this.db.findOne({ id });
  }
}
```

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    // not yet using isolated declarations
  }
}
```

## After

```typescript
// explicit return types enable parallel declaration emit
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

export function createUser(name: string, email: string): User {
  return {
    id: crypto.randomUUID(),
    name,
    email,
    createdAt: new Date(),
  };
}

interface AppConfig {
  version: number;
  [key: string]: unknown;
}

export const parseConfig = (raw: string): AppConfig => {
  const parsed = JSON.parse(raw);
  return { ...parsed, version: parsed.version ?? 1 };
};

export class UserService {
  getUser(id: string): Promise<User | null> {
    return this.db.findOne({ id });
  }
}
```

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "isolatedDeclarations": true
  }
}
```

## Conditions

- Only needed for large projects wanting parallel or third-party declaration emit (e.g., swc, esbuild)
- Requires explicit type annotations on all exported functions, classes, and variables
- Non-exported (internal) declarations do not need explicit annotations
- Tools like `dts-buddy` or `isolatedDeclarations` codefixes can auto-add missing annotations
- Combine with `--declaration` for the full benefit of parallelized `.d.ts` generation
