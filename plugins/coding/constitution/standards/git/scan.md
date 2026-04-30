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
- DO NOT submit a PR outside the green zone without a Risk and Test plan section [`GIT-PR-SIZE-02`]
- DO NOT submit a red-zone PR without an isolation justification and reviewer-time estimate [`GIT-PR-SIZE-03`]
- DO NOT submit a black-zone PR (>60 files OR >2000 LOC) without surfacing the rejection template from `write.md` [`GIT-PR-SIZE-04`]
- DO NOT open a PR without declaring one of the 12 PR categories in title prefix or body header [`GIT-PR-TYPE-01`]
- DO NOT mix code spec or scaffolding with implementation in the same PR [`GIT-PR-TYPE-02`]
- DO NOT mix database or config migrations with logic changes in the same PR [`GIT-PR-TYPE-03`]
- DO NOT mix mechanical refactors (renames, file moves) with behaviour changes [`GIT-PR-TYPE-04`]
- DO NOT mix generated files with hand-written changes without a clear marker or separation [`GIT-PR-TYPE-05`]
- DO NOT submit a migration PR without a rollback section [`GIT-PR-TYPE-03`]
- DO NOT submit a feature-flag PR without naming the flag and stating its default state [`GIT-PR-STACK-04`]
- DO NOT submit a UI PR without before/after screenshots in the description [`GIT-PR-TYPE-01`]
- DO NOT use stack bookmarks that don't follow `<feature-slug>/NN-<type>` [`GIT-PR-STACK-01`]
- DO NOT fix issues by patching a later PR when the bug originates in an earlier unmerged change [`GIT-PR-STACK-02`]
- DO NOT rewrite public history after a stacked PR merges; use a corrective PR instead [`GIT-PR-STACK-03`]
- DO NOT land behaviour changes outside a feature flag unless the change is tiny, isolated, and reversible [`GIT-PR-STACK-04`]
- DO NOT merge stacked PRs out of order or skip rebasing the next PR onto main after the lower lands [`GIT-PR-STACK-05`]
- DO NOT open stacked PRs as ready-for-review; always start in draft [`GIT-PR-STACK-06`]

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
| `GIT-PR-SIZE-01` | Green-zone definition not respected | (informational — establishes ≤15 files OR ≤500 LOC baseline) |
| `GIT-PR-SIZE-02` | Yellow-zone PR missing Risk or Test plan | 22 files / 900 LOC PR with no Risk section |
| `GIT-PR-SIZE-03` | Red-zone PR without justification or reviewer-time estimate | 45 files / 1500 LOC PR with no `## Why this size` block |
| `GIT-PR-SIZE-04` | Black-zone PR submitted without rejection template | 80 files / 3500 LOC PR opened ready-for-review |
| `GIT-PR-TYPE-01` | Missing PR category declaration | `feat(api): add export` with no category prefix or body header among the 12 archetypes |
| `GIT-PR-TYPE-02` | Spec or scaffolding mixed with implementation | One PR adds `domain/order.ts` types and the `processOrder()` impl |
| `GIT-PR-TYPE-03` | Migration mixed with logic, or migration PR missing rollback | Prisma migration + new business rule in same PR; migration PR with no `## Rollback` |
| `GIT-PR-TYPE-04` | Mechanical refactor mixed with behaviour change | Rename `User` -> `Account` plus a new `suspend()` method in same PR |
| `GIT-PR-TYPE-05` | Generated files mixed with hand-written code without marker | `pnpm-lock.yaml` + lockfile-shaped diffs alongside hand edits, no separator |
| `GIT-PR-STACK-01` | Bookmark naming wrong | `auth-rewrite-spec`; `01_spec`; `feature/auth/spec` |
| `GIT-PR-STACK-02` | Fix applied at the wrong stack level | Adding a defensive null check in PR-03 for a bug introduced in PR-01 (still unmerged) |
| `GIT-PR-STACK-03` | History rewrite after merge | `git push --force` to a branch whose lower PR has already merged |
| `GIT-PR-STACK-04` | Behaviour change without flag, or flag PR missing default state | Switching auth provider in a non-flagged PR; `feature-flag` PR not stating `default: off` |
| `GIT-PR-STACK-05` | Out-of-order merge or missing rebase | Merging PR-03 before PR-02; not rebasing PR-04 onto main after PR-03 lands |
| `GIT-PR-STACK-06` | Stacked PR opened ready-for-review | Stack PR created without `--draft` |
