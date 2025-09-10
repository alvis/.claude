# TypeScript Standards

_Core TypeScript standards for type safety, imports, and language usage_

## Core Principles

### Type Safety First

Prioritize compile-time type checking to prevent runtime errors and enhance code reliability. Every type should have a clear, specific purpose that minimizes potential for unexpected behavior.

### Immutability and Predictability

Design types and functions to be as immutable and predictable as possible. Prefer `readonly` types, pure functions, and minimize side effects.

### Explicit Type Narrowing When Needed

Always explicit declare type definitions when narrowing is required, e.g. ✅ `const currency: CurrencyCode = "USD"` over ❌ `const currency = "USD";`

## 🚨 MANDATORY PREREQUISITE STANDARDS

**[IMPORTANT]** Before applying these standards, you MUST also thoroughly read and understand the following foundational standards:

- [General Coding Principles](@./general-principles.md)
- Naming Standards:
  - [Files](@./naming/files.md)
  - [Functions](@./naming/functions.md)
  - [Types](@./naming/types.md)
  - [Variables](@./naming/variables.md)
- [Function Standards](@./functions.md)
- [Documentation Standards](@./documentation.md)

**Compliance is Non-Negotiable:** Every TypeScript implementation MUST adhere to these prerequisite standards in addition to the specific TypeScript guidelines that follow.

## Strict Configuration

### Required Compiler Settings

Always enable strict mode configuration:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
```

### Type Safety Rules

- **NO `any` type** - Use `unknown` or specific types instead
- **For testing errors only**: Use `// @ts-expect-error` comment when necessary
- **Prefer `readonly`** for immutable data structures
- **Use `#private`** over `private` keyword for class members
- **American English only** - Use American spelling in all code, comments, and documentation

### American English Convention

Always use American English spelling:

```typescript
// ✅ GOOD: american English
interface ColorConfig {
  primaryColor: string;
  backgroundColor: string;
  customizable: boolean;
  favoriteColors: string[];
  authorized: boolean;
  initialization: () => void;
}

// ❌ BAD: british English
interface ColourConfig {
  primaryColour: string;
  backgroundColour: string;
  customisable: boolean;
  favouriteColours: string[];
  authorised: boolean;
  initialisation: () => void;
}
```

## Language and Framework Usage

### Use Modern JavaScript/TypeScript Features

Leverage ES6+ features for cleaner code:

```typescript
// ✅ GOOD: modern features
// arrow functions
const double = (n: number): number => n * 2;

// destructuring
const { name, email } = user;

// template literals
const message = `Welcome ${name}!`;

// optional chaining
const city = user?.address?.city;

// nullish coalescing
const port = process.env.PORT ?? 3000;

// array methods
const activeUsers = users.filter((user) => user.isActive);
const userNames = users.map((user) => user.name);
```

### Avoid Deprecated Patterns

Stay current with best practices:

```typescript
// ❌ BAD: deprecated patterns
var name = "John"; // Use const/let
arguments.callee; // Deprecated
with (obj) {
} // Deprecated

// ✅ GOOD: modern alternatives
const name = "John";
const args = [...arguments]; // Or use rest parameters
// Use explicit property access instead of 'with'
```

## Type Definitions

### Interface vs Type

```typescript
// ✅ GOOD: use interfaces for object shapes
interface User {
  readonly id: string;
  name: string;
  email: string;
  createdAt: Date;
}

// ✅ GOOD: use types for unions and computed types
type Status = "active" | "inactive" | "pending";
type UserWithStatus = User & { status: Status };

// ✅ GOOD: use types for function signatures
type EventHandler<T> = (event: T) => void;
```

### Interface Documentation

All interfaces must be fully documented with JSDoc comments:

```typescript
// ✅ GOOD: fully documented interface
/** represents a user in the system */
interface User {
  /** unique identifier */
  id: string;

  /** user's full name */
  name: string;

  /** email address for authentication */
  email: string;

  /** account creation timestamp */
  createdAt: Date;

  /** last profile update timestamp */
  updatedAt: Date;

  /** whether the user has verified their email */
  isVerified: boolean;

  /** user's subscription tier */
  subscriptionLevel: "free" | "pro" | "enterprise";

  /** optional profile settings */
  preferences?: UserPreferences;
}

// ✅ GOOD: group related fields with comments
interface ApiResponse<T> {
  // response data //
  /** the main response payload */
  data: T;
  /** pagination metadata if applicable */
  pagination?: PaginationInfo;

  // response metadata //
  /** http status code */
  status: number;
  /** response timestamp */
  timestamp: string;
  /** request tracking id */
  requestId: string;

  // error information //
  /** error details if request failed */
  error?: ErrorInfo;
}

// ❌ BAD: missing documentation
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
  updatedAt: Date;
}
```

### Interface Guidelines

- **Document every field** with JSDoc comments
- **Use lowercase** for all documentation
- **Be concise** but descriptive
- **Group related fields** with comment separators
- **Explain constraints** or special values
- **Document optional fields** and when they're used

### Strict Typing Patterns

```typescript
// ✅ GOOD: use unknown instead of any
function parseJson(input: string): unknown {
  return JSON.parse(input);
}

// ✅ GOOD: type guards for unknown values
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value &&
    "email" in value
  );
}

// ✅ GOOD: readonly for immutable data
interface ReadonlyConfig {
  readonly apiUrl: string;
  readonly timeout: number;
  readonly features: readonly string[];
}

// ✅ GOOD: private fields with #
class UserService {
  #repository: UserRepository;
  #cache: Map<string, User> = new Map();

  constructor(repository: UserRepository) {
    this.#repository = repository;
  }
}
```

## Import Organization

### Critical Import Rules

**REQUIRED IMPORT ORDER:**

1. **Import actual code before types**
2. **Separate import groups with a blank line**
3. **Keep type imports separate from actual imports**
4. **Follow this specific order:**
   - Building modules (prefixed with `node:`)
   - Libraries
   - Project modules:
     - Components starting with `@/`
     - Helpers prefixed with `#`
     - Relative path imports (farthest to closest: `../../*`, `../*`, `./*`)
5. **Use the same import order for types as for actual code**

### Import Examples

```typescript
// built-in modules
import { log } from 'node:console';
import { readFile } from 'node:fs/promises';

// third-party libraries
import { LibComponent } from 'some-library';
import { useState, useEffect } from 'react';
import axios from 'axios';

// project modules
import { FeatureComponent } from '@/components/FeatureComponent';
import { useFeature } from '@/hooks/useFeature';
import { featureFunction } from '#utils/featureUtils';
import { parentFunction } from '../helpers';
import { SiblingComponent } from './SiblingComponent';

// built-in modules
import type { Console } from 'node:console';

// third-party libraries
import type { AxiosResponse } from 'axios';
import type { FC, ReactNode } from 'react';

// project modules
import type { FeatureProps } from '@/types/feature';
import type { UserData } from '#types/user';
import type { LocalConfig } from './types';
```

### Import Rules

- **NO mixed code/type imports** - Avoid `import { useState, type FC } from 'react';`
- **NO default imports** (except when required by library)
- **NO namespace imports** (`import * as`) - Avoid `import * as React from 'react';`
- **Prefer named imports**
- **Use subpath imports** (e.g., `#components`) when available in package.json

```typescript
// ✅ GOOD: named imports
import { useState, useEffect } from "react";
import { UserService } from "#services/user";

// ✅ GOOD: separate type imports
import type { User } from "#types/user";
import type { FC } from "react";

// ❌ BAD: mixed imports
import React, { useState, type FC } from "react";

// ❌ BAD: namespace imports
import * as React from "react";

// ❌ BAD: default imports when named available
import React from "react";
```

## Generic Types

### Generic Constraints

```typescript
// ✅ GOOD: constrained generics
interface Repository<T extends { id: string }> {
  get(id: string): Promise<T | null>;
  save(entity: T): Promise<T>;
}

// ✅ GOOD: multiple constraints
function merge<
  T extends Record<string, unknown>,
  U extends Record<string, unknown>,
>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}

// ✅ GOOD: conditional types
type ApiResponse<T> = T extends Error
  ? { status: "error"; error: T }
  : { status: "success"; data: T };
```

### Utility Types

```typescript
// ✅ GOOD: use built-in utility types
type CreateUser = Omit<User, "id" | "createdAt" | "updatedAt">;
type UpdateUser = Partial<Pick<User, "name" | "email">>;
type UserEmail = User["email"];

// ✅ GOOD: custom utility types
type NonNullable<T> = T extends null | undefined ? never : T;
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};
```

## Error Handling Types

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
    public readonly field: string,
    public readonly value: unknown,
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

// ✅ GOOD: error handling with types
function parseUser(input: unknown): Result<User, ValidationError> {
  if (!isValidUserInput(input)) {
    return {
      success: false,
      error: new ValidationError("Invalid user input", "input", input),
    };
  }

  return { success: true, data: input };
}
```

## Advanced Type Patterns

### Template Literal Types

```typescript
// ✅ GOOD: template literal types for API routes
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type ApiRoute = `/api/${string}`;
type ApiEndpoint = `${HttpMethod} ${ApiRoute}`;

// Usage
const endpoint: ApiEndpoint = "GET /api/users";
```

### Mapped Types

```typescript
// ✅ GOOD: mapped types for transformations
type Optional<T> = {
  [K in keyof T]?: T[K];
};

type Serialized<T> = {
  [K in keyof T]: T[K] extends Date
    ? string
    : T[K] extends object
      ? Serialized<T[K]>
      : T[K];
};

// Usage
type SerializedUser = Serialized<User>;
// { id: string; name: string; email: string; createdAt: string; }
```

## Type Assertion and Guards

### Type Guards

```typescript
// ✅ GOOD: proper type guards
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof (value as any).id === "string" &&
    "name" in value &&
    typeof (value as any).name === "string"
  );
}

// ✅ GOOD: array type guards
function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(isString);
}
```

### Safe Type Assertions

```typescript
// ✅ GOOD: use type guards instead of assertions
function processUser(input: unknown): void {
  if (!isUser(input)) {
    throw new Error("Invalid user input");
  }

  // TypeScript now knows input is User
  console.log(input.name);
}

// ❌ Avoid: Unsafe type assertions
function badProcessUser(input: unknown): void {
  const user = input as User; // Unsafe!
  console.log(user.name);
}
```

## Module and Namespace Usage

### Module Patterns

```typescript
// ✅ GOOD: named exports
export const userService = new UserService();
export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

// ✅ GOOD: re-exports
export { UserRepository } from "./user-repository";
export { EmailService } from "./email-service";
export type { User, CreateUser, UpdateUser } from "./types";

// ❌ Avoid: Default exports unless required
export default userService; // Only when library requires it
```

### Barrel Exports

```typescript
// index.ts - Barrel export file
export { UserService } from "./user-service";
export { UserRepository } from "./user-repository";
export { validateUser } from "./validation";

export type { User, CreateUser, UpdateUser } from "./types";
```

## Function Parameter Patterns

### Parameter Destructuring

Follow these patterns for parameter destructuring and defaults:

- **Avoid inline destruct in parameter declarations**
- **Handle optional parameters with defaults at the start**
- **Use object spread for safe destruct**
- **Never destruct nullable parameters directly**

```typescript
// ❌ BAD: inline destructuring with defaults
function processUser({
  name,
  role = 'user',
  status = 'active'
}: {
  name: string
  role?: string
  status?: string
}) { }

// ✅ GOOD: clean parameter declaration with safe destructuring
function processUser(options?: {
  name: string
  role?: string
  status?: string
}) {
  const {
    name,
    role = 'user',
    status = 'active'
  } = { ...options }
}

// ✅ GOOD: using default values for optional parameters
function configure(options: Options = { timeout: 1000, retries: 3 }) {
  // Safe to use options directly
}
```

### Object Parameters Shape Declaration

Follow these guidelines when defining function parameters:

#### For Exported Functions

Always define parameter shapes as separate interfaces:

```typescript
// ✅ GOOD: exported function with separate interface
export interface UpdateUserOptions {
  name?: string;
  email?: string;
}

export function updateUser(options: UpdateUserOptions) { ... }
```

#### For Internal Functions

Use inline parameter shapes for simpler functions:

```typescript
// ✅ GOOD: simple internal function with inline types
function processData(options: { data: string; strict?: boolean }) { ... }

// ✅ GOOD: complex parameters warrant separate interface
interface ValidationConfig {
  rules: Rule[];
  strict: boolean;
  onError?: (error: Error) => void;
}

function validateInternal(config: ValidationConfig) { ... }

// ✅ GOOD: shared interface with exported function
export interface AuthOptions {
  token: string;
  refresh?: boolean;
}

export function authenticate(options: AuthOptions) { ... }
function validateAuth(options: AuthOptions) { ... }
```

### Object Parameter Ordering

Use this **standard order** to improve predictability and readability:

1. **Required identity fields** (e.g. `id`, `file`, `name`)
2. **Primary functional arguments** (e.g. `content`, `source`)
3. **Optional modifiers/flags** (e.g. `isDraft`, `overwrite`, `sortOrder`)
4. **Callback or hooks** (e.g. `onSuccess`, `onError`)
5. **Misc config or metadata** (e.g. `context`, `traceId`)

```typescript
function uploadFile({
  file,
  destination,
  overwrite = false,
  onProgress,
  context,
}: {
  file: File
  destination: string
  overwrite?: boolean
  onProgress?: (percent: number) => void
  context?: UploadContext
}) { ... }
```

### Object Property Ordering

For complex objects and interfaces, organize properties into logical groups with comment separators:

```typescript
interface User {
  // index //
  id: string;
  uuid: string;

  // identity //
  email: string;
  name: string;
  username: string;

  // permissions //
  isActive: boolean;
  isAdmin: boolean;
  roles: string[];

  // metadata //
  createdAt: Date;
  updatedAt: Date;
}
```

**Guidelines:**

- Group related properties together
- Order properties alphabetically within each group
- Use `// groupname //` comment separators
- Common groups: index, identity, config, permissions, metadata, timestamps

## Configuration and Environment Types

### Environment Variables

```typescript
// ✅ GOOD: typed environment configuration
interface EnvironmentConfig {
  readonly NODE_ENV: "development" | "staging" | "production";
  readonly PORT: number;
  readonly DATABASE_URL: string;
  readonly JWT_SECRET: string;
}

function loadConfig(): EnvironmentConfig {
  const config = {
    NODE_ENV: process.env.NODE_ENV as EnvironmentConfig["NODE_ENV"],
    PORT: parseInt(process.env.PORT || "3000", 10),
    DATABASE_URL: process.env.DATABASE_URL,
    JWT_SECRET: process.env.JWT_SECRET,
  };

  // Validate required fields
  if (!config.DATABASE_URL || !config.JWT_SECRET) {
    throw new Error("Missing required environment variables");
  }

  return config;
}
```

## Testing Types

### Test Type Patterns

```typescript
// ✅ GOOD: mock types
type MockUser = jest.Mocked<User>;
type MockRepository<T> = jest.Mocked<Repository<T>>;

// ✅ GOOD: test data factories
function createTestUser(overrides: Partial<User> = {}): User {
  return {
    id: "test-user-id",
    name: "Test User",
    email: "test@example.com",
    createdAt: new Date(),
    updatedAt: new Date(),
    ...overrides,
  };
}

// ✅ GOOD: type-safe test assertions
function assertIsUser(value: unknown): asserts value is User {
  if (!isUser(value)) {
    throw new Error("Expected User object");
  }
}
```

## Anti-Patterns

### Type Assertion Misuse

```typescript
// ❌ BAD: Unsafe type assertions that bypass type checking
const user = input as User; // Completely unsafe!

// Problem: No runtime guarantee that input matches User type
// Risks silent failures and potential runtime errors

// ✅ GOOD: Safe type narrowing with type guards
function safeProcessUser(input: unknown): void {
  if (!isUser(input)) {
    throw new Error("Invalid user input");
  }
  // TypeScript guarantees input is User
}
```

### Overly Broad Types

```typescript
// ❌ BAD: any type that defeats TypeScript's purpose
function processData(data: any) { ... }

// Problem: Loses all type safety, equivalent to writing JavaScript
// Risks unexpected runtime errors

// ✅ GOOD: Use unknown with type guards
function processData(data: unknown) {
  if (typeof data === 'object' && data !== null) {
    // Safely handle object data
  }
}
```
