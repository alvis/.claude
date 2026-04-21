# File and Directory Naming Standards

Standards for naming files, directories, modules, and environment configurations

## Core Principles

### Case Conventions

Use kebab-case for files, PascalCase for React components.

```typescript
// ✅ GOOD: proper casing
user-service.ts         // Standalone (no typed directory)
user.ts                 // Inside services/ directory
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

### Avoid Path Redundancy

Do not repeat a word in a file name that is already expressed by its parent directory. When a file lives inside a typed directory, omit the type suffix from the file name.

```typescript
// ❌ BAD: word repeated in path
store/token-store.ts
services/user-service.ts
repositories/user-repository.ts

// ✅ GOOD: directory provides the context
store/token.ts
services/user.ts
repositories/user.ts

// ✅ OK: suffix needed when no typed directory
lib/token-store.ts
src/user-service.ts
```

> **Rule of thumb:** Read the full path aloud. If a word appears in both the directory and file name, remove it from the file name.

## File Naming Patterns

### TypeScript Files

```typescript
// service files
user-service.ts               // standalone (no typed directory)
services/user.ts              // inside typed directory (preferred)

// test files
user-service.spec.ts          // standalone
services/user.spec.ts         // inside typed directory

// type files
types.ts                      // co-located types for a module
types/user.ts                 // typed directory for multiple type files
types/api.ts
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
// barrel → barrel: wildcard via subpath alias (covers code and types)
export * from '#auth';

// barrel → leaf: explicit named exports (code then types)
export { UserService } from './user-service';
export type { User } from './types';

// ❌ BAD: wildcard from a leaf file (leaks internal symbols)
export * from './user-service';

// ❌ BAD: explicit picks from another barrel (duplicates its surface area)
export { UserService } from '#auth';

// ❌ BAD: logic in index
class UserService { ... }  // Don't define here
```

See TYP-MODL-04 for the full rule.

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

### Splitting Long Files

When a file exceeds the project's `max-lines` threshold, apply the **two-stage rule** — never split arbitrarily.

**Stage 1 — Extract shared helpers first.** Look for logic that genuinely belongs elsewhere (another existing file, or a new helper module) and move it out. Prefer this when the extracted code is reused by more than one caller, or when it represents a distinct concern that stands on its own.

**Stage 2 — Folder split if still too long.** If the file still exceeds `max-lines` after extraction, split it into a folder using the `<base>.ts` + `<base>/*.ts` pattern:

- The entry file `<base>.ts` remains a thin re-exports/orchestrator and preserves the public surface.
- Helpers live inside `<base>/*.ts` with **short names** — the folder name already provides the context, so do not repeat the base in the file name (see "Avoid Path Redundancy").

```typescript
// ❌ BEFORE: single file is too long
adapters/anthropic.ts          // 520 lines — exceeds max-lines

// ✅ AFTER: folder split with thin entry + short helper names
adapters/anthropic.ts          // thin entry: orchestrates and re-exports
adapters/anthropic/schema.ts   // zod schemas
adapters/anthropic/parse.ts    // response parsing
adapters/anthropic/request.ts  // request building

// ❌ BAD: helper names repeat the base (folder already provides context)
adapters/anthropic/anthropic-schema.ts
adapters/anthropic/anthropic-parse.ts
```

> **Do not split into arbitrary sibling files** (e.g. `anthropic.schema.ts`, `anthropic.parse.ts` alongside `anthropic.ts`) unless that naming is already an established project convention. The folder pattern is preferred because it keeps related helpers grouped and lets the folder name carry the context.

## Quick Reference

| File Type  | Pattern                    | Example              | Notes                          |
|------------|----------------------------|----------------------|--------------------------------|
| Service    | kebab-case (+ -service)    | `services/user.ts`   | Omit suffix in typed directory |
| Repository | kebab-case (+ -repository) | `repositories/user.ts` | Omit suffix in typed directory |
| Component  | PascalCase                 | `UserProfile.tsx`    | React only                     |
| Test       | source + .spec             | `user.spec.ts`       | Match source                   |
| Types      | `types.ts` or `types/<name>.ts` | `types/user.ts` | No `.type` suffix              |
| Config     | kebab-case + .config       | `database.config.ts` | Configuration                  |
| Utils      | kebab-case (+ -utils)      | `utilities/date.ts`  | Omit suffix in typed directory |

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

4. **Path Redundancy**
   - Problem: Same word in directory and file name
   - Solution: Let the directory provide the type context
   - Example: `services/user-service.ts` → `services/user.ts`

## Quick Decision Tree

1. **File type determination**
   - If React component → PascalCase
   - Otherwise → kebab-case
   - If test → match source + .spec

2. **File in typed directory?**
   - If directory already conveys the type (services/, store/, repositories/) → omit type suffix
   - Otherwise → include type suffix

3. **Export type**
   - If exports class/object → noun name
   - If exports function → verb name
   - If multiple related → domain-utils pattern
