# Code Review & Quality Standards

*Standards for code review, testing, documentation, and quality assurance*

## Table of Contents

- [Testing Review Standards](#testing_review_standards) `testing_review_standards`
- [Documentation Review Standards](#documentation_review_standards) `documentation_review_standards`
- [Code Architecture Review](#code_architecture_review)
- [Code Review Process](#code_review_process) `code_review_process` - **workflow:** `review-code`
- [Review Checklist](#review_checklist)
- [Quality Gates](#quality_gates) `review_quality_gates` - **workflow:** `approve-pr`

<testing_review_standards>

## 🧪 Testing Review Standards

### Test Quality Review

When reviewing tests, verify:

- Tests follow TDD principles (see general-coding.md for TDD workflow)
- 100% coverage maintained with minimal tests
- BDD style descriptions: "should [expected behavior]"
- Proper Arrange → Act → Assert structure

### Review Test Patterns

```typescript
// ✅ Good test structure
describe('fn:fetchUserProfile', () => {
  it('should return user data when given valid id', () => {
    const expected = { id: '123', name: 'John' };
    
    const result = fetchUserProfile('123');
    
    expect(result).toEqual(expected);
  });
});
```

### Test Review Checklist

✅ Uses proper test file naming (`*.spec.ts`, `*.spec.tsx`)?
✅ Includes appropriate prefixes (`fn:`, `op:`, `cl:`, `ty:`, `rc:`)?
✅ Follows Arrange → Act → Assert pattern?
✅ Mocks external dependencies properly?
✅ Covers edge cases and error scenarios?
✅ No `any` types used in tests?
✅ Expected values declared before result?

### Mocking Review

Verify mocking follows the standard pattern:

```typescript
const { functionName } = vi.hoisted(() => ({
  functionName: vi.fn(),
}));

vi.mock('#module', () => ({
  functionName,
}) satisfies Partial<typeof import('#module')>);
```

</testing_review_standards>

<documentation_review_standards>

## 📚 Documentation Review Standards

### Documentation Quality Check

During review, verify documentation follows standards from general-coding.md:

- JSDoc format is correct (one-line preferred)
- Functions use 3rd-person verbs, lowercase, no period
- Non-functions use noun phrases
- All `@param` and `@throws` are listed
- NO TypeScript types in prose

### Documentation Review Checklist

✅ JSDoc format follows conventions?
✅ Interface properties have descriptions?
✅ Complex functions explain their purpose?
✅ Comment casing follows rules (lowercase sentences)?
✅ No temporary tags committed (`TODO`, `FIXME`, `DEBUG`)?
✅ Review tags removed before merge (`REVIEW`, `REFACTOR`)?
✅ Comments explain WHY, not WHAT?

### Review Comment Tags

Look for and flag these during review:

**Must be removed before merge:**

- `// TODO:` - Implementation needed
- `// FIXME:` - Broken code needs fixing
- `// DEBUG:` - Debug code to remove
- `// TEMP:` - Temporary code/stubs
- `// REVIEW:` - Needs peer review
- `// REFACTOR:` - Should be refactored

**Acceptable to keep:**

- `// HACK:` - Non-ideal solution to refactor later
- `// WORKAROUND:` - Bypasses external issue
- `// NOTE:` - Important context/explanation
- `// WARNING:` - Potential risks/edge cases

</documentation_review_standards>

<code_review_process>

## 👀 Code Review Process

<workflow name="review-code">

### Review Tone

- Use constructive, polite language
- Suggest improvements with justification
- Avoid blaming (❌ "this is wrong")
- Focus on the code, not the person

### Review Checklist

✅ Single responsibility functions (<60 lines)?
✅ Clear variable/type names?
✅ Errors handled explicitly?
✅ Edge cases tested?
✅ Files in correct directories?
✅ TypeScript conventions followed?
✅ React patterns followed?
✅ Tests written (TDD)?
✅ No console.log statements?
✅ No hardcoded secrets?
✅ Comments meaningful, not redundant?
✅ Naming conventions consistent?
✅ Import order correct?
✅ No TODO/FIXME/TEMP comments?

</workflow>

### Feedback Format

```typescript
// SUGGESTION: Consider using discriminated union for extensibility
type Status = 'active' | 'inactive' | 'pending';

// CONSIDER: Extract this to a reusable utility function
const formatDate = (date: Date) => {...};

// QUESTION: Is this error case handled upstream?
if (!user) throw new Error();

// NICE: Great use of early return pattern here! 👍
if (!isValid) return null;
```

### Priority Levels

- 🔴 **Critical** - Bugs, security issues
- 🟡 **Important** - Performance, maintainability
- 🟢 **Nice to have** - Style, minor improvements

</code_review_process>

<review_quality_gates>

## 🎯 Review Quality Gates

<workflow name="approve-pr">

### Review Completion Checklist

Before approving any pull request, verify:

✅ **Code Quality**

- Functions follow single responsibility (<60 lines)
- Clear variable/type names used
- TypeScript conventions followed
- Import order correct (see general-coding.md)

✅ **Testing**

- Tests written following TDD approach
- 100% coverage maintained
- Edge cases covered
- External dependencies mocked

✅ **Documentation**

- JSDoc format followed
- Comments explain WHY, not WHAT
- No temporary tags committed

✅ **Security**

- No hardcoded secrets
- Errors handled explicitly
- No console.log statements left

✅ **Architecture**

- Follows established patterns
- Files in correct directories
- React/service patterns followed

### Review Standards

**NEVER approve PRs that:**

- Use `--no-verify` commits
- Have failing tests or linting
- Missing documentation for public APIs
- Contain TODO/FIXME in production code

</workflow>

</review_quality_gates>
