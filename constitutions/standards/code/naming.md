# Naming Conventions - Overview

_This file has been reorganized into focused, context-specific naming standards for better navigation._

## 📁 Naming Standards Have Moved

The comprehensive naming standards have been split into specialized files for easier reference and maintenance:

### Core Naming Standards

| Standard      | Purpose                                     | Location                                       |
| ------------- | ------------------------------------------- | ---------------------------------------------- |
| **Variables** | Variables, constants, collections, booleans | [→ naming/variables.md](./naming/variables.md) |
| **Functions** | Functions, methods, async patterns          | [→ naming/functions.md](./naming/functions.md) |
| **Types**     | Interfaces, classes, types, enums           | [→ naming/types.md](./naming/types.md)         |
| **Files**     | Files, directories, modules                 | [→ naming/files.md](./naming/files.md)         |
| **Patterns**  | Common patterns and anti-patterns           | [→ naming/patterns.md](./naming/patterns.md)   |

## Quick Reference

### Case Standards Summary

| Case Style         | Usage                         | Example                      | Details                                                                |
| ------------------ | ----------------------------- | ---------------------------- | ---------------------------------------------------------------------- |
| `camelCase`        | Variables, functions, methods | `userName`, `getUserById()`  | [Variables](./naming/variables.md), [Functions](./naming/functions.md) |
| `PascalCase`       | Types, interfaces, classes    | `UserService`, `ApiResponse` | [Types](./naming/types.md)                                             |
| `kebab-case`       | File names, URLs              | `user-service.ts`            | [Files](./naming/files.md)                                             |
| `UPPER_SNAKE_CASE` | Constants, env vars           | `MAX_RETRIES`, `API_KEY`     | [Variables](./naming/variables.md#constant-naming)                     |

### Common Patterns Quick Links

- **Boolean Naming** → [Variables](./naming/variables.md#boolean-variables) & [Patterns](./naming/patterns.md#boolean-naming-patterns)
- **Collection Naming** → [Variables](./naming/variables.md#collection-naming) & [Patterns](./naming/patterns.md#collection-naming-patterns)
- **Async Functions** → [Functions](./naming/functions.md#async-function-patterns)
- **Component Naming** → [Types](./naming/types.md#component-classes) & [Files](./naming/files.md#component-files)
- **Anti-Patterns** → [Patterns](./naming/patterns.md#common-anti-patterns)

## Navigation by Use Case

### "I need to name a..."

- **Variable or constant** → [variables.md](./naming/variables.md)
- **Function or method** → [functions.md](./naming/functions.md)
- **Class or interface** → [types.md](./naming/types.md)
- **File or directory** → [files.md](./naming/files.md)
- **Boolean value** → [variables.md](./naming/variables.md#boolean-variables)
- **React component** → [types.md](./naming/types.md#component-classes) & [files.md](./naming/files.md#component-files)
- **API endpoint** → [patterns.md](./naming/patterns.md#api-and-http)

### "I want to avoid..."

- **Common mistakes** → [patterns.md](./naming/patterns.md#common-anti-patterns)
- **Reserved words** → [patterns.md](./naming/patterns.md#reserved-words-and-conflicts)
- **Bad patterns** → Each file has an "Anti-Patterns" section

## Core Principles (Summary)

### 1. Clarity Over Brevity

```typescript
// ✅ Good
const userAuthenticationToken = generateToken();

// ❌ Bad
const tok = generateToken();
```

### 2. Consistency Throughout

```typescript
// ✅ Good - Same pattern everywhere
(getUserById(), getProductById(), getOrderById());

// ❌ Bad - Mixed patterns
(getUserById(), fetchProduct(), orderDetails());
```

### 3. Domain Vocabulary

```typescript
// ✅ Good - Matches business domain
const shoppingCart = new ShoppingCart();
const patientRecord = new PatientRecord();
```

### 4. Self-Documenting

```typescript
// ✅ Good - Purpose is clear
function validateEmailFormat(email: string): boolean;

// ❌ Bad - Unclear purpose
function check(str: string): boolean;
```

## Migration Guide

If you're looking for specific content from the old monolithic naming.md file:

- **Case Standards** → Now in each relevant file's introduction
- **Variable Naming** → [variables.md](./naming/variables.md)
- **Function Naming** → [functions.md](./naming/functions.md)
- **Boolean Naming** → [variables.md](./naming/variables.md#boolean-variables)
- **Class and Type Naming** → [types.md](./naming/types.md)
- **File and Directory Naming** → [files.md](./naming/files.md)
- **Acronym Handling** → [patterns.md](./naming/patterns.md#acronym-handling)
- **Anti-Patterns** → [patterns.md](./naming/patterns.md#common-anti-patterns)
- **Singular vs Plural** → [patterns.md](./naming/patterns.md#collection-naming-patterns)

## Quick Decision Tree

1. **What am I naming?**
   - Variable/Constant → [variables.md](./naming/variables.md)
   - Function/Method → [functions.md](./naming/functions.md)
   - Type/Class/Interface → [types.md](./naming/types.md)
   - File/Directory → [files.md](./naming/files.md)

2. **What case should I use?**
   - See Case Standards Summary above

3. **Is there a pattern I should follow?**
   - Check [patterns.md](./naming/patterns.md)

4. **What should I avoid?**
   - See Anti-Patterns in each file

## See Also

- [TypeScript Standards](./typescript.md) - Language-specific conventions
- [General Principles](./general-principles.md) - Overall coding standards
- [Folder Structure](./folder-structure.md) - Project organization

---

**Note**: This file now serves as a navigation guide. All detailed naming conventions have been moved to the specialized files in the [naming/](./naming/) directory for better organization and easier reference.
