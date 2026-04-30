# Split-Mode Workflow (Spike → Slice)

Use when an existing chunky working copy or branch needs slicing into a stack before review.

## Inputs

- Working copy with >5 changed files OR >300 LOC of diff vs `main@origin` (the same threshold `detect-mode.py` uses).
- Slug (auto-derived or `--slug`).

## Steps

1. **Bootstrap** — `python3 scripts/bootstrap.py`.
2. **Detect** — `python3 scripts/detect-mode.py --slug <slug>` should emit `{"mode":"split",...}`. Confirm.
3. **Propose splits** — `python3 scripts/propose-splits.py --slug <slug> > /tmp/plan.json`. The script:
   - Reads `jj diff --name-only` (falls back to git).
   - Clusters paths by top-level prefix (`--depth N`, default 2).
   - Derives a Conventional Commits *scope* per cluster from the most common second path segment (`lib.derive_scope_from_paths`). Bookmark slugs use this scope (`<slug>/NN-<scope>`), not a PR-type taxonomy.
   - Co-locates `*.spec.ts` / `*_test.py` with their implementation (`GIT-PR-SIZE-01` edge cases).
   - Orders clusters lexicographically by path prefix; reviewers re-order in the proposal JSON if needed.
4. **Review proposal** — present the table on stderr to the user. Allow edits to `/tmp/plan.json` (re-order, re-scope, re-bookmark, set explicit `title`).
5. **Dry-run** — `execute-stack.py --proposal /tmp/plan.json --dry-run`. Print the planned `jj`/`gh` commands. The dry-run validates every PR's title against the Conventional Commits regex up-front; a violation aborts before any mutation.
6. **Approve** — confirm with user; drop `--dry-run`.
7. **Execute** — `execute-stack.py --proposal /tmp/plan.json`. Splits, describes, bookmarks, pushes, opens draft PRs with conventional titles and the unified body from `../write-pr/references/templates/pr.md`.
8. **Verify** — `verify.py --slug <slug>`.

## Clustering Rationale

- **Path-prefix clustering** keeps the file-system layout as the primary signal; reviewers naturally read by directory.
- **Tests stay with implementation** because `GIT-PR-SIZE-01` edge cases call this out (a green-LOC PR with a 400-line test file is still green).
- **Scope, not type**, drives bookmark naming. The Conventional Commits *type* (`feat`, `fix`, `chore`, ...) lives in the commit subject and the PR title; the *scope* (`auth`, `customer`, ...) lives in both the commit subject and the bookmark suffix.

## Cross-References

- `references/bookmark-naming.md`
- `references/state-schema.md`
