---
since: "TS 5.0"
min-es-target: "any"
module: "any (requires --module es2015 or later)"
---

## Detection

`"moduleResolution": "node"` in tsconfig.json when the project uses a bundler (webpack, vite, esbuild, rollup)

## Before

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "node",
    // manual workarounds for missing features
    "paths": {
      "#utils/*": ["./src/utils/*"]
    }
  }
}
```

## After

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "bundler"
    // paths workarounds can often be removed —
    // package.json "imports" and "exports" are resolved natively
  }
}
```

## Conditions

- Only for projects that are built with a bundler (webpack, vite, esbuild, rollup, parcel)
- Not suitable for Node.js direct execution or libraries consumed without a bundler; use `"nodenext"` for those
- Requires `--module` to be set to `es2015` or later (not `commonjs`)
- Enables extensionless relative imports, `package.json` `"exports"` and `"imports"` field resolution, and directory index resolution — matching how bundlers actually resolve modules
- The legacy `"moduleResolution": "node"` does not understand `package.json` `"exports"` at all
