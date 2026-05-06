# RC-STRUCT-02: Exported Props Interface

## Intent

Every component exports a named `interface <Name>Props` and types itself with `FC<<Name>Props>`. Inline anonymous prop types prevent reuse, complicate documentation, and break type-only re-exports.

## Fix

- Replace inline destructured types with an exported interface
- Name the interface `<ComponentName>Props`
- Type the component as `FC<<ComponentName>Props>`

```typescript
// ❌ BAD: inline props type, not exported
const BadButton = ({ onClick }: { onClick: () => void }) => {
  return <button onClick={onClick}>...</button>;
};

// ✅ GOOD: exported interface
export interface ButtonProps {
  onClick?: () => void;
}

export const Button: FC<ButtonProps> = ({ onClick }) => {
  return <button onClick={onClick}>...</button>;
};
```

## Code Superpowers

- AST-scan component declarations for inline object-type annotations on the props parameter
- Flag any `FC<{...}>` literal type instead of a named interface
- Confirm each `export const X` has a matching `export interface XProps` in the same file

## Common Mistakes

1. Inlining props as `({ x, y }: { x: string; y: number })`
2. Declaring the interface but forgetting to `export` it
3. Naming the interface `Props` instead of `<Component>Props` (collides on re-export)

## Edge Cases

- Trivially small private components inside the same file may use inline types if not re-exported

## Related

RC-STRUCT-01, RC-PROPS-01
