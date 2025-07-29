# Testing Standards

## Testing Security

- **Use mocks for credentials** - Never use real credentials in tests
- **Private keys** - Allowed only inside unit test folders for testing purposes

## Testing (Vitest, BDD)

### Core Testing Principles

- **Always BDD**: All new code must include tests written in Behavior-Driven Development (BDD) style
- **Test Before Code**: Always write tests for expected behaviors before implementing code
- **Minimal Coverage**: Write the minimum number of tests needed to achieve 100% coverage
- **Efficient Testing**: Make each test as general as possible to cover multiple cases and scenarios

| Rule         | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| Coverage     | **100 %** (barrel files `/* v8 ignore start */` exempt)                   |
| File names   | `*.spec.ts` unit · `*.spec.int.ts` integration · `*.spec-d.ts` type tests |
| Prefixes     | `fn:` `op:` `cl:` `ty:` `rc:` (all lower‑case)                            |
| Descriptions | Lower‑case natural language describing expected behavior                  |
| Structure    | Arrange — Act — Assert (blank line between)                               |
| Vars         | Declare `expected` **before** `result`                                    |
| Assertions   | `toBe` primitives/identity, `toEqual` deep, inline `toThrow`              |
| Isolation    | Unit mocks all externals; integration may hit real DB/API                 |
| Mocks        | Framework resets mocks; **no `clearAllMocks` calls**                      |
| Types        | Never use `any` or `as any` casting                                       |
| Cleanup      | Use `beforeEach / afterEach` for non-mock setup/teardown only             |

**Note on barrel files**: Add `/* v8 ignore start */` at the top of any barrel files (typically index.ts) to exclude from coverage

### Test Efficiency Guidelines

When writing tests, prioritize efficiency and avoid over-testing:

- **Avoid redundant tests**: Don't write multiple tests that cover the same code paths
- **Combine related scenarios**: Use parameterized tests or single tests with multiple assertions when testing similar behaviors
- **Focus on edge cases**: Write comprehensive tests for boundary conditions, error cases, and complex logic
- **Maximize coverage per test**: Each test should exercise as much relevant code as possible while remaining focused

**Example of efficient vs inefficient testing:**

```typescript
// ❌ inefficient - multiple tests for similar cases
it('should handle user with id 1', () => {
  /* ... */
});
it('should handle user with id 2', () => {
  /* ... */
});
it('should handle user with id 999', () => {
  /* ... */
});

// ✅ efficient - single test covering the general case
it('should handle valid user id', () => {
  const result = getUserById(1);
  expect(result).toBeDefined();
});
```

### Test Structure & Organization

#### Basic Structure

- Structure each test into 3 sections with a blank line between each:
  - **Arrange**: Set up the test environment and inputs
  - **Act**: Execute the function or operation being tested
  - **Assert**: Verify the output or behavior against expected results
- For pure functions, use `result` and `expected` variables
- Declare `expected` value in the arrangement section (before `result`)

#### Section Organization

- **Long sections**: Break into logical subsections with blank lines for readability
- **Logical ordering**: Within each section, organize lines in the most readable way:
  - Group related setup steps together
  - Order setup from general to specific
  - Place variable declarations before their usage
- **Input/Expected variables**: In arrange section, separate with blank line:
  - Place setup code first
  - Add blank line
  - Then declare `input` and `expected` variables
- **Assert ordering**: Order from most detailed to least detailed:
  - Place assertions with more diagnostic value first (e.g., `toHaveBeenCalledWith({...})` before `toHaveBeenCalledTimes(1)`)
  - Group related assertions together

#### Comments

- **No structure comments**: Never use comments indicating test structure (`// arrange`, `// act`, `// assert`, or any variations)
- **Explanatory comments**: Use comments to explain complex or non-obvious steps:
  - When setup involves multiple related operations
  - When business logic requires context
  - When assertions test edge cases or specific behaviors
  - When the "why" behind a step is not immediately clear from code

### Test Descriptions

Write `it()` descriptions using BDD "should" style that clearly state expected behavior:

#### Guidelines

- Use exact type names (e.g., `PaymentAccount` not "payment account") for precision
- Be specific about expected behavior
- Focus on business value and outcomes

#### Examples

**Good:**

- `'should return user data when given a valid id'`
- `'should throw an error when given an invalid id'`
- `'should create a PaymentAccount with valid data'`
- `'should return a UserProfile object'`

**Avoid:**

- `'should work correctly'` ❌
- `'should handle edge cases'` ❌
- `'should work as expected'` ❌

### Mocking & Test Organization

#### Mocking Guidelines

- Use `mock` to control upstream behavior when needed
- Integration tests: Ensure all necessary credentials are supplied
- Use type-safe mocking pattern:

```typescript
const { functionName } = vi.hoisted(() => ({
  functionName: vi.fn(),
}));

vi.mock(
  '#module/path',
  () =>
    ({
      functionName,
    }) satisfies Partial<typeof import('#module/path')>,
);
```

#### File Organization

**Standard Pattern:** One-to-one mapping from source to spec folder

```plaintext
packages/cache/
├── source/
│   ├── adapters/
│   │   ├── disabled.ts
│   │   └── memory.ts
│   └── client.ts
└── spec/
    ├── adapters/
    │   ├── disabled.spec.ts
    │   └── memory.spec.ts
    └── client.spec.ts
```

**Data Services Pattern (data/\*):** Integration tests with shared utilities

```plaintext
data/billing/
├── source/
│   ├── operations/
│   │   └── getPaymentAccount.ts
│   └── types/
└── spec/
    ├── common.ts              # Shared test instances
    ├── fixture.ts             # Test data fixtures
    └── operations/
        └── getPaymentAccount.spec.int.ts
```

#### Test Data Management (Data Services Only)

```typescript
// common.ts - shared test setup
import { env } from '@theriety/utilities';

import { Import } from '#index';
import { PrismaClient } from '#prisma';

export const instance = new Import({
  type: 'postgres',
  url: env('POSTGRES_URL_FOR_SCHEMA_MUTATION'),
});

export const prisma = new PrismaClient({
  datasourceUrl: env('POSTGRES_URL_FOR_SCHEMA_MUTATION'),
});

// fixture.ts - database fixtures
export default async function setup() {
  await prisma.user.deleteMany();
  await prisma.user.create({
    data: {
      /* ... */
    },
  });
}
```

### Example Test Structure

```ts
import { describe, it, expect } from 'vitest';

describe('fn:fetchUserProfile', () => {
  it('should return user data when given a valid id', () => {
    const expected = {
      /* … */
    };

    const result = fetchUserProfile('123');

    expect(result).toEqual(expected);
  });

  it('should throw an error when given an invalid id', () => {
    expect(() => fetchUserProfile('bad')).toThrow();
  });
});
```

### Running Tests

```bash
# Run tests for multiple specific files
pnpm --filter <project-name> test -- --coverage [path/to/file.spec.ts] [path/to/another.spec.ts] ...
```

### Vitest Utility Matchers

Vitest provides utility matchers that are shortcuts for common `expect.asymmetricMatcher()` patterns:

#### Object and Array Utilities

```ts
// instead of: expect(obj).toEqual(expect.objectContaining({ name: 'John' }))
expect(obj).toMatchObject({ name: 'John' });

// instead of: expect(arr).toEqual(expect.arrayContaining(['apple']))
expect(arr).toContain('apple');
expect(arr).toContainEqual({ fruit: 'apple', count: 5 }); // deep equality

// property checking
expect(obj).toHaveProperty('user.name');
expect(obj).toHaveProperty('user.name', 'John'); // with value check

// length checking
expect(arr).toHaveLength(3);
expect(str).toHaveLength(10);
```

#### String Utilities

```ts
// instead of: expect(obj).toEqual({ msg: expect.stringContaining('error') })
expect(str).toMatch(/error/); // regex or substring
expect(str).toMatch('error'); // substring
```

#### Comparison Utilities

```ts
// numeric comparisons
expect(value).toBeGreaterThan(10);
expect(value).toBeGreaterThanOrEqual(10);
expect(value).toBeLessThan(20);
expect(value).toBeLessThanOrEqual(20);

// set membership
expect(fruit).toBeOneOf(['apple', 'banana', 'orange']);
```

#### Type and Instance Utilities

```ts
// type checking
expect(value).toBeTypeOf('string'); // 'string', 'number', 'object', etc.
expect(instance).toBeInstanceOf(MyClass);

// strict equality vs deep equality
expect(obj1).toBe(obj2); // reference equality (Object.is)
expect(obj1).toEqual(obj2); // deep structural equality
expect(obj1).toStrictEqual(obj2); // strict deep equality (considers undefined props, sparseness)
```

**Prefer these utility matchers over asymmetric matchers when available** - they're more readable and provide better error messages.

### Type Testing (\*.spec-d.ts)

Type testing ensures TypeScript type correctness using `expectTypeOf` from Vitest:

#### Type Testing Conventions

- **File extension**: Use `*.spec-d.ts` for type-only tests
- **Test prefix**: Use `ty:` prefix for type tests (e.g., `describe('ty:MyType', () => ...)`)
- **Variable naming**:
  - Use `PascalCase` for type variables: `ExpectedType`, `ResultType`, `InputType`
  - Follow normal naming for runtime variables: `expected`, `result`
- **Import pattern**: Import `expectTypeOf` from `vitest`
- **Test structure**: Follow same BDD structure as runtime tests

#### Type Testing Patterns

```ts
import { describe, expectTypeOf, it } from 'vitest';
import type { MyUtilityType } from '#types';

describe('ty:MyUtilityType', () => {
  it('should transform input type correctly', () => {
    type InputType = { foo: string; bar: number };
    type ExpectedType = { foo: string };
    type ResultType = MyUtilityType<InputType>;

    expectTypeOf<ResultType>().toEqualTypeOf<ExpectedType>();
  });

  it('should handle edge cases', () => {
    type ExpectedType = never;
    type ResultType = MyUtilityType<{}>;

    expectTypeOf<ResultType>().toEqualTypeOf<ExpectedType>();
  });
});
```

#### Common Type Test Assertions

- `expectTypeOf<T>().toEqualTypeOf<U>()` - Exact type equality (strictest)
- `expectTypeOf<T>().toExtend<U>()` - Type inheritance/"is-a" relationships (T extends U)
- `expectTypeOf<T>().toMatchObjectType<U>()` - Object structural compatibility (checks if T has at least the structure of U)
- `expectTypeOf<T>().not.toEqualTypeOf<U>()` - Type inequality
- `expectTypeOf(value).toEqualTypeOf<Type>()` - Runtime value type checking

**Note**: `toMatchTypeOf` is deprecated. Use `toMatchObjectType` for object type subset checking or `toExtend` for inheritance relationships.

#### Complex Type Testing

For complex types with multiple parameters or conditional types:

```ts
describe('ty:ServiceAgent', () => {
  it('should create correct dispatcher types for sync operations', () => {
    type ResultType = ServiceAgent<false, typeof peer>;
    type ExpectedType = {
      standalone: {
        operation: (payload: string) => Promise<{ result: string }>;
      };
    };

    expectTypeOf<ResultType>().toEqualTypeOf<ExpectedType>();

    // test specific method signatures
    expectTypeOf<ResultType['standalone']['operation']>().toEqualTypeOf<
      ExpectedType['standalone']['operation']
    >();
  });
});
```

## Coverage Fixing Workflow

### Overview

The goal is to achieve 100% code coverage (excluding barrel files marked with `/* v8 ignore start */`).

### Step 1: Run Coverage Tests

Navigate to the specific package directory and run:

```bash
pnpm run coverage
```

### Step 2: Identify Uncovered Lines

Use this command to extract all uncovered lines from the coverage report:

```bash
jq -r --arg pwd "$(pwd)" 'to_entries[] | select(.value.s | to_entries | map(select(.value == 0)) | length > 0) | .key as $file | .value.s | to_entries | map(select(.value == 0) | .key) | ($file | sub($pwd + "/"; "")) + ": " + join(", ")' coverage/coverage-final.json
```

This command will output uncovered lines in the format:

```plaintext
path/to/file.ts: 12, 44, 61
path/to/another.ts: 9, 21
```

### Step 3: Fix Coverage Incrementally

1. **Start from the bottom**: Use `tail` to get the last few files:

   ```bash
   jq -r --arg pwd "$(pwd)" 'to_entries[] | select(.value.s | to_entries | map(select(.value == 0)) | length > 0) | .key as $file | .value.s | to_entries | map(select(.value == 0) | .key) | ($file | sub($pwd + "/"; "")) + ": " + join(", ")' coverage/coverage-final.json | tail -5
   ```

2. **Fix one file at a time**: Starting with the simplest files first
3. **Re-run coverage**: After fixing each file, run `pnpm run coverage` again
4. **Repeat**: Continue until no uncovered lines remain

### Common Coverage Gaps

Common uncovered code patterns include:

- Error handling branches and throw statements
- Type guards and validation checks
- Catch blocks in try-catch statements
- Default parameter values
- Early returns and edge cases

### Quick Reference Commands

```bash
# run coverage for a specific package
pnpm --filter <package-name> run coverage

# get all uncovered lines
jq -r --arg pwd "$(pwd)" 'to_entries[] | select(.value.s | to_entries | map(select(.value == 0)) | length > 0) | .key as $file | .value.s | to_entries | map(select(.value == 0) | .key) | ($file | sub($pwd + "/"; "")) + ": " + join(", ")' coverage/coverage-final.json

# get last 5 files with uncovered lines
jq -r --arg pwd "$(pwd)" 'to_entries[] | select(.value.s | to_entries | map(select(.value == 0)) | length > 0) | .key as $file | .value.s | to_entries | map(select(.value == 0) | .key) | ($file | sub($pwd + "/"; "")) + ": " + join(", ")' coverage/coverage-final.json | tail -5

# count total uncovered statements
jq '[.[] | .s | to_entries[] | select(.value == 0)] | length' coverage/coverage-final.json
```

--- END ---
