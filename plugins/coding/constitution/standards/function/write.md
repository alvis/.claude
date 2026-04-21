# Function: Compliant Code Patterns

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.
> **Compliance**: Also follow `scan.md` in this directory to avoid violations during writing. When unsure about a specific rule, consult its detailed guidance in `rules/<rule-id>.md`.

## Key Principles

- Every function declares an explicit return type
- Positional params for up to 2 required args; object param for 3+ or optional/config flags
- Use canonical parameter names: `params`, `options`, `data`, `config`, `context`, `details`
- Every field of an `Options` type is optional; defaults are applied at use site.
- Immutable transforms by default (`map`/`filter`/`reduce`, object spread)
- Single responsibility: one purpose, one reason to change
- Pure functions for transformation logic; side effects at clear boundaries
- Multi-line text via `Array.join("\n")`, not concatenation

## Core Rules Summary

### Architecture (FUNC-ARCH)

- **FUNC-ARCH-01**: Each function has one clear purpose and one primary reason to change. (→ GEN-DESN-01)
- **FUNC-ARCH-02**: Use `Array.join("\n")` for multi-line messages rather than repeated concatenation.
- **FUNC-ARCH-03**: Do not create pass-through wrappers that add no policy, validation, or transformation. (→ GEN-DESN-03)
- **FUNC-ARCH-04**: Remove early-return short-circuit guards when the protected loop averages ≤3 iterations; tiny guards before tiny loops add branch noise without saving meaningful work, so prefer optional chaining (`fn?.(...)`) at the call site and reserve guards for loops that typically run more than three iterations.

```ts
// good
for (const x of items) cb?.(x);

// bad
if (!cb) return;
for (const x of items) cb(x);
```

### Signatures (FUNC-SIGN)

- **FUNC-SIGN-01**: Every function signature MUST declare its return type.
- **FUNC-SIGN-02**: Positional parameters for up to two required arguments; one object parameter for 3+ inputs or optional/config flags.
- **FUNC-SIGN-03**: Use canonical semantic names (`params`, `options`, `data`, `config`, `context`, `details`); avoid `payload`, `cfg`, `extra`. (→ NAM-TYPE-02)
- **FUNC-SIGN-04**: Optional object parameters must be destructured safely using defaults or guarded merging. Every field of an `Options` type MUST be optional, AND the entire `options` parameter MUST be optional. If a field is genuinely required and not defaultable, rename the type to `*Params` (input contract) or `*Config` (durable provider config). (→ TYP-PARM-01)

```ts
// good
type Options = { model?: string; signal?: AbortSignal };
function run(input: Input, options?: Options): Out { /* defaults inside */ }

// bad — required field in Options
type Options = { model: string };
// bad — options itself required
function run(input: Input, options: Options): Out {}
```

- **FUNC-SIGN-05**: Exported functions MUST use dedicated parameter/result interfaces/types where contracts are non-trivial. (→ TYP-PARM-02)
- **FUNC-SIGN-06**: Object-param functions MUST NOT destructure inline at the declaration; accept `params: { ... }` and destructure in the body so future readers see the full param shape at the call boundary, stack frames keep `params` intact for readability, and debuggers/inspectors can reason about a single named argument. When a function takes `options`, it MUST be a separate trailing positional arg (`fn(params, options?)`), NEVER folded into the `params` object.

```ts
// good
function f(params: { a: T; b: U }): R {
  const { a, b } = params;
  /* body */
}

// bad
function f({ a, b }: { a: T; b: U }): R {
  /* body */
}

// good — options is a separate trailing arg
function f(params: { a: T; b: U }, options?: Options): R {
  const { a, b } = params;
}
// bad — options folded into params
function f(params: { a: T; b: U; options?: Options }): R {}
```

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
