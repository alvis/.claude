# File and Directory Naming Standards

Standards for naming files, directories, modules, and environment configurations

## Core Principles

### Case Conventions

Use kebab-case for files, PascalCase for React components.

```typescript
// ✅ GOOD: proper casing
user-service.ts         // Regular file
UserProfile.tsx         // React component
api-client.spec.ts     // Test file

// ❌ BAD: wrong casing
UserService.ts          // Not a component
user_service.ts         // Snake case
userservice.ts          // No separation
```

### Match Export Type

File names should reflect what they export.

```typescript
// ✅ GOOD: noun for class/object
// user-validator.ts
export class UserValidator { ... }

// ✅ GOOD: verb for function
// validate-user.ts  
export function validateUser() { ... }
```

## File Naming Patterns

### TypeScript Files

```typescript
// service files
user-service.ts
payment-processor.ts

// test files
user-service.spec.ts

// type files
user.type.ts
api.type.ts
```

### Component Files

```typescript
// react components - PascalCase
Button.tsx
UserProfile.tsx
NavigationBar.tsx

// component folder structure
UserProfile/
  UserProfile.tsx
  UserProfile.stories.tsx
  UserProfile.css
  index.ts
```

### Index Files

```typescript
// re-export only
export { UserService } from "./user-service";
export type { User } from "./user.types";

// ❌ BAD: logic in index
class UserService { ... }  // Don't define here
```

## Export-Based Naming

### Export Type Matching

```typescript
// noun for class/object
// user-validator.ts
export class UserValidator { ... }

// verb for function
// validate-user.ts
export function validateUser() { ... }

// common patterns:
// parser.ts → class Parser
// parse.ts → function parse()
```

### Multiple Exports

```typescript
// related exports - OK
// user-utils.ts
export function validateUser() { ... }
export function sanitizeUser() { ... }

// ❌ BAD: unrelated exports
export function validateUser() { ... }
export function formatCurrency() { ... }  // Different domain
```

## Quick Reference

| File Type | Pattern | Example | Notes |
|-----------|---------|---------|-------|
| Service | kebab-case + .service | `user-service.ts` | Domain service |
| Repository | kebab-case + .repository | `user-repository.ts` | Data layer |
| Component | PascalCase | `UserProfile.tsx` | React only |
| Test | source + .spec | `user.spec.ts` | Match source |
| Types | kebab-case + .type | `api.type.ts` | Type definitions |
| Config | kebab-case + .config | `database.config.ts` | Configuration |
| Utils | kebab-case + -utils | `date-utils.ts` | Utilities |

## Patterns & Best Practices

### Environment Files

**Purpose**: Environment-specific configuration

**When to use**:

- Different configs per environment
- Secret management

**Implementation**:

Use `.env`, `.env.<environment>`, `.env.<platform>` or `.env.<platform>.<environment>` pattern for environment-specific configurations.

EXAMPLE

```bash
.env                # Global config for universal settings such as npm secret
.env.local          # Local development overrides
.env.development    # Development environment
.env.production     # Production environment
.env.test           # Test environment
.env.supabase.local # Local supabase configuration
```

**`.env.<suffix>.example` Required** - All applications using environment variables MUST provide a sample `.env.<suffix>.example` file with explanation and options for each line.

Note that environment files are loaded in the following order (later files override earlier ones):

1. `.env` (defaults)
2. `.env.local` (local overrides, never committed)
3. `.env.<platform>` (environment-specific)
4. `.env.<platform>.local` (local environment overrides)

## Anti-Patterns

### Poor File Names

```typescript
// ❌ BAD: common mistakes
utils.ts            // Too generic
helpers.ts          // Too vague
index.js            // Too many index files
UserServiceImpl.ts  // Implementation suffix
IUserService.ts     // Interface prefix

// ✅ GOOD: specific names
utilities/date.ts
validation.ts
services/user.ts
```

### Common Mistakes to Avoid

1. **Generic Names**
   - Problem: No clear purpose
   - Solution: Be specific
   - Example: `utilities.ts` → `utilities/date.ts` or `utilities/to-iso-date.ts`

2. **Inconsistent Casing**
   - Problem: Mixed conventions
   - Solution: Stick to one pattern
   - Example: `userService.ts` + `user-repository.ts` → consistent kebab-case

3. **Deep Nesting**
   - Problem: Hard to navigate
   - Solution: Flatten structure
   - Example: Max 3-4 levels deep

## Quick Decision Tree

1. **File type determination**
   - If React component → PascalCase
   - Otherwise → kebab-case
   - If test → match source + .spec

2. **Export type**
   - If exports class/object → noun name
   - If exports function → verb name
   - If multiple related → domain-utils pattern
