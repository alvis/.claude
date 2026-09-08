# DOC-CONT-06: Document Directly Raised Errors

## Intent

Document only errors raised by the function itself. Do not copy errors from called functions, libraries, getters, or awaited operations into its `@throws` or rejection documentation. Transitive error lists duplicate implementation details and become stale when callees change.

## Detection

For each documented error, locate the owning function or method and evidence that it directly raises that error under the stated condition. Explicit `throw`, including an unchanged caught-value rethrow, and locally created promise rejections qualify. A returned or awaited callee's rejection does not.

Inspect the owning body, excluding nested functions and callbacks: their throws belong to their own contracts. A `new Promise` executor's own reject parameter is the specific exception when it creates the promise returned by the owner. `Promise.reject(...)` must likewise contribute to the owner's rejection; a detached or handled rejection is not evidence that the owner rejects.

Check each error independently. One local throw does not justify every tag. Errors caught and consumed within the owner do not escape it. Dynamic error identities, declarations without implementations, or uncertain control flow require review; never infer a clean result or delete documentation solely from an advisory candidate.

## Fix

```typescript
/**
 * parses a required numeric value
 * @param text numeric input
 * @returns parsed number
 * @throws when the input is empty
 */
function parseRequiredNumber(text: string): number {
  if (text.length === 0) throw new Error("input is empty");
  return parseNumber(text);
}
```

The local empty-input error belongs here. Any error propagated from `parseNumber` does not. Remove only unsupported error claims; preserve directly raised errors and the rest of the function documentation. If the function catches an error and throws a replacement, document the replacement, not a separate list of underlying causes.

## Related

DOC-CONT-04, DOC-FORM-02, DOC-LIFE-04
