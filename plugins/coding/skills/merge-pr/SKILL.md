---
name: merge-pr
description: 'Merge a linear stack of GitHub pull requests while restacking descendants between merges. Use when a user invokes /merge-pr with PR numbers, asks to merge stacked PRs, or needs gh-driven bottom-up PR merging with automatic downstream rebase.'
model: opus
allowed-tools: Bash(git:*), Bash(jj:*), Bash(gh:*), Bash(sleep:*), Bash(jq:*), Read
argument-hint: "<pr numbers...> [--method=rebase|squash|merge] [--force]"
---

# Merge Stacked Pull Requests

Merge a supplied stack of GitHub PRs bottom-up with `gh`, restacking every remaining downstream branch after each merge so GitHub-generated merge commits or rebased commits do not cause the next PR to replay already-merged work. This skill owns remote PR merges plus descendant branch/bookmark rebases in either git or jj repositories; local commit creation remains `coding:commit`, and code/CI repair remains `coding:fix`.

## Boundaries

- Use for: `/merge-pr 12 13 14`, "merge this stack of PRs", "merge PRs 8, 9, and 10 with squash", or any request to merge multiple dependent GitHub PRs while automatically rebasing downstream PR branches.
- Do not use for: creating PRs (`coding:commit --create-pr` + `coding:write-pr`), saving local changes (`coding:commit`), writing code fixes (`coding:fix`), or validating unpushed commits before opening PRs (`coding:finalize-commits`).

## Inputs

- **Required**: PR numbers in bottom-to-top order unless the user explicitly states the order is unknown; verify and stop if the real stack is not exactly linear.
- **Optional**:
  - `--method=rebase|squash|merge`; default is `rebase`.
  - `--force`; bypasses the green-CI gate but never bypasses stack-shape validation or conflict safety.
- **Prerequisites**: authenticated `gh`, a clean git or jj working copy, all target PR head branches/bookmarks pushable by the current actor, and local `origin` remotes for the PR heads.

<IMPORTANT>
- Do not merge any PR until all supplied PRs are proven to form one linear base chain.
- Without `--force`, do not merge any PR unless every PR currently in the stack has green CI.
- If you make or request fixes for failing CI, summarize the changes to the user and post the same summary as a PR comment, then wait for explicit user approval before merging.
- Never use plain `git rebase origin/main` for descendants. Before each merge, snapshot the current tip of every PR still in the stack, then restack with `git rebase --onto <new-parent> <round-parent-tip> <child>` in git repos or the equivalent jj rebase. Keep that round's snapshot unchanged until every descendant has been restacked, then refresh the saved tips before the next merge.
- On conflicts, stop with the current branch, conflicted files, and exact recovery commands; do not resolve unless the user asks.
</IMPORTANT>

## Workflow

1. **Parse arguments and preflight.** Extract PR numbers, merge method, and `--force`. Reject unknown methods. Detect whether the repository is jj-colocated or plain git, then discover any existing local branches, git worktrees, jj bookmarks, and jj workspaces before creating or checking out anything locally:

   ```bash
   jj root >/dev/null 2>&1 && jj status || git status --short
   gh auth status
   git branch --list
   git worktree list
   git fetch origin --prune
   jj git fetch --remote origin  # jj repos only
   jj bookmark list --all        # jj repos only
   jj workspace list             # jj repos only
   ```

   Reuse an existing clean worktree/workspace or branch/bookmark whose tip matches the PR head. If a local checkout exists but has uncommitted work or a different tip, stop and ask before reusing, moving, or overwriting it.

2. **Read PR metadata.** For every PR, collect number, state, base ref, head ref, head repository owner, head SHA, mergeability, and status rollup:

   ```bash
   gh pr view <n> --json number,state,baseRefName,headRefName,headRepositoryOwner,headRepository,headRefOid,mergeStateStatus,statusCheckRollup,url,title
   ```

   Stop if any PR is closed, merged, from an unavailable fork, or has a head branch/bookmark that cannot be checked out, rewritten, and pushed.

3. **Verify one linear chain.** The stack is valid only when each downstream PR's `baseRefName` equals the previous PR's `headRefName`, and the first PR's base is the destination branch that will receive the stack. Also verify ancestry locally after fetching all heads. In plain git, use:

   ```bash
   git fetch origin <base>:refs/remotes/origin/<base>
   git fetch origin <head>:refs/remotes/origin/<head>
   git merge-base --is-ancestor origin/<previous-head> origin/<child-head>
   ```

   For PR 1, verify `merge-base --is-ancestor origin/<base> origin/<head>`. In jj repos, verify explicit ancestor containment instead of using `x..y`, which does not require `x` to be an ancestor of `y`:

   ```bash
   jj log -r '<previous-head>@origin & ::<child-head>@origin' --no-graph -T 'commit_id'
   jj log -r '<base>@origin & ::<head>@origin' --no-graph -T 'commit_id'
   ```

   Require each jj command to produce a non-empty commit ID. If any git link fails or any jj containment query is empty, stop and show the expected chain as `base <- PR1 head <- PR2 head ...` plus the detected mismatch.

4. **Check CI unless forced.** Without `--force`, require every status check on every PR to be successful, skipped, or neutral. Treat pending, queued, expected, action-required, cancelled, timed-out, failure, error, or missing required checks as not green. Use both `mergeStateStatus` and `statusCheckRollup` from `gh pr view`.

   If CI is not green, print a concise summary of failing checks and likely issue areas by PR, then ask whether the user wants to fix the issues locally and update the affected PRs. Suggest running `coding:fix` on the detected CI issues, updating the stacked PRs, then `/loop` for 1 minute to wait for checks to turn green or rerun the fix when they fail again. Stop before merging until the user chooses a fix or force path.

5. **Record branch identities and initial tips.** Save every PR head SHA/change ID and branch or bookmark name in order. The tips establish the first round's cut points and must be refreshed between later rounds:

   ```bash
   saved_tip_<n>=$(git rev-parse origin/<head-branch>)        # plain git
   saved_tip_<n>=$(jj log -r '<head-branch>@origin' --no-graph -T 'change_id')  # jj
   ```

6. **Merge and restack bottom-up.** For each PR from bottom to top:

   a. Recheck that the current PR is green unless `--force`, because prior restacks rerun CI. Immediately before merging, snapshot the current tip of the PR being merged and every remaining descendant. These immutable round tips are the cut points for every descendant rebase in this round:

   ```bash
   round_tip_<n>=$(git rev-parse origin/<head-branch>)        # plain git
   round_tip_<n>=$(jj log -r '<head-branch>@origin' --no-graph -T 'change_id')  # jj
   ```

   b. Merge it with the selected method:

   ```bash
   gh pr merge <number> --rebase --delete-branch=false
   gh pr merge <number> --squash --delete-branch=false
   gh pr merge <number> --merge --delete-branch=false
   ```

   Use exactly one command matching `--method`. Keep `--delete-branch=false` until all descendants have been restacked.

   c. Fetch the new parent target:

   ```bash
   git fetch origin --prune
   ```

   d. Restack every remaining downstream PR, one link at a time. For the immediate child of a PR merged into the destination branch, replay only child-exclusive commits onto `origin/<destination>` using the merged parent's `round_tip`. For deeper descendants, replay onto the freshly restacked parent branch/bookmark using that parent branch's pre-restack `round_tip`. Use the repository's native VCS path:

   ```bash
   git switch <child-head-branch>
   git rebase --onto <new-parent-ref> <round-parent-tip-sha>
   git push --force-with-lease origin HEAD:<child-head-branch>
   ```

   ```bash
   child_root=$(jj log -r 'roots(<round-parent-tip>..<round-child-tip>)' --no-graph -T 'change_id')
   jj rebase -s "$child_root" -d <new-parent-ref>
   jj bookmark set <child-head-branch> --revision <new-child-tip>
   jj bookmark set <grandchild-head-branch> --revision <new-grandchild-tip>
   jj git push --remote origin --all
   ```

   Use `jj rebase -s` for jj stacks because it moves the selected child-exclusive root and its descendants together. `jj git push --all` pushes all bookmarks in one command; if unrelated local bookmarks must not move, replace `--all` with repeated `--bookmark <stack-bookmark>` arguments in one `jj git push` command. Jujutsu's push safety checks are lease-like: rerun `jj git fetch --remote origin` and resolve bookmark conflicts if a remote bookmark changed unexpectedly.

   e. After each push, use that child's new local tip as `<new-parent-ref>` for its child, but do not change any `round_tip` while the round is in progress. After every remaining descendant has been restacked and pushed successfully, replace the saved tips with the new branch/bookmark tips. The next merge round must snapshot these refreshed tips so it cannot replay commits already moved by an earlier round.

   f. Wait for GitHub to observe the push, then re-check CI before merging the next PR. If checks are pending, report that the stack was restacked and stop unless the user asked to wait; if asked to wait, poll at a reasonable interval for up to the user's requested duration.

7. **Fix handling gate.** If any CI fix was made during this workflow by invoking or following `coding:fix`, update the affected PR branches/bookmarks using the same restack and push instructions above, but do not perform any `gh pr merge` action for the fixed PR or any downstream PR until the user gives explicit approval. Post a comment on the relevant PRs with the fix summary:

   ```bash
   gh pr comment <number> --body-file <summary-file>
   ```

   Then present the same summary to the user and wait for explicit approval before returning to step 4. Until approval arrives, treat all downstream PRs as blocked even if their checks are green.

8. **Conflict or failure recovery.** On rebase conflict, stop immediately and show the recovery commands for the active VCS:

   ```bash
   git status --short
   git rebase --abort
   git rebase --continue
   ```

   ```bash
   jj status
   jj op log -n 5
   jj op restore <operation-id-before-rebase>
   ```

   Include the conflicted branch/bookmark, round parent tip, intended new parent, and PR number. On push rejection, fetch and rerun the same native restack only after confirming the remote branch/bookmark was not updated by someone else.

## Verification

- Dry-run mentally from the recorded metadata before mutating: the detected chain must be exactly linear.
- Before every merge without `--force`, `gh pr view <n> --json mergeStateStatus,statusCheckRollup` must show green checks for the PR being merged.
- After every restack, verify ancestry with the active VCS:

  ```bash
  git merge-base --is-ancestor <new-parent-ref> origin/<child-head-branch>
  jj log -r '<new-parent-ref> & ::<child-head-branch>@origin' --no-graph -T 'commit_id'
  ```

  Require the jj containment query to produce a non-empty commit ID.

- Validate this skill when edited:

  ```bash
  claude plugin validate --strict plugins/coding
  python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py plugins/coding/skills/merge-pr
  ```

## Completion

Report the PRs merged, merge method, branches/bookmarks restacked, per-round parent tips used as cut points, CI status after each restack, comments posted for any fixes, and any blocked PRs. Once the stack has merged, inspect `git worktree list` and `jj workspace list` for worktrees/workspaces whose current tips exactly match the merged PR head tips, then ask the user whether they also want those corresponding git worktrees or jj workspaces removed; do not remove them without confirmation. If stopped for approval after fixes, clearly say that no merge occurred after those fixes and identify the approval needed.
