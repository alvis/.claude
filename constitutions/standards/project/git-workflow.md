# Git Workflow Standards

_Standards for version control, commit messages, and branch management_

## Commit Format

```plaintext
<type>(<scope>): <summary>   # ≤72 chars, imperative

<body>

<footer>
```

### Commit Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting (no logic change)
- `refactor` - Code restructuring
- `perf` - Performance improvement
- `test` - Test updates
- `build` - Build system changes
- `ci` - CI/CD changes
- `chore` - Routine tasks/dependencies
- `revert` - Revert previous commit

### Commit Rules

- **Scope**: directory/module (optional)
- **Summary**: Present tense, imperative mood
- **Reference issues**: `(#123)`
- **Footer**: `Closes #123, #456`

### Commit Examples

```bash
# Good commits
feat(auth): add OAuth2 login support
fix(api): handle null user in profile endpoint
docs(readme): update installation instructions
test(user): add edge case for email validation

# Bad commits
fixed bug
update code
changes
WIP
```

## Branch Naming

Format: `<type>/<scope>/<topic>`

### Examples

- `feat/web-talent/add-job-filter`
- `fix/profile/correct-validation`
- `chore/update-dependencies`
- `docs/api/add-endpoint-examples`

### Rules

- Use lowercase-kebab-case only
- Keep branch names descriptive but concise
- Include scope when relevant
- Delete branches after merge

## Critical Quality Gates

### Pre-commit Requirements

**🔴 MANDATORY: Run before every commit**

```bash
npm run lint             # Must pass
npm run coverage            # Must pass
npm run typecheck       # Must pass (if available)
```

### Absolute Prohibitions

- **NEVER use `--no-verify`** - bypasses essential checks
- **NEVER commit failing tests**
- **NEVER commit linting errors**
- **NEVER commit secrets or sensitive data**
- **NEVER commit commented-out code**
- **NEVER commit console.log statements**

## Branching Strategy

### Main Branch Protection

- All changes via pull requests
- Require passing CI checks
- Require code review approval
- Automatically delete merged branches

### Feature Branch Workflow

1. Create feature branch from main
2. Make changes with frequent commits
3. Push branch and create PR
4. Address review feedback
5. Merge via pull request
6. Delete feature branch

### Hotfix Workflow

For critical production fixes:

1. Create hotfix branch from main
2. Make minimal fix with tests
3. Create PR with "hotfix" label
4. Fast-track review process
5. Merge and deploy immediately

## Merge Strategies

### Squash and Merge (Preferred)

- Combines all commits into single commit
- Keeps main branch history clean
- Good for feature branches

### Merge Commit

- Preserves individual commits
- Use for important historical context
- Good for release branches

### Rebase and Merge

- Replays commits onto main
- No merge commit created
- Use sparingly for linear history

## Commit Message Best Practices

### Structure

```
feat(user-profile): add avatar upload functionality

- Implement file upload with validation
- Add image processing and resizing
- Update user model with avatar field
- Include comprehensive test coverage

Closes #245
```

### Guidelines

- **Subject line**: 50 chars or less, imperative mood
- **Body**: Wrap at 72 chars, explain WHY not WHAT
- **Footer**: Reference issues and breaking changes

### Good Examples

```bash
fix(auth): prevent token expiration edge case

The JWT validation was not handling the exact expiration
timestamp correctly, causing valid tokens to be rejected
in some timezone configurations.

Fixes #456

refactor(api): extract common validation logic

Move shared validation functions to utils module to
reduce code duplication across multiple endpoints.

- Extract email validation
- Extract phone number validation
- Add comprehensive test coverage

No breaking changes
```

## Repository Hygiene

### Regular Maintenance

- Delete merged branches weekly
- Review and close stale PRs
- Update dependencies monthly
- Clean up unused files

### Security Practices

- Never commit `.env` files
- Use `.gitignore` properly
- Rotate any accidentally committed secrets
- Regular security audits of dependencies

### Performance Considerations

- Keep repository size reasonable
- Use Git LFS for large files
- Regular garbage collection
- Shallow clones for CI when possible

## Pull Request Standards

### PR Template

Use this template for all pull requests:

```markdown
📌 In plain language, explain the purpose of the PR and its main changes in less than 3 sentences.

## 📝 Context

Include any relevant context or background information that helps reviewers understand the change, e.g.
- Why is this change needed? Any problems or symptoms?
- Links to the related bug tickets?
- What problem does it solve? and Why?
- Any relevant background or design considerations

## 🛠️ Implementation

Describe what has been implemented
- Any features implemented
- Outline how the solution was achieved
- Any trade-offs, architectural choices, or design patterns

## ✅ Checklist

List all items that need to be completed before the PR can be merged, e.g.
- [ ] Code adheres to style guide
- [ ] Unit tests added/updated
- [ ] Documentation updated
- [ ] Manually tested

## 💥 Breaking Changes

List any breaking changes introduced by this PR
- Note if there are any changes that might break existing functionality
- Include upgrade or migration instructions if relevant

## 🔗 Related Issues

Reference related tickets, issues, RFCs, discussions, e.g.
- `Closes #123, See #456, Spec: [Notion doc](https://...)`

## 🧪 Manual Testing

If applicable, describe how to manually test the changes, including
- Steps or instructions for a reviewer to manually verify the change
- Screenshots or screencasts if relevant

## 📋 Additional Notes

List any other information useful for reviewers or future maintainers, e.g.
- Known issues, temporary limitations, future follow-ups
```

### PR Description Requirements

- **Stay clear and professional**
- **Keep each section focused and concise**
- **Link to code, tickets, specs, or discussions**
- **Explain non-obvious decisions or technical details**
- **Make it easy for reviewers and future maintainers to follow and understand**
- **Use paragraphs for longer explanations in general, but use point form if points are short, related and best expressed as a list** (e.g., checklist, breaking changes, etc.)
- **Require Summary and Checklist sections**, other sections are optional

### PR Title Format

Follow the same format as commit messages:

```
<type>(<scope>): <summary>
```

Examples:

- `feat(auth): add multi-factor authentication`
- `fix(api): resolve race condition in user updates`
- `docs(readme): update deployment instructions`

### PR Review Checklist

#### For Authors

Before requesting review:

- [ ] **Tests**: All tests pass locally
- [ ] **Lint**: No linting errors or warnings
- [ ] **Types**: TypeScript compilation succeeds
- [ ] **Coverage**: Test coverage maintained or improved
- [ ] **Documentation**: Updated relevant docs
- [ ] **Commits**: Clean commit history (squash if needed)
- [ ] **Size**: PR is focused and not too large
- [ ] **Description**: Clear PR description with context

#### For Reviewers

When reviewing PRs:

- [ ] **Functionality**: Does the code do what it claims?
- [ ] **Tests**: Are tests comprehensive and meaningful?
- [ ] **Code Quality**: Is the code clean and maintainable?
- [ ] **Performance**: No obvious performance issues?
- [ ] **Security**: No security vulnerabilities?
- [ ] **Architecture**: Follows project patterns?
- [ ] **Documentation**: Is the code self-documenting or commented?
- [ ] **Edge Cases**: Are edge cases handled?

### PR Size Guidelines

Keep PRs small and focused:

- **Small**: < 100 lines changed (quick review)
- **Medium**: 100-500 lines changed (normal review)
- **Large**: 500-1000 lines changed (needs justification)
- **Too Large**: > 1000 lines (split into multiple PRs)

### PR Review Etiquette

#### For Authors

- Respond to all comments
- Mark resolved conversations
- Explain any non-obvious decisions
- Be receptive to feedback
- Update PR based on feedback promptly

#### For Reviewers

- Be constructive and specific
- Suggest improvements, not just problems
- Acknowledge good code
- Focus on important issues first
- Use conventional comment prefixes:
  - `nit:` - Minor issue (optional fix)
  - `question:` - Seeking clarification
  - `suggestion:` - Recommended improvement
  - `issue:` - Must be addressed
  - `praise:` - Highlighting good code

### Merge Requirements

Before merging:

1. **Approvals**: Required number of approvals received
2. **CI/CD**: All checks pass
3. **Conflicts**: No merge conflicts
4. **Comments**: All review comments addressed
5. **Tests**: New tests for new functionality
6. **Documentation**: Updated if needed
7. **Changelog**: Updated if user-facing changes

### Special PR Types

#### Hotfix PRs

For critical production fixes:

- Title must start with `hotfix:`
- Minimal changes only
- Must include tests
- Fast-track review process
- Deploy immediately after merge

#### Breaking Change PRs

For backwards-incompatible changes:

- Title must include `BREAKING CHANGE:`
- Migration guide required
- Major version bump needed
- Extended review period
- Coordinate with dependent teams

#### Documentation PRs

For documentation-only changes:

- Title starts with `docs:`
- Can skip certain CI checks
- Still requires review
- Update relevant indexes
