# Documentation Standards

*Standards for JSDoc, comments, inline documentation, and code explanation*

## JSDoc Format

### Basic JSDoc Structure

Use one-line format when possible, multi-line when necessary:

```typescript
/** calculates user's total score from all completed assessments */
function calculateUserScore(assessments: Assessment[]): number {
  return assessments.reduce((total, assessment) => total + assessment.score, 0);
}

/**
 * Processes user payment with validation and external service integration
 * @param userId - The unique identifier for the user
 * @param amount - Payment amount in cents
 * @param paymentMethod - Payment method configuration
 * @returns Promise resolving to payment confirmation
 * @throws {ValidationError} When payment data is invalid
 * @throws {PaymentError} When payment processing fails
 */
async function processPayment(
  userId: string,
  amount: number,
  paymentMethod: PaymentMethod
): Promise<PaymentConfirmation> {
  // Implementation
}
```

### JSDoc Style Rules

#### Functions: 3rd-Person Verbs, Lowercase, No Period

```typescript
// ✅ Good: Function documentation
/** validates email address format using RFC 5322 standard */
function validateEmail(email: string): boolean { }

/** fetches user profile from database with caching */
async function fetchUserProfile(userId: string): Promise<User> { }

/** transforms raw API response to domain model */
function transformUserData(apiResponse: ApiUserResponse): User { }

// ❌ Bad: Wrong style
/** Validates email address format. */  // Capitalized, has period
/** Email validation */                  // Noun phrase for function
/** This function validates email */     // Too verbose
```

#### Non-Functions: Noun Phrases

```typescript
// ✅ Good: Non-function documentation
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
type PaymentMethod = 'credit_card' | 'paypal' | 'bank_transfer';

/** maximum number of retry attempts for failed requests */
const MAX_RETRY_ATTEMPTS = 3;
```

### Complete JSDoc Examples

```typescript
/**
 * Retrieves paginated list of users with optional filtering
 * @param filter - Optional filter criteria for user search
 * @param pagination - Pagination parameters with defaults
 * @returns Promise resolving to paginated user results
 * @throws {ValidationError} When filter parameters are invalid
 * @throws {DatabaseError} When database query fails
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
  pagination: PaginationParams = { page: 1, limit: 50 }
): Promise<PaginatedResult<User>> {
  // Implementation
}

/**
 * User repository for database operations
 * Provides CRUD operations with caching and validation
 */
class UserRepository {
  /**
   * finds user by unique identifier with optional caching
   * @param id - User's unique identifier
   * @param useCache - Whether to use cached result if available
   * @returns Promise resolving to user or null if not found
   */
  async findById(id: string, useCache = true): Promise<User | null> {
    // Implementation
  }
}
```

### Parameter Documentation

```typescript
/**
 * Creates new user account with validation and welcome email
 * @param userData - User information for account creation
 * @param userData.name - Full name of the user
 * @param userData.email - Valid email address (will be normalized)
 * @param userData.password - Password meeting security requirements
 * @param options - Optional configuration for account creation
 * @param options.sendWelcomeEmail - Whether to send welcome email (default: true)
 * @param options.role - User role assignment (default: 'user')
 * @returns Promise resolving to created user with generated ID
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
  } = {}
): Promise<User> {
  // Implementation
}
```

## Inline Comments

### When to Comment

```typescript
// ✅ Good: Explain WHY, not WHAT
function calculateShippingCost(weight: number, distance: number): number {
  // Use expedited shipping calculation for heavy items to ensure delivery reliability
  if (weight > 50) {
    return distance * 0.15 + weight * 0.05;
  }
  
  // Standard rate applies for lightweight packages
  return distance * 0.10;
}

// ✅ Good: Document workarounds or constraints
function parseUserInput(input: string): User {
  // NOTE: API returns inconsistent date formats, normalize to ISO
  const normalizedInput = input.replace(/(\d{2})\/(\d{2})\/(\d{4})/, '$3-$1-$2');
  
  // WORKAROUND: Third-party service occasionally returns null as string "null"
  if (normalizedInput === 'null') {
    throw new ValidationError('Invalid user data received');
  }
  
  return JSON.parse(normalizedInput);
}

// ✅ Good: Clarify non-obvious business logic
function calculateLateFee(daysLate: number, originalAmount: number): number {
  // Business rule: Late fee caps at 25% of original amount to comply with regulations
  const maxFee = originalAmount * 0.25;
  const calculatedFee = daysLate * 5.00;
  
  return Math.min(calculatedFee, maxFee);
}
```

### Comment Casing Rules

```typescript
// ✅ Good: Lowercase for sentences and phrases
// check user permissions before allowing access
const hasAccess = checkPermissions(user, resource);

// api requires authentication token in header
const headers = { 'Authorization': `Bearer ${token}` };

// temporary workaround until API v2 is released
const legacyResponse = await callLegacyAPI(data);

// ✅ Good: Uppercase for proper nouns and acronyms
// API calls require authentication token
// Layout components should be memoized for performance
// PostgreSQL connection needs retry logic

// ❌ Bad: Capitalized sentences
// Check user permissions before allowing access
// API requires authentication token in header
```

### Comment Tags

#### Temporary Tags (Must Be Removed Before Commit)

```typescript
// TODO: implement retry logic for failed requests
function apiRequest(url: string): Promise<Response> {
  // Current implementation without retry
  return fetch(url);
}

// FIXME: memory leak in event listener cleanup
function setupEventListeners(): void {
  // Broken cleanup logic
}

// DEBUG: temporary logging for investigation
function processOrder(order: Order): void {
  console.log('DEBUG: Processing order', order.id);
  // Implementation
}

// TEMP: hardcoded value until configuration is available
const API_TIMEOUT = 5000;
```

#### Documentation Tags (Can Stay in Code)

```typescript
// HACK: workaround for third-party library bug in version 2.1.0
// Remove when upgrading to version 2.2.0 or later
function handleBuggyLibraryResponse(response: any): ProcessedResponse {
  // Compensate for library's incorrect null handling
  return response === null ? {} : response;
}

// WORKAROUND: browser inconsistency in date parsing
// Safari interprets dates differently than Chrome/Firefox
function parseDate(dateString: string): Date {
  // Normalize format for cross-browser compatibility
  return new Date(dateString.replace(/-/g, '/'));
}

// NOTE: this function modifies global state by design
// Used specifically for application-wide configuration
function updateGlobalSettings(settings: GlobalSettings): void {
  Object.assign(globalConfig, settings);
}

// WARNING: changing this value affects all existing user sessions
// Coordinate with operations team before modification
const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

// PERFORMANCE: this operation is O(n²) but acceptable for small datasets
// Consider optimization if dataset size grows beyond 1000 items
function findDuplicates(items: Item[]): Item[] {
  return items.filter((item, index) => 
    items.findIndex(other => other.id === item.id) !== index
  );
}

// SECURITY: input validation is critical here
// Never bypass validation even for internal calls
function executeQuery(sql: string, params: unknown[]): Promise<QueryResult> {
  validateSqlQuery(sql);
  validateParameters(params);
  return database.query(sql, params);
}

// COMPATIBILITY: IE11 requires polyfill for this feature
// Include polyfill in build process for production
function modernBrowserFeature(): void {
  if (!Array.prototype.includes) {
    throw new Error('Browser compatibility issue detected');
  }
}

// LIMITATION: current implementation only supports up to 100 concurrent connections
// Database connection pool needs expansion for higher loads
function createConnectionPool(): ConnectionPool {
  return new ConnectionPool({ maxConnections: 100 });
}
```

## Interface and Type Documentation

### Interface Documentation

```typescript
/**
 * User account information with authentication details
 * Used across authentication, profile, and authorization systems
 */
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

/**
 * Configuration for API client initialization
 * Supports multiple environments and retry strategies
 */
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
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

/** user role levels with increasing permissions */
type UserRole = 'viewer' | 'editor' | 'admin';

/** payment processing status during transaction lifecycle */
type PaymentStatus = 
  | 'pending'    // Initial state, awaiting processing
  | 'processing' // Currently being processed by payment provider
  | 'completed'  // Successfully processed
  | 'failed'     // Processing failed, user notified
  | 'cancelled'; // User cancelled before completion

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

```typescript
/**
 * Validates and normalizes user email address
 * @param email - Raw email input from user
 * @returns Normalized email address
 * @throws {ValidationError} When email format is invalid
 * 
 * @example
 * Basic usage:
 * ```typescript
 * const email = normalizeEmail('  John.Doe@EXAMPLE.COM  ');
 * console.log(email); // 'john.doe@example.com'
 * ```
 * 
 * @example
 * Error handling:
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
    throw new ValidationError('Invalid email format');
  }
  
  return trimmed;
}
```

## Documentation Anti-Patterns

### What NOT to Document

```typescript
// ❌ Bad: Stating the obvious
/** gets the user's name */
function getName(user: User): string {
  return user.name; // ❌ Bad: obvious comment
}

// ❌ Bad: Redundant comments
const users: User[] = []; // ❌ Bad: type is already clear

// ❌ Bad: Outdated comments
/** returns user age in years */
function getUserInfo(user: User): string { // ❌ Bad: returns string, not age
  return `${user.name} (${user.email})`;
}

// ❌ Bad: Commented-out code
function processUser(user: User): void {
  validateUser(user);
  // updateDatabase(user); // Old implementation
  // sendNotification(user); // Removed feature
  saveUser(user);
}
```

### Comments to Avoid

```typescript
// ❌ Bad: Restating the code
function calculateTotal(items: Item[]): number {
  let total = 0; // Initialize total to zero
  
  // Loop through each item in the items array
  for (const item of items) {
    total += item.price; // Add item price to total
  }
  
  return total; // Return the calculated total
}

// ✅ Good: Explain business logic instead
function calculateTotal(items: Item[]): number {
  // Apply bulk discount for orders over $100
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  return subtotal > 100 ? subtotal * 0.9 : subtotal;
}
```

## Documentation Maintenance

### Keeping Documentation Current

```typescript
/**
 * User preferences for application behavior
 * @since 1.2.0 - Added theme and language preferences
 * @deprecated theme field - Use appearance.theme instead (since 2.0.0)
 */
interface UserPreferences {
  /** @deprecated Use appearance.theme instead */
  theme?: 'light' | 'dark';
  
  /** appearance settings including theme and layout */
  appearance: {
    theme: 'light' | 'dark' | 'auto';
    compactMode: boolean;
  };
  
  /** preferred language code (ISO 639-1) */
  language: string;
  
  /** notification delivery preferences */
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
}
```

### Version Documentation

```typescript
/**
 * Authentication service with JWT token management
 * 
 * @version 2.1.0
 * @since 1.0.0
 * 
 * @changelog
 * - 2.1.0: Added refresh token support
 * - 2.0.0: Breaking: Changed token format to JWT
 * - 1.5.0: Added role-based permissions
 * - 1.0.0: Initial implementation
 */
class AuthService {
  /**
   * authenticates user and returns JWT tokens
   * @since 2.0.0 - Returns JWT tokens instead of session cookies
   */
  async authenticate(credentials: Credentials): Promise<AuthTokens> {
    // Implementation
  }
}
```