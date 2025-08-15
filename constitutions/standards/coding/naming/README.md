# Naming Standards

_Comprehensive naming conventions organized by context for consistent, readable code_

This directory contains focused naming standards that were extracted from the monolithic `naming.md` file to improve navigation and maintainability.

## Naming Standards Overview

| Standard                    | Purpose                           | Key Topics                                  |
| --------------------------- | --------------------------------- | ------------------------------------------- |
| [Variables](@./variables.md) | Variable and constant naming      | camelCase, collections, booleans, constants |
| [Functions](@./functions.md) | Function and method naming        | Verbs, async patterns, callbacks            |
| [Types](@./types.md)         | Types, interfaces, and classes    | PascalCase, generics, enums                 |
| [Files](@./files.md)         | Files and directories             | kebab-case, modules, organization           |
| [Patterns](@./patterns.md)   | Common patterns and anti-patterns | Conventions, acronyms, context              |

## Quick Reference by Use Case

### 🔤 **Naming a Variable**

```typescript
// ✅ Good
const userName = "John";
const isActive = true;
const userList = await getUsers();

// ❌ Bad
const n = "John";
const active = true;
const users = await getUser(); // Misleading
```

→ See [Variables](@./variables.md)

### 📞 **Naming a Function**

```typescript
// ✅ Good
function getUserById(id: string): User {}
async function fetchUserData(): Promise<User> {}
function validateEmail(email: string): boolean {}

// ❌ Bad
function user(id: string): User {}
function data(): User {}
function email(email: string): boolean {}
```

→ See [Functions](@./functions.md)

### 🏗️ **Naming a Type/Interface**

```typescript
// ✅ Good
interface User {}
class UserService {}
type UserRole = "admin" | "user";

// ❌ Bad
interface IUser {}
class user_service {}
type TUserRole = "admin" | "user";
```

→ See [Types](@./types.md)

### 📁 **Naming a File**

```typescript
// ✅ Good
user - service.ts;
Button.tsx;
validate - email.ts;

// ❌ Bad
userService.ts; // Use kebab-case
button.tsx; // Components use PascalCase
validateEmail.ts; // Use kebab-case
```

→ See [Files](@./files.md)

## Core Naming Principles

### 🎯 Clarity Over Brevity

Names should clearly communicate purpose. A longer descriptive name is better than a short cryptic one.

```typescript
// ✅ Good
const userAuthenticationToken = generateToken();

// ❌ Bad
const token = generateToken(); // What kind of token?
const uat = generateToken(); // Cryptic abbreviation
```

### 🔄 Consistency is Key

Use the same naming pattern for similar concepts throughout the codebase.

```typescript
// ✅ Good - Consistent patterns
function getUserById(id: string): User {}
function getProductById(id: string): Product {}
function getOrderById(id: string): Order {}

// ❌ Bad - Inconsistent patterns
function getUserById(id: string): User {}
function fetchProduct(productId: string): Product {}
function orderDetails(id: string): Order {}
```

### 📚 Use Domain Vocabulary

Match the naming to the business domain and use terms that domain experts would recognize.

```typescript
// E-commerce domain
const shoppingCart = new ShoppingCart();
const orderInvoice = generateInvoice(order);
const customerLoyaltyPoints = calculatePoints(purchase);

// Healthcare domain
const patientRecord = new PatientRecord();
const prescriptionRefill = requestRefill(prescription);
const insuranceClaim = submitClaim(treatment);
```

## Case Standards Summary

| Case Style         | Usage                                  | Example                            |
| ------------------ | -------------------------------------- | ---------------------------------- |
| `camelCase`        | Variables, functions, methods          | `userName`, `getUserById()`        |
| `PascalCase`       | Types, interfaces, classes, components | `UserService`, `ApiResponse`       |
| `kebab-case`       | File names, URLs, CSS classes          | `user-service.ts`, `api-client.ts` |
| `UPPER_SNAKE_CASE` | Global constants, env variables        | `MAX_RETRIES`, `API_KEY`           |

## Common Patterns Quick Reference

### Boolean Naming

- **State**: `is` + Adjective → `isActive`, `isVisible`
- **Possession**: `has` + Noun → `hasPermission`, `hasChildren`
- **Capability**: `can` + Verb → `canEdit`, `canDelete`
- **Recommendation**: `should` + Verb → `shouldRefresh`, `shouldRetry`

### Collection Naming

- **Arrays**: Use plural → `users`, `products`, `orders`
- **Maps**: Use `<item>By<Key>` → `userById`, `productsByCategory`
- **Filtered**: Be descriptive → `activeUsers`, `pendingOrders`

### Async Operations

- **External fetch**: `fetch` + Resource → `fetchUserData()`
- **Database ops**: Action + Resource → `createUser()`, `updateProduct()`
- **Complex async**: `retrieve` + Resource → `retrieveUserDashboard()`

### Time-Related

- **Timestamps**: `<event>At` → `createdAt`, `updatedAt`
- **Durations**: Include units → `timeoutMs`, `delaySeconds`
- **Ranges**: `<start>To<End>` → `startDate`, `endDate`

## Anti-Patterns to Avoid

### ❌ Never Use These

```typescript
// Single letters (except loop indices)
const d = new Date();
const u = await getUser();

// Meaningless names
const data = fetchData();
const thing = process();

// Hungarian notation
const strName = 'John';
const arrUsers = [];

// Reserved words
const class = 'UserClass';
const package = {};
```

### ❌ Common Mistakes

```typescript
// Misleading names
const users = await getUser(); // Returns single user

// Abbreviated names
const usr = user;
const err = error;

// Generic names
const handler = () => {};
const process = () => {};

// Number suffixes
const user1 = users[0];
const user2 = users[1];
```

## Framework-Specific Conventions

### React Components

```typescript
// Components - PascalCase files and exports
Button.tsx → export const Button: React.FC
UserProfile.tsx → export const UserProfile: React.FC

// Hooks - camelCase with 'use' prefix
useAuth.ts → export function useAuth()
useLocalStorage.ts → export function useLocalStorage()
```

### Node.js Modules

```typescript
// Services and utilities - kebab-case files
email-service.ts → export class EmailService
auth-middleware.ts → export function authMiddleware()
```

## Quick Decision Tree

1. **Is it a variable or function?** → Use `camelCase`
2. **Is it a type, interface, or class?** → Use `PascalCase`
3. **Is it a file name?** → Use `kebab-case` (except React components)
4. **Is it a global constant?** → Use `UPPER_SNAKE_CASE`
5. **Is it a boolean?** → Prefix with `is`, `has`, `can`, or `should`
6. **Is it a collection?** → Use plural form
7. **Is it async?** → Consider `fetch`, `retrieve`, or async-indicating verbs

## Migration Guide

If you're updating from the old monolithic `naming.md`:

1. **Variables section** → Now in [variables.md](@./variables.md)
2. **Function section** → Now in [functions.md](@./functions.md)
3. **Class/Type section** → Now in [types.md](@./types.md)
4. **File naming section** → Now in [files.md](@./files.md)
5. **Anti-patterns and patterns** → Now in [patterns.md](@./patterns.md)

## References

- [TypeScript Standards](@../../typescript.md) - Language-specific standards
- [General Principles](@../../general-principles.md) - Overall coding standards
- [Folder Structure](@../../folder-structure.md) - Project organization
