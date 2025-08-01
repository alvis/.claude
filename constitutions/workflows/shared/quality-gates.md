# Quality Gates Workflow

**Purpose**: Standardized quality verification steps used across all workflows  
**When to use**: Before committing code, after making changes, during reviews  
**Prerequisites**: Node.js environment with project dependencies installed

## Quick Reference

```bash
# Standard quality gate sequence
npm run typecheck    # TypeScript compilation
npm run lint         # Code style and quality
npm run coverage     # Test suite with coverage
```

## Detailed Steps

### 1. TypeScript Compilation Check

**Run TypeScript compiler**

```bash
npm run typecheck
# If not available, try:
npx tsc --noEmit
```

**Success Criteria:**

- ✅ No TypeScript errors
- ✅ All types properly defined
- ✅ Strict mode compliance

**Common Issues:**

- Missing type definitions → Add explicit types or install @types packages
- Implicit any errors → Enable noImplicitAny and fix
- Strict null checks → Handle null/undefined cases

### 2. Linting Validation

**Run ESLint/linter**

```bash
npm run lint
# Auto-fix when possible:
npm run lint:fix
```

**Success Criteria:**

- ✅ No linting errors
- ✅ No security warnings
- ✅ Import order correct

**Common Issues:**

- Import order → Run auto-fix or manually reorder
- Unused variables → Remove or prefix with underscore
- Missing deps → Add to useEffect/useMemo arrays

### 3. Test Coverage Verification

**Run test suite with coverage**

```bash
npm run coverage
# Or if using specific test runner:
npm run test -- --coverage
```

**Success Criteria:**

- ✅ All tests passing
- ✅ Coverage meets thresholds (100% for new code)
- ✅ No snapshot mismatches

**Common Issues:**

- Failing tests → Fix implementation or update tests
- Low coverage → Add missing test cases
- Snapshot failures → Review and update if intentional

### 4. Build Verification (Optional)

**For production readiness**

```bash
npm run build
```

**Success Criteria:**

- ✅ Build completes without errors
- ✅ Bundle size within limits
- ✅ No missing dependencies

## Quality Gate Sequence

### Standard Flow

1. **TypeScript** → Catch type errors early
2. **Linting** → Ensure code style consistency
3. **Tests** → Verify functionality and coverage
4. **Build** → Confirm production readiness

### Quick Check (During Development)

```bash
# Run all checks in sequence
npm run typecheck && npm run lint && npm run coverage
```

### Pre-Commit Check

```bash
# Ensure all quality gates pass before committing
npm run typecheck && npm run lint:fix && npm run coverage
```

## Integration with Workflows

This quality gate workflow is referenced by:

- [Write Code (TDD)](../coding/write-code-tdd.md) - After implementation
- [Prepare for Coding](../coding/prepare-coding.md) - Before starting
- [Commit with Git](../project/commit-with-git.md) - Before committing
- [Build Component](../frontend/build-component.md) - After component creation
- [Build Service](../backend/build-service.md) - After service implementation

## Automation

### Git Hooks

Pre-commit hooks automatically run quality gates:

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "npm run typecheck && npm run lint-staged && npm run test:staged"
    }
  }
}
```

### CI/CD Pipeline

Quality gates run automatically on:

- Pull request creation
- Push to feature branches
- Merge to main branch

## Standards References

- [TypeScript Standards](../../standards/code/typescript.md) - Type safety requirements
- [Testing Standards](../../standards/quality/testing.md) - Coverage requirements
- [Code Style](../../standards/code/general-principles.md) - Linting rules

## Exit Criteria

✅ **All quality gates must pass before:**

- Committing code
- Creating pull requests
- Merging to main branch
- Deploying to production

❌ **Block if any gate fails:**

- TypeScript errors present
- Linting violations exist
- Tests failing or coverage below threshold
- Build errors occur
