---
since: "TS 5.8"
min-es-target: "any"
module: "nodenext"
---

## Detection

`await import\(` in `.cts` or CJS files, used because `require()` could not load ESM packages

## Before

```typescript
// src/loader.cts — CJS file that needs to use an ESM-only package

// Had to use dynamic import() because require() couldn't load ESM
async function loadPrettier() {
  const prettier = await import("prettier");
  return prettier.format("const x=1", { parser: "babel" });
}

// Forced the entire call chain to be async
async function formatCode(code: string) {
  const prettier = await import("prettier");
  const result = await prettier.format(code, { parser: "typescript" });
  return result;
}

// Top-level wrapper to handle the async requirement
(async () => {
  const formatted = await formatCode("const   x =    1;");
  console.log(formatted);
})();
```

## After

```typescript
// src/loader.cts — CJS file can now require() ESM packages on Node.js 22+

// Synchronous require() of ESM — no async wrapper needed
const prettier = require("prettier");

function formatCode(code: string) {
  return prettier.format(code, { parser: "typescript" });
}

// Direct synchronous usage
const formatted = formatCode("const   x =    1;");
console.log(formatted);
```

## Conditions

- Requires Node.js 22+ which added support for `require()` of ESM modules
- Requires `--module nodenext` in TS 5.8
- The ESM module being required must NOT use top-level `await`; if it does, `require()` will throw at runtime
- TS 5.8 understands this Node.js feature and will not error when `require()` targets an ESM package
- Particularly useful for CLI tools, build scripts, and CJS packages that need to consume ESM-only dependencies
- If the project must support Node.js versions older than 22, keep using `await import()` instead
- Check the ESM package's entry point for top-level `await` before switching to `require()`
