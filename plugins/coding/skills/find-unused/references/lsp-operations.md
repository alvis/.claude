# LSP Operations Reference

This reference maps each detection task in `find-unused` to the specific LSP operation that performs it, plus how to classify the references the LSP returns.

## Detection Task → LSP Operation

| Detection Task | LSP Operation | Description |
| -------------- | ------------- | ----------- |
| Enumerate symbols in a file | `documentSymbol` | Get all functions, classes, variables in a document |
| Find if symbol is used | `findReferences` | Find all references to a symbol |
| Trace call chains (2nd-degree) | `incomingCalls` / `outgoingCalls` | Find callers/callees of a function |
| Search symbols across workspace | `workspaceSymbol` | Find symbols matching a query across all files |
| Find symbol definitions | `goToDefinition` | Navigate to where a symbol is defined |
| Find implementations | `goToImplementation` | Find implementations of interfaces/abstract methods |

## Reference Classification (Critical)

When using `findReferences`, classify each returned reference by its surrounding context. Only "actual usage" references count toward marking a symbol as used.

| Reference Type | Counts as Usage? | Example |
| -------------- | ---------------- | ------- |
| Function call | Yes | `myFunction()` |
| Class instantiation | Yes | `new MyClass()` |
| Variable read | Yes | `const x = myVar` |
| Property access | Yes | `obj.myMethod()` |
| Type annotation | Yes | `const x: MyType` |
| Export statement | No | `export { myFunc }` |
| Re-export | No | `export * from './mod'` |
| Import statement | No | `import { x } from './y'` |
| Type-only import | No | `import type { X }` |
| Definition itself | No | `function myFunc() {}` |

**A symbol is UNUSED if `findReferences` returns ONLY non-usage references (definition, exports, imports).**

## LSP Response Validation

Before trusting analysis output, verify the LSP layer is healthy:

- Confirm `documentSymbol` returns expected symbol kinds (functions, classes, variables, types).
- Validate `findReferences` includes all reference locations across the workspace, not just the current file.
- Check `incomingCalls` / `outgoingCalls` for completeness when tracing 2nd-degree chains.
- Ensure `workspaceSymbol` covers all entry points declared in `package.json` (including subpath exports).
