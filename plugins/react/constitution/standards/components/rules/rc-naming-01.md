# RC-NAMING-01: Component & Hook File Naming

## Intent

Component files use `PascalCase.tsx` (e.g., `Button.tsx`); hook files use `camelCase.ts` starting with `use` (e.g., `useScroll.ts`). Tests and stories sit alongside the implementation as `<Name>.spec.tsx` and `<Name>.stories.tsx`.

## Fix

- Rename component files from lowercase or kebab-case to PascalCase: `browser.tsx` → `Browser.tsx`
- Rename hook files starting with capital `Use` to lowercase `use`: `UseScroll.ts` → `useScroll.ts`
- Place tests next to the component: `Button.tsx` + `Button.spec.tsx`
- Place stories next to the component: `Button.tsx` + `Button.stories.tsx`

## Code Superpowers

- Walk `components/` and flag any `.tsx` whose basename does not start with an uppercase letter (excluding `index.tsx`)
- Walk `components/` and `hooks/` and flag any `.ts` whose basename starts with `Use` instead of `use`
- Verify each `<Name>.tsx` has a sibling `<Name>.spec.tsx`

## Common Mistakes

1. Lowercase component files: `browser.tsx` instead of `Browser.tsx`
2. PascalCase hook files: `UseScroll.ts` instead of `useScroll.ts`
3. Tests in a separate `__tests__/` directory instead of co-located

## Edge Cases

- `index.tsx` re-export barrels are allowed
- Generated files from codegen tools may use other casing if isolated

## Related

RC-STRUCT-01, RC-STRUCT-02
