# Monitor and repair hosted CI

### 4. Schedule and consume the initial poll

Immediately after every initial publication, including `--skip-local-test`, run
this command with actual bottom-to-top PR URLs substituted:

```text
/loop 5m Dispatch ONE small read-oriented polling subagent for <stack PR URLs> in bottom-up order. Pass it the stack and discovered expected hosted checks, and require it to load and follow the Poll contract in coding:push-pr references/push-pr/30-monitor-and-repair.md; only when it classifies a red check, require it to load references/repair-red-ci.md. Consume its bounded <report>, then take the parent action it requests. The scheduled parent MUST NOT run gh polling itself.
```

Capture the returned task/job ID as `active_loop_id`. Cancel only that exact ID
with `CronDelete(active_loop_id)` or the scheduler's natural cancellation keyed
by the same ID; never cancel by cadence or description.

#### Poll contract

The one poller queries every PR bottom-up, without `--required` or filtering:

```bash
gh pr checks <pr> --json bucket,completedAt,link,name,startedAt,state,workflow
```

Before consuming checks, query the current PR `headRefOid` and require it to
equal the parent's recorded `expected_head_oid`. Treat a mismatch as pending
with explicit stale-head evidence; never accept checks from an older or
unexpected revision.

It is read-oriented: it may inspect with `gh` and, only through the red
reference, dispatch exactly one scoped fixer; it MUST NOT edit, commit, rebase,
restack, or push. It returns under 1000 tokens:

<report>

```yaml
stack:
  - pr: <number-or-url>
    head: <bookmark>
    head_oid: <current remote PR head SHA>
    expected_head_oid: <SHA recorded immediately after the latest push>
    base: <base branch>
    config_ref: <workflow/ruleset ref confirmed for this head/base>
    state: green | pending | red
    expected_checks:
      - name: <workflow job or required status name>
        source: <workflow path/job, branch protection, or ruleset>
    inaccessible_expected_sources: [<source and access error>]
    observed_checks:
      - name: <name>
        workflow: <workflow>
        bucket: <bucket>
        state: <state>
        link: <url>
        started_at: <timestamp>
        completed_at: <timestamp or null>
        wall_time_seconds: <completedAt-startedAt or null>
schedule:
  task_id: <active_loop_id>
  action: keep | cancel | replace
red_repair: <report from repair-red-ci.md or null>
blocker: <configuration/provider blocker or null>
unresolved: [<remaining blocker>]
action: notify_and_cancel | wait | parent_repair | blocked
```

</report>

Classify every returned check from both `bucket` and `state`, with precedence
red, pending, green:

- **Red**: any check has a fail/cancel bucket or failure, cancelled, or
  timed-out state. Cancel `active_loop_id`, process the earliest red PR, and
  load [repair-red-ci.md](../repair-red-ci.md). The poller follows that
  conditional reference before returning its report.
- **Pending**: none are red and any check is pending, queued, expected, waiting,
  in progress, lacks `completedAt`, belongs to a mismatched head SHA, or is an
  expected check not yet observed. Match matrix jobs using the documented
  stable job-name prefix captured during discovery; otherwise require an exact
  name match. Zero observed with a confirmed nonempty expected list is pending.
  Keep `active_loop_id`, make no edits, dispatch no fixer, and return
  `action: wait` for the next wake.
- **Green**: every observed check is pass/success, skipping/skipped, or an
  explicitly accepted neutral result, every expected check has a matched
  terminal accepted observation for `expected_head_oid`, and no observed check
  is red or pending. Zero observed is green only after refreshing the remote PR
  head, confirming current workflow/base required-status/ruleset configuration,
  and proving the expected list empty; retain expected/observed evidence. When
  every PR is green, cancel `active_loop_id`, notify, and stop.

For zero observed checks with inaccessible/unconfirmed expected sources, keep
the PR pending, cancel the loop, and return top-level `action: blocked` with
head/config/source/access evidence. Never use an arbitrary timeout to infer a
state.

Scheduled tasks fire only while the session is open and idle. Unexpired tasks
restore on `--resume` or `--continue`; expired tasks are not replayed.
