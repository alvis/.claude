---
since: "TS 5.8"
min-es-target: "any"
module: "any"
---

## Detection

`@typescript/lib-` packages in `package.json` dependencies

## Before

```jsonc
// package.json — custom lib replacement packages installed
{
  "dependencies": {
    "@anthropic-ai/sdk": "^0.20.0"
  },
  "devDependencies": {
    "typescript": "~5.7.0",
    "@typescript/lib-dom": "npm:@AnotherScope/lib-dom@^1.0.0"
  }
}
```

```jsonc
// tsconfig.json — no way to know if replacements are active
{
  "compilerOptions": {
    "lib": ["ES2022", "DOM"]
  }
}
```

```typescript
// Custom lib packages might silently fail to load, and you'd get
// the default built-in lib definitions without any warning
```

## After

```jsonc
// package.json
{
  "dependencies": {
    "@anthropic-ai/sdk": "^0.20.0"
  },
  "devDependencies": {
    "typescript": "~5.8.0",
    "@typescript/lib-dom": "npm:@AnotherScope/lib-dom@^1.0.0"
  }
}
```

```jsonc
// tsconfig.json — explicit control over lib replacement behavior
{
  "compilerOptions": {
    "lib": ["ES2022", "DOM"],
    "libReplacement": true
  }
}
```

```typescript
// TS 5.8 now actively looks for @typescript/lib-* packages when
// libReplacement is true (default when such packages are detected).
// Set to false to explicitly opt out of lib replacement.
```

## Conditions

- `libReplacement` defaults to `true` when `@typescript/lib-*` packages are detected in `node_modules`, and `false` otherwise
- Set `"libReplacement": false` to explicitly disable lib replacement even if packages are present
- Set `"libReplacement": true` to force TS to look for replacement packages (useful for debugging if they are not being picked up)
- Only relevant for projects that use custom lib replacement packages (e.g., stricter DOM types, custom built-in type definitions)
- Most projects do not use lib replacement and can ignore this flag entirely
