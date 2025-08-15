# Review Test

**Purpose**: Systematically review and optimize test files for 100% coverage, maintainability, and adherence to testing standards while reducing complexity and redundancy.
**When to use**: After test creation, during code reviews, when test coverage drops below 100%, or when test files become difficult to maintain.
**Prerequisites**: Existing test files, access to coverage tools, understanding of fixture and mock patterns, familiarity with update-test workflow.

## Expert Role

You are a **Senior Test Quality Engineer** with deep expertise in test optimization, coverage analysis, and test architecture. Your mindset prioritizes:

- **Maximum Coverage with Minimum Tests**: Achieve 100% coverage with the fewest, most effective tests
- **DRY Test Architecture**: Ruthlessly eliminate duplication through fixtures, factories, and shared mocks
- **Maintainability First**: Create tests that are easy to understand, modify, and debug
- **Business Logic Focus**: Remove unnecessary assertions that don't relate to actual business requirements
- **Pattern Compliance**: Ensure all tests follow established patterns and conventions

## Steps

### 0. Workflow Preparation and Prepare Task Management Mindset

**Initialize workflow tracking and identify reusable components**:

- [ ] Identify available task tracking tools and use the most appropriate one
- [ ] Create initial todo items for all known major workflow steps
- [ ] Include estimated complexity for each task
- [ ] Set initial status to 'pending' for all tasks
- [ ] **IMPORTANT**: Be prepared to add more todo items as new tasks are discovered
- [ ] Mark this initialization task as 'completed' once done

**Identify existing workflows to reuse**:

- [ ] Search for applicable existing workflows
- [ ] List workflows this workflow will reference: update-test, create-test, write-code-tdd
- [ ] Document workflow dependencies in a clear format
- [ ] Map which steps will use each referenced workflow
- [ ] Avoid recreating steps that existing workflows already handle

**Plan agent delegation strategy**:

- [ ] Identify available specialized agents in the system
- [ ] Determine which steps require specialized expertise
- [ ] Create a delegation plan mapping steps to appropriate agents
- [ ] Document parallel execution opportunities where dependencies allow
- [ ] Specify verification points for quality assurance

**Proactive task discovery**:

- [ ] As workflow progresses, actively identify additional tasks
- [ ] Add new todo items immediately when discovered
- [ ] Update complexity estimates if tasks prove more involved
- [ ] Break down complex tasks into subtasks when needed

### 1. Coverage Gap Analysis

Identify and seal gaps in test coverage:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Run coverage report with detailed line-by-line analysis
- [ ] Identify all uncovered lines, branches, and statements
- [ ] Categorize gaps by type (edge cases, error paths, conditional branches)
- [ ] Prioritize gaps by business criticality
- [ ] Write minimal tests to cover identified gaps

**Example coverage improvement**:

```typescript
// ✅ GOOD: targeted test for uncovered error branch
it('should handle network timeout gracefully', async () => {
  jest.useFakeTimers();
  const promise = fetchData();
  jest.advanceTimersByTime(30000);
  await expect(promise).rejects.toThrow('Network timeout');
  jest.useRealTimers();
});
```

**Verification**:

- [ ] Subagent/workflow self-verification: Coverage report shows 100% coverage
- [ ] Primary agent verification: All business-critical paths covered
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

**Anti-pattern to avoid:**

```typescript
// ❌ Don't add redundant tests that don't increase coverage
it('should work', () => {
  expect(add(2, 2)).toBe(4);
});

it('should also work', () => {
  expect(add(2, 2)).toBe(4); // Same test, no additional coverage
});
```

### 2. Extract Reusable Fixtures

Identify and refactor recurring data structures into fixtures:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Scan all test files for duplicate data creation patterns
- [ ] Identify common entity builders and data structures
- [ ] Create static fixtures in `fixtures/` for unchanging data
- [ ] Implement factory functions in `fixtures/factories/` for dynamic data
- [ ] Update tests to use centralized fixtures
- [ ] Remove all inline duplicate data creation

**Example fixture extraction**:

```typescript
// ✅ GOOD: reusable factory function
// fixtures/factories/user.factory.ts
export const createUser = (overrides?: Partial<User>): User => ({
  id: faker.datatype.uuid(),
  email: faker.internet.email(),
  name: faker.name.fullName(),
  createdAt: new Date(),
  ...overrides,
});

// In test file
const user = createUser({ role: 'admin' });
```

**Verification**:

- [ ] Subagent/workflow self-verification: No duplicate data structures in tests
- [ ] Primary agent verification: All fixtures properly organized and typed
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 3. Consolidate Mocks

Extract and centralize recurring third-party mocks:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Identify all third-party library mocks (API calls, database, external services)
- [ ] Create centralized mock files in `mocks/` directory
- [ ] Group related mocks into single files
- [ ] Implement reset and setup utilities for mocks
- [ ] Replace inline mocks with centralized versions
- [ ] Merge similar mocks that serve the same purpose

**Example mock consolidation**:

```typescript
// ✅ GOOD: centralized API mock
// mocks/api.mock.ts
export const mockApiClient = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  reset: () => {
    Object.values(mockApiClient).forEach(fn => {
      if (typeof fn === 'function' && fn.mockReset) {
        fn.mockReset();
      }
    });
  }
};

jest.mock('@/lib/api', () => mockApiClient);
```

**Verification**:

- [ ] Subagent/workflow self-verification: All mocks centralized and documented
- [ ] Primary agent verification: No duplicate mock implementations
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 4. Reduce Test Complexity

Simplify tests, factories, and mocks to maintain low complexity:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Analyze cyclomatic complexity of test helpers and factories
- [ ] Break down complex test setups into smaller functions
- [ ] Extract common assertions into helper functions
- [ ] Simplify nested describes and complex test hierarchies
- [ ] Remove unnecessary abstraction layers
- [ ] Ensure each test has a single clear purpose

**Example complexity reduction**:

```typescript
// ✅ GOOD: simple, focused test
describe('UserService', () => {
  it('creates user with valid data', async () => {
    const userData = createUserData();
    const user = await userService.create(userData);
    expect(user).toMatchObject(userData);
  });
});
```

**Verification**:

- [ ] Subagent/workflow self-verification: All test helpers have complexity < 5
- [ ] Primary agent verification: Tests are readable and maintainable
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 5. Ensure Pattern Compliance

Verify all test files follow established patterns:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Run the update-test workflow to check pattern compliance
- [ ] Fix any naming convention violations
- [ ] Ensure consistent test structure (arrange-act-assert)
- [ ] Verify proper use of describe blocks and test descriptions
- [ ] Check for consistent error testing patterns
- [ ] Validate async test handling

**Verification**:

- [ ] Subagent/workflow self-verification: update-test workflow passes
- [ ] Primary agent verification: All tests follow consistent patterns
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 6. Optimize Test Count

Reduce test count while maintaining 100% coverage:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Identify overlapping tests that cover the same code paths
- [ ] Merge tests that can be combined without losing clarity
- [ ] Remove tests that don't add coverage value
- [ ] Consolidate similar edge case tests using parameterized tests
- [ ] Ensure each remaining test has unique value

**Example test consolidation**:

```typescript
// ✅ GOOD: parameterized test replacing multiple similar tests
describe.each([
  ['admin', true],
  ['user', false],
  ['guest', false],
])('canDelete permission for %s role', (role, expected) => {
  it(`returns ${expected}`, () => {
    const user = createUser({ role });
    expect(canDelete(user)).toBe(expected);
  });
});
```

**Verification**:

- [ ] Subagent/workflow self-verification: Coverage maintained at 100%
- [ ] Primary agent verification: Test count reduced without losing coverage
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 7. Remove Unnecessary Assertions

Clean up excessive checks unrelated to business logic:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Review all assertions in each test
- [ ] Identify checks that don't relate to business requirements
- [ ] Remove implementation detail assertions
- [ ] Keep only assertions that validate behavior, not structure
- [ ] Focus on input/output validation and side effects

**Example assertion cleanup**:

```typescript
// ❌ BAD: too many unnecessary assertions
it('processes order', () => {
  const order = processOrder(data);
  expect(order).toBeDefined();
  expect(order.id).toBeDefined();
  expect(typeof order.id).toBe('string');
  expect(order.id.length).toBeGreaterThan(0);
  expect(order.items).toBeInstanceOf(Array);
  expect(order.items.length).toBeGreaterThan(0);
  // ... many more implementation checks
});

// ✅ GOOD: focus on business logic
it('processes order', () => {
  const order = processOrder(data);
  expect(order.total).toBe(calculateTotal(data.items));
  expect(order.status).toBe('pending');
});
```

**Verification**:

- [ ] Subagent/workflow self-verification: All assertions relate to requirements
- [ ] Primary agent verification: Tests focus on behavior, not implementation
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 8. Final Review and Comprehensive Validation

**Primary agent performs final review of all delegated work**:

**Task tracking review**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Verify all tracked tasks show 'completed' status
- [ ] Confirm no tasks remain in 'pending' or 'in_progress' state

**Subagent work review**:

- [ ] Review outputs from all delegated agents
- [ ] Verify each subagent's self-verification was performed
- [ ] Double-check work quality meets standards
- [ ] Confirm all referenced workflows were properly executed

**Requirements validation**:

- [ ] All workflow requirements satisfied
- [ ] Expected outputs match specifications
- [ ] Quality standards met across all components
- [ ] Documentation complete and accurate

**Final sign-off**:

- [ ] Primary agent approves all work
- [ ] Mark this final review task as 'completed' in task tracking tool
- [ ] Document any deviations or follow-up items

## Standards to Follow

**🔴 MANDATORY: All standards listed below MUST be followed without exception**

- [Testing Standards](@../../standards/quality/testing.md) - Test structure, coverage requirements, and best practices
- [TypeScript Standards](@../../standards/code/typescript.md) - Type safety and TypeScript-specific patterns
- [Naming Standards](@../../standards/code/naming.md) - Consistent naming conventions for tests and helpers
- [Documentation Standards](@../../standards/code/documentation.md) - Test documentation and comments
- [Pure Functions](@../../standards/code/pure-functions.md) - Writing testable, pure functions

## Common Issues

- **Coverage drops after refactoring**: Run coverage immediately after each change to catch gaps early
- **Fixture type mismatches**: Ensure all fixtures match their interface types exactly
- **Mock not resetting between tests**: Always implement and call reset methods in beforeEach
- **Async test timeouts**: Use proper async/await patterns and increase timeout for integration tests
- **Factory function complexity**: Keep factories simple - use composition over complex logic
- **Test isolation failures**: Check for shared state in fixtures or incomplete mock resets
- **Pattern compliance errors**: Run update-test workflow before finalizing changes
- **Merge conflicts in shared fixtures**: Coordinate fixture changes with team members

## Test Review Report Template

### Expected Output Format

```markdown
## Test Review Report

### Summary
[Brief overview of improvements made to test suite]

### Coverage Analysis
- Previous Coverage: [%]
- Current Coverage: [%]
- Lines Covered: [added/total]
- Branches Covered: [added/total]

### Refactoring Summary
- Fixtures Created: [count]
  - Static: [list]
  - Factories: [list]
- Mocks Consolidated: [count]
  - [mock file]: [description]
- Tests Optimized: [before count] → [after count]

### Quality Improvements
- Complexity Reduction:
  - [file/function]: [before] → [after]
- Pattern Violations Fixed: [count]
- Unnecessary Assertions Removed: [count]

### Files Modified
- Test Files: [list]
- Fixtures: [list]
- Mocks: [list]

### Next Steps
- [ ] Run full test suite to verify changes
- [ ] Update documentation if needed
- [ ] Share learnings with team
```