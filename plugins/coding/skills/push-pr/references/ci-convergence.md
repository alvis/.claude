# Hosted CI Convergence

This is the conditional hosted-CI loop for `coding:push-pr`. The parent owns
history and remote mutations; one small poller reads checks, gathers evidence,
and dispatches at most one scoped fixer for a red cycle.

## Poll contract

On every `/loop` wake, the poller queries every PR in bottom-to-top stack order:

```bash
gh pr checks <pr> --json bucket,completedAt,link,name,startedAt,state,workflow
```

Keep the poller read-oriented: it may run `gh` inspection commands and dispatch
one fixer, but MUST NOT edit, commit, rebase, restack, or push. Bound its report
to under 1000 tokens. A fixer is the only subagent allowed to edit, and any
review agent is read-only.

<report>

```yaml
stack:
  - pr: <number-or-url>
    head: <bookmark>
    base: <base branch>
    state: green | pending | red
    checks:
      - name: <name>
        workflow: <workflow>
        bucket: <bucket>
        state: <state>
        link: <url>
        started_at: <timestamp>
        completed_at: <timestamp or null>
        wall_time_seconds: <completedAt-startedAt or null>
failures:
  - pr: <number-or-url>
    check: <name>
    link: <failed-check URL>
    log_excerpt: <bounded failure text including expected/received and stack trace when present>
    root_cause: <diagnosis tied to evidence>
    owning_change: <change or outside-current-pr>
fixer:
  status: not_run | fixed | blocked
  files_edited: [<path>]
  checks_run:
    - command: <exact command>
      status: <integer exit status>
action: notify_and_cancel | wait | parent_repair | blocked
```

</report>

## Classify the stack

- **Green**: all required checks on every PR are completed in a successful or
  accepted neutral/skipped bucket. Notify the parent with the report and
  cancel `/loop 5m` (or `/loop 1m`). This is the only success state.
- **Pending**: any check is queued, in progress, or lacks `completedAt`, and no
  check is red. A newly pushed PR with no checks observed yet is also pending.
  Do not edit or dispatch a fixer; return `action: wait` for the next scheduled
  wake.
- **Red**: any required check failed, timed out, or was cancelled unexpectedly.
  Process the earliest red PR first because descendants may be derivative.

## Red evidence and repair

1. Preserve the failed check's `link` before dispatch. Derive the Actions run
   ID from it and collect the failed log with:

   ```bash
   gh run view <run-id> --log-failed
   ```

   If the link targets a job, use the corresponding `--job` query. Capture
   the relevant error, expected/received values, stack trace, and file/line.
   Calculate each completed check's CI wall time as
   `completedAt - startedAt`; retain the failing cycle's longest relevant wall
   time for the next repush schedule.
2. Trace the failure to the earliest owning change. A changed caller does not
   own a defect in a shared function introduced below it. Give one relevant
   fixer the failed-check link, bounded log evidence, exact scope, owning
   change, and root-cause guardrails. The fixer reports under 1000 tokens:

   <report>

   ```yaml
   root_cause: <evidence-backed cause>
   owning_change: <change-id or outside-current-pr>
   files_edited: [<path>]
   checks_run:
     - command: <exact command>
       status: <integer exit status>
       duration_seconds: <elapsed seconds>
   unresolved: [<blocker>]
   ```

   </report>

3. The fixer MUST repair the root cause and MUST NOT weaken correct tests,
   alter valid expectations, add ignores/suppressions, or delete checks to get
   green. It may edit a test only when the captured evidence proves the test
   itself is wrong. If expected behavior is ambiguous, return a blocker.
4. The poller returns the evidence and fixer report to the parent. The parent
   reviews the diff and invokes `coding:commit --retrospective` after every
   repair. If the cause belongs outside the current PR, use `coding:commit` to
   create a separate repair commit earlier than the current PR, then invoke
   `coding:stack-code` to rebase/reparent the current and every downstream PR
   above it. Monitor every PR in the resulting stack.
5. Rerun the affected local checks. On zero exits, the parent follows
   [publish-stack.md](publish-stack.md) to push the repaired bookmark and every
   restacked descendant and to repair PR bases. A nonzero check returns to one
   evidence-backed fixer cycle; unchanged evidence that requires user input or
   external state is a concrete blocker, not permission to weaken checks.

## Repush timing

After repush, cancel the current recurring wake and schedule one one-shot check
for the previous relevant CI wall time plus one minute. If the one-shot finds
all PRs green, notify and stop. If it finds a red PR, run the red workflow. If
it finds only pending PRs, start `/loop 1m` and continue until all are green or
a concrete blocker remains.

When only `/loop` is available, implement the one-shot as a loop scheduled for
that delay and cancel it immediately after its first wake. `/loop` works only
while the current session is open; it cannot resume a closed conversation, so
surface that limitation whenever monitoring begins or is handed back.
