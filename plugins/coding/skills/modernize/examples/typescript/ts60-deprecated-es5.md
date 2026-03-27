---
since: "TS 6.0"
min-es-target: "ES2015"
module: "any"
---

## Detection

`"target": "es5"` in tsconfig.json
`"target": "ES5"` in tsconfig.json
`"target": "es3"` in tsconfig.json

## Before

```jsonc
// tsconfig.json — targeting ES5 for legacy browser support
{
  "compilerOptions": {
    "target": "ES5",
    "lib": ["dom", "ES5"],
    "downlevelIteration": true,
    "outDir": "./dist"
  }
}
```

```typescript
// tsc downlevels to ES5 — generates verbose helper code
class Animal {
  constructor(public name: string) {}
  speak() {
    return `${this.name} makes a noise.`;
  }
}

// Emitted ES5 includes __extends, __spreadArray, template literal polyfills
// Output is significantly larger than ES2015+ equivalent
```

## After

```jsonc
// tsconfig.json — ES2015 is the minimum target in TS 6.0
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "ES2020"],
    "outDir": "./dist"
  }
}
```

```typescript
// Same source — emitted as-is with native class syntax
class Animal {
  constructor(public name: string) {}
  speak() {
    return `${this.name} makes a noise.`;
  }
}

// No helper code needed — output is smaller and faster
```

```jsonc
// If legacy browser support is still required, use a bundler + Babel
// tsconfig.json — TypeScript targets modern JS
{
  "compilerOptions": {
    "target": "ES2020",
    "outDir": "./dist"
  }
}

// babel.config.json — Babel handles legacy downleveling
// {
//   "presets": [
//     ["@babel/preset-env", { "targets": "> 0.25%, not dead" }]
//   ]
// }
```

## Conditions

- ES5 and ES3 targets are removed in TS 6.0 — the compiler will error
- Minimum supported target is now ES2015
- `downlevelIteration` is no longer needed when targeting ES2015+
- If legacy browser support (IE11) is still required, use TypeScript with `target: "ES2020"` and a separate Babel/SWC step for downleveling
- Consider targeting ES2020 or higher — all modern browsers and Node 14+ support it
- Smaller output, better debugging experience, faster execution
