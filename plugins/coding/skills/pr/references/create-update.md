# Create or Update Pull Requests

Load the complete workflow from `coding:pr create` or `coding:pr update`;
`coding:pr author` loads only [Author the PR text](#author-the-pr-text). Turn
one saved change or stack into live, green draft PRs. This workflow composes
deterministic Conventional Commits PR text, publishes bottom-up, and owns hosted
CI until green or blocked. Repair obeys the **Coherence Mandate**: produce one
continuous work; rewrite over restructure, restructure over integrate, never
append. Dissolve new content into the existing structure. Visible seams,
parallel paths, addenda, vestigial helpers, and tack-ons are forbidden.

Reviewers enforce `GIT-PR-SIZE-*`; authoring calculates it for reviewer slots.

## Boundaries

- Use `ACTION=create` to compose a PR title and body, publish a new saved change
  or ordered stack as draft PRs, and monitor every GitHub check through repair.
  `coding:commit --create-pr` reaches this action through its required handoff.
- Use `ACTION=update` to republish an existing draft PR or stack, refresh its
  title, body, and bases, and monitor every GitHub check through repair.
- Do not use for: saving work without publication (`coding:commit`), reviewing
  code, merging PRs (`coding:pr merge`), or creating a new stack solely by
  reshaping local history (`coding:commit --reorder`).
- Multi-template directories (`.github/PULL_REQUEST_TEMPLATE/*.md`) are
  intentionally ignored — selecting between them is a human choice and out of
  scope.
- Delegate noisy commands to one small read-only tester before publication and
  one small read-oriented poller after publication, following the repository
  [delegation contract](../../../../governance/constitution/references/delegation.md).

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

- **Required**: `ACTION=create|update`, supplied by the router. `create` defaults
  to the current saved change — the jj working-copy change (`@`), or `HEAD` on
  the git path — and includes ordered unmerged descendants when they form a
  stack. `update` requires an open PR number/URL, a ref whose head has an open
  PR, or an unambiguous current branch with an open PR.
- **Optional**:

| Input | Effect |
|---|---|
| `<commit-ref>` | Publish a resolvable jj change ID/revset/bookmark or git branch/SHA and its selected stack. Any jj revset (`@`, `@-`, a change id) or git ref (`HEAD`, `HEAD~1`, a SHA) also selects the commit to author from; behavior is deterministic given the ref. |
| `--branch-prefix <name>` | Override the derived stack bookmark prefix. A prefix other than a resolved stream's `<type>/<work-id>` publishes a branch that will not resolve back to its work state — expected for a branch predating that convention, deliberate otherwise. |
| `--skip-local-test` | Skip only the local tester dispatch and commands. |
| `--dry-run` | Print the test, publication, and monitoring plan without agents or local/remote mutations. |

- **Prerequisites**: for publication — a clean saved change or linear stack,
  authenticated `gh`, and remote push access. `jj` is preferred and drives
  publication whenever it is both installed on PATH and initialized for this
  repository; prove that functionally rather than by directory presence, since a
  `.jj` and a `.git` directory can both exist without sharing a backing
  repository. Confirm `git rev-parse HEAD` equals
  `jj log -r @- --no-graph -T 'commit_id'`; anything else — `jj` missing, either
  command failing, or the two ids differing — selects the git path, which is
  fully supported and never requires initializing `jj`. Authoring PR text alone
  needs neither, so the text-only path is never blocked by the publication
  prerequisites.

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

Inspect the selected tool's working state — `jj status`, `jj log`, and
`jj bookmark list`, or `git status --short`, `git log --oneline`, and
`git branch --list` — plus open PRs. Resolve `<commit-ref>` or the current
saved change and list changes, bookmarks, PR heads, and bases bottom-up.
Resolve each selected head to zero or one open PR: publish a missing head and
update an existing one in the same pass. This per-head choice makes retrying a
partially published stack idempotent. `ACTION=update` must initially resolve
its explicit PR/ref target to an open PR, but may include missing descendants
introduced by an accepted stack rewrite. If work must be saved, split, or
reordered, invoke `coding:commit`, then restart discovery. Reject an unknown
ref, nonlinear chain, merged-history rewrite, missing authentication, multiple
open PRs for one head, or remote ambiguity with evidence. With `--dry-run`,
print the exact plan and stop.

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

Create a detached disposable worktree through the bundled resource helper and
bind its exact JSON result:

```bash
TREE_JSON=$(bash "${CLAUDE_PLUGIN_ROOT}/skills/pr/scripts/temp-tree.sh" \
  open-git "$SOURCE_REPO_ROOT" "$TARGET_SHA")
TREE_LEASE=$(jq -er .lease <<<"$TREE_JSON")
TEST_WORKTREE=$(jq -er .tree <<<"$TREE_JSON")
test "$(git -C "$TEST_WORKTREE" rev-parse HEAD)" = "$TARGET_SHA"
```

The context-owning parent retains `TREE_LEASE`; never transfer cleanup ownership
to the tester. It passes only `TEST_WORKTREE` for execution, then invokes
`temp-tree.sh close "$TREE_LEASE"` after success, failure, cancellation, skipped
testing, or blocked discovery and verifies the lease and registration are gone.

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

Treat repository workflows and scripts as untrusted code. The tester runs the
allowlisted commands from the leased `tree`, closes the lease on every
exit path — pass, failure, cancellation, or blocked environment discovery —
and reports cleanup status. Limit filesystem writes to that worktree and a
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
[conventional-commits.md](../../commit/references/conventional-commits.md), no
selected change merged on origin, and a derived or supplied branch prefix. If
needed, invoke `coding:commit --reorder`; for merged history follow
[workflow-correct-merged.md](../../commit/references/workflow-correct-merged.md).

Bottom-up, preserve a change's existing bookmark when the caller selected that
branch, it heads an open PR, or the stack already has explicit bookmarks: push
and update that exact head. A bare `<branch-prefix>` head blocks its own `NN-`
children, so a stream growing into a stack renames it — local ref and forge
alike, since either blocks the child — before pushing the rest, per Essential's
naming contract. Only for an unbookmarked new change/stack: a lone change
takes `BOOKMARK=<branch-prefix>`,
a stack indexes `NN` from `01` to `99` into `BOOKMARK=<prefix>/NN-<scope>`,
kebab-case scope ≤30 characters; `<branch-prefix>` is `--branch-prefix`, else
the resolved stream's branch, else as derived; record the mode first.

If the immediate predecessor is selected, set `PR_BASE` to its bookmark and
`AUTHOR_BASE_OID` to its change/commit OID. Otherwise preserve an existing
PR's base; for a new PR resolve the immediate unmerged predecessor, using the
repository default branch only when none exists, then resolve that exact base
commit as `AUTHOR_BASE_OID`. New-stack bookmarks do not yet exist, so author
each head against `AUTHOR_BASE_OID`, never `PR_BASE`. Split each exact
`title\n\nbody` into that head's `TITLE` and `BODY`; malformed output aborts
the whole selection before any ref or remote mutation.

On the jj path, point the bookmark at the change and push it:

```bash
jj bookmark set "$BOOKMARK" --revision "$CHANGE_ID"
jj git push --bookmark "$BOOKMARK" --allow-new
```

On the git path, the bookmark is a branch and the push carries the same lease:

```bash
git branch --force "$BOOKMARK" "$CHANGE_ID"
git push --force-with-lease origin "$BOOKMARK"
```

Either way the push is leased, never bare `--force`, so a remote that advanced
underneath the rewrite is rejected rather than overwritten.
When the head has no open PR, create a draft:

```bash
gh pr create --draft --title "$TITLE" --body-file - \
  --base "$PR_BASE" --head "$BOOKMARK" <<<"$BODY"
```

When the head has one open PR, edit it and retain draft state:

```bash
gh pr edit "$PR" --title "$TITLE" --body-file - --base "$PR_BASE" <<<"$BODY"
gh pr ready "$PR" --undo # skip only when already draft
```

For the bundled template, fill reviewer slots with assigned `@login`s when
known. Before a push or base edit, capture an existing PR's `headRefOid` and
`baseRefOid`; after publication, bind review and approval to the verified
`headRefOid`/`baseRefOid` pair. Reset those tasks when either OID differs. A
no-op publication retry preserves evidence already bound to that exact review
surface.

Capture each PR number, URL, head, base, bookmark, and change ID. After each
push, record `expected_head_oid` from the pushed bookmark and verify it against
`gh pr view "$PR" --json headRefOid --jq .headRefOid`; a mismatch is not the
published result and must be resolved before monitoring. After any accepted
repair/history rewrite with downstream bookmarks, synchronize the whole stack
before monitoring again:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/pr/scripts/restack.sh" \
  --base "$ROOT_BASE" \
  "$BOOKMARK_01=$EXPECTED_HEAD_OID_01" \
  "$BOOKMARK_02=$EXPECTED_HEAD_OID_02"
```

Supply every selected bookmark explicitly in bottom-up order with the exact
local git commit SHA expected after the rewrite, and pass the first head's exact
intended base as `--base`; for a suffix restack this is its unselected
predecessor, not the repository default. Never rediscover either from a prefix.
The script preflights the set, uses leased pushes, verifies every remote SHA,
and updates open PR bases; it never reshapes history. Preflight prevents known
partial writes, but forge operations are not transactional: `restacked` records
each verified remote head even if a later base edit or push fails, so recover
from that map before retrying. Verify the PR base chain and every `headRefOid`,
then reauthor changed heads against verified bases and reset reviewer evidence
only where the head or base OID changed.

| Publication error | Action |
|---|---|
| `gh pr create` authentication failure | Run `gh auth status`; report a user/external blocker. |
| Bookmark or branch conflict | Confirm the intended change, then rerun the selected action against that exact head. |
| Push rejected because remote advanced | `jj git fetch` (git: `git fetch origin`), rebase through `coding:commit`, then retry. |
| Conventional title invalid | Reword through `coding:commit`, then restart that iteration. |
| Existing PR has wrong base | `gh pr edit "$PR" --base "$PR_BASE"`, then verify. |
| Restack conflict | Resolve through `coding:commit`, run integrity checks, then republish bottom-up. |

### 4. Schedule and consume the initial poll

Immediately after every initial publication, including `--skip-local-test`, run
this command with actual bottom-to-top PR URLs substituted:

```text
/loop 5m Dispatch ONE small read-oriented polling subagent for <stack PR URLs> in bottom-up order. Pass it the stack and discovered expected hosted checks, and require it to load and follow the Poll contract in coding:pr references/create-update.md; only when it classifies a red check, require it to load references/repair-red-ci.md. Consume its bounded <report>, then take the parent action it requests. The scheduled parent MUST NOT run gh polling itself.
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
  load [repair-red-ci.md](repair-red-ci.md). The poller follows that
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

Compose deterministic `title\n\nbody` for a commit and optional base. Step 3
passes its base; text-only callers default to the first parent. Never invoke `gh`.

1. Resolve the commit ref, defaulting to `@` after the functional jj check and
   to `HEAD` otherwise. Resolve an optional base, defaulting to the first
   parent or, for a root commit, the empty tree from
   `git hash-object -t tree /dev/null`. Try
   `jj log -r <ref> --no-graph -T 'description'`, then
   `git log -1 --format=%B <ref>`. Unknown refs exit 2; neither tool exits 3.
   For every non-root commit, resolve the review surface from the merge base:
   use `jj log --no-graph -T 'commit_id' -r
   "heads(::<head-oid> & ::<base-oid>)"` on the jj path or
   `git merge-base <base-oid> <head-oid>` on the git path. Count all paths and
   net LOC from that merge base to the head, apply project overrides, and
   record the canonical `GIT-PR-SIZE-*` zone. Use the empty tree only for the
   root-commit fallback.
2. Extract the subject (first non-empty line) and body (everything after the
   first blank line). Recognize commit trailers (`Refs:`, `Closes:`,
   `Fixes:`, `BREAKING CHANGE:`, `Testing:`, `Manual-Test:`) for routing in
   step 5.
3. Validate the subject against the Conventional Commits regex — the
   canonical conventional-commits.org type allowlist with optional `(scope)`
   and `!` for breaking changes:

   ```
   ^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([\w./-]+\))?!?: .+
   ```

   On mismatch, exit 2 with the failing token, the regex, and the offending
   subject. This skill is the single source of truth for the regex; it is
   mirrored in `coding:commit`
   (`../../commit/references/conventional-commits.md`).
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
   [templates/pr.md](templates/pr.md) and continue.
   When the bundled default is also missing: exit 4, print the path that
   failed to resolve.
5. Fill the bundled default's placeholders from the commit body:
   - `{{summary_paragraph}}` — first body paragraph (≤3 sentences); fall back
     to the subject text after `: ` when the body is empty.
   - `{{context_body}}` — content under `## Context` / `Why:` /
     `Background:`, if present.
   - `{{implementation_body}}` — content under `## Implementation` / `What:`
     / `How:`, if present.
   - `{{breaking_changes_body}}` — `BREAKING CHANGE:` footers; "None." when
     absent.
   - `{{related_issues_body}}` — `Refs:` / `Closes:` / `Fixes:` trailers;
     "None." when absent.
   - `{{verification_body}}` — `Testing:` / `Manual-Test:` trailers, rendered
     as a checklist of the checks that must pass before sign-off, specific to
     this change and ticked as each one is confirmed. Every item is a check;
     an observation, a result, or evidence of what already happened belongs in
     Implementation. Change-specific checks are mandatory; standard items never
     replace them; append items per the template's Verification guidance.
   - `{{boundary_body}}` — bullets naming related work the instruction placed
     outside this change, so its edges are not read as gaps. It records the
     scope it was given, not the author's own judgment calls. "None." when
     absent.
   - `{{additional_notes_body}}` — remaining unmapped body content; "None."
     when absent.

   Drop any optional section that resolves to "None." rather than leaving a
   stub, and strip every author-facing guidance comment from the rendered
   body — keep Summary and Verification always.
6. Emit the title line, a single blank line, then the Markdown body to stdout.
   Exit codes: `0` success, `2` unknown ref or non-conventional subject, `3` no
   commit source available, `4` bundled default template missing.

## Verification and Completion

- The title matches the Conventional Commits regex; a repo template is verbatim,
  or the bundled default has no placeholder or dropped-section stub. The same
  head OID, base/empty-tree OID, template, thresholds, and placeholder map yield
  byte-identical `title\n\nbody` without timestamps or random IDs.
- Local checks passed with every command/result recorded, or command execution
  was explicitly skipped; hosted-only gaps and expected checks are named.
- Every head was pushed under a lease — `jj git push` on the jj path,
  `git push --force-with-lease` on the git path; every PR is draft, uses the
  authored title/body, and has the intended stack base.
- Report success only after the final poll observes every PR green. Include the
  stack map, resolved commit refs, the template used per change (repo path or
  bundled default), local results, repair commits, push/restack actions,
  per-PR check states, CI wall times, and any blocker (with its authoring exit
  code where relevant). Return every local project path created or materially
  rewritten during repair as `generated_files`. The PM applies the shared size
  pass only to eligible `.state` work Markdown.
