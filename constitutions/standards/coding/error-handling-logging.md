# Error Handling & Logging

<error_handling>

## Use Specific Error Classes

```typescript
// ✅ GOOD: specific error classes
import { MissingDataError } from '@theriety/error';

class ValidationError extends Error { ... }

if (!user) {
  throw new MissingDataError('User not found');
}

// ❌ BAD: generic errors
throw new Error('User not found');
```

## Rules

- Throw early when detecting invalid states
- Use specific error classes for different scenarios
- Handle errors explicitly at boundaries
- NEVER swallow errors silently

</error_handling>

<logging>

## CRITICAL: Use Transactional Logger

```typescript
// ✅ GOOD: Use action.log
export async function processOrder(orderId: string, action: Action) {
  action.log.info("Processing order", { orderId });
}

// ❌ BAD: Never use console
console.log("This is wrong");
```

</logging>

<message_formatting>

## Message Formatting Rules

### 1. Start with Action Verb

- ✅ GOOD: "Processing payment", "Validating user input", "Connecting to database"
- ❌ BAD: "Payment", "User", "Database"

### 2. Be Specific but Concise

- ✅ GOOD: "Failed to parse JSON response from payment gateway"
- ❌ BAD: "Error" or overly verbose messages

### 3. Use Consistent Terminology

- Always use "user" (not sometimes "customer", "client", "account")
- Always use "order" (not sometimes "purchase", "transaction")

### 4. Include Outcome for Completion

- ✅ GOOD: "Order processed successfully", "Authentication failed: invalid token"
- ❌ BAD: "Order processed", "Authentication complete"

### 5. Avoid Redundancy

- ✅ GOOD: message: "User login successful", meta: { userId: "123" }
- ❌ BAD: message: "User 123 login successful", meta: { userId: "123" }

</message_formatting>

<log_levels>

## Log Levels

**TRACE** - Conceptual level for automatic instrumentation

- Used only in createTracer() for ultra-verbose automatic instrumentation
- Manual TRACE logs not recommended - use DEBUG instead

**DEBUG** - Verbose diagnostic information

- Development only (disabled in production)
- Function inputs/outputs, SQL queries, API response bodies
- Detailed execution flow, variable values, internal state

**INFO** - High-level application events

- All environments
- Service lifecycle events, major milestones, user-initiated actions
- Normal, significant operations

**WARN** - Recoverable issues needing attention

- All environments
- Performance degradation, fallback behavior, retry attempts
- Unusual situations that don't prevent execution

**ERROR** - Failures requiring investigation

- All environments (triggers alerts)
- Caught exceptions, failed operations, broken functionality
- Business rule violations that stop processing

**FATAL** - Critical failures requiring immediate shutdown

- All environments (triggers critical alerts, then process exits)
- Unrecoverable errors preventing application function
- Missing critical configuration, corrupted state

</log_levels>

<structured_logging>

## Structured Logging

```typescript
// ✅ GOOD: structured with context
action.log.error("Payment failed", {
  userId,
  orderId,
  amount: order.total,
  error: error.message,
  gateway: "stripe",
});

// ❌ BAD: string concatenation
action.log.error("Error: " + error.message);
```

## User Actions

```typescript
// ✅ GOOD - structured with context, no PII
action.log.info('User login successful', {
  operation: 'auth:login',
  meta: {
    userId: user.id,
    loginMethod: 'oauth',
    provider: 'google'
  }
});

// ❌ BAD - no context, includes PII
console.log(`User ${user.email} logged in`);
```

## Performance Logging

```typescript
// ✅ GOOD - conditional logging with context
const startTime = Date.now();
const result = await slowOperation();
const duration = Date.now() - startTime;

if (duration > PERFORMANCE_THRESHOLD) {
  action.log.warn('Slow operation detected', {
    operation: 'data:processing',
    meta: {
      duration,
      threshold: PERFORMANCE_THRESHOLD,
      recordCount: result.length
    }
  });
}

// ❌ BAD - no threshold, always logs
const startTime = Date.now();
const result = await slowOperation();
console.log(`Operation took ${Date.now() - startTime}ms`);
```

</structured_logging>

<what_to_log>

## Always Log

- Auth failures
- Validation errors
- External service failures
- Unhandled exceptions
- Performance warnings
- Business rule violations
- Critical state changes

## NEVER Log

- Passwords or tokens
- PII (Personal Identifiable Info)
- Credit card numbers
- API keys or secrets
- Full request bodies with sensitive data
- User email addresses in messages (use userId instead)

</what_to_log>

<best_practices>

## Error Messages

```typescript
// ✅ GOOD: user-facing - clear and actionable
throw new ValidationError("Email address must be valid");

// ✅ GOOD: developer details in logs only
action.log.debug("Email validation failed", {
  email,
  pattern: EMAIL_REGEX.toString(),
});
```

## Performance Monitoring

```typescript
const startTime = performance.now();

try {
  const result = await processData();
  const duration = performance.now() - startTime;

  if (duration > 5000) {
    action.log.warn("Slow processing detected", { 
      duration, 
      threshold: 5000 
    });
  }

  return result;
} catch (error) {
  action.log.error("Processing failed", { 
    error: error.message,
    duration: performance.now() - startTime 
  });
  throw error;
}
```

## Context Preservation

```typescript
// ✅ GOOD: preserve error context
try {
  await riskyOperation();
} catch (originalError) {
  const contextualError = new ProcessingError(
    "Failed to process user data",
    { cause: originalError }
  );
  action.log.error("Processing failed", {
    error: contextualError.message,
    originalError: originalError.message,
    stack: originalError.stack
  });
  throw contextualError;
}
```

</best_practices>
