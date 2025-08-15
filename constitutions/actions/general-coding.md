# General Coding Standards

_Core standards for day-to-day code writing across all languages and frameworks_

## Table of Contents

- [Security Principles](#security_principles) `security_principles`
- [TypeScript Core](#typescript_core) `typescript_core`
- [Naming Conventions](#naming_conventions) `naming_conventions`
- [Function Design](#function_design) `function_design`
- [File Organization](#file_organization) `file_organization`
- [Code Quality](#code_quality) `code_quality`
- [TDD Workflow](#tdd_workflow) `tdd_workflow` - **workflow:** `write-code`
- [Documentation Standards](#documentation_standards) `documentation_standards`
- [Error Handling](#error_handling) `error_handling`
- [Before Coding](#before_coding) `before_coding` - **workflow:** `prepare-coding`

<security_principles>

## 🔒 Security First

### NEVER Commit Secrets

- Use mocks in tests - no real secrets required
- No private keys except in unit tests
- Private keys must not appear outside test environments
- Provide `.env.example` with all keys and explanations
- Use approved secret managers only
- Use specific error classes either by defining one or from a destinated package

</security_principles>

<typescript_core>

## 📘 TypeScript Standards

### Strict Configuration

- Strict mode ALWAYS (`strict: true`)
- **NO `any` type** - use `unknown` or specific types
- **For testing errors only**: use `// @ts-expect-error` comment when necessary
- Prefer `readonly` for immutable data
- Use `#private` over `private` keyword
- American English throughout

### Import Organization

**CRITICAL: Import Rules**

1. Node built-ins (`node:*`)
2. Third-party libraries
3. Project modules:
   - `#*` subpath imports (REQUIRED when available)
   - Relative imports (`../../*` → `../*` → `./*`)

```typescript
// Code imports
import { readFile } from "node:fs/promises";
import { useState } from "react";
import { useFeature } from "#hooks/useFeature";
import { helper } from "../utils";

// Type imports (separate)
import type { FC } from "react";
import type { FeatureProps } from "#types/feature";
```

### Rules

- NO mixed code/type imports
- NO default imports (except required by library)
- NO namespace imports (`import * as`)
- Prefer named imports

</typescript_core>

<naming_conventions>

## 🏷️ Naming Conventions

### Case Standards

- `camelCase` - Variables, functions
- `PascalCase` - Types, classes, components
- `UPPER_SNAKE` - Global constants only

### Variables

- Be specific: `employees` not `users` when filtering
- Full descriptive names: `userId` not `userID`
- Well-known acronyms OK: `id`, `url`
- Plural nouns for collections: `clients`, `clientMap`, `clientsById`

### Functions

**Verb-first principle** - start with action verb:

- Data retrieval: `get`, `find`, `list`
- Data creation: `insert`, `add`
- Data modification: `update`, `change`
- Data upsert: `set`
- External retrieval: `fetch`, `retrieve`

### Factory Functions

- `createX()` for simple creation
- `xFactory()` for reusable factories with configuration

### Booleans

- `is<Adjective>` - Current states (isActive, isVisible)
- `has<Noun>` - Possession/milestones (hasAttachment, hasCompletedOnboarding)

### Classes

- PascalCase nouns: `EmailValidator`, `OrderProcessor`
- Self-contained, avoid abbreviations

### Acronyms

- Always UPPER case: `getHTMLParser` not `getHtmlParser`

</naming_conventions>

<function_design>

## ⚙️ Function Design

### Core Principles

- **Single Responsibility** - Functions <60 lines
- **Pure Functions Preferred** - No side effects when possible
- **Always declare return types explicitly**
- **Prefer Functions Over Classes** - Make function out of a class as much as possible
- **Extract Static Methods** - A class method must be out of a class if it doesn't access `this`

### Parameter Patterns

#### Positional vs Object Parameters

**Use Positional (≤2 parameters) when:**

- Intuitive, natural order
- All parameters required
- Parameter order commonly understood
  **Use Object (≥3 parameters) when:**
- Optional values or config-style flags
- Parameters closely related
- Need named arguments for clarity

#### Parameter Object Naming

- `params` - Structured query/command inputs
- `query` - Declarative filtering criteria
- `options` - Optional modifiers/behavior flags
- `data` - Core subject matter
- `config` - Configuration options
- `context` - Execution context
- `details` - Supplementary input

#### Parameter Ordering

1. Required identity fields (id, file, name)
2. Primary functional arguments (content, source)
3. Optional modifiers/flags (isDraft, overwrite)
4. Callbacks (onSuccess, onError)
5. Misc config/metadata (context, traceId)

### Interface Strategy

**Exported functions:** Always separate interfaces
**Internal functions:** Inline types for simple, separate for complex

### Parameter Destructuring Safety

When destructuring optional parameters, use object spread for safety:

```typescript
// ❌ BAD: direct destructuring can fail if undefined
function processUser({ name, role = "user" }: UserOptions) {}

// ✅ GOOD: safe destructuring with spread
function processUser(options?: UserOptions) {
  const { name, role = "user" } = { ...options };
}
```

</function_design>

<file_organization>

## 📁 File Organization

**🚨 CRITICAL FILE CREATION RULES:**

- **Do NOT create files unless absolutely necessary** - prefer editing existing files
- **Do NOT proactively create documentation files** unless explicitly requested
- Always check for existing components before creating new ones

### "Name as Exported" Principle

- **emitter.ts** - exports object/class representing an emitter
- **emit.ts** - exports function/action for emitting

### File Naming

- Code files: `camelCase.ts`
- Components: `PascalCase.tsx`
- Hooks: `camelCase.ts` (useAuth.ts)

### Environment Files

Must start with `.env`:

- ✅ `.env.development`
- ✅ `.env.supabase.local`
- ❌ `env.local`, `.supabase.env`

### Component Structure

```
components/
├── Button/
│   ├── Button.tsx          # Component
│   ├── Button.spec.tsx     # Tests
│   ├── Button.stories.tsx  # Basic stories
│   └── index.ts            # Barrel export
```

</file_organization>

<code_quality>

## ✨ Code Quality Standards

### Pure Functions & Immutability

```typescript
// ✅ Pure - no side effects
const add = (a: number, b: number) => a + b;

// ❌ Impure - modifies external state
let total = 0;
const addToTotal = (n: number) => {
  total += n;
};
```

### Immutability Rules

- **Use `const` by default** - avoid `let` whenever possible
- **Use const and pure functions as much as possible**
- Never mutate parameters
- Use spread operators, map, filter
- Local mutation OK for performance only

### Object Organization

Group related keys and alphabetize within groups:

```typescript
{
  // index //
  id: '123',

  // display //
  email: 'user@example.com',
  name: 'John Doe',

  // flags //
  isActive: true,
}
```

### Text Generation

```typescript
// Multi-line text with conditional parts
const message = ["Hello", userName && `Welcome ${userName}`, "Please login"]
  .filter(Boolean)
  .join("\n");
```

</code_quality>

<tdd_workflow>

## 🧪 Test-Driven Development (TDD)

**🔴 CRITICAL REQUIREMENT: YOU MUST follow TDD practices - write tests BEFORE implementation**

<workflow name="write-code">

### Full Development Workflow

**Complete process for implementing any feature:**

1. **Plan Tests** - Write test descriptions for expected behavior
2. **Write Tests** - Create failing test cases FIRST
3. **Write Skeleton** - Add minimal type-conforming code
4. **Implement** - Write code to pass tests
5. **Verify** - Run `npx tsc --noEmit`, `npm run coverage` and `npm run lint`
6. **Fix Issues** - Fix any issues without modifying tests
7. **Commit** - Commit with descriptive message following git standards

**⚠️ NO EXCEPTIONS: Tests must be written before any implementation code**

</workflow>

### Test File Structure

- Unit: `*.spec.ts`
- Integration: `*.spec.int.ts`
- Type tests: `*.spec-d.ts`
- React components: `*.spec.tsx`
- Prefix descriptions: `fn:` `op:` `cl:` `ty:` `rc:`

### Test Format (BDD Style)

```typescript
describe("fn:fetchUserProfile", () => {
  it("should return user data when given valid id", () => {
    const expected = { id: "123", name: "John" };

    const result = fetchUserProfile("123");

    expect(result).toEqual(expected);
  });
});
```

### Coverage Requirements

- Target 100% coverage with minimal tests
- Use Arrange → Act → Assert pattern
- Mock all external dependencies in unit tests
- Focus on edge cases and complex logic

</tdd_workflow>

<documentation_standards>

## 📚 Documentation & Comments

### JSDoc Format

- One-line preferred: `/** handles user auth */`
- Functions: 3rd-person verb, lowercase, no period
- Non-functions: Noun phrases
- List all `@param` and `@throws`
- NO TypeScript types in prose

### JSDoc Examples

```typescript
// FUNCTIONS: 3rd-person verbs
/** fetches user profile from database */
async function fetchUserProfile(userId: string): Promise<User> {
  // ...
}

// NON-FUNCTIONS: Noun phrases
/** configuration options for API client */
interface ApiConfig {
  /** base URL for requests */
  baseUrl: string;
  /** timeout in milliseconds */
  timeout: number;
}
```

### Inline Comments

#### When to Comment

- Explain WHY, not WHAT
- Document workarounds or constraints
- Clarify non-obvious decisions
- Public APIs, parameters, return values
- Known side effects
- NEVER restate the code

#### Comment Casing Rules

- **Always lowercase** for sentences/phrases
  - ✅ `// check user exists before proceeding`
  - ❌ `// Check user exists before proceeding`
- **Uppercase** only for referencing code elements
  - ✅ `// API calls require authentication token`
  - ✅ `// Layout components should be memoized`

#### Comment Tags

**Temporary Tags (Do NOT commit):**

- `// TODO:` - Implementation needed
- `// FIXME:` - Broken code needs fixing
- `// DEBUG:` - Debug code to remove
- `// TEMP:` - Temporary code/stubs
  **Documentation Tags (Can stay):**
- `// HACK:` - Non-ideal solution to refactor later
- `// WORKAROUND:` - Bypasses external issue
- `// NOTE:` - Important context/explanation
- `// WARNING:` - Potential risks/edge cases
- `// PERFORMANCE:` - Performance considerations
- `// SECURITY:` - Security implications
- `// COMPATIBILITY:` - Browser/platform compatibility issues
- `// LIMITATION:` - Known implementation limitations

</documentation_standards>

<error_handling>

## 🚨 Error Handling Standards

### Error Classification

```typescript
// Use specific error classes
class ValidationError extends Error {
  constructor(
    message: string,
    public field: string,
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

class NotFoundError extends Error {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`);
    this.name = "NotFoundError";
  }
}
```

### Error Handling Patterns

- NO silent errors - always handle explicitly
- Use specific error classes either by defining one or from a destinated package
- Log errors with context (requestId, userId, operation)
- Return meaningful error messages to users
- Never expose internal details in user-facing errors

### Logging Standards

```typescript
// Structured logging with context
logger.error("User validation failed", {
  error: error.message,
  userId,
  requestId,
  field: error.field,
});
```

</error_handling>

<before_coding>

## 🔍 Pre-Coding Checklist

<workflow name="prepare-coding">

### Before Writing Code

- Verify libraries in package.json
- Look at neighboring files for patterns
- Check existing components before creating new
- Match import style and framework choices
- Reuse existing utilities and helpers

### Quality Gates

**Required Before Committing:**

```bash
pnpm --filter <project> test -- --coverage
pnpm --filter <project> lint
npm run typecheck  # if available
```

Skip only when modifying comments/docs.

</workflow>

</before_coding>
