# Approve Pull Request

**Purpose**: Final quality gate process before merging code changes
**When to use**: After code review completion, before merging PR
**Prerequisites**: Code review completed, all feedback addressed, tests passing

## Steps

### 1. Verify Review Completion

Ensure all review feedback has been addressed:

- [ ] All review comments have been resolved or replied to
- [ ] Critical and important issues have been fixed
- [ ] Author has responded to questions and clarifications
- [ ] Any requested changes have been implemented
- [ ] Follow-up discussions have reached conclusion

### 2. Code Quality Final Check

Perform final verification of code quality standards:

**Function Design:**
- [ ] Functions follow single responsibility (<60 lines)
- [ ] Clear, descriptive variable and type names used
- [ ] Proper error handling with explicit types
- [ ] No hardcoded values or magic numbers

**Architecture Compliance:**
- [ ] TypeScript conventions followed (strict types, no `any`)
- [ ] Import order correct (Node built-ins → third-party → project modules)
- [ ] Files placed in correct directories
- [ ] Follows established project patterns

**React-Specific (if applicable):**
- [ ] Components use FC type with arrow functions
- [ ] Props interfaces are exported
- [ ] Accessibility standards followed
- [ ] Performance optimizations applied appropriately

### 3. Testing Final Verification

Confirm comprehensive test coverage:

**Test Quality:**
- [ ] Tests written following TDD approach
- [ ] 100% coverage maintained with minimal, meaningful tests
- [ ] Proper test file naming with prefixes (`fn:`, `rc:`, `op:`)
- [ ] Arrange → Act → Assert pattern followed consistently

**Test Coverage:**
- [ ] All new functionality covered by tests
- [ ] Edge cases and error scenarios tested
- [ ] External dependencies properly mocked
- [ ] Integration points validated

**Test Execution:**
- [ ] All tests passing locally and in CI
- [ ] No flaky or intermittent test failures
- [ ] Test performance acceptable (no unnecessarily slow tests)

### 4. Documentation Verification

Ensure documentation meets standards:

**JSDoc Standards:**
- [ ] JSDoc format correct (one-line preferred, multi-line when needed)
- [ ] Functions use 3rd-person verbs, lowercase, no period
- [ ] Non-functions use noun phrases
- [ ] All parameters and throws documented
- [ ] Complex interfaces have property descriptions

**Comment Quality:**
- [ ] Comments explain WHY, not WHAT
- [ ] Comment casing follows rules (lowercase sentences)
- [ ] No temporary tags committed (`TODO`, `FIXME`, `DEBUG`, `TEMP`)
- [ ] Review tags removed (`REVIEW`, `REFACTOR`)

### 5. Security Final Assessment

Verify security practices have been followed:

**Code Security:**
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] No sensitive data exposed in logs or error messages
- [ ] Input validation implemented for external data
- [ ] Authentication/authorization checks in place

**Development Artifacts:**
- [ ] No console.log statements in production code
- [ ] No debug code or development-only features
- [ ] No commented-out code blocks
- [ ] No temporary implementations or stubs

### 6. Build and Deployment Readiness

Confirm the code is ready for deployment:

**Build Process:**
- [ ] Code compiles without TypeScript errors
- [ ] Linting passes with no violations
- [ ] Build process completes successfully
- [ ] No build warnings for new code

**Quality Gates:**
- [ ] All automated checks passing in CI/CD
- [ ] No `--no-verify` commits used
- [ ] Pre-commit hooks have run successfully
- [ ] Code formatting consistent with project standards

### 7. Integration Considerations

Assess broader integration impact:

**Dependencies:**
- [ ] No new unnecessary dependencies introduced
- [ ] Dependency versions are appropriate and secure
- [ ] Breaking changes are documented and coordinated
- [ ] Database migrations (if any) are backward compatible

**API Changes:**
- [ ] Public API changes are backward compatible or properly versioned
- [ ] Interface changes don't break existing consumers
- [ ] Documentation updated for API modifications

## Critical Approval Blockers

**NEVER approve PRs that contain:**

🔴 **Security Issues:**
- Hardcoded secrets or credentials
- SQL injection vulnerabilities
- XSS vulnerabilities
- Unauthorized data access

🔴 **Quality Issues:**
- Use of `--no-verify` commits
- Failing tests or linting errors
- Missing tests for new functionality
- TypeScript `any` types without justification

🔴 **Documentation Issues:**
- Missing documentation for public APIs
- TODO/FIXME comments in production code
- Temporary implementation placeholders
- Outdated or incorrect documentation

🔴 **Architecture Issues:**
- Violations of established patterns
- Circular dependencies
- Inappropriate abstractions
- Performance regressions

## Approval Decision Matrix

| Criteria | Must Pass | Should Pass | Nice to Have |
|----------|-----------|-------------|--------------|
| Security | ✅ No vulnerabilities | ✅ Best practices followed | 📝 Security comments added |
| Functionality | ✅ Feature works correctly | ✅ Edge cases handled | 📝 Performance optimized |
| Tests | ✅ Coverage maintained | ✅ Quality tests added | 📝 Integration tests included |
| Documentation | ✅ Public APIs documented | ✅ Complex logic explained | 📝 Examples provided |
| Standards | ✅ Coding standards met | ✅ Patterns followed | 📝 Code style exemplary |

## Post-Approval Process

After approving the PR:

### 1. Merge Strategy Selection

Choose appropriate merge strategy:

- **Squash and merge** - For feature branches with multiple commits
- **Merge commit** - For releases or significant feature integration
- **Rebase and merge** - For clean history when commits are already well-formed

### 2. Final Merge Verification

Before clicking merge:

- [ ] PR title and description are clear and accurate
- [ ] Commit message follows project conventions
- [ ] Target branch is correct (usually main/master)
- [ ] No conflicts with target branch

### 3. Post-Merge Monitoring

After merging:

- [ ] Monitor deployment pipeline for any issues
- [ ] Verify deployed changes work as expected
- [ ] Watch for any error alerts or monitoring issues
- [ ] Follow up on any automated notifications

## Standards Referenced

- [Code Review Process](./review-code.md)
- [Testing Standards](../../standards/quality/testing.md)
- [TypeScript Standards](../../standards/code/typescript.md)
- [Documentation Standards](../../standards/code/documentation.md)
- [Git Workflow Standards](../../standards/project/git-workflow.md)

## Quality Metrics

Track these metrics to improve the approval process:

- **Time to approval** - From review completion to merge
- **Post-merge issues** - Bugs introduced after approval
- **Review coverage** - Percentage of code covered by review
- **Standards compliance** - Adherence to coding standards

Use these metrics to identify areas for process improvement and ensure the approval process maintains high quality while enabling efficient development flow.