# Error Handling & Logging

## Error Handling Patterns

### Use @theriety/error Classes

- **Always use** custom error classes from `@theriety/error`
- **Never use** generic `Error` or silent error handling
- **Throw early** when detecting invalid states
- **Handle errors explicitly** at appropriate boundaries

### Error Class Hierarchy

```typescript
// use specific error classes for different scenarios
import {
  MissingDataError,
  ValidationError,
  UnauthorizedError,
  ConflictError,
} from '@theriety/error';

// ✅ GOOD: Specific error class
if (!user) {
  throw new MissingDataError('user profile not found');
}

// ❌ Bad: Generic error
if (!user) {
  throw new Error('User not found');
}
```

### Error Handling in Async Code

```typescript
// ✅ real-world example: user profile operation
export async function getUserProfile(
  userId: string,
  action: Action,
): Promise<UserProfile | null> {
  try {
    action.log.info('fetching user profile', { userId });

    const user = await prisma.user.findUnique({
      where: { id: userId },
      include: {
        profile: true,
        preferences: true,
      },
    });

    if (!user) {
      throw new MissingDataError('user not found');
    }

    // validate profile completeness
    if (!user.profile?.isComplete) {
      throw new ValidationError('user profile incomplete');
    }

    return mapToUserProfile(user);
  } catch (error) {
    if (error instanceof MissingDataError) {
      action.log.warn('user not found', { userId });

      return null;
    }

    if (error instanceof ValidationError) {
      action.log.warn('profile validation failed', { userId, error });
      // return partial profile for incomplete data
      return createPartialProfile(userId);
    }

    // log unexpected errors and re-throw
    action.log.error('failed to fetch user profile', { userId, error });
    throw error;
  }
}

// ✅ real-world example: payment processing with retries
export async function processPayment(
  orderId: string,
  action: Action,
): Promise<PaymentResult> {
  const maxRetries = 3;
  let lastError: Error;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      action.log.info('processing payment', { orderId, attempt });

      const order = await getOrder(orderId);
      if (!order) {
        throw new MissingDataError('order not found');
      }

      const result = await paymentGateway.charge({
        amount: order.total,
        currency: order.currency,
        customerId: order.customerId,
      });

      action.log.info('payment successful', {
        orderId,
        transactionId: result.id,
      });

      return result;
    } catch (error) {
      lastError = error;

      if (error instanceof MissingDataError) {
        // don't retry for missing data
        throw error;
      }

      if (error instanceof PaymentDeclinedError) {
        action.log.warn('payment declined', { orderId, attempt, error });
        // don't retry declined payments
        throw error;
      }

      if (attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 1000; // exponential backoff
        action.log.warn('payment failed, retrying', {
          orderId,
          attempt,
          delay,
          error,
        });

        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  action.log.error('payment failed after all retries', {
    orderId,
    attempts: maxRetries,
    error: lastError,
  });

  throw new ServiceUnavailableError('payment processing failed');
}

// ✅ real-world example: batch operation with partial failure handling
export async function syncUserData(
  userIds: string[],
  action: Action,
): Promise<SyncResult> {
  const results = await Promise.allSettled(
    userIds.map((userId) => syncSingleUser(userId, action)),
  );

  const succeeded = results.filter((r) => r.status === 'fulfilled');
  const failed = results.filter((r) => r.status === 'rejected');

  if (failed.length > 0) {
    action.log.warn('partial sync failure', {
      total: userIds.length,
      succeeded: succeeded.length,
      failed: failed.length,
      errors: failed.map((r) => (r as PromiseRejectedResult).reason),
    });
  }

  return {
    total: userIds.length,
    succeeded: succeeded.length,
    failed: failed.length,
    failedUserIds: userIds.filter(
      (_, index) => results[index].status === 'rejected',
    ),
  };
}
```

### Error Boundaries (React)

See `06-react-conventions.md` for React error boundary implementation details.

## Logging Guidelines

### Transactional Logger

**IMPORTANT**: Never use `console.log` directly. Every service operation receives a transactional logger through the `action` parameter.

```typescript
// ✅ correct: use transactional logger
export async function processOrder(orderId: string, action: Action) {
  action.log.info('processing order', { orderId });

  try {
    const result = await performOperation();
    action.log.debug('operation completed', { orderId, result });
    return result;
  } catch (error) {
    action.log.error('order processing failed', { orderId, error });
    throw error;
  }
}

// ❌ wrong: never use console directly
function badExample() {
  console.log('This is wrong');
  console.error('Never do this');
}
```

### Log Levels

Use appropriate log levels for different scenarios:

- **FATAL**: System-critical errors requiring immediate intervention
- **ERROR**: Unrecoverable errors in the current operation
- **WARN**: Recoverable issues or unexpected but handled conditions
- **INFO**: Important business events or state changes
- **DEBUG**: Detailed information for debugging
- **TRACE**: Very detailed information (rarely used)

### Structured Logging

```typescript
// ✅ good: structured logging with context
action.log.error('payment processing failed', {
  userId,
  orderId,
  amount: order.total,
  error: error.message,
  errorCode: error.code,
  gateway: 'stripe',
});

// ❌ bad: unstructured string concatenation
action.log.error('Error: ' + error.message + ' for user ' + userId);

// ✅ good: include relevant metadata
action.log.info('user authenticated', {
  userId: user.id,
  method: 'oauth',
  provider: 'google',
  ip: request.ip,
  userAgent: request.headers['user-agent'],
});
```

### What to Log

#### Always Log

- Authentication/authorization failures
- Data validation errors
- External service failures
- Unhandled exceptions
- Performance warnings (slow queries, etc.)

#### Never Log

- Passwords or authentication tokens
- Personal identifiable information (PII)
- Credit card numbers
- API keys or secrets
- Full request/response bodies with sensitive data

### Logging Best Practices

```typescript
// ✅ log at appropriate boundaries
export async function createUser(input: CreateUserInput, action: Action) {
  action.log.info('creating user', { email: input.email });

  try {
    // validate input
    const validated = await validateUserInput(input);
    action.log.debug('input validated', { email: input.email });

    // check for duplicates
    const existing = await findUserByEmail(input.email);
    if (existing) {
      action.log.warn('duplicate user attempt', { email: input.email });
      throw new ConflictError('user already exists');
    }

    // create user
    const user = await prisma.user.create({ data: validated });
    action.log.info('user created successfully', {
      userId: user.id,
      email: user.email,
    });

    // send welcome email
    try {
      await sendWelcomeEmail(user);
      action.log.debug('welcome email sent', { userId: user.id });
    } catch (error) {
      // non-critical failure
      action.log.warn('failed to send welcome email', {
        userId: user.id,
        error,
      });
    }

    return user;
  } catch (error) {
    action.log.error('user creation failed', { email: input.email, error });
    throw error;
  }
}

// ✅ use appropriate log levels
action.log.trace('entering function', { args }); // very detailed
action.log.debug('cache hit', { key, value }); // debugging info
action.log.info('order placed', { orderId, total }); // business events
action.log.warn('rate limit approaching', { current: 95, max: 100 }); // warnings
action.log.error('database connection failed', { error }); // errors
action.log.fatal('system out of memory'); // critical
```

## Error Messages

### User-Facing Messages

```typescript
// ✅ Good: Clear, actionable user messages
throw new ValidationError('Email address must be valid');
throw new ConflictError('Username already taken');

// ❌ Bad: Technical or vague messages
throw new Error('Invalid input');
throw new Error('Database constraint violation');
```

### Developer Messages

```typescript
// include technical details in logs, not error messages
if (!EMAIL_REGEX.test(email)) {
  action.log.debug('email validation failed', {
    email,
    pattern: EMAIL_REGEX.toString(),
  });
  throw new ValidationError('please enter a valid email address');
}
```

## Monitoring & Alerting

### Error Tracking

- Track error rates and types
- Monitor error spikes
- Set up alerts for critical errors
- Include error context in tracking

```typescript
// Example error tracking integration
function trackError(error: Error, context?: Record<string, unknown>): void {
  // Send to monitoring service
  if (window.Sentry) {
    window.Sentry.captureException(error, {
      extra: context,
    });
  }
}
```

### Performance Monitoring

```typescript
// log slow operations
export async function processLargeDataset(
  datasetId: string,
  action: Action,
): Promise<ProcessingResult> {
  const startTime = performance.now();

  action.log.info('starting dataset processing', { datasetId });

  try {
    const result = await performProcessing(datasetId);
    const duration = performance.now() - startTime;

    // log performance metrics
    action.log.info('dataset processing completed', {
      datasetId,
      duration: Math.round(duration),
      recordsProcessed: result.recordCount,
      throughput: Math.round(result.recordCount / (duration / 1000)),
    });

    // warn if slow
    if (duration > 5000) {
      action.log.warn('slow dataset processing', {
        datasetId,
        duration: Math.round(duration),
        threshold: 5000,
      });
    }

    return result;
  } catch (error) {
    const duration = performance.now() - startTime;
    action.log.error('dataset processing failed', {
      datasetId,
      duration: Math.round(duration),
      error,
    });
    throw error;
  }
}
```

## Best Practices

### 1. Fail Fast

- Validate inputs early
- Throw errors at the point of detection
- Don't propagate invalid states

### 2. Be Specific

- Use specific error types
- Include relevant context
- Provide actionable messages

### 3. Handle Gracefully

- Catch errors at appropriate boundaries
- Provide fallbacks where possible
- Don't swallow errors silently

### 4. Log Thoughtfully

- Log enough to debug issues
- Always attach relevant data in the log handler

--- END ---
