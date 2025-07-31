# Data Controller Pattern Template

*Template for implementing data controllers with validation, logging, and error handling*

## Basic Controller Template

```typescript
class UserController implements DataController<User> {
  constructor(
    private repository: UserRepository,
    private validator: UserValidator,
    private logger: Logger
  ) {}

  async search(options: QueryOptions): Promise<PaginatedResult<User>> {
    this.logger.info('Searching users', { options });
    
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
      this.logger.error('User search failed', { error, options });
      throw new SearchError('Failed to search users', error);
    }
  }

  async get(id: string): Promise<User | null> {
    this.logger.info('Getting user', { id });
    
    try {
      this.validator.validateId(id);
      const user = await this.repository.get({ id });
      
      if (!user) {
        this.logger.warn('User not found', { id });
      }
      
      return user;
    } catch (error) {
      this.logger.error('Failed to get user', { error, id });
      throw new RetrievalError('Failed to retrieve user', error);
    }
  }

  async upsert(data: UpsertData<User>): Promise<User> {
    this.logger.info('Upserting user', { data: this.sanitizeLogData(data) });
    
    try {
      // Validate input data
      const validatedData = this.validator.validateUpsertData(data);
      
      // Transform data for repository
      const user = this.transformToUser(validatedData);
      
      // Execute upsert
      const result = await this.repository.set(user);
      
      this.logger.info('User upserted successfully', { id: result.id });
      return result;
    } catch (error) {
      this.logger.error('User upsert failed', { error, data: this.sanitizeLogData(data) });
      throw new UpsertError('Failed to upsert user', error);
    }
  }

  async delete(id: string): Promise<void> {
    this.logger.info('Deleting user', { id });
    
    try {
      this.validator.validateId(id);
      
      // Check if user exists
      const existingUser = await this.repository.get({ id });
      if (!existingUser) {
        throw new NotFoundError('User', id);
      }
      
      await this.repository.drop(id);
      this.logger.info('User deleted successfully', { id });
    } catch (error) {
      this.logger.error('User deletion failed', { error, id });
      throw new DeletionError('Failed to delete user', error);
    }
  }

  async bulkCreate(data: CreateData<User>[]): Promise<User[]> {
    this.logger.info('Bulk creating users', { count: data.length });
    
    try {
      // Validate all data first
      const validatedData = data.map(item => this.validator.validateCreateData(item));
      
      // Transform to users
      const users = validatedData.map(item => this.transformToUser(item));
      
      // Execute batch operation
      const results = await this.repository.setBatch(users);
      
      this.logger.info('Bulk user creation completed', { 
        count: results.length,
        ids: results.map(u => u.id)
      });
      
      return results;
    } catch (error) {
      this.logger.error('Bulk user creation failed', { error, count: data.length });
      throw new BatchCreateError('Failed to create users in bulk', error);
    }
  }

  private buildPaginationMeta(options: QueryOptions, total: number) {
    const { limit = 50, offset = 0 } = options;
    const page = Math.floor(offset / limit) + 1;
    const hasMore = offset + limit < total;
    
    return { page, limit, total, hasMore };
  }

  private transformToUser(data: UpsertData<User> | CreateData<User>): User {
    return {
      id: 'id' in data ? data.id : undefined,
      name: data.name,
      email: data.email.toLowerCase(),
      createdAt: 'createdAt' in data ? data.createdAt : new Date(),
      updatedAt: new Date(),
    } as User;
  }

  private sanitizeLogData(data: any): any {
    const sanitized = { ...data };
    
    // Remove sensitive fields from logs
    if (sanitized.password) {
      sanitized.password = '[REDACTED]';
    }
    if (sanitized.token) {
      sanitized.token = '[REDACTED]';
    }
    
    return sanitized;
  }
}
```

## Variations

### With Caching Layer

```typescript
class CachedUserController extends UserController {
  constructor(
    repository: UserRepository,
    validator: UserValidator,
    logger: Logger,
    private cache: CacheService
  ) {
    super(repository, validator, logger);
  }

  async get(id: string): Promise<User | null> {
    const cacheKey = `user:${id}`;
    
    // Try cache first
    const cached = await this.cache.get<User>(cacheKey);
    if (cached) {
      this.logger.debug('User found in cache', { id });
      return cached;
    }

    // Fallback to repository
    const user = await super.get(id);
    if (user) {
      await this.cache.set(cacheKey, user, { ttl: 300 });
    }
    
    return user;
  }

  async upsert(data: UpsertData<User>): Promise<User> {
    const result = await super.upsert(data);
    
    // Invalidate cache
    await this.cache.delete(`user:${result.id}`);
    
    return result;
  }
}
```

### With Event Publishing

```typescript
class EventDrivenUserController extends UserController {
  constructor(
    repository: UserRepository,
    validator: UserValidator,
    logger: Logger,
    private eventPublisher: EventPublisher
  ) {
    super(repository, validator, logger);
  }

  async upsert(data: UpsertData<User>): Promise<User> {
    const isUpdate = 'id' in data && data.id;
    const result = await super.upsert(data);
    
    // Publish domain event
    const event = isUpdate 
      ? new UserUpdatedEvent(result)
      : new UserCreatedEvent(result);
    
    await this.eventPublisher.publish(event);
    
    return result;
  }

  async delete(id: string): Promise<void> {
    const user = await this.get(id);
    if (!user) {
      throw new NotFoundError('User', id);
    }

    await super.delete(id);
    
    // Publish deletion event
    await this.eventPublisher.publish(new UserDeletedEvent(user));
  }
}
```

### With Authorization

```typescript
class SecureUserController extends UserController {
  constructor(
    repository: UserRepository,
    validator: UserValidator,
    logger: Logger,
    private authService: AuthService
  ) {
    super(repository, validator, logger);
  }

  async get(id: string, context: RequestContext): Promise<User | null> {
    // Check permissions
    await this.authService.requirePermission(context, 'user:read');
    
    // Check if user can access this specific user
    if (!await this.canAccessUser(context.userId, id)) {
      throw new ForbiddenError('Cannot access this user');
    }
    
    return super.get(id);
  }

  async upsert(data: UpsertData<User>, context: RequestContext): Promise<User> {
    const isUpdate = 'id' in data && data.id;
    const permission = isUpdate ? 'user:update' : 'user:create';
    
    await this.authService.requirePermission(context, permission);
    
    if (isUpdate && !await this.canModifyUser(context.userId, data.id)) {
      throw new ForbiddenError('Cannot modify this user');
    }
    
    return super.upsert(data);
  }

  private async canAccessUser(requestingUserId: string, targetUserId: string): Promise<boolean> {
    // Users can always access their own data
    if (requestingUserId === targetUserId) {
      return true;
    }
    
    // Check if user has admin role
    return this.authService.hasRole(requestingUserId, 'admin');
  }
}
```

## Usage Notes

### When to Use
- Need orchestration layer between API and repository
- Require input validation and error handling
- Want consistent logging and monitoring
- Need to handle business logic beyond simple CRUD

### Common Mistakes to Avoid
- Putting business logic directly in repository
- Not validating inputs before processing
- Missing proper error classification
- Logging sensitive data without sanitization
- Not providing meaningful error messages to clients