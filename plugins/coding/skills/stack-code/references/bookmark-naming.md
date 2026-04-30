# Bookmark Naming

Stack bookmarks follow `<slug>/NN-<scope>` per `GIT-PR-STACK-01`.

## Format

- **`<slug>`**: shared kebab-case feature identifier. Letters, digits, dashes only. Max 40 chars (enforced by `lib.slug_derive`).
- **`/`**: literal separator.
- **`NN`**: zero-padded two-digit ordinal (`01`, `02`, ..., `99`). Lexicographic sort matches review order.
- **`-`**: literal separator.
- **`<scope>`**: kebab-case Conventional Commits scope (e.g. `auth`, `customer`, `billing/api`). Derived from the commit's `feat(<scope>): ...` header or, in split-mode, from the cluster's path prefix via `lib.derive_scope_from_paths`. Validated against `^[a-z0-9][a-z0-9._/-]*$`.

The 12-category PR-type taxonomy that previously appeared here is gone — Conventional Commits *types* live in the commit subject (`feat`, `fix`, `chore`, ...), not in the bookmark name.

## Examples

```
auth-rewrite/01-auth
auth-rewrite/02-contracts
auth-rewrite/03-prisma
auth-rewrite/04-migrations
auth-rewrite/05-services
auth-rewrite/06-ui
auth-rewrite/07-ci
```

## Helpers

- `lib.bookmark_name(slug, n, scope)` returns the canonical string and validates the scope.
- `lib.slug_derive(text)` derives a safe slug from a branch/topic name.
- `lib.derive_scope_from_paths(paths)` infers the most-common second path segment as the scope.

## Rules

- **Lexicographic ordering must match merge order** (`GIT-PR-STACK-05`).
- **Reordering**: when reordering an open stack, re-number from the changed point downward and force-push the unmerged bookmarks. Merged-PR ordinals are frozen (`GIT-PR-STACK-03`).
- **Two stacks per slug**: suffix the slug — e.g. `auth-rewrite-phase2/01-auth`.
- **Tooling defaults** (Graphite, Sapling) MUST be configured to emit this format; do not let them invent their own.

## Cross-References

- `GIT-PR-STACK-01` (canonical rule)
- Conventional Commits (`lib.CONVENTIONAL_TYPES`)
