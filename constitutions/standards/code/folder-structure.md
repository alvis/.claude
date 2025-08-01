# Folder Structure Standards

_Standards for organizing code files, directories, and maintaining a scalable project structure_

## Core Principles

### Organization Goals

- **Discoverability** - Easy to find related code
- **Scalability** - Structure that grows with the project
- **Modularity** - Clear separation of concerns
- **Consistency** - Predictable file locations
- **Colocation** - Keep related files together

## Domain-Based Structure

### Organize by Feature/Domain

Group related functionality together rather than by file type:

```plaintext
✅ Good: Domain-based structure
src/
├── user/
│   ├── UserService.ts
│   ├── UserRepository.ts
│   ├── UserController.ts
│   ├── UserValidation.ts
│   ├── UserTypes.ts
│   └── __tests__/
│       ├── UserService.spec.ts
│       └── UserController.spec.ts
├── product/
│   ├── ProductService.ts
│   ├── ProductRepository.ts
│   ├── ProductController.ts
│   └── ProductTypes.ts
└── order/
    ├── OrderService.ts
    ├── OrderRepository.ts
    └── OrderTypes.ts

❌ Bad: Type-based structure
src/
├── services/
│   ├── UserService.ts
│   ├── ProductService.ts
│   └── OrderService.ts
├── repositories/
│   ├── UserRepository.ts
│   ├── ProductRepository.ts
│   └── OrderRepository.ts
├── controllers/
│   ├── UserController.ts
│   ├── ProductController.ts
│   └── OrderController.ts
```

### Benefits of Domain Grouping

1. **All related code in one place** - Easy to understand a feature
2. **Reduced coupling** - Clear boundaries between domains
3. **Easy refactoring** - Move or extract entire features
4. **Team scalability** - Teams can own domains

## Component Structure

### React Component Organization

```plaintext
✅ Good: Component with all related files
components/
└── UserProfile/
    ├── UserProfile.tsx          # Component implementation
    ├── UserProfile.spec.tsx     # Tests
    ├── UserProfile.stories.tsx  # Storybook stories
    ├── UserProfile.module.css   # Styles (if using CSS modules)
    └── index.ts                 # Public export

✅ Good: Complex component with sub-components
components/
└── DataTable/
    ├── DataTable.tsx           # Main component
    ├── DataTableHeader.tsx     # Sub-component
    ├── DataTableRow.tsx        # Sub-component
    ├── DataTablePagination.tsx # Sub-component
    ├── DataTable.spec.tsx      # Tests
    ├── DataTable.stories.tsx   # Stories
    ├── hooks/
    │   └── useDataTable.ts     # Component-specific hook
    ├── utils/
    │   └── sortHelpers.ts      # Component-specific utils
    └── index.ts                # Public exports
```

### Component Export Pattern

```typescript
// components/Button/index.ts
export { Button } from "./Button";
export type { ButtonProps } from "./Button";

// Usage remains clean
import { Button, ButtonProps } from "#components/Button";
```

## Project Root Structure

### Standard Directories

```plaintext
project-root/
├── src/                    # Source code
│   ├── app/               # Next.js app directory
│   ├── components/        # Shared UI components
│   ├── features/          # Feature modules
│   ├── hooks/             # Shared React hooks
│   ├── lib/               # Core libraries and utilities
│   ├── services/          # External service integrations
│   ├── types/             # Shared TypeScript types
│   └── utils/             # Utility functions
├── public/                # Static assets
├── tests/                 # Integration/E2E tests
├── scripts/               # Build and utility scripts
├── docs/                  # Documentation
└── config/                # Configuration files
```

### Directory Descriptions

#### src/features/

Domain-specific modules containing all related code:

```plaintext
features/
├── auth/
│   ├── components/        # Feature-specific components
│   ├── hooks/            # Feature-specific hooks
│   ├── services/         # Feature business logic
│   ├── stores/           # Feature state management
│   ├── types/            # Feature types
│   └── utils/            # Feature utilities
└── dashboard/
    ├── components/
    ├── hooks/
    └── services/
```

#### src/lib/

Core functionality and integrations:

```plaintext
lib/
├── api/                  # API client configuration
├── auth/                 # Authentication utilities
├── database/             # Database connections
├── email/                # Email service
└── storage/              # File storage utilities
```

#### src/services/

External service integrations:

```plaintext
services/
├── stripe/               # Payment processing
├── sendgrid/             # Email service
├── analytics/            # Analytics tracking
└── monitoring/           # Error tracking
```

## File Naming Conventions

### Consistency Rules

```plaintext
✅ Good: Consistent naming
user/
├── user.service.ts       # Service class
├── user.repository.ts    # Repository class
├── user.controller.ts    # Controller class
├── user.validation.ts    # Validation schemas
├── user.types.ts         # Type definitions
└── user.utils.ts         # Utility functions

❌ Bad: Inconsistent naming
user/
├── UserService.ts        # Mixed casing
├── user-repo.ts          # Abbreviated
├── userCtrl.ts           # Abbreviated differently
├── validation.ts         # Missing prefix
└── types.ts              # Missing prefix
```

### Index Files

Use index files sparingly for public APIs:

```typescript
// ✅ Good: Clean public API
// user/index.ts
export { UserService } from "./user.service";
export { UserRepository } from "./user.repository";
export type { User, CreateUserData } from "./user.types";

// ❌ Bad: Exposing internals
// user/index.ts
export * from "./user.service";
export * from "./user.repository";
export * from "./user.validation";
export * from "./user.utils";
```

## Special Directories

### Test Files

```plaintext
✅ Good: Colocated tests
feature/
├── user.service.ts
├── user.service.spec.ts    # Unit test
└── __tests__/
    └── user.integration.spec.ts  # Integration test

✅ Good: Separate test directory for E2E
tests/
└── e2e/
    ├── auth.e2e.spec.ts
    └── checkout.e2e.spec.ts
```

### Generated Files

```plaintext
generated/
├── graphql/               # GraphQL types
├── prisma/                # Prisma client
└── api/                   # OpenAPI clients

# Always gitignore generated files
# Regenerate in CI/CD pipeline
```

### Configuration Files

```plaintext
config/
├── jest/                  # Jest configuration
├── webpack/               # Webpack configs
└── docker/                # Docker configs

# Or at root for standard configs
.eslintrc.js
.prettierrc
jest.config.js
```

## Import Organization

### Import Order

1. External dependencies
2. Internal aliases
3. Relative imports
4. Type imports

```typescript
// ✅ Good: Organized imports
// External
import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { z } from "zod";

// Internal aliases
import { Button } from "#components/Button";
import { useAuth } from "#hooks/useAuth";
import { api } from "#lib/api";

// Relative imports
import { UserProfile } from "./UserProfile";
import { formatUserName } from "./utils";

// Type imports
import type { User } from "#types/user";
import type { UserProfileProps } from "./UserProfile";
```

## Scaling Patterns

### Feature Modules

As features grow, maintain structure:

```plaintext
features/
└── blog/
    ├── api/              # Feature API routes
    ├── components/       # Feature components
    ├── pages/           # Feature pages
    ├── hooks/           # Feature hooks
    ├── services/        # Feature services
    ├── stores/          # Feature state
    ├── types/           # Feature types
    ├── utils/           # Feature utilities
    └── index.ts         # Feature exports
```

### Shared Code

Extract truly shared code to common locations:

```plaintext
src/
├── components/          # Shared across features
│   ├── Button/
│   ├── Modal/
│   └── DataTable/
├── hooks/              # Shared hooks
│   ├── useDebounce.ts
│   └── useLocalStorage.ts
└── utils/              # Shared utilities
    ├── formatters.ts
    └── validators.ts
```

## Anti-Patterns to Avoid

### Common Mistakes

```plaintext
❌ Bad: Deeply nested structures
src/
└── components/
    └── common/
        └── ui/
            └── buttons/
                └── primary/
                    └── Button.tsx  # Too deep!

❌ Bad: Duplicate code organization
src/
├── components/Button.tsx
├── shared/components/Button.tsx
└── common/Button.tsx  # Which one to use?

❌ Bad: Mixed concerns
components/
└── UserProfile/
    ├── UserProfile.tsx
    ├── api.ts           # API calls don't belong here
    ├── database.ts      # Database logic doesn't belong here
    └── email.ts         # Email logic doesn't belong here
```

### Circular Dependencies

Avoid circular dependencies through proper structure:

```typescript
// ❌ Bad: Circular dependency
// user/user.service.ts
import { OrderService } from "../order/order.service";

// order/order.service.ts
import { UserService } from "../user/user.service";

// ✅ Good: Use dependency injection or events
// user/user.service.ts
export class UserService {
  constructor(private eventBus: EventBus) {}

  async createUser(data: CreateUserData) {
    const user = await this.repository.create(data);
    this.eventBus.emit("user.created", user);
    return user;
  }
}
```

## Migration Strategy

### Gradual Migration

When refactoring to domain-based structure:

1. **Start with new features** - Implement new features with proper structure
2. **Refactor during changes** - When modifying existing code, restructure it
3. **Create migration plan** - Document which modules to migrate and when
4. **Maintain consistency** - Don't mix patterns within the same domain

```plaintext
# Migration tracking
src/
├── features/          # New structure
│   └── user/         # Migrated ✓
└── legacy/           # Old structure
    ├── services/     # To be migrated
    └── controllers/  # To be migrated
```

## Best Practices

### Guidelines

1. **Prefer flat over nested** - Avoid directories more than 3-4 levels deep
2. **Colocate related code** - Keep files that change together in the same directory
3. **Clear naming** - Directory and file names should clearly indicate contents
4. **Consistent patterns** - Use the same structure across all features
5. **Document decisions** - Add README files to explain non-obvious structures

### Example Feature README

```markdown
# User Feature

This module handles all user-related functionality.

## Structure

- `components/` - User-specific React components
- `services/` - Business logic for user operations
- `types/` - TypeScript interfaces and types

## Key Files

- `user.service.ts` - Main service for user operations
- `user.repository.ts` - Database access layer
- `user.validation.ts` - Input validation schemas

## Dependencies

- Auth feature (for authentication)
- Email service (for notifications)
```
