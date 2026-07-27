# GIT-PR-STACK-01: Stack Bookmark Naming

## Severity

error

## Intent

Every stacked-PR bookmark (Jujutsu bookmark, Git branch, or Graphite branch) follows the format `<feature-slug>/NN-<scope>` where `<feature-slug>` is the shared kebab-case feature identifier, `NN` is a zero-padded ordinal, and `<scope>` is a short kebab-case summary of what that PR does.

`<scope>` is free-form. It is not drawn from the `GIT-PR-TYPE-01` categories, and it need not match the conventional-commit scope either — a PR declares its category in the PR itself, so encoding one in the bookmark would only duplicate it less reliably. Write whatever names the slice: `02-impl`, `03-token-refresh`, `04-rollback-path`.

Consistent bookmark naming makes the stack legible at a glance, lets tooling sort the stack lexicographically, and tells a reviewer what each PR covers before they open it.

When the stack belongs to an engineering work stream, `<feature-slug>` is `<type>/<work-id>` — the stream's branch — so a work ID of `work-id-naming` gives `feat/work-id-naming/02-impl`. The stream is then identified from any bookmark in the stack instead of being asked for at every transition.

## Fix

```text
auth-rewrite/01-spec
auth-rewrite/02-impl
auth-rewrite/03-integration
auth-rewrite/04-feature-flag
auth-rewrite/05-cleanup
```

Any short kebab-case summary works; these read as categories only because that is often the clearest way to say what a slice does:

```text
order-archive/01-migration
order-archive/02-feature-flag
order-archive/03-impl
order-archive/04-ui
```

For single-PR work that is not part of a stack, the existing branch convention from `GIT-BRN-01` and `GIT-BRN-02` applies — `<type>/(<scope>)/<topic>`. The stack format kicks in only when a stack exists. An engineering work stream follows the same split: one PR is the bare `<type>/<work-id>`, and a stack is numbered beneath it. The two cannot coexist, since git stores refs as files, so a stream that grows past one PR renames its branch into the namespace first.

### Why this matters

- Lexicographic sort matches review order, so `jj log` or `git branch --list` shows the stack top-to-bottom correctly.
- The ordinal makes "land the next one" unambiguous; the scope says what the diff covers.
- The shared slug groups the stack across `gh pr list`, dashboards, and CI artefacts.

## Edge Cases

- Reordering a stack mid-flight: re-number from the changed point downward and force-update bookmarks for any stack PR not yet merged. Once a PR has merged, its number is frozen (`GIT-PR-STACK-03`).
- If two stacks share a slug (e.g. two phases of `auth-rewrite`), suffix the slug: `auth-rewrite-phase2/01-spec`.
- Tooling (Graphite, Sapling, jj) sometimes injects its own naming. Configure it to follow this format; do not let tooling defaults override the standard.

## Related

GIT-BRN-01, GIT-BRN-02, GIT-PR-TYPE-01, GIT-PR-STACK-03, GIT-PR-STACK-05
