# Function: Violation Scan

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.

Any single violation blocks submission by default.
If a violation is detected, load the matching rule guide at `./rules/<rule-id>.md`.

## Quick Scan

- DO NOT mix multiple responsibilities in one function [`FUNC-ARCH-01`] (→ GEN-DESN-01)
- DO NOT build multi-line text with string concatenation [`FUNC-ARCH-02`]
- DO NOT add wrappers that provide no behavioral value [`FUNC-ARCH-03`] (→ GEN-DESN-03)
- DO NOT omit explicit return types [`FUNC-SIGN-01`]
- DO NOT use overly long positional signatures [`FUNC-SIGN-02`]
- DO NOT use non-standard parameter names, such as `payload`, `cfg`, or `extra` when canonical names apply [`FUNC-SIGN-03`] (→ NAM-TYPE-02)
- DO NOT use unsafe optional destructuring [`FUNC-SIGN-04`] (→ TYP-PARM-01)
- DO NOT omit exported contract types [`FUNC-SIGN-05`] (→ TYP-PARM-02)
- DO NOT mutate input parameters [`FUNC-STAT-01`]
- DO NOT use mutable transforms when immutable transforms suffice, such as `items.push(...)` instead of creating a new array [`FUNC-STAT-02`]
- DO NOT mix pure logic with side effects [`FUNC-STAT-03`]
- DO NOT hide side effects in utility-style flows [`FUNC-STAT-04`]

## Rule Matrix

| Rule ID | Violation | Bad Examples |
|---|---|---|
| `FUNC-ARCH-01` | Function has multiple responsibilities | `function saveAndNotify(){ saveUser(user); sendWelcomeEmail(user); }` |
| `FUNC-ARCH-02` | Multi-line text uses concatenation | `msg += "- Email is required\n"`; `let message = "Validation failed:\n";` |
| `FUNC-ARCH-03` | Wrapper adds no behavioral value | `return service.run(data)` |
| `FUNC-SIGN-01` | Missing explicit return type | `function parse(x){ return x }`; `function getUserById(id: string) {` |
| `FUNC-SIGN-02` | Positional signature is overly long | `createUser(n,e,r,w,d)` |
| `FUNC-SIGN-03` | Parameter names are non-standard | `fn(payload, cfg, extra)` |
| `FUNC-SIGN-04` | Optional destructuring is unsafe | `const { a } = maybeOpts`; `function run({ id }: Options | undefined) {}` |
| `FUNC-SIGN-05` | Exported contract type is missing | `export function createUser(p:any)` |
| `FUNC-STAT-01` | Input parameter is mutated | `user.name = user.name.trim()`; `function processUser(user: User): User {` |
| `FUNC-STAT-02` | Mutable transform used without need | `items.push(nextItem)`; `for (const item of items) total += item.price` where `reduce`/immutable flow is sufficient |
| `FUNC-STAT-03` | Pure logic mixed with side effects | `logger.info(calc(x))` |
| `FUNC-STAT-04` | Side effects hidden in utility flow | `function sum(){ db.save() }` |
