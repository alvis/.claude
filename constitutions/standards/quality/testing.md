# Testing Standards

_Comprehensive testing standards for quality assurance and TDD compliance_

## Testing Framework

### Required Framework

**Vitest** is our testing framework of choice. All projects must use Vitest for unit and integration testing.

## Core Testing Principles

### Critical Testing Rules

- **Always BDD** - All new code must include tests written in Behavior-Driven Development (BDD) style
- **Test Before Code** - Always write tests for expected behaviors before implementing code
- **Follow TDD principles** - Write tests first, then implementation
- **100% coverage maintained with minimal tests** - Cover everything efficiently
  - Maintain **100%** coverage, excluding barrel files (typically `index.ts`)
  - Use `/* v8 ignore start */` at the top of any barrel file to exclude it from coverage reports
- **BDD style descriptions** - Use "should [expected behavior]" format
- **Proper test structure** - Follow Arrange → Act → Assert pattern
- **Minimize test quantity** - Add minimal meaningful tests that cover everything
- **Maximize test reuse** - Think critically about minimizing complexity and maximizing reuse
- **Ignore lines marked with v8 ignore** - No need to create any tests for lines meant to be ignore from coverage
- **Use `const` over `let`** - Create fresh instances per test instead of reassigning variables
- **Avoid `beforeEach`** - Keep tests self-contained when possible, use factory functions for complex setups
- **Never use `any` type in tests** - Use specific types with `satisfies` pattern for type safety
- **Never use dynamic imports** - Always use static imports at module level, no `await import()` in tests
- **Avoid over-mocking** - Use real implementations for simple logic, only mock external dependencies with side effects
- **Test outcomes, not mocks** - Focus on business logic and results, not mock call verification

### Test File Naming and Organization

**File Naming Convention:**

- Unit tests: `*.spec.ts` or `*.spec.tsx`
- Integration tests: `*.int.spec.ts`
- End-to-end tests: `*.e2e.spec.ts`

**Test Isolation Requirements:**

- Unit tests (`.spec.ts`) must be fully isolated from external dependencies. Use mocks for databases, APIs, and other services.
- Integration tests (`.int.spec.ts`) may interact with real databases or third-party services. Ensure all necessary credentials are supplied before running the tests.

**Test Description Prefixes:**

- `fn:` - Functions
- `op:` - Operations/methods
- `cl:` - Classes
- `ty:` - Types/interfaces
- `rc:` - React components
- `hk:` - React hooks
- `sv:` - Services
- `rp:` - Repositories

### Test Double Organization

**File Structure:**

Use a simplified, pragmatic structure for test doubles:

```typescript
spec/
├── mocks/                   // shared mocks across test files
│   ├── services/
│   │   └── user.ts          // no .mock.ts suffix needed
│   ├── repositories/
│   │   └── crypto.ts
│   ├── external/            // third-party service mocks
│   │   └── stripe.ts
│   └── factories/           // mock factory functions
│       ├── user.ts
│       └── order.ts
├── fixtures/                // shared test data
│   ├── users.ts
│   ├── products.ts
│   ├── orders.ts
│   └── factories/           // fixture factory functions
│       ├── user.ts
│       └── product.ts
└── utilities/               // test utilities
    ├── helpers.ts
    └── setup.ts             // vitest setup file
```

**Placement Guidelines:**

- **Inline (Preferred for single-use):** Place at the top of the test file when only used in that file
- **Shared (For reuse):** Place in `spec/mocks` or `spec/fixtures` when needed by multiple test files
- **Clean naming:** Use `const user = ...` instead of `const mockUser = ...` - TypeScript provides type clarity
- **No suffixes:** Use `mocks/user.ts` instead of `user.mock.ts` for cleaner imports

```typescript
// ✅ Good: Proper test organization
// Test descriptions must be written in lowercase
describe("fn:calculateOrderTotal", () => {
  it("should return correct total with tax and shipping", () => {
    // Test implementation
  });
});

describe("rc:UserProfile", () => {
  it("should render user information correctly", () => {
    // Test implementation
  });
});

// For general-purpose tests, use a clear description without a prefix
describe("authentication flow", () => {
  it("should redirect to login when unauthorized", () => {
    // Test implementation
  });
});
```

## Test Structure Standards

### Arrange-Act-Assert Pattern

All tests must follow the AAA pattern with proper spacing:

- Structure each test into 3 sections: Arrange, Act, Assert
- **A line space is required between each section**
- No need to add `// arrange`, `// act`, or `// assert` comments in the test code
- [[IMPORTANT] For testing pure functions, use `result` and `expected` variables]
- Declare `expected` value in the arrangement section (before `result`)

```typescript
// ✅ Good: Clear AAA structure with proper spacing
describe("fn:formatCurrency", () => {
  it("should format number as USD currency", () => {
    const amount = 1234.56;
    const expected = "$1,234.56";

    const result = formatCurrency(amount, "USD");

    expect(result).toBe(expected);
  });
});

// ❌ Bad: Unclear structure
describe("fn:formatCurrency", () => {
  it("should format currency", () => {
    expect(formatCurrency(1234.56, "USD")).toBe("$1,234.56");
  });
});
```

### Test Data Management

**Use `const` for immutable test data:**

```typescript
// ✅ Good: Immutable test data
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

// ❌ Bad: Mutable test data
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
// ✅ Good: Self-contained tests with fresh instances
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

// ✅ Good: Factory function for complex setup
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

// ❌ Bad: Using let with reassignment in hooks
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
// ✅ Good: Appropriate assertion methods
expect(result).toBe(42); // Primitive comparison
expect(error).toBeInstanceOf(ValidationError); // Type checking
expect(() => validateUser(null)).toThrow(); // Inline throwing
expect(user).toEqual({ id: 1, name: "John" }); // Deep object comparison

// ❌ Bad: Inappropriate assertion methods
expect(result).toEqual(42); // Overkill for primitives
expect(user).toBe({ id: 1, name: "John" }); // Will fail - different references
```

## Mocking Standards

### Vi.hoisted Pattern with Type Safety

Use the standard vi.hoisted pattern with `satisfies` for type-safe mocking:

```typescript
// ✅ Good: Type-safe vi.hoisted pattern with satisfies
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

// ✅ Good: Type-safe fixtures with satisfies
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

// ❌ Bad: Manual mock cleanup (unnecessary with proper config)
describe("fn:apiCall", () => {
  afterEach(() => {
    vi.clearAllMocks(); // Not needed with proper Vitest configuration
  });
});

// ✅ Good: Let Vitest handle mock cleanup automatically
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
// ✅ Good: React component testing
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
// ✅ Good: Testing user interactions
describe('rc:LoginForm', () => {
  it('should submit form with valid credentials', async () => {
    const onSubmit = vi.fn();

    render(<LoginForm onSubmit={onSubmit} />);

    // Arrange user inputs
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    // Act - simulate user interaction
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    // Assert
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
// ✅ Good: Service testing
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
// ✅ Good: Factory function with overrides
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

// ✅ Good: Factory for fixtures
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
// ✅ Good: Error condition testing
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

// ✅ Good: Async error testing
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
// ✅ Good: Fast, isolated tests
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

// ❌ Bad: Slow, interdependent tests
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

## Test Documentation

### Descriptive Test Names

```typescript
// ✅ Good: Descriptive test names
describe("fn:processPayment", () => {
  it("should process payment successfully with valid card", () => {});
  it("should reject payment when card is expired", () => {});
  it("should retry payment up to 3 times on network failure", () => {});
  it("should handle insufficient funds gracefully", () => {});
});

// ❌ Bad: Vague test names
describe("fn:processPayment", () => {
  it("should work", () => {});
  it("should fail", () => {});
  it("should retry", () => {});
});
```

### Test Documentation Comments

```typescript
// ✅ Good: Document complex test scenarios
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
// ❌ Bad: Over-mocking simple logic
const dateFormatter = vi.fn().mockReturnValue('2024-01-01');
const validator = vi.fn().mockReturnValue(true);
const config = vi.fn().mockReturnValue({ apiUrl: 'https://api.example.com' });

// ✅ Good: Use real implementations for simple logic
import { formatDate } from '#utils/date';
import { validateEmail } from '#utils/validators';
import { config } from '#config';

// Only mock external dependencies with side effects
const apiClient = createApiClient();
const database = createDatabaseConnection();

// ❌ Bad: Testing the mock instead of business logic
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

// ✅ Good: Test business logic and outcomes
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

// ❌ Bad: Dynamic imports in tests
describe('fn:validatePermissions', () => {
  it('should validate user permissions', async () => {
    const { validatePermissions } = await import('#auth/permissions');
    const { getUserRole } = await import('#auth/roles');
    
    const role = await getUserRole('user-123');
    const isValid = validatePermissions(role, 'write');
    expect(isValid).toBe(true);
  });
});

// ✅ Good: Static imports at module level
import { validatePermissions } from '#auth/permissions';
import { getUserRole } from '#auth/roles';

describe('fn:validatePermissions', () => {
  it('should validate user permissions', async () => {
    const role = await getUserRole('user-123');
    const isValid = validatePermissions(role, 'write');
    expect(isValid).toBe(true);
  });
});

// ❌ Bad: Testing implementation details
describe('rc:UserList', () => {
  it('should call useState with empty array', () => {
    const useStateSpy = vi.spyOn(React, 'useState');
    render(<UserList />);
    expect(useStateSpy).toHaveBeenCalledWith([]);
  });
});

// ✅ Good: Test behavior, not implementation
describe('rc:UserList', () => {
  it('should display user names when users are provided', () => {
    const users = [{ id: '1', name: 'John' }, { id: '2', name: 'Jane' }];

    render(<UserList users={users} />);

    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Jane')).toBeInTheDocument();
  });
});
```
