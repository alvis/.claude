# TypeScript Standards

_Core TypeScript standards for type safety, imports, and language usage_

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
// ✅ Good: American English
interface ColorConfig {
  primaryColor: string;
  backgroundColor: string;
  customizable: boolean;
  favoriteColors: string[];
  authorized: boolean;
  initialization: () => void;
}

// ❌ Bad: British English
interface ColourConfig {
  primaryColour: string;
  backgroundColour: string;
  customisable: boolean;
  favouriteColours: string[];
  authorised: boolean;
  initialisation: () => void;
}
```

## Type Definitions

### Interface vs Type

```typescript
// ✅ Good: Use interfaces for object shapes
interface User {
  readonly id: string;
  name: string;
  email: string;
  createdAt: Date;
}

// ✅ Good: Use types for unions and computed types
type Status = "active" | "inactive" | "pending";
type UserWithStatus = User & { status: Status };

// ✅ Good: Use types for function signatures
type EventHandler<T> = (event: T) => void;
```

### Interface Documentation

All interfaces must be fully documented with JSDoc comments:

```typescript
// ✅ Good: Fully documented interface
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

// ✅ Good: Group related fields with comments
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

// ❌ Bad: Missing documentation
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
// ✅ Good: Use unknown instead of any
function parseJson(input: string): unknown {
  return JSON.parse(input);
}

// ✅ Good: Type guards for unknown values
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value &&
    "email" in value
  );
}

// ✅ Good: Readonly for immutable data
interface ReadonlyConfig {
  readonly apiUrl: string;
  readonly timeout: number;
  readonly features: readonly string[];
}

// ✅ Good: Private fields with #
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

1. **Node built-ins** (`node:*`)
2. **Third-party libraries**
3. **Project modules**:
   - `#*` subpath imports (REQUIRED when available)
   - Relative imports (`../../*` → `../*` → `./*`)

### Import Examples

```typescript
// ✅ Good: Proper import order
// 1. Node built-ins
import { readFile } from "node:fs/promises";
import { join } from "node:path";

// 2. Third-party libraries
import { useState, useEffect } from "react";
import { z } from "zod";

// 3. Project modules with subpath imports
import { useFeature } from "#hooks/useFeature";
import { validateEmail } from "#utils/validation";

// 4. Relative imports (closest last)
import { helper } from "../utils/helper";
import { config } from "./config";

// Type imports (separate section)
import type { FC } from "react";
import type { User } from "#types/user";
import type { Config } from "./types";
```

### Import Rules

- **NO mixed code/type imports**
- **NO default imports** (except when required by library)
- **NO namespace imports** (`import * as`)
- **Prefer named imports**
- **Use subpath imports** (e.g., `#components`) when available in package.json

```typescript
// ✅ Good: Named imports
import { useState, useEffect } from "react";
import { UserService } from "#services/user";

// ✅ Good: Separate type imports
import type { User } from "#types/user";
import type { FC } from "react";

// ❌ Bad: Mixed imports
import React, { useState, type FC } from "react";

// ❌ Bad: Namespace imports
import * as React from "react";

// ❌ Bad: Default imports when named available
import React from "react";
```

## Generic Types

### Generic Constraints

```typescript
// ✅ Good: Constrained generics
interface Repository<T extends { id: string }> {
  get(id: string): Promise<T | null>;
  save(entity: T): Promise<T>;
}

// ✅ Good: Multiple constraints
function merge<
  T extends Record<string, unknown>,
  U extends Record<string, unknown>,
>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}

// ✅ Good: Conditional types
type ApiResponse<T> = T extends Error
  ? { status: "error"; error: T }
  : { status: "success"; data: T };
```

### Utility Types

```typescript
// ✅ Good: Use built-in utility types
type CreateUser = Omit<User, "id" | "createdAt" | "updatedAt">;
type UpdateUser = Partial<Pick<User, "name" | "email">>;
type UserEmail = User["email"];

// ✅ Good: Custom utility types
type NonNullable<T> = T extends null | undefined ? never : T;
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};
```

## Error Handling Types

### Error Type Patterns

```typescript
// ✅ Good: Discriminated union for results
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

// ✅ Good: Specific error types
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

// ✅ Good: Error handling with types
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
// ✅ Good: Template literal types for API routes
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type ApiRoute = `/api/${string}`;
type ApiEndpoint = `${HttpMethod} ${ApiRoute}`;

// Usage
const endpoint: ApiEndpoint = "GET /api/users";
```

### Mapped Types

```typescript
// ✅ Good: Mapped types for transformations
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
// ✅ Good: Proper type guards
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

// ✅ Good: Array type guards
function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(isString);
}
```

### Safe Type Assertions

```typescript
// ✅ Good: Use type guards instead of assertions
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
// ✅ Good: Named exports
export const userService = new UserService();
export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

// ✅ Good: Re-exports
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

## Configuration and Environment Types

### Environment Variables

```typescript
// ✅ Good: Typed environment configuration
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
// ✅ Good: Mock types
type MockUser = jest.Mocked<User>;
type MockRepository<T> = jest.Mocked<Repository<T>>;

// ✅ Good: Test data factories
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

// ✅ Good: Type-safe test assertions
function assertIsUser(value: unknown): asserts value is User {
  if (!isUser(value)) {
    throw new Error("Expected User object");
  }
}
```
