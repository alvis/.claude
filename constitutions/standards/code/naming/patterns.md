# Naming Patterns and Common Conventions

_Common patterns, anti-patterns, and conventions for consistent naming across the codebase_

## Core Pattern Principles

### MUST Follow Rules

- **MUST be consistent** - Same pattern for similar concepts
- **MUST avoid reserved words** - Never use language keywords
- **MUST indicate plurality** - Clear distinction between single/multiple
- **MUST avoid ambiguity** - Names should have one clear meaning
- **MUST match context** - Use domain-appropriate terminology

### SHOULD Follow Guidelines

- **SHOULD follow conventions** - Framework and library patterns
- **SHOULD group logically** - Related items share prefixes/suffixes
- **SHOULD indicate relationships** - Clear parent-child naming
- **SHOULD be pronounceable** - Avoid unpronounceable abbreviations

## Function Naming Patterns

### Standard Verb Patterns

```typescript
// ✅ Good: Consistent verb usage

// Data Retrieval (Sync/Async)
function getUser(id: string): User | null; // Sync, may be cached
function fetchUser(id: string): Promise<User>; // Async, external source
function findUser(criteria: SearchCriteria): User | null; // Search operation
function listUsers(): User[]; // Get all items
function retrieveUserData(id: string): Promise<UserData>; // Complex async operation

// Data Manipulation
function createUser(data: CreateUserData): Promise<User>;
function updateUser(id: string, data: UpdateData): Promise<User>;
function deleteUser(id: string): Promise<void>;
function saveUser(user: User): Promise<User>; // Create or update
function insertUser(user: User): Promise<User>; // Explicit create

// Validation and Checks
function validateEmail(email: string): ValidationResult;
function isValidEmail(email: string): boolean;
function checkUserExists(id: string): Promise<boolean>;
function verifyAuthentication(token: string): Promise<boolean>;
function ensureUserActive(user: User): User | never;

// Transformation
function transformUserData(raw: unknown): User;
function parseUserInput(input: string): UserInput;
function formatUserName(user: User): string;
function serializeUser(user: User): string;
function deserializeUser(data: string): User;

// State Changes
function enableFeature(featureId: string): void;
function disableFeature(featureId: string): void;
function toggleFeature(featureId: string): void;
function activateUser(userId: string): Promise<void>;
function deactivateUser(userId: string): Promise<void>;
```

### Handler and Callback Patterns

```typescript
// ✅ Good: Event handler naming
function handleClick(event: MouseEvent): void;
function handleSubmit(event: FormEvent): void;
function handleUserUpdate(user: User): void;

// ✅ Good: Callback naming
function onSuccess(result: Result): void;
function onError(error: Error): void;
function onChange(value: string): void;
function onComplete(): void;

// ✅ Good: Lifecycle naming
function beforeSave(entity: Entity): void;
function afterSave(entity: Entity): void;
function onMount(): void;
function onUnmount(): void;
```

## Boolean Naming Patterns

### State and Condition Prefixes

```typescript
// ✅ Good: Boolean prefixes
const isActive = user.status === "active";
const isLoading = state === "loading";
const isVisible = !element.hidden;
const isEnabled = feature.enabled;
const isAuthenticated = !!user.token;

const hasPermission = permissions.includes("write");
const hasChildren = node.children.length > 0;
const hasError = errors.length > 0;
const hasChanges = isDirty(form);

const canEdit = role === "admin" || isOwner;
const canDelete = hasPermission && !isProtected;
const canSubmit = isValid && !isSubmitting;

const shouldRefresh = Date.now() - lastUpdate > TTL;
const shouldRetry = attempts < maxAttempts;
const shouldDisplay = isActive && hasPermission;

const willExpire = expiryDate < futureDate;
const willUpdate = version < latestVersion;

// ❌ Bad: Unclear boolean names
const active = true; // Missing 'is' prefix
const permission = false; // Unclear what permission
const editable = true; // Should be canEdit or isEditable
```

### Boolean Method Patterns

```typescript
// ✅ Good: Boolean method naming
class User {
  isActive(): boolean {}
  hasRole(role: string): boolean {}
  canPerformAction(action: string): boolean {}
  shouldReceiveNotifications(): boolean {}
}

interface Validator {
  isValid(value: unknown): boolean;
  hasErrors(): boolean;
  canProceed(): boolean;
}
```

## Collection Naming Patterns

### Arrays and Lists

```typescript
// ✅ Good: Collection naming
const users: User[] = []; // Plural for arrays
const activeUsers = users.filter((u) => u.isActive);
const userIds = users.map((u) => u.id);
const userEmails = users.map((u) => u.email);

// Specific collection patterns
const customerOrders = await getOrdersForCustomer(customerId);
const pendingInvoices = invoices.filter((i) => i.status === "pending");
const availableProducts = products.filter((p) => p.inStock);

// ❌ Bad: Singular names for collections
const user = []; // Confusing
const product = getProducts(); // Misleading
```

### Maps and Dictionaries

```typescript
// ✅ Good: Map naming patterns
const userById = new Map<string, User>();
const usersByRole = new Map<Role, User[]>();
const emailToUser = new Map<string, User>();

// Object as dictionary
const errorMessages: Record<ErrorCode, string> = {
  E001: "Invalid input",
  E002: "Unauthorized",
};

const currencySymbols: Record<Currency, string> = {
  USD: "$",
  EUR: "€",
  GBP: "£",
};

// Lookup tables
const statusColors = {
  active: "green",
  pending: "yellow",
  inactive: "red",
};
```

## Temporal Naming Patterns

### Time-Related Variables

```typescript
// ✅ Good: Time variable naming
const createdAt = new Date();
const updatedAt = new Date();
const deletedAt: Date | null = null;
const publishedAt = new Date();
const expiresAt = addDays(now, 30);

// Duration with units
const timeoutMs = 5000;
const delaySeconds = 30;
const durationMinutes = 15;
const intervalHours = 24;
const cacheTtlDays = 7;

// Time ranges
const startDate = new Date("2024-01-01");
const endDate = new Date("2024-12-31");
const fromTimestamp = Date.now() - 24 * 60 * 60 * 1000;
const toTimestamp = Date.now();

// ❌ Bad: Ambiguous time names
const time = 5000; // 5000 what?
const duration = 30; // Missing unit
const date = new Date(); // What date? Created? Updated?
```

## Configuration and Options Patterns

### Configuration Objects

```typescript
// ✅ Good: Config naming patterns
interface DatabaseConfig {
  host: string;
  port: number;
  username: string;
  password: string;
  database: string;
}

interface ServerOptions {
  port: number;
  host: string;
  cors: CorsOptions;
  rateLimit: RateLimitOptions;
}

// Settings vs Config
const userSettings = {
  // User-configurable
  theme: "dark",
  language: "en",
  notifications: true,
};

const systemConfig = {
  // System-level
  maxConnections: 100,
  timeout: 30000,
  retryAttempts: 3,
};

// ❌ Bad: Unclear config names
const options = {}; // Too generic
const settings = {}; // What kind of settings?
const config = {}; // What is being configured?
```

## Error and Exception Patterns

### Error Naming

```typescript
// ✅ Good: Error naming patterns
class ValidationError extends Error {}
class AuthenticationError extends Error {}
class AuthorizationError extends Error {}
class NotFoundError extends Error {}
class ConflictError extends Error {}
class NetworkError extends Error {}
class DatabaseError extends Error {}

// Error codes
enum ErrorCode {
  INVALID_INPUT = "INVALID_INPUT",
  UNAUTHORIZED = "UNAUTHORIZED",
  NOT_FOUND = "NOT_FOUND",
  INTERNAL_ERROR = "INTERNAL_ERROR",
}

// Error messages
const errorMessages = {
  userNotFound: "User not found",
  invalidCredentials: "Invalid username or password",
  insufficientPermissions: "Insufficient permissions",
  networkTimeout: "Network request timed out",
};
```

## Acronym Handling

### Consistent Acronym Casing

```typescript
// ✅ Good: Consistent acronym handling
const apiURL = "https://api.example.com"; // URL stays uppercase
const userUUID = generateUUID(); // UUID stays uppercase
const htmlParser = new HTMLParser(); // HTML stays uppercase
const xmlDocument = parseXML(data); // XML stays uppercase
const httpClient = new HTTPClient(); // HTTP stays uppercase
const sqlQuery = "SELECT * FROM users"; // SQL stays uppercase

// Well-known lowercase acronyms
const userId = user.id; // 'id' is universally lowercase
const apiUrl = config.apiUrl; // 'url' acceptable in context

// ❌ Bad: Inconsistent acronyms
const apiUrl = "https://api.example.com"; // Should be apiURL
const htmlparser = new HtmlParser(); // Should be HTMLParser
const XmlDocument = parseXml(data); // Inconsistent casing
```

## Common Anti-Patterns

### Names to Avoid

```typescript
// ❌ Bad: Generic meaningless names
const data = await fetchData();
const info = getUserInfo();
const obj = processObject();
const thing = getThing();
const stuff = doStuff();
const temp = calculateTemp(); // Unless it's temperature
const tmp = await getUser(); // Avoid abbreviations

// ❌ Bad: Single letter variables (except loops)
const u = await getUser();
const p = processPayment();
const e = handleError();

// ❌ Bad: Hungarian notation
const strName = "John"; // Type is clear from TypeScript
const arrUsers = []; // Redundant prefix
const bIsActive = true; // Just use isActive
const intCount = 5; // Type system handles this

// ❌ Bad: Numbered variables
const user1 = users[0];
const user2 = users[1];
const error1 = "First error";
const error2 = "Second error";

// ❌ Bad: Overly clever names
const batman = cacheManager; // Cute but unclear
const ninja = secretFunction; // Confusing
const magic = algorithm; // Doesn't explain purpose
```

### Reserved Words and Conflicts

```typescript
// ❌ Bad: Using reserved words
const class = 'UserClass';      // 'class' is reserved
const delete = () => {};        // 'delete' is reserved
const const = 'constant';       // 'const' is reserved
const package = {};             // 'package' is reserved

// ✅ Good: Alternatives
const className = 'UserClass';
const deleteUser = () => {};
const constant = 'constant';
const packageInfo = {};

// ❌ Bad: Shadowing built-ins
const toString = () => {};      // Shadows Object.toString
const length = 5;               // Confusing with array.length
const filter = data;            // Shadows Array.filter
```

## Context-Specific Patterns

### API and HTTP

```typescript
// ✅ Good: API-related naming
const apiClient = new ApiClient();
const apiEndpoint = "/users";
const apiResponse = await fetch(url);
const requestHeaders = { "Content-Type": "application/json" };
const responseStatus = 200;
const httpMethod = "POST";
```

### Database and ORM

```typescript
// ✅ Good: Database patterns
const userRepository = new UserRepository();
const dbConnection = await connect();
const queryBuilder = new QueryBuilder();
const migrationVersion = "001_create_users";
const transactionScope = await beginTransaction();
```

### UI Components

```typescript
// ✅ Good: UI naming patterns
const isModalOpen = false;
const selectedItems: Item[] = [];
const activeTab = "profile";
const formErrors: ValidationError[] = [];
const isSubmitting = false;
const hasUnsavedChanges = true;
```

## Testing Patterns

```typescript
// ✅ Good: Test naming patterns
describe("UserService", () => {
  const mockUser = createMockUser();
  const stubRepository = new UserRepositoryStub();
  const fakeData = { id: "123", name: "Test" };
  const expectedResult = { success: true };
  const actualResult = service.process(input);

  it("should create user when valid data provided", () => {});
  it("should throw error when email already exists", () => {});
  it("should return null when user not found", () => {});
});
```

## References

- [Variable Naming](./variables.md) - Variable conventions
- [Function Naming](./functions.md) - Function patterns
- [Type Naming](./types.md) - Type and class patterns
- [File Naming](./files.md) - File organization patterns
