# TypeScript: Violation Scan

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.

Any single violation blocks submission by default.
If a violation is detected, load the matching rule guide at `./rules/<rule-id>.md`.

## Quick Scan

- DO NOT use boundary values without explicit domain typing [`TYP-CORE-01`]
- DO NOT use `any` [`TYP-CORE-02`]
- DO NOT use type-escape casts in production/runtime paths, such as `as unknown as` or `as never` [`TYP-CORE-03`]
- DO NOT add suppression comments without approval [`TYP-CORE-04`] (→ `GEN-SAFE-01`)
- DO NOT use mutable bindings without need [`TYP-CORE-05`]
- DO NOT use non-American spelling in code symbols [`TYP-CORE-06`] (→ `GEN-CONS-02`)
- DO NOT use deprecated JS patterns in TypeScript code [`TYP-CORE-07`]
- DO NOT place imports out of category order (node: built-in → third-party → project subpath/alias/relative; type imports follow the same order), such as `import x from "#a"; import fs from "fs"` [`TYP-IMPT-01`]
- DO NOT mix code and type imports [`TYP-IMPT-02`]
- DO NOT use namespace imports [`TYP-IMPT-03`]
- DO NOT use relative paths where subpath aliases exist, such as `../fastify/request` instead of `#fastify/request` [`TYP-IMPT-04`]
- DO NOT use subpath imports inside the same subpath module, such as `#fastify/error` from another file under `#fastify/*` [`TYP-IMPT-05`]
- DO NOT use default imports when named imports exist [`TYP-IMPT-06`]
- DO NOT break top-level symbol group ordering (imports → re-exports → types → constants → classes → functions), such as `export function run() {} const X = 1` [`TYP-MODL-01`]
- DO NOT place helper/leaf functions before the public/root functions that call them, such as defining `checkFields()` before `processUser()` that calls it [`TYP-MODL-02`]
- DO NOT expose default exports from modules where disallowed [`TYP-MODL-03`]
- DO NOT use unsafe optional object destructuring [`TYP-PARM-01`] (→ `FUNC-SIGN-04`)
- DO NOT use inline/weak typing for exported contracts [`TYP-PARM-02`] (→ `FUNC-SIGN-05`)
- DO NOT ignore property ordering contracts, such as `type X = { meta: string; id: string }` when canonical order is `id` then `meta` [`TYP-PARM-03`]
- DO NOT use `type` for plain object shapes (use `interface`) or `interface` for unions/intersections (use `type`), such as `type User = { id: string }` [`TYP-TYPE-01`]
- DO NOT leave public interfaces without required docs [`TYP-TYPE-02`]
- DO NOT use `private` keyword instead of `#` prefix for class fields, or omit `readonly` where values are never reassigned, such as `class S { private repo: Repo }` [`TYP-TYPE-03`]
- DO NOT leave generics unconstrained where bounds are needed [`TYP-TYPE-04`]
- DO NOT use throw-only flow for expected failures [`TYP-TYPE-05`]
- DO NOT cast unknown input without validation [`TYP-TYPE-06`]
- DO NOT misuse testing-only cast/typing exception patterns in production paths, such as `as unknown as User` or `as never` [`TYP-TYPE-07`]

## Rule Matrix

| Rule ID | Violation | Bad Examples |
|---|---|---|
| `TYP-CORE-01` | Boundary value is used without explicit domain typing | `const currency = "USD"`; `const currency = "USD"; // could be any string` |
| `TYP-CORE-02` | `any` is used | `const data: any = payload`; `function parseJson(input: string): any { ... }` |
| `TYP-CORE-03` | Type-escape casting bypasses type safety | `value as unknown as User`; `supabaseClient as never` |
| `TYP-CORE-04` | Suppression comment used without approval | `// @ts-ignore` |
| `TYP-CORE-05` | Mutable binding declared without need | `let baseUrl = "https://api"`; `let baseUrl = 'https://api.example.com'; // never reassigned` |
| `TYP-CORE-06` | Non-American spelling appears in code symbols | `interface ColourConfig {}` |
| `TYP-CORE-07` | Deprecated JS pattern appears in TS code | `var total = list.length`; `var name = "John"; // use const` |
| `TYP-IMPT-01` | Imports are not in category order (node: → third-party → project; type imports follow same order) | `import x from "#a"; import fs from "fs"`; `import { useState } from "react"; import { readFile } from "node:fs/promises"` |
| `TYP-IMPT-02` | Code and type imports are mixed | `import { x, type T } from "pkg"`; `import { useState, type FC } from 'react';` |
| `TYP-IMPT-03` | Namespace import is used | `import * as React from "react"`; `import * as React from 'react';` |
| `TYP-IMPT-04` | Relative path used where subpath exists | `import { h } from "../fastify/request"`; `import { handler } from './fastify/request';` |
| `TYP-IMPT-05` | Subpath used inside the same subpath module | `import { e } from "#fastify/error"`; `import { formatResponse } from '#fastify/response';` |
| `TYP-IMPT-06` | Default import is used when named import exists | `import React from "react"`; `import React from 'react';` |
| `TYP-MODL-01` | Symbol group order violated (imports → re-exports → types → constants → classes → functions) | `export function run() {} const X = 1`; `const Y = 1; interface Config {}` |
| `TYP-MODL-02` | Helper/leaf function appears before the root function that calls it | `function validate(u: User) {} export function createUser(u: User) { validate(u); }` |
| `TYP-MODL-03` | Module exposes default export | `export default userService`; `export default userService;` |
| `TYP-PARM-01` | Optional object destructuring is unsafe | `function run({id}:Opts){}`; `function processUser({ name, role = 'user' }: UserOptions) {` |
| `TYP-PARM-02` | Exported contract uses inline/weak typing | `export function setUser(p:any){}` |
| `TYP-PARM-03` | Property ordering contract is ignored | `type X={meta:string,id:string}` |
| `TYP-TYPE-01` | `type` used for object shape (should be `interface`) or `interface` used for union/intersection (should be `type`) | `type User = { id: string }` |
| `TYP-TYPE-02` | Public interface lacks required docs | `interface User { id: string }`; `interface User {` |
| `TYP-TYPE-03` | `private` used instead of `#` prefix, or `readonly` omitted on never-reassigned field | `class S { private repo: Repo }`; `class Service {` |
| `TYP-TYPE-04` | Generic design lacks useful constraints | `interface Repo<T>{get(id:string):T}`; `function parse<T>(input: string): T` |
| `TYP-TYPE-05` | Expected failure uses throw-only flow | `throw new Error("not found")` |
| `TYP-TYPE-06` | Unknown input is cast without validation | `const user = payload as User` |
| `TYP-TYPE-07` | Testing exception pattern is misused in production/runtime paths | `const u = {} as unknown as User`; `fn(partialClient as never)` |
