# Service Template Pattern

*Template for implementing backend services with handlers, business logic, and proper architecture*

## Basic Service Template

```typescript
// Handler Layer
export async function getUserHandler(
  params: { userId: string },
  context: HandlerContext,
  options: HandlerOptions = {}
): Promise<ApiResponse<User>> {
  try {
    // 1. Validate input
    validateUserId(params.userId);
    
    // 2. Check authorization
    const authContext = await buildAuthContext(context.authToken);
    requirePermission('user:read')(authContext);
    
    // 3. Check resource access
    if (!await canAccessResource(authContext.user.userId, params.userId, 'read')) {
      throw new ForbiddenError('Cannot access this user');
    }
    
    // 4. Execute business logic
    const user = await userService.getUser(params.userId);
    
    // 5. Return success response
    return {
      status: 'success',
      data: user,
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  } catch (error) {
    // 6. Transform and return error
    return transformError(error);
  }
}

// Service Layer
class UserService {
  constructor(
    private userRepository: UserRepository,
    private validator: UserValidator,
    private logger: Logger
  ) {}

  async getUser(userId: string): Promise<User> {
    this.logger.info('Getting user', { userId });
    
    try {
      // Validate input
      this.validator.validateId(userId);
      
      // Fetch from repository
      const user = await this.userRepository.get({ id: userId });
      if (!user) {
        throw new NotFoundError('User', userId);
      }
      
      this.logger.info('User retrieved successfully', { userId });
      return user;
    } catch (error) {
      this.logger.error('Failed to get user', { error, userId });
      throw error;
    }
  }

  async createUser(params: CreateUserParams): Promise<User> {
    this.logger.info('Creating user', { email: params.email });
    
    try {
      // Validate input
      const validatedParams = this.validator.validateCreateParams(params);
      
      // Check business rules
      await this.checkEmailUnique(validatedParams.email);
      
      // Create user
      const user = await this.userRepository.set({
        name: validatedParams.name,
        email: validatedParams.email.toLowerCase(),
        createdAt: new Date(),
        updatedAt: new Date(),
      });
      
      this.logger.info('User created successfully', { userId: user.id });
      return user;
    } catch (error) {
      this.logger.error('Failed to create user', { error, email: params.email });
      throw error;
    }
  }

  async updateUser(userId: string, params: UpdateUserParams): Promise<User> {
    this.logger.info('Updating user', { userId });
    
    try {
      // Validate input
      this.validator.validateId(userId);
      const validatedParams = this.validator.validateUpdateParams(params);
      
      // Check user exists
      const existingUser = await this.userRepository.get({ id: userId });
      if (!existingUser) {
        throw new NotFoundError('User', userId);
      }
      
      // Check email uniqueness if email is being updated
      if (validatedParams.email && validatedParams.email !== existingUser.email) {
        await this.checkEmailUnique(validatedParams.email);
      }
      
      // Update user
      const updatedUser = await this.userRepository.set({
        ...existingUser,
        ...validatedParams,
        updatedAt: new Date(),
      });
      
      this.logger.info('User updated successfully', { userId });
      return updatedUser;
    } catch (error) {
      this.logger.error('Failed to update user', { error, userId });
      throw error;
    }
  }

  private async checkEmailUnique(email: string): Promise<void> {
    const existingUser = await this.userRepository.get({ email });
    if (existingUser) {
      throw new ConflictError('Email already exists', { email });
    }
  }
}
```

## Service with Transaction Support

```typescript
class OrderService {
  constructor(
    private orderRepository: OrderRepository,
    private inventoryService: InventoryService,
    private paymentService: PaymentService,
    private transactionManager: TransactionManager,
    private logger: Logger
  ) {}

  async createOrder(params: CreateOrderParams): Promise<Order> {
    return this.transactionManager.executeTransaction(async (ctx) => {
      this.logger.info('Creating order', { customerId: params.customerId });
      
      try {
        // 1. Validate order
        const validatedParams = this.validator.validateCreateParams(params);
        
        // 2. Check inventory
        await this.checkInventoryAvailability(validatedParams.items);
        
        // 3. Calculate totals
        const totals = await this.calculateOrderTotals(validatedParams.items);
        
        // 4. Process payment
        const paymentResult = await this.paymentService.processPayment({
          amount: totals.total,
          customerId: validatedParams.customerId,
          paymentMethod: validatedParams.paymentMethod,
        });
        
        // 5. Reserve inventory
        await this.inventoryService.reserveItems(validatedParams.items);
        
        // 6. Create order
        const order = await this.orderRepository.set({
          customerId: validatedParams.customerId,
          items: validatedParams.items,
          totals,
          paymentId: paymentResult.id,
          status: 'confirmed',
          createdAt: new Date(),
          updatedAt: new Date(),
        });
        
        this.logger.info('Order created successfully', { orderId: order.id });
        return order;
      } catch (error) {
        this.logger.error('Failed to create order', { error, customerId: params.customerId });
        throw error;
      }
    });
  }

  private async checkInventoryAvailability(items: OrderItem[]): Promise<void> {
    for (const item of items) {
      const available = await this.inventoryService.getAvailableQuantity(item.productId);
      if (available < item.quantity) {
        throw new InsufficientInventoryError(item.productId, item.quantity, available);
      }
    }
  }
}
```

## Service with Caching

```typescript
class ProductService {
  constructor(
    private productRepository: ProductRepository,
    private cache: CacheService,
    private logger: Logger
  ) {}

  async getProduct(productId: string): Promise<Product | null> {
    const cacheKey = `product:${productId}`;
    
    try {
      // Try cache first
      const cached = await this.cache.get<Product>(cacheKey);
      if (cached) {
        this.logger.debug('Product found in cache', { productId });
        return cached;
      }
      
      // Fallback to repository
      const product = await this.productRepository.get({ id: productId });
      if (product) {
        // Cache for 5 minutes
        await this.cache.set(cacheKey, product, { ttl: 300 });
        this.logger.debug('Product cached', { productId });
      }
      
      return product;
    } catch (error) {
      this.logger.error('Failed to get product', { error, productId });
      throw error;
    }
  }

  async updateProduct(productId: string, params: UpdateProductParams): Promise<Product> {
    try {
      const product = await this.productRepository.set({
        id: productId,
        ...params,
        updatedAt: new Date(),
      });
      
      // Invalidate cache
      const cacheKey = `product:${productId}`;
      await this.cache.delete(cacheKey);
      
      // Invalidate related caches
      await this.cache.deletePattern(`category:${product.categoryId}:*`);
      
      this.logger.info('Product updated and cache invalidated', { productId });
      return product;
    } catch (error) {
      this.logger.error('Failed to update product', { error, productId });
      throw error;
    }
  }
}
```

## Service with Event Publishing

```typescript
class UserService {
  constructor(
    private userRepository: UserRepository,
    private eventPublisher: EventPublisher,
    private logger: Logger
  ) {}

  async createUser(params: CreateUserParams): Promise<User> {
    try {
      const user = await this.userRepository.set({
        name: params.name,
        email: params.email,
        createdAt: new Date(),
        updatedAt: new Date(),
      });
      
      // Publish domain event
      await this.eventPublisher.publish(new UserCreatedEvent({
        userId: user.id,
        email: user.email,
        name: user.name,
        createdAt: user.createdAt,
      }));
      
      this.logger.info('User created and event published', { userId: user.id });
      return user;
    } catch (error) {
      this.logger.error('Failed to create user', { error });
      throw error;
    }
  }

  async updateUser(userId: string, params: UpdateUserParams): Promise<User> {
    const existingUser = await this.userRepository.get({ id: userId });
    if (!existingUser) {
      throw new NotFoundError('User', userId);
    }

    const updatedUser = await this.userRepository.set({
      ...existingUser,
      ...params,
      updatedAt: new Date(),
    });

    // Publish update event with changes
    const changes = this.detectChanges(existingUser, updatedUser);
    await this.eventPublisher.publish(new UserUpdatedEvent({
      userId: updatedUser.id,
      changes,
      updatedAt: updatedUser.updatedAt,
    }));

    return updatedUser;
  }

  private detectChanges(oldUser: User, newUser: User): Record<string, { old: any; new: any }> {
    const changes: Record<string, { old: any; new: any }> = {};
    
    for (const [key, newValue] of Object.entries(newUser)) {
      const oldValue = oldUser[key as keyof User];
      if (oldValue !== newValue && key !== 'updatedAt') {
        changes[key] = { old: oldValue, new: newValue };
      }
    }
    
    return changes;
  }
}
```

## Service with Background Jobs

```typescript
class EmailService {
  constructor(
    private emailRepository: EmailRepository,
    private jobQueue: JobQueue,
    private logger: Logger
  ) {}

  async sendEmail(params: SendEmailParams): Promise<void> {
    try {
      // Create email record
      const email = await this.emailRepository.set({
        to: params.to,
        subject: params.subject,
        body: params.body,
        status: 'queued',
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      // Queue for background processing
      await this.jobQueue.add('send-email', {
        emailId: email.id,
        to: params.to,
        subject: params.subject,
        body: params.body,
      }, {
        delay: 0,
        attempts: 3,
        backoff: 'exponential',
      });

      this.logger.info('Email queued for sending', { emailId: email.id });
    } catch (error) {
      this.logger.error('Failed to queue email', { error, to: params.to });
      throw error;
    }
  }

  async processEmailJob(job: Job<SendEmailJobData>): Promise<void> {
    const { emailId, to, subject, body } = job.data;
    
    try {
      // Send email via external service
      await this.externalEmailService.send({ to, subject, body });
      
      // Update status
      await this.emailRepository.updateStatus(emailId, 'sent');
      
      this.logger.info('Email sent successfully', { emailId });
    } catch (error) {
      // Update status
      await this.emailRepository.updateStatus(emailId, 'failed');
      
      this.logger.error('Failed to send email', { error, emailId });
      throw error;
    }
  }
}
```

## Usage Notes

### When to Use
- Need to implement business logic layer
- Require coordination between multiple repositories
- Want consistent error handling and logging
- Need transaction support
- Require caching or event publishing

### Common Patterns
- **Single Responsibility**: Each service handles one domain
- **Dependency Injection**: Services receive dependencies in constructor
- **Error Handling**: Consistent error transformation and logging
- **Validation**: Input validation at service boundaries
- **Transaction Management**: Use transactions for multi-step operations
- **Event Publishing**: Publish domain events for integration

### Common Mistakes to Avoid
- Putting HTTP concerns in service layer
- Not validating inputs at service boundaries
- Missing proper error handling and logging
- Creating services that are too large or handle multiple domains
- Not using transactions for operations that require consistency