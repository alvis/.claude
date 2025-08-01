# Comment Standards

_Standards for code comments, documentation, and inline explanations_

## Core Comment Principles

### When to Write Comments

Write comments that explain **"why"**, not **"what"**:

- **Purpose or reasoning** that isn't immediately obvious
- **Workarounds** for external constraints or legacy issues
- **Intentional deviations** from best practices
- **Public API documentation** - parameters, return values, side effects
- **Complex algorithms** needing explanation
- **Business logic** that isn't self-evident
- **Temporary solutions** with context

### Comment Casing Rules

**Always use lowercase** for comments that are sentences or phrases:

```typescript
// ✅ Good: Lowercase comments
// this function handles user authentication
// api calls require authentication token
// check if user exists before proceeding

// ❌ Bad: Uppercase comments
// This function handles user authentication
// API calls require authentication token
// Check if user exists before proceeding
```

**Use uppercase only** when referencing code elements:

```typescript
// ✅ Good: Uppercase for code references
// the UserService handles authentication
// call the API with proper headers
// Layout components should be memoized

// ❌ Bad: Lowercase for code references
// the userservice handles authentication
// call the api with proper headers
// layout components should be memoized
```

## Comment Tags

Use comment tags to indicate the purpose of comments:

### Temporary Tags (Never Commit)

These tags indicate issues that must be resolved before committing:

```typescript
// TODO: implement error handling for network failures
// FIXME: this calculation is incorrect for edge cases
// DEBUG: console.log for debugging - remove before commit
// TEMP: stub implementation - replace with real logic
// QUESTION: should we validate email format here?
// IDEA: could optimize this with memoization
// INTENT: clarifies why something is implemented this way
```

### Review Tags (Remove Before Merge)

For draft PRs only - remove before merging:

```typescript
// REVIEW: need second opinion on this approach
// REFACTOR: this code needs restructuring
// OPTIMIZE: performance could be improved here
```

### Documentation Tags (Can Remain)

These can stay in production code:

```typescript
// HACK: workaround for library bug - remove when fixed
// WORKAROUND: bypass issue with third-party API
// NOTE: important context or non-obvious explanation
// WARNING: alerts about potential risks or edge cases
// PERFORMANCE: highlights optimization opportunities
// SECURITY: documents security implications
// COMPATIBILITY: handles browser/platform specific issues
// LIMITATION: documents known limitation
```

### Tag Formatting

For multi-line content, start tag on its own line:

```typescript
// ✅ Good: Single-line format
// NOTE: skip root tsconfig to avoid circular refs

// ✅ Good: Multi-line format
// NOTE:
// lockfile stored in workspace root only
// when shared-workspace-lockfile=true

// WARNING:
// this mutation is intentional for performance
// do not refactor to immutable without benchmarking
```

## JSDoc Standards

### Function Documentation

```typescript
/**
 * validates user input and returns formatted data
 * @param input raw user data from form submission
 * @returns validated and formatted user object
 * @throws ValidationError if required fields are missing
 * @throws FormatError if email format is invalid
 */
function validateUserInput(input: unknown): User {
  // implementation
}
```

### JSDoc Rules

- **Begin with third-person singular verb** (e.g., "validates" not "validate")
- **Write all JSDoc in lowercase**
- **Omit hyphens** in @param tags
- **Exclude TypeScript types** from JSDoc (they're in the code)
- **No periods** at the end of JSDoc comments
- **List all @throws** with conditions

### Single vs Multi-line JSDoc

```typescript
// ✅ Preferred: Single-line for simple descriptions
/** handles user logout and clears session data */
function logout(): void {}

// ✅ Good: Multi-line for complex documentation
/**
 * processes payment with retry logic
 * @param payment payment details including amount and method
 * @param options processing options like retry count
 * @returns payment confirmation or failure details
 * @throws PaymentError if payment gateway rejects
 * @throws NetworkError if connection fails
 */
async function processPayment(
  payment: Payment,
  options?: PaymentOptions,
): Promise<PaymentResult> {}

// ❌ Avoid: Multi-line when single-line suffices
/**
 * gets user by id
 */
function getUser(id: string): User {}
```

## Interface Documentation

Document all interface fields with JSDoc:

```typescript
/** represents a product in the catalog */
interface Product {
  // metadata //
  /** unique identifier */
  id: string;
  /** creation timestamp */
  createdAt: Date;

  // details //
  /** product display name */
  name: string;
  /** price in cents */
  price: number;
  /** markdown description */
  description: string;

  // inventory //
  /** current stock level */
  quantity: number;
  /** minimum stock before reorder */
  reorderPoint: number;
}
```

## Code Explanation Comments

### Good Comments

Explain the **why**, not the **what**:

```typescript
// ✅ Good: Explains reasoning
// use Map for O(1) lookup performance with large datasets
const userIndex = new Map<string, User>();

// ✅ Good: Explains workaround
// setTimeout with 0ms to push to next tick and avoid race condition
setTimeout(() => updateUI(), 0);

// ✅ Good: Explains business logic
// customers get 20% discount after 3rd purchase in same month
const discount = purchases.length > 3 ? 0.2 : 0;

// ✅ Good: Explains deviation
// using any here because third-party library has incorrect types
const result = externalLib.process(data as any);
```

### Bad Comments

Avoid redundant or obvious comments:

```typescript
// ❌ Bad: Restates the obvious
// increment counter by 1
counter++;

// ❌ Bad: Explains what instead of why
// loop through users array
users.forEach((user) => {});

// ❌ Bad: Redundant with clear code
// return true if user is active
return user.isActive;
```

## Comment Maintenance

### Keep Comments Updated

```typescript
// ❌ Bad: Outdated comment
// calculate 15% tax (old rate)
const tax = amount * 0.18; // actual rate

// ✅ Good: Updated comment
// calculate 18% tax (updated Jan 2024)
const tax = amount * 0.18;
```

### Remove Dead Comments

```typescript
// ❌ Bad: Commented-out code
// const oldLogic = true;
// if (oldLogic) {
//   processLegacy();
// }

// ✅ Good: Clean code without dead comments
// legacy processing removed in v2.0 - see PR #123
```

## Best Practices

### Comment Density

- **Minimize comments** by writing self-explanatory code
- **Strategic placement** - comment complex sections, not every line
- **Quality over quantity** - few meaningful comments beat many obvious ones

### Comment Style

- **Concise and clear** - get to the point quickly
- **Professional tone** - avoid humor or personal notes
- **Actionable** - comments should help the next developer

### Examples

```typescript
// ✅ Good: Explains complex regex
// matches email with optional '+' addressing (e.g., user+tag@example.com)
const emailRegex = /^[^\s@]+(\+[^\s@]+)?@[^\s@]+\.[^\s@]+$/;

// ✅ Good: Documents assumption
// assume UTC timezone since user timezone not provided
const date = new Date(timestamp);

// ✅ Good: Explains performance choice
// pre-sort for binary search efficiency on repeated lookups
const sortedData = data.sort((a, b) => a.id - b.id);

// ✅ Good: Security note
// sanitize to prevent XSS - never trust user input
const safe = sanitizeHtml(userContent);
```

## Anti-Patterns

Avoid these common mistakes:

```typescript
// ❌ Bad: Noise comments
/**
 * Constructor
 */
constructor() { }

// ❌ Bad: Version history (use git)
// Modified by John on 2024-01-15
// Fixed bug #123

// ❌ Bad: Obvious comments
// return the result
return result;

// ❌ Bad: Commented code for "just in case"
// Might need this later
// function oldImplementation() { }

// ❌ Bad: Personal notes
// I think this could be better but deadline is tight

// ❌ Bad: Excessive punctuation
// WARNING!!!! DO NOT CHANGE THIS!!!!!
```
