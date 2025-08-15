# Data Operations Standards

_Core standards for data controllers, database operations, and data management_

## Data Operation Naming

### Core Operation Verbs

- `Search<Entity>` - NLP-enhanced search queries with natural language
- `List<Entity>` - Filter-only structured queries (rule-based)
- `Get<Entity>` - Single entity retrieval by identifier
- `Set<Entity>` - Create/update operations (upsert pattern)
- `Drop<Entity>` - Delete operations (discouraged, prefer status updates)

### Naming Rules

- Search operations support natural language queries
- List operations use structured filters only
- Get returns single entity or null
- Set handles both create and update seamlessly
- Drop returns void on success

### Implementation Examples

```typescript
// ✅ Correct naming
async function searchUsers(options: QueryOptions): Promise<User[]>;
async function listUsers(filter: UserFilter): Promise<User[]>;
async function getUser(params: { id: string }): Promise<User | null>;
async function setUser(user: User): Promise<User>;
async function dropUser(params: { id: string }): Promise<void>;

// ❌ Avoid these names
async function fetchUsers(); // Use list or search
async function deleteUser(); // Use drop
async function updateUser(); // Use set
async function createUser(); // Use set
```

## Query Structure

### Standard Query Options

All read-only database queries should use this structure:

```typescript
interface QueryOptions {
  /** natural language search query */
  query?: string; // available for Search<Entity> operations only

  /** rule-based structured filters */
  filter?: Record<string, unknown>;

  /** cursor marker for the next result set, used for cursor-based pagination */
  cursor?: string;

  /** number of items to skip, used for offset-based pagination */
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

### Query Pattern Examples

```typescript
// Search with natural language
await searchCommunities({
  query: "climate tech in Europe",
  limit: 20,
});

// List with structured filters
await listCommunities({
  filter: { country: "UK", active: true },
  limit: 50,
  sort: [{ field: "createdAt", order: "desc" }],
});

// Get single entity
await getProduct({ id: "abc123" });
await getUser({ slug: "john-doe" });
```

## Repository Patterns

### Repository Interface Design

```typescript
interface EntityRepository<T, K = string> {
  // Read operations
  search(options: QueryOptions): Promise<T[]>;
  list(filter: Partial<T>): Promise<T[]>;
  get(identifier: K | { [key: string]: unknown }): Promise<T | null>;

  // Write operations
  set(entity: T): Promise<T>;
  drop(identifier: K): Promise<void>;

  // Batch operations
  setBatch(entities: T[]): Promise<T[]>;
  dropBatch(identifiers: K[]): Promise<void>;
}
```

## Data Controller Patterns

### Controller Structure

```typescript
interface DataController<T> {
  // Query operations
  search(options: QueryOptions): Promise<PaginatedResult<T>>;
  list(
    filter: Partial<T>,
    pagination?: PaginationOptions,
  ): Promise<PaginatedResult<T>>;
  get(id: string): Promise<T | null>;

  // Mutation operations
  create(data: CreateData<T>): Promise<T>;
  update(id: string, data: UpdateData<T>): Promise<T>;
  upsert(data: UpsertData<T>): Promise<T>;
  delete(id: string): Promise<void>;

  // Batch operations
  bulkCreate(data: CreateData<T>[]): Promise<T[]>;
  bulkUpdate(updates: Array<{ id: string; data: UpdateData<T> }>): Promise<T[]>;
  bulkDelete(ids: string[]): Promise<void>;
}

// Result types
interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
  };
}
```

## Transaction Management

### Transaction Patterns

```typescript
interface TransactionContext {
  commit(): Promise<void>;
  rollback(): Promise<void>;
  query<T>(sql: string, params?: unknown[]): Promise<QueryResult<T>>;
}

class TransactionManager {
  async executeTransaction<T>(
    operation: (ctx: TransactionContext) => Promise<T>,
  ): Promise<T> {
    const client = await this.pool.connect();

    try {
      await client.query("BEGIN");

      const context: TransactionContext = {
        query: (sql, params) => client.query(sql, params),
        commit: () => client.query("COMMIT"),
        rollback: () => client.query("ROLLBACK"),
      };

      const result = await operation(context);
      await context.commit();

      return result;
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    } finally {
      client.release();
    }
  }
}
```

## Data Validation Patterns

### Validation Schema

```typescript
interface ValidationSchema<T> {
  validate(data: unknown): T;
  validatePartial(data: unknown): Partial<T>;
  validateArray(data: unknown[]): T[];
}

class UserValidator implements ValidationSchema<User> {
  validate(data: unknown): User {
    if (!this.isObject(data)) {
      throw new ValidationError("Data must be an object");
    }

    return {
      id: this.validateId(data.id),
      name: this.validateName(data.name),
      email: this.validateEmail(data.email),
      createdAt: this.validateDate(data.createdAt),
      updatedAt: this.validateDate(data.updatedAt),
    };
  }

  private validateEmail(value: unknown): string {
    if (typeof value !== "string") {
      throw new ValidationError("Email must be a string", "email");
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      throw new ValidationError("Email must be valid", "email");
    }

    return value.toLowerCase();
  }
}
```

## Caching Strategies

### Cache Patterns

```typescript
interface CacheStrategy<T> {
  get(key: string): Promise<T | null>;
  set(key: string, value: T, ttl?: number): Promise<void>;
  delete(key: string): Promise<void>;
  invalidatePattern(pattern: string): Promise<void>;
}

class LayeredCacheRepository<T> implements EntityRepository<T> {
  constructor(
    private repository: EntityRepository<T>,
    private cache: CacheStrategy<T>,
    private keyBuilder: (id: string) => string,
  ) {}

  async get(identifier: string | object): Promise<T | null> {
    const key = this.buildCacheKey(identifier);

    // Try cache first
    const cached = await this.cache.get(key);
    if (cached) {
      return cached;
    }

    // Fallback to repository
    const entity = await this.repository.get(identifier);
    if (entity) {
      // Cache for future use
      await this.cache.set(key, entity, 300); // 5 minutes TTL
    }

    return entity;
  }

  async set(entity: T): Promise<T> {
    // Update repository
    const result = await this.repository.set(entity);

    // Invalidate cache
    const key = this.buildCacheKey(result);
    await this.cache.delete(key);

    return result;
  }
}
```
