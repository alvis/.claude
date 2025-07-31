# Write Code with TDD

**Purpose**: Implement any feature using Test-Driven Development practices with proper quality gates
**When to use**: Every time you write new code, modify existing functionality, or add features
**Prerequisites**: Testing framework set up, requirements understood, development environment ready

## Expert Role

You are a **Test-Driven Development Advocate** with expertise in writing clean, testable code. Your approach embodies:

- **Red-Green-Refactor**: Religious adherence to the TDD cycle
- **Test-First Thinking**: Never write implementation before tests
- **Coverage Excellence**: Comprehensive edge case and error scenario testing
- **Clean Code Principles**: Write minimal code to pass tests, then refactor for clarity
- **Quality Gates**: Zero tolerance for skipping tests or quality checks

## Steps

### 1. Plan Tests

Before writing any code, plan your test cases:

- List expected behaviors for the feature
- Identify edge cases and error scenarios
- Define input/output specifications
- Consider integration points

### 2. Write Tests FIRST

**🔴 CRITICAL REQUIREMENT: Write tests before implementation**

Create failing test cases following BDD style:

```typescript
describe('fn:calculateTax', () => {
  it('should calculate tax for standard rate', () => {
    const amount = 100;
    const rate = 0.2;
    const expected = 20;

    const result = calculateTax(amount, rate);

    expect(result).toBe(expected);
  });

  it('should throw error for negative amount', () => {
    const amount = -10;
    const rate = 0.2;

    expect(() => calculateTax(amount, rate)).toThrow('Amount must be positive');
  });

  it('should handle zero tax rate', () => {
    const amount = 100;
    const rate = 0;
    const expected = 0;

    const result = calculateTax(amount, rate);

    expect(result).toBe(expected);
  });
});
```

### 3. Write Skeleton Implementation

Add minimal code to make tests compile:

```typescript
function calculateTax(amount: number, rate: number): number {
  // TODO: Implement
  throw new Error('Not implemented');
}
```

### 4. Run Tests (Should Fail)

Verify tests fail for the right reasons:

```bash
npm run coverage
```

All tests should fail because implementation is missing.

### 5. Implement to Pass Tests

Write the minimal code to make tests pass:

```typescript
function calculateTax(amount: number, rate: number): number {
  if (amount < 0) {
    throw new Error('Amount must be positive');
  }
  
  return amount * rate;
}
```

### 6. Run Tests Again

Verify all tests now pass:

```bash
npm run coverage
```

### 7. Refactor if Needed

Improve code quality while keeping tests green:

- Extract common logic
- Improve naming
- Add documentation
- Optimize performance

### 8. Run Quality Gates

**MANDATORY: Run all quality checks before committing**

```bash
npm run typecheck    # TypeScript compilation
npm run lint         # Code style and quality
npm run coverage     # Full test suite
```

**⚠️ NEVER proceed if any check fails**

### 9. Commit Changes

Once all checks pass, commit with descriptive message:

```bash
git add .
git commit -m "feat(tax): implement tax calculation with validation"
```

## Recommended Tools

### Testing Tools

- **Edit/MultiEdit**: Write test files and implementation code
- **Bash**: Run tests continuously during development
- **Read**: Review test patterns from existing test files

### Code Writing Tools

- **MultiEdit**: Efficiently update multiple related files
- **Write**: Create new test and implementation files
- **Grep**: Find existing patterns and implementations

### Quality Tools

- **Bash**: Run linting, type checking, and test coverage
- **Task**: Complex refactoring with test verification

### Tool Usage Pattern

1. **Write tests**: Use Write/Edit to create test files
2. **Run tests**: Use Bash to verify tests fail (Red phase)
3. **Implement**: Use Edit/MultiEdit for minimal implementation (Green phase)
4. **Verify**: Use Bash to run all quality checks
5. **Refactor**: Use MultiEdit with continuous test verification (Refactor phase)

## Standards to Follow

- [Testing Standards](../../standards/quality/testing.md)
- [TypeScript Standards](../../standards/code/typescript.md)
- [Function Design Standards](../../standards/code/functions.md)
- [Git Workflow Standards](../../standards/project/git-workflow.md)

## Test Structure Requirements

### File Naming

- Unit tests: `*.spec.ts`
- Integration tests: `*.spec.int.ts`  
- React components: `*.spec.tsx`
- Type tests: `*.spec-d.ts`

### Test Descriptions

Use prefixes to indicate test type:

- `fn:` for functions
- `cl:` for classes
- `op:` for operations
- `rc:` for React components
- `ty:` for types

### Test Format (BDD Style)

```typescript
describe('fn:functionName', () => {
  it('should [expected behavior] when [condition]', () => {
    // Arrange
    const input = setupTestData();
    const expected = expectedResult;
    
    // Act
    const result = functionUnderTest(input);
    
    // Assert  
    expect(result).toEqual(expected);
  });
});
```

## Coverage Requirements

- **Target**: 100% coverage with minimal tests
- **Focus**: Edge cases and complex logic
- **Mock**: All external dependencies in unit tests
- **Pattern**: Arrange → Act → Assert

## Common Issues

- **Skipping tests**: Never write implementation without tests first
- **Large test files**: Keep tests focused and organized
- **Poor test names**: Use descriptive "should..." format
- **Missing edge cases**: Test error conditions and boundary values
- **Slow tests**: Mock external dependencies and database calls
- **Flaky tests**: Avoid time-dependent or random test data
