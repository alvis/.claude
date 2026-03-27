---
since: "TS 5.0"
---

## Deprecated Compiler Options

The following tsconfig options were deprecated in TS 5.0 and became hard errors in TS 5.5.

### `target: "ES3"`

Remove and set `target` to `"ES5"` or later. ES3 environments (IE6-8) are no longer supported.

### `charset`

Remove entirely. TypeScript only reads UTF-8 encoded files. This option had no effect.

### `importsNotUsedAsValues`

Replace with `"verbatimModuleSyntax": true`. See `ts50-verbatim-module-syntax.md`.

### `preserveValueImports`

Replace with `"verbatimModuleSyntax": true`. See `ts50-verbatim-module-syntax.md`.

### `noImplicitUseStrict`

Remove entirely. ES modules always use strict mode. If targeting CommonJS, strict mode is standard practice and should not be disabled.

### `keyofStringsOnly`

Remove entirely. This was a TS 2.9 migration flag that forced `keyof` to return only `string` instead of `string | number | symbol`. Modern code should handle all key types.

### `suppressExcessPropertyErrors`

Remove entirely. Excess property checks catch real bugs. If specific cases require extra properties, use an index signature or type assertion.

### `suppressImplicitAnyIndexErrors`

Remove entirely. Use `"noUncheckedIndexedAccess": true` instead for safer index access. If a specific object allows arbitrary keys, add an explicit index signature.

### `out`

Replace with `"outFile"`. The `out` option concatenated files in an unpredictable order. `outFile` is the corrected version (relevant only for `--module amd` or `--module system`).

### `prepend` (in project references)

Remove from project references. This option worked only with `out` and had the same ordering issues. Use a bundler for file concatenation instead.

## Detection

```jsonc
// tsconfig.json — any of these flags trigger this deprecation
{
  "compilerOptions": {
    "target": "ES3",
    "charset": "utf8",
    "importsNotUsedAsValues": "error",
    "preserveValueImports": true,
    "noImplicitUseStrict": true,
    "keyofStringsOnly": true,
    "suppressExcessPropertyErrors": true,
    "suppressImplicitAnyIndexErrors": true,
    "out": "./bundle.js"
  },
  "references": [
    { "path": "../lib", "prepend": true }
  ]
}
```
