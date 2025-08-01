# General Coding Principles

_Core principles that guide all development work across the codebase_

## Fundamental Principles

### Code Quality Standards

- **Prioritize readability and maintainability** - Code is read far more often than it's written
- **Write self-explanatory code** - Use meaningful variable and function names
- **Follow the DRY principle** - Don't Repeat Yourself to minimize redundancy
- **Ensure scalability** - Allow for future extensions with minimal changes
- **Follow established patterns** - Match existing code style, structure, and templates
- **Test-driven mindset** - Write tests (or stubs) alongside code as you develop

### Single Responsibility Principle

Each module, class, or function should have one clear purpose:

```typescript
// ✅ Good: Single responsibility
class EmailValidator {
  validate(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}

class EmailSender {
  async send(to: string, subject: string, body: string): Promise<void> {
    // Send email logic
  }
}

// ❌ Bad: Multiple responsibilities
class EmailManager {
  validate(email: string): boolean {}
  send(to: string, subject: string, body: string): void {}
  saveToDatabase(email: Email): void {}
  generateTemplate(type: string): string {}
}
```

### DRY (Don't Repeat Yourself)

Eliminate code duplication through abstraction:

```typescript
// ❌ Bad: Repeated logic
function calculateUserDiscount(user: User): number {
  if (user.membershipLevel === "gold") {
    return user.purchaseAmount * 0.2;
  }
  return user.purchaseAmount * 0.1;
}

function calculateProductDiscount(product: Product): number {
  if (product.category === "premium") {
    return product.price * 0.2;
  }
  return product.price * 0.1;
}

// ✅ Good: Extracted common logic
function calculateDiscount(amount: number, isPremium: boolean): number {
  const discountRate = isPremium ? 0.2 : 0.1;
  return amount * discountRate;
}

function calculateUserDiscount(user: User): number {
  return calculateDiscount(
    user.purchaseAmount,
    user.membershipLevel === "gold",
  );
}

function calculateProductDiscount(product: Product): number {
  return calculateDiscount(product.price, product.category === "premium");
}
```

### Readability Over Cleverness

Write code that's easy to understand:

```typescript
// ❌ Bad: Clever but unclear
const isValid = !!(user && user.email && +user.age >= 18);

// ✅ Good: Clear and explicit
const hasUser = user !== null && user !== undefined;
const hasEmail = user?.email !== undefined;
const isAdult = Number(user?.age) >= 18;
const isValid = hasUser && hasEmail && isAdult;

// ✅ Even better: Extract to function
function isValidUser(user: User | null): boolean {
  if (!user || !user.email) {
    return false;
  }

  return Number(user.age) >= 18;
}
```

### Maintainability First

Structure code for easy modification:

```typescript
// ✅ Good: Configurable and maintainable
const UserRoles = {
  ADMIN: "admin",
  EDITOR: "editor",
  VIEWER: "viewer",
} as const;

const RolePermissions = {
  [UserRoles.ADMIN]: ["read", "write", "delete", "manage"],
  [UserRoles.EDITOR]: ["read", "write"],
  [UserRoles.VIEWER]: ["read"],
} as const;

function hasPermission(role: string, permission: string): boolean {
  return RolePermissions[role]?.includes(permission) || false;
}

// ❌ Bad: Hard to maintain
function hasPermission(role: string, permission: string): boolean {
  if (role === "admin") {
    return true;
  }
  if (role === "editor" && (permission === "read" || permission === "write")) {
    return true;
  }
  if (role === "viewer" && permission === "read") {
    return true;
  }
  return false;
}
```

### Scalability by Design

Write code that accommodates growth:

```typescript
// ✅ Good: Scalable design with strategy pattern
interface PaymentProcessor {
  process(amount: number): Promise<PaymentResult>;
}

class StripeProcessor implements PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // Stripe-specific logic
  }
}

class PayPalProcessor implements PaymentProcessor {
  async process(amount: number): Promise<PaymentResult> {
    // PayPal-specific logic
  }
}

class PaymentService {
  private processors: Map<string, PaymentProcessor> = new Map();

  registerProcessor(name: string, processor: PaymentProcessor): void {
    this.processors.set(name, processor);
  }

  async processPayment(method: string, amount: number): Promise<PaymentResult> {
    const processor = this.processors.get(method);
    if (!processor) {
      throw new Error(`Payment method ${method} not supported`);
    }
    return processor.process(amount);
  }
}
```

### Test-Driven Development

Write tests alongside implementation:

```typescript
// 1. Write test first
describe("fn:calculateDiscount", () => {
  it("should apply 20% discount for premium customers", () => {
    const amount = 100;
    const isPremium = true;
    const expected = 20;

    const result = calculateDiscount(amount, isPremium);

    expect(result).toBe(expected);
  });
});

// 2. Then implement
function calculateDiscount(amount: number, isPremium: boolean): number {
  const discountRate = isPremium ? 0.2 : 0.1;
  return amount * discountRate;
}
```

## Pattern Following

### Match Existing Patterns

Before implementing something new:

1. **Check existing implementations** - Look for similar functionality
2. **Follow established conventions** - Use the same patterns
3. **Maintain consistency** - Don't introduce new patterns without team discussion

```typescript
// If the codebase uses this pattern for services:
class UserService {
  constructor(private repository: UserRepository) {}

  async findById(id: string): Promise<User | null> {
    return this.repository.findOne(id);
  }
}

// ✅ Good: Follow the same pattern
class ProductService {
  constructor(private repository: ProductRepository) {}

  async findById(id: string): Promise<Product | null> {
    return this.repository.findOne(id);
  }
}

// ❌ Bad: Different pattern
class ProductManager {
  static async getProduct(id: string): Promise<Product | null> {
    // Different approach
  }
}
```

### Code Organization

Keep related functionality together:

```typescript
// ✅ Good: Cohesive module
// user/user.service.ts
export class UserService {
  constructor(
    private repository: UserRepository,
    private emailService: EmailService,
  ) {}

  async createUser(data: CreateUserDto): Promise<User> {
    const user = await this.repository.create(data);
    await this.emailService.sendWelcome(user.email);
    return user;
  }
}

// user/user.repository.ts
export class UserRepository {
  async create(data: CreateUserDto): Promise<User> {
    // Database logic
  }
}

// user/user.types.ts
export interface User {
  id: string;
  email: string;
  name: string;
}
```

## Language and Framework Usage

### Use Modern JavaScript/TypeScript Features

Leverage ES6+ features for cleaner code:

```typescript
// ✅ Good: Modern features
// Arrow functions
const double = (n: number): number => n * 2;

// Destructuring
const { name, email } = user;

// Template literals
const message = `Welcome ${name}!`;

// Optional chaining
const city = user?.address?.city;

// Nullish coalescing
const port = process.env.PORT ?? 3000;

// Array methods
const activeUsers = users.filter((user) => user.isActive);
const userNames = users.map((user) => user.name);
```

### Avoid Deprecated Patterns

Stay current with best practices:

```typescript
// ❌ Bad: Deprecated patterns
var name = "John"; // Use const/let
arguments.callee; // Deprecated
with (obj) {
} // Deprecated

// ✅ Good: Modern alternatives
const name = "John";
const args = [...arguments]; // Or use rest parameters
// Use explicit property access instead of 'with'
```

## Error Prevention

### Defensive Programming

Anticipate and handle edge cases:

```typescript
// ✅ Good: Defensive checks
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("Division by zero");
  }
  return a / b;
}

function processUser(user: User | null | undefined): void {
  if (!user) {
    console.warn("No user provided");
    return;
  }

  // Process user safely
}

// ✅ Good: Guard clauses
function calculatePrice(
  basePrice: number,
  discount?: number,
  tax?: number,
): number {
  if (basePrice < 0) {
    throw new Error("Base price cannot be negative");
  }

  const discountAmount = (discount ?? 0) * basePrice;
  const subtotal = basePrice - discountAmount;
  const taxAmount = (tax ?? 0) * subtotal;

  return subtotal + taxAmount;
}
```

## Performance Considerations

### Optimize Thoughtfully

Don't optimize prematurely, but be aware of performance:

```typescript
// ✅ Good: Efficient when needed
// Cache expensive computations
const fibonacci = (() => {
  const cache = new Map<number, number>();

  return function fib(n: number): number {
    if (n <= 1) return n;

    if (cache.has(n)) {
      return cache.get(n)!;
    }

    const result = fib(n - 1) + fib(n - 2);
    cache.set(n, result);
    return result;
  };
})();

// Use appropriate data structures
const userIndex = new Map<string, User>(); // O(1) lookup
const sortedUsers = [...users].sort((a, b) => a.name.localeCompare(b.name));
```

## Continuous Improvement

### Refactor Regularly

Improve code quality over time:

1. **Boy Scout Rule** - Leave code better than you found it
2. **Incremental improvements** - Small, safe refactorings
3. **Update documentation** - Keep docs in sync with code
4. **Remove dead code** - Delete unused functionality
5. **Modernize patterns** - Update to current best practices

### Learn from Code Reviews

- Accept feedback gracefully
- Apply lessons to future code
- Share knowledge with team
- Document decisions and rationale
