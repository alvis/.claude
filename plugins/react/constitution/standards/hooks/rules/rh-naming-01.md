# RH-NAMING-01: Hook Naming Convention

## Intent

All custom hooks must start with the `use` prefix. This is required for React's lint rules (`react-hooks/rules-of-hooks`, `react-hooks/exhaustive-deps`) to detect them. Names should be specific to the data or behavior they encapsulate, not generic.

## Fix

- Rename any function calling React hooks internally to start with `use`
- Replace generic names (`useData`, `useStuff`) with specific ones (`useUserData`, `useApiRequest`)
- Move shared, non-React utilities out of `use*`-prefixed names

```typescript
// ✅ GOOD: proper hook naming
useUserData(userId: string)
useApiRequest<T>(url: string)
useLocalStorage(key: string)

// ❌ BAD: missing prefix or unclear names
getUserData(userId: string)  // missing 'use' prefix
useData()                    // too generic
```

## Code Superpowers

- Grep functions that call `useState`/`useEffect`/`useCallback`/`useMemo`/`useReducer`/`useRef` and confirm their name starts with `use`
- Flag any exported `use*` whose name is one syllable or under 5 chars (likely too generic)

## Common Mistakes

1. Naming a hook `getX` because it returns data (lint won't enforce rules-of-hooks)
2. `useData`, `useState`-shadowing, or other ambiguous names
3. Prefixing utilities with `use` even though they don't call any hooks (creates false positives in lint)

## Edge Cases

- Higher-order hook factories (`createUseXxx`) may legitimately not start with `use`

## Related

RH-RETURN-01
