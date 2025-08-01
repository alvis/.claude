# Variable Naming Standards

_Standards for naming variables, constants, and object properties_

## Core Variable Naming Principles

### MUST Follow Rules

- **MUST use camelCase** for all variables and properties
- **MUST use descriptive names** - Variable purpose should be immediately clear
- **MUST use plural for collections** - Arrays and sets should have plural names
- **MUST avoid abbreviations** - Write full words for clarity
- **MUST use UPPER_SNAKE_CASE** for global constants only

### SHOULD Follow Guidelines

- **SHOULD use domain-specific terms** - Match business vocabulary
- **SHOULD group related variables** - Use consistent prefixes/suffixes
- **SHOULD indicate units in names** - Include ms, px, count when relevant
- **SHOULD use positive names** - Avoid negative prefixes when possible

## Basic Variable Naming

### Descriptive and Specific

```typescript
// ✅ Good: Specific and descriptive
const activeUsers = users.filter((u) => u.isActive);
const emailValidationError = "Invalid email format";
const databaseConnectionTimeout = 5000;
const userProfileData = await fetchUserProfile(userId);
const paymentProcessingFee = calculateFee(amount);

// ❌ Bad: Vague or abbreviated
const data = users.filter((u) => u.isActive);
const err = "Invalid email format";
const timeout = 5000;
const temp = await fetchUserProfile(userId);
const fee = calculateFee(amount);
```

### Variable Length Guidelines

```typescript
// ✅ Good: Appropriate length for context
const users = await getUsers(); // Simple, clear context
const activeUserCount = users.filter((u) => u.isActive).length;
const monthlyRecurringRevenue = calculateMRR(subscriptions);
const isEmailVerificationRequired = config.auth.requireEmailVerification;

// ❌ Bad: Too short or too long
const u = await getUsers(); // Too abbreviated
const theListOfAllActiveUsersInTheSystem = users.filter((u) => u.isActive); // Too verbose
```

## Collection Naming

### Arrays and Lists

```typescript
// ✅ Good: Plural nouns for collections
const users = await getUserList();
const products = inventory.getAllProducts();
const orderItems = order.items;
const errorMessages = validation.errors;

// ✅ Good: Descriptive collection names
const activeEmployees = employees.filter((emp) => emp.status === "active");
const pendingOrders = orders.filter((order) => order.status === "pending");
const expiredSubscriptions = subscriptions.filter((sub) => sub.expiresAt < now);

// ❌ Bad: Singular for collections or unclear names
const user = await getUserList(); // Confusing - is it one or many?
const item = order.items; // Misleading singular name
const list = inventory.getAllProducts(); // Generic name
```

### Maps and Dictionaries

```typescript
// ✅ Good: Clear map naming patterns
const userById = new Map<string, User>();
const productsByCategory = groupBy(products, "category");
const errorCodeToMessage: Record<string, string> = {
  E001: "Invalid input",
  E002: "Unauthorized access",
};
const cacheDuration = 300; // Clear unit indication

// Pattern: <item>By<key> or <item>To<value>
const ordersByCustomerId = new Map<string, Order[]>();
const currencyToSymbol = { USD: "$", EUR: "€", GBP: "£" };

// ❌ Bad: Unclear map relationships
const userMap = new Map<string, User>(); // What's the key?
const cache = new Map(); // What's cached?
```

## Constant Naming

### Global Constants

```typescript
// ✅ Good: UPPER_SNAKE_CASE for true constants
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_PAGE_SIZE = 20;
const API_BASE_URL = "https://api.example.com";
const CACHE_TTL_SECONDS = 300;
const SUPPORTED_FILE_TYPES = ["jpg", "png", "pdf"] as const;

// Configuration constants
const DATABASE_CONFIG = {
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || "5432"),
  maxConnections: 10,
} as const;

// ❌ Bad: Incorrect constant casing
const maxRetryAttempts = 3; // Should be UPPER_SNAKE_CASE
const MAX_retry_attempts = 3; // Inconsistent casing
let MAX_ATTEMPTS = 3; // Should use const, not let
```

### Local Constants

```typescript
// ✅ Good: camelCase for function-scoped constants
function processPayment(amount: number) {
  const taxRate = 0.08;
  const processingFee = 2.99;
  const minimumAmount = 1.0;

  const taxAmount = amount * taxRate;
  const totalAmount = amount + taxAmount + processingFee;

  return totalAmount;
}

// ✅ Good: Enum-like constants
const OrderStatus = {
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  CANCELLED: "cancelled",
} as const;
```

## Context-Specific Naming

### Domain Vocabulary

```typescript
// ✅ Good: Use domain-specific terms
// E-commerce context
const customers = await getCustomers();
const shoppingCart = user.cart;
const orderTotal = calculateOrderTotal(items);
const shippingAddress = order.delivery.address;

// Healthcare context
const patients = await getPatients();
const medicalRecords = patient.records;
const prescriptions = doctor.issuedPrescriptions;
const appointmentSlots = schedule.availableSlots;

// ❌ Bad: Generic terms when specific available
const users = await getCustomers(); // Less clear in e-commerce
const data = patient.records; // Too generic for medical records
const items = doctor.issuedPrescriptions; // Vague in medical context
```

### Temporal Variables

```typescript
// ✅ Good: Clear time-related names
const createdAt = new Date();
const updatedAt = new Date();
const deletedAt: Date | null = null;
const expiresAt = addDays(createdAt, 30);
const durationMs = endTime - startTime;
const delaySeconds = 5;
const timeoutMs = 30000;

// Include units in time variables
const sessionDurationMinutes = 30;
const cacheExpiryHours = 24;
const retryDelayMs = 1000;

// ❌ Bad: Ambiguous time variables
const time = new Date(); // What time? Created? Updated?
const duration = 30; // 30 what? Seconds? Minutes?
const timeout = 5000; // Include unit in name
```

## Boolean Variables

### State and Condition Booleans

```typescript
// ✅ Good: Boolean naming patterns
const isActive = user.status === "active";
const isVisible = element.style.display !== "none";
const isLoading = requestState === "pending";
const isAuthenticated = !!user.token;

const hasPermissions = permissions.length > 0;
const hasCompletedOnboarding = user.onboardingStep === "complete";
const hasUnsavedChanges = formState.isDirty;

const canEdit = userRole === "admin" || userId === resourceOwnerId;
const canDelete = userRole === "admin" && resource.isDeletable;

const shouldRefresh = lastUpdate < Date.now() - CACHE_TTL;
const shouldRetry = attemptCount < MAX_RETRY_ATTEMPTS;

// ❌ Bad: Unclear boolean names
const active = user.status === "active"; // Missing 'is' prefix
const permission = permissions.length > 0; // Singular suggests non-boolean
const refresh = lastUpdate < Date.now(); // Verb without context
```

## Iteration Variables

### Loop Variables

```typescript
// ✅ Good: Meaningful iteration variables
for (const user of users) {
  processUser(user);
}

for (const [index, product] of products.entries()) {
  console.log(`${index}: ${product.name}`);
}

users.forEach((user, index) => {
  console.log(`User ${index + 1}: ${user.name}`);
});

// ✅ Acceptable: Simple index variables for numeric loops
for (let i = 0; i < array.length; i++) {
  // When you need the index
}

// ❌ Bad: Single letters for complex objects
for (const u of users) {
  // Use 'user' instead
  processUser(u);
}
```

## Destructuring Variables

### Object Destructuring

```typescript
// ✅ Good: Maintain clear names in destructuring
const { firstName, lastName, email } = user;
const { street, city, state, zipCode } = address;

// ✅ Good: Rename for clarity when needed
const {
  name: productName,
  price: productPrice,
  inStock: isProductAvailable,
} = product;

// ❌ Bad: Overly abbreviated destructured names
const { fn, ln, e } = user; // Too abbreviated
```

## Anti-Patterns to Avoid

### Common Naming Mistakes

```typescript
// ❌ Bad: Single letter variables (except loop indices)
const d = new Date();
const u = await getUser();
const e = error.message;

// ❌ Bad: Meaningless names
const data = await fetchData();
const obj = processObject();
const thing = getThing();
const stuff = doStuff();

// ❌ Bad: Hungarian notation
const strName = "John"; // Type is clear from TypeScript
const arrUsers = []; // Redundant type prefix
const bIsActive = true; // Use isActive instead

// ❌ Bad: Numbered variables
const user1 = users[0];
const user2 = users[1]; // Use array or destructuring

// ❌ Bad: Overly clever names
const batman = cacheManager; // Cute but unclear
const magic = complexAlgorithm; // Doesn't explain what it does
```

## Testing Variable Naming

```typescript
describe("UserService", () => {
  // ✅ Good: Clear test data names
  const mockUser = { id: "1", name: "Test User" };
  const validEmail = "test@example.com";
  const invalidEmail = "not-an-email";
  const expectedResult = { success: true };

  it("should validate email addresses", () => {
    // ✅ Good: Descriptive variable names in tests
    const validationResult = validateEmail(validEmail);
    const errorResult = validateEmail(invalidEmail);

    expect(validationResult).toBe(true);
    expect(errorResult).toBe(false);
  });
});
```

## References

- [TypeScript Standards](../typescript.md) - Type annotations
- [Function Naming](./functions.md) - Function naming patterns
- [General Principles](../general-principles.md) - Overall coding standards
