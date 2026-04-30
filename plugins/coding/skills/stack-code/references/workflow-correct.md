# Correction Workflow

Use when responding to review comments on an open stack PR, or when fixing a flaw discovered after merge.

## Sub-flows

### A. `jj edit` — fix in the earliest owning unmerged change

When the comment targets code introduced in PR `<slug>/NN-<scope>` and that PR is still open:

1. `jj edit <change_id_of_NN>` (from the state file).
2. Apply the fix in the working copy.
3. `jj describe -m <updated-msg>` if the message needs adjustment (the new subject MUST still match the Conventional Commits regex).
4. `jj git push --bookmark <slug>/NN-<scope>` to refresh the open PR.
5. `verify.py --slug <slug>` to typecheck.

This obeys `GIT-PR-STACK-02` (fix in the earliest owning unmerged change). All PRs above re-parent automatically because they descend from the edited change in jj's DAG.

### B. `jj absorb` — bulk-distribute working-copy edits

If you've made multiple small fixes in `@` and want them absorbed into the right ancestor changes:

1. Stage the fixes in the working copy.
2. `jj absorb` — jj rewrites each hunk into the closest ancestor that already touched the same lines.
3. Push every affected bookmark: `jj git push --all` (jj only pushes tracked, unmerged bookmarks).

### C. Corrective PR — when the flaw is in merged history

`GIT-PR-STACK-03` forbids rewriting public history. Open a NEW PR on top of the stack:

1. `jj new <top_bookmark>`.
2. Apply the corrective fix.
3. `jj describe -m "fix(<scope>): <correction>"` (Conventional Commits subject required).
4. `jj bookmark set <slug>/NN+1-<scope>` per `GIT-PR-STACK-01`.
5. `jj git push --bookmark <slug>/NN+1-<scope>`.
6. Compose the body from `../write-pr/references/templates/pr.md` (or invoke `coding:write-pr` for a one-off), then `gh pr create --draft --title "fix(<scope>): <correction>" --body-file <tmp> --base <top_bookmark>`.

### D. Compat-migration sub-flow

When merged-upstream code requires a compatibility shim before the corrective fix can land:

1. Open a migration PR FIRST (`feat(<scope>)!: ...` or `chore(migrations): ...` per the change), isolated from logic per `GIT-PR-STACK-02`.
2. Land it.
3. Open the corrective PR (sub-flow C) with the migration as its base.
4. Land them bottom-to-top per `GIT-PR-STACK-05`.

## Cross-References

- `GIT-PR-STACK-02`, `GIT-PR-STACK-03`, `GIT-PR-STACK-05`
- Conventional Commits allowlist (`lib.CONVENTIONAL_TYPES`)
