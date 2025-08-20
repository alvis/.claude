# Function Naming Standards

_Standards for naming functions, methods, and callable expressions_

## Core Principles

### Verb-First Convention

Functions perform actions, so they must start with verbs.

```typescript
// ✅ GOOD: starts with verb
function createUser(data): User { ... }
function validateEmail(email): boolean { ... }

// ❌ BAD: no verb
function user(data): User { ... }
function validation(email): boolean { ... }
```

### Async Clarity

Async operations should be immediately obvious from the name.

```typescript
// ✅ GOOD: clear async intent
async function fetchUserData(id): Promise<User> { ... }
async function loadConfiguration(): Promise<Config> { ... }

// ❌ BAD: misleading sync name
async function getUser(id): Promise<User> { ... }
```

### Return Type Indication

Function names should hint at what they return.

```typescript
// ✅ GOOD: clear return expectation
function isValid(value): boolean { ... }
function getUserCount(): number { ... }
function findUser(id): User | null { ... }
```

## Verb Categories

### Data Retrieval

```typescript
// get - sync, may be cached
function getUserName(user: User): string { ... }

// fetch - async, external source  
async function fetchUserProfile(id): Promise<User> { ... }

// find - search, may return null
function findUserByEmail(email): User | null { ... }

// list - return collection
function listActiveUsers(): User[] { ... }
```

### Data Manipulation

```typescript
// create - new instance
async function createUser(data): Promise<User> { ... }

// update - modify existing
async function updateUser(id, data): Promise<User> { ... }

// delete/remove - eliminate
async function deleteUser(id): Promise<void> { ... }

// set - create or update
async function setPreference(key, value): Promise<void> { ... }
```

### Validation and Checks

```typescript
// validate - detailed results
function validateInput(input): ValidationResult { ... }

// is - state check  
function isValidEmail(email): boolean { ... }

// has - possession
function hasPermission(user, permission): boolean { ... }

// can - capability
function canEdit(user, resource): boolean { ... }

// should - recommendation
function shouldRefresh(token): boolean { ... }
```

### Transformation

```typescript
// transform - general change
function transformData(raw): Processed { ... }

// parse - string to structured
function parseConfig(content): Config { ... }

// format - structured to string  
function formatCurrency(amount): string { ... }

// serialize - object to string
function serializeUser(user): string { ... }
```

## Patterns & Best Practices

### Factory Pattern

**Purpose:** Create instances with consistent initialization

**When to use:**

- Creating objects with defaults
- Abstracting complex construction

**Implementation:**

```typescript
function createUser(data): User {
  return new User(data);
}

function createDefaultConfig(): Config {
  return { port: 3000, ... };
}
```

### Builder Pattern

**Purpose:** Construct complex objects step by step

**When to use:**

- Assembling multi-part objects
- Conditional construction logic

**Implementation:**

```typescript
function buildQueryString(params): string {
  return Object.entries(params)
    .map(([k, v]) => `${k}=${v}`)
    .join("&");
}
```

### Common Patterns

1. **Event Handlers** - Use `handle*` prefix

   ```typescript
   handleClick(event), handleSubmit(event)
   ```

2. **Callbacks** - Use `on*` prefix  

   ```typescript
   onClick(event), onSuccess(result), onError(error)
   ```

3. **Async Suffix** - Optional for clarity

   ```typescript
   processData() vs processDataAsync()
   ```

## Anti-Patterns

### Poor Naming

```typescript
// ❌ BAD: common mistakes
function user(id): User {}        // No verb
function getUsers(): void {}      // Wrong return expectation
function process(data): any {}    // Too generic
function gUsr(id): User {}       // Unnecessary abbreviation

// ✅ GOOD: clear naming
function getUser(id): User {}
function dropUsers(): void {}
function processPayment(data): PaymentResult {}
function getUser(id): User {}
```

### Common Mistakes to Avoid

1. **Missing Verbs**
   - Problem: Functions without action words
   - Solution: Start with appropriate verb
   - Example: `user()` → `getUser()`

2. **Generic Names**  
   - Problem: Meaningless function names
   - Solution: Be specific about purpose
   - Example: `process()` → `processPayment()`

3. **Misleading Names**
   - Problem: Name doesn't match behavior
   - Solution: Ensure name reflects actual operation
   - Example: `getUser()` that creates → `createUser()`

## Quick Decision Tree

1. **Choosing function verb**
   - If retrieving data → `get*`
   - If searching → `search*` (NLP) or `list*` (conventional filter)
   - If creating → `create*` (instance) or `build*` (data structure)
   - If modifying → `set*`
   - If removing → `drop*`

2. **Boolean functions**
   - If checking state → `is*`
   - If checking possession → `has*`
   - If checking capability → `can*`
