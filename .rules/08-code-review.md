# Code Review Checklist

When reviewing code (or suggesting via Copilot):

## Review Tone

- Use constructive, polite language
- Suggest improvements with justification
- Avoid blaming language (e.g., ❌ "this is wrong")

## Checklist

- ✅ Is the function self-contained and single-responsibility?
- ✅ Are all variables and types named clearly?
- ✅ Are errors handled explicitly?
- ✅ Are all edge cases tested?
- ✅ Are new files placed in correct directories?
- ✅ Do changes follow our TypeScript guidelines (see `05-code-style-conventions.md`)?
- ✅ Do React components follow conventions (see `06-react-conventions.md`)?

~ ✅ EXAMPLE ~

```typescript
// SUGGESTION: Consider using a discriminated union instead of a boolean here to improve extensibility
```

--- END ---
