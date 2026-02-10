# TYP-MODL-03: Prefer Named Exports

## Intent

Use named exports by default. Default exports are allowed only when an external contract requires it (e.g., Next.js page components).

## Fix

```typescript
// ✅ GOOD: named exports
export const userService = new UserService();
export const validateEmail = (email: string): boolean => { /* ... */ };

// ✅ GOOD: re-exports
export { UserRepository } from "./user-repository";
export type { User, CreateUser } from "./types";

// ❌ BAD: default exports (avoid unless required)
export default userService;
```

## Edge Cases

- When existing code matches prior violation patterns such as ❌ `export default userService`, refactor before adding new behavior.
- Default exports are acceptable only when an external framework or contract requires it.

## Related

TYP-MODL-01, TYP-MODL-02, TYP-IMPT-06
