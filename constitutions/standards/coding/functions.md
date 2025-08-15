# Function Design Standards

_Standards for function design, parameters, interfaces, and code organization_

## Core Principles

### Single Responsibility

- **One clear purpose** - Each function should do one thing well
- **Functions should be <60 lines** - Break down complex operations (< 30 lines preferred)
- **Extract static methods** - Class methods that don't use `this` should be standalone functions
- **Avoid side effects** - Prefer pure functions when possible

```typescript
// ✅ GOOD: single responsibility
function calculateTax(amount: number, rate: number): number {
  return amount * rate;
}

function formatCurrency(amount: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(amount);
}

// ❌ BAD: multiple responsibilities
function calculateAndFormatTax(
  amount: number,
  rate: number,
  currency = "USD",
): string {
  const tax = amount * rate;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(tax);
}
```

### Always Declare Return Types

```typescript
// ✅ GOOD: explicit return types
function getUserById(id: string): Promise<User | null> {
  return userRepository.findById(id);
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function processItems(items: Item[]): ProcessedItem[] {
  return items.map((item) => processItem(item));
}

// ❌ BAD: inferred return types
function getUserById(id: string) {
  // return type unclear
  return userRepository.findById(id);
}
```

### Function Naming Consistency

- **Verb-first** for actions: `createUser`, `validateEmail`
- **is/has prefix** for booleans: `isValid`, `hasPermission`
- **get prefix** for accessors: `getUserName`, `getConfig`
- **on prefix** for handlers: `onClick`, `onSubmit`

### Return Type Consistency

```typescript
// ✅ GOOD: consistent return types
function findUser(id: string): User | null {
  // always returns User or null, never undefined
}

async function fetchUsers(): Promise<User[]> {
  // always returns array, never null/undefined
  return users || [];
}
```

## Pure Functions and Side Effects

### Pure Functions Preferred

Pure functions produce the same output for the same input and have no side effects. Use them for:

- **Data transformations** - Mapping, filtering, reducing
- **Calculations** - Math operations, aggregations
- **Formatters** - String formatting, date formatting
- **Validators** - Input validation, business rule checks
- **Utilities** - Helper functions, converters

```typescript
// ✅ GOOD: pure function - no side effects, deterministic
function add(a: number, b: number): number {
  return a + b;
}

// ❌ BAD: impure function with side effects
let total = 0;
function addToTotal(value: number): void {
  total += value; // modifies external state
}
```

### Segregate Side Effects

Keep pure business logic separate from side effects:

```typescript
// pure business logic
function calculateTotal(order: Order): number {
  return order.items.reduce((sum, item) => sum + item.price, 0);
}

// side effects in outer layer
async function processOrder(order: Order): Promise<void> {
  const total = calculateTotal(order);    // pure
  await saveOrder(order.id, total);       // side effect
}
```

### When Impure Functions Are Acceptable

Use impure functions for:

- **I/O operations** - Database queries, API calls, file operations
- **State management** - Redux actions, state updates
- **Event handlers** - User interactions, system events
- **Side effects** - Logging, analytics, notifications

```typescript
// ✅ GOOD: clearly impure for i/o
async function saveUser(user: User): Promise<void> {
  await database.users.insert(user);
  await emailService.sendWelcome(user.email);
  logger.info("User created", { userId: user.id });
}

// ✅ GOOD: event handler with side effects
function handleButtonClick(): void {
  analytics.track("button_clicked");
  updateUIState();
  showNotification("Action completed");
}
```

## Parameter Design

### Never Mutate Parameters

```typescript
// ❌ BAD: mutating parameters
function processUser(user: User): User {
  user.status = 'processed'; // never mutate inputs!
  return user;
}

// ✅ GOOD: return new object
function processUser(user: User): User {
  return { ...user, status: 'processed' };
}
```

### Positional vs Object Parameters

#### Use Positional Parameters (≤2 parameters) When

- **Intuitive, natural order** exists
- **All parameters are required**
- **Parameter order is commonly understood**

```typescript
// ✅ GOOD: positional parameters
function add(a: number, b: number): number {
  return a + b;
}

function getUserById(id: string): Promise<User | null> {
  return userRepository.findById(id);
}

function formatDate(date: Date, format: string): string {
  return date.toLocaleDateString("en-US", { format });
}
```

#### Use Object Parameters (≥3 parameters) When

- **Optional values or config-style flags** are present
- **Parameters are closely related**
- **Need named arguments for clarity**

```typescript
// ✅ GOOD: object parameters for complex options
interface CreateUserOptions {
  name: string;
  email: string;
  role?: string;
  sendWelcomeEmail?: boolean;
  department?: string;
}

function createUser(options: CreateUserOptions): Promise<User> {
  const {
    name,
    email,
    role = "user",
    sendWelcomeEmail = true,
    department,
  } = options;
  // implementation
}

// usage
const user = await createUser({
  name: "John Doe",
  email: "john@example.com",
  role: "admin",
  sendWelcomeEmail: false,
});
```

### Standard Parameter Names

Use these standard names consistently across the codebase:

#### params

Use as the default parameter name:

```typescript
function getUserProfile(params: { userId: string }): Promise<User> {
  return api.get(`/users/${params.userId}`);
}
```

#### options

Use for optional configuration:

```typescript
// ✅ GOOD: options parameter
interface FormatOptions {
  locale?: string;
  currency?: string;
  precision?: number;
}

function formatPrice(amount: number, options: FormatOptions = {}): string {
  const { locale = "en-US", currency = "USD", precision = 2 } = options;

  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits: precision,
  }).format(amount);
}
```

#### data

Use for primary data payload:

```typescript
function createUser(data: CreateUserData): Promise<User> {
  return api.post("/users", data);
}

function updateProfile(userId: string, data: UpdateProfileData): Promise<User> {
  return api.patch(`/users/${userId}`, data);
}
```

#### config

Use for initialization or complex configuration:

```typescript
interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  ssl?: boolean;
  poolSize?: number;
}

class Database {
  constructor(config: DatabaseConfig) {
    this.config = config;
    this.connect();
  }
}
```

#### context

Use for request context or execution context:

```typescript
interface RequestContext {
  user: User;
  requestId: string;
  permissions: string[];
}

function checkAccess(resource: Resource, context: RequestContext): boolean {
  if (resource.ownerId === context.user.id) return true;
  if (context.permissions.includes("admin")) return true;
  return false;
}
```

#### details

Use for additional information or metadata:

```typescript
interface ErrorDetails {
  code: string;
  field?: string;
  originalError?: Error;
}

function logError(message: string, details: ErrorDetails): void {
  logger.error(message, {
    errorCode: details.code,
    field: details.field,
    stack: details.originalError?.stack,
  });
}
```

### Parameter Destructuring Patterns

#### Safe Destructuring

```typescript
// ✅ GOOD: explicit optional parameter
function processUser(options?: UserOptions): User {
  const { name = "Unknown", role = "user", active = true } = { ...options };
  // safe - handles undefined options
}

// ❌ BAD: direct destructuring can fail
function processUserBad({
  name = "Unknown",
  role = "user",
}: UserOptions): User {
  // will throw if called with undefined
}
```

#### Advanced Destructuring Patterns

```typescript
// ✅ GOOD: destructure in parameter list
function createUser({ name, email, role = "user" }: CreateUserData): User {

  return {
    id: generateId(),
    name,
    email,
    role,
    createdAt: new Date(),
  };
}

// ✅ GOOD: destructure with rename
function processOrder({
  items,
  customer: buyer, // rename for clarity
  discount = 0,
}: OrderData): ProcessedOrder {
  const total = calculateTotal(items, discount);

  return { items, buyer, total };
}

// ✅ GOOD: nested destructuring
interface Config {
  server: {
    host: string;
    port: number;
  };
  database: {
    url: string;
  };
}

function initialize({
  server: { host, port },
  database: { url },
}: Config): void {
  startServer(host, port);
  connectDatabase(url);
}
```

#### Rest Parameters

```typescript
// ✅ GOOD: rest parameters for variable arguments
function combine(separator: string, ...parts: string[]): string {
  return parts.filter(Boolean).join(separator);
}

// ✅ GOOD: rest with destructuring
function logEvent(eventName: string, { userId, ...metadata }: EventData): void {
  logger.info(eventName, {
    userId,
    metadata,
    timestamp: Date.now(),
  });
}
```

## Interface Strategy

### Exported Functions - Always Separate Interfaces

```typescript
// ✅ GOOD: separate interfaces for exported functions
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
  options?: CreateUserOptions,
): Promise<User> {
  // implementation
}
```

### Internal Functions - Context-Dependent

```typescript
// ✅ GOOD: separate interface for internal functions
interface ValidationContext {
  strict: boolean;
  allowedDomains: string[];
  customRules: ValidationRule[];
}

function validateEmailWithContext(
  email: string,
  context: ValidationContext,
): boolean {
  // Complex validation logic
}
```

## Immutability Patterns

### Default to Immutability

Always prefer immutable operations unless performance requires mutation:

```typescript
// ✅ GOOD: immutable array operations
const numbers = [1, 2, 3];
const doubled = numbers.map((n) => n * 2); // [2, 4, 6]
const filtered = numbers.filter((n) => n > 1); // [2, 3]
const sum = numbers.reduce((acc, n) => acc + n, 0); // 6

// ✅ GOOD: immutable object updates
const user = { name: "John", age: 30 };
const updated = { ...user, age: 31 };
const withEmail = { ...user, email: "john@example.com" };

// ❌ BAD: mutating arrays
const numbers = [1, 2, 3];
numbers.push(4); // Mutation
numbers[0] = 10; // Mutation

// ❌ BAD: mutating objects
const user = { name: "John", age: 30 };
user.age = 31; // Mutation
```

### When Mutation Is Acceptable

Mutation is acceptable for:

- **Performance-critical code** - Large data sets, tight loops
- **Local scope only** - Within function boundaries
- **Explicit documentation** - Clear comments explaining why

```typescript
// ✅ GOOD: local mutation for performance
function processLargeDataSet(items: Item[]): ProcessedItem[] {
  // NOTE: mutating local array for performance with 1M+ items
  const results: ProcessedItem[] = [];

  for (const item of items) {
    if (item.isValid) {
      results.push(processItem(item)); // local mutation OK
    }
  }

  return results;
}
```

## Text Joining Patterns

### Always Use Array.join() for Multi-line Text

```typescript
// ✅ GOOD: array.join for clean multi-line strings
const errorMessage = [
  "Validation failed:",
  "- Email is required",
  "- Password must be at least 8 characters",
  "- Username already taken",
].join("\n");

// ❌ BAD: string concatenation
let message = "Validation failed:\n";
message += "- Email is required\n";
message += "- Password must be at least 8 characters\n";
```

## Anti-Patterns to Avoid

### Common Function Mistakes

```typescript
// ❌ BAD: functions doing too much
function processUserAndSendEmail(userData: any): void {
  // validation
  if (!userData.email) throw new Error("Email required");

  // user creation
  const user = createUser(userData);

  // email sending
  sendWelcomeEmail(user.email);

  // logging
  console.log(`User ${user.id} created and email sent`);
}

// ✅ GOOD: separate concerns
function processUser(userData: UserData): User {
  validateUserData(userData);
  return createUser(userData);
}

function sendWelcomeEmailToUser(user: User): Promise<void> {
  return sendWelcomeEmail(user.email);
}

// ❌ BAD: modifying parameters
function updateUserAge(user: User, newAge: number): User {
  user.age = newAge; // mutates input
  return user;
}

// ✅ GOOD: immutable approach
function updateUserAge(user: User, newAge: number): User {
  return { ...user, age: newAge };
}
```

## Key Principles Summary

1. **Never mutate function parameters**
2. **Use `const` by default and avoid `let`**
3. **Keep side effects at application edges**
4. **Allow local mutation for performance**
5. **Use array join for multi-line text**
6. **Keep functions small** (< 30 lines preferred)
7. **Extract complex logic** into helper functions
8. **Single responsibility** per function