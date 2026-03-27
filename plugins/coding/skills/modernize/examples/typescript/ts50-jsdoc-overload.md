---
since: "TS 5.0"
min-es-target: "any"
module: "any"
---

## Detection

JavaScript functions with complex union parameter types that would benefit from overload signatures

## Before

```javascript
/**
 * @param {string | URL} input
 * @param {{ json?: boolean }} [options]
 * @returns {Promise<string | object>}
 */
async function fetchData(input, options) {
  const response = await fetch(typeof input === "string" ? input : input.href);

  if (options?.json) {
    return response.json();
  }

  return response.text();
}

// return type is always Promise<string | object> — caller must narrow manually
const data = await fetchData("/api/users", { json: true });
// data is string | object even though json: true always returns object
```

## After

```javascript
/**
 * @overload
 * @param {string | URL} input
 * @param {{ json: true }} options
 * @returns {Promise<object>}
 */
/**
 * @overload
 * @param {string | URL} input
 * @param {{ json?: false }} [options]
 * @returns {Promise<string>}
 */
/**
 * @param {string | URL} input
 * @param {{ json?: boolean }} [options]
 * @returns {Promise<string | object>}
 */
async function fetchData(input, options) {
  const response = await fetch(typeof input === "string" ? input : input.href);

  if (options?.json) {
    return response.json();
  }

  return response.text();
}

// return type is now precise based on the options argument
const data = await fetchData("/api/users", { json: true });
// data is object

const text = await fetchData("/api/page");
// text is string
```

## Conditions

- Only applies to JavaScript files using JSDoc type checking (`checkJs: true` or `// @ts-check`)
- Not relevant for `.ts` files, which use native function overload syntax
- Each `@overload` tag must be in its own JSDoc comment block, immediately preceding the next
- The final JSDoc comment is the implementation signature and must be compatible with all overloads
