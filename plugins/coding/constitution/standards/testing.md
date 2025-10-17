# Testing Standards

_Comprehensive testing standards for quality assurance, TDD compliance, and TypeScript type safety_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- TypeScript Standards (standard:typescript) - Tests must follow TypeScript type safety requirements and use proper typing throughout
- General Coding Principles (standard:general-principles) - Test code must adhere to fundamental coding principles and consistency rules
- Naming Standards (standard:naming) - Test functions must follow function naming, structure, and documentation standards
- Documentation Standards (standard:documentation) - Test interfaces and complex test scenarios require proper JSDoc documentation

## Core Principles

### TypeScript Standards Compliance

<IMPORTANT>
Testing code inherits all project TypeScript requirements. You MUST read the [Typescript Standard](./typescript.md) together with this document.

- **No `any` types** - Use specific types for complete type safety
- **Strict type checking** - All mocks, fixtures, and test utilities must be properly typed
- **Type-safe assertions** - Ensure all expectations are type-safe and provide meaningful error messages
- **Proper imports** - Follow TypeScript import standards including separation of code and type imports
- **Interface documentation** - All test interfaces must be fully documented with JSDoc comments
</IMPORTANT>

```typescript
// ✅ GOOD: type-safe test with proper typescript compliance
import { describe, it, expect, vi } from 'vitest';

import type { User } from '#types/user';

vi.mock('#user', (): UserRepository => ({
    save: vi.fn(),
    findById: vi.fn(),
    findAll: vi.fn(),
  }) satisfies Partial<typeof import ('#repositories/user)>
);

// ❌ BAD: using any types bypasses typescript safety
const mockRepo: any = {
  save: vi.fn(),
  findById: vi.fn(),
};
```

### Test-Driven Development (TDD)

All new code must follow TDD principles with complete TypeScript compliance:

- **Test Before Code** - Write type-safe tests for expected behaviors before implementing code
- **Follow TDD cycle** - Red → Green → Refactor with TypeScript checking at each step
- **BDD style descriptions** - Use "should [expected behavior]" format
- **Type safety first** - Ensure tests catch type errors before runtime

### Quality and Coverage

<IMPORTANT>
Maintain high quality standards while ensuring complete type safety:

## 🚨 CRITICAL: Absolute Minimal Testing Principle

**Every test must add unique value. Redundant tests are maintenance debt.**

- **100% coverage with ABSOLUTE MINIMUM tests** - One test per unique behavior path
  - Maintain **100%** coverage, excluding barrel files (typically `index.ts`) and pure type files (ususally `types.ts`)
  - Use `/* v8 ignore start */` at the top of any barrel and type files to exclude them from coverage reports and signal no test is needed
- **BAD: Artificial scenario variations** - No testing same logic with different fake data
- **BAD: Redundant edge cases** - If logic is identical, one test is enough
- **Maximize test reuse** - Parameterized tests over copy-paste variations
- **Ignore lines marked with v8 ignore** - No need to create any tests for lines meant to be ignore from coverage
- Every test must verify at least one of:
  - **Different code path**: Conditional branches, error handling
  - **Different behavior**: Not just different inputs producing predictable outputs
  - **Real edge case**: Actual boundary conditions, not artificial scenarios
</IMPORTANT>

#### Zero Redundancy Rule

```typescript
// ❌ BAD: testing same logic with artificial variations
describe("fn:calculateDiscount", () => {
  it("should calculate 10% discount for $100", () => {
    expect(calculateDiscount(100, 0.1)).toBe(90);
  });
  
  it("should calculate 10% discount for $200", () => {
    expect(calculateDiscount(200, 0.1)).toBe(180);
  });
  
  it("should calculate 10% discount for $300", () => {
    expect(calculateDiscount(300, 0.1)).toBe(270);
  });
  // STOP! same logic, different numbers = WASTE
});

// ✅ GOOD: one test per unique behavior
describe("fn:calculateDiscount", () => {
  it("should apply percentage discount correctly", () => {
    expect(calculateDiscount(100, 0.1)).toBe(90);
  });
  
  it("should handle zero discount", () => {
    expect(calculateDiscount(100, 0)).toBe(100);
  });
  
  it("should throw for negative amounts", () => {
    expect(() => calculateDiscount(-100, 0.1)).toThrow();
  });
  // each test verifies DIFFERENT behavior
});
```

#### Coverage-Driven Test Development Workflow

<IMPORTANT>
**Coverage-First Approach**: Before writing ANY test, run coverage to identify which lines and branches are uncovered. Only add tests that touch previously uncovered code. The coverage report is your guide - it shows exactly which lines (red/uncovered) need tests and which lines (green/covered) are already tested.

Run coverage FIRST to reveal uncovered positions:

```bash
# Identify what needs testing
vitest --coverage spec/path/to/file.spec.ts
```

The coverage report shows:

- **Uncovered lines** (typically shown in red): Need tests
- **Covered lines** (typically shown in green): Already tested, no additional tests needed
- **Branch indicators**: Show which conditional paths (if/else, switch, ternary) need coverage
</IMPORTANT>

<IMPORTANT>
Tests MUST be written one at a time with mandatory coverage verification after each test. If a test adds ZERO coverage improvement, it MUST be removed immediately. This ensures every test adds unique value.
</IMPORTANT>

<IMPORTANT>
**MINIMAL TESTING PRINCIPLE**: Write the SMALLEST number of tests that achieve 100% coverage. Every test must justify its existence by adding measurable coverage. More tests = more maintenance cost without additional value.
</IMPORTANT>

**Required Workflow:**

1. **Run coverage FIRST** (if starting new test file or continuing):

   ```bash
   # Identify uncovered lines and branches
   vitest --coverage spec/adapters/azure.spec.ts
   ```

   Review the report to see which lines/branches need tests

2. **Write ONE test** targeting an uncovered line or branch (following AAA pattern)

3. **Run coverage verification** again:

   ```bash
   # Per-file coverage verification (preferred during development)
   vitest --coverage spec/adapters/azure.spec.ts

   # Alternative using npm script
   npm run coverage -- spec/adapters/azure.spec.ts
   ```

4. **Verify coverage improvement**:
   - Check that line/branch coverage increased
   - Confirm the previously uncovered line is now covered
   - If coverage increased → Keep test and continue
   - If coverage stayed the same → **DELETE the test immediately**

5. **Repeat** for next uncovered line/branch

**Example Workflow:**

```typescript
// Step 0: Run coverage FIRST to identify what needs testing
// $ vitest --coverage spec/utils/validate.spec.ts
// Coverage: Lines 60% (12/20), Branches 50% (2/4)
// Report shows: Lines 15-18 uncovered (email validation), Lines 22-25 uncovered (error handling)

// Step 1: Write first test targeting uncovered lines 15-18
describe("fn:validateEmail", () => {
  it("should accept valid email format", () => {
    expect(validateEmail("user@example.com")).toBe(true);
  });
});

// Step 2: Run coverage to verify
// $ vitest --coverage spec/utils/validate.spec.ts
// Coverage: Lines 85% (17/20), Branches 75% (3/4)
// Lines 15-18 now covered ✅

// Step 3: Verify - coverage increased from 60% to 85% ✅ Keep test

// Step 4: Attempt second test (targeting same logic with different input - BAD)
describe("fn:validateEmail", () => {
  it("should accept valid email format", () => {
    expect(validateEmail("user@example.com")).toBe(true);
  });

  it("should also accept another valid email", () => {
    expect(validateEmail("another@example.com")).toBe(true);
  });
});

// Step 5: Run coverage
// $ vitest --coverage spec/utils/validate.spec.ts
// Coverage: Lines 85% (17/20), Branches 75% (3/4)
// Same as before - no new lines covered!

// Step 6: Verify - NO coverage improvement ❌ DELETE second test immediately

// Step 7: Check coverage report for remaining uncovered lines
// Report shows: Lines 22-25 still uncovered (error handling branch)

// Step 8: Write meaningful test targeting uncovered lines 22-25
describe("fn:validateEmail", () => {
  it("should accept valid email format", () => {
    expect(validateEmail("user@example.com")).toBe(true);
  });

  it("should reject missing @ symbol", () => {
    expect(validateEmail("userexample.com")).toBe(false);
  });
});

// Step 9: Run coverage
// $ vitest --coverage spec/utils/validate.spec.ts
// Coverage: Lines 90% (18/20), Branches 100% (4/4)
// Lines 22-25 now covered ✅

// Step 10: Verify - coverage increased from 85% to 90%, branches 75% to 100% ✅ Keep test

// Step 11: Check coverage report - Lines 28-29 still uncovered, continue with next test...
```

**Test Removal Criteria:**

```typescript
// ❌ DELETE: Test adds zero coverage
it("should calculate tax for $100", () => {
  expect(calculateTax(100)).toBe(10);
});
it("should calculate tax for $200", () => {
  // Same code path, different number - DELETE THIS
  expect(calculateTax(200)).toBe(20);
});

// ✅ KEEP: Test adds new coverage
it("should calculate tax for positive amount", () => {
  expect(calculateTax(100)).toBe(10);
});
it("should throw for negative amount", () => {
  // Different code path (error handling) - KEEP THIS
  expect(() => calculateTax(-100)).toThrow();
});
```

### TypeScript Testing Patterns

<IMPORTANT>
Follow these TypeScript-specific testing patterns:

- **Use `const` over `let`** - Create fresh instances per test instead of reassigning variables
- **Avoid `beforeEach`** - Keep tests self-contained when possible, use factory functions for complex setups
- **Never use dynamic imports** - Always use static imports at module level, no `await import()` in tests
- **Avoid over-mocking** - Use real implementations for simple logic, only mock external dependencies with side effects
- **Test outcomes, not mocks** - Focus on business logic and results, not mock call verification
- **Type-safe mock creation** - All mocks must implement proper TypeScript interfaces
</IMPORTANT>

## Testing Framework

### Required Framework

**Vitest** is our testing framework of choice. All projects must use Vitest for unit and integration testing.

### TypeScript Configuration for Testing

Ensure your Vitest configuration supports TypeScript standards:

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    mockReset: true,
    clearMocks: true,
    restoreMocks: true,
    typecheck: {
      checker: 'tsc',
      include: ['**/*.{test,spec}.ts', '**/*.{test,spec}.tsx'],
    },
  },
});
```

## Test File Structure

### Test File Naming and Organization

**File Naming Convention (following naming standards)**:

- Unit tests: `*.spec.ts` or `*.spec.tsx`
- Integration tests: `*.int.spec.ts`
- End-to-end tests: `*.e2e.spec.ts`

**TypeScript Import Standards in Tests**:

All test files must follow TypeScript import standards (standard:typescript):

```typescript
// ✅ GOOD: proper import organization
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { UserService } from '#services/user';
import { createUser } from './factories/user';

import type { User } from '#types/user';
import type { MockRepository } from './types/mocks';
```

**Test Isolation Requirements**:

- Unit tests (`.spec.ts`) must be fully isolated from external dependencies. Use mocks for databases, APIs, and other services.
- Integration tests (`.int.spec.ts`) may interact with real databases or third-party services. Ensure all necessary credentials are supplied before running the tests.

**Test Description Prefixes**:

- `fn:` - Functions
- `sv:` - Services
- `op:` - Operations
- `cl:` - Classes
- `mt:` - Class methods
- `gt:` - Class getters
- `st:` - Class setters
- `ty:` - Utility types or interfaces
- `rc:` - React components
- `hk:` - React hooks

For general-purpose test suites that do not map cleanly to one of these categories, use a clear natural-language description without a prefix.

### Test Double Organization

**File Structure with TypeScript Standards**:

Use a simplified, pragmatic structure for test doubles with proper TypeScript typing:

```typescript
spec/
├── mocks/                   // shared mocks across test files
│   ├── services/
│   │   └── user.ts          // implements proper TypeScript interfaces
│   ├── repositories/
│   │   └── crypto.ts        // type-safe repository mocks
│   ├── external/            // third-party service mocks
│   │   └── stripe.ts        // properly typed external mocks
│   └── factories/           // mock factory functions
│       └── order.ts         // type-safe factory functions
├── fixtures/                // shared test data
│   ├── users.ts             // typed fixtures
│   └── factories/           // fixture factory functions
│       └── user.ts          // type-safe fixtures
└── utilities/               // test utilities
    ├── helpers.ts           // type-safe test helpers
    └── setup.ts             // vitest setup file
```

**TypeScript-Compliant Placement Guidelines**:

- **Inline (Preferred for single-use)**: Place at the top of the test file when only used in that file, with proper TypeScript typing
- **Shared (For reuse)**: Place in `spec/mocks` or `spec/fixtures` when needed by multiple test files
- **Clean naming**: Use `const user = ...` instead of `const mockUser = ...` - TypeScript provides type clarity
- **No suffixes**: Use `mocks/user.ts` instead of `user.mock.ts` for cleaner imports
- **Type safety**: All mocks and fixtures must implement proper TypeScript interfaces
- **Documentation**: Follow TypeScript documentation standards for all test doubles

```typescript
// ✅ GOOD: proper test organization with typescript compliance
// ✅ GOOD: test descriptions must be written in lowercase
import type { OrderTotal, TaxCalculation } from '#types/order';

describe("fn:calculateOrderTotal", () => {
  it("should return correct total with tax and shipping", () => {
    const orderData = {
      subtotal: 100,
      tax: 8.5,
      shipping: 10,
    } satisfies Partial<OrderTotal>;
    
    // test implementation with type safety
  });
});

describe("rc:UserProfile", () => {
  it("should render user information correctly", () => {
    const user = {
      id: 'user-123',
      name: 'John Doe',
      email: 'john@example.com',
    } satisfies Partial<User>;
    
    // test implementation
  });
});

// for general-purpose tests, use a clear description without a prefix
describe("authentication flow", () => {
  it("should redirect to login when unauthorized", () => {
    // test implementation with proper TypeScript types
  });
});
```

### Section Headers for Long Test Files

<IMPORTANT>
Test files containing setup areas (types/interfaces, setup helpers, constants, mocks) before describe blocks MUST use standardized section headers to clearly separate different organizational areas.
</IMPORTANT>

**Section Header Format**:

All section headers must use exactly this format with consistent character width (26 characters total, 20 equal signs):

```typescript
// ==================== //
// SECTION NAME IN CAPS //
// ==================== //
```

**When to Use**:

Use section headers in test files that contain any of these setup areas before the test suites:

- Type/Interface definitions
- Setup helper functions
- Shared constants
- Mock definitions and configurations

**Standard Section Names**:

Use these standardized section names in order of appearance:

1. `TYPES` - Type definitions and interfaces
2. `MOCKS` - Mock definitions using vi.hoisted pattern
3. `CONSTANTS` - Shared test constants and fixtures
4. `HELPERS` - Helper functions for test setup
5. `TEST SUITES` - The describe blocks containing actual tests

**Complete Example**:

```typescript
// ✅ GOOD: organized test file with clear section headers
import { describe, it, expect, vi } from 'vitest';
import type { User, UserRepository } from '#types';

// ==================== //
//         TYPES        //
// ==================== //

interface TestContext {
  repository: UserRepository;
  service: UserService;
}

// ==================== //
//        MOCKS         //
// ==================== //

const { fetchUser } = vi.hoisted(() => ({
  fetchUser: vi.fn(),
}));

vi.mock(
  '#services/userService',
  () => ({
    fetchUser,
  }) satisfies Partial<typeof import('#services/userService')>,
);

// ==================== //
//      CONSTANTS       //
// ==================== //

const VALID_USER_DATA = {
  name: 'John Doe',
  email: 'john@example.com',
} as const;


// ==================== //
//        HELPERS       //
// ==================== //

const createTestContext = (): TestContext => {
  const repository = createMockUserRepository();
  const service = new UserService(repository);
  return { repository, service };
};

// ==================== //
//     TEST SUITES      //
// ==================== //

describe('sv:UserService', () => {
  it('should create user successfully', () => {
    const { service } = createTestContext();

    const result = service.createUser(VALID_USER_DATA);

    expect(result).toBeDefined();
  });
});
```

**Formatting Guidelines**:

- Section names should be centered or left-aligned within the header
- Maintain consistent spacing (2 slashes, 1 space, content, 1 space, 2 slashes)
- Total line width must be exactly 26 characters
- Use CAPS for all section names
- Keep section headers aligned vertically

```typescript
// ❌ BAD: inconsistent header format and missing sections
import { describe, it, expect, vi } from 'vitest';

// mocks
const { fetchUser } = vi.hoisted(() => ({
  fetchUser: vi.fn(),
}));

const VALID_USER = { name: 'John' };

describe('sv:UserService', () => {
  // tests without clear organization
});

// ✅ GOOD: consistent headers with clear organization
import { describe, it, expect, vi } from 'vitest';

// ==================== //
//       MOCKS          //
// ==================== //

const { fetchUser } = vi.hoisted(() => ({
  fetchUser: vi.fn(),
}));

// ==================== //
//     CONSTANTS        //
// ==================== //

const VALID_USER = { name: 'John' };

// ==================== //
//    TEST SUITES       //
// ==================== //

describe('sv:UserService', () => {
  it('should handle user creation', () => {
    // test implementation
  });
});
```

**When NOT to Use**:

Skip section headers for simple test files that:

- Contain only describe blocks with no setup
- Have minimal or inline mocks
- Are short (<100 lines) with straightforward structure

```typescript
// ✅ GOOD: simple test file without section headers
import { describe, it, expect } from 'vitest';
import { calculateDiscount } from './discount';

describe('fn:calculateDiscount', () => {
  it('should calculate percentage discount', () => {
    expect(calculateDiscount(100, 0.1)).toBe(90);
  });
});
```

## Test Structure Standards

### Arrange-Act-Assert Pattern with TypeScript

<IMPORTANT>
All tests must follow the AAA pattern with proper spacing and TypeScript compliance:

- Structure each test into 3 sections: Arrange, Act, Assert
- **A line space is required between each section**
- No need to add `// arrange`, `// act`, or `// assert` comments in the test code
- **For testing pure functions, use `result` and `expected` variables with proper TypeScript types**
- Declare `expected` value in the arrangement section (before `result`) with explicit typing
- **All variables must follow TypeScript standards** - no `any` types, proper type annotations
</IMPORTANT>

```typescript
// ✅ GOOD: clear aaa structure with proper spacing and typescript compliance
import type { CurrencyCode } from '#types/currency';

describe("fn:formatCurrency", () => {
  it("should format number as USD currency", () => {
    const amount = 1234.56;
    const currency: CurrencyCode = "USD";
    const expected = "$1,234.56";

    const result = formatCurrency(amount, currency);

    expect(result).toBe(expected);
  });
});

// ❌ BAD: unclear structure and missing typescript types
describe("fn:formatCurrency", () => {
  it("should format currency", () => {
    expect(formatCurrency(1234.56, "USD")).toBe("$1,234.56");
  });
});
```

### Test Data Management

**Use `const` for immutable test data**:

```typescript
// ✅ GOOD: immutable test data
describe("fn:processUser", () => {
  it("should validate user email format", () => {
    const userData = {
      id: "123",
      name: "John Doe",
      email: "john@example.com",
    };
    const expected = { isValid: true, errors: [] };

    const result = processUser(userData);

    expect(result).toEqual(expected);
  });
});

// ❌ BAD: mutable test data
describe("fn:processUser", () => {
  let userData = {
    id: "123",
    name: "John Doe",
    email: "john@example.com",
  };

  it("should validate user email format", () => {
    userData.email = "test@example.com"; // Mutating shared data
    const result = processUser(userData);
    expect(result.isValid).toBe(true);
  });
});
```

### Avoiding beforeEach and Using Factory Functions

Keep tests self-contained when possible. Use factory functions for complex setups. Reserve `beforeEach` / `afterEach` for environment resets that cannot happen inline (e.g. resetting databases, clearing fixtures) rather than routine mock wiring:

```typescript
// ✅ GOOD: self-contained tests with fresh instances
describe("cl:UserService", () => {
  it("should create user with valid data", () => {
    const repository = createMockUserRepository();
    const service = new UserService(repository);
    const userData = { name: "John", email: "john@example.com" };

    const result = service.createUser(userData);

    expect(result).toBeDefined();
  });

  it("should throw error with invalid email", () => {
    const repository = createMockUserRepository();
    const service = new UserService(repository);
    const userData = { name: "John", email: "invalid-email" };

    expect(() => service.createUser(userData)).toThrow();
  });
});

// factory function for complex setup
const createTestContext = () => {
  const repository = createMockUserRepository();
  const cacheService = createCacheService();
  const service = new UserService(repository, cacheService);
  return { repository, cacheService, service };
};

describe("cl:UserService", () => {
  it("should cache user after creation", () => {
    const { service, cacheService } = createTestContext();
    const userData = { name: "John", email: "john@example.com" };

    service.createUser(userData);

    expect(cacheService.set).toHaveBeenCalled();
  });
});

// ❌ BAD: using let with reassignment in hooks
describe("cl:UserService", () => {
  let service: UserService;
  let repository: MockUserRepository;

  beforeEach(() => {
    repository = createMockUserRepository();
    service = new UserService(repository);
  });

  it("should create user with valid data", () => {
    // test implementation
  });
});
```

### Test Comparison Preferences

Use the most appropriate assertion method:

- **Prefer inline throwing function** in `expect`, e.g. `expect(() => fn()).toThrow()`
- **Use `.toBe(...)`** for primitive values or reference identity
- **Use `.toEqual(...)`** only for deep comparisons (objects, arrays)

```typescript
// ✅ GOOD: appropriate assertion methods
expect(result).toBe(42); // Primitive comparison
expect(error).toBeInstanceOf(ValidationError); // Type checking
expect(() => validateUser(null)).toThrow(); // Inline throwing
expect(user).toEqual({ id: 1, name: "John" }); // Deep object comparison

// ❌ BAD: inappropriate assertion methods
expect(result).toEqual(42); // Overkill for primitives
expect(user).toBe({ id: 1, name: "John" }); // Will fail - different references
```

### Object and Array Assertions

<IMPORTANT>
When asserting on objects or arrays, use a single assertion that validates the entire structure. Do NOT check individual fields or elements one by one with separate expect statements.
</IMPORTANT>

**Object Assertions:**

```typescript
// ❌ BAD: checking fields one by one
it("should return file metadata", async () => {
  const result = await storage.metadata('file.txt');

  expect(result.mime).toBe('application/octet-stream');
  expect(result.size).toBe(0);
  expect(result.etag).toBe('');
  expect(result.lastModified).toBeInstanceOf(Date);
});

// ✅ GOOD: single assertion with full object
it("should return file metadata", async () => {
  const result = await storage.metadata('file.txt');

  expect(result).toEqual({
    mime: 'application/octet-stream',
    size: 0,
    etag: '',
    lastModified: expect.any(Date),
  });
});

// ✅ GOOD: partial matching when only some fields matter
it("should return file metadata with correct mime type", async () => {
  const result = await storage.metadata('file.txt');

  expect(result).toEqual(
    expect.objectContaining({
      mime: 'application/octet-stream',
      size: expect.any(Number),
      lastModified: expect.any(Date),
    })
  );
});
```

**Array Assertions:**

```typescript
// ❌ BAD: checking array elements one by one
it("should return list of users", async () => {
  const users = await service.listUsers();

  expect(users[0].name).toBe('Alice');
  expect(users[0].email).toBe('alice@example.com');
  expect(users[1].name).toBe('Bob');
  expect(users[1].email).toBe('bob@example.com');
});

// ✅ GOOD: single assertion with full array
it("should return list of users", async () => {
  const users = await service.listUsers();

  expect(users).toEqual([
    { name: 'Alice', email: 'alice@example.com' },
    { name: 'Bob', email: 'bob@example.com' },
  ]);
});

// ✅ GOOD: array with dynamic values
it("should return list of users with IDs", async () => {
  const users = await service.listUsers();

  expect(users).toEqual([
    expect.objectContaining({ name: 'Alice', email: 'alice@example.com' }),
    expect.objectContaining({ name: 'Bob', email: 'bob@example.com' }),
  ]);
});

// ✅ GOOD: array length and structure check
it("should return non-empty user list", async () => {
  const users = await service.listUsers();

  expect(users).toHaveLength(2);
  expect(users).toEqual(
    expect.arrayContaining([
      expect.objectContaining({ name: 'Alice' }),
      expect.objectContaining({ name: 'Bob' }),
    ])
  );
});
```

**Why this matters:**

- Single assertion is more maintainable and readable
- Shows the complete expected structure at a glance
- Easier to update when structure changes
- Better error messages showing full diff
- Reduces test verbosity

## Mocking Standards

### Vi.hoisted Pattern with Type Safety

<IMPORTANT>
All module mocks MUST use vi.hoisted() with proper type safety. Mock objects MUST use `satisfies Partial<MockedObject<Type>>` and module mocks MUST use `satisfies Partial<typeof import('...')>` for compile-time type checking.
</IMPORTANT>

Use the standard vi.hoisted pattern with destructured returns and helper utilities:

```typescript
// ✅ GOOD: advanced vi.hoisted pattern with helper utilities and type safety
import type { MockedObject } from '@theriety/testing';
import type {
  BlobServiceClient,
  BlockBlobClient,
  ContainerClient
} from '@azure/storage-blob';

// define helper utilities and mocks within hoisted block
const {
  blockBlobClient,
  containerClient,
  getContainerClient,
  toAsyncIterableIterator,
} = vi.hoisted(() => {
  // helper function for async iteration (useful for mocking streams)
  const toAsyncIterableIterator = <T>(items: readonly T[]) => {
    let i = 0;
    return {
      async next() {
        if (i >= items.length) return { done: true, value: undefined };
        const value = items[i++];
        return { done: false, value };
      },
      async *[Symbol.asyncIterator]() {
        for (const item of items) {
          yield item;
        }
      },
    };
  };

  // type-safe mock objects with MockedObject utility
  const blockBlobClient = {
    upload: vi.fn().mockResolvedValue({ etag: '"etag"' }),
    download: vi.fn().mockResolvedValue({ readableStreamBody: null }),
    exists: vi.fn().mockResolvedValue(true),
    getProperties: vi.fn().mockResolvedValue({ contentLength: 1024 }),
  } satisfies Partial<MockedObject<BlockBlobClient>>;

  const containerClient = {
    getBlockBlobClient: vi.fn().mockReturnValue(blockBlobClient),
    listBlobsFlat: vi.fn(),
  } satisfies Partial<MockedObject<ContainerClient>>;

  const getContainerClient = vi.fn(() => containerClient);

  return {
    blockBlobClient,
    containerClient,
    getContainerClient,
    toAsyncIterableIterator,
  };
});

// module mock with type safety
vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceClient: vi.fn(
        class {
          getContainerClient = getContainerClient;
        },
      ) as unknown as typeof BlobServiceClient,
      StorageSharedKeyCredential: vi.fn(
        class {},
      ) as unknown as typeof StorageSharedKeyCredential,
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);

describe("fn:uploadToStorage", () => {
  it("should upload file successfully", async () => {
    blockBlobClient.upload.mockResolvedValue({
      etag: '"new-etag"',
      isServerEncrypted: true
    });

    const result = await uploadToStorage('test.txt', Buffer.from('data'));

    expect(result.success).toBe(true);
    expect(blockBlobClient.upload).toHaveBeenCalled();
  });
});

// ✅ GOOD: simple vi.hoisted pattern for basic mocks
const { fetchUser } = vi.hoisted(() => ({
  fetchUser: vi.fn(),
}));

vi.mock(
  "#services/userService",
  () =>
    ({
      fetchUser,
    }) satisfies Partial<typeof import("#services/userService")>,
);

// type-safe fixtures with satisfies
import type { User } from "#types";

export const userFixtures = {
  validUser: {
    id: "user-001",
    email: "john@example.com",
    name: "John Doe",
    role: "admin",
  },
  invalidUser: {
    id: "",
    email: "invalid-email",
    name: "",
    role: "unknown",
  },
} satisfies Record<string, Partial<User>>;
```

### Type Aliases for Complex Mock Types

<IMPORTANT>
When mocking complex return types, use type aliases to maintain type safety and readability. This ensures mock return values match the actual function signatures.
</IMPORTANT>

```typescript
// ✅ GOOD: type alias for complex return type
import type { ContainerClient } from '@azure/storage-blob';

type ListBlobsFlatResponse = ReturnType<ContainerClient['listBlobsFlat']>;

const containerClient = {
  listBlobsFlat: vi.fn(
    () => toAsyncIterableIterator([...]) as unknown as ListBlobsFlatResponse
  ),
} satisfies Partial<MockedObject<ContainerClient>>;

// ❌ BAD: no type alias, unclear return type
const containerClient = {
  listBlobsFlat: vi.fn(() => toAsyncIterableIterator([...])),
};
```

### Class Mocking Pattern

<IMPORTANT>
When mocking classes, use `vi.fn(class {})` with proper type casting to ensure TypeScript compatibility. The type assertion `as unknown as typeof OriginalClass` is required because vi.fn() doesn't directly support class constructors.
</IMPORTANT>

```typescript
// ✅ GOOD: type-safe class mocking
import type { BlobServiceClient } from '@azure/storage-blob';

vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceClient: vi.fn(
        class {
          getContainerClient = getContainerClient;
          // add other methods as needed
        },
      ) as unknown as typeof BlobServiceClient,
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);

// ❌ BAD: no type casting
vi.mock('@azure/storage-blob', () => ({
  BlobServiceClient: vi.fn(class {
    getContainerClient = getContainerClient;
  }),
}));
```

### Type Safety Enforcement in Mocks

<IMPORTANT>
TypeScript type safety in mocks is enforced through multiple mechanisms that provide compile-time validation. Understanding these mechanisms ensures your mocks are type-safe and catch errors before runtime.
</IMPORTANT>

#### Mechanism 1: satisfies Partial<MockedObject<Type>>

**Purpose**: Ensures mock objects implement the correct interface structure while allowing partial implementation.

**How it works**: The `satisfies` operator provides compile-time type checking without affecting the inferred type. `Partial<MockedObject<T>>` allows you to implement only the methods you need while ensuring they match the original interface.

**Benefits**:

- Compile-time validation that mock methods match real interface signatures
- Auto-completion for mock object properties in your IDE
- Catches typos and signature mismatches immediately
- Type inference for mock methods ensures correct usage in tests

```typescript
// ✅ GOOD: satisfies validates mock structure at compile-time
import type { MockedObject } from '@theriety/testing';
import type { UserService } from '#services/user';

const mockUserService = {
  getUser: vi.fn<[string], Promise<User>>(),
  createUser: vi.fn<[UserData], Promise<User>>(),
  // TypeScript ensures these signatures match UserService interface
} satisfies Partial<MockedObject<UserService>>;

// ❌ BAD: typo in method name - caught at compile-time with satisfies
const mockUserService = {
  getUzer: vi.fn(), // ❌ TypeScript error: 'getUzer' doesn't exist on UserService
} satisfies Partial<MockedObject<UserService>>;

// ❌ BAD: wrong signature - caught at compile-time
const mockUserService = {
  getUser: vi.fn<[number], string>(), // ❌ Wrong parameter and return types
} satisfies Partial<MockedObject<UserService>>;
```

#### Mechanism 2: satisfies Partial<typeof import('...')>

**Purpose**: Validates that mocked modules export the correct structure and types.

**How it works**: Uses TypeScript's `typeof import()` to reference the actual module's export structure, then validates your mock matches it.

**Benefits**:

- Ensures mocked modules have the same exports as real modules
- Catches missing or incorrectly typed exports before runtime
- Works with TypeScript's module type system
- Validates both values and types exported by the module

```typescript
// ✅ GOOD: module mock validated against actual module exports
vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceClient: vi.fn(class {}),
      StorageSharedKeyCredential: vi.fn(class {}),
      BlobSASPermissions: { parse: vi.fn() },
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);

// ❌ BAD: wrong export name - caught at compile-time
vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceCliient: vi.fn(class {}), // ❌ Typo caught by TypeScript
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);

// ❌ BAD: missing type annotation - no compile-time validation
vi.mock('@azure/storage-blob', () => ({
  BlobServiceClient: vi.fn(class {}), // No type safety
}));
```

#### Mechanism 3: vi.fn() with Generic Type Parameters

**Purpose**: Explicitly type function signatures for mock functions.

**How it works**: Provide generic type parameters `vi.fn<[Params], ReturnType>()` to specify exact function signatures.

**Benefits**:

- Explicit type annotations for complex function signatures
- Ensures mock calls match expected parameter types
- Validates return types at compile-time
- Improves IDE auto-completion and error messages

```typescript
// ✅ GOOD: explicit function signature typing
import type { User, UserData } from '#types';

const mockRepository = {
  save: vi.fn<[UserData], Promise<User>>(),
  findById: vi.fn<[string], Promise<User | null>>(),
  findAll: vi.fn<[], Promise<User[]>>(),
};

// in test: TypeScript validates all calls
mockRepository.save({ name: 'John', email: 'john@example.com' }); // ✅ Valid
mockRepository.save('invalid'); // ❌ TypeScript error: wrong parameter type
mockRepository.findById(123); // ❌ TypeScript error: expects string, got number

// ❌ BAD: no generic types - no compile-time validation
const mockRepository = {
  save: vi.fn(), // No type information
  findById: vi.fn(), // Parameters and return types unknown
};
```

#### Mechanism 4: Type Casting for Class Mocks

**Purpose**: Handle Vitest's class mocking limitations with proper type assertions.

**How it works**: Use `vi.fn(class {}) as unknown as typeof OriginalClass` to mock class constructors.

**Why needed**: Vitest's `vi.fn()` doesn't directly support class constructors, requiring the `as unknown as` double assertion.

```typescript
// ✅ GOOD: proper type casting for class mocks
import type { BlobServiceClient } from '@azure/storage-blob';

vi.mock(
  '@azure/storage-blob',
  () =>
    ({
      BlobServiceClient: vi.fn(
        class {
          getContainerClient = vi.fn();
        },
      ) as unknown as typeof BlobServiceClient,
    }) satisfies Partial<typeof import('@azure/storage-blob')>,
);

// ❌ BAD: missing type cast
vi.mock('@azure/storage-blob', () => ({
  BlobServiceClient: vi.fn(class {}), // ❌ Type error: incompatible with constructor
}));
```

#### Mechanism 5: MockedObject<T> Utility Type

**Purpose**: Transform interface methods to vi.fn() mocks while preserving type signatures.

**How it works**: The `MockedObject<T>` utility type (from `@theriety/testing`) replaces each method in interface `T` with a properly typed `vi.fn()` mock.

**Benefits**:

- Automatically converts interface methods to mock functions
- Preserves all type information from the original interface
- Ensures mock method signatures match the original
- Works seamlessly with `satisfies Partial<MockedObject<T>>`

```typescript
// ✅ GOOD: MockedObject preserves all type information
import type { MockedObject } from '@theriety/testing';
import type { UserRepository } from '#repositories/user';

// MockedObject<UserRepository> transforms methods to vi.fn() with correct types
const mockRepo = {
  save: vi.fn(),
  findById: vi.fn(),
} satisfies Partial<MockedObject<UserRepository>>;

// TypeScript knows the exact signature of each mock
mockRepo.save.mockResolvedValue(user); // ✅ Validated
mockRepo.findById.mockResolvedValue(null); // ✅ Validated

// ❌ BAD: manual typing without MockedObject
const mockRepo: Partial<UserRepository> = {
  save: vi.fn(), // ❌ Type error: vi.fn() is not assignable to the method type
};
```

### Type Safety Decision Tree

Use this decision tree to choose the right type safety mechanism:

```
Need to mock a module?
├─ Yes → Use satisfies Partial<typeof import('...')>
│         └─ Mocking a class in the module?
│             └─ Yes → Also use (vi.fn(class {}) as unknown as typeof Class)
│
└─ No → Mocking an object/service?
    └─ Yes → Use satisfies Partial<MockedObject<Interface>>
        ├─ Simple function signatures?
        │   └─ MockedObject handles it automatically
        │
        └─ Complex function signatures needing clarity?
            └─ Add explicit generics: vi.fn<[Params], Return>()
```

### Mock Cleanup and Vitest Configuration

<IMPORTANT>
Configure Vitest for automatic cleanup. Never use manual cleanup in tests. The following configuration is REQUIRED in all projects:

```typescript
// vitest.config.ts - required configuration
export default defineConfig({
  test: {
    mockReset: true,     // automatically reset mock implementations between tests
    clearMocks: true,    // clear call history between tests
    restoreMocks: true,  // restore original implementations
  }
});
```

</IMPORTANT>

```typescript
// ❌ BAD: manual mock cleanup (unnecessary with proper config)
describe("fn:apiCall", () => {
  afterEach(() => {
    vi.clearAllMocks(); // Not needed with proper Vitest configuration
  });
});

// ✅ GOOD: let vitest handle mock cleanup automatically
describe("fn:apiCall", () => {
  it("should handle successful response", () => {
    const fetchUser = vi.fn().mockResolvedValue({ id: "123" });
    // each test gets fresh mock state automatically
  });

  it("should handle error response", () => {
    const fetchUser = vi.fn().mockRejectedValue(new Error("Failed"));
    // previous test's mock state is automatically cleared
  });
});
```

## React Component Testing

### Component Test Structure

```typescript
// ✅ GOOD: react component testing
import { render, screen, fireEvent } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('rc:UserCard', () => {
  it('should render user information correctly', () => {
    const user = {
      id: '123',
      name: 'John Doe',
      email: 'john@example.com'
    };

    render(<UserCard user={user} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('should call onEdit when edit button is clicked', () => {
    const user = { id: '123', name: 'John' };
    const onEdit = vi.fn();

    render(<UserCard user={user} onEdit={onEdit} />);

    fireEvent.click(screen.getByRole('button', { name: /edit/i }));

    expect(onEdit).toHaveBeenCalledWith('123');
  });
});
```

### Testing User Interactions

```typescript
// ✅ GOOD: testing user interactions
describe('rc:LoginForm', () => {
  it('should submit form with valid credentials', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });
});
```

## Service and Repository Testing

### Service Testing Patterns

```typescript
// ✅ GOOD: service testing
describe("sv:UserService", () => {
  it("should create user and return success result", async () => {
    const repository = {
      save: vi.fn().mockResolvedValue({ id: "123", name: "John" }),
      findById: vi.fn(),
      findAll: vi.fn(),
    };
    const service = new UserService(repository);
    const userData = { name: "John", email: "john@example.com" };
    const expected = { success: true, data: { id: "123", name: "John" } };

    const result = await service.createUser(userData);

    expect(result).toEqual(expected);
    expect(repository.save).toHaveBeenCalledWith(userData);
  });

  it("should return error result when repository fails", async () => {
    const repository = {
      save: vi.fn().mockRejectedValue(new Error("Database error")),
      findById: vi.fn(),
      findAll: vi.fn(),
    };
    const service = new UserService(repository);
    const userData = { name: "John", email: "invalid" };

    const result = await service.createUser(userData);

    expect(result.success).toBe(false);
    expect(result.error).toBeInstanceOf(Error);
  });
});
```

## Factory Functions for Test Doubles

### Factory Function Pattern

Use factory functions to create consistent, type-safe test doubles:

```typescript
// ✅ GOOD: factory function supports overrides for flexible testing
export function createUserService(
  overrides?: Partial<UserService>
): UserService {
  return {
    getUser: vi.fn().mockResolvedValue(createUser()),
    createUser: vi.fn().mockResolvedValue({ id: 'new-user-id' }),
    updateUser: vi.fn().mockResolvedValue(true),
    dropUser: vi.fn().mockResolvedValue(true),
    listUsers: vi.fn().mockResolvedValue([]),
    ...overrides
  };
}

// usage with overrides in test
describe('fn:handleUserNotFound', () => {
  it('should handle user not found gracefully', async () => {
    const userService = createUserService({
      getUser: vi.fn().mockRejectedValue(new Error('User not found'))
    });
    const handler = new UserHandler(userService);
    
    const result = await handler.fetchUserSafely('user-123');
    
    expect(result).toBeNull();
  });
});

// factory for fixtures
export const createUserFixture = (overrides?: Partial<User>): User => ({
  id: `user-${Date.now()}`,
  email: `test-${Date.now()}@example.com`,
  name: 'Test User',
  role: 'user',
  createdAt: new Date().toISOString(),
  ...overrides
});

// usage in tests
describe('fn:processUser', () => {
  it('should process admin user differently', () => {
    const adminUser = createUserFixture({ role: 'admin' });
    const regularUser = createUserFixture({ role: 'user' });
    
    const adminResult = processUser(adminUser);
    const regularResult = processUser(regularUser);
    
    expect(adminResult.permissions).toContain('admin');
    expect(regularResult.permissions).not.toContain('admin');
  });
});
```

## Error Testing

### Testing Error Conditions

```typescript
// ✅ GOOD: error condition testing
describe("fn:validateUser", () => {
  it("should throw ValidationError for invalid email", () => {
    const invalidUser = { name: "John", email: "invalid-email" };

    expect(() => validateUser(invalidUser)).toThrow("Invalid email format");
  });

  it("should throw ValidationError for missing name", () => {
    const invalidUser = { name: "", email: "john@example.com" };

    expect(() => validateUser(invalidUser)).toThrow("Name is required");
  });
});

// ✅ GOOD: async error testing
describe("fn:fetchUserData", () => {
  it("should reject with error when user not found", async () => {
    const userId = "nonexistent";

    await expect(fetchUserData(userId)).rejects.toThrow("User not found");
  });
});
```

## Coverage Standards

### Coverage Requirements

<IMPORTANT>
- **Minimum coverage**: 100% line coverage
- **Branch coverage**: 100% for critical paths
- **Function coverage**: 100% for public APIs
- **Statement coverage**: 100% for business logic

All projects MUST maintain 100% coverage with the absolute minimum number of tests. Use the coverage-driven test development workflow to ensure each test adds unique value.
</IMPORTANT>

### Coverage Configuration

```json
// vitest.config.ts coverage settings
{
  "coverage": {
    "provider": "v8",
    "reporter": ["text", "json", "html"],
    "thresholds": {
      "global": {
        "branches": 100,
        "functions": 100,
        "lines": 100,
        "statements": 100
      }
    },
    "exclude": [
      "node_modules/**",
      "dist/**",
      "**/*.d.ts",
      "**/*.config.*",
      "**/coverage/**"
    ]
  }
}
```

## Test Performance

### Performance Guidelines

- **Fast execution** - Unit tests should run in milliseconds
- **Isolated tests** - No dependencies between tests
- **Minimal setup** - Avoid complex test fixtures
- **Parallel execution** - Tests should be parallelizable

```typescript
// ✅ GOOD: fast, isolated tests
describe("fn:calculateDiscount", () => {
  it("should calculate 10% discount for premium users", () => {
    const result = calculateDiscount(100, "premium");
    expect(result).toBe(90);
  });

  it("should calculate 5% discount for regular users", () => {
    const result = calculateDiscount(100, "regular");
    expect(result).toBe(95);
  });
});

// ❌ BAD: slow, interdependent tests
describe("UserService Integration", () => {
  it("should create user in database", async () => {
    // slow database operation
    await database.connect();
    const user = await service.createUser(userData);
    globalTestUser = user; // Creates dependency
  });

  it("should find user created in previous test", async () => {
    // depends on previous test
    const user = await service.findUser(globalTestUser.id);
    expect(user).toBeDefined();
  });
});
```

## Test Documentation with TypeScript

### Descriptive Test Names with TypeScript Context

```typescript
// ✅ GOOD: descriptive test names
describe("fn:processPayment", () => {
  it("should process payment successfully with valid card", () => {});
  it("should reject payment when card is expired", () => {});
  it("should retry payment up to 3 times on network failure", () => {});
  it("should handle insufficient funds gracefully", () => {});
});

// ❌ BAD: vague test names
describe("fn:processPayment", () => {
  it("should work", () => {});
  it("should fail", () => {});
  it("should retry", () => {});
});
```

### Test Documentation Comments

```typescript
// ✅ GOOD: document complex test scenarios
describe("fn:complexBusinessLogic", () => {
  it("should calculate tier pricing based on volume and customer history", () => {
    // this test verifies the complex pricing algorithm that considers:
    // 1. Current order volume (>$1000 gets tier 1 pricing)
    // 2. Customer loyalty status (premium customers get additional 5% off)
    // 3. Seasonal promotions (active during Q4)

    const orderData = {
      amount: 1500,
      customerId: "premium-customer-123",
      date: new Date("2023-12-15"), // Q4 date
    };
    const expected = {
      basePrice: 1500,
      tierDiscount: 150, // 10% tier 1 discount
      loyaltyDiscount: 75, // 5% loyalty discount
      finalPrice: 1275,
    };

    const result = calculateTierPricing(orderData);

    expect(result).toEqual(expected);
  });
});
```

## Anti-Patterns

### Common Mistakes to Avoid

```typescript
// ❌ BAD: over-mocking simple logic
const dateFormatter = vi.fn().mockReturnValue('2024-01-01');
const validator = vi.fn().mockReturnValue(true);

// ✅ GOOD: use real implementations for simple logic
import { formatDate } from '#utils/date';
import { validateEmail } from '#utils/validators';

// only mock external dependencies with side effects
const apiClient = createApiClient();

// ❌ BAD: testing the mock instead of business logic
describe('sv:UserService', () => {
  it('should fetch user data', async () => {
    const userApi = createUserApi();
    await service.enrichUserProfile('user-123');
    
    // only testing that the mock was called - missing actual business logic
    expect(userApi.getUser).toHaveBeenCalledWith('user-123');
  });
});

// ✅ GOOD: test business logic and outcomes
describe('sv:UserService', () => {
  it('should enrich user profile with preferences', async () => {
    const userApi = createUserApi();
    userApi.getUser.mockResolvedValue({ id: 'user-123', name: 'John' });
    userApi.getPreferences.mockResolvedValue({ theme: 'dark' });
    
    const enrichedProfile = await service.enrichUserProfile('user-123');
    
    // primary: test the actual business logic
    expect(enrichedProfile).toEqual({
      id: 'user-123',
      name: 'John',
      preferences: { theme: 'dark' },
      enrichedAt: expect.any(Date)
    });
  });
});

// ❌ BAD: dynamic imports in tests
describe('fn:validatePermissions', () => {
  it('should validate user permissions', async () => {
    const { validatePermissions } = await import('#auth/permissions');
    // ...
  });
});

// ✅ GOOD: static imports at module level
import { validatePermissions } from '#auth/permissions';
import { getUserRole } from '#auth/roles';

describe('fn:validatePermissions', () => {
  it('should validate user permissions', async () => {
    const role = await getUserRole('user-123');
    const isValid = validatePermissions(role, 'write');
    expect(isValid).toBe(true);
  });
});

// ❌ BAD: testing implementation details
describe('rc:UserList', () => {
  it('should call useState with empty array', () => {
    const useStateSpy = vi.spyOn(React, 'useState');
    render(<UserList />);
    expect(useStateSpy).toHaveBeenCalledWith([]);
  });
});

// ✅ GOOD: test behavior, not implementation
describe('rc:UserList', () => {
  it('should display user names when users are provided', () => {
    const users: User[] = [
      { id: '1', name: 'John', email: 'john@example.com', ... }, 
      { id: '2', name: 'Jane', email: 'jane@example.com', ... }
    ];

    render(<UserList users={users} />);

    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Jane')).toBeInTheDocument();
  });
});

// ❌ BAD: major typescript violation: using any types in tests
const mockService: any = { getData: vi.fn(), ... };

// ✅ GOOD: proper typescript mock with satisfies pattern
const mockService: DataService = {
  getData: vi.fn<[], Promise<Data>>(),
  saveData: vi.fn<[Data], Promise<void>>()
};
```

## 🚨 CRITICAL VIOLATIONS: Minimal Testing Enforcement

### Immediate Rejection Criteria

The following patterns will result in **IMMEDIATE CODE REVIEW REJECTION**:

```typescript
// ❌ REJECTED: Multiple tests for mathematical variations
describe("fn:calculateTax", () => {
  it("should calculate tax for $10", () => {
    expect(calculateTax(10)).toBe(1);
  });
  // more similar tests with different amounts...
  // REJECTED: same formula, different numbers
});

// ❌ REJECTED: Testing wrapper functions
describe("sv:UserService", () => {
  it("should call repository.save", () => {
    const repo = { save: vi.fn() };
    service.saveUser(userData);
    expect(repo.save).toHaveBeenCalledWith(userData);
    // REJECTED: service just passes through to repo
  });
});

// ❌ REJECTED: Artificial test data variations
describe("fn:validateEmail", () => {
  it("should validate john@example.com", () => {
    expect(validateEmail("john@example.com")).toBe(true);
  });
  // more tests with different valid email names...
  // REJECTED: same validation logic, different names
});

// ✅ ACCEPTED: Each test verifies unique behavior
describe("fn:validateEmail", () => {
  it("should accept valid email format", () => {
    expect(validateEmail("user@example.com")).toBe(true);
  });
  it("should reject missing @", () => {
    expect(validateEmail("userexample.com")).toBe(false);
  });
  it("should reject empty string", () => {
    expect(validateEmail("")).toBe(false);
  });
  // ACCEPTED: different validation rules tested
});
```

### Enforcement Rules

<IMPORTANT>
1. **One Test Per Behavior** - Not per input value
2. **No Wrapper Testing** - Test outcomes, not pass-throughs
3. **No Artificial Variations** - Real edge cases only
4. **Value or Delete** - Every test must earn its maintenance cost

Any code containing redundant tests, tests that add zero coverage, or tests with artificial variations will be IMMEDIATELY REJECTED during code review.
</IMPORTANT>

---

## Quick Reference

| Test Type | File Pattern | Purpose | Example |
|-----------|-------------|---------|----------|
| Unit | `*.spec.ts` | Isolated component testing | `user.service.spec.ts` |
| Integration | `*.int.spec.ts` | Component interaction testing | `auth.int.spec.ts` |
| E2E | `*.e2e.spec.ts` | Full system testing | `login.e2e.spec.ts` |

## Patterns & Best Practices

### Factory Pattern for Test Data

**Purpose**: Create consistent, type-safe test data with minimal boilerplate

**When to use**:

- Multiple tests need similar data structures
- Need to test with variations of the same entity
- Want to avoid data setup duplication

**Implementation**:

```typescript
// pattern template
export const createTestEntity = <T>(base: T, overrides?: Partial<T>): T => ({
  ...base,
  ...overrides
});

// real-world example
export const createUser = (overrides?: Partial<User>): User => ({
  id: `user-${Date.now()}`,
  email: `test@example.com`,
  name: 'Test User',
  ...overrides
});
```

### Common Patterns

1. **AAA Pattern** - Structure all tests with Arrange, Act, Assert

2. **Factory Functions** - Create test data generators for complex objects

3. **Type-Safe Mocks** - Use satisfies pattern for TypeScript compliance

## Quick Decision Tree

1. **What am I testing?**
   - If single function/method → Use unit test with `fn:` prefix
   - If component interaction → Use integration test  
   - If full user workflow → Use e2e test

2. **Do I need real dependencies?**
   - If testing logic only → Mock external dependencies
   - If testing integration → Use real implementations where safe
   - If testing system → Use real services with test data

3. **Is this test adding unique value?**
   - If testing same logic with different data → Combine into parameterized test
   - If testing different behavior → Keep as separate test
   - If testing implementation detail → Remove test

**COMPLIANCE REMINDER**:

All test code MUST strictly follow TypeScript standards AND minimal testing principles. Any test code that uses `any` types, bypasses type checking, violates TypeScript best practices, OR contains redundant tests will be rejected during code review. This standard works in conjunction with, not as a replacement for, all other coding standards.
