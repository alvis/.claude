# Development Best Practices

## Core Principles

- **Single responsibility** - Keep functions focused; break up any function longer than 60 lines
- **DRY (Don't Repeat Yourself)** - Reuse logic or components from packages/ when possible
- **Follow established patterns** - Match existing code style, structure, and templates
- **Test-driven mindset** - Write tests (or stubs) alongside code as you develop

## Security Requirements

- **Never commit secrets** - Keep all credentials and sensitive data out of the codebase
- **Environment variables** - Always provide `.env.example` with all consumed keys
- **Secret management** - Use only approved secret managers in production
- **No silent errors** - Use `@theriety/error` classes for explicit error handling

## Following established patterns

When making changes to files, first understand the file's code conventions:

- **Never assume libraries are available** - Check neighboring files or package.json
- **Mimic existing code style** - Use existing libraries, utilities, and patterns
- **Check before using** - Look at:
  - Neighboring files for patterns
  - package.json (or cargo.toml, etc.) for dependencies
  - Existing components before creating new ones
  - Code's imports to understand framework choices
- **Follow established patterns** - Match existing code style, structure, and templates
- **Reuse existing code** - Prefer reusing logic or components from packages/ when possible

## Code Patterns

### Pure Functions

- Prefer pure functions whenever possible:
  - No modification of external state
  - No side effects
  - No reliance on external state
  - Always return the same output for the same input
- Non-pure functions allowed only when side effects are required:
  - Updating global or application state
  - Caching or memoization
  - Registering event handlers or subscriptions

### Immutability

- Use `const` by default; avoid reassigning variables
- Favor immutable operations (`...`, `map`, `filter`, etc.)
- Never mutate function parameters - return new objects instead
- Local mutation acceptable within function scope for performance

### Functional Programming

- **Prefer functional programming patterns** for all code unless performance requires otherwise:
  - Use `map`, `filter`, `reduce` instead of imperative loops
  - Use method chaining for data transformations
  - Avoid `for` loops except when dealing with very high iterations (hundreds per request)
- **Always use functional programming** in setup scripts and initialization code
- **Acceptable imperative patterns** only when:
  - Processing arrays with hundreds of items per request
  - Performance profiling shows functional approach causes bottlenecks
  - Working with external APIs that require imperative patterns
- Example transformations:
  ```typescript
  // ✅ Preferred functional approach
  const results = items
    .filter(item => item.isActive)
    .map(item => ({ id: item.id, name: item.name }));
  
  // ❌ Avoid imperative approach (unless performance critical)
  const results = [];
  for (let i = 0; i < items.length; i++) {
    if (items[i].isActive) {
      results.push({ id: items[i].id, name: items[i].name });
    }
  }
  ```

### Text Generation

- For multi-line text, use array joining:

  ```typescript
  const lines = [
    'First line',
    'Second line',
    condition && 'Optional line',
  ].filter(Boolean);
  return lines.join('\n');
  ```

## Required checks before submitting

- Run tests and linters on all added/changed files
- Check README or search codebase for test commands if unclear
- Run lint and typecheck commands (e.g., `npm run lint`, `npm run typecheck`)
- These checks may be skipped **only** when modifying comments or documentation

## Established Code Patterns

For service-specific patterns (operation implementation, configuration schemas, type exports), see `10-service-design-patterns.md`.

## Quality Checks

- Run tests: `pnpm --filter <project> test -- --coverage`
- Run linters: `pnpm --filter <project> lint`
- Run typecheck: `npm run typecheck` (if available)
- These checks may be skipped **only** when modifying comments or documentation

--- END ---
