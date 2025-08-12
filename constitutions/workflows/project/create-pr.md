# Create Pull Request

**Purpose**: Create a well-structured pull request following team standards
**When to use**: When feature branch is ready for review and merge
**Prerequisites**: All commits follow git standards, tests pass, code is complete

## Steps

### 1. Prepare Branch

Ensure your branch is ready:

- All commits follow [commit standards](../../standards/project/git-workflow.md)
- All tests pass locally
- Code follows quality standards
- Feature is complete and tested

### 2. Create PR with Proper Title

Use same format as commit messages:

```
feat(api): add user export functionality
```

### 3. Fill PR Description Template

```markdown
### 📌

**> Purpose and main changes in <3 sentences**

### 📝 Context

Why this change is needed, related tickets

### 🛠️ Implementation

What was implemented and how

### ✅ Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Manually tested

### 💥 Breaking Changes

(omit if none)

### 🔗 Related Issues

Closes #123, See #456

### 🧪 Manual Testing

(omit if not needed)

### 📋 Additional Notes

(omit if none)
```

### 4. Start as Draft PR

- Create as draft initially
- Update description as code evolves
- Convert to ready when complete

### 5. Request Reviews

- Request reviews from appropriate team members
- Tag relevant stakeholders
- Follow up on review feedback

### 6. Address Feedback

- Make requested changes
- Update PR description if scope changes
- Re-request reviews after changes

### 7. Merge When Approved

- Ensure all checks pass
- Merge using appropriate strategy (usually squash)
- Delete feature branch after merge

## Standards to Follow

**🔴 MANDATORY: All standards listed below MUST be followed without exception**

- [Git Workflow Standards](../../standards/project/git-workflow.md) - PR title and description formats
- [Code Review Standards](../../standards/quality/code-review.md) - Review preparation checklist
- [Communication Standards](../../standards/project/communication.md) - PR communication guidelines
- [Testing Standards](../../standards/quality/testing.md) - Test coverage requirements
- [Documentation Guidelines](../../standards/code/documentation.md) - Documentation updates
- [Review Code Workflow](../quality/review-code.md) - Review process guidelines

## PR Workflow Phases

### Draft Phase

- Incomplete work in progress
- Used for early feedback
- Can have failing tests temporarily

### Ready for Review

- All functionality complete
- All tests passing
- Ready for final review

### Approved

- All reviews completed
- All checks passed
- Ready to merge

## Common Issues

- **Missing context**: Explain WHY the change is needed, not just WHAT changed
- **Too large**: Break large PRs into smaller, focused changes
- **Missing tests**: Every PR should include appropriate test coverage
- **Unclear title**: Use descriptive, specific titles following commit format
- **Stale branch**: Rebase on main branch before creating PR
- **Missing documentation**: Update relevant docs when adding new features
