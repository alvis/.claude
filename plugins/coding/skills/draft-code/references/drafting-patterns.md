# Drafting Patterns

Canonical placeholder forms and skeleton examples for `coding:draft-code`.
These exact forms are the handoff contract: `coding:complete-code` claims only
the production markers below, and `coding:complete-test` claims only the test
placeholders below. Ambiguous plain `TODO:` markers are claimable by neither.

## Production markers

- Mark every incomplete code section with
  `// TODO(implementation): <explicit production behavior>` — state the exact
  behavior to implement, never a vague reminder.
- Where a value is expected (non-void return) or the body would otherwise be
  empty, throw the sentinel:

  ```typescript
  throw new Error('IMPLEMENTATION: <what is missing>, requiring <parameters as JSON object>');
  ```

  This satisfies the declared return type and avoids unused-variable
  complaints while keeping the stub loudly incomplete at runtime. Example:

  ```typescript
  throw new Error(
    `IMPLEMENTATION: user authentication logic needed, requiring ${JSON.stringify({ userId, token })}`,
  );
  ```

- Add `TODO(implementation):` comments for deferred validation logic inside
  type guards or constructors as well — types ship complete, behavior does not.

## Test placeholders

- Use `describe.todo()` / `it.todo()` only while no interface exists yet; they
  mark tests as pending without compile-time coupling and are completed later
  by `coding:complete-test`.
- As soon as an interface exists, write real test cases with assertions against
  it. The suite fails red until implementation lands — that is the desired TDD
  signal, not a defect.
- Structure suites as one describe block per behavior, prepared for the
  arrange-act-assert pattern, with planned cases covering all functionality.
- Draft supporting test utilities only as far as the scaffold needs: mock
  factories, fixture templates, and shared helpers.

## Examples

Draft a new service:

```bash
/draft-code "Create user authentication service with login, logout, and token refresh"
# Creates:
# - src/services/auth/types.ts (interfaces)
# - src/services/auth/auth.service.ts (stubs)
# - src/services/auth/auth.test.ts (test structure)
```

Draft an API endpoint:

```bash
/draft-code "REST endpoint for product CRUD operations"
# Creates skeleton for controller, service, and tests
```

Draft a utility module:

```bash
/draft-code "Date formatting utilities with timezone support"
# Creates type-safe utility functions with TODO(implementation) markers
```

Rejected — instruction too vague:

```bash
/draft-code "thing"
# Error: instruction too vague to derive types
# Suggestion: provide specific requirements like "Create validation helpers for user input"
```
