---
since: "TS 5.6"
min-es-target: "any"
module: "esnext or nodenext"
---

## Detection

Workarounds for exporting names with special characters -- wrapper functions, string-keyed objects, or `Object.defineProperty` on module exports

## Before

```typescript
// cannot export names with special characters directly
// workaround: wrapper object
const exports = {
  "my-component/button": ButtonComponent,
  "my-component/input": InputComponent,
};

// workaround: dynamic property assignment
module.exports["my-export/name"] = myFunction;

// WebAssembly interop -- wasm often exports names with special chars
// workaround: manual binding
import * as wasm from "./module.wasm";
const greet = wasm["com.example/greet"]; // type is any
```

## After

```typescript
// string literal export names -- valid per TC39 Module Harmony proposal
const ButtonComponent = () => {};
const InputComponent = () => {};

export { ButtonComponent as "my-component/button" };
export { InputComponent as "my-component/input" };

// re-export with string identifier
export { greet as "com.example/greet" } from "./wasm-bindings.js";

// import with string identifier
import { "my-component/button" as Button } from "./components.js";

// useful for WebAssembly module interop
import { "com.example/greet" as greet } from "./module.wasm";
```

## Conditions

- Module identifiers can be any valid string literal, including those with `/`, `-`, `.`, spaces, etc.
- Follows the TC39 Module Harmony / Import Attributes proposal
- Primarily useful for FFI interop: WebAssembly, native modules, or cross-language bindings
- Requires `--module esnext` or `--module nodenext`
- Import-side must use `as` to bind the string identifier to a valid local variable name
- Not commonly needed in pure TypeScript projects -- mainly for interop scenarios
