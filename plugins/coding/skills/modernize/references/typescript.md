# TypeScript Feature Reference

Compact reference for the `modernize` skill. One `use` line per feature, linking to versioned example files.

---

## TypeScript 5.0

- use TC39 decorators instead of experimental decorators → [ts50-tc39-decorators.md](../examples/typescript/ts50-tc39-decorators.md)
- use `const` type parameters for literal type inference in generics → [ts50-const-type-parameters.md](../examples/typescript/ts50-const-type-parameters.md)
- use union enum types (all enums are now union enums) → [ts50-union-enum-types.md](../examples/typescript/ts50-union-enum-types.md)
- use `export type *` for type-only namespace re-exports → [ts50-export-type-star.md](../examples/typescript/ts50-export-type-star.md)
- use `--moduleResolution bundler` for bundler-based projects → [ts50-module-resolution-bundler.md](../examples/typescript/ts50-module-resolution-bundler.md)
- use `--verbatimModuleSyntax` instead of `importsNotUsedAsValues`/`preserveValueImports` → [ts50-verbatim-module-syntax.md](../examples/typescript/ts50-verbatim-module-syntax.md)
- use `--allowArbitraryExtensions` for non-JS/TS file imports via declaration files → [ts50-allow-arbitrary-extensions.md](../examples/typescript/ts50-allow-arbitrary-extensions.md)
- use `--resolvePackageJsonExports` and `--resolvePackageJsonImports` for package.json field resolution → [ts50-resolve-package-json-fields.md](../examples/typescript/ts50-resolve-package-json-fields.md)
- use multiple `extends` in tsconfig.json for shared configurations → [ts50-extends-multiple-configs.md](../examples/typescript/ts50-extends-multiple-configs.md)
- use JSDoc `@satisfies` for type validation without losing specificity → [ts50-jsdoc-satisfies.md](../examples/typescript/ts50-jsdoc-satisfies.md)
- use JSDoc `@overload` for function overload declarations in JS → [ts50-jsdoc-overload.md](../examples/typescript/ts50-jsdoc-overload.md)
- ⚠️ deprecated: `target: ES3`, `charset`, `importsNotUsedAsValues`, `noImplicitUseStrict`, `keyofStringsOnly`, `suppressExcessPropertyErrors`, `suppressImplicitAnyIndexErrors`, `out`, `preserveValueImports`, `prepend` → [ts50-deprecations.md](../examples/typescript/ts50-deprecations.md)

## TypeScript 5.1

- use implicit returns for `undefined`-returning functions → [ts51-implicit-undefined-returns.md](../examples/typescript/ts51-implicit-undefined-returns.md)
- use unrelated types for getters and setters → [ts51-unrelated-accessor-types.md](../examples/typescript/ts51-unrelated-accessor-types.md)
- use namespaced JSX attributes (`svg:xmlns`, `xlink:href`) → [ts51-namespaced-jsx-attributes.md](../examples/typescript/ts51-namespaced-jsx-attributes.md)

## TypeScript 5.2

- use `using` and `await using` declarations for explicit resource management → [ts52-using-declarations.md](../examples/typescript/ts52-using-declarations.md)
- use decorator metadata via `Symbol.metadata` and `context.metadata` → [ts52-decorator-metadata.md](../examples/typescript/ts52-decorator-metadata.md)
- use non-mutating array methods: `toSorted()`, `toSpliced()`, `toReversed()`, `with()` (ES2023) → [ts52-array-copying-methods.md](../examples/typescript/ts52-array-copying-methods.md)
- use symbols as `WeakMap`/`WeakSet` keys → [ts52-symbols-as-weakmap-keys.md](../examples/typescript/ts52-symbols-as-weakmap-keys.md)

## TypeScript 5.3

- use import attributes (`with { type: "json" }`) instead of import assertions (`assert`) → [ts53-import-attributes.md](../examples/typescript/ts53-import-attributes.md)
- use `switch(true)` with type narrowing in case clauses → [ts53-switch-true-narrowing.md](../examples/typescript/ts53-switch-true-narrowing.md)
- use `instanceof` narrowing through `Symbol.hasInstance` → [ts53-instanceof-symbol-hasinstance.md](../examples/typescript/ts53-instanceof-symbol-hasinstance.md)
- use narrowing on boolean comparisons (`x === true`) → [ts53-boolean-comparison-narrowing.md](../examples/typescript/ts53-boolean-comparison-narrowing.md)

## TypeScript 5.4

- use `NoInfer<T>` to prevent unwanted type inference at specific positions → [ts54-noinfer-utility-type.md](../examples/typescript/ts54-noinfer-utility-type.md)
- use `Object.groupBy()` instead of manual reduce/loop grouping (ES2024) → [ts54-object-groupby.md](../examples/typescript/ts54-object-groupby.md)
- use `Map.groupBy()` for grouping into Map instances (ES2024) → [ts54-map-groupby.md](../examples/typescript/ts54-map-groupby.md)
- use preserved narrowing in closures after last assignment → [ts54-closure-narrowing.md](../examples/typescript/ts54-closure-narrowing.md)
- use subpath imports (`#*`, `#/*`, `#/`) via package.json `imports` field → [ts54-subpath-imports.md](../examples/typescript/ts54-subpath-imports.md)

## TypeScript 5.5

- use inferred type predicates (remove explicit `is` return annotations when TS can infer) → [ts55-inferred-type-predicates.md](../examples/typescript/ts55-inferred-type-predicates.md)
- use control flow narrowing for constant indexed accesses (`obj[key]`) → [ts55-constant-indexed-access-narrowing.md](../examples/typescript/ts55-constant-indexed-access-narrowing.md)
- use regular expression syntax checking (compile-time regex validation) → [ts55-regex-syntax-checking.md](../examples/typescript/ts55-regex-syntax-checking.md)
- use `--isolatedDeclarations` for parallel declaration emit with explicit annotations → [ts55-isolated-declarations.md](../examples/typescript/ts55-isolated-declarations.md)
- use JSDoc `@import` tag for explicit type imports in JS files → [ts55-jsdoc-import-tag.md](../examples/typescript/ts55-jsdoc-import-tag.md)
- use Set methods: `.union()`, `.intersection()`, `.difference()`, `.symmetricDifference()`, `.isDisjointFrom()` → [ts55-set-methods.md](../examples/typescript/ts55-set-methods.md)
- use `${configDir}` template variable in tsconfig.json for portable paths → [ts55-config-dir-template.md](../examples/typescript/ts55-config-dir-template.md)

## TypeScript 5.6

- use disallowed nullish/truthy checks to catch always-true/falsy conditions → [ts56-disallowed-nullish-truthy-checks.md](../examples/typescript/ts56-disallowed-nullish-truthy-checks.md)
- use `IteratorObject` type, subtypes, and iterator helper methods (`.map()`, `.filter()`, `.take()`, `.drop()`, `Iterator.from()`) → [ts56-iterator-helpers.md](../examples/typescript/ts56-iterator-helpers.md)
- use `--noUncheckedSideEffectImports` to catch typos in side-effect imports → [ts56-no-unchecked-side-effect-imports.md](../examples/typescript/ts56-no-unchecked-side-effect-imports.md)
- use `--noCheck` to skip type checking while emitting (faster builds) → [ts56-no-check-option.md](../examples/typescript/ts56-no-check-option.md)
- use arbitrary module identifiers (string literal import/export names) → [ts56-arbitrary-module-identifiers.md](../examples/typescript/ts56-arbitrary-module-identifiers.md)

## TypeScript 5.7

- use never-initialized variable checks (catches vars used without assignment) → [ts57-never-initialized-variable-checks.md](../examples/typescript/ts57-never-initialized-variable-checks.md)
- use `--rewriteRelativeImportExtensions` for automatic `.ts` → `.js` path rewriting → [ts57-rewrite-relative-import-extensions.md](../examples/typescript/ts57-rewrite-relative-import-extensions.md)
- use validated JSON imports with `type: "json"` attribute in `--module nodenext` → [ts57-validated-json-imports.md](../examples/typescript/ts57-validated-json-imports.md)
- use `--allowImportingTsExtensions` with `require()` (not just `import`) → [ts57-allow-importing-ts-extensions-require.md](../examples/typescript/ts57-allow-importing-ts-extensions-require.md)
- use `Promise.withResolvers()` for deferred promise creation (ES2024 lib) → [ts57-promise-with-resolvers.md](../examples/typescript/ts57-promise-with-resolvers.md)

## TypeScript 5.8

- use granular return branch checks (catches `any` contamination in ternary returns) → [ts58-granular-return-branch-checks.md](../examples/typescript/ts58-granular-return-branch-checks.md)
- use preserved computed property names in declaration files → [ts58-computed-property-declarations.md](../examples/typescript/ts58-computed-property-declarations.md)
- use `require()` of ESM modules in `--module nodenext` (Node.js 22+) → [ts58-require-esm-nodenext.md](../examples/typescript/ts58-require-esm-nodenext.md)
- use `--module node18` for Node.js 18-locked projects → [ts58-module-node18.md](../examples/typescript/ts58-module-node18.md)
- use `--libReplacement` flag to control lib file substitution → [ts58-lib-replacement-flag.md](../examples/typescript/ts58-lib-replacement-flag.md)
- ⚠️ deprecated: import assertions (`assert` keyword) under `--module nodenext` — use `with` instead → [ts58-import-assertions-deprecated.md](../examples/typescript/ts58-import-assertions-deprecated.md)

## TypeScript 5.9

- use `import defer` for deferred/lazy module loading → [ts59-import-defer.md](../examples/typescript/ts59-import-defer.md)
- use `--module node20` for Node.js 20 module resolution → [ts59-module-node20.md](../examples/typescript/ts59-module-node20.md)

## TypeScript 6.0

- use `Temporal` API for modern date/time handling (requires `esnext` lib) → [ts60-temporal-api.md](../examples/typescript/ts60-temporal-api.md)
- use `RegExp.escape()` for safe regex string escaping (ES2025 lib) → [ts60-regexp-escape.md](../examples/typescript/ts60-regexp-escape.md)
- use `Promise.try()` for synchronous-throw-safe promise wrapping (ES2025 lib) → [ts60-promise-try.md](../examples/typescript/ts60-promise-try.md)
- use `--stableTypeOrdering` for consistent union ordering in `.d.ts` files → [ts60-stable-type-ordering.md](../examples/typescript/ts60-stable-type-ordering.md)
- use `dom` lib which now includes `dom.iterable` and `dom.asynciterable` → [ts60-dom-iterable-included.md](../examples/typescript/ts60-dom-iterable-included.md)
- ⚠️ deprecated: `--outFile` (removed — use bundlers) → [ts60-removed-outfile.md](../examples/typescript/ts60-removed-outfile.md)
- ⚠️ deprecated: `--moduleResolution classic` (removed — use `nodenext`/`bundler`) → [ts60-removed-classic.md](../examples/typescript/ts60-removed-classic.md)
- ⚠️ deprecated: `target: es5` (minimum now ES2015) → [ts60-deprecated-es5.md](../examples/typescript/ts60-deprecated-es5.md)
- ⚠️ deprecated: `module` keyword for namespaces (use `namespace`) → [ts60-deprecated-module-namespace.md](../examples/typescript/ts60-deprecated-module-namespace.md)
- ⚠️ deprecated: `--module amd`, `--module umd`, `--module system` (removed) → [ts60-removed-module-formats.md](../examples/typescript/ts60-removed-module-formats.md)
