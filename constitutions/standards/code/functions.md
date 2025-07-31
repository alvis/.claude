# Function Design Standards

*Standards for function design, parameters, interfaces, and code organization*

## Core Principles

### Single Responsibility

- **Functions should be <60 lines** - Break down complex operations
- **One clear purpose** - Each function should do one thing well
- **Avoid side effects** - Prefer pure functions when possible
- **Extract static methods** - Class methods that don't use `this` should be standalone functions

```typescript
// ✅ Good: Single responsibility
function calculateTax(amount: number, rate: number): number {
  return amount * rate;
}

function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency 
  }).format(amount);
}

// ❌ Bad: Multiple responsibilities
function calculateAndFormatTax(amount: number, rate: number, currency = 'USD'): string {
  const tax = amount * rate;
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency 
  }).format(tax);
}
```

### Pure Functions Preferred

```typescript
// ✅ Good: Pure function - no side effects
function add(a: number, b: number): number {
  return a + b;
}

function getUserDisplayName(user: User): string {
  return `${user.firstName} ${user.lastName}`;
}

// ❌ Bad: Impure function with side effects
let total = 0;
function addToTotal(value: number): void {
  total += value; // Modifies external state
}
```

### Always Declare Return Types

```typescript
// ✅ Good: Explicit return types
function getUserById(id: string): Promise<User | null> {
  return userRepository.findById(id);
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function processItems(items: Item[]): ProcessedItem[] {
  return items.map(item => processItem(item));
}

// ❌ Bad: Inferred return types
function getUserById(id: string) { // Return type unclear
  return userRepository.findById(id);
}
```

## Parameter Design

### Positional vs Object Parameters

#### Use Positional Parameters (≤2 parameters) When:
- **Intuitive, natural order** exists
- **All parameters are required**
- **Parameter order is commonly understood**

```typescript
// ✅ Good: Positional parameters
function add(a: number, b: number): number {
  return a + b;
}

function getUserById(id: string): Promise<User | null> {
  return userRepository.findById(id);
}

function formatDate(date: Date, format: string): string {
  return date.toLocaleDateString('en-US', { format });
}
```

#### Use Object Parameters (≥3 parameters) When:
- **Optional values or config-style flags** are present
- **Parameters are closely related**
- **Need named arguments for clarity**

```typescript
// ✅ Good: Object parameters for complex options
interface CreateUserOptions {
  name: string;
  email: string;
  role?: string;
  sendWelcomeEmail?: boolean;
  department?: string;
}

function createUser(options: CreateUserOptions): Promise<User> {
  const { name, email, role = 'user', sendWelcomeEmail = true, department } = options;
  // Implementation
}

// Usage
const user = await createUser({
  name: 'John Doe',
  email: 'john@example.com',
  role: 'admin',
  sendWelcomeEmail: false
});
```

### Parameter Object Naming

Use specific names based on the parameter's purpose:

```typescript
// ✅ Good: Specific parameter object names
interface SearchParams {
  query: string;
  limit?: number;
  offset?: number;
}

interface ValidationOptions {
  strict?: boolean;
  allowEmpty?: boolean;
  customRules?: ValidationRule[];
}

interface ApiRequestConfig {
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
}

interface UserContext {
  userId: string;
  permissions: string[];
  sessionId: string;
}

// ❌ Bad: Generic names
interface Options { } // Too vague
interface Data { }    // Too generic
interface Input { }   // Not descriptive
```

### Parameter Ordering

When using positional parameters, follow this order:

1. **Required identity fields** (id, key, name)
2. **Primary functional arguments** (data, content, source)
3. **Optional modifiers/flags** (options, config)
4. **Callbacks** (onSuccess, onError)
5. **Miscellaneous** (context, metadata)

```typescript
// ✅ Good: Logical parameter ordering
function updateUser(
  userId: string,                    // 1. Identity
  userData: UpdateUserData,          // 2. Primary data
  options: UpdateOptions = {},       // 3. Optional modifiers
  onSuccess?: (user: User) => void,  // 4. Callbacks
  context?: RequestContext           // 5. Miscellaneous
): Promise<User> {
  // Implementation
}
```

### Parameter Destructuring Safety

```typescript
// ✅ Good: Safe destructuring with defaults
function processUser(options: UserOptions = {}): User {
  const { name = 'Unknown', role = 'user', active = true } = options;
  // Safe - won't fail if options is undefined
}

// ✅ Good: Explicit optional parameter
function processUserSafe(options?: UserOptions): User {
  const { name = 'Unknown', role = 'user', active = true } = options || {};
  // Safe - handles undefined options
}

// ❌ Bad: Direct destructuring can fail
function processUserBad({ name = 'Unknown', role = 'user' }: UserOptions): User {
  // Will throw if called with undefined
}
```

## Interface Strategy

### Exported Functions - Always Separate Interfaces

```typescript
// ✅ Good: Separate interfaces for exported functions
export interface CreateUserParams {
  name: string;
  email: string;
  role?: string;
}

export interface CreateUserOptions {
  sendWelcomeEmail?: boolean;
  validateEmail?: boolean;
}

export function createUser(
  params: CreateUserParams, 
  options: CreateUserOptions = {}
): Promise<User> {
  // Implementation
}
```

### Internal Functions - Context-Dependent

```typescript
// ✅ Good: Inline types for simple internal functions
function formatUserName(user: { firstName: string; lastName: string }): string {
  return `${user.firstName} ${user.lastName}`;
}

// ✅ Good: Separate interface for complex internal functions
interface ValidationContext {
  strict: boolean;
  allowedDomains: string[];
  customRules: ValidationRule[];
}

function validateEmailWithContext(email: string, context: ValidationContext): boolean {
  // Complex validation logic
}
```

## Function Composition and Higher-Order Functions

### Function Composition

```typescript
// ✅ Good: Composable functions
function trim(str: string): string {
  return str.trim();
}

function toLowerCase(str: string): string {
  return str.toLowerCase();
}

function normalizeEmail(email: string): string {
  return toLowerCase(trim(email));
}

// ✅ Good: Higher-order function for composition
function pipe<T>(...fns: Array<(arg: T) => T>) {
  return (value: T): T => fns.reduce((acc, fn) => fn(acc), value);
}

const normalizeEmailPiped = pipe(trim, toLowerCase);
```

### Currying and Partial Application

```typescript
// ✅ Good: Curried functions for reusability
function multiply(factor: number) {
  return (value: number): number => value * factor;
}

const double = multiply(2);
const triple = multiply(3);

// Usage
const doubled = [1, 2, 3].map(double); // [2, 4, 6]
```

## Error Handling in Functions

### Explicit Error Handling

```typescript
// ✅ Good: Explicit error handling with specific types
function parseUser(input: unknown): User {
  if (typeof input !== 'object' || input === null) {
    throw new ValidationError('Input must be an object');
  }
  
  if (!('email' in input) || typeof input.email !== 'string') {
    throw new ValidationError('Email is required and must be a string');
  }
  
  return input as User;
}

// ✅ Good: Result type for error handling
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };

function safeParseUser(input: unknown): Result<User, ValidationError> {
  try {
    const user = parseUser(input);
    return { success: true, data: user };
  } catch (error) {
    return { success: false, error: error as ValidationError };
  }
}
```

## Async Function Patterns

### Promise-Based Functions

```typescript
// ✅ Good: Consistent async patterns
async function fetchUser(id: string): Promise<User | null> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(`Network error: ${error.message}`);
  }
}

// ✅ Good: Timeout handling
async function fetchWithTimeout<T>(
  promise: Promise<T>, 
  timeoutMs: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(() => reject(new Error('Request timeout')), timeoutMs);
  });
  
  return Promise.race([promise, timeout]);
}
```

## Function Documentation

### JSDoc Standards

```typescript
/**
 * Calculates the total price including tax for an order
 * @param subtotal - The subtotal amount before tax
 * @param taxRate - The tax rate as a decimal (e.g., 0.08 for 8%)
 * @param discountAmount - Optional discount to apply before tax calculation
 * @returns The total amount including tax
 * @throws {ValidationError} When subtotal is negative or tax rate is invalid
 */
function calculateTotal(
  subtotal: number, 
  taxRate: number, 
  discountAmount = 0
): number {
  if (subtotal < 0) {
    throw new ValidationError('Subtotal cannot be negative');
  }
  
  if (taxRate < 0 || taxRate > 1) {
    throw new ValidationError('Tax rate must be between 0 and 1');
  }
  
  const discountedSubtotal = Math.max(0, subtotal - discountAmount);
  return discountedSubtotal * (1 + taxRate);
}
```

## Performance Considerations

### Function Optimization

```typescript
// ✅ Good: Memoization for expensive calculations
const memoize = <T extends (...args: any[]) => any>(fn: T): T => {
  const cache = new Map();
  return ((...args: any[]) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
};

const expensiveCalculation = memoize((n: number): number => {
  // Complex calculation
  return Math.pow(n, 10) * Math.log(n);
});

// ✅ Good: Early returns to avoid deep nesting
function processUser(user: User): ProcessedUser {
  if (!user) {
    return null;
  }
  
  if (!user.isActive) {
    return { ...user, status: 'inactive' };
  }
  
  if (!user.permissions.length) {
    return { ...user, accessLevel: 'none' };
  }
  
  // Main processing logic
  return {
    ...user,
    accessLevel: calculateAccessLevel(user.permissions),
    lastProcessed: new Date()
  };
}
```

## Function Anti-Patterns

### Common Mistakes to Avoid

```typescript
// ❌ Bad: Functions doing too much
function processUserAndSendEmail(userData: any): void {
  // Validation
  if (!userData.email) throw new Error('Email required');
  
  // User creation
  const user = createUser(userData);
  
  // Email sending
  sendWelcomeEmail(user.email);
  
  // Logging
  console.log(`User ${user.id} created and email sent`);
}

// ✅ Good: Separate concerns
function processUser(userData: UserData): User {
  validateUserData(userData);
  return createUser(userData);
}

function sendWelcomeEmailToUser(user: User): Promise<void> {
  return sendWelcomeEmail(user.email);
}

// ❌ Bad: Modifying parameters
function updateUserAge(user: User, newAge: number): User {
  user.age = newAge; // Mutates input
  return user;
}

// ✅ Good: Immutable approach
function updateUserAge(user: User, newAge: number): User {
  return { ...user, age: newAge };
}
```