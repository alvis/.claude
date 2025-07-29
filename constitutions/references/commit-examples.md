# Commit Message Examples & References

*Reference examples of good and bad commit messages with detailed patterns*

## Table of Contents

- [Good Examples](#good_examples) `good_examples`
- [Bad Examples](#bad_examples) `bad_examples`
- [Commit Title Guidelines](#title_guidelines) `title_guidelines`
- [Common Commit Patterns](#common_patterns) `common_patterns`
- [Message Body Examples](#message_body_examples) `message_body_examples`
- [Quick Reference](#quick_reference) `quick_reference`

<good_examples>

## ✅ Good Commit Examples

### Features

```plaintext
feat(auth): implement OAuth2 authentication
feat(ui): add dark mode toggle
feat(search): implement fuzzy search algorithm
feat(component): add new React component for user profile
feat(storybook): update storybook configuration for new components
feat(user): add new UserProfile component
```

### Bug Fixes

```plaintext
fix(api): resolve race condition in user registration
fix(security): patch XSS vulnerability in comment system
fix(mobile): resolve layout issues on small screens
fix(test): resolve flaky e2e tests in auth flow
fix(a11y): improve accessibility in navigation menu
fix(types): correct type declarations for build
fix(auth): allow login with email alias
fix(profile, auth): stop access when role is missing (#123, #789)
```

### Documentation

```plaintext
docs(readme): update installation instructions
docs(api): update OpenAPI documentation
docs(contributing): add pull request guidelines
docs(storybook): add documentation for new storybook components
```

### Style Changes

```plaintext
style(css): format stylesheet according to style guide
style(js): apply prettier formatting to all JavaScript files
style(html): ensure consistent indentation
```

### Refactoring

```plaintext
refactor(utils): simplify date formatting function
refactor(auth): extract login logic into separate service
refactor(state): migrate from Redux to React Context API
refactor(components): convert class components to functional
refactor(web): reorder exports for better organization
```

### Performance

```plaintext
perf(database): optimize query for faster user lookup
perf(images): implement lazy loading for gallery
perf(rendering): optimize React component re-renders
```

### Testing

```plaintext
test(user): add unit tests for password reset flow
test(e2e): add Cypress tests for checkout process
test(unit): fix failing tests in user service
test(vitest): update Vitest configuration for better performance
```

### Build System

```plaintext
build(docker): update Dockerfile for multi-stage builds
build(webpack): optimize bundle size
build(storybook): update storybook build process
build: update webpack configuration for production
build: add precommit hook for linting
```

### Continuous Integration

```plaintext
ci(github): add workflow for automatic dependency updates
ci(github): cache node_modules for faster builds
ci(actions): fix caching issues in GitHub Actions workflow
```

### Maintenance

```plaintext
chore(deps): update lodash to v4.17.21
chore(gitignore): update .gitignore with new build artifacts
chore(lint): resolve ESLint warnings in src directory
chore(types): update TypeScript definitions
chore(prettier): apply consistent code formatting
chore(comments): add explanatory comments to clarify code logic
chore: update TypeScript to v5.5
```

### Dependency Updates

```plaintext
chore: update TypeScript to v5.5              # For build system dependency upgrades
fix: upgrade axios to fix security vulnerability    # For dependency upgrades addressing bugs
feat: upgrade next.js for new app router feature   # For dependency upgrades to access new features
```

</good_examples>

<bad_examples>

## ❌ Bad Examples (and How to Fix)

### Vague or Unclear

```plaintext
❌ fix: DB health survey update limit
✅ fix(survey): use stream to update health survey sendAt

❌ fix: warn users when they try to join a deleted office  
✅ fix(officelyfm): warn users when they try to join a deleted office

❌ fix: handle unhandled error and log body
✅ feat(app): handle unhandled error and log body

❌ fix: warn users when they try to join a deleted office via OfficelyFM
✅ fix(officelyfm): warn users when they try to join a deleted office
```

### Wrong Type Classification

```plaintext
❌ feat(onboarding): rename neighborhood
✅ feat(onboarding): use neighborhood in American spelling

❌ fix(setting): ignore removed neighborhoods  
✅ fix(user): ignore deleted favorite neighborhoods in preference

❌ fix(receiver): handle unhandled error and log body
✅ feat(app): handle unhandled error and log body

❌ fix(officespage): use American spelling, neighborhood
✅ feat(office): use neighborhood in American spelling
```

### Multiple Changes in One Commit

```plaintext
❌ fix(onboarding): add office layout diagram and rename neighborhood
✅ feat(onboarding): add office layout
✅ feat: rename neighborhood to neighborhood

❌ feat(auth, profile): add login and update user settings
✅ feat(auth): add OAuth login functionality  
✅ feat(profile): add user settings update
```

### Poor Scope Usage

```plaintext
❌ fix(getbestneighborhood): fix recurring booking
✅ fix(recurring): skip booking if favorite neighborhoods get deleted

❌ docs: correct broken link  
✅ docs(readme): correct broken link

❌ fix(app): log error with more context, including userId, workspaceId
✅ feat(app): log error with more context including userId and workspaceId
```

</bad_examples>

<title_guidelines>

## Commit Title Guidelines

### Length Limits

- **Preferred**: ≤50 characters for readability
- **Acceptable**: Up to 72 characters if needed for clarity
- **Hard limit**: 72 characters maximum

### Format Rules

- Use present-tense, imperative mood
  - ✅ `add`, `fix`, `refactor`
  - ❌ `added`, `fixed`, `refactored`
- Include scope when relevant: `feat(auth): add login`
- Reference issues when helpful: `fix(profile): stop mutation (#123, #456)`

### Scope Guidelines

- Use directory or module name: `feat(client/web-talent)`, `fix(service/profile)`
- Omit scope if not relevant: `chore: update TypeScript to v5.5`
- Use component names for specific fixes: `fix(auth)`, `feat(dashboard)`

</title_guidelines>

<common_patterns>

## Common Commit Patterns

### Scope Patterns

```plaintext
# Service/Module scopes
feat(auth): implement login
fix(profile): correct validation  
refactor(dashboard): simplify layout

# Directory scopes
feat(client/web): add new landing page
fix(service/api): resolve timeout issue
test(packages/utils): add validation tests

# No scope (project-wide)
chore: update dependencies
build: configure webpack
ci: add GitHub Actions workflow
```

### Issue References

```plaintext
# Single issue
fix(auth): resolve login timeout (fixes #123)
feat(dashboard): add export feature (closes #456)

# Multiple issues  
fix(profile): handle edge cases (#123, #456)
feat(api): add bulk operations (closes #789, #012)
```

### Breaking Changes

```plaintext
# Minor breaking change
feat(api)!: change user response format

# Major breaking change with body
feat(auth)!: redesign authentication flow

BREAKING CHANGE: Authentication now requires OAuth2.
Migration guide available at docs/auth-migration.md
```

</common_patterns>

<message_body_examples>

## Message Body Examples

### Complex Feature

```plaintext
feat(auth): implement OAuth2 authentication

Add support for Google and GitHub OAuth providers.
Includes user account linking and automatic profile creation.

- Add OAuth2 client configuration
- Implement provider-specific handlers  
- Add user account merge logic
- Update login UI with provider buttons

Closes #456, #789
```

### Bug Fix with Context

```plaintext
fix(profile): resolve avatar upload race condition

When users uploaded multiple avatars quickly, the last
upload would sometimes fail due to concurrent S3 operations.

Now using atomic uploads with unique file keys to prevent
conflicts and ensure reliable avatar updates.

Fixes #234
```

### Breaking Change

```plaintext
feat(api)!: standardize error response format  

BREAKING CHANGE: Error responses now use consistent format.
All API errors return { error: { code, message, details } }
instead of previous mixed formats.

Migration guide: docs/api-v2-migration.md
```

</message_body_examples>

<quick_reference>

## Quick Reference

### Commit Types Quick List

- `feat` - New feature
- `fix` - Bug fix  
- `docs` - Documentation
- `style` - Code formatting
- `refactor` - Code restructuring
- `perf` - Performance improvement
- `test` - Test changes
- `build` - Build system/tools
- `ci` - CI/CD changes
- `chore` - Routine maintenance
- `revert` - Revert previous commit

### Common Scopes

- `auth` - Authentication/authorization
- `api` - API changes
- `ui` - User interface
- `db` - Database changes
- `config` - Configuration
- `deps` - Dependencies
- `security` - Security improvements
- `a11y` - Accessibility
- `i18n` - Internationalization
- `mobile` - Mobile-specific changes
- `desktop` - Desktop-specific changes

### Footer Keywords

- `Closes #123` - Closes issue
- `Fixes #123` - Fixes bug
- `Resolves #123` - Resolves issue
- `See #123` - References related issue
- `BREAKING CHANGE:` - Breaking change description

</quick_reference>
