---
since: "TS 5.5"
min-es-target: "any"
module: "any"
---

## Detection

`"extends":` in tsconfig files combined with relative `outDir`, `rootDir`, `baseUrl`, or `paths` that break in nested projects

## Before

```jsonc
// packages/tsconfig.base.json (shared config)
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "nodenext",
    "strict": true,
    "outDir": "../dist",
    "rootDir": "./src",
    "declarationDir": "../types",
    "baseUrl": ".",
    "paths": {
      "@shared/*": ["../shared/src/*"]
    }
  }
}
```

```jsonc
// packages/app/tsconfig.json
{
  // "../dist" resolves relative to packages/app/, not packages/
  // this breaks -- outDir becomes packages/dist instead of packages/app/dist
  "extends": "../tsconfig.base.json"
}
```

## After

```jsonc
// packages/tsconfig.base.json (shared config)
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "nodenext",
    "strict": true,
    "outDir": "${configDir}/dist",
    "rootDir": "${configDir}/src",
    "declarationDir": "${configDir}/types",
    "baseUrl": "${configDir}",
    "paths": {
      "@shared/*": ["${configDir}/../shared/src/*"]
    }
  }
}
```

```jsonc
// packages/app/tsconfig.json
{
  // ${configDir} resolves to packages/app/ -- paths are correct
  "extends": "../tsconfig.base.json"
}
```

## Conditions

- `${configDir}` resolves to the directory containing the tsconfig file that inherits the shared config
- Only useful for shared tsconfig files consumed from different directory depths
- Works in `outDir`, `rootDir`, `declarationDir`, `baseUrl`, `paths`, and other path-based options
- Does not apply to single-project setups where relative paths are already correct
- The template variable is replaced at config resolution time, not at runtime
