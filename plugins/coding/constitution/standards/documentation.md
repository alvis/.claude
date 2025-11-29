# Documentation Standards

_Standards for code comments, JSDoc, inline documentation, and code explanation_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- General Principles (standard:general-principles) - Foundational code quality principles that inform documentation practices, including clarity, maintainability, and professional standards

## Core Comment Principles

### When to Write Comments

Write comments that explain **"why"**, not **"what"**:

- **Purpose or reasoning** that isn't immediately obvious
- **Workarounds** for external constraints or legacy issues
- **Intentional deviations** from best practices
- **Public API documentation** - parameters, return values, side effects
- **Complex algorithms** needing explanation
- **Business logic** that isn't self-evident
- **Temporary solutions** with context

### Comment Casing Rules

**Always use lowercase** for comments that are sentences or phrases except for referencing code elements or acronym like HTTP:

```typescript
// ✅ GOOD: lowercase comments
// this function handles user authentication
// check if user exists before proceeding

// ❌ BAD: uppercase comments
// This function handles user authentication
// Check if user exists before proceeding
```

**Use uppercase only** when referencing code elements or acronym:

```typescript
// ✅ GOOD: uppercase for code references
// the UserService handles authentication
// call the OAuth AS with proper headers
// Layout components should be memoized

// ❌ BAD: lowercase for code references
// the userservice handles authentication
// call the OAuth AS with proper headers
// layout components should be memoized
```

## Comment Tags

Use comment tags to indicate the purpose of comments:

### Temporary Tags (Never Commit)

These tags indicate issues that **MUST** be resolved before committing. **NEVER** commit code containing these tags:

```typescript
// TODO: implement error handling for network failures
// FIXME: this calculation is incorrect for edge cases  
// DEBUG: console.log for debugging - remove before commit
// TEMP: stub implementation - replace with real logic
// QUESTION: should we validate email format here?
// IDEA: could optimize this with memoization
// INTENT: clarifies why something is implemented this way
```

**Enforcement**: These tags should trigger pre-commit hooks to prevent accidental commits.

### Review Tags (Remove Before Merge)

For draft PRs only - remove before merging:

```typescript
// REVIEW: need second opinion on this approach
// REFACTOR: this code needs restructuring
// OPTIMIZE: performance could be improved here
```

### Documentation Tags (Can Remain)

These can stay in production code:

```typescript
// HACK: workaround for library bug - remove when fixed
// WORKAROUND: bypass issue with third-party API
// NOTE: important context or non-obvious explanation
// WARNING: alerts about potential risks or edge cases
// PERFORMANCE: highlights optimization opportunities
// SECURITY: documents security implications
// COMPATIBILITY: handles browser/platform specific issues
// LIMITATION: documents known limitation
```

### Tag Formatting

For multi-line content, start tag on its own line:

```typescript
// ✅ GOOD: single-line format
// NOTE: skip root tsconfig to avoid circular refs

// ✅ GOOD: multi-line format
// NOTE:
// lockfile stored in workspace root only
// when shared-workspace-lockfile=true

// WARNING:
// this mutation is intentional for performance
// do not refactor to immutable without benchmarking
```

## JSDoc Standards

### Basic JSDoc Structure

**[IMPORTANT]** Use one-line JSDoc when there are no parameters and return is void/Promise<void>. Use multi-line when there are parameters or non-void returns:

```typescript
/** calculates user's total score from all completed assessments */
function calculateUserScore(assessments: Assessment[]): number {
  return assessments.reduce((total, assessment) => total + assessment.score, 0);
}

/**
 * processes user payment with validation and external service integration
 * @param userId the unique identifier for the user
 * @param amount payment amount in cents
 * @param paymentMethod payment method configuration
 * @returns promise resolving to payment confirmation
 * @throws {ValidationError} when payment data is invalid
 * @throws {PaymentError} when payment processing fails
 */
async function processPayment(
  userId: string,
  amount: number,
  paymentMethod: PaymentMethod,
): Promise<PaymentConfirmation> {
  // Implementation
}
```

### JSDoc Rules

- **Oneline section header** in UPPER CASE
- **Begin with third-person singular verb** (e.g., "validates" not "validate")
- **Write all JSDoc in lowercase**
- **Parameter descriptions start with lowercase** (unless referencing types/interfaces/acronyms)
- **Omit hyphens** after parameter names in @param tags
- **Exclude TypeScript types** from JSDoc (they're in the code)
- **No periods** at the end of JSDoc comments
- **List all @throws** with conditions

#### Section: // SECTION NAME IN UPPER CASE //

```typescript
// ✅ GOOD: One line section

// USER //

// ❌ BAD: non-standard section
/* USER */

//////////
// USER //
/////////

```

#### Functions: 3rd-Person Verbs, Lowercase, No Period

```typescript
// ✅ GOOD: function documentation
/** ensures required environment variable exist */
function ensureEnv(): void {}

// ❌ BAD: wrong style
/** Validates email address format. */ // Capitalized, has period
/** Email validation */ // Noun phrase for function
/** This function validates email */ // Too verbose
/** 
 * ensures required environment variable exist
 */ // Unnecessary multiline
```

#### Parameter Descriptions: Lowercase Unless Referencing Types

```typescript
// ✅ GOOD: lowercase for general descriptions
/**
 * @param userId the unique identifier for the user
 * @param amount payment amount in cents
 * @param options optional configuration settings
 */

// ✅ GOOD: uppercase when referencing types/interfaces
/**
 * @param user the User object containing profile data
 * @param config ApiConfig instance for initialization
 * @param status PaymentStatus enum value
 */

// ❌ BAD: incorrect capitalization
/**
 * @param userId The unique identifier // should be lowercase 'the'
 * @param user the user object // should be uppercase 'User'
 */
```

#### Non-Functions: Noun Phrases

```typescript
// ✅ GOOD: non-function documentation
/** configuration options for API client initialization */
interface ApiConfig {
  baseUrl: string;
  timeout: number;
}

/** user authentication and profile information */
interface User {
  id: string;
  email: string;
}

/** supported payment methods for transaction processing */
type PaymentMethod = "credit_card" | "paypal" | "bank_transfer";

/** maximum number of retry attempts for failed requests */
const MAX_RETRY_ATTEMPTS = 3;
```

### Complete JSDoc Examples

````typescript
/**
 * retrieves paginated list of users with optional filtering
 * @param filter optional filter criteria for user search
 * @param pagination pagination parameters with defaults
 * @returns promise resolving to paginated user results
 * @throws {ValidationError} when filter parameters are invalid
 * @throws {DatabaseError} when database query fails
 * @example
 * ```typescript
 * const users = await getUsers(
 *   { status: 'active', department: 'engineering' },
 *   { page: 1, limit: 20 }
 * );
 * ```
 */
async function getUsers(
  filter: UserFilter = {},
  pagination: PaginationParams = { page: 1, limit: 50 },
): Promise<PaginatedResult<User>> {
  // implementation
}

/**
 * User repository for database operations
 * provides CRUD operations with caching and validation
 */
class UserRepository {
  /**
   * finds user by unique identifier with optional caching
   * @param id user's unique identifier
   * @param useCache whether to use cached result if available
   * @returns promise resolving to user or null if not found
   */
  async findById(id: string, useCache = true): Promise<User | null> {
    // implementation
  }
}
````

### Parameter Documentation

```typescript
/**
 * creates new user account with validation and welcome email
 * @param userData user information for account creation
 * @param userData.name full name of the user
 * @param userData.email valid email address (will be normalized)
 * @param userData.password password meeting security requirements
 * @param options optional configuration for account creation
 * @param options.sendWelcomeEmail whether to send welcome email (default: true)
 * @param options.role user role assignment (default: 'user')
 * @returns promise resolving to created user with generated ID
 */
async function createUser(
  userData: {
    name: string;
    email: string;
    password: string;
  },
  options: {
    sendWelcomeEmail?: boolean;
    role?: string;
  } = {},
): Promise<User> {
  // Implementation
}
```

## Inline Comments

### Code Explanation Comments

#### Good Comments

Explain the **why**, not the **what**:

```typescript
// ✅ GOOD: explains reasoning
// use Map for O(1) lookup performance with large datasets
const userIndex = new Map<string, User>();

// ✅ GOOD: explains workaround
// setTimeout with 0ms to push to next tick and avoid race condition
setTimeout(() => updateUI(), 0);

// ✅ GOOD: explains business logic
// customers get 20% discount after 3rd purchase in same month
const discount = purchases.length > 3 ? 0.2 : 0;

// ✅ GOOD: explains deviation
// using any here because third-party library has incorrect types
const result = externalLib.process(data as any);

```

#### Bad Comments

Avoid redundant or obvious comments:

```typescript
// ❌ BAD: restates the obvious
// increment counter by 1
counter++;

// ❌ BAD: explains what instead of why
// loop through users array
users.forEach((user) => {});

// ❌ BAD: redundant with clear code
// return true if user is active
return user.isActive;
```

### Examples

```typescript
// ✅ GOOD: explains complex regex
// matches email with optional '+' addressing (e.g., user+tag@example.com)
const emailRegex = /^[^\s@]+(\+[^\s@]+)?@[^\s@]+\.[^\s@]+$/;

// ✅ GOOD: documents assumption
// assume UTC timezone since user timezone not provided
const date = new Date(timestamp);

// ✅ GOOD: explains performance choice
// pre-sort for binary search efficiency on repeated lookups
const sortedData = data.sort((a, b) => a.id - b.id);

// ✅ GOOD: security note
// sanitize to prevent XSS - never trust user input
const safe = sanitizeHtml(userContent);
```

## Interface and Type Documentation

### Interface Documentation

```typescript
/** user account information with authentication details */
interface User {
  /** unique identifier for the user account */
  readonly id: string;

  /** user's display name, max 100 characters */
  name: string;

  /** normalized email address used for authentication */
  email: string;

  /** user roles for authorization (admin, editor, viewer) */
  roles: string[];

  /** account creation timestamp */
  readonly createdAt: Date;

  /** last profile update timestamp */
  updatedAt: Date;

  /** optional profile picture URL */
  avatarUrl?: string;
}

/** configuration for API client initialization */
interface ApiClientConfig {
  /** base URL for all API requests */
  baseUrl: string;

  /** request timeout in milliseconds (default: 5000) */
  timeout?: number;

  /** maximum number of retry attempts (default: 3) */
  maxRetries?: number;

  /** authentication token for API access */
  authToken?: string;

  /** custom headers to include with all requests */
  defaultHeaders?: Record<string, string>;
}
```

### Type Documentation

```typescript
/** supported HTTP methods for API requests */
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

/** user role levels with increasing permissions */
type UserRole = "viewer" | "editor" | "admin";

/** payment processing status during transaction lifecycle */
type PaymentStatus =
  | "pending" // initial state, awaiting processing
  | "processing" // currently being processed by payment provider
  | "completed" // successfully processed
  | "failed" // processing failed, user notified
  | "cancelled"; // user cancelled before completion

/**
 * Result wrapper for operations that may succeed or fail
 * Eliminates need for try-catch in consuming code
 */
type Result<TData, TError = Error> =
  | { success: true; data: TData }
  | { success: false; error: TError };
```

## Code Examples in Documentation

### Example Documentation

````typescript
/**
 * validates and normalizes user email address
 * @param email raw email input from user
 * @returns normalized email address
 * @throws {ValidationError} when email format is invalid
 *
 * @example
 * basic usage:
 * ```typescript
 * const email = normalizeEmail('  John.Doe@EXAMPLE.COM  ');
 * console.log(email); // 'john.doe@example.com'
 * ```
 *
 * @example
 * error handling:
 * ```typescript
 * try {
 *   const email = normalizeEmail('invalid-email');
 * } catch (error) {
 *   if (error instanceof ValidationError) {
 *     console.error('Invalid email format:', error.message);
 *   }
 * }
 * ```
 */
function normalizeEmail(email: string): string {
  const trimmed = email.trim().toLowerCase();

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
    throw new ValidationError("Invalid email format");
  }

  return trimmed;
}
````

## Documentation Anti-Patterns

### What NOT to Document

```typescript
// ❌ BAD: stating the obvious
/** gets the user's name */
function getName(user: User): string {
  return user.name; // ❌ BAD: obvious comment
}

// ❌ BAD: redundant comments
const users: User[] = []; // ❌ BAD: type is already clear

// ❌ BAD: outdated comments
/** returns user age in years */
function getUserInfo(user: User): string {
  // ❌ BAD: returns string, not age
  return `${user.name} (${user.email})`;
}

// ❌ BAD: commented-out code
function processUser(user: User): void {
  validateUser(user);
  // updateDatabase(user); // old implementation
  // sendNotification(user); // removed feature
  saveUser(user);
}
```

### Comments to Avoid

Avoid these common mistakes:

```typescript
// ❌ BAD: noise comments
/**
 * Constructor
 */
constructor() { }

// ❌ BAD: version history (use git)
// modified by John on 2024-01-15
// fixed bug #123

// ❌ BAD: obvious comments
// return the result
return result;

// ❌ BAD: commented code for "just in case"
// might need this later
// function oldImplementation() { }

// ❌ BAD: personal notes
// I think this could be better but deadline is tight

// ❌ BAD: excessive punctuation
// WARNING!!!! DO NOT CHANGE THIS!!!!!

// ❌ BAD: restating the code
function calculateTotal(items: Item[]): number {
  let total = 0; // initialize total to zero

  // loop through each item in the items array
  for (const item of items) {
    total += item.price; // add item price to total
  }

  return total; // return the calculated total
}

// ✅ GOOD: explain business logic instead
function calculateTotal(items: Item[]): number {
  // apply bulk discount for orders over $100
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  return subtotal > 100 ? subtotal * 0.9 : subtotal;
}
```

## Comment Maintenance

### Keep Comments Updated

```typescript
// ❌ BAD: outdated comment
// calculate 15% tax (old rate)
const tax = amount * 0.18; // actual rate

// ✅ GOOD: updated comment
// calculate 18% tax (updated Jan 2024)
const tax = amount * 0.18;
```

### Remove Dead Comments

```typescript
// ❌ BAD: commented-out code
// const oldLogic = true;
// if (oldLogic) {
//   processLegacy();
// }

// ✅ GOOD: clean code without dead comments
// legacy processing removed in v2.0 - see PR #123
```

## Best Practices

### Comment Density

- **Minimize comments** by writing self-explanatory code
- **Strategic placement** - comment complex sections, not every line
- **Quality over quantity** - few meaningful comments beat many obvious ones

### Comment Style

- **Concise and clear** - get to the point quickly
- **Professional tone** - avoid humor or personal notes
- **Actionable** - comments should help the next developer

### Documentation Maintenance

```typescript
/**
 * User preferences for application behavior
 * @deprecated use appearance.theme instead (since 2.0.0)
 */
interface UserPreferences {
  /** @deprecated Use appearance.theme instead */
  theme?: "light" | "dark";

  /** appearance settings including theme and layout */
  appearance: {
    theme: "light" | "dark" | "auto";
    compactMode: boolean;
  };

  /** preferred language code (ISO 639-1) */
  language: string;
}
```

## Quick Reference

| Element | Format | Example |
|---------|--------|---------|
| Function | 3rd person verb, lowercase | `/** validates user input */` |
| Interface | Noun phrase, lowercase | `/** user account information */` |
| Type | Descriptive phrase | `/** payment processing status */` |
| Parameter | Lowercase description | `@param userId the unique identifier` |
