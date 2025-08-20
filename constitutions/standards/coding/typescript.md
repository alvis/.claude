# TypeScript Standards

_Core TypeScript standards for type safety, imports, and language usage_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- [General Coding Principles](@./general-principles.md) - Test code must adhere to fundamental coding principles and consistency rules
- [Function Standards](@./functions.md) - Test functions must follow function naming, structure, and documentation standards
- [Documentation Standards](@./documentation.md) - Test interfaces and complex test scenarios require proper JSDoc documentation

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

### Import Order

**Required order:**

1. Built-in modules (`node:`)
2. Third-party libraries
3. Project modules (`@/`, `#`, relative)
4. Type imports (same order)

```typescript
import { readFile } from 'node:fs/promises';

import { useState } from 'react';
import axios from 'axios';

import { FeatureComponent } from '@/components/FeatureComponent';
import { featureFunction } from '#utils/featureUtils';
import { parentFunction } from '../helpers';

import type { FC } from 'react';

import type { User } from '#types/user';
```

### Import Rules

- **NO mixed code/type imports**
- **NO namespace imports** (`import * as`)
- **Prefer named imports**
- **Use subpath imports** (e.g., `#components`) when available in package.json
- **Separate type imports**

```typescript
// ✅ GOOD: clean imports
import { useState, useEffect } from 'react';
import type { FC } from 'react';

// ❌ BAD: mixed imports
import React, { useState, type FC } from 'react';

// ❌ BAD: namespace imports
import * as React from 'react';

// ❌ BAD: default imports when named available
import React from 'react';
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

// ✅ GOOD: use type guards instead of assertions
function processUser(input: unknown): void {
  if (!isUser(input)) {
    throw new Error("Invalid user input");
  }
  console.log(input.name); // TypeScript knows input is User
}

// ❌ BAD: unsafe type assertions
function badProcessUser(input: unknown): void {
  const user = input as User; // unsafe!
  console.log(user.name);
}
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

## Anti-Patterns

### Common Mistakes to Avoid

1. **Type Assertion Misuse**
   - Problem: Using `as` without runtime validation
   - Solution: Use type guards instead
   - Example: `input as User` // unsafe

2. **Using Any Type**
   - Problem: Defeats TypeScript's purpose
   - Solution: Use `unknown` with type guards
   - Example: `function process(data: any)` // loses type safety

3. **Mixed Imports**
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
