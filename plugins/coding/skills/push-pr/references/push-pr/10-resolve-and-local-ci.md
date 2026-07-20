# Resolve and reproduce local CI

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
