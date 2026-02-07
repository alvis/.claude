# Testing Standards

_Comprehensive testing standards for quality assurance, TDD compliance, and TypeScript type safety_

## Dependent Standards

You MUST also read the following standards together with this file:

- TypeScript Standards (standard:typescript) - Tests must follow TypeScript type safety requirements
- General Coding Principles (standard:general-principles) - Test code must adhere to fundamental coding principles
- Naming Standards (standard:naming) - Test functions must follow naming conventions
- Documentation Standards (standard:documentation) - Complex test scenarios require proper JSDoc documentation

## What's Stricter Here

This standard enforces requirements beyond typical Vitest best practices:

| Standard Practice          | Our Stricter Requirement                               |
| -------------------------- | ------------------------------------------------------ |
| vi.hoisted for all mocks   | **vi.hoisted only for spying/error tests**             |
| Modify mock returns freely | **Only error throwing allowed**                        |
| High coverage encouraged   | **100% coverage mandatory**                            |
| Mocks optional typing      | **All mocks must use `satisfies`**                     |
| Any test structure         | **AAA with mandatory blank lines**                     |
| beforeEach acceptable      | **File-level instances by default; per-test only when test mutates** |
| Coverage threshold config  | **Delete tests that add zero coverage**                |

## Violation Checklist

Before submitting tests, verify NONE of these violations are present:

- ❌ DO NOT omit 'should' prefix in test descriptions
- ❌ DO NOT write redundant tests with artificial variations
- ❌ DO NOT capitalize comments (follow documentation standard for lowercase)
- ❌ DO NOT add AAA section comments or inline comments that don't explain why
- ❌ DO NOT use mutable shared state with `let` in test setup
- ❌ DO NOT assert object/array fields one by one
- ❌ DO NOT change mock success return values inside `it()` blocks
- ❌ DO NOT create mocks without default happy-path return values
- ❌ DO NOT set mock return values repeatedly in each test for happy paths
- ❌ DO NOT include unused mock functions just to satisfy type shape
- ❌ DO NOT add manual cleanup in beforeEach/afterEach
- ❌ DO NOT set system time inside individual tests (set at file level)
- ❌ DO NOT use `any` types in test code
- ❌ DO NOT use dynamic imports in tests
- ❌ DO NOT use mutable variables to control mock behavior
- ❌ DO NOT pass `undefined` fields to factory/mock overrides — omit them (or drop the arg entirely)
- ❌ DO NOT wrap simple constructors in arrow functions — use direct instantiation
- ❌ DO NOT create per-test instances unless the test mutates the instance — place at file or describe level by default
- ❌ DO NOT manually list each property/assignment in class mock constructors — use `Object.assign(this, mockObject)`
- ❌ DO NOT prefix mock variable names with `mock` — test context already signals these are test doubles
- ❌ DO NOT define custom interfaces for mock objects (e.g., `interface MockService`) — use `satisfies Partial<T>` with the real type
- ❌ DO NOT use `typeof import('...')` (module type) when validating mock instance methods — use `InstanceType<typeof import('...')['ClassName']>` or import the class type directly
- ❌ DO NOT leave data fixtures inside `vi.hoisted()` without `satisfies` — applies to ALL test doubles, not just `vi.fn()` wrappers

### Test Descriptions

```typescript
// ❌ VIOLATION: missing 'should' prefix
it('passes through MIME type', () => { ... });
it('returns empty array', () => { ... });
```

**See**: [Core Principles > TDD](#test-driven-development-tdd)

### Redundant Testing

```typescript
// ❌ VIOLATION: testing same logic with artificial variations
it('should calculate 10% discount for $100', () => {
  expect(calculateDiscount(100, 0.1)).toBe(90);
});
it('should calculate 10% discount for $200', () => {
  expect(calculateDiscount(200, 0.1)).toBe(180); // SAME LOGIC!
});
```

```typescript
// ❌ VIOLATION: constructor-only test — every other test already proves instantiation
it('should instantiate successfully', () => {
  const instance = new MyClass();
  expect(instance).toBeInstanceOf(MyClass);
});
```

**See**: [Core Principles > Minimal Testing](#minimal-testing-principle)

### Comments

```typescript
// ❌ VIOLATION: comment restates the obvious
expect(result.name).toBe('John'); // check that result has name

// ❌ VIOLATION: AAA section comments
// Arrange  <-- blank lines already show structure
const items = [...];
// Act  <-- remove these
const result = fn(items);
// Assert  <-- the structure is self-evident
expect(result).toBe(30);
```

**See**: [Test Structure > Comments](#comments-in-tests)

### Shared State

```typescript
// ❌ VIOLATION: mutable shared state
let service: UserService;
beforeEach(() => {
  service = new UserService(repo);
});
```

**See**: [Test Structure > Test Data Management](#test-data-management)

### Assertions

```typescript
// ❌ VIOLATION: checking fields one by one
expect(result.mime).toBe('application/octet-stream');
expect(result.size).toBe(0);
expect(result.lastModified).toBeInstanceOf(Date);

// ❌ VIOLATION: checking array elements one by one
expect(users[0].name).toBe('Alice');
expect(users[1].name).toBe('Bob');
```

**See**: [Test Structure > Assertions](#object-and-array-assertions)

### Mocking

```typescript
// ❌ VIOLATION: setting success return value inside it() block
it('should upload with different etag', () => {
  upload.mockResolvedValue({ etag: 'different-etag' });
  // ...
});

// ❌ VIOLATION: setting system time inside individual test
it('should format date correctly', () => {
  vi.setSystemTime(new Date('2025-01-01T00:00:00.000Z'));
  // ...
});

// ❌ VIOLATION: manual cleanup
afterEach(() => {
  vi.clearAllMocks();
  vi.unstubAllGlobals();
});
```

**See**: [Mocking Standards](#mocking-standards)

### Mock Setup

```typescript
// ❌ VIOLATION: combines both problems - no defaults and unused mocks, no use of `satisfies Type` or `satisfies Partial<Type>`
const { emailService } = vi.hoisted(() => ({
  emailService: {
    send: vi.fn(), // no default return!
    sendBatch: vi.fn(), // unused!
    verify: vi.fn(), // unused!
    getStatus: vi.fn(), // unused!
    scheduleDelivery: vi.fn(), // unused!
  },
}));
```

```typescript
// ❌ VIOLATION: data fixtures inside vi.hoisted() missing satisfies
const { source, display } = vi.hoisted(() => ({
  source: {
    id: 'screen:0',
    name: 'Entire Screen',
    display_id: '0',
  },
  display: {
    id: 0,
    bounds: { x: 0, y: 0, width: 1920, height: 1080 },
  },
}));

// ✅ CORRECT: all typed test doubles use satisfies
const { source, display } = vi.hoisted(() => ({
  source: {
    id: 'screen:0',
    name: 'Entire Screen',
    display_id: '0',
  } satisfies Partial<DesktopCapturerSource>,
  display: {
    id: 0,
    bounds: { x: 0, y: 0, width: 1920, height: 1080 },
  } satisfies Partial<Display>,
}));
```

**See**: [Mocking Standards](#mocking-standards)

### Mutable Mock State

```typescript
// ❌ VIOLATION: mutating external state to control mock behavior
mockScenario.existsReturnsFalse = true;
const result = await storage.exists('any-path.txt');
mockScenario.existsReturnsFalse = false;
```

**CORRECT**: Mock behavior should be based on **input parameters**

```typescript
// ✅ RIGHT: behavior depends on input
exists: vi.fn(async (path: string) => {
  if (path.includes('/missing/')) return false;
  return true;
}),

// In test - path controls behavior
const result = await storage.exists('bucket/missing/file.txt');
expect(result).toBe(false);
```

**Why**:

- Input-based mocks are self-documenting (the test path explains the scenario)
- No cleanup required (no state to reset)
- Test isolation guaranteed
- Easier to debug

**See**: [Mocking Standards](#mocking-standards)

### Critical (Immediate Rejection)

| Violation                  | Example                                 |
| -------------------------- | --------------------------------------- |
| Mathematical variations    | Testing calculateTax with $10, $20, $30 |
| Wrapper testing            | Only verifying mock was called          |
| Artificial data variations | Valid emails with different names       |
| Any types in tests         | `const mockService: any = {}`           |
| Testing implementation     | Spying on useState                      |
| Dynamic imports            | `await import('#module')`               |
| Constructor-only assertion | `expect(x).toBeInstanceOf(Cls)` with no behavior test |

**See**: [Core Principles > Minimal Testing](#minimal-testing-principle)

## Core Principles

### TypeScript Compliance

<IMPORTANT>
Testing code inherits all project TypeScript requirements:

- **No `any` types** - Use specific types for complete type safety
- **Strict type checking** - All mocks, fixtures, and test utilities must be properly typed
- **Type-safe assertions** - Ensure all expectations are type-safe
- **Proper imports** - Separate code and type imports
</IMPORTANT>

```typescript
// ❌ VIOLATION: using any types bypasses typescript safety
const mockRepo: any = {
  save: vi.fn(),
  findById: vi.fn(),
};
```

### Test-Driven Development (TDD)

- **Test Before Code** - Write type-safe tests before implementing code
- **Follow TDD cycle** - Red → Green → Refactor with TypeScript checking at each step
- **BDD style descriptions** - Use 'should [expected behavior]' format

<IMPORTANT>
**All test descriptions MUST start with 'should'** - This is non-negotiable BDD format.

```typescript
// ✅ CORRECT: starts with 'should'
it('should pass through MIME type', () => { ... });
it('should return empty array', () => { ... });
it('should handle null input', () => { ... });
```

</IMPORTANT>

### Minimal Testing Principle

<IMPORTANT>
**Every test must add unique value. Redundant tests are maintenance debt.**

- **100% coverage with ABSOLUTE MINIMUM tests** - One test per unique behavior path
- Exclude barrel files (`index.ts`) and pure type files (`types.ts`) by placing `/* v8 ignore file */` at the top of the file
- Every test must verify: different code path, different behavior, OR real edge case
</IMPORTANT>

```typescript
// ✅ CORRECT: one test per unique behavior
describe('fn:calculateDiscount', () => {
  it('should apply percentage discount correctly', () => {
    expect(calculateDiscount(100, 0.1)).toBe(90);
  });
  it('should handle zero discount', () => {
    expect(calculateDiscount(100, 0)).toBe(100);
  });
  it('should throw for negative amounts', () => {
    expect(() => calculateDiscount(-100, 0.1)).toThrow();
  });
});
```

## Test File Structure

### File Naming

- Unit tests: `*.spec.ts` or `*.spec.tsx`
- Integration tests: `*.int.spec.ts`
- End-to-end tests: `*.e2e.spec.ts`

**Test Isolation**: Unit tests (`.spec.ts`) must be fully isolated. Use mocks for databases, APIs, and services. Integration tests (`.int.spec.ts`) may use real internal dependencies and external services. **Mocking is NOT allowed in integration tests** - they must exercise real code paths.

### Test Description Prefixes

| Prefix | Usage                       |
| ------ | --------------------------- |
| `fn:`  | Functions                   |
| `sv:`  | Services                    |
| `op:`  | Operations                  |
| `cl:`  | Classes                     |
| `mt:`  | Class methods               |
| `gt:`  | Class getters               |
| `st:`  | Class setters               |
| `ty:`  | Utility types or interfaces |
| `rc:`  | React components            |
| `hk:`  | React hooks                 |

For general-purpose tests, use clear natural-language descriptions without prefixes.

### Import Organization

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { UserService } from '#services/user';

import type { User } from '#types/user';
```

### Test Double Organization

```text
spec/
├── mocks/           # shared mocks across test files
├── fixtures/        # shared test data
└── utilities/       # test utilities and setup
```

- **Inline**: Place at top of test file when only used in that file
- **Shared**: Place in `spec/mocks` or `spec/fixtures` when reused
- **Clean naming**: Use `const user = ...` not `const mockUser = ...` - test context makes it clear these are test doubles

### Section Headers (for complex test files)

Use standardized headers for files with setup areas before describe blocks:

```typescript
// TYPES //
// MOCKS //
// CONSTANTS //
// HELPERS //
// TEST SUITES //
```

```typescript
// ❌ VIOLATION: inconsistent header format and missing sections
import { describe, it, expect, vi } from 'vitest';

// mocks  <-- lowercase like comment, inconsistent format as a section header
const { fetchUser } = vi.hoisted(() => ({
  fetchUser: vi.fn(),
}));

const VALID_USER = { name: 'John' };
// missing section header for constants
```

## Test Structure

### Arrange-Act-Assert Pattern

<IMPORTANT>
All tests must follow AAA with proper spacing. **A line space is required between each section.**
</IMPORTANT>

```typescript
describe('fn:formatCurrency', () => {
  it('should format number as USD currency', () => {
    const amount = 1234.56;
    const currency: CurrencyCode = 'USD';
    const expected = '$1,234.56';

    const result = formatCurrency(amount, currency);

    expect(result).toBe(expected);
  });
});
```

```typescript
// ❌ VIOLATION: unclear structure without AAA spacing
describe('fn:formatCurrency', () => {
  it('should format currency', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });
});
```

### Comments in Tests

Explanatory comments are valuable when they clarify non-obvious test behavior. Follow documentation standards for comment formatting (lowercase, explain 'why' not 'what').

**JSDoc for test helpers and factories must also follow documentation standards** - use lowercase for descriptions.

```typescript
// ✅ CORRECT: explains non-obvious assertion reasoning
it('should handle partial completion', async () => {
  await startOperations();
  await waitForFirstPhase();

  // copy should have completed, but delete should not
  expect(copyResult.status).toBe('complete');
  expect(deleteResult.status).toBe('pending');
});

// ✅ CORRECT: clarifies timing expectations
it('should debounce rapid calls', async () => {
  trigger();
  trigger();
  trigger();

  // only the last call should execute after debounce window
  await vi.advanceTimersByTimeAsync(300);
  expect(handler).toHaveBeenCalledTimes(1);
});
```

### Test Data Management

Use `const` for immutable test data. Place class instances at file or describe level by default. Only create a per-test instance when the test itself will mutate the instance (e.g., calling setters, modifying internal state). Since Vitest auto-resets mocks, mock dependencies are always fresh between tests — there is no need to recreate the instance for mock isolation.

```typescript
// ✅ CORRECT: fresh instances per test
describe('cl:UserService', () => {
  it('should create user with valid data', () => {
    const repository = createMockUserRepository();
    const service = new UserService(repository);
    // ...
  });
});
```

```typescript
// ❌ VIOLATION: mutable shared state with let
describe('fn:processUser', () => {
  let userData = {
    id: '123',
    name: 'John Doe',
    email: 'john@example.com',
  };

  it('should validate user email format', () => {
    userData.email = 'test@example.com'; // mutating shared data
    const result = processUser(userData);
    expect(result.isValid).toBe(true);
  });
});
```

**Instance Placement (default: file-level):**

```typescript
// ✅ DEFAULT: file-level instance — dependencies are auto-reset by Vitest
const screenCapture = new ScreenCapture();

describe('cl:ScreenCapture', () => {
  it('should capture screenshot of primary display', async () => {
    const result = await screenCapture.captureScreen();

    expect(result).toBe('base64-encoded-webp-string');
  });

  it('should throw when capture fails', async () => {
    getSources.mockRejectedValueOnce(new Error('Capture failed'));

    await expect(screenCapture.captureScreen()).rejects.toThrow(ApplicationError);
  });
});
```

```typescript
// ❌ VIOLATION: per-test creation when the test doesn't mutate the instance
describe('cl:ScreenCapture', () => {
  it('should capture screenshot', async () => {
    const screenCapture = new ScreenCapture();
    // ...
  });
  it('should throw when capture fails', async () => {
    const screenCapture = new ScreenCapture(); // redundant — no mutation
    // ...
  });
});
```

**When per-test instances ARE needed:**
- The test mutates the instance itself (e.g., calling setters, changing internal state)
- Constructor takes different arguments per test

```typescript
// ✅ CORRECT: per-test because constructor args vary
it('should use custom config', () => {
  const service = new Service({ timeout: 5000 });
  // ...
});
it('should use default config', () => {
  const service = new Service({ timeout: 30000 });
  // ...
});
```

### Assertion Preferences

- **`.toBe()`** for primitives and reference identity
- **`.toEqual()`** for deep comparisons (objects, arrays)
- **Inline throwing**: `expect(() => fn()).toThrow()`
- **Single assertion per structure**: Don't check fields one by one

### Object and Array Assertions

<IMPORTANT>
When asserting on objects or arrays, use a single assertion that validates the entire structure. Do NOT check individual fields or elements one by one.
</IMPORTANT>

**Object Assertions:**

```typescript
// ✅ CORRECT: single assertion with full object
expect(result).toEqual({
  mime: 'application/octet-stream',
  size: 0,
  lastModified: expect.any(Date),
});

// ✅ CORRECT: partial matching when only some fields matter
expect(result).toEqual(
  expect.objectContaining({
    mime: 'application/octet-stream',
    size: expect.any(Number),
  }),
);
```

**Array Assertions:**

```typescript
// ✅ CORRECT: single assertion with full array
expect(users).toEqual([
  { name: 'Alice', email: 'alice@example.com' },
  { name: 'Bob', email: 'bob@example.com' },
]);

// ✅ CORRECT: array with dynamic values
expect(users).toEqual([
  expect.objectContaining({ name: 'Alice' }),
  expect.objectContaining({ name: 'Bob' }),
]);
```

## Mocking Standards

### When to Mock

<IMPORTANT>
**Only mock when the dependency involves:**
1. **IO Operations** - File system, network, database
2. **External Services** - Third-party APIs, cloud services
3. **Behavior Control** - Time/dates, random values, specific error scenarios

**For all other cases, use the real implementation.**
</IMPORTANT>

| Dependency Type             | Mock? | Reason                      |
| --------------------------- | ----- | --------------------------- |
| Database queries            | Yes   | IO, side effects            |
| HTTP/API calls              | Yes   | IO, external service        |
| File system                 | Yes   | IO                          |
| Date/time                   | Yes   | Behavior control            |
| Pure utility functions      | No    | No side effects             |
| Internal business logic     | No    | Part of what you're testing |
| Simple data transformations | No    | Deterministic               |

```typescript
// ❌ VIOLATION: unnecessary mock for pure function
const { formatCurrency } = vi.hoisted(() => ({
  formatCurrency: vi.fn(() => '$90.00'),
}));
// pure functions have no side effects - use real implementation
```

### Module Mocking Patterns

#### Happy Path vs Error Path Mocking

<IMPORTANT>
**Happy path return values MUST be defined inside `vi.mock() or vi.hoisted`**.

Use `vi.hoisted()` ONLY when you need to:

1. **Spy on calls** - Verify mock was called with specific arguments
2. **Throw errors** - Test error handling paths

If you only need the mock to return success data and don't need to inspect calls or throw errors, put everything inside `vi.mock()`:
</IMPORTANT>

```typescript
// ✅ CORRECT: happy path mock defined directly in vi.mock()
vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceClient: class {
        getContainerClient() {
          return {
            getBlockBlobClient: () => ({
              upload: vi.fn(async () => ({ etag: 'etag' })),
              exists: vi.fn(async () => true),
            }),
          };
        }
      },
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);
```

#### Mock Pattern Decision Guide

| Need                           | Pattern    | Location of Mock Returns                          |
| ------------------------------ | ---------- | ------------------------------------------------- |
| Just need mock to return data  | Default    | Inside `vi.mock()` factory                        |
| Need to verify mock was called | vi.hoisted | vi.hoisted, then reference in vi.mock             |
| Need to test error paths       | vi.hoisted | vi.hoisted with mockRejectedValue                 |
| Need both happy path AND spy   | vi.hoisted | vi.hoisted for spied fn, happy returns in factory |

**Default Pattern** - Nest all mock code directly inside `vi.mock()`:

```typescript
vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceClient: class {
        getContainerClient() {
          return {
            getBlockBlobClient: () => ({
              upload: vi.fn(async () => ({ etag: 'etag' })),
              exists: vi.fn(async () => true),
            }),
          };
        }
      },
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);
```

**vi.hoisted Pattern** - ONLY when spying on calls or testing error paths:

<IMPORTANT>
**All mocks MUST define default happy-path return values with `satisfies Type` or `satisfies Partial<Type>`**

This applies to ALL typed test doubles inside `vi.hoisted()` — not just mock functions (`vi.fn()`), but also data fixtures representing external types (e.g., Electron's `DesktopCapturerSource`, `Display`, `NativeImage`).

Use `vi.hoisted()` ONLY when you need to:

1. **Spy on calls** - Verify mock was called with specific arguments
2. **Test error paths** - ONLY `mockRejectedValue()` or throwing

**Setting `.mockResolvedValue()` or `.mockReturnValue()` inside `it()` blocks for happy paths is FORBIDDEN.**

If you find yourself calling `.mockResolvedValue()` in multiple tests with similar success data, you're missing a default - fix the mock definition instead.
</IMPORTANT>

```typescript
import type { BlockBlobClient } from '@azure/storage-blob';

// MOCKS //

const { upload } = vi.hoisted(() => ({
  upload: vi.fn(async () => ({ etag: 'etag' })),
}) satisfies Partial<BlockBlobClient>);

vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceClient: class {
        getContainerClient = () => ({
          getBlockBlobClient: () =>
            ({ upload }) satisfies Partial<BlockBlobClient>,
        });
      },
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);

// TEST SUITES //

describe('fn:uploadToStorage', () => {
  // ✅ ALLOWED: Spying on calls
  it('should upload with correct params', async () => {
    await uploadToStorage('test.txt', Buffer.from('data'));

    expect(upload).toHaveBeenCalledWith(
      expect.any(Buffer),
      expect.any(Number),
    );
  });

  // ✅ ALLOWED: Error path testing
  it('should handle upload failure', async () => {
    upload.mockRejectedValue(new Error('Network error'));

    await expect(
      uploadToStorage('test.txt', Buffer.from('data')),
    ).rejects.toThrow('Network error');
  });
});
```

#### vi.hoisted Type Alternatives

When using `vi.hoisted()`, you have two options for typing mock objects:

- **Explicit type import**: Use when the type is needed elsewhere in the test file
- **Inline type extraction**: Use `typeof import('...')['Type']` when the type is only needed for the mock

```typescript
// ✅ CORRECT: type imported explicitly (preferred when type used elsewhere)
import type { BlockBlobClient } from '@azure/storage-blob';

const { upload } = vi.hoisted(() => ({
  upload: vi.fn(async () => ({ etag: 'etag' })),
}) satisfies Partial<BlockBlobClient>);

// ✅ CORRECT: inline type extraction (when type not needed elsewhere)
const { upload } = vi.hoisted(() => ({
  upload: vi.fn(async () => ({ etag: 'etag' })),
}) satisfies Partial<typeof import('@azure/storage-blob')['BlockBlobClient']>);
```

### Mock Setup Decision Guide

When creating a mock, ask these questions:

1. **Will this method be called in tests?**
   - No → Don't include it (use `satisfies Partial<T>`)
   - Yes → Continue to question 2

2. **Do tests need to spy on calls or test error paths?**
   - No → Put mock directly in `vi.mock()` factory with default return
   - Yes → Use `vi.hoisted()` with default return value

3. **What return value should it have?**
   - Define a sensible happy-path default
   - Tests should NOT need to call `.mockResolvedValue()` for normal behavior
   - Only error tests override with `.mockRejectedValue()`

### Signs You're Violating Mock Standards

❌ **You're setting the same `.mockResolvedValue()` in multiple tests**
→ Define a default in `vi.hoisted()` or `vi.mock()`

❌ **You have `vi.fn()` with chained `.mockResolvedValue()` or `.mockReturnValue()`**
→ Either add a default return, or remove if unused

❌ **Your mock object has more than 3-4 methods**
→ Likely mocking unused methods; use `satisfies Partial<T>`

❌ **You're copying mock setup between test files**
→ Move shared mocks to `spec/mocks/` with proper defaults

❌ **You're using mutable variables to control mock behavior**
→ Use input-based mock logic instead (path patterns, argument values)

❌ **You're defining a custom interface for your mock (e.g., `interface MockBrowserWindow`)**
→ Use `satisfies Partial<BrowserWindow>` instead — the real type is the source of truth

### Shared Mock Extraction

When the same class is mocked in 3+ test files, extract a canonical mock to `spec/mocks/`:

```typescript
// spec/mocks/logger.ts
export const logger = {
  debug: vi.fn(),
  info: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
} satisfies Partial<Logger>;
```

Each test file imports and can spy or override error paths as needed. This prevents divergent mock definitions across files.

### Module Mocking Strategies

**Partial Module Mocking** - When you only need specific exports:

```typescript
vi.mock(
  '@theriety/config',
  () =>
    ({
      getValidatedServiceConfig,
    }) satisfies Partial<typeof import('@theriety/config')>,
);
```

**Full Module Override with importActual** - When preserving real exports:

```typescript
vi.mock(
  '@theriety/message',
  async (importActual) =>
    ({
      ...(await importActual<typeof import('@theriety/message')>()),
      createInvoker,
    }) satisfies typeof import('@theriety/message'),
);
```

### Type Safety Patterns

All mocks must use the `satisfies` pattern for compile-time validation:

| Pattern                                              | Usage                                               |
| ---------------------------------------------------- | --------------------------------------------------- |
| `satisfies Partial<Type>`                                      | Mock objects implementing interface (type imported)            |
| `satisfies Partial<typeof import('...')['Type']>`              | Mock objects when type not imported elsewhere                  |
| `satisfies Partial<typeof import('...')>`                      | Partial module mocks in vi.mock()                             |
| `satisfies typeof import('...')`                               | Full module mocks with importActual                           |
| `vi.fn<[Params], Return>()`                                    | Explicit function signatures                                  |
| `satisfies Partial<InstanceType<typeof import('...')['Cls']>>` | Hoisted mock objects for class instance methods               |
| `satisfies Constructor<Partial<Cls>>`                          | Mock classes in vi.mock (import `Constructor` from type-fest) |
| `satisfies Partial<Type>` (on data fixtures)                   | Typed test data in vi.hoisted (e.g., fake `Display`, `Source`) |

**Class type disambiguation** — when a module exports a class, these three expressions resolve differently:

| Expression                                    | Resolves To          | Use For                                           |
| --------------------------------------------- | -------------------- | ------------------------------------------------- |
| `typeof import('#m')`                         | `{ Cls: typeof Cls }` | Module-level `satisfies` in vi.mock return        |
| `typeof import('#m')['Cls']`                  | `new () => Cls`      | Constructor type comparison                       |
| `InstanceType<typeof import('#m')['Cls']>`    | `Cls`                | Hoisted mock objects, `Constructor<Partial<...>>` |

**Triple Pattern for Partial Results** - Use when returning incomplete mock data that must satisfy a full type. The `satisfies Partial<T> as Partial<T> as T` chain validates structure while allowing incomplete data:

```typescript
vi.mock(
  '#user',
  () =>
    ({
      createUserResolver: vi.fn(
        () =>
          ({
            id: 'user-id',
            status: 'active' as const,
          }) satisfies Partial<UserDetails> as Partial<UserDetails> as UserDetails,
      ),
    }) satisfies Partial<typeof import('#user')>,
);
```

### Class Mocking Pattern

Use constructor hijacking with `Object.assign` to return pre-defined mock instances.

<IMPORTANT>
**When mocking classes with instance methods, use `Object.assign(this, mockObject)` in the constructor** instead of manually declaring types and assigning each property. This eliminates the triple-repetition of every method name (hoisted definition, type declaration, constructor assignment).
</IMPORTANT>

**Instance method mocking** — when the class under test creates instances with methods:

```typescript
import type { Constructor } from 'type-fest';

import type { Encoder } from '#encoder';

// MOCKS //

const { encoder } = vi.hoisted(() => ({
  encoder: {
    encode: vi.fn(async () => Buffer.from('encoded')),
    decode: vi.fn(async () => Buffer.from('decoded')),
  } satisfies Partial<Encoder>,
}));

vi.mock('#encoder', () => ({
  Encoder: class {
    constructor() {
      Object.assign(this, encoder);
    }
  } satisfies Constructor<Partial<Encoder>>,
}));
```

When the type is only needed for the mock (not imported elsewhere), use inline type extraction:

```typescript
const { encoder } = vi.hoisted(() => ({
  encoder: {
    encode: vi.fn(async () => Buffer.from('encoded')),
    decode: vi.fn(async () => Buffer.from('decoded')),
  } satisfies Partial<InstanceType<typeof import('#encoder')['Encoder']>>,
}));

vi.mock('#encoder', () => ({
  Encoder: class {
    constructor() {
      Object.assign(this, encoder);
    }
  } satisfies Constructor<Partial<InstanceType<typeof import('#encoder')['Encoder']>>>,
}));
```

```typescript
// ❌ VIOLATION: manually listing every method — scales O(n) with method count
vi.mock('#encoder', () => ({
  Encoder: class {
    public encode: typeof encoder.encode;
    public decode: typeof encoder.decode;

    constructor() {
      this.encode = encoder.encode;
      this.decode = encoder.decode;
    }
  },
}));

// ❌ VIOLATION: using module type for instance mock
const { encoder } = vi.hoisted(() => ({
  encoder: {
    encode: vi.fn(),
  } satisfies Partial<typeof import('#encoder')>,
  // typeof import(...) is { Encoder: typeof Encoder }, not the instance type
}));
```

**Return-value hijacking** — when the mock class delegates to pre-defined mock objects via methods:

```typescript
const { blobClient } = vi.hoisted(() => ({
  blobClient: {
    upload: vi.fn(),
    download: vi.fn(),
  } satisfies Partial<BlobClient>,
}));

vi.mock(
  '@azure/storage-blob',
  async (importActual) =>
    ({
      ...(await importActual<typeof import('@azure/storage-blob')>()),
      // @ts-expect-error mocking class with #private fields
      BlobServiceClient: class BlobServiceClient
        implements Partial<BlobServiceClient>
      {
        getContainerClient() {
          return { getBlockBlobClient: () => blobClient };
        }
      },
    }) satisfies typeof import('@azure/storage-blob'),
);
```

**Never use**: `as unknown as typeof Class` — bypasses type checking.

```typescript
// ❌ VIOLATION: double assertion bypasses type safety
const blobClient = {} as unknown as BlobClient;
// this compiles but provides zero type checking
```

### Mock Cleanup Configuration

Configure Vitest for automatic cleanup. **Never use manual cleanup in hooks.**

```typescript
// vitest.config.ts - REQUIRED
export default defineConfig({
  test: {
    mockReset: true,
    clearMocks: true,
    restoreMocks: true,
    unstubEnvs: true,
    unstubGlobals: true,
  },
});
```

<IMPORTANT>
With proper Vitest configuration, **NEVER add manual cleanup in beforeEach/afterEach**. Let Vitest handle cleanup automatically via config.
</IMPORTANT>

### Stubbing Globals and Environment Variables

Use `vi.stubGlobal` and `vi.stubEnv` for global/environment stubs:

```typescript
describe('fn:getApiUrl', () => {
  it('should use custom API URL from environment', () => {
    vi.stubEnv('API_URL', 'https://custom.api.com');

    const result = getApiUrl();

    expect(result).toBe('https://custom.api.com');
  });

  it('should handle missing fetch global', () => {
    vi.stubGlobal('fetch', undefined);

    expect(() => makeRequest()).toThrow('fetch is not available');
  });
});
```

**Note**: With `unstubEnvs: true` and `unstubGlobals: true` in config, stubs are automatically restored after each test.

### Default Mock Behavior

Define sensible defaults with conditional logic. Override only for exception testing:

```typescript
const { getConfig } = vi.hoisted(() => ({
  getConfig: vi.fn((url: string): ServiceConfig => {
    switch (url) {
      case 'provider://full/path':
        return { cache: { type: 'disabled' } };
      default:
        throw new Error(`missing mocked url: ${url}`);
    }
  }),
}));

// In tests: only override for error paths
it('should handle config fetch failure', async () => {
  getConfig.mockRejectedValue(new Error('Network error'));
  await expect(processConfig('any')).rejects.toThrow('Network error');
});
```

## Factory Functions

Factory functions add complexity and must justify their existence:

- **No zero-parameter factories or constructor wrappers** - Use `const` for data, direct instantiation for classes
- **Must be called with different parameters** - If always same params, use `const`
- **Date.now() doesn't justify a factory** - Freeze time with `vi.setSystemTime()`
- **Use const arrow function syntax** when justified

```typescript
// ✅ CORRECT: factory with meaningful variations
const createUser = (overrides?: Partial<User>): User => ({
  id: `user-${Date.now()}`,
  email: 'test@example.com',
  name: 'Test User',
  ...overrides,
});

// Usage justifies existence:
const adminUser = createUser({ role: 'admin' });
const regularUser = createUser({ role: 'user' });
```

```typescript
// ❌ VIOLATION: zero-parameter factory
const createDefaultUser = () => ({
  id: 'user-1',
  name: 'John',
  email: 'john@example.com',
});
// use const DEFAULT_USER = { ... } instead

// ❌ VIOLATION: factory always called without parameters
createUser(); // if always called this way, use const

// ❌ VIOLATION: Date.now() doesn't justify factory
const createTimestampedUser = () => ({
  id: `user-${Date.now()}`,
  name: 'Test',
});
// use vi.setSystemTime() for deterministic tests instead

// ❌ VIOLATION: wrapping constructor in arrow function
const createScreenCapture = () => new ScreenCapture();
// use `const screenCapture = new ScreenCapture()` instead

// ❌ VIOLATION: passing undefined to factory overrides
const session = createMockSession({
  expires_at: undefined as unknown as number,
});
// omit undefined fields — or drop the arg if it becomes empty:
const session = createMockSession();
```

## Coverage Standards

### Requirements

<IMPORTANT>
- **100% line coverage** (excluding barrel and type files)
- **100% branch coverage** for critical paths
- Write tests ONE AT A TIME with coverage verification after each
- If a test adds ZERO coverage improvement, DELETE IT immediately
</IMPORTANT>

### Coverage-Driven Workflow

1. **Run coverage FIRST** to identify uncovered lines
2. **Write ONE test** targeting an uncovered line/branch
3. **Run coverage again** to verify improvement
4. **Keep or delete**: Coverage increased → keep; Same → delete immediately
5. **Repeat** for next uncovered line

```bash
vitest --coverage spec/path/to/file.spec.ts
```

### Configuration

```typescript
// vitest.config.ts
{
  coverage: {
    provider: 'v8',
    thresholds: {
      global: { branches: 100, functions: 100, lines: 100, statements: 100 }
    }
  }
}
```

## Error Testing

```typescript
describe('fn:validateUser', () => {
  it('should throw ValidationError for invalid email', () => {
    const invalidUser = { name: 'John', email: 'invalid-email' };
    expect(() => validateUser(invalidUser)).toThrow('Invalid email format');
  });
});

// Async error testing
await expect(fetchUserData('nonexistent')).rejects.toThrow('User not found');
```

## Performance Guidelines

- **Fast execution** - Unit tests should run in milliseconds
- **Isolated tests** - No dependencies between tests
- **Minimal setup** - Avoid complex test fixtures
- **Parallel execution** - Tests should be parallelizable

## Quick Reference

| Test Type   | File Pattern    | Purpose                       |
| ----------- | --------------- | ----------------------------- |
| Unit        | `*.spec.ts`     | Isolated component testing    |
| Integration | `*.int.spec.ts` | Component interaction testing |
| E2E         | `*.e2e.spec.ts` | Full system testing           |
