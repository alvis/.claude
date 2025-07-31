# Testing Standards

*Comprehensive testing standards for quality assurance and TDD compliance*

## Core Testing Principles

### Critical Testing Rules

- **Follow TDD principles** - Write tests first, then implementation
- **100% coverage maintained with minimal tests** - Cover everything efficiently
- **BDD style descriptions** - Use "should [expected behavior]" format
- **Proper test structure** - Follow Arrange → Act → Assert pattern
- **Minimize test quantity** - Add minimal meaningful tests that cover everything
- **Maximize test reuse** - Think critically about minimizing complexity and maximizing reuse
- **Use `const` over `let`** - Prefer immutable test data
- **Avoid `beforeEach`** - Keep tests self-contained when possible

### Test File Naming and Organization

**File Naming Convention:**

- Unit tests: `*.spec.ts` or `*.spec.tsx`
- Integration tests: `*.integration.spec.ts`
- End-to-end tests: `*.e2e.spec.ts`

**Test Description Prefixes:**

- `fn:` - Functions
- `op:` - Operations/methods
- `cl:` - Classes
- `ty:` - Types/interfaces
- `rc:` - React components
- `hk:` - React hooks
- `sv:` - Services
- `rp:` - Repositories

```typescript
// ✅ Good: Proper test organization
describe('fn:calculateOrderTotal', () => {
  it('should return correct total with tax and shipping', () => {
    // Test implementation
  });
});

describe('rc:UserProfile', () => {
  it('should render user information correctly', () => {
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
- IMPORTANT: For testing pure functions, use `result` and `expected` variables
- Declare `expected` value in the arrangement section (before `result`)

```typescript
// ✅ Good: Clear AAA structure
describe('fn:formatCurrency', () => {
  it('should format number as USD currency', () => {
    // Arrange
    const amount = 1234.56;
    const expected = '$1,234.56';
    
    // Act
    const result = formatCurrency(amount, 'USD');
    
    // Assert
    expect(result).toBe(expected);
  });
});

// ❌ Bad: Unclear structure
describe('fn:formatCurrency', () => {
  it('should format currency', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });
});
```

### Test Data Management

**Use `const` for immutable test data:**

```typescript
// ✅ Good: Immutable test data
describe('fn:processUser', () => {
  it('should validate user email format', () => {
    const userData = {
      id: '123',
      name: 'John Doe',
      email: 'john@example.com'
    };
    const expected = { isValid: true, errors: [] };
    
    const result = processUser(userData);
    
    expect(result).toEqual(expected);
  });
});

// ❌ Bad: Mutable test data
describe('fn:processUser', () => {
  let userData = {
    id: '123',
    name: 'John Doe',
    email: 'john@example.com'
  };
  
  it('should validate user email format', () => {
    userData.email = 'test@example.com'; // Mutating shared data
    const result = processUser(userData);
    expect(result.isValid).toBe(true);
  });
});
```

### Avoiding beforeEach

Keep tests self-contained when possible:

```typescript
// ✅ Good: Self-contained tests
describe('cl:UserService', () => {
  it('should create user with valid data', () => {
    const mockRepository = createMockUserRepository();
    const service = new UserService(mockRepository);
    const userData = { name: 'John', email: 'john@example.com' };
    
    const result = service.createUser(userData);
    
    expect(result).toBeDefined();
  });
  
  it('should throw error with invalid email', () => {
    const mockRepository = createMockUserRepository();
    const service = new UserService(mockRepository);
    const userData = { name: 'John', email: 'invalid-email' };
    
    expect(() => service.createUser(userData)).toThrow();
  });
});

// ❌ Avoid: beforeEach when not necessary
describe('cl:UserService', () => {
  let service: UserService;
  let mockRepository: MockUserRepository;
  
  beforeEach(() => {
    mockRepository = createMockUserRepository();
    service = new UserService(mockRepository);
  });
  
  it('should create user with valid data', () => {
    // Test implementation
  });
});
```

## Mocking Standards

### Vi.hoisted Pattern

Use the standard vi.hoisted pattern for mocking:

```typescript
// ✅ Good: Standard vi.hoisted pattern
const { fetchUser } = vi.hoisted(() => ({
  fetchUser: vi.fn(),
}));

vi.mock('#services/userService', () => ({
  fetchUser,
}) satisfies Partial<typeof import('#services/userService')>);

describe('fn:getUserProfile', () => {
  it('should return user profile when user exists', () => {
    const expectedUser = { id: '123', name: 'John' };
    fetchUser.mockResolvedValue(expectedUser);
    
    const result = getUserProfile('123');
    
    expect(result).resolves.toEqual(expectedUser);
    expect(fetchUser).toHaveBeenCalledWith('123');
  });
});
```

### Mock Cleanup

```typescript
// ✅ Good: Proper mock cleanup
describe('fn:apiCall', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });
  
  it('should handle successful response', () => {
    fetchUser.mockResolvedValue({ id: '123' });
    
    // Test implementation
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
    const mockOnEdit = vi.fn();
    
    render(<UserCard user={user} onEdit={mockOnEdit} />);
    
    fireEvent.click(screen.getByRole('button', { name: /edit/i }));
    
    expect(mockOnEdit).toHaveBeenCalledWith('123');
  });
});
```

### Testing User Interactions

```typescript
// ✅ Good: Testing user interactions
describe('rc:LoginForm', () => {
  it('should submit form with valid credentials', async () => {
    const mockOnSubmit = vi.fn();
    
    render(<LoginForm onSubmit={mockOnSubmit} />);
    
    // Arrange user inputs
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });
    
    // Act - simulate user interaction
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    // Assert
    expect(mockOnSubmit).toHaveBeenCalledWith({
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
describe('sv:UserService', () => {
  it('should create user and return success result', async () => {
    const mockRepository = {
      save: vi.fn().mockResolvedValue({ id: '123', name: 'John' }),
      findById: vi.fn(),
      findAll: vi.fn()
    };
    const service = new UserService(mockRepository);
    const userData = { name: 'John', email: 'john@example.com' };
    const expected = { success: true, data: { id: '123', name: 'John' } };
    
    const result = await service.createUser(userData);
    
    expect(result).toEqual(expected);
    expect(mockRepository.save).toHaveBeenCalledWith(userData);
  });
  
  it('should return error result when repository fails', async () => {
    const mockRepository = {
      save: vi.fn().mockRejectedValue(new Error('Database error')),
      findById: vi.fn(),
      findAll: vi.fn()
    };
    const service = new UserService(mockRepository);
    const userData = { name: 'John', email: 'invalid' };
    
    const result = await service.createUser(userData);
    
    expect(result.success).toBe(false);
    expect(result.error).toBeInstanceOf(Error);
  });
});
```

## Error Testing

### Testing Error Conditions

```typescript
// ✅ Good: Error condition testing
describe('fn:validateUser', () => {
  it('should throw ValidationError for invalid email', () => {
    const invalidUser = { name: 'John', email: 'invalid-email' };
    
    expect(() => validateUser(invalidUser))
      .toThrow('Invalid email format');
  });
  
  it('should throw ValidationError for missing name', () => {
    const invalidUser = { name: '', email: 'john@example.com' };
    
    expect(() => validateUser(invalidUser))
      .toThrow('Name is required');
  });
});

// ✅ Good: Async error testing
describe('fn:fetchUserData', () => {
  it('should reject with error when user not found', async () => {
    const userId = 'nonexistent';
    
    await expect(fetchUserData(userId))
      .rejects
      .toThrow('User not found');
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
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html'],
    thresholds: {
      global: {
        branches: 100,
        functions: 100,
        lines: 100,
        statements: 100
      }
    },
    exclude: [
      'node_modules/**',
      'dist/**',
      '**/*.d.ts',
      '**/*.config.*',
      '**/coverage/**'
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
describe('fn:calculateDiscount', () => {
  it('should calculate 10% discount for premium users', () => {
    const result = calculateDiscount(100, 'premium');
    expect(result).toBe(90);
  });
  
  it('should calculate 5% discount for regular users', () => {
    const result = calculateDiscount(100, 'regular');
    expect(result).toBe(95);
  });
});

// ❌ Bad: Slow, interdependent tests
describe('UserService Integration', () => {
  it('should create user in database', async () => {
    // Slow database operation
    await database.connect();
    const user = await service.createUser(userData);
    globalTestUser = user; // Creates dependency
  });
  
  it('should find user created in previous test', async () => {
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
describe('fn:processPayment', () => {
  it('should process payment successfully with valid card', () => {});
  it('should reject payment when card is expired', () => {});
  it('should retry payment up to 3 times on network failure', () => {});
  it('should handle insufficient funds gracefully', () => {});
});

// ❌ Bad: Vague test names
describe('fn:processPayment', () => {
  it('should work', () => {});
  it('should fail', () => {});
  it('should retry', () => {});
});
```

### Test Documentation Comments

```typescript
// ✅ Good: Document complex test scenarios
describe('fn:complexBusinessLogic', () => {
  it('should calculate tier pricing based on volume and customer history', () => {
    // This test verifies the complex pricing algorithm that considers:
    // 1. Current order volume (>$1000 gets tier 1 pricing)
    // 2. Customer loyalty status (premium customers get additional 5% off)
    // 3. Seasonal promotions (active during Q4)
    
    const orderData = {
      amount: 1500,
      customerId: 'premium-customer-123',
      date: new Date('2023-12-15') // Q4 date
    };
    const expected = {
      basePrice: 1500,
      tierDiscount: 150,    // 10% tier 1 discount
      loyaltyDiscount: 75,  // 5% loyalty discount  
      finalPrice: 1275
    };
    
    const result = calculateTierPricing(orderData);
    
    expect(result).toEqual(expected);
  });
});
```

## Test Anti-Patterns

### Common Mistakes to Avoid

```typescript
// ❌ Bad: Testing implementation details
describe('rc:UserList', () => {
  it('should call useState with empty array', () => {
    const useStateSpy = vi.spyOn(React, 'useState');
    render(<UserList />);
    expect(useStateSpy).toHaveBeenCalledWith([]);
  });
});

// ❌ Bad: Overly complex test setup
describe('fn:complexFunction', () => {
  beforeEach(() => {
    // 50 lines of setup code
    setupComplexTestEnvironment();
    initializeMultipleMocks();
    configureTestDatabase();
  });
});

// ❌ Bad: Testing multiple things in one test
describe('fn:processOrder', () => {
  it('should validate input, calculate total, save to database, and send email', () => {
    // Testing too many responsibilities in one test
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
