# Git Workflow: Violation Scan

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.

Any single violation blocks submission by default.
If a violation is detected, load the matching rule guide at `./rules/<rule-id>.md`.

## Quick Scan

- DO NOT use a wrong or missing commit type prefix [`GIT-MSG-01`]
- DO NOT use directory paths as scope instead of short package names [`GIT-MSG-02`]
- DO NOT exceed the 72-character hard limit for commit titles [`GIT-MSG-03`]
- DO NOT use past tense or non-imperative mood in commit titles [`GIT-MSG-04`]
- DO NOT use `Fixes` or `Resolves` in footers instead of `Closes` [`GIT-MSG-05`]
- DO NOT exceed the 72-character wrap limit for commit body lines [`GIT-MSG-06`]
- DO NOT use more than 2 comma-separated scopes [`GIT-MSG-07`]
- DO NOT use camelCase or underscores in branch names instead of lowercase-kebab-case [`GIT-BRN-01`]
- DO NOT use branch scopes that don't follow the commit scope convention [`GIT-BRN-02`]
- DO NOT create PRs as ready-for-review without starting as draft [`GIT-PR-01`]
- DO NOT omit the required Summary or Checklist sections from PR descriptions [`GIT-PR-02`]
- DO NOT use PR titles that don't follow the commit message format [`GIT-PR-03`]

## Rule Matrix

| Rule ID | Violation | Bad Examples |
|---|---|---|
| `GIT-MSG-01` | Wrong or missing commit type | `update code`; `fixed bug`; `changes` |
| `GIT-MSG-02` | Directory path used as scope | `feat(client/web-talent): add filter`; `fix(service/profile): correct validation` |
| `GIT-MSG-03` | Title exceeds 72 characters | `feat(authentication-service): add comprehensive OAuth2 login support with multiple providers and token refresh` |
| `GIT-MSG-04` | Past tense or non-imperative mood | `fixed bug`; `added feature`; `refactored code` |
| `GIT-MSG-05` | Wrong footer keyword | `Fixes #123`; `Resolves #456` |
| `GIT-MSG-06` | Body line exceeds 72 characters | Long unwrapped paragraphs in commit body |
| `GIT-MSG-07` | Too many comma-separated scopes | `fix(auth,profile,dashboard): update validation` |
| `GIT-BRN-01` | Non-kebab-case branch name | `feat/addFilter`; `fix/user_profile` |
| `GIT-BRN-02` | Branch scope mismatch | `feat/client-web-talent/add-filter` (uses directory path, not package name) |
| `GIT-PR-01` | PR not started as draft | Creating PR directly as ready-for-review |
| `GIT-PR-02` | Missing required PR sections | PR without Summary or Checklist |
| `GIT-PR-03` | PR title format incorrect | `Add new feature`; `Fix: bug in auth` |
