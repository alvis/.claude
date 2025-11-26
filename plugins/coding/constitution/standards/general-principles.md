# General Coding Principles

_Core principles that guide all development work across the codebase_

## Thinking Frameworks

### Model-Based, Systems Thinking

Approach problems mathematically and systemically:

```typescript
// ✅ GOOD: Think in systems and models
interface CacheStrategy {
  get(key: string): Promise<Value | null>;
  set(key: string, value: Value, ttl?: number): Promise<void>;
  invalidate(pattern: string): Promise<void>;
}

// Model the system: Cache → Repository → Database
// Reason about: What if cache fails? What if DB is slow?
// Optimize for: Long-term sustainability, not quick fixes
```

**Application**:
- Map systems and their interactions before coding
- Consider long-term consequences, not just immediate fixes
- Reason quantitatively where appropriate (complexity, performance)

### Listen First, Speak Last

Gather complete context before acting:

```typescript
// ✅ GOOD: Read existing patterns before creating new ones
// 1. Search codebase for similar functionality
// 2. Understand current patterns and conventions
// 3. Only then propose solution aligned with existing system
```

**Application**:
- Read relevant code before modifying
- Check existing implementations for patterns
- Ask clarifying questions when requirements are ambiguous
- Gather input before making architectural decisions

### "What Am I Missing?" Checkpoint

Before major decisions, explicitly check for blindspots:

**Questions to ask**:
- What assumptions am I making?
- What information don't I have?
- What could go wrong that I haven't considered?
- Who else should weigh in?
- What are the unintended consequences?

```typescript
// ✅ GOOD: Document key decisions and uncertainties
/**
 * Decision: Using LRU cache with 1-hour TTL
 *
 * Assumptions:
 * - Data changes infrequently (< 1/hour)
 * - Memory is available for cache
 * - Cache misses are acceptable
 *
 * Uncertainties:
 * - Actual data update frequency unknown
 * - Cache memory impact not measured
 *
 * Monitoring: Track cache hit rate, memory usage
 */
```

## Core Principles

### Single Responsibility Principle

Each module, class, or function should have one clear purpose:

```typescript
// ✅ GOOD: single responsibility
class EmailValidator {
  validate(email: string): boolean { ... }
}

// ❌ BAD: multiple responsibilities
class EmailManager {
  validate(email: string): boolean { ... }
  send(to: string, subject: string, body: string): void { ... }
  saveToDatabase(email: Email): void { ... }
  // doing too much!
}
```

### DRY (Don't Repeat Yourself)

Eliminate code duplication through abstraction:

```typescript
// ❌ BAD: repeated logic
function calculateUserDiscount(user: User): number {
  if (user.membershipLevel === "gold") {
    return user.purchaseAmount * 0.2;
  }
  return user.purchaseAmount * 0.1;
}

// ✅ GOOD: extracted common logic
function calculateDiscount(amount: number, isPremium: boolean): number {
  return amount * (isPremium ? 0.2 : 0.1);
}

function calculateUserDiscount(user: User): number {
  return calculateDiscount(user.purchaseAmount, user.membershipLevel === "gold");
}
```

### Readability Over Cleverness

Write code that's easy to understand:

```typescript
// ❌ BAD: clever but unclear
const isValid = !!(user && user.email && +user.age >= 18);

// ✅ GOOD: clear and explicit
function isValidUser(user: User | null): boolean {
  if (!user?.email) return false;
  return Number(user.age) >= 18;
}
```

### Maintainability First

Structure code for easy modification:

```typescript
// ✅ GOOD: configurable and maintainable
const RolePermissions = {
  admin: ["read", "write", "drop", "manage"],
  editor: ["read", "write"],
  viewer: ["read"],
} as const;

function hasPermission(role: string, permission: string): boolean {
  return RolePermissions[role]?.includes(permission) || false;
}

// ❌ BAD: hard to maintain
function hasPermission(role: string, permission: string): boolean {
  if (role === "admin") return true;
  if (role === "editor" && (permission === "read" || permission === "write")) {
    return true;
  }
  // ... more hardcoded conditions
}
```

### Zero Wrapper Tolerance

Functions that merely wrap other functions without adding value are **STRICTLY PROHIBITED**:

```typescript
// ❌ BAD: pointless wrapper function
function getUser(id: string): Promise<User> {
  return userRepository.findById(id); // no value added!
}

// ✅ GOOD: wrapper adds actual value
class UserService {
  async findUser(id: string): Promise<User> {
    const cached = await this.cache.get(`user:${id}`);
    if (cached) return cached;
    
    const user = await this.repo.find(id);
    if (!user) throw new UserNotFoundError(`User ${id} not found`);
    
    await this.cache.set(`user:${id}`, user, { ttl: 3600 });
    return user;
  }
}
```

### Scalability by Design

Write code that accommodates growth:

```typescript
// ✅ GOOD: scalable design with strategy pattern
interface PaymentProcessor {
  process(amount: number): Promise<PaymentResult>;
}

class PaymentService {
  private processors = new Map<string, PaymentProcessor>();

  registerProcessor(name: string, processor: PaymentProcessor): void {
    this.processors.set(name, processor);
  }

  async processPayment(method: string, amount: number): Promise<PaymentResult> {
    const processor = this.processors.get(method);
    if (!processor) throw new Error(`Payment method ${method} not supported`);
    return processor.process(amount);
  }
}
```

## Pattern Consistency

### Match Existing Patterns

Before implementing something new:

1. **Check existing implementations** - Look for similar functionality
2. **Follow established conventions** - Use the same patterns
3. **Maintain consistency** - Don't introduce new patterns without team discussion

```typescript
// if the codebase uses this pattern:
class UserService {
  constructor(private repository: UserRepository) {}
  async findById(id: string): Promise<User | null> { ... }
}

// ✅ GOOD: follow the same pattern
class ProductService {
  constructor(private repository: ProductRepository) {}
  async findById(id: string): Promise<Product | null> { ... }
}

// ❌ BAD: different pattern without justification
class ProductManager {
  static async getProduct(id: string): Promise<Product | null> { ... }
}
```

### Defensive Programming

Anticipate and handle edge cases:

```typescript
// ✅ GOOD: guard clauses
function calculatePrice(basePrice: number, discount = 0, tax = 0): number {
  if (basePrice < 0) throw new Error("Base price cannot be negative");
  
  const subtotal = basePrice - (discount * basePrice);
  return subtotal + (tax * subtotal);
}
```

### Optimize Thoughtfully

Don't optimize prematurely, but be aware of performance:

```typescript
// ✅ GOOD: cache expensive computations
const fibonacci = (() => {
  const cache = new Map<number, number>();
  return function fib(n: number): number {
    if (n <= 1) return n;
    if (cache.has(n)) return cache.get(n)!;
    
    const result = fib(n - 1) + fib(n - 2);
    cache.set(n, result);
    return result;
  };
})();

// use appropriate data structures
const userIndex = new Map<string, User>(); // O(1) lookup
```

## Anti-Patterns

### Common Mistakes to Avoid

1. **Wrapper Functions Without Value**
   - Problem: Functions that just call other functions without adding value
   - Solution: Only create wrappers that add caching, validation, or transformation
   - Example: `function getUser(id) { return userRepo.find(id); }` // unnecessary

2. **Premature Optimization**
   - Problem: Optimizing code before identifying actual bottlenecks
   - Solution: Profile first, optimize second

3. **Clever Code Over Clear Code**
   - Problem: Writing "smart" code that's hard to understand
   - Solution: Prioritize readability and maintainability

<IMPORTANT>

## CRITICAL: Never Suppress Errors - Fix Root Causes

**DO NOT use suppression comments** (`eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`, etc.) to mask underlying problems. It is **VERY RARE** that they are necessary.

### The Problem with Suppression Comments:

- **Masks real issues** - Problem continues to exist, just hidden
- **Creates technical debt** - Future maintainers won't understand why code is structured oddly
- **Breaks continuous improvement** - Can't identify and fix root causes
- **Violates DRY principle** - You're working around a problem instead of fixing it

### Correct Approach:

1. **Understand the root cause** - Use diagnostic tools to see the underlying issue
2. **Refactor or fix** - Change the code structure, types, or logic to resolve it properly
3. **Test the solution** - Verify that the fix is correct and complete
4. **Document if needed** - Only add comments to explain legitimate design decisions

### Example:

```typescript
// ❌ BAD: Suppressing the error
// @ts-ignore - types are broken here
const user = getData() as User;

// ✅ GOOD: Fixing the actual problem
interface DataResponse {
  success: boolean;
  data: unknown;
}

function processData(response: DataResponse): User {
  if (!response.success || !isValidUser(response.data)) {
    throw new Error("Invalid user data in response");
  }
  return response.data; // Now TypeScript knows this is User
}
```

</IMPORTANT>
