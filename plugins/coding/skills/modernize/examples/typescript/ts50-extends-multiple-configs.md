---
since: "TS 5.0"
min-es-target: "any"
module: "any"
---

## Detection

Duplicated compiler options across multiple tsconfig files, or chained single `"extends"` inheritance

## Before

```jsonc
// tsconfig.json — can only extend one config
{
  "extends": "./configs/base.json",
  "compilerOptions": {
    // must duplicate strict settings here because we cannot also extend strict.json
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

```jsonc
// workaround: intermediate config that chains extends
// configs/base-strict.json
{
  "extends": "./base.json",
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

## After

```jsonc
// tsconfig.json — extend multiple configs directly
{
  "extends": ["./configs/base.json", "./configs/strict.json"],
  "compilerOptions": {
    // project-specific overrides only
    "outDir": "./dist"
  }
}
```

```jsonc
// configs/base.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "esnext",
    "moduleResolution": "bundler"
  }
}
```

```jsonc
// configs/strict.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

## Conditions

- Later configs in the array override earlier ones when the same option is specified
- The project's own `compilerOptions` override all extended configs
- Useful for monorepo setups with shared base configs (e.g., `@tsconfig/node20`, a team strict preset, and a project-specific config)
- `files`, `include`, and `exclude` from extended configs are also merged, with later entries taking precedence
