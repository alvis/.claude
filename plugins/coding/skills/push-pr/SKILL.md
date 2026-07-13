---
name: push-pr
description: 'Publish a saved change or ordered stack as draft pull requests and drive GitHub CI to green. Use when asked to push, open or update PRs, babysit checks, repair CI failures, or republish an existing stack; use coding:commit for local history work without publication.'
model: opus
argument-hint: "[<commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--dry-run]"
---

# Push Pull Request

Publish one saved change or an ordered stack as draft pull requests, then own
the hosted-CI lifecycle until every PR is green or a concrete blocker requires
user action or external state. `coding:write-pr` remains the PR-text owner.

**Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike.

## Boundaries

- Use for: publishing or republishing a saved jj change, branch, current draft
  PR, or ordered stack and monitoring every GitHub check through repair.
- Do not use for: saving an unsaved working copy or rewriting local history
  without publication (`coding:commit`), authoring PR text only
  (`coding:write-pr`), reviewing code, or merging PRs.
- Delegate noisy command execution to one small read-only tester before
  publication and one small read-oriented poller after publication, following
  the repository
  [delegation contract](../../../governance/constitution/references/delegation.md).

<IMPORTANT>
- Ownership is singular: `coding:commit` owns direct history mutations;
  `coding:stack-code` is invoked to orchestrate reshaping/reparenting when a
  root cause belongs in a lower PR outside the current PR;
  [publish-stack.md](references/publish-stack.md) owns push, restack, and PR
  base mechanics; [ci-convergence.md](references/ci-convergence.md) only
  decides status, gathers evidence, and directs the parent to
  `publish-stack.md`.
  The parent alone accepts fixer edits and performs commit, push, and restack
  mutations; the poller may dispatch exactly one scoped fixer per red cycle.
- `--skip-local-test` skips only the local pre-push test phase. It never skips
  publication, GitHub monitoring, evidence collection, repair, or convergence.
- Fix root causes. MUST NOT weaken a correct test, alter a valid expectation,
  add ignores or suppressions, or delete checks merely to pass. Edit a test
  only when captured failure evidence proves that the test itself is the root
  cause.
- Never report success while any PR in the resulting stack is pending or red.
</IMPORTANT>

## Inputs

- **Required**: none; default to the saved change at the current jj revision
  and include its ordered unmerged descendants when they form a stack.
- **Optional**:

| Input | Effect |
|---|---|
| `<commit-ref>` | Publish the resolvable jj change ID, revset, bookmark, git branch, or SHA and its selected stack. |
| `--branch-prefix <name>` | Override the derived `<branch-prefix>` used for stack bookmarks. |
| `--skip-local-test` | Skip only step 2's local pre-push checks. |
| `--dry-run` | Inspect and print the complete test, publication, and monitoring plan without dispatching agents or mutating local/remote state. |

- **Prerequisites**: a clean saved change or linear stack, a jj-colocated
  repository, authenticated `gh`, and push access to the remote.

## Workflow

1. **Resolve and plan.** Inspect `jj status`, `jj log`, `jj bookmark list`,
   `git status --short`, and open PRs. Resolve `<commit-ref>` or the current
   saved change; list the bottom-to-top changes, bookmarks, PR heads, and
   bases. If unsaved or mixed work must be committed/split/reordered, invoke
   `coding:commit`, then restart discovery. Reject an unknown ref, nonlinear
   chain, merged-history rewrite, missing authentication, or remote ambiguity
   with concrete evidence. With `--dry-run`, print this plan and stop.

2. **Run local CI parity unless skipped.** Read `.github/workflows/*` and the
   repository's script definitions (`package.json`, workspace manifests,
   Makefiles, task files, or equivalent). Derive the exact compile, type,
   lint, test, and build commands that reproduce CI without hosted services;
   record each hosted-only check and the unavailable service or credential.
   Dispatch one small-model test subagent for the whole command set. The
   tester is read-only: it MUST NOT edit, format, commit, or push anything.
   It runs every discovered runnable command in CI order, continuing through
   independent commands after a failure, and returns under 1000 tokens:

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
   overall: pass | fail | blocked
   ```

   </report>

   On failure, diagnose from the captured output before editing. Dispatch one
   relevant fix agent, scoped to the named root cause and affected files. The
   fixer may edit and returns under 1000 tokens:

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
   `coding:commit --retrospective`, and sends the tester back to rerun the
   affected commands and then the full runnable set. Publish only when every
   runnable command exits zero. Any separate review is read-only.
   With `--skip-local-test`, do not dispatch the tester; continue directly to
   publication and hosted convergence.

3. **Publish bottom-up.** Load and follow
   [references/publish-stack.md](references/publish-stack.md) for bookmark
   naming, `jj git push`, `coding:write-pr`, draft `gh pr create`/update, stack
   bases, restacking, and publication errors. Capture every PR number, URL,
   head bookmark, base, and change ID.

4. **Start hosted convergence immediately.** Immediately after publication,
   load and follow
   [references/ci-convergence.md](references/ci-convergence.md). Schedule its
   executable `/loop 5m <explicit prompt>` with one small read-oriented poller
   for the entire stack, capture the returned task/job ID, and retain it for
   exact cancellation. Do this even when `--skip-local-test` was supplied.

## Verification and Completion

- Local phase passed with every runnable command and result recorded, or was
  explicitly skipped by `--skip-local-test`; hosted-only gaps are named.
- Every selected bookmark was pushed with `jj git push`; every PR uses the
  intended stack base, title/body from `coding:write-pr`, and draft state.
- The poller observed every PR green after the final push. Report the final
  stack map, local results, repair commits, push/restack actions, per-PR check
  state, CI wall times, and any blocker.
- State the operational limit: scheduled tasks fire only while the session is
  open and idle. Unexpired tasks are restored by `--resume` or `--continue`;
  expired tasks are not replayed.
