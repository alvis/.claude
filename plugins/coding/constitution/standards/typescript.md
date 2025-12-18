# TypeScript Standards

_Core TypeScript standards for type safety, imports, and language usage_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- General Coding Principles (standard:general-principles) - Test code must adhere to fundamental coding principles and consistency rules
- Naming Standards (standard:naming) - Test functions must follow function naming, structure, and documentation standards
- Documentation Standards (standard:documentation) - Test interfaces and complex test scenarios require proper JSDoc documentation

## What's Stricter Here

This standard enforces requirements beyond typical TypeScript practices:

| Standard Practice                | Our Stricter Requirement                  |
|----------------------------------|-------------------------------------------|
| `any` allowed for quick fixes    | **NO `any` types ever**                   |
| `as unknown as TYPE` for casting | **Type guards or fix root cause**         |
| Mixed imports acceptable         | **Separate code and type imports**        |
| Namespace imports OK             | **Named imports only**                    |
| Default exports common           | **Named exports preferred**               |
| `private` keyword                | **Use `#private` fields**                 |
| Suppression comments as needed   | **MUST consult user first**               |
| `let` for flexibility            | **`const` by default, `let` last resort** |

## Violation Checklist

Before submitting code, verify NONE of these violations are present:

### No Any Type

```typescript
// ❌ VIOLATION: any defeats TypeScript's purpose
function parseJson(input: string): any { ... }
const data: any = {};
```

**See**: [No Any Type](#no-any-type)

### Type Casting

```typescript
// ❌ VIOLATION: unsafe double casting
const user = data as unknown as User;
```

**See**: [No Unsafe Type Casting](#no-unsafe-type-casting)

### Suppression Comments

```typescript
// ❌ VIOLATION: silencing errors without approval
// @ts-ignore
// @ts-expect-error
// eslint-disable-next-line
```

**See**: [CRITICAL: Avoid Suppression Comments](#critical-avoid-suppression-comments)

### Import Organization

```typescript
// ❌ VIOLATION: mixed code and type imports
import { useState, type FC } from 'react';

// ❌ VIOLATION: namespace imports
import * as React from 'react';
```

**See**: [Import Organization](#import-organization)

### Variable Declaration

```typescript
// ❌ VIOLATION: let when const would work
let baseUrl = 'https://api.example.com'; // never reassigned
```

**See**: [Prefer const over let](#prefer-const-over-let)

### Class Members

```typescript
// ❌ VIOLATION: private keyword instead of #private
class Service {
  private repository: Repository; // use #repository instead
}
```

**See**: [Type Safety Rules](#type-safety-rules)

### Module Exports

```typescript
// ❌ VIOLATION: default exports
export default userService;
```

**See**: [Module Patterns](#module-patterns)

### Subpath Imports

```typescript
// ❌ VIOLATION: relative import when subpath exists
import { handler } from './fastify/request';

// ❌ VIOLATION: subpath import within same subpath
// file: src/fastify/request.ts
import { formatResponse } from '#fastify/response';
```

**See**: [Subpath Requirements](#subpath-requirements)

### Critical (Immediate Rejection)

| Violation                    | Example                |
|------------------------------|------------------------|
| `any` type                   | `const data: any = {}` |
| Double casting               | `as unknown as User`   |
| Suppression without approval | `@ts-ignore`           |
| Namespace imports            | `import * as React`    |

## Core Principles

### Type Safety First

Prioritize compile-time type checking to prevent runtime errors:

```typescript
// ✅ GOOD: explicit type narrowing
const currency: CurrencyCode = "USD";

// ❌ BAD: inference allows wrong values
const currency = "USD"; // could be any string
```

### No Any Type

Use `unknown` or specific types instead of `any`:

```typescript
// ✅ GOOD: use unknown for safe handling
function parseJson(input: string): unknown {
  return JSON.parse(input);
}

// ❌ BAD: any defeats TypeScript's purpose
function parseJson(input: string): any {
  return JSON.parse(input);
}
```

### No Unsafe Type Casting

**NEVER use `as unknown as TYPE` casting** - it bypasses TypeScript's type safety just like `any`:

```typescript
// ❌ BAD: double casting defeats type safety
const user = data as unknown as User; // no validation!

// ✅ GOOD: use type guards for safe type narrowing
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value
  );
}

if (!isUser(data)) {
  throw new ValidationError("Invalid user data");
}
const user = data; // TypeScript knows this is safe

// ✅ GOOD: refactor to fix type issues
interface ApiResponse {
  user: User;
  metadata: ResponseMetadata;
}
const response: ApiResponse = await fetchUser(); // proper typing
const user = response.user;

// ✅ ACCEPTABLE (TESTING ONLY): see Testing Patterns below
```

**Why `as unknown as TYPE` is dangerous**:

1. **No validation**: Bypasses all type checking - the data could be anything
2. **Runtime errors**: Creates false confidence in type safety
3. **Hidden bugs**: Type mismatches only discovered at runtime
4. **Defeats TypeScript**: Makes the type system useless

**Required approach when tempted to use `as unknown as TYPE`**:

1. **Ultrathink** - Deeply analyze WHY the types don't match
2. **Root cause analysis** - Identify the actual type issue:
   - Incorrect type definitions?
   - Missing type guards?
   - Wrong function signature?
   - Data structure mismatch?
3. **Fix properly** - Use one of these solutions:
   - Create type guards with runtime validation
   - Refactor data structures to match types
   - Update type definitions to reflect reality
   - Add proper validation at boundaries
4. **User confirmation** - If you believe `as unknown as TYPE` is necessary, **MUST confirm with user first**

**Testing Patterns** (TESTING ONLY):

Two distinct patterns depending on context:

```typescript
// ✅ INSIDE vi.mock: Triple pattern when mocking partial module
vi.mock("./user-service", () => ({
  userService: {
    getUser: vi.fn(),
  } satisfies Partial<MockedObject<UserService>> as Partial<
    MockedObject<UserService>
  > as MockedObject<UserService>,
}));

// ✅ OUTSIDE vi.mock: Strictly satisfies only
// Test code must know the exact shape of the mock
const mockUser = {
  id: "123",
  name: "Test User",
} satisfies Partial<User>;

// Use the partial mock with explicit type annotation
function setupTest(user: Partial<User> = mockUser) {
  // ...
}
```

**Why two patterns?**

- **Inside vi.mock**: The module system requires the exact type, so triple casting is necessary
- **Outside vi.mock**: Test code should explicitly handle partial types for accuracy

**NOTE**: These patterns ONLY allowed in test files. Production code must NEVER use these patterns.

### Prefer const over let

Use `const` by default and `let` only as a last resort when reassignment is absolutely necessary. Avoid mutation whenever possible:

```typescript
// ✅ GOOD: const for immutable values
const userId = "user-123";
const config = { apiUrl: "https://api.example.com" };
const users = await fetchUsers();

// ✅ GOOD: functional approach instead of mutation
const processedUsers = users.map(user => ({ ...user, processed: true }));
const validUsers = users.filter(user => user.isActive);
const total = items.reduce((sum, item) => sum + item.value, 0);

// ✅ ACCEPTABLE: let only for truly unavoidable cases
let buffer: string;
imperativeApiThatRequiresMutation(value => { buffer = value; });

// NOTE: Most patterns can use pure functions instead:
// - Accumulation → reduce(), - Conditionals → ternary/logical operators
// - Multi-step transforms → method chaining, - Loops → Array.from()/generators

// ❌ BAD: let when const would work
let baseUrl = "https://api.example.com"; // never reassigned
let userCount = users.length; // never reassigned

// ❌ BAD: unnecessary mutation
let processedUsers = [];
for (const user of users) {
  processedUsers.push({ ...user, processed: true });
}
```

### Type Safety Rules

- **NO `any` type** - Use `unknown` or specific types
- **NO `as unknown as TYPE` casting** - Use type guards or fix root cause (see "No Unsafe Type Casting")
- **Use `#private`** over `private` keyword for class members
- **Prefer `readonly`** for immutable data structures

### American English Convention

- **American English only** - Use American spelling in all code

```typescript
// ✅ GOOD: american English
interface ColorConfig {
  primaryColor: string;
  customizable: boolean;
  // ...
}

// ❌ BAD: british English
interface ColourConfig {
  primaryColour: string;
  customisable: boolean;
  // ...
}
```

## Modern Language Features

### Use ES6+ Features

```typescript
// ✅ GOOD: modern features
const double = (n: number): number => n * 2;
const { name, email } = user;
const message = `Welcome ${name}!`;
const city = user?.address?.city;
const port = process.env.PORT ?? 3000;
```

### Avoid Deprecated Patterns

```typescript
// ❌ BAD: outdated patterns
var name = "John"; // use const
arguments.callee; // deprecated

// ✅ GOOD: modern alternatives
const name = "John";
const args = [...arguments];
```

## File Organization & Symbol Ordering

Organize file contents in a consistent, predictable order to improve navigability and reduce merge conflicts.

### Import Organization

**MUST follow these rules for all imports**:

1. **Order imports by category** - builtin → third-party → project → types
2. **Separate type imports** - Always use blank line between code and type imports
3. **Use subpath imports** - When defined in package.json, use subpath instead of relative
4. **Use relative within same subpath** - Files in same subpath use relative imports only

**STRICT order** (blank lines separate each category):

1. **Built-in modules** (`node:`)
2. **Third-party libraries**
3. **Project modules** (subpath `#*`, path alias `@*`, or relative `../`)
4. **Type imports** (repeat same order as above)

```typescript
import { readFile } from 'node:fs/promises';

import { useState } from 'react';
import axios from 'axios';

import { FeatureComponent } from '@/components/FeatureComponent';
import { featureFunction } from '#utilities/feature';
import { parentFunction } from '../helpers';

import type { FC } from 'react';

import type { User } from '#types/user';
```

**Import Style Rules**:

- **NEVER mix code/type imports** - Separate with blank line
- **NEVER use namespace imports** (`import * as`) - Use explicit named imports
- **USE named imports** - Only use defaults when that's the only export
- **ALWAYS separate type imports** - Keep `type` imports on separate lines

```typescript
// ✅ DO: clean, separated imports
import { useState, useEffect } from 'react';
import type { FC } from 'react';

// ❌ DON'T: mixed imports
import React, { useState, type FC } from 'react';

// ❌ DON'T: namespace imports
import * as React from 'react';

// ❌ DON'T: default imports when named available
import React from 'react';
```

**Subpath Requirements**:

Check package.json for subpath mappings under `exports` or `imports`:

```json
{
  "exports": {
    "#utilities/*": "./src/utilities/*.ts",
    "#fastify/*": "./src/fastify/*.ts",
    "#request": "./src/fastify/request.ts"
  }
}
```

**The Two Rules for Subpath Imports**:

**RULE 1: USE SHORTEST SUBPATH (Default)**

For ALL cross-module imports, use the subpath defined in package.json.

```typescript
// ✅ DO: use subpaths for cross-module imports
import { handler } from '#request';
import { helper } from '#utilities/validator';
import { errorHandler } from '#fastify/error';

// ❌ DON'T: use relative paths when subpath exists
import { handler } from './fastify/request';
import { helper } from '../utilities/validator';
import { errorHandler } from './fastify/error';
```

**RULE 2: USE RELATIVE (Same-Subpath Exception)**

For imports WITHIN the same subpath, use relative imports. NEVER use subpath.

```typescript
// File: src/fastify/request.ts (part of #fastify/*)

// ✅ DO: relative imports within same subpath
import { formatResponse } from './response';
import { errorHandler } from './error';

// ❌ DON'T: subpath imports within same subpath
import { formatResponse } from '#fastify/response';
import { errorHandler } from '#fastify/error';

// ✅ DO: subpath to different subpath
import { validate } from '#utilities/validator';
import { request } from './request';
```

### Top-Level Symbol Ordering

Organize file contents in this strict order with blank lines separating major groups. Within each group, order symbols from **root to leaf** (high-level/public to low-level/detail).

**GROUP 1: External Imports**

1. `import` statements (code imports)
2. `import type` statements (type-only imports)

**GROUP 2: Re-exports**
3. `export { ... } from` statements (code re-exports)
4. `export type { ... } from` statements (type-only re-exports)

**GROUP 3: Type Definitions**
5. Exported types/interfaces (`export type`, `export interface`)
6. Private types/interfaces (non-exported)

**GROUP 4: Constants & Variables**
7. Exported constants (`export const`)
8. Private constants (non-exported `const`)

**GROUP 5: Classes**
9. Exported classes (`export class`)
10. Private classes (non-exported)

**GROUP 6: Functions**
11. Exported functions (`export function`, `export const fn =`)
12. Private functions (non-exported)

**Within-Group Ordering: Root to Leaves**

Within each subgroup, order symbols from **high-level** to **low-level/detail** based on call hierarchy:

- **Root level**: Primary API functions, main business logic
- **Branch level**: Helper functions used by root functions
- **Leaf level**: Utility functions, implementation details

```typescript
// ✅ GOOD: root to leaves ordering
export function processUser(user: User): Result {
  const validated = validateUser(user);
  const normalized = normalizeData(validated);
  return formatResult(normalized);
}

// branch: helpers for main API
function validateUser(user: User): ValidatedUser {
  return checkFields(user);
}

function normalizeData(user: ValidatedUser): NormalizedUser {
  return trimFields(user);
}

// leaves: low-level utilities
function checkFields(user: User): ValidatedUser { /* ... */ }
function trimFields(user: ValidatedUser): NormalizedUser { /* ... */ }
function formatResult(user: NormalizedUser): Result { /* ... */ }
```

**Complete File Example**:

```typescript
// GROUP 1: EXTERNAL IMPORTS //

import { readFile } from 'node:fs/promises';

import { validate } from 'express-validator';
import axios from 'axios';

import { DatabaseClient } from '#database/client';
import { logger } from '#utilities/logger';

import type { Request, Response } from 'express';

import type { User, CreateUserInput } from '#types/user';
import type { DatabaseConfig } from '#database/types';

// GROUP 2: RE-EXPORTS //

export { UserRepository } from './repository';
export { createUserService } from './factory';

export type { User, CreateUserInput } from './types';

// GROUP 3: TYPE DEFINITIONS //

export interface UserServiceConfig {
  database: DatabaseConfig;
  cacheEnabled: boolean;
}

export type UserResult = Result<User, UserError>;

interface CacheEntry {
  user: User;
  timestamp: number;
}

// GROUP 4: CONSTANTS //

export const DEFAULT_CACHE_TTL = 3600;
export const USER_VALIDATION_RULES = {
  minAge: 18,
  maxNameLength: 100,
} as const;

const CACHE_KEY_PREFIX = 'user:';

// GROUP 5: CLASSES //

export class UserService {
  #repository: UserRepository;
  #cache: Map<string, CacheEntry>;

  constructor(config: UserServiceConfig) {
    this.#repository = new UserRepository(config.database);
    this.#cache = new Map();
  }

  async findUser(id: string): Promise<UserResult> {
    const cached = this.#getCached(id);
    if (cached) return { success: true, data: cached };

    const user = await this.#repository.find(id);
    if (!user) return { success: false, error: new UserNotFoundError(id) };

    this.#setCached(id, user);
    return { success: true, data: user };
  }

  #getCached(id: string): User | null {
    const entry = this.#cache.get(buildCacheKey(id));
    return entry && !isCacheExpired(entry) ? entry.user : null;
  }

  #setCached(id: string, user: User): void {
    this.#cache.set(buildCacheKey(id), {
      user,
      timestamp: Date.now(),
    });
  }
}

// GROUP 6: FUNCTIONS //

// root: main exported API
export function createUser(input: CreateUserInput): Promise<UserResult> {
  const validated = validateUserInput(input);
  if (!validated.valid) {
    return Promise.resolve({
      success: false,
      error: new ValidationError(validated.errors)
    });
  }

  return persistUser(validated.data);
}

// branch: helpers for main API
function validateUserInput(input: CreateUserInput): ValidationResult {
  const errors = checkRequiredFields(input);
  return { valid: errors.length === 0, errors };
}

async function persistUser(user: User): Promise<UserResult> {
  const saved = await saveToDatabase(user);
  return { success: true, data: saved };
}

// leaves: low-level utilities
function checkRequiredFields(input: CreateUserInput): string[] {
  // implementation
}

function saveToDatabase(user: User): Promise<User> {
  // implementation
}

function buildCacheKey(id: string): string {
  return `${CACHE_KEY_PREFIX}${id}`;
}

function isCacheExpired(entry: CacheEntry): boolean {
  return Date.now() - entry.timestamp > DEFAULT_CACHE_TTL * 1000;
}
```

**Special Cases**:

- **Constants used by multiple groups**: Place in GROUP 4 even if used by types/classes
- **Type guards**: Treat as functions in GROUP 6
- **Factory functions**: Treat as root-level functions in GROUP 6

## Type Definitions

### Interface vs Type

```typescript
// ✅ GOOD: interfaces for object shapes
interface User {
  readonly id: string;
  name: string;
  email: string;
}

// ✅ GOOD: types for unions and computed types
type Status = "active" | "inactive" | "pending";
type UserWithStatus = User & { status: Status };
type EventHandler<T> = (event: T) => void;
```

### Interface Documentation

Document interfaces with JSDoc comments:

```typescript
// ✅ GOOD: documented interface
/** represents a user in the system */
interface User {
  /** identifies the user uniquely */
  id: string;
  /** stores user's full name */
  name: string;
  /** provides email address for authentication */
  email: string;
  // ...
}

// ✅ GOOD: group related fields
interface ApiResponse<T> {
  // response data //
  data: T;
  pagination?: PaginationInfo;
  // metadata //
  status: number;
  requestId: string;
}

// ❌ BAD: missing documentation
interface User {
  id: string;
  name: string;
  // ...
}
```

### Strict Typing Patterns

```typescript
// ✅ GOOD: type guards for unknown values
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value
  );
}

// ✅ GOOD: readonly for immutable data
interface ReadonlyConfig {
  readonly apiUrl: string;
  readonly features: readonly string[];
}

// ✅ GOOD: private fields with #
class UserService {
  #repository: UserRepository;
  #cache = new Map<string, User>();
}
```

## Generic Types

### Generic Constraints

```typescript
// ✅ GOOD: constrained generics
interface Repository<T extends { id: string }> {
  get(id: string): Promise<T | null>;
  save(entity: T): Promise<T>;
}

// ✅ GOOD: conditional types
type ApiResponse<T> = T extends Error
  ? { status: "error"; error: T }
  : { status: "success"; data: T };
```

### Utility Types

```typescript
// ✅ GOOD: use built-in utility types
type CreateUser = Omit<User, "id" | "createdAt">;
type UpdateUser = Partial<Pick<User, "name" | "email">>;
type UserEmail = User["email"];
```

### Error Type Patterns

```typescript
// ✅ GOOD: discriminated union for results
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

// ✅ GOOD: specific error types
class ValidationError extends Error {
  constructor(
    message: string,
    public readonly field: string
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

// ✅ GOOD: usage
function parseUser(input: unknown): Result<User, ValidationError> {
  if (!isValidUserInput(input)) {
    return { success: false, error: new ValidationError("Invalid input", "input") };
  }
  return { success: true, data: input };
}
```

### Advanced Type Patterns

```typescript
// ✅ GOOD: template literal types
type ApiEndpoint = `${'GET' | 'POST'} /api/${string}`;
const endpoint: ApiEndpoint = "GET /api/users";

// ✅ GOOD: mapped types
type Serialized<T> = {
  [K in keyof T]: T[K] extends Date ? string : T[K];
};

type SerializedUser = Serialized<User>;
// { id: string; name: string; createdAt: string; }
```

## Type Guards

Type guards are the ONLY safe alternative to `as unknown as TYPE` casting. See "No Unsafe Type Casting" for detailed explanation and examples of why casting is dangerous.

### Type Guard Patterns

```typescript
// ✅ GOOD: basic type guard pattern
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value
  );
}

// ✅ GOOD: compose type guards
function isUserArray(value: unknown): value is User[] {
  return Array.isArray(value) && value.every(isUser);
}

// ✅ GOOD: type guards for discriminated unions
type ApiResult =
  | { status: "success"; data: User }
  | { status: "error"; message: string };

function isSuccessResult(result: ApiResult): result is Extract<ApiResult, { status: "success" }> {
  return result.status === "success";
}

// usage
const result: ApiResult = await fetchUser();
if (isSuccessResult(result)) {
  console.log(result.data.name); // TypeScript knows result.data exists
}
```

### Testing Exceptions

For testing with partial objects, see "Testing Exceptions" in "No Unsafe Type Casting" (for patterns and detailed guidance on when this is acceptable).

### Module Patterns

```typescript
// ✅ GOOD: named exports
export const userService = new UserService();
export const validateEmail = (email: string): boolean => { ... };

// ✅ GOOD: re-exports
export { UserRepository } from "./user-repository";

export type { User, CreateUser } from "./types";

// ❌ BAD: default exports (avoid unless required)
export default userService;
```

### Barrel Exports

```typescript
// index.ts - barrel export file
export { UserService } from "./user-service";
export { UserRepository } from "./user-repository";

export type { User, CreateUser } from "./types";
```

## Function Parameters

### Parameter Destructuring

```typescript
// ✅ GOOD: safe destructuring with defaults
function processUser(options?: {
  name: string;
  role?: string;
}) {
  const { name, role = 'user' } = { ...options };
  // ...
}

// ❌ BAD: inline destructuring (can fail)
function processUser({ name, role = 'user' }: UserOptions) {
  // throws if called with undefined
}
```

### Interface Strategy

```typescript
// ✅ GOOD: exported functions use separate interfaces
export interface UpdateUserOptions {
  name?: string;
  email?: string;
}
export function updateUser(options: UpdateUserOptions) { ... }

// ✅ GOOD: simple internal functions can use inline types
function processData(options: { data: string; strict?: boolean }) { ... }
```

### Object Property Ordering

Use this **standard order** and grouped with comment separators to improve predictability and readability:

1. **Required identity fields** (e.g. `id`, `file`, `name`)
2. **Primary functional arguments** (e.g. `content`, `source`)
3. **Optional modifiers/flags** (e.g. `isDraft`, `overwrite`, `sortOrder`)
4. **Callback or hooks** (e.g. `onSuccess`, `onError`)
5. **Misc config or metadata** (e.g. `context`, `traceId`)

```typescript
// ✅ GOOD: grouped with comment separators
interface SetUserInput {
  // identity //
  id: string;
  email: string;
  name: string;

  // primary //
  source: string;
  roles: string[];

  // optional //
  isActive?: boolean;

  // hooks //
  onSuccess: ()=>void;

  // metadata //
  createdAt: Date;
  updatedAt: Date;
}
```

## Patterns & Best Practices

### Result/Either Pattern for Error Handling

Encapsulate success and failure states in a discriminated union:

**Purpose**: Functional error handling without exceptions, enabling type-safe error recovery

**When to use**:

- API functions that can fail
- Data transformation pipelines
- User input validation
- Operations with expected failure modes

**Implementation**:

```typescript
// pattern template
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

// real-world example
async function fetchUser(id: string): Promise<Result<User, FetchError>> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      return { success: false, error: new FetchError("User not found") };
    }
    return { success: true, data: await response.json() };
  } catch (err) {
    return { success: false, error: new FetchError("Network error") };
  }
}

// safe usage with type narrowing
const result = await fetchUser("123");
if (result.success) {
  console.log(result.data.name); // data is safely typed
} else {
  console.error(result.error.message);
}
```

### Discriminated Union Pattern

Use literal types to create exhaustive type unions:

**Purpose**: Enable TypeScript's exhaustiveness checking for complete handling of all cases

**Implementation**:

```typescript
// pattern template
type Event<T extends { type: string }> = T;

type Action =
  | { type: 'USER_LOGIN'; userId: string }
  | { type: 'USER_LOGOUT' }
  | { type: 'USER_UPDATE'; userId: string; name: string };

// exhaustive handler with type narrowing
function handleAction(action: Action): void {
  switch (action.type) {
    case 'USER_LOGIN':
      console.log(`Login: ${action.userId}`); // userId is known
      break;
    case 'USER_LOGOUT':
      console.log('Logout');
      break;
    case 'USER_UPDATE':
      console.log(`Update: ${action.name}`); // name is known
      break;
    // ✅ TypeScript error if case is missing!
  }
}
```

### Type Guard Pattern

Create reusable type predicates for runtime validation:

**Purpose**: Safe type narrowing with runtime checks, enabling both TypeScript and runtime safety

**Implementation**:

```typescript
// pattern template
function isType(value: unknown): value is TargetType {
  return (
    typeof value === 'object' &&
    value !== null &&
    'requiredField' in value &&
    // ... more checks
  );
}

// real-world example
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as any).id === 'string' &&
    typeof (value as any).email === 'string' &&
    Array.isArray((value as any).roles)
  );
}

// usage with guaranteed type safety
function processData(data: unknown): void {
  if (!isUser(data)) {
    throw new ValidationError('Invalid user data');
  }
  // data is now safely typed as User
  console.log(data.email);
}
```

### Factory Pattern with Types

Create type-safe object constructors using generics:

**Implementation**:

```typescript
// pattern template
interface Factory<T> {
  create(config: Config): T;
}

// real-world example
interface HandlerFactory<T extends Handler> {
  create(options: { path: string; method: string }): T;
}

const apiHandlerFactory: HandlerFactory<ApiHandler> = {
  create({ path, method }) {
    return {
      path,
      method: method as HttpMethod,
      handle: (request) => ({ status: 200, body: {} }),
    };
  },
};
```

### Common Patterns

1. **Exhaustive Checking** - Use `satisfies` for compile-time validation without type narrowing

   ```typescript
   const config = {
     debug: true,
     port: 3000,
   } satisfies ServerConfig;
   ```

2. **Const Assertions** - Preserve literal types in complex structures

   ```typescript
   const permissions = ['read', 'write', 'admin'] as const;
   type Permission = (typeof permissions)[number]; // "read" | "write" | "admin"
   ```

3. **Async Result Pattern** - Combine Promise with Result type

   ```typescript
   type AsyncResult<T, E = Error> = Promise<Result<T, E>>;

   async function safeFetch(url: string): AsyncResult<Response, FetchError> {
     // implementation
   }
   ```

4. **Branded Types** - Create nominally typed strings for type safety

   ```typescript
   type UserId = string & { readonly brand: 'UserId' };
   function userId(value: string): UserId {
     return value as UserId;
   }
   ```

## Quick Reference

| Pattern             | Use Case          | Example                                                                          |
|---------------------|-------------------|----------------------------------------------------------------------------------|
| Interface           | Object shapes     | `interface User { id: string; }`                                                 |
| Type                | Unions/computed   | `type Status = "active" \| "inactive"`                                           |
| Unknown             | Unsafe input      | `function parse(input: unknown)`                                                 |
| Type Guard          | Runtime check     | `function isUser(x): x is User`                                                  |
| Result Pattern      | Error handling    | `type Result<T, E> = { success: true; data: T } \| { success: false; error: E }` |
| Discriminated Union | Exhaustive checks | `type Action = { type: 'A' } \| { type: 'B' }`                                   |
| Branded Type        | Type safety       | `type UserId = string & { readonly brand: 'UserId' }`                            |

## Quick Decision Tree

### 1. Choosing Between Interface and Type

- **Do you need object shape composition (extending multiple shapes)?**
  - YES → Use `interface`
  - NO → Continue to next decision

- **Do you need union, intersection, or computed types?**
  - YES → Use `type`
  - NO → Use `interface` (more readable)

- **Is this for a public API/export?**
  - YES → Use `interface` (allows declaration merging)
  - NO → Use `type` (simpler, more flexible)

### 2. Handling Unknown Data

- **Does the data come from external sources (API, user input, JSON)?**
  - YES → Use `unknown` type with type guards
  - NO → Use a specific type

- **Do you need to transform the data?**
  - YES → Create a type guard function with validation
  - NO → Just narrow with simple type checks

### 3. When Types Don't Match

See "No Unsafe Type Casting" for detailed decision tree. Quick summary:

- **Never use `as unknown as TYPE`** in production code
- Use type guards, refactor data structures, or fix type definitions instead
- Testing only: `as Partial<TYPE> as TYPE` when partial objects are appropriate

### 4. Error Handling Strategy

- **Can the error be recovered from?**
  - YES → Use Result pattern or return optional
  - NO → Throw an exception

- **Is this function expected to fail in normal operation?**
  - YES → Use Result pattern (discriminated union)
  - NO → Use exceptions (unexpected failures)

### 5. Import Path Decision

- **Is there a subpath defined in package.json for this file?**
  - YES → Continue to next decision
  - NO → Use relative import

- **Are both files in the same subpath?**
  - YES → Use relative import
  - NO → Use subpath import from package.json

### 6. Generic Type Decision

- **Do you need the type parameter in the function/class signature?**
  - YES → Use generics with proper constraints
  - NO → Use wider types or union types

- **Is the generic type used throughout the implementation?**
  - YES → Keep the generic
  - NO → Remove it (over-engineering)
