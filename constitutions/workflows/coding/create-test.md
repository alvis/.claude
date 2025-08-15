# Create Test

**Purpose**: Generate comprehensive test structures for specified code areas to achieve 100% branch coverage following TDD principles
**When to use**: When you need to create test structures for untested code, improve coverage, or establish testing patterns before implementation
**Prerequisites**: TypeScript/JavaScript codebase, testing framework configured (Vitest), understanding of existing test patterns

## Expert Role

You are a **Test Architecture Specialist** with deep expertise in test-driven development and coverage optimization. Your mindset prioritizes:

- **Coverage Excellence**: Achieving 100% branch coverage with minimal, effective tests
- **Fixture Reusability**: Maximizing reuse of test doubles, fixtures, and mocks across the test suite
- **Type Safety**: Leveraging TypeScript's `satisfies` operator for compile-time fixture validation
- **TDD Philosophy**: Creating test structures that guide implementation design
- **Pattern Recognition**: Identifying common testing patterns to reduce duplication

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
- [ ] List workflows this workflow will reference
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

### 1. Context Analysis and Coverage Discovery

Analyze the target area and identify testing gaps:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Parse command input to determine scope (specific area or entire codebase)
- [ ] **OPEN Testing Standards**: Keep [Testing Standards](@../../standards/quality/testing.md) document open for reference
- [ ] Scan target files/directories for existing test coverage
- [ ] Ignore files that are marked to ignore (v8 ignore patterns)
- [ ] **VERIFY against Testing Standards**: Check existing tests comply with Testing Standards patterns
- [ ] Identify all functions, classes, and methods requiring tests per Testing Standards prefixes
- [ ] Map out all code branches and decision points for 100% coverage requirement
- [ ] **COMPLIANCE CHECK**: Analyze existing test files against Testing Standards patterns
- [ ] Locate and catalog existing test fixtures, mocks, and stubs per Testing Standards organization
- [ ] [[IMPORTANT] Carefully analyze the code and test files and identify any uncovered code]
- [ ] Document complex logic requiring special test attention with Testing Standards approach

**Verification**:

- [ ] Subagent/workflow self-verification: Coverage map generated with all branches identified
- [ ] Primary agent verification: All testable units cataloged
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

**Anti-pattern to avoid:**

- ❌ Create tests for a file marked to ignore
- ❌ Don't create tests without understanding existing patterns
- ❌ Creating inconsistent test structures that don't align with project standards

### 2. Fixture Analysis and Optimization

Analyze and optimize existing test fixtures for maximum reuse:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] **REVIEW Testing Standards**: Study [Testing Standards - Test Double Organization](@../../standards/quality/testing.md#test-double-organization)
- [ ] **VERIFY**: Inventory existing fixtures against Testing Standards organization (spec/mocks, spec/fixtures)
- [ ] **COMPLIANCE CHECK**: Identify fixtures not using satisfies operator per Testing Standards
- [ ] Plan fixture generalization following Testing Standards factory patterns
- [ ] Create fixture reuse matrix per Testing Standards consolidation guidelines
- [ ] **VALIDATE**: Design new fixtures using satisfies operator as required by Testing Standards
- [ ] Document fixture patterns following Testing Standards builder and factory patterns
- [ ] Map fixtures to test scenarios per Testing Standards approach

**Verification**:

- [ ] Subagent/workflow self-verification: Fixture optimization plan complete
- [ ] Primary agent verification: All reuse opportunities identified
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 3. Test Structure Generation

Generate comprehensive test structures for all identified gaps:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] **BEFORE Generating**: Read entire [Testing Standards](@../../standards/quality/testing.md) and follow any sub-standards
- [ ] **BEFORE Generating**: Read entire [TypeScript Standards](@../../standards/code/typescript.md) and follow any sub-standards
- [ ] Create test file structure following Testing Standards naming conventions (`.spec.ts`, `.int.spec.ts`)
- [ ] **VALIDATE**: Generate describe blocks with Testing Standards prefixes (fn:, cl:, op:, rc:, sv:, rp:, hk:, ty:)
- [ ] **CONFIRM**: Create test cases following BDD style ("should [behavior]") per Testing Standards
- [ ] **CHECK**: Structure tests using AAA pattern with proper spacing per Testing Standards
- [ ] Include edge cases and error handling for 100% coverage per Testing Standards
- [ ] **VERIFY**: Generate mocks using vi.hoisted pattern per Testing Standards
- [ ] **VALIDATE**: All fixtures use satisfies operator per Testing Standards type safety requirements
- [ ] Create shared fixture files following Testing Standards organization (spec/mocks, spec/fixtures)
- [ ] Document test dependencies per Testing Standards guidelines

**Test structure approach**:

Refer to [Testing Standards](@../../standards/quality/testing.md) for:

- Test Structure Standards (AAA pattern)
- Test Description Prefixes
- Mocking Standards (vi.hoisted pattern)
- Factory Functions for Test Doubles
- Coverage Requirements (100%)

All generated tests must exactly match Testing Standards patterns.

**Verification**:

- [ ] Subagent/workflow self-verification: All branches have corresponding test structures
- [ ] Primary agent verification: Test structures follow project standards
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 4. Fixture Refactoring and Generalization

Refactor existing fixtures for better reusability:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] **REVIEW Testing Standards**: Study [Testing Standards - Factory Functions](@../../standards/quality/testing.md#factory-functions-for-test-doubles)
- [ ] Consolidate duplicate fixtures following Testing Standards consolidation guidelines
- [ ] **VERIFY**: Create fixture builder patterns per Testing Standards examples
- [ ] **VALIDATE**: Implement factory functions matching Testing Standards patterns exactly
- [ ] **CONFIRM**: Add satisfies operator to all fixtures per Testing Standards type safety requirements
- [ ] Create fixture inheritance following Testing Standards organization
- [ ] Document fixture usage per Testing Standards documentation guidelines
- [ ] **CHECK**: Update existing tests to use refactored fixtures per Testing Standards

**Fixture refactoring approach**:

Refer to [Testing Standards - Test Double Organization](@../../standards/quality/testing.md#test-double-organization) for:

- Fixture file structure (spec/mocks, spec/fixtures)
- Factory function patterns with overrides
- Builder pattern implementation
- Type-safe fixtures with satisfies operator

All fixtures must follow Testing Standards patterns exactly.

**Verification**:

- [ ] Subagent/workflow self-verification: All fixtures properly generalized
- [ ] Primary agent verification: No fixture duplication remains
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 5. Coverage Validation and Documentation

Validate coverage completeness and document test strategy:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] **VERIFY Testing Standards**: Review [Testing Standards - Coverage Standards](@../../standards/quality/testing.md#coverage-standards)
- [ ] **CHECK**: Verify all branches have tests for 100% coverage per Testing Standards
- [ ] **VALIDATE**: Confirm edge cases and error conditions covered per Testing Standards requirements
- [ ] **CONFIRM**: Validate test structures follow BDD style per Testing Standards
- [ ] **VERIFY**: All tests follow AAA pattern with proper spacing per Testing Standards
- [ ] Document testing strategy following Testing Standards approach
- [ ] Create test execution plan following Testing Standards TDD principles
- [ ] Generate coverage report meeting Testing Standards thresholds (100%)
- [ ] Document any v8 ignore patterns per Testing Standards exclusion guidelines
- [ ] [[IMPORTANT] If coverage is not 100% (excluding allowed exclusions), go back to step 1]

**Verification**:

- [ ] All quality gates satisfied
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks or issues discovered during testing

### 6. Standards Compliance Verification

**Mandatory compliance verification against Testing Standards**:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] **OPEN Testing Standards**: Keep [Testing Standards](@../../standards/quality/testing.md) document open for reference
- [ ] **SECTION-BY-SECTION CHECK**: Verify each generated test against:
  - Core Testing Principles section (TDD, BDD, 100% coverage)
  - Test File Naming and Organization section
  - Test Structure Standards section (AAA pattern)
  - Mocking Standards section (vi.hoisted, type safety)
  - Test Double Organization section (fixture structure)
  - Coverage Standards section (100% requirement)
  - Test Anti-Patterns section (patterns to avoid)
- [ ] **DOCUMENT COMPLIANCE**: Create compliance matrix showing:
  - Test file generated
  - Testing Standards section checked
  - Pass/Fail status
  - Any deviations from standards
- [ ] **REJECT NON-COMPLIANCE**: Any generated test that doesn't meet Testing Standards must be regenerated
- [ ] **RE-VERIFY AFTER FIXES**: After regeneration, check compliance again
- [ ] **FINAL SIGN-OFF**: Confirm all tests meet every Testing Standards requirement

**Compliance verification checklist**:

- [ ] All tests use AAA pattern with proper spacing
- [ ] All test descriptions use correct prefixes (fn:, cl:, rc:, etc.)
- [ ] All tests use BDD naming ("should [behavior]")
- [ ] No use of `any` type - all use satisfies pattern
- [ ] All mocks use vi.hoisted pattern
- [ ] All test data uses const, not let
- [ ] Tests are self-contained (no unnecessary beforeEach)
- [ ] Tests focus on behavior, not implementation
- [ ] 100% coverage achieved (excluding v8 ignore patterns)
- [ ] All fixtures follow approved organization structure

**Verification**:

- [ ] Every generated test file checked against Testing Standards
- [ ] All standards violations fixed
- [ ] Mark this task as 'completed' in task tracking tool when verified

### 7. Final Review and Comprehensive Validation

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

- [ ] [[IMPORTANT] If any test standard (e.g. not archiving 100% coverage) → Reject and go back to step 1]
- [ ] Primary agent approves all work
- [ ] Mark this final review task as 'completed' in task tracking tool
- [ ] Document any deviations or follow-up items

## Standards to Follow

**🔴 MANDATORY: You MUST actively verify compliance with these standards**

- [ ] **BEFORE generating tests**: Read entire [Testing Standards](@../../standards/quality/testing.md)
- [ ] **DURING test generation**: Cross-reference each test with standards
- [ ] **AFTER test generation**: Run full compliance check against all standards
- [ ] **VERIFICATION**: Each test must pass ALL standards checks
- [ ] **DOCUMENTATION**: Record which standard sections were verified

**Required standards to follow and verify:**

- [Testing Standards](@../../standards/quality/testing.md) - **MUST VERIFY**: Test structure, coverage, AAA pattern, BDD naming
- [TypeScript Standards](@../../standards/code/typescript.md) - **MUST VERIFY**: Type safety, satisfies operator, no any types
- [Function Design Standards](@../../standards/code/functions.md) - **MUST CHECK**: Function testing patterns
- [Pure Functions Standards](@../../standards/code/pure-functions.md) - **MUST CHECK**: Testing without side effects
- [Error Handling Standards](@../../standards/backend/error-handling.md) - **MUST VERIFY**: Error condition coverage
- [Documentation Guidelines](@../../standards/code/documentation.md) - **MUST FOLLOW**: Test documentation

**Required verification checklist:**

- [ ] Core Testing Principles (TDD, BDD, 100% coverage) - VERIFIED
- [ ] Test Structure Standards (AAA pattern with spacing) - VERIFIED
- [ ] Mocking Standards (vi.hoisted, type safety) - VERIFIED
- [ ] Factory Functions and Test Doubles - VERIFIED
- [ ] Coverage Standards (100% requirement) - VERIFIED
- [ ] Test Anti-Patterns (none present) - VERIFIED

**Agent Instructions:**

- **DO NOT proceed** if any standard is violated
- **DO NOT skip** verification steps
- **DO NOT assume** compliance - actively check each standard
- **MUST document** every verification performed
- **MUST regenerate** tests if standards not met

## Common Issues

- **Over-testing**: Creating redundant tests that don't add coverage value
- **Under-mocking**: Not properly isolating units under test
- **Fixture sprawl**: Creating new fixtures instead of reusing existing ones
- **Missing branches**: Forgetting to test error conditions or edge cases
- **Type safety gaps**: Not using `satisfies <TYPE>` operator for fixture validation
- **Poor test names**: Using vague descriptions instead of BDD style
- **Complex setup**: Creating overly complicated test arrangements
- **Ignoring patterns**: Not following existing test patterns in the codebase

## Test Structure Output Template

### Expected Output Format

```markdown
## Test Coverage Analysis for [Area of Interest]

### Coverage Summary
- Current coverage: X%
- Target coverage: 100%
- Missing branches: Y
- New tests required: Z

### Test Structure Plan

#### File: [filename.spec.ts]
- **Function**: functionName
  - ✅ Happy path test
  - ❌ Edge case: null input
  - ❌ Error case: invalid parameter
  
#### Fixtures to Create/Modify
- `fixtures/user.ts` - Generalize for reuse across test files
- `mocks/userService.ts` - Add type safety with satisfies operator

### Implementation Order
1. Create shared fixtures
2. Write test structures for critical paths
3. Add edge case tests
4. Complete error handling tests

### Reusable Patterns Identified
- Builder pattern for complex objects
- Factory functions for mock services
- Shared error scenarios

### Standards Compliance Status
| Standard Section | Compliance | Notes |
|-----------------|------------|--------|
| Core Testing Principles | ✅ | TDD, BDD, 100% coverage |
| AAA Pattern | ✅ | All tests properly structured |
| Type Safety | ✅ | satisfies operator used |
| Mocking Standards | ✅ | vi.hoisted pattern |
| Coverage Requirements | ✅ | 100% achieved |
```

## Example Command Usage

### Targeted Test Creation

```bash
/create-test src/utilities.ts
# Generates test structures specifically for utilities.ts
```

### Comprehensive Coverage

```bash
/create-test
# Analyzes entire codebase and creates tests for all missing coverage
```

### Module-Level Testing

```bash
/create-test authentication
# Creates test structures for all files in authentication module
```

## Testing Patterns Reference

For all testing patterns and examples, refer to:

- [Testing Standards](@../../standards/quality/testing.md) - Complete testing patterns and examples
- [Test Structure Standards](@../../standards/quality/testing.md#test-structure-standards) - AAA pattern
- [Mocking Standards](@../../standards/quality/testing.md#mocking-standards) - vi.hoisted pattern
- [Factory Functions](@../../standards/quality/testing.md#factory-functions-for-test-doubles) - Fixture patterns
- [Test Anti-Patterns](@../../standards/quality/testing.md#test-anti-patterns) - Patterns to avoid

All generated tests must exactly match Testing Standards patterns.
