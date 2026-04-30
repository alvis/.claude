# Correction Workflow

Use when responding to review comments on an open stack PR, when re-running `execute-stack.py` for an already-pushed bookmark, or when fixing a flaw discovered after merge.

`execute-stack.py` exposes a `--fix-up` switch that selects between rewriting an existing change in-place (sub-flows A/B below — `--fix-up` ON) and appending a follow-up commit on the existing bookmark (sub-flow E — `--fix-up` OFF, the default). Sub-flow C is the merged-history guard `--fix-up` MUST respect; sub-flow D is the compat-migration variant of sub-flow C.

## Sub-flows

### A. `jj edit` — fix in the earliest owning unmerged change (`--fix-up` default path)

When the comment targets code introduced in PR `<slug>/NN-<scope>` and that PR is still open, AND `--fix-up` is ON, this is the default rewrite path used by `execute-stack.py --fix-up`:

1. `jj edit <change_id_of_NN>` (from the state file).
2. Apply the fix in the working copy.
3. `jj describe -m <updated-msg>` if the message needs adjustment (the new subject MUST still match the Conventional Commits regex).
4. `jj git push --bookmark <slug>/NN-<scope>` (force-with-lease for unmerged bookmarks) to refresh the open PR. Public git history then reads as if the change had been implemented correctly the first time.
5. `verify.py --slug <slug>` to typecheck.
6. Orchestrator unconditionally invokes `scripts/restack.py --slug <slug>` (see closing invariant) so downstream stack PRs are re-parented onto the new tip.

This obeys `GIT-PR-STACK-02` (fix in the earliest owning unmerged change). All PRs above re-parent automatically because they descend from the edited change in jj's DAG; the explicit `restack.py` invocation guarantees the GitHub-side bases on the open PRs follow.

### B. `jj absorb` — bulk-distribute working-copy edits (`--fix-up` default path)

If you've made multiple small fixes in `@` and want them absorbed into the right ancestor changes, AND `--fix-up` is ON, this is the bulk variant of sub-flow A used by `execute-stack.py --fix-up`:

1. Stage the fixes in the working copy.
2. `jj absorb` — jj rewrites each hunk into the closest ancestor that already touched the same lines.
3. Push every affected bookmark: `jj git push --all` (jj only pushes tracked, unmerged bookmarks; force-with-lease applies to unmerged bookmarks that were rewritten).
4. Orchestrator unconditionally invokes `scripts/restack.py --slug <slug>` (see closing invariant) so downstream stack PRs are re-parented onto the new tips of every affected bookmark.

### C. Corrective PR — merged-history guard (what `--fix-up` MUST refuse)

`GIT-PR-STACK-03` forbids rewriting public history. `execute-stack.py --fix-up` MUST detect this case BEFORE any mutation: it queries `gh pr view --json state` for each affected bookmark and, on `MERGED`, exits with a non-zero status and a clear, actionable error pointing the user to this sub-flow. Open a NEW PR on top of the stack instead:

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

### E. Follow-up commit on the existing bookmark (`--fix-up` OFF, default)

When `--fix-up` is OFF (the default), a re-run of `execute-stack.py` for a bookmark that is already pushed and still open does NOT rewrite the existing owning change. It instead appends a new commit on top of the existing bookmark, so a single PR may carry multiple commits:

1. `jj new <change_id_of_NN>` (from the state file) — start a new change descending from the bookmark's current tip.
2. Apply the new edits in the working copy.
3. `jj describe -m <conventional-msg>` (the subject MUST match the Conventional Commits regex; `lib.commit_message` composes it the same way as the initial run).
4. `jj bookmark set <slug>/NN-<scope> -r @-` — move the bookmark forward to the new commit.
5. `jj git push --bookmark <slug>/NN-<scope>` (no force needed — fast-forward).
6. `verify.py --slug <slug>` to typecheck.
7. Orchestrator unconditionally invokes `scripts/restack.py --slug <slug>` (see closing invariant) so downstream stack PRs are re-parented onto the new tip.

This path leaves the original commit on the PR untouched and adds the follow-up as an additional commit, which is the right shape when reviewers want to see the correction as a discrete diff rather than as a silently-rewritten change.

## Invariant: mandatory restack after any rewrite or follow-up

After ANY successful `execute-stack.py` re-run (sub-flows A, B, or E) that touched an unmerged bookmark — whether `--fix-up` was ON (rewrite) or OFF (follow-up commit) — the orchestrator MUST unconditionally invoke `scripts/restack.py --slug <slug>`. This guarantees downstream stack PRs are re-parented onto the new tip and never depend on stale git commits. A failure of `restack.py` is treated as a hard error and surfaced in the run summary; idempotence in `restack.py` makes the call safe when nothing downstream needs re-parenting.

## Cross-References

- `GIT-PR-STACK-02`, `GIT-PR-STACK-03`, `GIT-PR-STACK-05`
- Conventional Commits allowlist (`lib.CONVENTIONAL_TYPES`)
