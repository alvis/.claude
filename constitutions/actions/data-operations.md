# Data Operations & Controllers Standards

_Specific standards for data controllers, database operations, and data management_

## Table of Contents

- [Data Operation Naming](#data_operation_naming) `data_operation_naming`
- [Query Structure](#query_structure) `query_structure`
- [Repository Patterns](#repository_patterns) `repository_patterns` - **workflow:** `build-data-controller`
- [Data Controller Patterns](#data_controller_patterns) `data_controller_patterns`
- [Transaction Management](#transaction_management) `transaction_management`
- [Data Validation Patterns](#data_validation) `data_validation`
- [Caching Strategies](#caching_strategies) `caching_strategies`
- [Data Migration Patterns](#data_migration) `data_migration`

<data_operation_naming>

## 🔍 Data Operation Naming

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

</data_operation_naming>

<query_structure>

## 📋 Query Parameter Structure

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

</query_structure>

<repository_patterns>

## 🏛️ Repository Patterns

<workflow name="build-data-controller">

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

</workflow>

// Specific implementation
interface UserRepository extends EntityRepository<User, string> {
  search(options: QueryOptions): Promise<User[]>;
  list(filter: UserFilter): Promise<User[]>;
  get(params: { id: string } | { email: string }): Promise<User | null>;
  set(user: User): Promise<User>;
  drop(id: string): Promise<void>;
}
```

### Repository Implementation

```typescript
class DatabaseUserRepository implements UserRepository {
  constructor(private db: DatabaseService) {}

  async search(options: QueryOptions): Promise<User[]> {
    const { query, filter, limit = 50, offset = 0, sort } = options;

    // Build search query with natural language processing
    const searchQuery = this.buildSearchQuery(query, filter);
    const sortClause = this.buildSortClause(sort);

    const sql = `
      SELECT * FROM users 
      WHERE ${searchQuery}
      ${sortClause}
      LIMIT $1 OFFSET $2
    `;

    const result = await this.db.query(sql, [limit, offset]);
    return result.rows.map(this.mapToUser);
  }

  async list(filter: UserFilter): Promise<User[]> {
    const { where, params } = this.buildWhereClause(filter);

    const sql = `SELECT * FROM users WHERE ${where}`;
    const result = await this.db.query(sql, params);
    return result.rows.map(this.mapToUser);
  }

  async get(
    identifier: { id: string } | { email: string },
  ): Promise<User | null> {
    let sql: string;
    let params: unknown[];

    if ("id" in identifier) {
      sql = "SELECT * FROM users WHERE id = $1";
      params = [identifier.id];
    } else {
      sql = "SELECT * FROM users WHERE email = $1";
      params = [identifier.email];
    }

    const result = await this.db.query(sql, params);
    return result.rows[0] ? this.mapToUser(result.rows[0]) : null;
  }

  async set(user: User): Promise<User> {
    if (user.id) {
      return this.updateUser(user);
    } else {
      return this.createUser(user);
    }
  }

  private async createUser(user: Omit<User, "id">): Promise<User> {
    const sql = `
      INSERT INTO users (name, email, created_at, updated_at)
      VALUES ($1, $2, NOW(), NOW())
      RETURNING *
    `;

    const result = await this.db.query(sql, [user.name, user.email]);
    return this.mapToUser(result.rows[0]);
  }

  private async updateUser(user: User): Promise<User> {
    const sql = `
      UPDATE users 
      SET name = $1, email = $2, updated_at = NOW()
      WHERE id = $3
      RETURNING *
    `;

    const result = await this.db.query(sql, [user.name, user.email, user.id]);
    return this.mapToUser(result.rows[0]);
  }
}
```

</repository_patterns>

<data_controller_patterns>

## 🎮 Data Controller Patterns

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

### Controller Implementation

```typescript
class UserController implements DataController<User> {
  constructor(
    private repository: UserRepository,
    private validator: UserValidator,
    private logger: Logger,
  ) {}

  async search(options: QueryOptions): Promise<PaginatedResult<User>> {
    this.logger.info("Searching users", { options });

    try {
      // Validate query options
      const validatedOptions = this.validator.validateQueryOptions(options);

      // Execute search
      const users = await this.repository.search(validatedOptions);
      const total = await this.repository.count(validatedOptions);

      // Build pagination metadata
      const pagination = this.buildPaginationMeta(validatedOptions, total);

      return { data: users, pagination };
    } catch (error) {
      this.logger.error("User search failed", { error, options });
      throw new SearchError("Failed to search users", error);
    }
  }

  async get(id: string): Promise<User | null> {
    this.logger.info("Getting user", { id });

    try {
      this.validator.validateId(id);
      const user = await this.repository.get({ id });

      if (!user) {
        this.logger.warn("User not found", { id });
      }

      return user;
    } catch (error) {
      this.logger.error("Failed to get user", { error, id });
      throw new RetrievalError("Failed to retrieve user", error);
    }
  }

  async upsert(data: UpsertData<User>): Promise<User> {
    this.logger.info("Upserting user", {
      data: { ...data, password: "[REDACTED]" },
    });

    try {
      // Validate input data
      const validatedData = this.validator.validateUpsertData(data);

      // Transform data for repository
      const user = this.transformToUser(validatedData);

      // Execute upsert
      const result = await this.repository.set(user);

      this.logger.info("User upserted successfully", { id: result.id });
      return result;
    } catch (error) {
      this.logger.error("User upsert failed", { error, data });
      throw new UpsertError("Failed to upsert user", error);
    }
  }

  private buildPaginationMeta(options: QueryOptions, total: number) {
    const { limit = 50, offset = 0 } = options;
    const page = Math.floor(offset / limit) + 1;
    const hasMore = offset + limit < total;

    return { page, limit, total, hasMore };
  }
}
```

</data_controller_patterns>

<transaction_management>

## 🔄 Transaction Management

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

// Usage example
async function transferFunds(
  fromUserId: string,
  toUserId: string,
  amount: number,
): Promise<void> {
  await transactionManager.executeTransaction(async (ctx) => {
    // Debit from source account
    await ctx.query(
      "UPDATE accounts SET balance = balance - $1 WHERE user_id = $2",
      [amount, fromUserId],
    );

    // Credit to destination account
    await ctx.query(
      "UPDATE accounts SET balance = balance + $1 WHERE user_id = $2",
      [amount, toUserId],
    );

    // Log transaction
    await ctx.query(
      "INSERT INTO transactions (from_user, to_user, amount, created_at) VALUES ($1, $2, $3, NOW())",
      [fromUserId, toUserId, amount],
    );
  });
}
```

</transaction_management>

<data_validation>

## ✅ Data Validation Patterns

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

  validatePartial(data: unknown): Partial<User> {
    if (!this.isObject(data)) {
      throw new ValidationError("Data must be an object");
    }

    const result: Partial<User> = {};

    if ("name" in data) {
      result.name = this.validateName(data.name);
    }
    if ("email" in data) {
      result.email = this.validateEmail(data.email);
    }

    return result;
  }

  private validateName(value: unknown): string {
    if (typeof value !== "string" || value.trim().length === 0) {
      throw new ValidationError("Name must be a non-empty string", "name");
    }
    return value.trim();
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

</data_validation>

<caching_strategies>

## 🗄️ Caching Strategies

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

  private buildCacheKey(identifier: string | object): string {
    if (typeof identifier === "string") {
      return this.keyBuilder(identifier);
    }

    // Handle object identifiers
    const keyParts = Object.entries(identifier)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => `${key}:${value}`)
      .join("|");

    return this.keyBuilder(keyParts);
  }
}
```

</caching_strategies>

<data_migration>

## 🔄 Data Migration Patterns

### Migration Structure

```typescript
interface Migration {
  id: string;
  description: string;
  up(context: MigrationContext): Promise<void>;
  down(context: MigrationContext): Promise<void>;
}

interface MigrationContext {
  query<T>(sql: string, params?: unknown[]): Promise<QueryResult<T>>;
  logger: Logger;
}

class CreateUsersTable implements Migration {
  id = "001_create_users_table";
  description = "Create users table with basic fields";

  async up(ctx: MigrationContext): Promise<void> {
    await ctx.query(`
      CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )
    `);

    await ctx.query(`
      CREATE INDEX idx_users_email ON users(email)
    `);

    ctx.logger.info("Created users table");
  }

  async down(ctx: MigrationContext): Promise<void> {
    await ctx.query("DROP TABLE IF EXISTS users");
    ctx.logger.info("Dropped users table");
  }
}
```

</data_migration>
