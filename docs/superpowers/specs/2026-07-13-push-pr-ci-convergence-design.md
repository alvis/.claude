# Push PR CI Convergence Design

## Outcome

Add `coding:push-pr` as the single owner of publishing pull requests and
driving every PR in a stack to green CI. Keep `coding:write-pr` responsible
only for title/body composition and `coding:commit` responsible only for
history mutation.

`coding:commit --create-pr` and `--branch-prefix` remain supported. The
create-PR route delegates immediately to `coding:push-pr`, so existing callers
keep working without retaining a second publishing workflow.

## Ownership

| Skill | Owned responsibility |
|---|---|
| `coding:commit` | Save, split, reorder, absorb, and restack history; delegate `--create-pr` |
| `coding:write-pr` | Produce deterministic Conventional Commit PR title and body |
| `coding:push-pr` | Run CI-equivalent local checks, push/open PRs, monitor CI, fix failures, and converge the stack to green |
| `coding:stack-code` | Create or reshape stacked commits/PRs when a fix belongs outside the current PR |

## Push Workflow

1. Resolve the target change or ordered stack and inspect GitHub workflow files
   plus repository scripts to identify locally runnable CI-equivalent checks.
2. Unless `--skip-local-test` is present, dispatch one read-only small test
   subagent to run those checks and report commands, status, duration, and
   failure evidence. Do not guess at unavailable hosted services.
3. On failure, dispatch the smallest relevant fix subagent. It must diagnose
   the root cause and may not weaken tests, change valid expectations, or add
   ignore/suppression comments merely to pass CI. Test changes are permitted
   only when evidence proves the test itself is wrong.
4. After a local fix, the parent invokes `coding:commit --retrospective`, reruns
   affected checks, and repeats until locally green or concretely blocked.
5. Push bookmarks with `jj git push`, invoke `coding:write-pr`, and create or
   update draft PRs in stack order with `gh`.
6. Start `/loop 5m` with a prompt that dispatches one small polling subagent for
   the whole stack. The poller uses `gh pr checks --json` and reports every PR
   as pending, green, or red.

## CI Convergence

- **Green:** report the green PR or stack and stop/cancel monitoring.
- **Pending:** let the current loop wake again without other work.
- **Red:** the polling subagent collects failed-check links/log evidence and
  wall time, then dispatches one relevant fix subagent with that evidence. It
  reports the diagnosis, edits, check results, and measured CI duration to the
  parent. The parent runs `coding:commit --retrospective`, pushes the rewritten
  bookmark, and restacks downstream PRs when required.
- **Out-of-scope root cause:** create the fix as a separate earlier commit and
  invoke `coding:stack-code` to rebase/reparent the current PR above it. The
  resulting PRs form one stack, and monitoring succeeds only when every PR is
  green.
- **After repush:** schedule one one-shot check for `last CI wall time + 1
  minute`. If that check is still pending, start `/loop 1m`; red or green takes
  the branches above.

The loop is intentionally unbounded while it can make progress. It stops only
on green CI or a concrete blocker requiring user authority or unavailable
external state. `/loop` is session-scoped, so the session must remain open (or
be resumed while the scheduled task is still valid).

## Files

- Add `plugins/coding/skills/push-pr/SKILL.md` for the always-used workflow.
- Add `plugins/coding/skills/push-pr/references/ci-convergence.md` for the
  conditional red/pending/retry branches.
- Add `plugins/coding/skills/push-pr/evals/evals.yaml` for trigger and behavior
  evaluation.
- Relocate and adapt
  `plugins/coding/skills/commit/references/workflow-stacked-pr.md` under
  `push-pr/references/`.
- Update `plugins/coding/skills/commit/SKILL.md` so `--create-pr` delegates to
  `coding:push-pr` while preserving both existing flags.

## Verification

- Baseline pressure evaluations demonstrate that the old workflow stops after
  PR creation and does not guarantee green CI.
- Repository policy validation passes with no new strict plugin-validation
  failures beyond the two recorded baseline warnings.
- Positive evaluations cover local checks, `--skip-local-test`, pending CI,
  red CI with retrospective repair, and out-of-scope stacked repair.
- Near-miss trigger evaluations keep commit-only work in `coding:commit` and
  PR-text-only work in `coding:write-pr`.
- Diff review confirms the old create-PR implementation no longer remains in
  `coding:commit`.
