# Review Code

**Purpose**: Complete code review process to ensure quality, maintainability, and standards compliance
**When to use**: When reviewing pull requests or code changes
**Prerequisites**: Understanding of project standards, access to code changes, testing environment available

## Steps

### 1. Review Tone and Approach

Set the right tone for constructive feedback:

- **Use constructive, polite language** - Focus on helping improve the code
- **Suggest improvements with justification** - Explain why changes are needed
- **Avoid blaming language** - Don't say "this is wrong", explain what could be better
- **Focus on the code, not the person** - Keep feedback objective and professional
- **Recognize good work** - Call out well-written code and good patterns

### 2. Code Quality Assessment

Review fundamental code quality aspects:

**Function Design:**

- [ ] Functions follow single responsibility principle (<60 lines)
- [ ] Clear, descriptive function names
- [ ] Proper parameter design (positional vs object parameters)
- [ ] Return types explicitly declared

**Variable and Type Naming:**

- [ ] Clear, descriptive variable names
- [ ] Consistent naming conventions (camelCase, PascalCase)
- [ ] No abbreviations or unclear names
- [ ] Type names are descriptive and specific

**Error Handling:**

- [ ] Errors handled explicitly with specific types
- [ ] No silent failures or ignored errors
- [ ] Proper error messages for debugging
- [ ] Edge cases considered and handled

### 3. Architecture and Patterns Review

Verify architectural compliance:

**File Organization:**

- [ ] Files placed in correct directories
- [ ] Proper import/export patterns
- [ ] No circular dependencies
- [ ] Consistent file naming

**Framework Patterns:**

- [ ] TypeScript conventions followed (strict types, no `any`)
- [ ] React patterns followed (FC types, hooks usage, accessibility)
- [ ] Service patterns followed (proper error handling, data validation)
- [ ] Import order correct (Node → third-party → project modules)

### 4. Testing Review

Assess test quality and coverage:

**Test Structure:**

- [ ] Tests written following TDD approach
- [ ] Proper test file naming with prefixes (`fn:`, `rc:`, `op:`)
- [ ] Arrange → Act → Assert pattern followed
- [ ] Tests are self-contained and focused

**Test Quality:**

- [ ] 100% coverage maintained with minimal tests
- [ ] Edge cases and error scenarios covered
- [ ] External dependencies properly mocked
- [ ] Uses `const` over `let`, avoids `beforeEach`
- [ ] No `any` types used in tests

**Test Patterns:**

```typescript
// ✅ Look for proper test structure
describe("fn:calculateTotal", () => {
  it("should return correct total with tax applied", () => {
    const expected = 108.0;

    const result = calculateTotal(100, 0.08);

    expect(result).toBe(expected);
  });
});
```

### 5. Documentation Review

Check documentation quality:

**JSDoc Standards:**

- [ ] JSDoc format is correct (one-line when possible)
- [ ] Functions use 3rd-person verbs, lowercase, no period
- [ ] Non-functions use noun phrases
- [ ] All `@param` and `@throws` documented
- [ ] No TypeScript types duplicated in prose

**Comment Quality:**

- [ ] Comments explain WHY, not WHAT
- [ ] Comment casing follows rules (lowercase sentences)
- [ ] No redundant or obvious comments
- [ ] Complex business logic is explained

### 6. Security Review

Verify security practices:

**Code Security:**

- [ ] No hardcoded secrets or API keys
- [ ] No sensitive data in logs
- [ ] Input validation for external data
- [ ] Proper authentication/authorization checks

**Development Artifacts:**

- [ ] No console.log statements in production code
- [ ] No debug code or temporary implementations
- [ ] No commented-out code blocks

### 7. Comment Tag Review

Flag problematic comment tags:

**Must be removed before merge:**

- `// TODO:` - Implementation needed
- `// FIXME:` - Broken code needs fixing
- `// DEBUG:` - Debug code to remove
- `// TEMP:` - Temporary code/stubs
- `// REVIEW:` - Needs peer review
- `// REFACTOR:` - Should be refactored

**Acceptable to keep:**

- `// HACK:` - Non-ideal solution with future refactor plan
- `// WORKAROUND:` - Bypasses external issue
- `// NOTE:` - Important context/explanation
- `// WARNING:` - Potential risks/edge cases

## Feedback Format Guidelines

### Feedback Categories

Use clear prefixes to categorize feedback:

```typescript
// SUGGESTION: Consider using discriminated union for extensibility
type Status = 'active' | 'inactive' | 'pending';

// CONSIDER: Extract this to a reusable utility function
const formatDate = (date: Date) => {...};

// QUESTION: Is this error case handled upstream?
if (!user) throw new Error();

// NICE: Great use of early return pattern here! 👍
if (!isValid) return null;

// CRITICAL: This could cause a security vulnerability
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

### Priority Levels

Assign appropriate priority to feedback:

- 🔴 **Critical** - Security issues, bugs that break functionality
- 🟡 **Important** - Performance issues, maintainability concerns, architectural problems
- 🟢 **Nice to have** - Style improvements, minor optimizations, suggestions

### Constructive Feedback Examples

```typescript
// ✅ Good feedback examples:

// SUGGESTION: Consider extracting this validation logic into a reusable function
// This pattern appears in multiple places and could benefit from centralization.

// CONSIDER: Using a Map here instead of an array filter would improve performance
// for large datasets (O(1) vs O(n) lookup time).

// QUESTION: Should we handle the case where the API returns a 429 status?
// The current implementation might retry indefinitely.

// NICE: Excellent use of TypeScript discriminated unions here!
// This makes the API much more type-safe.

// ❌ Poor feedback examples:

// This is wrong.
// Bad code.
// Why did you do this?
// This doesn't make sense.
```

## Expected Output Template

### Code Review Summary

Use this template when providing a comprehensive code review:

```markdown
## Code Review: [PR Title]

### Summary

[2-3 sentence overview of the changes and overall assessment]

### Quality Assessment

- **Code Quality**: [Excellent/Good/Needs Improvement]
- **Test Coverage**: [Complete/Adequate/Insufficient]
- **Documentation**: [Complete/Adequate/Missing]
- **Standards Compliance**: [Full/Partial/Non-compliant]

### Strengths ✅

- [Positive aspect 1]
- [Positive aspect 2]
- [Good patterns observed]

### Critical Issues 🔴

- [ ] [Security/Breaking issue that must be fixed]
- [ ] [Another critical issue]

### Important Suggestions 🟡

- [ ] [Performance or maintainability improvement]
- [ ] [Architectural concern]

### Minor Suggestions 🟢

- [ ] [Style improvement]
- [ ] [Optional enhancement]

### Detailed Feedback

[File-by-file feedback using the feedback format guidelines above]

### Testing Verification

- [ ] All tests pass locally
- [ ] New tests cover added functionality
- [ ] Edge cases considered
- [ ] Performance implications tested

### Final Recommendation

[Approve/Request Changes/Comment]

### Next Steps

[Clear action items for the author if changes are needed]
```

## Standards to Follow

- [Testing Standards](../../standards/quality/testing.md)
- [TypeScript Standards](../../standards/code/typescript.md)
- [Documentation Standards](../../standards/code/documentation.md)
- [React Component Standards](../../standards/frontend/react-components.md)
- [API Design Standards](../../standards/backend/api-design.md)

## Review Quality Gates

**Before providing approval, ensure:**

✅ **No Critical Issues:**

- [ ] No security vulnerabilities identified
- [ ] No functionality-breaking bugs
- [ ] No performance bottlenecks introduced

✅ **Standards Compliance:**

- [ ] All applicable coding standards followed
- [ ] Proper error handling implemented
- [ ] Documentation requirements met

✅ **Test Coverage:**

- [ ] All new code covered by tests
- [ ] Tests follow TDD principles
- [ ] No test quality regressions

## Common Review Issues

**Architecture Issues:**

- Functions that do too much (>60 lines)
- Unclear separation of concerns
- Inconsistent error handling patterns
- Missing abstraction layers

**Code Quality Issues:**

- Unclear variable/function names
- Complex nested conditionals
- Repeated code patterns
- Missing type safety

**Testing Issues:**

- Tests that test implementation details
- Missing edge case coverage
- Overly complex test setup
- Tests that don't follow AAA pattern

**Documentation Issues:**

- Missing JSDoc for public APIs
- Comments that restate the code
- Outdated documentation
- Temporary tags left in code

## Review Completion

After completing the review:

1. **Summarize findings** - Provide a brief overview of main concerns
2. **Categorize feedback** - Separate critical, important, and nice-to-have items
3. **Provide next steps** - Clear guidance on what needs to be addressed
4. **Offer assistance** - Be available for questions or pair programming if needed

The goal is to maintain high code quality while supporting team learning and growth.
