# Testing Standards

_Comprehensive testing standards for quality assurance, TDD compliance, and TypeScript type safety_

## Core Principles

## 🚨 MANDATORY PREREQUISITE STANDARDS

**[IMPORTANT]** Before applying these standards, you MUST also thoroughly read and understand the following foundational standards:

- [TypeScript Standards](@../code/typescript.md)
- [General Coding Principles](@../code/general-principles.md)
- [Function Standards](@../code/functions.md)
- [Documentation Standards](@../code/documentation.md)

### TypeScript Standards Compliance

- **No `any` types** - Use specific types for complete type safety
- **Strict type checking** - All mocks, fixtures, and test utilities must be properly typed
- **Type-safe assertions** - Ensure all expectations are type-safe and provide meaningful error messages
- **Proper imports** - Follow TypeScript import standards including separation of code and type imports
- **Interface documentation** - All test interfaces must be fully documented with JSDoc comments

```typescript
// ✅ GOOD: type-safe test with proper typescript compliance
import { describe, it, expect, vi } from 'vitest';

import type { User } from '#types/user';
import type { UserRepository } from '#repositories/user';

const createMockUserRepository = (): UserRepository => ({
  save: vi.fn(),
  findById: vi.fn(),
  findAll: vi.fn(),
});

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

Maintain high quality standards while ensuring complete type safety:

- **100% coverage maintained with minimal tests** - Cover everything efficiently
  - Maintain **100%** coverage, excluding barrel files (typically `index.ts`)
  - Use `/* v8 ignore start */` at the top of any barrel file to exclude it from coverage reports
- **Minimize test quantity** - Add minimal meaningful tests that cover everything
- **Maximize test reuse** - Think critically about minimizing complexity and maximizing reuse
- **Ignore lines marked with v8 ignore** - No need to create any tests for lines meant to be ignore from coverage

### TypeScript Testing Patterns

Follow these TypeScript-specific testing patterns:

- **Use `const` over `let`** - Create fresh instances per test instead of reassigning variables
- **Avoid `beforeEach`** - Keep tests self-contained when possible, use factory functions for complex setups
- **Never use dynamic imports** - Always use static imports at module level, no `await import()` in tests
- **Avoid over-mocking** - Use real implementations for simple logic, only mock external dependencies with side effects
- **Test outcomes, not mocks** - Focus on business logic and results, not mock call verification
- **Type-safe mock creation** - All mocks must implement proper TypeScript interfaces

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

**File Naming Convention (following TypeScript naming standards):**

- Unit tests: `*.spec.ts` or `*.spec.tsx`
- Integration tests: `*.int.spec.ts`
- End-to-end tests: `*.e2e.spec.ts`

**TypeScript Import Standards in Tests:**

All test files must follow [TypeScript import standards](@../code/typescript.md#import-organization):

```typescript
// ✅ GOOD: proper import organization
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { UserService } from '#services/user';
import { createUser } from './factories/user';

import type { User } from '#types/user';
import type { MockRepository } from './types/mocks';
```

**Test Isolation Requirements:**

- Unit tests (`.spec.ts`) must be fully isolated from external dependencies. Use mocks for databases, APIs, and other services.
- Integration tests (`.int.spec.ts`) may interact with real databases or third-party services. Ensure all necessary credentials are supplied before running the tests.

**Test Description Prefixes:**

- `fn:` - Functions
- `gt:` - Getter
- 'st:` - Setter
- `cl:` - Classes
- `ty:` - Types/interfaces
- `rc:` - React components
- `hk:` - React hooks
- `sv:` - Services
- `op:` - Operations
- `rp:` - Repositories

### Test Double Organization

**File Structure with TypeScript Standards:**

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

**TypeScript-Compliant Placement Guidelines:**

- **Inline (Preferred for single-use):** Place at the top of the test file when only used in that file, with proper TypeScript typing
- **Shared (For reuse):** Place in `spec/mocks` or `spec/fixtures` when needed by multiple test files
- **Clean naming:** Use `const user = ...` instead of `const mockUser = ...` - TypeScript provides type clarity
- **No suffixes:** Use `mocks/user.ts` instead of `user.mock.ts` for cleaner imports
- **Type safety:** All mocks and fixtures must implement proper TypeScript interfaces
- **Documentation:** Follow TypeScript documentation standards for all test doubles

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
    
    // Test implementation with type safety
  });
});

describe("rc:UserProfile", () => {
  it("should render user information correctly", () => {
    const user = {
      id: 'user-123',
      name: 'John Doe',
      email: 'john@example.com',
    } satisfies Partial<User>;
    
    // Test implementation
  });
});

// For general-purpose tests, use a clear description without a prefix
describe("authentication flow", () => {
  it("should redirect to login when unauthorized", () => {
    // Test implementation with proper TypeScript types
  });
});
```

## Test Structure Standards

### Arrange-Act-Assert Pattern with TypeScript

All tests must follow the AAA pattern with proper spacing and TypeScript compliance:

- Structure each test into 3 sections: Arrange, Act, Assert
- **A line space is required between each section**
- No need to add `// arrange`, `// act`, or `// assert` comments in the test code
- **[IMPORTANT] For testing pure functions, use `result` and `expected` variables with proper TypeScript types**
- Declare `expected` value in the arrangement section (before `result`) with explicit typing
- **All variables must follow TypeScript standards** - no `any` types, proper type annotations

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

**Use `const` for immutable test data:**

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

Keep tests self-contained when possible. Use factory functions for complex setups:

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
    // Test implementation
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

## Mocking Standards

### Vi.hoisted Pattern with Type Safety

Use the standard vi.hoisted pattern with `satisfies` for type-safe mocking:

```typescript
// ✅ GOOD: type-safe vi.hoisted pattern with satisfies
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

describe("fn:getUserProfile", () => {
  it("should return user profile when user exists", () => {
    const expectedUser = { id: "123", name: "John" };
    fetchUser.mockResolvedValue(expectedUser);

    const result = getUserProfile("123");

    expect(result).resolves.toEqual(expectedUser);
    expect(fetchUser).toHaveBeenCalledWith("123");
  });
});

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

### Mock Cleanup and Vitest Configuration

Configure Vitest for automatic cleanup. Never use manual cleanup in tests:

```typescript
// vitest.config.ts - required configuration
export default defineConfig({
  test: {
    mockReset: true,     // automatically reset mock implementations between tests
    clearMocks: true,    // clear call history between tests  
    restoreMocks: true,  // restore original implementations
  }
});

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
    // Each test gets fresh mock state automatically
  });

  it("should handle error response", () => {
    const fetchUser = vi.fn().mockRejectedValue(new Error("Failed"));
    // Previous test's mock state is automatically cleared
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
    deleteUser: vi.fn().mockResolvedValue(true),
    listUsers: vi.fn().mockResolvedValue([]),
    ...overrides
  };
}

// Usage with overrides in test
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

// Usage in tests
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

- **Minimum coverage**: 100% line coverage
- **Branch coverage**: 100% for critical paths
- **Function coverage**: 100% for public APIs
- **Statement coverage**: 100% for business logic

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
    // Slow database operation
    await database.connect();
    const user = await service.createUser(userData);
    globalTestUser = user; // Creates dependency
  });

  it("should find user created in previous test", async () => {
    // Depends on previous test
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
    // This test verifies the complex pricing algorithm that considers:
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

## Test Anti-Patterns

### Common Mistakes to Avoid

```typescript
// ❌ BAD: over-mocking simple logic
const dateFormatter = vi.fn().mockReturnValue('2024-01-01');
const validator = vi.fn().mockReturnValue(true);
const config = vi.fn().mockReturnValue({ apiUrl: 'https://api.example.com' });

// ✅ GOOD: use real implementations for simple logic
import { formatDate } from '#utils/date';
import { validateEmail } from '#utils/validators';
import { config } from '#config';

// Only mock external dependencies with side effects
const apiClient = createApiClient();
const database = createDatabaseConnection();

// ❌ BAD: testing the mock instead of business logic
describe('sv:UserService', () => {
  it('should fetch user data', async () => {
    const userApi = createUserApi();
    const service = new UserService(userApi);
    
    await service.enrichUserProfile('user-123');
    
    // Only testing that the mock was called
    expect(userApi.getUser).toHaveBeenCalledWith('user-123');
    expect(userApi.getPreferences).toHaveBeenCalled();
    // Missing: what did the service actually DO with this data?
  });
});

// ✅ GOOD: test business logic and outcomes
describe('sv:UserService', () => {
  it('should enrich user profile with preferences', async () => {
    const userApi = createUserApi();
    userApi.getUser.mockResolvedValue({ id: 'user-123', name: 'John' });
    userApi.getPreferences.mockResolvedValue({ theme: 'dark' });
    
    const service = new UserService(userApi);
    const enrichedProfile = await service.enrichUserProfile('user-123');
    
    // Primary: test the actual business logic
    expect(enrichedProfile).toEqual({
      id: 'user-123',
      name: 'John',
      preferences: { theme: 'dark' },
      enrichedAt: expect.any(Date)
    });
    
    // Secondary: verify correct API usage
    expect(userApi.getUser).toHaveBeenCalledWith('user-123');
  });
});

// ❌ BAD: dynamic imports in tests
describe('fn:validatePermissions', () => {
  it('should validate user permissions', async () => {
    const { validatePermissions } = await import('#auth/permissions');
    const { getUserRole } = await import('#auth/roles');
    
    const role = await getUserRole('user-123');
    const isValid = validatePermissions(role, 'write');
    expect(isValid).toBe(true);
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

// ✅ GOOD: test behavior, not implementation, with proper typescript
import type { User } from '#types/user';

describe('rc:UserList', () => {
  it('should display user names when users are provided', () => {
    const users: User[] = [
      { id: '1', name: 'John', email: 'john@example.com', createdAt: new Date(), updatedAt: new Date() }, 
      { id: '2', name: 'Jane', email: 'jane@example.com', createdAt: new Date(), updatedAt: new Date() }
    ];

    render(<UserList users={users} />);

    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Jane')).toBeInTheDocument();
  });
});

// ❌ BAD: major typescript violation: using any types in tests
const mockService: any = {
  getData: vi.fn(),
  saveData: vi.fn()
};

// ✅ GOOD: proper typescript mock with satisfies pattern
import type { DataService } from '#services/data';

const mockService: DataService = {
  getData: vi.fn<[], Promise<Data>>(),
  saveData: vi.fn<[Data], Promise<void>>()
};
```

---

**COMPLIANCE REMINDER:**

All test code MUST strictly follow TypeScript standards. Any test code that uses `any` types, bypasses type checking, or violates TypeScript best practices will be rejected during code review. This standard works in conjunction with, not as a replacement for, all other coding standards.
