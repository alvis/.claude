# Repository Pattern Template

_Template for implementing data access repositories following standard patterns_

## Basic Repository Template

```typescript
interface UserRepository extends EntityRepository<User, string> {
  search(options: QueryOptions): Promise<User[]>;
  list(filter: UserFilter): Promise<User[]>;
  get(params: { id: string } | { email: string }): Promise<User | null>;
  set(user: User): Promise<User>;
  drop(id: string): Promise<void>;
}

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

  async drop(id: string): Promise<void> {
    await this.db.query("DELETE FROM users WHERE id = $1", [id]);
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

  private mapToUser(row: any): User {
    return {
      id: row.id,
      name: row.name,
      email: row.email,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  }

  private buildWhereClause(filter: UserFilter): {
    where: string;
    params: unknown[];
  } {
    const conditions: string[] = [];
    const params: unknown[] = [];
    let paramIndex = 1;

    if (filter.name) {
      conditions.push(`name ILIKE $${paramIndex++}`);
      params.push(`%${filter.name}%`);
    }

    if (filter.email) {
      conditions.push(`email = $${paramIndex++}`);
      params.push(filter.email);
    }

    if (filter.isActive !== undefined) {
      conditions.push(`is_active = $${paramIndex++}`);
      params.push(filter.isActive);
    }

    return {
      where: conditions.length > 0 ? conditions.join(" AND ") : "1=1",
      params,
    };
  }

  private buildSortClause(
    sort?: Array<{ field: string; order: "asc" | "desc" }>,
  ): string {
    if (!sort || sort.length === 0) {
      return "ORDER BY created_at DESC";
    }

    const clauses = sort.map(
      ({ field, order }) => `${field} ${order.toUpperCase()}`,
    );
    return `ORDER BY ${clauses.join(", ")}`;
  }
}
```

## Variations

### With Caching

```typescript
class CachedUserRepository implements UserRepository {
  constructor(
    private repository: UserRepository,
    private cache: CacheService,
  ) {}

  async get(
    identifier: { id: string } | { email: string },
  ): Promise<User | null> {
    const key = this.buildCacheKey(identifier);

    const cached = await this.cache.get<User>(key);
    if (cached) return cached;

    const user = await this.repository.get(identifier);
    if (user) {
      await this.cache.set(key, user, { ttl: 300 });
    }

    return user;
  }

  async set(user: User): Promise<User> {
    const result = await this.repository.set(user);

    // Invalidate relevant cache entries
    await this.cache.delete(`user:${result.id}`);
    await this.cache.delete(`user:email:${result.email}`);

    return result;
  }
}
```

### With Transactions

```typescript
class TransactionalUserRepository implements UserRepository {
  constructor(
    private db: DatabaseService,
    private transactionManager: TransactionManager,
  ) {}

  async setBatch(users: User[]): Promise<User[]> {
    return this.transactionManager.executeTransaction(async (ctx) => {
      const results: User[] = [];

      for (const user of users) {
        const result = await this.setWithContext(user, ctx);
        results.push(result);
      }

      return results;
    });
  }

  private async setWithContext(
    user: User,
    ctx: TransactionContext,
  ): Promise<User> {
    if (user.id) {
      const result = await ctx.query(
        "UPDATE users SET name = $1, email = $2 WHERE id = $3 RETURNING *",
        [user.name, user.email, user.id],
      );
      return this.mapToUser(result.rows[0]);
    } else {
      const result = await ctx.query(
        "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
        [user.name, user.email],
      );
      return this.mapToUser(result.rows[0]);
    }
  }
}
```

## Usage Notes

### When to Use

- Building any data access layer
- Need consistent CRUD operations
- Want separation between business logic and data access
- Require testable data layer

### Common Mistakes to Avoid

- Mixing search and list operation logic
- Not handling nullable return types properly
- Using generic Error instead of specific error classes
- Forgetting to map database results to domain entities
- Not implementing proper transaction handling for batch operations
