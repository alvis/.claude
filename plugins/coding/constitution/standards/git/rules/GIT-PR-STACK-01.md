# GIT-PR-STACK-01: Stack Bookmark Naming

## Severity

error

## Intent

Every stacked-PR bookmark (Jujutsu bookmark, Git branch, or Graphite branch) follows the format `<feature-slug>/NN-<type>` where `<feature-slug>` is the shared kebab-case feature identifier, `NN` is a zero-padded ordinal, and `<type>` is one of the 12 PR categories from `GIT-PR-TYPE-01`.

Consistent bookmark naming makes the stack legible at a glance, lets tooling sort the stack lexicographically, and lets reviewers infer category before opening the PR.

## Fix

```text
auth-rewrite/01-spec
auth-rewrite/02-impl
auth-rewrite/03-integration
auth-rewrite/04-feature-flag
auth-rewrite/05-cleanup
```

Cross-references the conventional-commit type — they are usually the same word, but the bookmark uses the **PR category** (e.g. `mechanical-refactor`), not the commit type (`refactor`):

```text
order-archive/01-migration
order-archive/02-feature-flag
order-archive/03-impl
order-archive/04-ui
```

For single-PR work that is not part of a stack, the existing branch convention from `GIT-BRN-01` and `GIT-BRN-02` applies — `<type>/(<scope>)/<topic>`. The stack format kicks in only when a stack exists.

### Why this matters

- Lexicographic sort matches review order, so `jj log` or `git branch --list` shows the stack top-to-bottom correctly.
- The ordinal makes "land the next one" unambiguous; the category makes the diff's expected shape predictable.
- The shared slug groups the stack across `gh pr list`, dashboards, and CI artefacts.

## Edge Cases

- Reordering a stack mid-flight: re-number from the changed point downward and force-update bookmarks for any stack PR not yet merged. Once a PR has merged, its number is frozen (`GIT-PR-STACK-03`).
- If two stacks share a slug (e.g. two phases of `auth-rewrite`), suffix the slug: `auth-rewrite-phase2/01-spec`.
- Tooling (Graphite, Sapling, jj) sometimes injects its own naming. Configure it to follow this format; do not let tooling defaults override the standard.

## Related

GIT-BRN-01, GIT-BRN-02, GIT-PR-TYPE-01, GIT-PR-STACK-03, GIT-PR-STACK-05
