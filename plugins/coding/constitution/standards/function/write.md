# Function: Compliant Code Patterns

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.
> **Compliance**: Also follow `scan.md` in this directory to avoid violations during writing. When unsure about a specific rule, consult its detailed guidance in `rules/<rule-id>.md`.

## Key Principles

- Every function declares an explicit return type
- Positional params for up to 2 required args; object param for 3+ or optional/config flags
- Use canonical parameter names: `params`, `options`, `data`, `config`, `context`, `details`
- Immutable transforms by default (`map`/`filter`/`reduce`, object spread)
- Single responsibility: one purpose, one reason to change
- Pure functions for transformation logic; side effects at clear boundaries
- Multi-line text via `Array.join("\n")`, not concatenation

## Core Rules Summary

### Architecture (FUNC-ARCH)

- **FUNC-ARCH-01**: Each function has one clear purpose and one primary reason to change. (→ GEN-DESN-01)
- **FUNC-ARCH-02**: Use `Array.join("\n")` for multi-line messages rather than repeated concatenation.
- **FUNC-ARCH-03**: Do not create pass-through wrappers that add no policy, validation, or transformation. (→ GEN-DESN-03)

### Signatures (FUNC-SIGN)

- **FUNC-SIGN-01**: Every function signature MUST declare its return type.
- **FUNC-SIGN-02**: Positional parameters for up to two required arguments; one object parameter for 3+ inputs or optional/config flags.
- **FUNC-SIGN-03**: Use canonical semantic names (`params`, `options`, `data`, `config`, `context`, `details`); avoid `payload`, `cfg`, `extra`. (→ NAM-TYPE-02)
- **FUNC-SIGN-04**: Optional object parameters must be destructured safely using defaults or guarded merging. (→ TYP-PARM-01)
- **FUNC-SIGN-05**: Exported functions MUST use dedicated parameter/result interfaces/types where contracts are non-trivial. (→ TYP-PARM-02)

### State Safety (FUNC-STAT)

- **FUNC-STAT-01**: Treat input parameters as immutable.
- **FUNC-STAT-02**: Default to immutable transforms and return new values; mutation only for local performance-critical paths with explicit rationale.
- **FUNC-STAT-03**: Default to deterministic, side-effect-free functions for transformation logic.
- **FUNC-STAT-04**: Perform I/O, logging, persistence, and external calls at clear boundaries.

## Patterns

### Signature Style Decision

| Condition | Style |
|-----------|-------|
| Up to 2 required args with obvious order | Positional |
| 3+ inputs, optional flags, or ambiguous types | Object parameter |
| Non-trivial exported contract | Dedicated interface/type |

### Immutability Approach

Default to functional transforms that return new values:

- Arrays: `map`, `filter`, `reduce`, spread `[...arr, item]`
- Objects: spread `{ ...obj, key: value }`
- Mutation allowed only for local performance-critical paths with explicit rationale

## Anti-Patterns

- Large procedural functions with mixed concerns.
- Parameter overload via positional booleans.
- Implicit return types on exported logic.
- Hidden side effects inside utility-style function names.

## Quick Decision Tree

1. Define return type first (`FUNC-SIGN-01`).
2. Choose signature style (`FUNC-SIGN-02`).
3. Keep logic pure unless boundary work is required (`FUNC-STAT-03`, `FUNC-STAT-04`).
4. Validate immutability and contract clarity before merge (`FUNC-STAT-02`, `FUNC-SIGN-05`).
