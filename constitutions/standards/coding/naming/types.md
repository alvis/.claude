# Type Naming Standards

_Standards for naming classes, interfaces, types, and enums in TypeScript_

## Core Principles

### PascalCase Convention

All types, interfaces, classes, and enums use PascalCase.

```typescript
// ✅ GOOD: PascalCase
interface User {}
class UserService {}
type ApiResponse = {}
enum UserRole {}

// ❌ BAD: wrong casing
interface user {}
class user_service {}
```

### No Prefixes

Avoid Hungarian notation and unnecessary prefixes.

```typescript
// ✅ GOOD: clean names
interface User {}
type UserId = string;

// ❌ BAD: unnecessary prefixes
interface IUser {}
type TUserId = string;
```

### Descriptive Nouns

Types represent things, so use noun phrases.

```typescript
// ✅ GOOD: noun phrases
interface PaymentMethod {}
class OrderRepository {}

// ❌ BAD: verb-based
interface ProcessPayment {}
```

## Interface Naming

### Basic Interfaces

```typescript
// domain models
interface User {
  id: string;
  email: string;
  ...
}

// generic interfaces
interface ApiResponse<T> {
  data: T;
  status: number;
  ...
}

// ❌ BAD: avoid prefixes/suffixes
interface IUser {}         // No 'I' prefix
interface UserInterface {}  // No 'Interface' suffix
```

### Request/Response Patterns

```typescript
// clear purpose
interface CreateUserRequest {
  email: string;
  password: string;
}

interface CreateUserResponse {
  user: User;
  token: string;
}

// generic patterns
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  ...
}
```

## Type Aliases

### Union Types

```typescript
// simple unions
type UserRole = "admin" | "editor" | "viewer";
type Status = "pending" | "active" | "inactive";

// discriminated unions
type ApiResult<T> =
  | { success: true; data: T }
  | { success: false; error: string };
```

### Function Types

```typescript
// clear purpose
type Validator<T> = (value: T) => boolean;
type EventHandler<T> = (event: T) => void;
type AsyncOperation<T> = () => Promise<T>;

// callbacks
type OnSuccess<T> = (result: T) => void;
type OnError = (error: Error) => void;
```

## Class Naming

### Service Pattern

```typescript
// domain services
class UserService { ... }
class PaymentService { ... }
class EmailService { ... }

// ❌ BAD: vague names
class UserManager {}  // What does it manage?
class UserHelper {}   // Too generic
```

## Quick Reference

| Type | Pattern | Example | Notes |
|------|---------|---------|-------|
| Interface | PascalCase noun | `User` | No 'I' prefix |
| Type alias | PascalCase | `UserId` | No 'T' prefix |
| Class | PascalCase + suffix | `UserService` | Purpose suffix |
| Enum | PascalCase | `UserRole` | No 'E' prefix |
| Generic | Single letter | `T, K, V` | Start with T |
| Request | *Request suffix | `CreateUserRequest` | Clear intent |
| Response | *Response suffix | `ApiResponse<T>` | Clear return |

## Patterns & Best Practices

### Generic Parameters

**Purpose:** Type-safe reusable components

**When to use:**

- Container types
- Utility types
- Higher-order functions

**Implementation:**

```typescript
// standard generics
interface Container<T> { value: T; }
interface Map<K, V> { ... }

// constrained generics
interface Repository<T extends { id: string }> {
  findById(id: string): Promise<T | null>;
}
```

### Enum Patterns

**Purpose:** Type-safe constants

**When to use:**

- Fixed set of values
- State machines
- Configuration options

**Implementation:**

```typescript
enum UserRole {
  Admin = "ADMIN",
  User = "USER"
}

// or const assertion
const Status = {
  ACTIVE: "active",
  ...
} as const;
```

### Common Patterns

1. **Error Classes** - *Error suffix

   ```typescript
   ValidationError, NotFoundError, AuthError
   ```

2. **Config Types** - *Config suffix

   ```typescript
   DatabaseConfig, ServerConfig, AuthConfig
   ```

3. **Test Types** - Mock/Stub prefix

   ```typescript
   MockUser, StubRepository, TestFixture
   ```

## Anti-Patterns

### Unnecessary Prefixes

```typescript
// ❌ BAD: Hungarian notation
interface IUser {}      // No 'I' prefix
type TUserId = string;  // No 'T' prefix
enum EStatus {}         // No 'E' prefix

// ✅ GOOD: clean names
interface User {}
type UserId = string;
enum Status {}
```

### Common Mistakes to Avoid

1. **Generic Names**
   - Problem: Too vague to be useful
   - Solution: Be specific about purpose
   - Example: `Data` → `UserData`

2. **Redundant Suffixes**
   - Problem: Adds no value
   - Solution: Use clean names
   - Example: `UserInterface` → `User`

3. **Wrong Casing**
   - Problem: Inconsistent with TypeScript
   - Solution: Always use PascalCase
   - Example: `user_service` → `UserService`

## Quick Decision Tree

1. **Choosing type construct**
   - If object shape → `interface`
   - If union/alias → `type`
   - If implementation → `class`
   - If constants → `enum` or const assertion

2. **Naming pattern**
   - If service → `*Service` suffix
   - If repository → `*Repository` suffix
   - If config → `*Config` suffix
   - If error → `*Error` suffix
