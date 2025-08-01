# Error Handling Standards

_Standards for error classification, handling patterns, and logging in backend services_

## Error Classification

### Core Error Classes

```typescript
// Base error class
class BaseError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: unknown,
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

// Validation errors (400)
class ValidationError extends BaseError {
  constructor(
    message: string,
    public field?: string,
    details?: unknown,
  ) {
    super(message, "VALIDATION_ERROR", 400, details);
  }
}

// Authentication errors (401)
class AuthenticationError extends BaseError {
  constructor(message: string = "Authentication required") {
    super(message, "AUTHENTICATION_REQUIRED", 401);
  }
}

// Authorization errors (403)
class AuthorizationError extends BaseError {
  constructor(message: string = "Insufficient permissions") {
    super(message, "INSUFFICIENT_PERMISSIONS", 403);
  }
}

// Not found errors (404)
class NotFoundError extends BaseError {
  constructor(resource: string, identifier: string) {
    super(
      `${resource} with identifier ${identifier} not found`,
      "NOT_FOUND",
      404,
    );
  }
}

// Conflict errors (409)
class ConflictError extends BaseError {
  constructor(message: string, details?: unknown) {
    super(message, "CONFLICT", 409, details);
  }
}

// Business logic errors (422)
class BusinessRuleError extends BaseError {
  constructor(message: string, rule: string, details?: unknown) {
    super(message, "BUSINESS_RULE_VIOLATION", 422, { rule, ...details });
  }
}
```

### Domain-Specific Errors

```typescript
// User domain errors
class UserNotFoundError extends NotFoundError {
  constructor(userId: string) {
    super("User", userId);
    this.code = "USER_NOT_FOUND";
  }
}

class EmailAlreadyExistsError extends ConflictError {
  constructor(email: string) {
    super("Email address already exists", { email });
    this.code = "EMAIL_ALREADY_EXISTS";
  }
}

// Order domain errors
class InsufficientInventoryError extends BusinessRuleError {
  constructor(productId: string, requested: number, available: number) {
    super("Insufficient inventory for product", "inventory_check", {
      productId,
      requested,
      available,
    });
    this.code = "INSUFFICIENT_INVENTORY";
  }
}
```

## Error Transformation

### HTTP Error Transformation

```typescript
interface ApiError {
  code: string;
  message: string;
  statusCode: number;
  details?: unknown;
}

export function transformError(error: unknown): ApiResponse<never> {
  let apiError: ApiError;

  if (error instanceof BaseError) {
    apiError = {
      code: error.code,
      message: error.message,
      statusCode: error.statusCode,
      details: error.details,
    };
  } else if (error instanceof Error) {
    // Handle standard JavaScript errors
    apiError = {
      code: "INTERNAL_ERROR",
      message: "An unexpected error occurred",
      statusCode: 500,
    };
  } else {
    // Handle unknown error types
    apiError = {
      code: "UNKNOWN_ERROR",
      message: "An unknown error occurred",
      statusCode: 500,
    };
  }

  return {
    status: "error",
    error: {
      code: apiError.code,
      message: apiError.message,
      details: apiError.details,
    },
  };
}
```

### Database Error Handling

```typescript
export function handleDatabaseError(error: any): never {
  // PostgreSQL specific error codes
  switch (error.code) {
    case "23505": // unique_violation
      throw new ConflictError("Resource already exists", {
        constraint: error.constraint,
        detail: error.detail,
      });

    case "23503": // foreign_key_violation
      throw new ValidationError(
        "Referenced resource does not exist",
        undefined,
        {
          constraint: error.constraint,
          detail: error.detail,
        },
      );

    case "23502": // not_null_violation
      throw new ValidationError("Required field is missing", error.column);

    case "23514": // check_violation
      throw new ValidationError("Value violates constraints", undefined, {
        constraint: error.constraint,
      });

    case "42P01": // undefined_table
    case "42703": // undefined_column
      throw new Error("Database schema error");

    default:
      throw new Error("Database operation failed");
  }
}
```

## Logging Standards

### Structured Logging

```typescript
interface LogContext {
  requestId?: string;
  userId?: string;
  operation: string;
  duration?: number;
  [key: string]: unknown;
}

interface ErrorLogEntry {
  level: "error";
  message: string;
  timestamp: string;
  context: LogContext;
  error: {
    name: string;
    message: string;
    stack?: string;
    code?: string;
    statusCode?: number;
    details?: unknown;
  };
}

function logError(error: Error, context: LogContext): void {
  const logEntry: ErrorLogEntry = {
    level: "error",
    message: error.message,
    timestamp: new Date().toISOString(),
    context,
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack,
      code: error instanceof BaseError ? error.code : undefined,
      statusCode: error instanceof BaseError ? error.statusCode : undefined,
      details: error instanceof BaseError ? error.details : undefined,
    },
  };

  console.error(JSON.stringify(logEntry));
}
```

### Operation Logging

```typescript
function logOperation(context: LogContext, success: boolean = true): void {
  const level = success ? "info" : "warn";
  const message = `Operation ${context.operation} ${success ? "completed" : "failed"}`;

  const logEntry = {
    level,
    message,
    timestamp: new Date().toISOString(),
    context,
  };

  console.log(JSON.stringify(logEntry));
}
```

## Error Handling Patterns

### Handler Error Handling

```typescript
export async function createUserHandler(
  params: CreateUserParams,
  context: HandlerContext,
): Promise<ApiResponse<User>> {
  const startTime = Date.now();

  try {
    // Log operation start
    logOperation({
      ...context,
      operation: "create_user",
      params: sanitizeParams(params),
    });

    // Execute business logic
    const user = await userService.createUser(params);

    // Log success
    logOperation({
      ...context,
      operation: "create_user",
      duration: Date.now() - startTime,
      userId: user.id,
    });

    return {
      status: "success",
      data: user,
      meta: {
        timestamp: new Date().toISOString(),
      },
    };
  } catch (error) {
    // Log error with context
    logError(error as Error, {
      ...context,
      operation: "create_user",
      duration: Date.now() - startTime,
      params: sanitizeParams(params),
    });

    // Transform and return error response
    return transformError(error);
  }
}
```

### Service Error Handling

```typescript
class UserService {
  async createUser(params: CreateUserParams): Promise<User> {
    try {
      // Validate input
      this.validator.validateCreateParams(params);

      // Check business rules
      await this.checkEmailUnique(params.email);

      // Create user
      const user = await this.userRepository.set({
        name: params.name,
        email: params.email.toLowerCase(),
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      return user;
    } catch (error) {
      // Handle database errors
      if (this.isDatabaseError(error)) {
        handleDatabaseError(error);
      }

      // Re-throw application errors
      throw error;
    }
  }

  private async checkEmailUnique(email: string): Promise<void> {
    const existingUser = await this.userRepository.get({ email });
    if (existingUser) {
      throw new EmailAlreadyExistsError(email);
    }
  }
}
```

### Repository Error Handling

```typescript
class UserRepository {
  async get(
    identifier: { id: string } | { email: string },
  ): Promise<User | null> {
    try {
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
    } catch (error) {
      // Handle database connection errors
      if (this.isConnectionError(error)) {
        throw new Error("Database connection failed");
      }

      // Handle other database errors
      handleDatabaseError(error);
    }
  }
}
```

## Security Considerations

### Error Message Security

```typescript
// ✅ Good: Safe error messages
throw new AuthenticationError("Invalid credentials");
throw new NotFoundError("User", userId);
throw new ValidationError("Email format is invalid", "email");

// ❌ Bad: Exposing internal details
throw new Error("Database connection to postgres://user:pass@host failed");
throw new Error("JWT secret key is missing from environment");
throw new Error("User with email john@example.com already exists");
```

### Sensitive Data Sanitization

```typescript
function sanitizeParams(params: any): any {
  const sanitized = { ...params };

  // Remove sensitive fields
  const sensitiveFields = ["password", "token", "secret", "key"];

  for (const field of sensitiveFields) {
    if (sanitized[field]) {
      sanitized[field] = "[REDACTED]";
    }
  }

  return sanitized;
}

function sanitizeError(error: any): any {
  const sanitized = { ...error };

  // Remove sensitive information from error details
  if (sanitized.details) {
    sanitized.details = sanitizeParams(sanitized.details);
  }

  // Remove stack traces in production
  if (process.env.NODE_ENV === "production") {
    delete sanitized.stack;
  }

  return sanitized;
}
```

## Monitoring & Alerting

### Error Metrics

```typescript
interface ErrorMetrics {
  errorCode: string;
  errorType: string;
  operation: string;
  statusCode: number;
  count: number;
  timestamp: string;
}

function trackErrorMetrics(error: BaseError, context: LogContext): void {
  const metrics: ErrorMetrics = {
    errorCode: error.code,
    errorType: error.name,
    operation: context.operation,
    statusCode: error.statusCode,
    count: 1,
    timestamp: new Date().toISOString(),
  };

  // Send to monitoring service
  metricsService.increment("api.errors", metrics);
}
```

### Alert Conditions

- Error rate exceeds threshold (e.g., >5% over 5 minutes)
- Specific critical errors occur (authentication failures, database errors)
- New error types appear
- Error rate increases significantly compared to baseline

## Testing Error Scenarios

### Unit Tests

```typescript
describe("UserService.createUser", () => {
  it("should throw EmailAlreadyExistsError when email exists", async () => {
    // Arrange
    mockRepository.get.mockResolvedValue(existingUser);

    // Act & Assert
    await expect(userService.createUser(params)).rejects.toThrow(
      EmailAlreadyExistsError,
    );
  });

  it("should throw ValidationError for invalid email", async () => {
    // Arrange
    const invalidParams = { ...params, email: "invalid-email" };

    // Act & Assert
    await expect(userService.createUser(invalidParams)).rejects.toThrow(
      ValidationError,
    );
  });
});
```

### Integration Tests

```typescript
describe("POST /api/users", () => {
  it("should return 409 when email already exists", async () => {
    // Arrange
    await createTestUser({ email: "test@example.com" });

    // Act
    const response = await request(app)
      .post("/api/users")
      .send({ name: "Test User", email: "test@example.com" });

    // Assert
    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe("EMAIL_ALREADY_EXISTS");
  });
});
```
