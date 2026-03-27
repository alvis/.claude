---
since: "TS 5.1"
min-es-target: "any"
module: "any"
---

## Detection

`as any` or spread workarounds (`{...{"xmlns:xlink": ...}}`) for namespaced JSX attributes

## Before

```typescript
// Workaround: spread with type assertion for namespaced SVG attributes
function Icon() {
  return (
    <svg
      {...({ "xmlns:xlink": "http://www.w3.org/1999/xlink" } as any)}
      {...({ "xlink:href": "#icon-check" } as any)}
    >
      <use {...({ "xlink:href": "#icon-check" } as any)} />
    </svg>
  );
}

// Alternative workaround: dangerouslySetInnerHTML or string templates
function MathFormula() {
  return (
    <math
      {...({ "xmlns:mml": "http://www.w3.org/1998/Math/MathML" } as any)}
    />
  );
}
```

## After

```typescript
// TS 5.1+: namespaced attributes supported directly in JSX
function Icon() {
  return (
    <svg xmlns:xlink="http://www.w3.org/1999/xlink">
      <use xlink:href="#icon-check" />
    </svg>
  );
}

function MathFormula() {
  return <math xmlns:mml="http://www.w3.org/1998/Math/MathML" />;
}
```

## Conditions

- JSX must be enabled (`jsx` compiler option set)
- Primarily useful for SVG and MathML elements that use namespaced attributes
- The first segment of the namespaced name is used as the attribute name lookup on the JSX type
- Not needed for React's camelCase equivalents (`xlinkHref`) unless targeting raw SVG output
