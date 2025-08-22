# Service & Backend Coding Standards

_Specific standards for backend services, APIs, and server-side development_

## Table of Contents

- [Service Architecture](#service_architecture) `service_architecture`
- [API Design Patterns](#api_design_patterns) `api_design_patterns` - **workflow:** `build-service`
- [Data Operation Patterns](#data_operations) `data_operations`
- [Error Handling](#error_handling) `error_handling`
- [Authentication & Authorization](#authentication_patterns) `authentication_patterns`
- [Database Integration](#database_patterns) `database_patterns`
- [Service Testing](#testing_services) `testing_services`
- [Performance & Monitoring](#performance_monitoring) `performance_monitoring`

<service_architecture>

## 🏗️ Service Architecture

### Domain Alignment

Services, data, and manifests align by domain:

```plaintext
services/profile/
data/profile/
manifests/profile/
infrastructure/profile/
```

### Service Structure

```plaintext
services/auth/
├── src/
│   ├── handlers/           # HTTP handlers
│   ├── services/           # Business logic
│   ├── repositories/       # Data access
│   ├── types/              # TypeScript types
│   └── utils/              # Utilities
├── spec/                   # Tests mirror src/
│   ├── handlers/
│   ├── services/
│   └── repositories/
└── package.json
```

### Layered Architecture

- **Handlers** - HTTP/transport layer
- **Services** - Business logic
- **Repositories** - Data access
- **Types** - Shared interfaces
- **Utils** - Pure utilities

</service_architecture>

<api_design_patterns>

## 🔌 API Design Patterns

<workflow name="build-service">

### RESTful Conventions

```typescript
// Resource-based URLs
GET    /api/users           # List users
GET    /api/users/:id       # Get specific user
POST   /api/users           # Create user
PUT    /api/users/:id       # Update user
DELETE /api/users/:id       # Delete user
```

### Request/Response Patterns

```typescript
// Standard API response
interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  meta?: {
    pagination?: PaginationMeta;
    timestamp: string;
  };
}

// Pagination metadata
interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
}
```

### Handler Pattern

```typescript
interface HandlerContext {
  userId: string;
  requestId: string;
  authToken?: string;
}

interface HandlerOptions {
  timeout?: number;
  retries?: number;
}

export async function getUserHandler(
  params: { userId: string },
  context: HandlerContext,
  options: HandlerOptions = {},
): Promise<ApiResponse<User>> {
  try {
    const user = await userService.getUser(params.userId);

    return {
      status: "success",
      data: user,
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  } catch (error) {
    return {
      status: "error",
      error: {
        code: "USER_NOT_FOUND",
        message: "User not found",
        details: error,
      },
    };
  }
}
```

</workflow>

</api_design_patterns>

<data_operations>

## 💾 Data Operation Patterns

### Operation Naming

- `Search<Entity>` - NLP-enhanced search queries
- `List<Entity>` - Filter-only structured queries
- `Get<Entity>` - Single entity retrieval
- `Set<Entity>` - Create/update (upsert)
- `Drop<Entity>` - Delete operations

### Query Structure

```typescript
interface QueryOptions {
  /** natural language search query */
  query?: string; // available for Search<Entity> operations only

  /** rule-based structured filters */
  filter?: Record<string, unknown>;

  /** cursor marker for the next result set */
  cursor?: string;

  /** number of items to skip (offset pagination) */
  offset?: number;

  /** max number of records to return */
  limit?: number;

  /** sorting criteria */
  sort?: Array<{
    field: string;
    order: "asc" | "desc";
  }>;
}
```

### Repository Pattern

```typescript
interface UserRepository {
  searchUsers(options: QueryOptions): Promise<User[]>;
  listUsers(filter: UserFilter): Promise<User[]>;
  getUser(id: string): Promise<User | null>;
  setUser(user: User): Promise<User>;
  dropUser(id: string): Promise<void>;
}

class DatabaseUserRepository implements UserRepository {
  async getUser(id: string): Promise<User | null> {
    const result = await this.db.query("SELECT * FROM users WHERE id = $1", [
      id,
    ]);

    return result.rows[0] || null;
  }

  async setUser(user: User): Promise<User> {
    if (user.id) {
      // Update existing
      return this.updateUser(user);
    } else {
      // Create new
      return this.createUser(user);
    }
  }
}
```

</data_operations>

<error_handling>

## 🚨 Error Handling Patterns

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

class AuthenticationError extends Error {
  constructor(message: string = "Authentication required") {
    super(message);
    this.name = "AuthenticationError";
  }
}
```

### Error Transformation

```typescript
// Handler error transformation
export function transformError(error: unknown): ApiError {
  if (error instanceof ValidationError) {
    return {
      code: "VALIDATION_ERROR",
      message: error.message,
      statusCode: 400,
      details: { field: error.field },
    };
  }

  if (error instanceof NotFoundError) {
    return {
      code: "NOT_FOUND",
      message: error.message,
      statusCode: 404,
    };
  }

  // Default to internal server error
  return {
    code: "INTERNAL_ERROR",
    message: "An unexpected error occurred",
    statusCode: 500,
  };
}
```

### Logging Strategy

```typescript
// Structured logging
interface LogContext {
  requestId: string;
  userId?: string;
  operation: string;
  duration?: number;
}

function logError(error: Error, context: LogContext): void {
  logger.error({
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
  });
}

function logOperation(context: LogContext): void {
  logger.info({
    message: `Operation ${context.operation} completed`,
    context,
    timestamp: new Date().toISOString(),
  });
}
```

</error_handling>

<authentication_patterns>

## 🔐 Authentication & Authorization

### JWT Token Handling

```typescript
interface JWTPayload {
  userId: string;
  email: string;
  roles: string[];
  exp: number;
  iat: number;
}

async function verifyToken(token: string): Promise<JWTPayload> {
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET) as JWTPayload;

    // Check expiration
    if (Date.now() >= payload.exp * 1000) {
      throw new AuthenticationError("Token expired");
    }

    return payload;
  } catch (error) {
    throw new AuthenticationError("Invalid token");
  }
}
```

### Authorization Middleware

```typescript
interface AuthContext {
  user: JWTPayload;
  roles: string[];
}

function requireRole(requiredRole: string) {
  return (context: AuthContext) => {
    if (!context.roles.includes(requiredRole)) {
      throw new AuthorizationError(`Role ${requiredRole} required`);
    }
  };
}

function requirePermission(permission: string) {
  return (context: AuthContext) => {
    const userPermissions = getUserPermissions(context.user.userId);
    if (!userPermissions.includes(permission)) {
      throw new AuthorizationError(`Permission ${permission} required`);
    }
  };
}
```

</authentication_patterns>

<database_patterns>

## 🗄️ Database Integration

### Connection Management

```typescript
interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  ssl?: boolean;
  pool?: {
    min: number;
    max: number;
    idleTimeoutMillis: number;
  };
}

class DatabaseService {
  private pool: Pool;

  constructor(config: DatabaseConfig) {
    this.pool = new Pool({
      ...config,
      ssl: config.ssl ? { rejectUnauthorized: false } : false,
    });
  }

  async query<T>(sql: string, params: unknown[] = []): Promise<QueryResult<T>> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(sql, params);
      return result;
    } finally {
      client.release();
    }
  }
}
```

### Transaction Management

```typescript
async function executeTransaction<T>(
  operations: (client: PoolClient) => Promise<T>,
): Promise<T> {
  const client = await pool.connect();

  try {
    await client.query("BEGIN");
    const result = await operations(client);
    await client.query("COMMIT");
    return result;
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}
```

</database_patterns>

<testing_services>

## 🧪 Service Testing

### Integration Test Setup

```typescript
describe("op:getUserProfile", () => {
  let testDb: TestDatabase;
  let userService: UserService;

  beforeEach(async () => {
    testDb = await createTestDatabase();
    userService = new UserService(testDb);
  });

  afterEach(async () => {
    await testDb.cleanup();
  });

  it("should return user profile for valid id", async () => {
    const testUser = await testDb.createUser({
      name: "John Doe",
      email: "john@example.com",
    });
    const expected = { id: testUser.id, name: "John Doe" };

    const result = await userService.getUserProfile(testUser.id);

    expect(result).toMatchObject(expected);
  });
});
```

### Mock External Dependencies

```typescript
// Mock external HTTP calls
const mockAxios = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}));

vi.mock("axios", () => ({
  default: mockAxios,
}));

// Mock database operations
const mockRepository = vi.hoisted(() => ({
  getUser: vi.fn(),
  setUser: vi.fn(),
}));

vi.mock("#repositories/userRepository", () => ({
  userRepository: mockRepository,
}));
```

</testing_services>

<performance_monitoring>

## 📊 Performance & Monitoring

### Request Metrics

```typescript
interface RequestMetrics {
  requestId: string;
  method: string;
  path: string;
  statusCode: number;
  duration: number;
  timestamp: string;
  userId?: string;
}

function trackRequestMetrics(
  req: Request,
  res: Response,
  duration: number,
): void {
  const metrics: RequestMetrics = {
    requestId: req.headers["x-request-id"] as string,
    method: req.method,
    path: req.path,
    statusCode: res.statusCode,
    duration,
    timestamp: new Date().toISOString(),
    userId: req.user?.id,
  };

  // Send to monitoring service
  metricsService.track("http_request", metrics);
}
```

### Health Checks

```typescript
interface HealthStatus {
  status: "healthy" | "unhealthy" | "degraded";
  checks: {
    database: boolean;
    cache: boolean;
    externalApi: boolean;
  };
  timestamp: string;
}

export async function healthCheck(): Promise<HealthStatus> {
  const checks = await Promise.allSettled([
    checkDatabase(),
    checkCache(),
    checkExternalApi(),
  ]);

  const [database, cache, externalApi] = checks.map(
    (result) => result.status === "fulfilled" && result.value,
  );

  const allHealthy = database && cache && externalApi;
  const anyHealthy = database || cache || externalApi;

  return {
    status: allHealthy ? "healthy" : anyHealthy ? "degraded" : "unhealthy",
    checks: { database, cache, externalApi },
    timestamp: new Date().toISOString(),
  };
}
```

</performance_monitoring>
