---
name: write-pr
description: 'Author a conventional-commit PR title and unified body from a jj or git change ref, then publish saved changes as draft pull requests and drive GitHub CI to green. Use for PR descriptions, draft pull requests, and callers that need a unified title/body template from a commit, and when asked to push the latest commit, create or update a PR, repush after a fix, babysit pending checks, repair red CI, monitor every check, or converge a PR stack.'
model: opus
argument-hint: "[<commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--dry-run]"
---

# Write Pull Request

Turn one saved change or an ordered stack into live, green draft pull requests.
This skill composes a deterministic, regex-validated Conventional Commits PR
title and a unified PR body from each commit, publishes the change (or stack)
bottom-up as draft PRs, then owns the hosted-CI lifecycle until every PR is
green or a concrete blocker requires user action or external state. Because
repair can edit existing work, the governing rule is **Coherence Mandate.**
Every edit must produce one continuous, deliberate work. Rewrite over
restructure, restructure over integrate, never append. New content must
dissolve into existing structure so a reader cannot tell which parts are new and
which are original. Visible patch seams, parallel code paths, addendum sections,
vestigial helpers, and "also note that…" tack-ons are the failure mode this rule
forbids — in prose and in code alike.

Zone enforcement (GIT-PR-SIZE-01..04) belongs to the reviewer, not to this
skill.

## Boundaries

- Use for: composing a PR title and body for the current jj working-copy change
  or any resolvable commit ref, and publishing or republishing a saved jj
  change, branch, current draft PR, or ordered stack while monitoring every
  GitHub check through repair. `coding:commit --create-pr` reaches this path
  through its required handoff.
- Do not use for: saving work without publication (`coding:commit`), reviewing
  code, merging PRs (`coding:merge-pr`), or creating a new stack solely by
  reshaping local history (`coding:commit --reorder`).
- Multi-template directories (`.github/PULL_REQUEST_TEMPLATE/*.md`) are
  intentionally ignored — selecting between them is a human choice and out of
  scope.
- Delegate noisy commands to one small read-only tester before publication and
  one small read-oriented poller after publication, following the repository
  [delegation contract](../../../governance/constitution/references/delegation.md).

<IMPORTANT>
- Ownership is singular: `coding:commit` owns direct history mutations;
  its `--reorder` workflow owns reshaping/reparenting when a root cause belongs
  in a lower PR outside the current PR; the core publication phase below owns
  push, restack, and PR-base mechanics. The parent alone accepts
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

- **Required**: none; default to the current saved jj working-copy change (`@`)
  and include its ordered unmerged descendants when they form a stack.
- **Optional**:

| Input | Effect |
|---|---|
| `<commit-ref>` | Publish a resolvable jj change ID/revset/bookmark or git branch/SHA and its selected stack. Any jj revset (`@`, `@-`, a change id) or git ref (`HEAD`, `HEAD~1`, a SHA) also selects the commit to author from; behavior is deterministic given the ref. |
| `--branch-prefix <name>` | Override the derived stack bookmark prefix. |
| `--skip-local-test` | Skip only the local tester dispatch and commands. |
| `--dry-run` | Print the test, publication, and monitoring plan without agents or local/remote mutations. |

- **Prerequisites**: a clean saved change or linear stack, a jj-colocated
  repository, authenticated `gh`, and remote push access. `jj` on PATH (falls
  back to `git` for commit-text resolution when `jj` is absent).

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Publication-only runs may proceed
without creating work artifacts; before any red-CI repair, run the resolver,
ask only on `work_id_required`, and use the resolved work root. Give each fixer
a mission capsule with only the relevant contract/evidence paths. Fixers never
write PM-owned pointers or overview files.

## Workflow

### 1. Resolve and plan

Inspect `jj status`, `jj log`, `jj bookmark list`, `git status --short`, and
open PRs. Resolve `<commit-ref>` or the current saved change and list changes,
bookmarks, PR heads, and bases bottom-up. If work must be saved, split, or
reordered, invoke `coding:commit`, then restart discovery. Reject an unknown
ref, nonlinear chain, merged-history rewrite, missing authentication, or remote
ambiguity with evidence. With `--dry-run`, print the exact plan and stop.

### 2. Discover local CI parity and run it unless skipped

Resolve the target repository's main source checkout first:

```bash
SOURCE_REPO_ROOT=$(git rev-parse --show-toplevel)
```

Use that main checkout for read-only discovery of local environment sources and
command-level references. Inspect `.github/workflows/*`, `package.json`,
workspace manifests, Makefiles, and task files there, plus `.env`, `.env.local`,
and `.env.test` when present. These local files may be ignored and therefore
absent from a disposable worktree. Do not execute repository commands from the
main checkout or copy secret values into a report.

Then create a detached disposable worktree at the resolved target SHA and
install a guarded cleanup trap:

```bash
TEST_WORKTREE=$(mktemp -d)
cleanup() {
  if [ -n "${TEST_WORKTREE:-}" ] && [ "$TEST_WORKTREE" != / ]; then
    git worktree remove --force "$TEST_WORKTREE" >/dev/null 2>&1 ||
      rm -rf -- "$TEST_WORKTREE"
  fi
}
trap cleanup EXIT HUP INT TERM
git worktree add --detach "$TEST_WORKTREE" "$TARGET_SHA"
```

The parent uses this worktree to confirm selected-revision commands. If local
testing is dispatched,
give the path and cleanup ownership to the tester; it must install the same
guarded trap in its process before running commands and report cleanup status.
If testing is skipped or blocked, the parent runs `cleanup` before proceeding.

Read the same workflow and script definitions from `"$TEST_WORKTREE"` to
confirm the exact commands at the selected SHA, and inspect workflow `env`,
`secrets.*`, `vars.*`, and command-level environment references there for
revision drift. List the exact compile, type, lint, test, and build commands
that reproduce CI without hosted services. Record variable names and source
presence only; never copy secret values into a report. For every required
variable, verify that the isolated tester can receive it from a user-approved
source in the main checkout or another explicitly approved location; an env
file does not need to be copied into the worktree. Record hosted-only checks
and unavailable services or credentials. If a required variable is missing and
`--skip-local-test` was not supplied, ask the user to confirm its intended
source or location; if it remains unavailable, ask whether to use
`--skip-local-test` and proceed with publishing. When the flag was supplied,
record the missing variable as a hosted-only gap and do not execute local
commands. Do not guess a secret source or silently run with an empty value.
For each selected change, record expected hosted PR check/job names from
`pull_request`-triggered jobs at that ref and required branch status
checks/rulesets when accessible through `gh api`; record inaccessible sources
instead of assuming they are empty.

Unless `--skip-local-test` is present, dispatch one small-model read-only tester
for the whole command set. It MUST NOT edit, format, commit, or push. It runs
every runnable command in CI order, continues through independent commands
after a failure, and returns under 1000 tokens:

Treat repository workflows and scripts as untrusted code. The tester uses the
discovery worktree and removes it on every exit path. Before running
commands, it installs the guarded trap shown above in its own process and runs
the allowlisted commands from `"$TEST_WORKTREE"`.

The cleanup trap is mandatory after pass, failure, cancellation, or blocked
environment discovery. Limit filesystem writes to that worktree and a
temporary directory, deny network by default, and remove ambient tokens,
credential helpers, SSH agent sockets, cloud credentials, and unrelated
environment variables. Pass only the minimal allowlisted toolchain environment.
If this isolation is unavailable, or a command genuinely needs network access
or a credential, classify it as hosted-only or ask the user for that specific
authority; never expose the parent session's credentials to a local CI command.

<report>

```yaml
sources_read: [<workflow-or-script-path>]
required_environment:
  - name: <variable name>
    declared_source: <workflow/package/.env source>
    worktree_status: present | missing | hosted-only
runnable_commands:
  - command: <exact command>
    source: <path and job/script>
    status: <integer exit status>
    duration_seconds: <elapsed seconds>
    failure_evidence: <bounded stderr/stdout excerpt or null>
hosted_only:
  - check: <job or step>
    unavailable_requirement: <service, secret, runner, or credential>
temporary_worktree_cleanup: passed | blocked
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
Run the [Author the PR text](#author-the-pr-text) sub-procedure for this change
and capture its exact `title\n\nbody` output as `TITLE` and `BODY`. Set
`BASE=main` for PR 01 and the previous bookmark for every later PR. When no open
PR has this head, create a draft:

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
bash "${CLAUDE_PLUGIN_ROOT}/skills/write-pr/scripts/restack.sh" \
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
/loop 5m Dispatch ONE small read-oriented polling subagent for <stack PR URLs> in bottom-up order. Pass it the stack and discovered expected hosted checks, and require it to load and follow the Poll contract in coding:write-pr SKILL.md; only when it classifies a red check, require it to load references/repair-red-ci.md. Consume its bounded <report>, then take the parent action it requests. The scheduled parent MUST NOT run gh polling itself.
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

### Author the PR text

Compose the deterministic `title\n\nbody` for one commit. This sub-procedure is
self-contained: step 3 runs it at publish time, and a caller that needs only PR
text (no publication) may run just this block and consume its stdout. It never
invokes `gh`.

1. Resolve the commit ref: try `jj log -r <ref> --no-graph -T 'description'`
   first; fall back to `git log -1 --format=%B <ref>` when `jj` exits
   non-zero. Unknown ref: exit 2, print "no such revision" plus the failing
   ref. Neither `jj` nor `git` available: exit 3, "no commit source
   available".
2. Extract the subject (first non-empty line) and body (everything after the
   first blank line). Recognize commit trailers (`Refs:`, `Closes:`,
   `Fixes:`, `Breaking-Change:`, `Testing:`, `Manual-Test:`) for routing in
   step 5.
3. Validate the subject against the Conventional Commits regex — the
   canonical conventional-commits.org type allowlist with optional `(scope)`
   and `!` for breaking changes:

   ```
   ^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([\w./-]+\))?!?: .+
   ```

   On mismatch, exit 2 with the failing token, the regex, and the offending
   subject. This skill is the single source of truth for the regex; it is
   mirrored in `coding:commit` (`references/conventional-commits.md`).
4. Resolve the template — first hit wins, paths relative to the repo root:

   1. `.github/PULL_REQUEST_TEMPLATE.md`
   2. `.github/pull_request_template.md`
   3. `docs/PULL_REQUEST_TEMPLATE.md`
   4. `docs/pull_request_template.md`
   5. `PULL_REQUEST_TEMPLATE.md`
   6. `pull_request_template.md`

   <IMPORTANT>A repo-local template is emitted verbatim — never fill
   placeholders in or otherwise mutate a foreign template; skip step 5
   entirely.</IMPORTANT> When none exist, fall back to the bundled default at
   [references/templates/pr.md](references/templates/pr.md) and continue.
   When the bundled default is also missing: exit 4, print the path that
   failed to resolve.
5. Fill the bundled default's placeholders from the commit body:
   - `{{summary_paragraph}}` — first body paragraph (≤3 sentences); fall back
     to the subject text after `: ` when the body is empty.
   - `{{context_body}}` — content under `## Context` / `Why:` /
     `Background:`, if present.
   - `{{implementation_body}}` — content under `## Implementation` / `What:`
     / `How:`, if present.
   - `{{breaking_changes_body}}` — `Breaking-Change:` trailers; "None." when
     absent.
   - `{{related_issues_body}}` — `Refs:` / `Closes:` / `Fixes:` trailers;
     "None." when absent.
   - `{{manual_testing_body}}` — `Testing:` / `Manual-Test:` trailers;
     "Covered by automated tests." when absent.
   - `{{additional_notes_body}}` — remaining unmapped body content; "None."
     when absent.

   Drop any optional section that resolves to "None." rather than leaving a
   stub — keep Summary and the Checklist only.
6. Emit the title line, a single blank line, then the Markdown body to stdout.
   Exit codes: `0` success, `2` unknown ref or non-conventional subject, `3` no
   commit source available, `4` bundled default template missing.

## Verification and Completion

- The composed title matches the Conventional Commits regex; a repo template
  was emitted byte-for-byte verbatim, or a bundled default has no
  `{{placeholder}}` left unfilled and no dropped-section stubs. Authoring is
  idempotent: the same commit ref plus the same resolved template produces
  byte-identical `title\n\nbody` — no timestamps, random IDs, or diff stats.
- Local checks passed with every command/result recorded, or command execution
  was explicitly skipped; hosted-only gaps and expected checks are named.
- Every bookmark was pushed with `jj git push`; every PR is draft, uses the
  authored title/body, and has the intended stack base.
- Report success only after the final poll observes every PR green. Include the
  stack map, resolved commit refs, the template used per change (repo path or
  bundled default), local results, repair commits, push/restack actions,
  per-PR check states, CI wall times, and any blocker (with its authoring exit
  code where relevant). Return every local project path created or materially
  rewritten during repair as `generated_files`. The PM applies the shared size
  pass only to eligible `.engineering` work Markdown.
