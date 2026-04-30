# Restack Workflow

Use when:
- `main@origin` has moved while the stack was in review.
- A lower PR in the stack merged (others must rebase to avoid double-merge conflicts per `GIT-PR-STACK-05`).
- Author needs to refresh open bookmarks against the new base.

## Steps

1. **Fetch** — `python3 scripts/restack.py --slug <slug> --dry-run`. Internally runs `jj git fetch`.
2. **Detect merged bookmarks** — `gh pr view <bookmark> --json state` per stack entry. Drop merged ones from the active list (state file marks `status: merged`).
3. **Plan rebases** — for each surviving (unmerged) PR in order, the planned base is either `main@origin` (if it's the new bottom) or the previous unmerged bookmark.
4. **Review the plan** with the user.
5. **Execute** — drop `--dry-run`. For each surviving PR:
   - `jj rebase -b <bookmark> -d <new_base>`
   - `jj git push --bookmark <bookmark>` (force-push allowed only on UNMERGED bookmarks; never on merged ones — `GIT-PR-STACK-03`).
   - `gh pr edit <bookmark> --base <new_base>` to re-parent the PR.
6. **State update** — `state.last_op_id` records the latest `jj op log` id for rollback (`jj op restore <id>`).

## Edge Cases

- **PR closed without merging** — treat as "merged" for stack purposes (it's no longer in review); the next PR rebases onto the original base.
- **Conflicting rebase** — `jj rebase` will surface conflicts; resolve via `jj resolve` and re-run `restack.py` (idempotent).
- **Force-push protection** — never force-push a merged bookmark. `restack.py` skips entries whose `status == "merged"`.

## Cross-References

- `GIT-PR-STACK-03` (never rewrite public history)
- `GIT-PR-STACK-05` (bottom-to-top merge order)
- `references/state-schema.md`
