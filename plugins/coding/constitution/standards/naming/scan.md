# Naming: Violation Scan

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.

Any single violation blocks submission by default.
If a violation is detected, load the matching rule guide at `./rules/<rule-id>.md`.

## Quick Scan

- DO NOT use vague names without context [`NAM-CORE-01`]
- DO NOT use symbol casing that does not match symbol type [`NAM-CORE-02`]
- DO NOT use non-allowlisted abbreviations [`NAM-CORE-03`]
- DO NOT omit units from measured values [`NAM-CORE-04`]
- DO NOT use singular names for collections [`NAM-DATA-01`]
- DO NOT use map names that hide key-value relationships [`NAM-DATA-02`]
- DO NOT use boolean names without canonical prefixes [`NAM-DATA-03`]
- DO NOT use cryptic iteration variable names [`NAM-DATA-04`]
- DO NOT use noun-only function names [`NAM-FUNC-01`]
- DO NOT hide async behavior in function names [`NAM-FUNC-02`]
- DO NOT use inconsistent factory naming [`NAM-FUNC-03`]
- DO NOT use ambiguous data operation verbs, such as `FindById` or `process` for persisted-data operations [`NAM-FUNC-04`]
- DO NOT use legacy type prefixes [`NAM-TYPE-01`]
- DO NOT use non-standard parameter names [`NAM-TYPE-02`] (→ `FUNC-SIGN-03`)

## Rule Matrix

| Rule ID | Violation | Bad Examples |
|---|---|---|
| `NAM-CORE-01` | Name is vague without context | `const data = value`; `data` |
| `NAM-CORE-02` | Casing does not match symbol type | `const User_Name = "x"`; `user_service` |
| `NAM-CORE-03` | Non-allowlisted abbreviation used | `const usr = getUser()`; `gUsr()` |
| `NAM-CORE-04` | Unit missing from measured value | `const timeout = 5000` |
| `NAM-DATA-01` | Collections use singular names | `const user = []` |
| `NAM-DATA-02` | Map name hides relationship | `const userMap = new Map()` |
| `NAM-DATA-03` | Boolean missing canonical prefix | `const active = true`; `bIsActive` |
| `NAM-DATA-04` | Iteration variable is cryptic | `for (const x of items) {}` |
| `NAM-FUNC-01` | Function name is noun-only | `function user() {}`; `user()` |
| `NAM-FUNC-02` | Async behavior hidden by naming | `function user(){return fetch()}` |
| `NAM-FUNC-03` | Factory naming is inconsistent | `const createUserFactory = buildUserFactory()` |
| `NAM-FUNC-04` | Ambiguous data operation verb | `FindUserById(id)`; `process()` |
| `NAM-TYPE-01` | Legacy type prefixes used | `interface IUser {}`; `IUser` |
| `NAM-TYPE-02` | Parameter names are non-standard | `fn(payload, cfg, extra)` |
