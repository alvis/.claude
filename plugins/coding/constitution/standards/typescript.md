# TypeScript Standards

_Core TypeScript standards for type safety, imports, and language usage_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- General Coding Principles (standard:general-principles) - Test code must adhere to fundamental coding principles and consistency rules
- Naming Standards (standard:naming) - Test functions must follow function naming, structure, and documentation standards
- Documentation Standards (standard:documentation) - Test interfaces and complex test scenarios require proper JSDoc documentation

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

// ✅ ACCEPTABLE (TESTING ONLY): partial mocking pattern
const mockUser = {
  id: "123",
  name: "Test User",
} as Partial<User> as User; // explicit testing pattern

// ✅ ACCEPTABLE (TESTING ONLY): extends pattern
interface PartialUser extends Pick<User, "id" | "name"> {}
const mockUser: User = { id: "123", name: "Test" } as PartialUser as User;
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

**Testing exceptions ONLY**:

```typescript
// ✅ ACCEPTABLE: Testing with partial objects
const mockUser = {
  id: "123",
  name: "Test User",
} as Partial<User> as User;

// ✅ ACCEPTABLE: Testing with extends pattern
interface TestUser extends Pick<User, "id" | "name"> {}
const mockData: User = testData as TestUser as User;

// NOTE: These patterns ONLY allowed in test files
// Production code must NEVER use these patterns
```

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

<IMPORTANT>

## CRITICAL: Avoid Suppression Comments

**DO NOT use suppression comments** (`eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`, etc.) to silence errors or warnings. It is **VERY RARE** that they are necessary.

### Required Approach

1. **Ultrathink** - Deeply analyze the underlying cause of the error/warning
2. **Use Diagnostic Tools** - Leverage LSP tools (`lsp_get_diagnostics`, `ide__getDiagnostics`) to understand the issue
3. **Fix Properly** - Apply proper solutions:
   - Correct type definitions
   - Add proper type guards
   - Refactor code structure
   - Update imports/exports
   - Fix actual logic errors

### When All Else Fails

- Suppression comments are a **LAST RESORT ONLY**
- **MUST consult with the user** before applying any suppression comment
- Document why suppression is unavoidable
- Create a follow-up task to fix properly

### Examples

```typescript
// ❌ ABSOLUTELY BAD: Silencing the problem
// @ts-ignore
const result: User = riskyFunction();

// ✅ GOOD: Understanding and fixing the root cause
function isValidResult(value: unknown): value is Result {
  return typeof value === "object" && value !== null && "data" in value;
}

const rawResult = riskyFunction();
if (!isValidResult(rawResult)) {
  throw new Error("Invalid result from riskyFunction");
}
const result = rawResult;

// ✅ GOOD: Using type guards to narrow types safely
function processData(input: unknown): User {
  if (!isUser(input)) {
    throw new ValidationError("Invalid user data provided");
  }
  return input; // TypeScript knows input is User
}
```

</IMPORTANT>

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

## Import Organization

### Mandatory Rules

**MUST follow these rules for all imports**:

1. **Order imports by category** - builtin → third-party → project → types
2. **Separate type imports** - Always use blank line between code and type imports
3. **Use subpath imports** - When defined in package.json, use subpath instead of relative
4. **Use relative within same subpath** - Files in same subpath use relative imports only

### Required Import Order

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

### Import Style Rules

**NEVER violate these rules**:

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

### Subpath Requirements

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

### The Two Rules for Subpath Imports

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

### Safe Type Checking

**Type guards are the ONLY safe alternative to `as unknown as TYPE`**:

```typescript
// ✅ GOOD: proper type guards
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value
  );
}

// ✅ GOOD: use type guards instead of casting
function processUser(input: unknown): void {
  if (!isUser(input)) {
    throw new Error("Invalid user input");
  }
  console.log(input.name); // TypeScript knows input is User
}

// ❌ BAD: unsafe type casting
function badProcessUser(input: unknown): void {
  const user = input as unknown as User; // NO VALIDATION!
  console.log(user.name); // could crash at runtime
}
```

**Why type guards are better than `as unknown as TYPE`**:

```typescript
// ❌ DANGEROUS: double casting provides false confidence
function processApiResponse(response: unknown): void {
  const data = response as unknown as ApiResponse; // no validation
  console.log(data.user.name); // runtime crash if structure is wrong
}

// ✅ SAFE: type guard provides runtime validation
function isApiResponse(value: unknown): value is ApiResponse {
  return (
    typeof value === "object" &&
    value !== null &&
    "user" in value &&
    isUser((value as any).user)
  );
}

function processApiResponse(response: unknown): void {
  if (!isApiResponse(response)) {
    throw new ValidationError("Invalid API response structure");
  }
  console.log(response.user.name); // safe - validated at runtime
}
```

**Complex type guard patterns**:

```typescript
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

**Testing patterns (ONLY allowed in test files)**:

```typescript
// ✅ ACCEPTABLE (TESTING ONLY): partial object pattern
const mockUser = {
  id: "123",
  name: "Test User",
  email: "test@example.com",
} as Partial<User> as User;

// ✅ ACCEPTABLE (TESTING ONLY): extends pattern for type safety
interface TestUserData extends Pick<User, "id" | "name" | "email"> {}
const testData: TestUserData = { id: "123", name: "Test", email: "test@example.com" };
const mockUser: User = testData as TestUserData as User;

// NOTE: These patterns ONLY for tests where:
// 1. You don't need all object properties
// 2. The test doesn't access the missing properties
// 3. Using Partial<TYPE> makes the intent clear
```

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

## Anti-Patterns

### Common Mistakes to Avoid

1. ❌ **Type Assertion Misuse (CRITICAL)**

   **Problem**: Using `as unknown as TYPE` bypasses all type safety

   **Why it's dangerous**:
   - No runtime validation - data could be anything
   - Creates false confidence in type correctness
   - Defeats the entire purpose of TypeScript
   - Causes runtime crashes that TypeScript should prevent

   **Solution**: Use type guards with validation OR fix root type issue

   ```typescript
   // ❌ ABSOLUTELY BAD: double casting
   const user = apiResponse as unknown as User; // NO VALIDATION!
   console.log(user.name); // might crash at runtime

   // ❌ ABSOLUTELY BAD: bypassing type safety
   const config = JSON.parse(input) as unknown as Config; // unsafe!

   // ✅ GOOD: type guard with validation
   function isUser(value: unknown): value is User {
     return (
       typeof value === "object" &&
       value !== null &&
       "id" in value &&
       typeof (value as any).id === "string" &&
       "name" in value
     );
   }

   if (!isUser(apiResponse)) {
     throw new ValidationError("Invalid user data from API");
   }
   const user = apiResponse; // safe!

   // ✅ GOOD: fix the root type issue
   interface ApiResponse {
     user: User;
     metadata: Metadata;
   }
   const response: ApiResponse = await fetchData(); // proper types
   const user = response.user; // no casting needed
   ```

   **Testing exception** (ONLY in test files):

   ```typescript
   // ✅ ACCEPTABLE (TESTING ONLY): partial mock pattern
   const mockUser = {
     id: "123",
     name: "Test User",
   } as Partial<User> as User;

   // ✅ ACCEPTABLE (TESTING ONLY): extends pattern
   interface TestUser extends Pick<User, "id" | "name"> {}
   const mockUser: User = testData as TestUser as User;
   ```

   **Before using `as unknown as TYPE` - MUST ask user**:
   - Have you identified the root cause of the type mismatch?
   - Can you use a type guard instead?
   - Can you fix the type definitions?
   - Can you refactor the data structure?
   - Is this truly testing code where partial objects are acceptable?

2. ❌ **Using Any Type**
   - Problem: Defeats TypeScript's purpose
   - Solution: Use `unknown` with type guards
   - Example: `function process(data: any)` // loses type safety

3. ❌ **Mixed Imports**
   - Problem: Mixing code and type imports
   - Solution: Separate type imports
   - Example: `import { useState, type FC } from 'react'` // avoid

## Quick Reference

| Pattern | Use Case | Example |
|---------|----------|----------|
| Interface | Object shapes | `interface User { id: string; }` |
| Type | Unions/computed | `type Status = "active" \| "inactive"` |
| Unknown | Unsafe input | `function parse(input: unknown)` |
| Type Guard | Runtime check | `function isUser(x): x is User` |
| Result Pattern | Error handling | `type Result<T, E> = { success: true; data: T } \| { success: false; error: E }` |
| Discriminated Union | Exhaustive checks | `type Action = { type: 'A' } \| { type: 'B' }` |
| Branded Type | Type safety | `type UserId = string & { readonly brand: 'UserId' }` |

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

### 3. When Types Don't Match (CRITICAL)

**Follow this decision tree instead of using `as unknown as TYPE`**:

- **Are the types actually incompatible?**
  - YES → Continue to next decision
  - NO → There's a bug in your type definitions - fix them first

- **Is this production code?**
  - YES → **NEVER use `as unknown as TYPE`** → Continue to next decision
  - NO (test code) → Consider if partial objects are acceptable → Use `as Partial<TYPE> as TYPE` if appropriate

- **Why don't the types match?**
  - Wrong type definition → Fix the type definition
  - Missing properties → Refactor data structure or use proper type
  - API mismatch → Create proper interface for API response
  - Need validation → Create type guard with runtime checks
  - Data transformation needed → Write transformation function with proper types

- **Have you tried all proper solutions?**
  - NO → Try type guards, refactoring, proper types first
  - YES → **MUST confirm with user before using `as unknown as TYPE`**

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
