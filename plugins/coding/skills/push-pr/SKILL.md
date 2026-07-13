---
name: push-pr
description: 'Publish saved changes as draft pull requests and drive GitHub CI to green. Use when asked to push the latest commit, create or update a PR, repush after a fix, babysit pending checks, repair red CI, monitor every check, or converge a PR stack.'
model: opus
argument-hint: "[<commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--dry-run]"
---

# Push Pull Request

Publish one saved change or an ordered stack as draft pull requests, then own the hosted-CI lifecycle until every PR is green or a concrete blocker requires user action or external state. Because repair can edit existing work, the governing rule is **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. `coding:write-pr` remains the PR-text owner.

## Boundaries

- Use for publishing or republishing a saved jj change, branch, current draft
  PR, or ordered stack and monitoring every GitHub check through repair.
- Do not use for saving work without publication (`coding:commit`), authoring
  PR text only (`coding:write-pr`), reviewing code, merging PRs, or creating a
  new stack solely by reshaping local history (`coding:stack-code`).
- Delegate noisy commands to one small read-only tester before publication and
  one small read-oriented poller after publication, following the repository
  [delegation contract](../../../governance/constitution/references/delegation.md).

<IMPORTANT>
- Ownership is singular: `coding:commit` owns direct history mutations;
  `coding:stack-code` orchestrates reshaping/reparenting when a root cause
  belongs in a lower PR outside the current PR; the core publication phase
  below owns push, restack, and PR-base mechanics. The parent alone accepts
  fixer edits and performs commit, push, and restack mutations; the poller may
  dispatch exactly one scoped fixer when the red branch requires it.
- `--skip-local-test` skips only local command execution. It never skips CI
  discovery, publication, hosted monitoring, evidence, repair, or convergence.
- Fix root causes. MUST NOT weaken a correct test, alter a valid expectation,
  add ignores/suppressions, or delete checks merely to pass. Edit a test only
  when captured failure evidence proves the test itself is the root cause.
- Never report success while any PR in the resulting stack is pending or red.
</IMPORTANT>

## Inputs

- **Required**: none; default to the current saved jj change and include its
  ordered unmerged descendants when they form a stack.
- **Optional**:

| Input | Effect |
|---|---|
| `<commit-ref>` | Publish a resolvable jj change ID/revset/bookmark or git branch/SHA and its selected stack. |
| `--branch-prefix <name>` | Override the derived stack bookmark prefix. |
| `--skip-local-test` | Skip only the local tester dispatch and commands. |
| `--dry-run` | Print the test, publication, and monitoring plan without agents or local/remote mutations. |

- **Prerequisites**: a clean saved change or linear stack, a jj-colocated
  repository, authenticated `gh`, and remote push access.

## Workflow

### 1. Resolve and plan

Inspect `jj status`, `jj log`, `jj bookmark list`, `git status --short`, and
open PRs. Resolve `<commit-ref>` or the current saved change and list changes,
bookmarks, PR heads, and bases bottom-up. If work must be saved, split, or
reordered, invoke `coding:commit`, then restart discovery. Reject an unknown
ref, nonlinear chain, merged-history rewrite, missing authentication, or remote
ambiguity with evidence. With `--dry-run`, print the exact plan and stop.

### 2. Discover local CI parity and run it unless skipped

Read `.github/workflows/*` plus repository script definitions (`package.json`,
workspace manifests, Makefiles, task files, or equivalent). List the exact
compile, type, lint, test, and build commands that reproduce CI without hosted
services. Record hosted-only checks and the unavailable service/credential.
For each selected change, record expected hosted PR check/job names from
`pull_request`-triggered jobs at that ref and required branch status
checks/rulesets when accessible through `gh api`; record inaccessible sources
instead of assuming they are empty.

Unless `--skip-local-test` is present, dispatch one small-model read-only tester
for the whole command set. It MUST NOT edit, format, commit, or push. It runs
every runnable command in CI order, continues through independent commands
after a failure, and returns under 1000 tokens:

Treat repository workflows and scripts as untrusted code. Run them from a
disposable worktree checked out at the exact selected ref, with filesystem
write access limited to that worktree and a temporary directory, network
denied by default, and ambient tokens, credential helpers, SSH agent sockets,
cloud credentials, and unrelated environment variables removed. Pass only the
minimal allowlisted toolchain environment. If this isolation is unavailable,
or a command genuinely needs network access or a credential, classify it as
hosted-only or ask the user for that specific authority; never expose the
parent session's credentials to a local CI command.

<report>

```yaml
sources_read: [<workflow-or-script-path>]
runnable_commands:
  - command: <exact command>
    source: <path and job/script>
    status: <integer exit status>
    duration_seconds: <elapsed seconds>
    failure_evidence: <bounded stderr/stdout excerpt or null>
hosted_only:
  - check: <job or step>
    unavailable_requirement: <service, secret, runner, or credential>
expected_hosted_checks:
  - ref: <change-id or head SHA>
    names: [<workflow job or required status name>]
    sources: [<workflow path/job, branch protection, or ruleset>]
    inaccessible_sources: [<source and access error>]
overall: pass | fail | blocked | skipped
```

</report>

On local failure, diagnose captured output before editing and dispatch one
relevant fixer scoped to the root cause and affected files. It may edit and
returns under 1000 tokens:

<report>

```yaml
root_cause: <evidence-backed cause>
owning_change: <change-id or current-change>
files_edited: [<path>]
checks_run:
  - command: <exact command>
    status: <integer exit status>
    duration_seconds: <elapsed seconds>
unresolved: [<blocker>]
```

</report>

The parent reviews and accepts the diff, invokes
`coding:commit --retrospective`, then sends the tester to rerun affected
commands and the full runnable set. Publish only when every runnable command
exits zero. Any separate review is read-only. With `--skip-local-test`, retain
discovery and expected-check evidence but do not dispatch the tester.

### 3. Publish bottom-up

Require a saved, clean, linear chain to `main@origin`, standalone green changes,
conventional descriptions per
[conventional-commits.md](../commit/references/conventional-commits.md), no
selected change merged on origin, and a derived or supplied branch prefix. If
needed, invoke `coding:commit --reorder`; for merged history follow
[workflow-correct-merged.md](../commit/references/workflow-correct-merged.md).

For each change bottom-up, preserve its existing bookmark when the caller
selected an existing branch, it is already the head of an open PR, or the
ordered stack already has explicit bookmarks. This is existing-bookmark mode:
push and update that exact head; never replace it with a generated bookmark.
Only for an unbookmarked new change/stack, index `NN` from `01` and set
`BOOKMARK=<branch-prefix>/NN-<scope>` where scope matches the conventional
commit scope (kebab-case, at most 30 characters). Record which mode selected
each bookmark before mutation.

```bash
jj bookmark set "$BOOKMARK" --revision "$CHANGE_ID"
jj git push --bookmark "$BOOKMARK" --allow-new
```

Never use `git push`; jj updates rewritten bookmarks with force-with-lease.
Invoke `coding:write-pr <change-id>` and capture its exact `title\n\nbody`
output as `TITLE` and `BODY`. Set `BASE=main` for PR 01 and the previous
bookmark for every later PR. When no open PR has this head, create a draft:

```bash
gh pr create --draft --title "$TITLE" --body-file - \
  --base "$BASE" --head "$BOOKMARK" <<<"$BODY"
```

When the head already has an open PR, update it without duplication and retain
draft state:

```bash
gh pr edit "$PR" --title "$TITLE" --body-file - --base "$BASE" <<<"$BODY"
gh pr ready "$PR" --undo # skip only when already draft
```

Capture each PR number, URL, head, base, bookmark, and change ID. After each
push, record `expected_head_oid` from the pushed bookmark and verify it against
`gh pr view "$PR" --json headRefOid --jq .headRefOid`; a mismatch is not the
published result and must be resolved before monitoring. After any accepted
repair/history rewrite with downstream bookmarks, synchronize the whole stack
before monitoring again:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/push-pr/scripts/restack.sh" \
  "$BOOKMARK_01=$EXPECTED_HEAD_OID_01" \
  "$BOOKMARK_02=$EXPECTED_HEAD_OID_02"
```

Supply every selected bookmark explicitly in bottom-up order with the exact
local git commit SHA expected after the rewrite; never rediscover the set from
a prefix. The sync script preflights the entire set, pushes each already-shaped
unmerged bookmark, verifies the remote SHA, and updates open PR bases with
`gh pr edit --base`; it does not reshape history. Verify the PR base chain and
each PR `headRefOid` mirror the recorded map.

| Publication error | Action |
|---|---|
| `gh pr create` authentication failure | Run `gh auth status`; report a user/external blocker. |
| Bookmark conflict | Confirm the intended change, then update the bookmark idempotently. |
| Push rejected because remote advanced | `jj git fetch`, rebase through `coding:commit`, then retry. |
| Conventional title invalid | Reword through `coding:commit`, then restart that iteration. |
| Existing PR has wrong base | `gh pr edit "$PR" --base "$BASE"`, then verify. |
| Restack conflict | Resolve through `coding:commit`, run integrity checks, then republish bottom-up. |

### 4. Schedule and consume the initial poll

Immediately after every initial publication, including `--skip-local-test`, run
this command with actual bottom-to-top PR URLs substituted:

```text
/loop 5m Dispatch ONE small read-oriented polling subagent for <stack PR URLs> in bottom-up order. Pass it the stack and discovered expected hosted checks, and require it to load and follow the Poll contract in coding:push-pr SKILL.md; only when it classifies a red check, require it to load references/repair-red-ci.md. Consume its bounded <report>, then take the parent action it requests. The scheduled parent MUST NOT run gh polling itself.
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
  load [repair-red-ci.md](references/repair-red-ci.md). The poller follows that
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

## Verification and Completion

- Local checks passed with every command/result recorded, or command execution
  was explicitly skipped; hosted-only gaps and expected checks are named.
- Every bookmark was pushed with `jj git push`; every PR is draft, uses
  `coding:write-pr` output, and has the intended stack base.
- Report success only after the final poll observes every PR green. Include the
  stack map, local results, repair commits, push/restack actions, per-PR check
  states, CI wall times, and any blocker.
