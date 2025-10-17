# Naming Standards

_Comprehensive naming conventions for functions, types, variables, and constants_

## Core Principles

### Universal Rules

- **Descriptive over concise** - Names should immediately communicate purpose
- **No abbreviations** - Write full words unless universally understood (e.g., id, url, api)
- **Domain vocabulary** - Use business/technical terms familiar to the team (e.g. patients over users)
- **Consistency** - Follow patterns established in the codebase

### Casing Conventions

| Element | Convention | Examples |
|---------|-----------|----------|
| Functions/Methods | camelCase | `createUser`, `validateEmail`, `fetchData` |
| Variables | camelCase | `userName`, `activeUsers`, `totalCount` |
| Constants (global) | UPPER_SNAKE_CASE | `MAX_RETRY_ATTEMPTS`, `API_BASE_URL` |
| Constants (local) | camelCase | `taxRate`, `defaultTimeout` |
| Types/Interfaces | PascalCase | `User`, `ApiResponse`, `PaymentMethod` |
| Classes | PascalCase | `UserService`, `PaymentProcessor` |
| Enums | PascalCase | `UserRole`, `OrderStatus` |

## Function Naming

### Verb-First Convention

Functions perform actions and **MUST** start with verbs.

**✅ Approved**: `createUser`, `validateEmail`, `fetchUserData`, `hasPermission`, `canEdit`

**❌ Disallowed → ✅ Use instead**:

- `user` → `getUser`, `createUser` (factory), `setUser` (persisted entity), `updateUser`, `dropUser`
- `validation` → `validateInput`, `validateEmail`, `validateForm`
- `email` → `sendEmail`, `validateEmail`, `formatEmail`
- `permission` → `checkPermission`, `hasPermission`, `grantPermission`

### Async Clarity

Async operations **MUST** be obvious from the name.

**✅ Approved**: `getUser`, `fetchUserData`, `loadConfiguration`, `saveToDatabase`

### Verb Categories

| Verb | Usage | Return Type | Example |
|------|-------|-------------|---------|
| **get** | Async/Sync retrieval, may be cached | Any | `getUserName`, `getConfig` |
| **fetch** | Async, external source | `Promise<T>` | `fetchUserProfile`, `fetchOrders` |
| **find** | Search operation | `T \| null` | `findUserByEmail`, `findProduct` |
| **list** | Return collection | `T[]` | `listActiveUsers`, `listProducts` |
| **create** | New instance | `T` or `Promise<T>` | `createUser`, `createOrder` |
| **update** | Modify existing | `T` or `Promise<T>` | `updateUser`, `updateProfile` |
| **set** | Persist create/update | `void` or `Promise<void>` | `setUser`, `setWorkspace` |
| **drop** | Destructive persistence removal | `void` or `Promise<void>` | `dropUser`, `dropWorkspace` |
| **validate** | Detailed validation | `ValidationResult` | `validateInput`, `validateEmail` |
| **is** | State check | `boolean` | `isValid`, `isActive`, `isAuthenticated` |
| **has** | Possession check | `boolean` | `hasPermission`, `hasChanges` |
| **can** | Capability check | `boolean` | `canEdit`, `canDelete`, `canSubmit` |
| **should** | Recommendation | `boolean` | `shouldRefresh`, `shouldRetry` |
| **transform** | General change | `T` | `transformData`, `transformResponse` |
| **parse** | String to structured | `T` | `parseConfig`, `parseJson` |
| **format** | Structured to string | `string` | `formatCurrency`, `formatDate` |
| **serialize** | Object to string | `string` | `serializeUser`, `serializePayload` |
| **build** | Construct complex | `T` | `buildQueryString`, `buildRequest` |

<IMPORTANT>
**Persistence operations**: When working with persisted entities (database rows, durable resources), align with the data operation naming convention: use `Search<Entity>` / `List<Entity>` for multi-item reads, `Get<Entity>` for single-item reads, `Set<Entity>` for create/update upserts, and `Drop<Entity>` for destructive removes. Reserve `create*` for in-memory helpers or factories.
</IMPORTANT>

### Common Patterns

**Event Handlers**: `handle*`
Examples: `handleClick`, `handleSubmit`, `handleError`

**Callbacks**: `on*`
Examples: `onClick`, `onSuccess`, `onError`, `onChange`, `on<present tense verb>`

**Factories**: `create*`
Examples: `createDefaultConfig`, `createLogger`

### Factory Function Patterns

| Pattern | Use When… | Example |
|---------|-----------|---------|
| `createX` | Creating a single instance or value without persistent state | `createEventEmitter()`, `createLogger()` |
| `xFactory` | Returning a reusable or stateful factory function | `userFactory()`, `routerFactory()` |

- Use `createX` for one-off creators or stateless helpers (even if the function returns another function).
- Use `xFactory` when returning a higher-order factory that captures configuration or maintains state for reuse.
- Avoid naming factory helpers `create*` if they immediately return a configured reusable function; prefer the `xFactory` suffix instead.

<IMPORTANT>
 **Persistence reminder**: `create*` and `xFactory` apply to in-memory helpers. When interacting with persisted entities, use `Set<Entity>` instead of `create*` to express upsert behavior.
</IMPORTANT>

**Builders**: `build*`
Examples: `buildQueryString`, `buildResponse`

## Type Naming

### No Prefixes

**MUST NOT** use Hungarian notation or unnecessary prefixes.

**✅ Approved**: `User`, `UserId`, `UserRole`, `OrderStatus`

**❌ Disallowed → ✅ Use instead**:

- `IUser` → `User`
- `TUserId` → `UserId`
- `EUserRole` → `UserRole`
- `UserInterface` → `User`

### Interface & Type Patterns

| Pattern | Usage | Examples |
|---------|-------|----------|
| Domain models | Plain noun | `User`, `Order`, `Product` |
| Request types | `*Request` suffix | `CreateUserRequest`, `UpdateOrderRequest` |
| Response types | `*Response` suffix | `ApiResponse<T>`, `CreateUserResponse` |
| Generic types | Single letter (T, K, V) | `Container<T>`, `Map<K, V>` |
| Union types | Descriptive noun | `UserRole`, `Status`, `ApiResult<T>` |
| Function types | Descriptive | `Validator<T>`, `EventHandler<T>` |

### Class Patterns

| Pattern | Usage | Examples |
|---------|-------|----------|
| Managers | `*Manager` suffix | `ConnectionManager`, `CacheManager` |
| Handlers | `*Handler` suffix | `ErrorHandler`, `RequestHandler` |
| Processors | `*Processor` suffix | `PaymentProcessor`, `DataProcessor` |

### Special Type Patterns

**Error Classes**: `*Error` suffix
Examples: `ValidationError`, `NotFoundError`, `AuthError`

**Config Types**: `*Config` suffix
Examples: `DatabaseConfig`, `ServerConfig`, `AuthConfig`

**Test Types**: `Mock*`, `Stub*`, `Test*` prefix
Examples: `MockUser`, `StubRepository`, `TestFixture`

## Parameter Naming

Use descriptive parameter names that communicate the caller intent and follow these conventions:

- `params` — Structured inputs that describe a command or query (e.g., filters, identifiers):

  ```typescript
  function searchCommunities(params: SearchParams): SearchResult[] {
    return [];
  }
  ```

- `query` — Declarative filtering criteria for read operations:

  ```typescript
  function listUsers(query: UserQuery): User[] {
    return [];
  }
  ```

- `options` — Optional modifiers that influence behavior without redefining the primary subject:

  ```typescript
  function formatName(name: string, options?: FormatOptions): string {
    return name;
  }
  ```

- `data` — Core subject matter being created or updated:

  ```typescript
  function setUser(data: SetUserData): Promise<void> {
    return Promise.resolve();
  }
  ```

- `config` — Configuration objects or initialization settings:

  ```typescript
  function initializeApp(config: AppConfig): void {
    // ...
  }
  ```

- `context` — Execution context or request metadata:

  ```typescript
  function handleRequest(request: Request, context: RequestContext): Response {
    return { status: 200 };
  }
  ```

- `details` — Supplementary metadata accompanying the main subject:

  ```typescript
  function processOrder(details: OrderDetails): ProcessedOrder {
    return { ...details, processed: true };
  }
  ```

## Data Operation Naming Convention

### Multi-Item Reads

- **`Search<Entity>`** — Full-text or semantic queries that accept natural-language `query` input:

  ```typescript
  SearchCommunities({ query: "climate tech in europe", filter, limit });
  ```

- **`List<Entity>`** — Structured, rule-based filtering without natural language:

  ```typescript
  ListCommunities({ filter: { country: "UK" }, limit });
  ```

Avoid vague verbs like `Find` or `Query`; pick either `Search` or `List` based on the available capability.

### Single-Item Reads

- **`Get<Entity>`** — Retrieve exactly one record using a parameter object (id, slug, etc.):

  ```typescript
  GetUser({ id: "user-123" });
  GetWorkspace({ slug: "north-america" });
  ```

Avoid names like `FindById` or `Fetch` that leak implementation details.

### Mutations

- **`Set<Entity>`** — Create or update a persisted entity (supports upsert semantics):

  ```typescript
  SetProduct({ id: "prod-1", name: "Updated name" });
  SetUser({ name: "New user", email: "user@example.com" });
  ```

### Destructive Operations

- **`Drop<Entity>`** — Irreversible removal of a persisted record:

  ```typescript
  DropProduct({ id: "prod-1" });
  ```

<IMPORTANT>
 Drop operations are discouraged. Prefer `Set<Entity>` with a status field (e.g., `status: "inactive"`) to achieve soft-deletion semantics whenever possible.
</IMPORTANT>

## Variable Naming

### Accepted Abbreviations

Use full words unless the abbreviation appears in this allowlist: `fn`, `params`, `args`, `id`, `url`, `urn`, `uri`, `meta`, `info`.

All other abbreviations should be written out for clarity.

### Descriptive Variables

**✅ Approved**: `activeUsers`, `emailValidationError`, `databaseConnectionTimeout`, `userProfileData`

**❌ Disallowed → ✅ Use instead**:

- `data` → `userData`, `responseData`, `formData`, `userProfileData`
- `temp` → `temporaryCache`, `temporaryResult`, `bufferData`
- `err` → `error`, `validationError`, `authError`
- `timeout` → `timeoutMs`, `requestTimeout`, `connectionTimeout`
- `u` → `user`
- `usr` → `user`

### Collection Naming

**MUST** use plural for arrays and collections.

**✅ Approved**: `users`, `products`, `orderItems`, `errorMessages`, `activeEmployees`

**❌ Disallowed → ✅ Use instead**:

- `user` (for array) → `users`, `userList`, `activeUsers`
- `item` (for array) → `items`, `orderItems`, `cartItems`
- `list` (generic) → `users`, `products`, `orders` (specific plural)

### Map/Dictionary Patterns

Use `*By*` or `*To*` pattern to indicate relationships.

**✅ Approved**: `userById`, `productsByCategory`, `ordersByCustomerId`, `currencyToSymbol`

**❌ Disallowed → ✅ Use instead**:

- `userMap` → `userById`, `usersByEmail`, `usersByRole`
- `cache` → `userCache`, `responseCache`, `queryCacheByKey`
- `dict` → `errorCodeToMessage`, `statusToLabel`, `idToUser`

### Boolean Variables

| Prefix | Usage | Examples |
|--------|-------|----------|
| **is** | State check | `isActive`, `isVisible`, `isLoading`, `isAuthenticated` |
| **has** | Possession | `hasPermissions`, `hasChanges`, `hasError` |
| **can** | Capability | `canEdit`, `canDelete`, `canSubmit` |
| **should** | Recommendation | `shouldRefresh`, `shouldRetry` |

**❌ Disallowed → ✅ Use instead**:

- `active` → `isActive`
- `enabled` → `isEnabled`
- `visible` → `isVisible`
- `loading` → `isLoading`
- `authenticated` → `isAuthenticated`

### Constants

**Global constants (UPPER_SNAKE_CASE)**:
`MAX_RETRY_ATTEMPTS`, `DEFAULT_PAGE_SIZE`, `API_BASE_URL`, `CACHE_TTL_SECONDS`, `SUPPORTED_FILE_TYPES`

**Local constants (camelCase)**:
`taxRate`, `processingFee`, `minimumAmount`, `defaultTimeout`

### Temporal Variables

**MUST** include units in time-related variables.

**✅ Approved**: `createdAt`, `updatedAt`, `expiresAt`, `durationMs`, `delaySeconds`, `timeoutMs`, `sessionDurationMinutes`

**❌ Disallowed → ✅ Use instead**:

- `time` → `createdAt`, `updatedAt`, `timestamp`, `startTime`
- `duration` → `durationMs`, `durationSeconds`, `elapsedTimeMs`
- `timeout` → `timeoutMs`, `requestTimeoutSeconds`, `connectionTimeoutMs`
- `delay` → `delayMs`, `retryDelaySeconds`

### Iteration Variables

**✅ Approved**:

```typescript
for (const user of users) { ... }
for (const [index, product] of products.entries()) { ... }
users.forEach((user, index) => { ... })
for (let i = 0; i < array.length; i++) { ... } // acceptable for numeric loops
```

**❌ Disallowed → ✅ Use instead**:

- `for (const u of users)` → `for (const user of users)`
- `for (const p of products)` → `for (const product of products)`
- `items.map(i => ...)` → `items.map(item => ...)`

## Singular vs. Plural Naming

- Use **singular** names for single entities, classes, or value objects (`user`, `car`, `config`).
- Use **plural** names for collections, settings groups, or objects that intentionally aggregate multiple items (`options`, `settings`, `preferences`).
- When a plural object represents related settings, keep the plural form even if it currently has one property to signal future expansion.

## Anti-Patterns

### Common Mistakes

| Anti-Pattern | Problem | Solution | Example |
|--------------|---------|----------|---------|
| Missing verbs | No action word | Add appropriate verb | `user()` → `getUser()` |
| Generic names | Too vague | Be specific | `process()` → `processPayment()` |
| Abbreviations | Hard to read | Use full words | `gUsr()` → `getUser()` |
| Single letters | Unclear purpose | Descriptive names | `const d = new Date()` → `const createdAt = new Date()` |
| Numbered variables | Poor organization | Use arrays/objects | `user1`, `user2` → `users[0]`, `users[1]` |
| Hungarian notation | Redundant with TypeScript | Remove type prefixes | `strName` → `name`, `arrUsers` → `users` |
| Misleading names | Name doesn't match behavior | Align name with action | `getUser()` (creates) → `createUser()` |
| Unnecessary prefixes | `I`, `T`, `E` prefixes | Clean names | `IUser` → `User`, `TUserId` → `UserId` |
| Redundant suffixes | Adds no value | Simplify | `UserInterface` → `User` |

### Specific Examples to Avoid

**Functions**:

```
❌ user(id), getUsers() returning void, process(data), gUsr(id)
✅ getUser(id), dropUsers(), processPayment(data), getUser(id)
```

**Types**:

```
❌ IUser, TUserId, EStatus, UserInterface, user_service
✅ User, UserId, Status, User, UserService
```

**Variables**:

```
❌ data, temp, err, u, strName, arrUsers, bIsActive, user1/user2
✅ userProfileData, temporaryCache, validationError, user, name, users, isActive, users[0]/users[1]
```

## Quick Decision Trees

### Choosing Function Verbs

- **Retrieving data?** → `get*` (sync) or `fetch*` (async)
- **Searching?** → `find*` or `list*`
- **Creating?** → `create*` (in-memory/factory) or `build*` (structure); use `Set<Entity>` for persisted records
- **Modifying?** → `update*` for transient data; `Set<Entity>` for persisted state
- **Removing?** → Use `Drop<Entity>` for destructive persistence
- **Checking state?** → `is*`, `has*`, `can*`, `should*`
- **Transforming?** → `transform*`, `parse*`, `format*`, `serialize*`
- **Validating?** → `validate*`

### Choosing Type Constructs

- **Object shape?** → `interface`
- **Union/alias?** → `type`
- **Implementation?** → `class`
- **Constants set?** → `enum` or const assertion

### Choosing Variable Names

- **Collection?** → Use plural (e.g., `users`, `products`)
- **Map/dictionary?** → Use `*By*` or `*To*` pattern
- **Boolean?** → Use `is*`, `has*`, `can*`, `should*` prefix
- **Time-related?** → Include unit (`Ms`, `Seconds`, `Minutes`, etc.)
- **Constant?** → Global = UPPER_SNAKE_CASE, Local = camelCase

## References

- TypeScript Standards (standard:typescript) - Type annotations and TypeScript usage
- Function Standards (standard:functions) - Function structure and documentation
- General Principles (standard:general-principles) - Overall coding standards
