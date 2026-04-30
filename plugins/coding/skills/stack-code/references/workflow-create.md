# Create-Mode Workflow

Use when starting from a feature outline atop a clean `main@origin`.

## Inputs

- Feature outline (markdown bullets or design doc).
- Slug (auto-derived or `--slug`).

## Steps

1. **Bootstrap** — `python3 scripts/bootstrap.py`. Ensures jj installed, colocated, state dir exists.
2. **Detect** — `python3 scripts/detect-mode.py --slug <slug>` should emit `{"mode":"create",...}`. Confirm with user.
3. **Plan PRs from the outline** — for each planned PR, draft a Conventional Commits subject (`feat(<scope>): <summary>`, `fix(<scope>): ...`, `chore(<scope>): ...` etc.) and a one-line summary. Order so spec/scaffolding PRs land before behaviour PRs, and isolate migrations as their own PR.
4. **Per planned PR, write code** — invoke `coding:write-code` to author the change. After each, run `verify.py` (typecheck) before moving on.
5. **Build proposal JSON** — same shape as `propose-splits.py` output: one entry per PR with `{n, scope, files, loc, bookmark, summary, title}`. The `title` field carries the conventional-commit subject; bookmark scope is the commit scope.
6. **Execute stack** — `execute-stack.py --proposal <json> --dry-run`, confirm, then real run.
7. **Open draft PRs** — handled by `execute-stack.py`: it reads `../write-pr/references/templates/pr.md`, fills placeholders, and runs `gh pr create --draft --title "<conv-title>" --body-file <tmp>`.
8. **Verify** — `verify.py --slug <slug>`.

## Key Constraints

- All PRs MUST start in draft (`GIT-PR-STACK-06`).
- Bookmark naming MUST follow `<slug>/NN-<scope>` (`GIT-PR-STACK-01`).
- Bottom-to-top merge order (`GIT-PR-STACK-05`) — never merge PR #02 before PR #01.
- Behaviour changes ride feature flags (`GIT-PR-STACK-04`).
- Every commit subject AND every PR title MUST match the Conventional Commits regex enforced by `lib.validate_conventional_subject`.

## Cross-References

- `references/bookmark-naming.md`
- `references/state-schema.md`
