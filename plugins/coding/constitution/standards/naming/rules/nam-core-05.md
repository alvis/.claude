# NAM-CORE-05: No Path Redundancy

## Intent

File names must not repeat a word that is already expressed by the parent directory. When a file lives inside a typed directory (e.g., `services/`, `store/`, `repositories/`), omit the type suffix from the file name.

## Fix

```typescript
// ❌ BAD: word repeated in path
store/token-store.ts
services/user-service.ts
repositories/user-repository.ts

// ✅ GOOD: directory provides the context
store/token.ts
services/user.ts
repositories/user.ts

// ✅ OK: suffix needed when no typed directory
lib/token-store.ts
src/user-service.ts
```

## Decision Guide

Read the full path aloud. If a word appears in both the directory name and the file name, remove it from the file name.

| Directory | Bad File Name | Good File Name |
|-----------|---------------|----------------|
| `store/` | `token-store.ts` | `token.ts` |
| `services/` | `user-service.ts` | `user.ts` |
| `repositories/` | `user-repository.ts` | `user.ts` |
| `utilities/` | `date-utils.ts` | `date.ts` |

## Edge Cases

- **No typed directory**: When the file is not inside a directory that conveys the type, keep the suffix (e.g., `src/user-service.ts`).
- **React components**: `UserProfile/UserProfile.tsx` is acceptable — React convention requires matching component name to file name.
- **Tooling suffixes**: `.spec`, `.config` are tooling indicators, not domain-type suffixes. These are not affected by this rule.

## Related

NAM-CORE-01, file-structure standard
