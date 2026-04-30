# State File Schema

Path: `.jj/stack-code/<slug>.json` (relative to the repo root resolved by `lib.repo_root()`).

## Shape

```json
{
  "slug": "auth-rewrite",
  "mode": "split",
  "created_at": 1714060800,
  "base": "main@origin",
  "last_op_id": "abcd1234",
  "prs": [
    {
      "n": 1,
      "scope": "auth",
      "bookmark": "auth-rewrite/01-auth",
      "change_id": "qpvxyz12",
      "gh_url": "https://github.com/org/repo/pull/421",
      "title": "feat(auth): introduce session abstraction",
      "status": "draft"
    },
    {
      "n": 2,
      "scope": "contracts",
      "bookmark": "auth-rewrite/02-contracts",
      "change_id": "qpvxyz34",
      "gh_url": "https://github.com/org/repo/pull/422",
      "title": "feat(contracts): publish v2 auth contract",
      "status": "draft"
    }
  ]
}
```

## Field Notes

- **`slug`** — kebab-case feature identifier. Always matches the bookmark prefix.
- **`mode`** — `"create"` or `"split"` from `detect-mode.py`.
- **`created_at`** — unix timestamp; set on first save.
- **`base`** — base ref for the bottom PR (default `main@origin`).
- **`last_op_id`** — output of `jj op log -n1 --no-graph -T 'self.id().short()'`. Updated on every mutation. Rollback with `jj op restore <last_op_id>`.
- **`prs[]`** — ordered list of stack entries.
  - **`n`** — 1-indexed ordinal; matches `NN` in the bookmark.
  - **`scope`** — Conventional Commits scope (lower-case, kebab-case). Drives the bookmark suffix and the commit-subject scope.
  - **`bookmark`** — `<slug>/NN-<scope>`.
  - **`change_id`** — short jj change id (resolvable via `jj log -r <change_id>`).
  - **`gh_url`** — GitHub PR URL returned by `gh pr create`.
  - **`title`** — Conventional Commits PR title (validated by `lib.validate_conventional_subject`).
  - **`status`** — `draft | ready | merged`.

## Mutators

- **`execute-stack.py`** writes new PR entries and updates `last_op_id`.
- **`restack.py`** flips `status` to `merged` for closed/merged PRs and updates `last_op_id`.
- **`verify.py`** is read-only.

## Source-of-truth Guarantees

- The state file is authoritative for ordinal numbering and bookmark mapping.
- A re-run of `execute-stack.py` over an existing entry is a no-op iff the bookmark already maps to the recorded `change_id`.
