# Hosted CI Convergence

This is the conditional hosted-CI loop for `coding:push-pr`.

## Schedule the poller

Immediately after publication, run this command with the actual bottom-to-top
PR URLs substituted for `<stack PR URLs>`:

```text
/loop 5m Check every PR in <stack PR URLs> bottom-up. Run gh pr checks <pr> --json bucket,completedAt,link,name,startedAt,state,workflow for every PR, classify every returned check per ci-convergence.md, collect accessible evidence for red checks, dispatch at most one scoped fixer, and return the bounded poll report to the parent.
```

Capture the returned task/job ID as `active_loop_id`. On green, or before a red
repair is rescheduled, cancel that exact ID with `CronDelete(active_loop_id)`
or the scheduler's natural cancellation operation keyed by the same ID. Never
cancel a loop by cadence or description.

## Poll contract

On every `/loop` wake, the poller queries every PR in bottom-to-top stack order:

```bash
gh pr checks <pr> --json bucket,completedAt,link,name,startedAt,state,workflow
```

Keep the poller read-oriented: it may run `gh` inspection commands and dispatch
exactly one fixer per red cycle, but MUST NOT edit, commit, rebase, restack, or
push. Bound its report to under 1000 tokens. A fixer is the only subagent
allowed to edit, and any review agent is read-only.

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
    provider: github-actions | external
    link: <failed-check URL>
    evidence_status: captured | inaccessible
    log_excerpt: <bounded failure text including expected/received and stack trace when present>
    root_cause: <diagnosis tied to evidence>
    owning_change: <change or outside-current-pr>
fixer:
  status: not_run | fixed | blocked
  files_edited: [<path>]
  checks_run:
    - command: <exact command>
      status: <integer exit status>
      duration_seconds: <elapsed seconds>
schedule:
  task_id: <active_loop_id>
  action: keep | cancel | replace
action: notify_and_cancel | wait | cancel_and_parent_repair | blocked
```

</report>

## Classify every returned check

Do not add `--required` or filter the response. Classify every check from both
its `bucket` and `state`, with precedence red, then pending, then green:

- **Red**: any returned check has a failing/cancel bucket or a failure,
  cancelled, or timed-out state. Process the earliest red PR first because
  descendants may be derivative.
- **Pending**: none are red and any returned check is pending, queued,
  expected, waiting, or in progress, or has no completion timestamp. A newly
  pushed PR with no returned checks is also pending. Keep `active_loop_id`, do
  not edit or dispatch a fixer, and return `action: wait`.
- **Green**: at least one check was returned for each PR and every returned
  check is pass/success, skipping/skipped, or an explicitly accepted neutral
  result. Cancel `active_loop_id`, notify the parent, and stop. This is the
  only success state.

## Red evidence and repair

1. Preserve the failed check's provider and `link` before dispatch. Only when
   the URL is a GitHub Actions run/job URL, derive its run ID and collect the
   failed log with:

   ```bash
   gh run view <run-id> --log-failed
   ```

   If the Actions URL targets a job, use the corresponding `--job` query. For
   an external provider, retain its URL and use provider evidence only when it
   is accessible through the authenticated provider UI, CLI, or API. If
   either branch cannot provide failure details, cancel `active_loop_id` and
   return `action: blocked` with the provider and link; do not invent a run
   ID, log, root cause, or owning change. Otherwise capture the relevant
   error, expected/received values, stack trace, and file/line. Calculate each
   completed check's CI wall time as
   `completedAt - startedAt`; retain the failing cycle's longest relevant wall
   time for the next repush schedule.
2. Cancel `active_loop_id`, then trace the failure to the earliest owning
   change. A changed caller does not
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
   accepts or rejects the fixer diff and invokes
   `coding:commit --retrospective` after every accepted repair. If the cause
   belongs outside the current PR, the parent creates a separate repair commit
   earlier than the current PR with `coding:commit`, then invokes
   `coding:stack-code` to reshape/reparent the current and every downstream PR
   above it. Monitor every PR in the resulting stack.
5. Rerun the affected local checks. On zero exits, the parent follows
   [publish-stack.md](publish-stack.md) to push the repaired bookmark and every
   restacked descendant and to repair PR bases. A nonzero check returns to one
   evidence-backed fixer cycle; unchanged evidence that requires user input or
   external state is a concrete blocker, not permission to weaken checks.

## Repush timing

After repush, use the user's approved monitoring authorization; if it did not
cover a new scheduled task, ask before scheduling. Schedule a one-shot check
for the previous relevant CI wall time plus one minute and capture its task ID.
If only `/loop` supports that delay, run `/loop <wall-time-plus-1m> <the same
explicit poll prompt>`, capture its ID, and cancel that exact ID after its first
wake. A green result notifies and stops; red repeats the evidence workflow. If
the result is pending, schedule `/loop 1m <the same explicit poll prompt>`,
capture the replacement ID, and continue until all PRs are green or a concrete
blocker remains.

Scheduled tasks fire only while the session is open and idle. Unexpired tasks
restore on `--resume` or `--continue`; expired tasks are not replayed.
