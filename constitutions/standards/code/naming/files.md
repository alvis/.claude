# File and Directory Naming Standards

_Standards for naming files, directories, modules, and environment configurations_

## Core File Naming Principles

### MUST Follow Rules

- **MUST use kebab-case** for regular TypeScript/JavaScript files
- **MUST use PascalCase** for React component files only
- **MUST match export type** - Noun for objects/classes, verb for functions
- **MUST include file extensions** in imports when required
- **MUST use descriptive names** that indicate file purpose

### SHOULD Follow Guidelines

- **SHOULD group by feature** rather than file type
- **SHOULD keep names concise** but meaningful
- **SHOULD use consistent suffixes** (.service, .repository, .types)
- **SHOULD follow framework conventions** (React, Angular, etc.)

## File Naming Patterns

### TypeScript/JavaScript Files

```typescript
// ✅ Good: Clear, kebab-case naming
user - service.ts; // Service class file
email - validator.ts; // Validation utilities
api - client.ts; // API client implementation
order - repository.ts; // Data access layer
payment - processor.ts; // Business logic

// ✅ Good: Test file naming
user - service.test.ts; // Unit tests
user - service.spec.ts; // Alternative test suffix
email - validator.test.ts; // Matches source file name

// ❌ Bad: Poor file naming
userservice.ts; // No word separation
user_service.ts; // Wrong case style (snake_case)
UserService.ts; // PascalCase for non-components
utils.ts; // Too generic
helpers.ts; // Too vague
```

### Component Files (React/Vue/Angular)

```typescript
// ✅ Good: Component file naming
// React components
Button.tsx                  // Simple component
UserProfile.tsx             // Compound component name
NavigationBar.tsx           // Clear component purpose
ShoppingCartItem.tsx        // Specific component

// Component with associated files
UserProfile/
├── UserProfile.tsx         // Main component
├── UserProfile.test.tsx    // Component tests
├── UserProfile.stories.tsx // Storybook stories
└── UserProfile.module.css  // Component styles

// ❌ Bad: Component naming
button.tsx                  // Should be PascalCase
user-profile.tsx            // Components use PascalCase
UserProfileComponent.tsx    // Redundant 'Component' suffix
```

### Index Files

```typescript
// ✅ Good: Index file usage
// src/services/index.ts
export { UserService } from "./user-service";
export { AuthService } from "./auth-service";
export { EmailService } from "./email-service";

// src/components/Button/index.tsx
export { Button } from "./Button";
export type { ButtonProps } from "./Button.types";

// ❌ Bad: Avoid complex logic in index files
// index.ts
class ComplexService {
  // Don't define classes in index
  // Implementation
}
```

## Export-Based Naming

### Match File Name to Export Type

```typescript
// ✅ Good: Noun for classes/objects
// user-validator.ts - exports a class or object
export class UserValidator {
  validate(user: User): ValidationResult {
    // Implementation
  }
}

// OR
export const userValidator = {
  validate(user: User): ValidationResult {
    // Implementation
  },
};

// ✅ Good: Verb for functions
// validate-user.ts - exports a function
export function validateUser(user: User): ValidationResult {
  // Implementation
}

// More examples:
// parser.ts → exports class Parser or parser object
// parse.ts → exports function parse()
// emitter.ts → exports class Emitter or emitter object
// emit.ts → exports function emit()
// transformer.ts → exports class Transformer or transformer object
// transform.ts → exports function transform()
```

### Multiple Exports

```typescript
// ✅ Good: When file has multiple exports
// user-utils.ts - multiple related functions
export function validateUser(user: User): boolean {}
export function sanitizeUser(user: User): User {}
export function compareUsers(a: User, b: User): boolean {}

// user-types.ts - multiple type definitions
export interface User {}
export interface UserProfile {}
export type UserRole = "admin" | "user";

// ❌ Bad: Unrelated exports in same file
// utils.ts
export function validateUser() {}
export function formatCurrency() {} // Unrelated to users
export function parseDate() {} // Different domain
```

## Directory Structure

### Feature-Based Organization

```typescript
// ✅ Good: Organized by feature/domain
src/
├── user/
│   ├── user.service.ts
│   ├── user.repository.ts
│   ├── user.controller.ts
│   ├── user.types.ts
│   └── user.test.ts
├── order/
│   ├── order.service.ts
│   ├── order.repository.ts
│   ├── order.controller.ts
│   └── order.types.ts
├── payment/
│   ├── payment.service.ts
│   ├── payment.processor.ts
│   └── payment.types.ts
└── shared/
    ├── types/
    ├── utils/
    └── constants/
```

### Layer-Based Organization

```typescript
// ✅ Alternative: Organized by layer
src/
├── controllers/
│   ├── user.controller.ts
│   └── order.controller.ts
├── services/
│   ├── user.service.ts
│   └── order.service.ts
├── repositories/
│   ├── user.repository.ts
│   └── order.repository.ts
├── models/
│   ├── user.model.ts
│   └── order.model.ts
└── types/
    ├── user.types.ts
    └── order.types.ts
```

### Test File Organization

```typescript
// ✅ Good: Co-located tests
src/
├── user/
│   ├── user.service.ts
│   ├── user.service.test.ts    // Co-located with source
│   └── user.repository.ts
│   └── user.repository.test.ts

// ✅ Alternative: Separate test directory
src/
├── user/
│   ├── user.service.ts
│   └── user.repository.ts
└── __tests__/
    └── user/
        ├── user.service.test.ts
        └── user.repository.test.ts
```

## Module and Package Naming

### NPM Package Names

```typescript
// ✅ Good: NPM package naming
@company/ui-components      // Scoped package
@company/auth-sdk          // Clear purpose
react-payment-form         // Framework-specific
express-rate-limiter       // Purpose-clear

// Package.json
{
  "name": "@company/user-service",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts"
}

// ❌ Bad: Poor package naming
utils                      // Too generic
my-package                 // Not descriptive
MyPackage                  // Should be kebab-case
```

### Internal Module Names

```typescript
// ✅ Good: Internal module organization
// src/modules/authentication/index.ts
export * from "./auth.service";
export * from "./auth.guard";
export * from "./auth.types";

// src/modules/user-management/index.ts
export * from "./user.service";
export * from "./user.repository";
export * from "./user.types";
```

## Environment and Configuration Files

### Environment Files

```bash
# ✅ Good: Environment file naming
.env.local                 # Local development
.env.development          # Development environment
.env.staging              # Staging environment
.env.production           # Production environment
.env.test                 # Test environment

# Service-specific (when needed)
.env.database.local       # Database-specific config
.env.redis.production     # Redis-specific config

# ❌ Bad: Environment file naming
.env                      # No environment specified
env.local                 # Missing dot prefix
.local.env                # Wrong order
```

### Configuration Files

```typescript
// ✅ Good: Config file naming
config/
├── database.config.ts    // Database configuration
├── auth.config.ts        // Authentication config
├── app.config.ts         // Application config
├── redis.config.ts       // Redis config
└── index.ts              // Main config export

// ✅ Good: Environment-specific configs
config/
├── development.config.ts
├── staging.config.ts
├── production.config.ts
└── test.config.ts

// ❌ Bad: Config file naming
config.ts                 // Too generic
configuration.ts          // Unnecessarily long
settings.ts              // Ambiguous
```

### Environment Variable Naming

```typescript
// ✅ Good: Environment variable names in .env files
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://localhost:5432/mydb
JWT_SECRET=your-secret-key
AWS_ACCESS_KEY_ID=AKIA...
STRIPE_API_KEY=sk_live_...
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=info

// ✅ Good: Prefixed for clarity
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=dbuser
DB_PASSWORD=dbpass

API_BASE_URL=https://api.example.com
API_TIMEOUT=30000
API_RETRY_ATTEMPTS=3

// ❌ Bad: Environment variable naming
databaseUrl=...           // Should be UPPER_SNAKE_CASE
jwt_secret=...           // Should be all uppercase
JWTSECRET=...            // Missing underscore separator
URL=...                  // Too generic
```

## Special Files

### Documentation Files

```markdown
# ✅ Good: Documentation file naming

README.md # Project readme
CONTRIBUTING.md # Contribution guidelines
CHANGELOG.md # Version history
LICENSE.md # License file
SECURITY.md # Security policy

docs/
├── getting-started.md
├── api-reference.md
├── deployment.md
└── troubleshooting.md
```

### Build and Config Files

```typescript
// ✅ Good: Build/config file naming
tsconfig.json.eslintrc.js.prettierrc; // TypeScript config // ESLint config // Prettier config
jest.config.js; // Jest config
webpack.config.js; // Webpack config
rollup.config.js; // Rollup config
vite.config.ts; // Vite config

// Docker files
Dockerfile; // Main Docker file
docker - compose.yml; // Docker Compose
Dockerfile.dev; // Development Docker file
```

## Import Path Organization

```typescript
// ✅ Good: Import organization
// 1. Node modules
import express from "express";
import { readFile } from "fs/promises";

// 2. External packages
import axios from "axios";
import { z } from "zod";

// 3. Internal aliases
import { UserService } from "@/services/user-service";
import { logger } from "@/utils/logger";

// 4. Relative imports
import { validateUser } from "./validate-user";
import type { User } from "./user.types";

// ❌ Bad: Mixed import order
import { validateUser } from "./validate-user";
import express from "express";
import { UserService } from "@/services/user-service";
import axios from "axios";
```

## Anti-Patterns to Avoid

```typescript
// ❌ Bad: Common file naming mistakes
index.js                  // Too many index files
utils.ts                  // Too generic
helpers.ts                // Too vague
misc.ts                   // Unclear purpose
stuff.ts                  // Meaningless
data.ts                   // What kind of data?
functions.ts              // What functions?
UserServiceImpl.ts        // Implementation suffix unnecessary
IUserService.ts           // Interface prefix unnecessary

// ❌ Bad: Inconsistent naming
user-service.ts           // In one place
userRepository.ts         // Different style elsewhere
User_Controller.ts        // Yet another style

// ❌ Bad: Deep nesting
src/
└── features/
    └── user/
        └── management/
            └── services/
                └── implementation/
                    └── user-service.ts  // Too deep!
```

## References

- [Variable Naming](./variables.md) - Variable naming conventions
- [Type Naming](./types.md) - Type and interface naming
- [Folder Structure](../folder-structure.md) - Project organization
