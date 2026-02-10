# Testing: Violation Scan

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.

Any single violation blocks submission by default.
If a violation is detected, load the matching rule guide at `./rules/<rule-id>.md`.

## Quick Scan

- DO NOT bypass TypeScript safety requirements in tests [`TST-CORE-01`]
- DO NOT implement code before writing a failing test [`TST-CORE-02`]
- DO NOT use non-compliant test naming: `it(...)` must start with `should`; `describe(...)` titles scoped to a **symbol** (function, class, method, etc.) must use an approved prefix (`fn:`, `op:`, `sv:`, `cl:`, `mt:`, `gt:`, `st:`, `re:`, `ty:`, `rc:`, `hk:`); IMPORTANT: general-purpose `describe(...)` titles (e.g. grouping by scenario or context) must **NOT** use prefixes [`TST-CORE-03`]
- DO NOT add tests that provide no unique path or behavior [`TST-CORE-04`]
- DO NOT add artificial variation-only tests [`TST-CORE-05`]
- DO NOT write tests that only check wrapper/dependency calls [`TST-CORE-06`]
- DO NOT assert implementation details in tests [`TST-CORE-07`]
- DO NOT use dynamic imports in tests [`TST-CORE-08`]
- DO NOT merge with line coverage below 100% required threshold [`TST-COVR-01`]
- DO NOT leave critical branch paths untested [`TST-COVR-02`]
- DO NOT batch multiple tests before checking coverage [`TST-COVR-03`]
- DO NOT keep zero-coverage-gain tests [`TST-COVR-04`]
- DO NOT use mutable shared fixtures [`TST-DATA-01`]
- DO NOT assert object/array fields one-by-one [`TST-DATA-02`]
- DO NOT create factories without real variation needs [`TST-DATA-03`]
- DO NOT pass explicit `undefined` in override objects, such as `createUser({ role: undefined })` [`TST-DATA-04`]
- DO NOT create per-test instances without mutation need [`TST-DATA-05`]
- DO NOT mock pure/internal logic unnecessarily [`TST-MOCK-01`]
- DO NOT use `vi.hoisted` without spy/error need [`TST-MOCK-02`]
- DO NOT define happy-path defaults via chained `.mockResolvedValue(...)` / `.mockReturnValue(...)`, such as `vi.fn().mockResolvedValue(...)`; define defaults inline via `vi.fn(() => value)` or `vi.fn(async () => value)` [`TST-MOCK-03`]
- DO NOT use `beforeEach()` for mock setup (happy-path or otherwise); `beforeEach` is **only** for resetting call history of non-Vitest mocks that aren't automatically cleared (e.g., `client.resetHistory()`). Happy-path defaults go at file/describe level; error-path overrides go inside `it()`. Violations include `run.mockResolvedValue("ok")` in `it()`, `beforeEach(() => client.on(Cmd).resolves(...))`, and any `beforeEach` that configures mock return values [`TST-MOCK-04`]
- DO NOT skip `satisfies` checks in `vi.mock(...)` or `vi.hoisted(...)` mock typing, and DO NOT use weak generic types that bypass real type validation; `satisfies` must reference the **real module type** via `Partial<typeof import("...")>` or `Partial<RealType>` — never `Record<string, unknown>`, `Record<string, ReturnType<typeof vi.fn>>`, or inline structural types [`TST-MOCK-05`]
- DO NOT create oversized or synthetic mock surfaces [`TST-MOCK-06`]
- DO NOT control mock behavior with mutable flags [`TST-MOCK-07`]
- DO NOT manually assign every class mock method [`TST-MOCK-08`]
- DO NOT use double assertions that bypass mock typing, such as `as unknown as X` or `as any as X` [`TST-MOCK-09`]
- DO NOT replace config cleanup with manual cleanup hooks, such as `afterEach(() => vi.clearAllMocks())`, `beforeAll(() => vi.useFakeTimers())`, `afterAll(() => vi.useRealTimers())`, or `beforeEach(() => client.reset())` [`TST-MOCK-10`]
- DO NOT mutate globals/env without stubs [`TST-MOCK-11`]
- DO NOT repeat shared system time setup in individual test cases; set default `vi.useFakeTimers()` and `vi.setSystemTime(...)` at file or describe level [`TST-MOCK-12`]
- DO NOT use test identifiers that start with `mock` or `mocked` [`TST-MOCK-13`]
- DO NOT use module types for class instance mock typing, such as `typeof import("#svc")` for instance doubles [`TST-MOCK-14`]
- DO NOT wrap existing mock instances with nested `vi.fn` in `vi.mock` factories [`TST-MOCK-15`]
- DO NOT use `.test.ts` extension; use `.spec.ts` for unit, `.int.spec.ts` for integration, `.e2e.spec.ts` for e2e, such as `user.test.ts` instead of `user.spec.ts` [`TST-STRU-01`]
- DO NOT use ad-hoc test file layout/import order [`TST-STRU-02`]
- DO NOT add AAA section comments or inline noise comments or `expect(result).toBe(x); // check ...` [`TST-STRU-03`]

## Rule Matrix

| Rule ID | Violation | Bad Examples |
|---|---|--- |
| `TST-CORE-01` | Test code bypasses TypeScript safety requirements | `const svc: any = {}`; `const mockRepo: any = {` |
| `TST-CORE-02` | Code is implemented before a failing test exists | `runFeature(); // before failing test` |
| `TST-CORE-03` | Test naming format is non-compliant (`it`/`describe`) | `it("returns user", fn)`; `describe("processUser", () => { ... })`; `describe("fn:edge cases", () => { ... })` |
| `TST-CORE-04` | Test adds no unique path or behavior | `it("same case #2", fn)`; `it("should return user again with same input", fn)` |
| `TST-CORE-05` | Artificial variation tests are added | `tax(10); tax(20); tax(30)`; `it("should apply 10% discount for $101", fn)` when behavior is identical |
| `TST-CORE-06` | Test only checks wrapper/dependency calls | `expect(dep).toHaveBeenCalled()` |
| `TST-CORE-07` | Test asserts implementation details | `expect(useState).toHaveBeenCalled()` |
| `TST-CORE-08` | Dynamic import is used in tests | `const m = await import("#mod")` |
| `TST-COVR-01` | Line coverage is below 100% required threshold | `lines: 98 // required: 100` |
| `TST-COVR-02` | Critical branch path is untested | `if (err) throw err // untested` |
| `TST-COVR-03` | Multiple tests written before coverage check | `it.each(cases)(...)` |
| `TST-COVR-04` | Zero-coverage-gain test is kept | `coverageDelta === 0 // keep` |
| `TST-DATA-01` | Shared fixture is mutable | `let user = { id: "u1" }`; `let service: UserService;` |
| `TST-DATA-02` | Object/array assertion is field-by-field | `expect(result.id).toBe("1")`; `expect(result.mime).toBe('application/octet-stream');` |
| `TST-DATA-03` | Factory exists without real variation need | `const mk = () => new Service()`; `const createDefaultUser = () => ({ id: "u1", role: "user" })` used once |
| `TST-DATA-04` | Override passes explicit `undefined` field | `createUser({ role: undefined })`; `createSession({ expiresAt: undefined })` |
| `TST-DATA-05` | Per-test instance created without mutation need | `beforeEach(() => svc = new Svc())` when constructor args and state never change |
| `TST-MOCK-01` | Pure/internal logic is mocked unnecessarily | `vi.mock("#utils/math")`; `vi.spyOn(formatter, "formatCurrency").mockReturnValue("$0")` |
| `TST-MOCK-02` | `vi.hoisted` used without spy/error need | `const h = vi.hoisted(() => ({ x: 1 }))` |
| `TST-MOCK-03` | Mock lacks inline happy-path default or chains happy-path return mutators | `const run = vi.fn().mockResolvedValue("ok")`; `service.send.mockReturnValue("ok")` for baseline success |
| `TST-MOCK-04` | Mock setup inside `beforeEach` or happy-path return inside `it()` | `run.mockResolvedValue("ok")` inside `it(...)`; `beforeEach(() => run.mockReturnValue("ok"))`; `beforeEach(() => { client.on(Cmd).resolves(...) })`; `beforeEach(() => { client.reset(); client.on(Cmd).resolves(...) })` |
| `TST-MOCK-05` | Mock typing skips `satisfies` or uses weak generic types instead of real module types | `vi.mock("#repo", () => ({ get: vi.fn() }))`; `const repo = { get: vi.fn() } as Repo`; `satisfies Record<string, unknown>`; `satisfies Record<string, ReturnType<typeof vi.fn>>`; `satisfies { get: (key: string) => string \| null }` |
| `TST-MOCK-06` | Mock surface is oversized or synthetic | `interface MockRepo { get():void }`; `interface MockBrowserWindow {}` |
| `TST-MOCK-07` | Mutable flag controls mock behavior | `scenario.fail = true`; `mockScenario.existsReturnsFalse = true;` |
| `TST-MOCK-08` | Class mock manually assigns every method | `this.a = mock.a; this.b = mock.b`; `this.encode = encodeMock; this.decode = decodeMock` instead of `Object.assign` |
| `TST-MOCK-09` | Double assertion bypasses mock typing | `{} as unknown as BlobClient`; `{} as any as BlobClient` |
| `TST-MOCK-10` | Manual cleanup hooks replace config cleanup | `afterEach(() => vi.clearAllMocks())`; `afterEach(() => vi.restoreAllMocks())`; `beforeAll(() => vi.useFakeTimers())`; `afterAll(() => vi.useRealTimers())`; `beforeEach(() => client.reset())` |
| `TST-MOCK-11` | Globals/env are mutated without stubs | `process.env.API_URL = "x"` |
| `TST-MOCK-12` | Shared system time is repeated in individual test cases or wrapped in hooks | `it("x", () => vi.setSystemTime(now))`; `beforeAll(() => { vi.useFakeTimers(); vi.setSystemTime(date) })` |
| `TST-MOCK-13` | Test identifier starts with forbidden `mock` or `mocked` | `const mockUserRepo = {}` |
| `TST-MOCK-14` | Module type is used for class instance mock typing | `Partial<typeof import("#svc")>`; `const client: typeof import("#svc") = { ... }` for an instance double |
| `TST-MOCK-15` | Existing mock instance is wrapped by nested `vi.fn` in `vi.mock` factory | `existsSync: vi.fn((...args: unknown[]) => existsSync(...args))`; `upload: vi.fn(async (...args) => upload(...args))` |
| `TST-STRU-01` | Test file uses `.test.ts` instead of `.spec.ts` / `.int.spec.ts` / `.e2e.spec.ts` | `user.test.ts`; `user-api.integration.ts` |
| `TST-STRU-02` | File layout/import order is ad-hoc | `describe(...) // before mock setup`; `import { describe, it, expect, vi } from 'vitest';` |
| `TST-STRU-03` | AAA spacing/comment policy is violated | `// Arrange`; `expect(result.name).toBe('John'); // check that result has name` |
