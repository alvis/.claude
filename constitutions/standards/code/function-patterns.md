# Function Patterns

_Standards for function design, pure functions, immutability, and parameter conventions_

## Pure Functions

### When to Use Pure Functions

Pure functions produce the same output for the same input and have no side effects. Use them for:

- **Data transformations** - Mapping, filtering, reducing
- **Calculations** - Math operations, aggregations
- **Formatters** - String formatting, date formatting
- **Validators** - Input validation, business rule checks
- **Utilities** - Helper functions, converters

```typescript
// ✅ Good: Pure function - no side effects, deterministic
function calculateDiscount(price: number, discountPercent: number): number {
  return price * (1 - discountPercent / 100);
}

// ✅ Good: Pure transformation
function formatUserName(firstName: string, lastName: string): string {
  return `${firstName} ${lastName}`.trim();
}

// ❌ Bad: Impure - modifies external state
let totalPrice = 0;
function addToTotal(price: number): void {
  totalPrice += price; // Side effect
}

// ❌ Bad: Impure - non-deterministic
function generateId(): string {
  return Date.now().toString(); // Different output each time
}
```

### When Impure Functions Are Acceptable

Use impure functions for:

- **I/O operations** - Database queries, API calls, file operations
- **State management** - Redux actions, state updates
- **Event handlers** - User interactions, system events
- **Side effects** - Logging, analytics, notifications

```typescript
// ✅ Good: Clearly impure for I/O
async function saveUser(user: User): Promise<void> {
  await database.users.insert(user);
  await emailService.sendWelcome(user.email);
  logger.info("User created", { userId: user.id });
}

// ✅ Good: Event handler with side effects
function handleButtonClick(): void {
  analytics.track("button_clicked");
  updateUIState();
  showNotification("Action completed");
}
```

## Immutability Patterns

### Default to Immutability

Always prefer immutable operations unless performance requires mutation:

```typescript
// ✅ Good: Immutable array operations
const numbers = [1, 2, 3];
const doubled = numbers.map((n) => n * 2); // [2, 4, 6]
const filtered = numbers.filter((n) => n > 1); // [2, 3]
const sum = numbers.reduce((acc, n) => acc + n, 0); // 6

// ✅ Good: Immutable object updates
const user = { name: "John", age: 30 };
const updated = { ...user, age: 31 };
const withEmail = { ...user, email: "john@example.com" };

// ❌ Bad: Mutating arrays
const numbers = [1, 2, 3];
numbers.push(4); // Mutation
numbers[0] = 10; // Mutation

// ❌ Bad: Mutating objects
const user = { name: "John", age: 30 };
user.age = 31; // Mutation
```

### When Mutation Is Acceptable

Mutation is acceptable for:

- **Performance-critical code** - Large data sets, tight loops
- **Local scope only** - Within function boundaries
- **Explicit documentation** - Clear comments explaining why

```typescript
// ✅ Good: Local mutation for performance
function processLargeDataSet(items: Item[]): ProcessedItem[] {
  // NOTE: mutating local array for performance with 1M+ items
  const results: ProcessedItem[] = [];

  for (const item of items) {
    if (item.isValid) {
      results.push(processItem(item)); // Local mutation OK
    }
  }

  return results;
}

// ✅ Good: Documented mutation for performance
class PerformanceOptimizedBuffer {
  private buffer: number[];

  // WARNING: this mutation is intentional for performance
  // do not refactor to immutable without benchmarking
  append(value: number): void {
    this.buffer.push(value);
  }
}
```

## Text Joining Patterns

### Always Use Array.join() for Multi-line Text

```typescript
// ✅ Good: Array.join for clean multi-line strings
const errorMessage = [
  "Validation failed:",
  "- Email is required",
  "- Password must be at least 8 characters",
  "- Username already taken",
].join("\n");

// ✅ Good: Building complex text structures
function generateReport(data: ReportData): string {
  const lines = [
    `Report for ${data.date}`,
    "=".repeat(50),
    "",
    "Summary:",
    `Total Sales: ${data.totalSales}`,
    `New Customers: ${data.newCustomers}`,
    "",
    "Details:",
    ...data.items.map((item) => `- ${item.name}: ${item.value}`),
  ];

  return lines.join("\n");
}

// ❌ Bad: String concatenation
let message = "Validation failed:\n";
message += "- Email is required\n";
message += "- Password must be at least 8 characters\n";

// ❌ Bad: Template literals for many lines
const message = `Validation failed:
- Email is required
- Password must be at least 8 characters
- Username already taken`;
```

## Parameter Naming Conventions

### Standard Parameter Names

Use these standard names consistently across the codebase:

#### params

Use for route/path parameters:

```typescript
// ✅ Good: Route parameters
function getUserProfile(params: { userId: string }): Promise<User> {
  return api.get(`/users/${params.userId}`);
}

// Next.js page component
export default function UserPage({ params }: { params: { id: string } }) {
  const user = await getUser(params.id);
  return <UserProfile user={user} />;
}
```

#### query

Use for URL query parameters:

```typescript
// ✅ Good: Query parameters
function searchUsers(query: {
  search?: string;
  page?: number;
  limit?: number;
}): Promise<UserList> {
  const params = new URLSearchParams();
  if (query.search) params.set("q", query.search);
  if (query.page) params.set("page", query.page.toString());
  if (query.limit) params.set("limit", query.limit.toString());

  return api.get(`/users?${params}`);
}
```

#### options

Use for optional configuration:

```typescript
// ✅ Good: Options parameter
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
// ✅ Good: Data parameter for mutations
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
// ✅ Good: Config parameter
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
// ✅ Good: Context parameter
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
// ✅ Good: Details parameter
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

## Positional vs Object Parameters

### When to Use Positional Parameters

Use positional parameters for:

- **1-3 required parameters**
- **Simple, clear relationships**
- **Common patterns** (id, callback)

```typescript
// ✅ Good: Clear positional parameters
function getUser(id: string): Promise<User>;
function calculateArea(width: number, height: number): number;
function addEventListener(event: string, handler: EventHandler): void;

// ✅ Good: Optional parameter at end
function formatDate(date: Date, format?: string): string;
```

### When to Use Object Parameters

Use object parameters for:

- **3+ parameters**
- **Multiple optional parameters**
- **Related parameters**
- **Future extensibility**

```typescript
// ✅ Good: Object for multiple options
interface SearchOptions {
  query: string;
  filters?: FilterOptions;
  sort?: SortOptions;
  pagination?: PaginationOptions;
}

function searchProducts(options: SearchOptions): Promise<ProductList> {
  // Implementation
}

// ❌ Bad: Too many positional parameters
function searchProducts(
  query: string,
  category?: string,
  minPrice?: number,
  maxPrice?: number,
  sortBy?: string,
  sortOrder?: "asc" | "desc",
  page?: number,
  limit?: number,
): Promise<ProductList>;
```

## Parameter Destructuring

### Function Parameter Destructuring

```typescript
// ✅ Good: Destructure in parameter list
function createUser({ name, email, role = "user" }: CreateUserData): User {
  return {
    id: generateId(),
    name,
    email,
    role,
    createdAt: new Date(),
  };
}

// ✅ Good: Destructure with rename
function processOrder({
  items,
  customer: buyer, // Rename for clarity
  discount = 0,
}: OrderData): ProcessedOrder {
  const total = calculateTotal(items, discount);
  return { items, buyer, total };
}

// ✅ Good: Nested destructuring
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

### Rest Parameters

```typescript
// ✅ Good: Rest parameters for variable arguments
function combine(separator: string, ...parts: string[]): string {
  return parts.filter(Boolean).join(separator);
}

// ✅ Good: Rest with destructuring
function logEvent(eventName: string, { userId, ...metadata }: EventData): void {
  logger.info(eventName, {
    userId,
    metadata,
    timestamp: Date.now(),
  });
}
```

## Function Organization

### Parameter Order

1. **Required parameters first**
2. **Optional parameters last**
3. **Callback/handler last**
4. **Options object for multiple optionals**

```typescript
// ✅ Good: Logical parameter order
function createButton(
  text: string, // Required
  onClick: () => void, // Required callback
  options?: ButtonOptions, // Optional config
): ButtonElement;

function fetchData<T>(
  url: string, // Required
  options?: RequestOptions, // Optional
  onProgress?: ProgressCallback, // Optional callback
): Promise<T>;
```

### Default Parameters

```typescript
// ✅ Good: Defaults in destructuring
function createLogger({
  level = "info",
  format = "json",
  destination = "console",
}: LoggerOptions = {}): Logger {
  // Implementation
}

// ✅ Good: Defaults for primitives
function delay(ms: number = 1000): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

## Best Practices

### Function Length

- **Keep functions small** (< 20 lines preferred)
- **Extract complex logic** into helper functions
- **Single responsibility** per function

### Naming Consistency

- **Verb-first** for actions: `createUser`, `validateEmail`
- **is/has prefix** for booleans: `isValid`, `hasPermission`
- **get prefix** for accessors: `getUserName`, `getConfig`
- **on prefix** for handlers: `onClick`, `onSubmit`

### Return Type Consistency

```typescript
// ✅ Good: Consistent return types
function findUser(id: string): User | null {
  // Always returns User or null, never undefined
}

async function fetchUsers(): Promise<User[]> {
  // Always returns array, never null/undefined
  return users || [];
}

// ✅ Good: Explicit union types
function parseNumber(value: string): number | Error {
  const num = Number(value);
  if (isNaN(num)) {
    return new Error("Invalid number");
  }
  return num;
}
```
