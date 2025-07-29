# Error Handling & Logging

## Table of Contents

- [Error Handling](#error_handling) `error_handling`
- [Transactional Logger](#logging) `logging`
- [What to Log](#what_to_log) `what_to_log`
- [Best Practices](#best_practices) `best_practices`

<error_handling>

## Use @theriety/error Classes

```typescript
// ✅ GOOD: Specific error classes
import { MissingDataError, ValidationError } from '@theriety/error';

if (!user) {
  throw new MissingDataError('user profile not found');
}

// ❌ BAD: Generic errors
throw new Error('User not found');
```

## Error Handling Pattern

```typescript
export async function getUserProfile(userId: string, action: Action) {
  try {
    action.log.info('fetching user profile', { userId });
    
    const user = await prisma.user.findUnique({ where: { id: userId } });
    
    if (!user) {
      throw new MissingDataError('user not found');
    }
    
    return user;
  } catch (error) {
    if (error instanceof MissingDataError) {
      action.log.warn('user not found', { userId });
      return null;
    }
    
    action.log.error('unexpected error', { userId, error });
    throw error;
  }
}
```

## Rules

* Throw early when detecting invalid states
* Use specific error classes for different scenarios
* Handle errors explicitly at boundaries
* NEVER swallow errors silently

</error_handling>

<logging>

## CRITICAL: Use Transactional Logger

```typescript
// ✅ CORRECT: Use action.log
export async function processOrder(orderId: string, action: Action) {
  action.log.info('processing order', { orderId });
}

// ❌ WRONG: Never use console
console.log('This is wrong');
```

## Log Levels

* **FATAL** - System critical errors
* **ERROR** - Unrecoverable operation errors
* **WARN** - Recoverable issues
* **INFO** - Business events
* **DEBUG** - Debugging details
* **TRACE** - Very detailed (rare)

## Structured Logging

```typescript
// ✅ GOOD: Structured with context
action.log.error('payment failed', {
  userId,
  orderId,
  amount: order.total,
  error: error.message,
  gateway: 'stripe'
});

// ❌ BAD: String concatenation
action.log.error('Error: ' + error.message);
```

</logging>

<what_to_log>

## Always Log

* Auth failures
* Validation errors
* External service failures
* Unhandled exceptions
* Performance warnings

## NEVER Log

* Passwords or tokens
* PII (Personal Identifiable Info)
* Credit card numbers
* API keys or secrets
* Full request bodies with sensitive data

</what_to_log>

<best_practices>

## Error Messages

```typescript
// User-facing: Clear and actionable
throw new ValidationError('Email address must be valid');

// Developer details in logs only
action.log.debug('email validation failed', {
  email,
  pattern: EMAIL_REGEX.toString()
});
```

## Performance Monitoring

```typescript
const startTime = performance.now();

try {
  const result = await processData();
  const duration = performance.now() - startTime;
  
  if (duration > 5000) {
    action.log.warn('slow processing', { duration, threshold: 5000 });
  }
  
  return result;
} catch (error) {
  action.log.error('processing failed', { error });
  throw error;
}
```

</best_practices>
