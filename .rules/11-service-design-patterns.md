# API Design Patterns

## Service Architecture

### Service Organization

Based on the codebase structure:

```plaintext
services/       # Backend services
manifests/      # Service operation specs
data/           # Data controllers
```

Each service should:

- Have a corresponding manifest defining operations
- Use a matching data controller for database operations
- Follow domain-driven design principles

### Operation Naming

Follow the established patterns for data operations:

- `get<Entity>` - Retrieve single entity
- `list<Entities>` - Retrieve multiple entities
- `set<Entity>` - Create or update entity
- `drop<Entity>` - Delete entity
- `search<Entities>` - Search with filters

```typescript
// ✅ good: consistent operation naming
export interface ProfileOperations {
  getUser: (id: string) => Promise<User>;
  listUsers: (filter?: UserFilter) => Promise<User[]>;
  setUser: (user: User) => Promise<User>;
  dropUser: (id: string) => Promise<void>;
  searchUsers: (query: string) => Promise<User[]>;
}

// ❌ bad: inconsistent naming
export interface ProfileOperations {
  fetchUser: (id: string) => Promise<User>;
  getAllUsers: () => Promise<User[]>;
  createOrUpdateUser: (user: User) => Promise<User>;
  deleteUser: (id: string) => Promise<void>;
}
```

## Request/Response Structure

### Response Format

Maintain consistent response structures:

```typescript
// success response
interface SuccessResponse<T> {
  data: T;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
}

// error response (using @theriety/error)
interface ErrorResponse {
  error: {
    type: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

// list response with pagination
interface ListResponse<T> {
  data: T[];
  meta: {
    page: number;
    limit: number;
    total: number;
    hasNext: boolean;
  };
}
```

## Data Transfer Patterns

### DTOs (Data Transfer Objects)

Separate internal models from API contracts:

```typescript
// internal domain model
interface UserDomain {
  id: string;
  email: string;
  passwordHash: string;
  createdAt: Date;
  updatedAt: Date;
}

// api dto (exclude sensitive fields)
interface UserDTO {
  id: string;
  email: string;
  createdAt: string; // iso string for json
  updatedAt: string;
}

// transform function
function toUserDTO(user: UserDomain): UserDTO {
  return {
    id: user.id,
    email: user.email,
    createdAt: user.createdAt.toISOString(),
    updatedAt: user.updatedAt.toISOString(),
  };
}
```

### Pagination

Implement consistent pagination:

```typescript
interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// default pagination
const DEFAULT_PAGE = 1;
const DEFAULT_LIMIT = 20;
const MAX_LIMIT = 100;

function normalizePagination(params: PaginationParams) {
  return {
    page: Math.max(1, params.page || DEFAULT_PAGE),
    limit: Math.min(params.limit || DEFAULT_LIMIT, MAX_LIMIT),
    sortBy: params.sortBy || 'createdAt',
    sortOrder: params.sortOrder || 'desc',
  };
}
```

## Service Architecture Patterns

### Service File Structure

Each service follows a standardized 4-file structure:

```plaintext
services/<domain>/
├── factory.ts       # Creates service operations using createServiceFactory
├── client.ts        # Initializes data clients and external services (e.g., Supabase)
├── config.ts        # Defines service configuration schema using JSON Schema
└── peer.ts          # Imports manifest dependencies from other services
```

### Data Controller Integration

Each service integrates with a corresponding data controller:

```plaintext
data/<domain>/
├── source/
│   ├── index.ts           # Exports domain class (e.g., IAM, Billing)
│   ├── operations/        # Individual operation implementations
│   └── types/             # Domain-specific types
├── prisma/
│   ├── client.ts          # Prisma client initialization
│   ├── reset.ts           # Database reset utilities
│   ├── schema/            # Split schema files by entity
│   │   ├── schema.prisma  # Main schema importing others
│   │   └── <entity>.prisma # Individual entity schemas
│   └── seed.ts            # Seed data
```

- Constructor accepts `PostgresConfig`
- Methods follow naming convention: `getX`, `setX`, `listX`, `dropX`, `attachX`, `detachX`
- Private `#client` field holds the Prisma client instance

### Manifest Operation Structure

Operations are organized with consistent patterns:

```plaintext
manifests/<domain>/
├── operations/
│   └── <operationName>/
│       └── index.ts       # Uses createOperationManifest
├── schemas/
│   ├── index.ts           # Main schema exports
│   └── input.ts           # Input schema definitions
└── source/
    └── index.ts           # Exports operation types using FromSchema
```

### Service Operation Implementation

Operations follow consistent creation and implementation patterns:

```typescript
// Create operations using established factories
const operation = createOperation.getUserProfile({
  input: userInputSchema,
  async handler({ userId }, { data }) {
    // Use destructured data containing initialized clients
    const user = await data.prisma.user.findUnique({
      where: { id: userId }
    });
    
    // Use jsonify to ensure JSON-serializable output
    return jsonify(mapToUserProfile(user));
  }
});
```

### Configuration Schema Pattern

Use consistent configuration patterns with type safety:

```typescript
import type { ServiceConfigSpecification } from '#types/config';

// Use as const satisfies for type safety
export const config = {
  encryption: { /* ... */ },
  data: { /* ... */ },
  extra: { /* ... */ }
} as const satisfies ServiceConfigSpecification;
```

### Extended Operation Naming

Beyond basic data operations, services support relationship management:

- `get<Entity>` - Retrieve single entity
- `set<Entity>` - Create or update entity  
- `list<Entity>` - Retrieve multiple entities
- `drop<Entity>` - Delete entity
- `search<Entity>` - Search with filters
- `attach<Entity><Related>` - Create relationship
- `detach<Entity><Related>` - Remove relationship

```typescript
// ✅ Good: consistent with established patterns
export const operations = {
  getUser,
  setUser, 
  listUsers,
  dropUser,
  attachUserRole,
  detachUserRole
};

// ❌ Bad: inconsistent naming
export const operations = {
  fetchUser,
  createOrUpdateUser,
  getAllUsers,
  deleteUser
};
```

### Type Re-export Pattern

Keep public API surface clean while maintaining type availability:

```typescript
// index.ts - main module exports
export type * from '#operations/getUser';
export type * from '#operations/setUser';
export type * from '#types';

// Clean separation between implementation and public types
export { getUserOperation } from '#operations/getUser';
export { setUserOperation } from '#operations/setUser';
```

--- END ---
