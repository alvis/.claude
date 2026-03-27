---
since: "TS 6.0"
min-es-target: "any"
module: "any"
---

## Detection

`"dom.iterable"` in tsconfig `lib` array
`"dom.asynciterable"` in tsconfig `lib` array

## Before

```jsonc
// tsconfig.json — explicit dom.iterable and dom.asynciterable required
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "dom.asynciterable", "ES2022"]
  }
}
```

```typescript
// These required dom.iterable to type-check
for (const element of document.querySelectorAll("div")) {
  element.classList.add("active");
}

const entries = new FormData(form).entries();
const params = [...new URLSearchParams(location.search)];

// These required dom.asynciterable
for await (const chunk of readableStream) {
  process(chunk);
}
```

## After

```jsonc
// tsconfig.json — dom now includes iterable and asynciterable
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "ES2022"]
  }
}
```

```typescript
// All the same code works — no changes needed
for (const element of document.querySelectorAll("div")) {
  element.classList.add("active");
}

const entries = new FormData(form).entries();
const params = [...new URLSearchParams(location.search)];

for await (const chunk of readableStream) {
  process(chunk);
}
```

## Conditions

- Safe to remove `dom.iterable` and `dom.asynciterable` from the `lib` array
- The `dom` lib now includes both automatically in TS 6.0
- No code changes needed — only tsconfig cleanup
- Iteration over `NodeList`, `FormData`, `URLSearchParams`, `Headers`, `ReadableStream`, etc. all covered
