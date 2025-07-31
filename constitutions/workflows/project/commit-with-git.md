# Commit with Git

**Purpose**: Follow proper git workflow with quality gates and consistent commit messages
**When to use**: Every time you commit code changes to the repository
**Prerequisites**: Code changes ready, tests written, feature branch created

## Steps

### 1. Create Feature Branch

Create a descriptive branch following naming conventions:

```bash
git checkout -b feat/auth/add-oauth
```

Branch format: `<type>/<scope>/<topic>` using lowercase-kebab-case

### 2. Follow TDD Process

- Write tests first (see [TDD workflow](../coding/write-code-tdd.md))
- Implement code to pass tests
- Commit frequently with descriptive messages

### 3. Pre-commit Verification (MANDATORY)

**🔴 CRITICAL: Always run these commands before committing:**

```bash
npm run lint             # Fix linting issues
npm run coverage            # Ensure tests pass
npm run typecheck       # Verify types (if available)
```

**⚠️ NEVER proceed with commit if any of these fail**

### 4. Stage and Commit

```bash
git add .
git commit -m "feat(auth): implement OAuth2 login"
```

Use the [commit message format](../../standards/project/git-workflow.md#commit-format):

```
<type>(<scope>): <summary>   # ≤72 chars, imperative

<body>

<footer>
```

### 5. Push Changes

```bash
git push -u origin feat/auth/add-oauth
```

### 6. Create Pull Request

- Use [PR template](create-pr.md)
- Request reviews from appropriate team members
- Address feedback and update PR

## Standards to Follow

- [Git Workflow Standards](../../standards/project/git-workflow.md)
- [TDD Workflow](../coding/write-code-tdd.md)

## Critical Rules

**🚨 ABSOLUTE PROHIBITIONS:**

- **NEVER use `--no-verify`** when committing - this bypasses essential quality gates
- **NEVER commit without running** `npm run coverage` and `npm run lint` first
- **NEVER commit failing tests or linting errors**

**📋 COMMIT REQUIREMENTS:**

- All commits must pass linting and tests
- Keep commit messages clear and atomic
- Follow TDD practices

## Common Issues

- **Failing pre-commit hooks**: Fix the issues, don't bypass with `--no-verify`
- **Large commits**: Break into smaller, atomic commits with clear messages
- **Vague commit messages**: Use specific, imperative mood descriptions
- **Committed secrets**: Never commit sensitive data, use environment variables
- **Mixed concerns**: One commit should address one logical change
