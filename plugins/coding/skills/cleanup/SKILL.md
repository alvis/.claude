---
name: cleanup
description: Audit stale development state across git branches, remote branches, git worktrees, and jj workspaces. Use when a user asks to run /cleanup, find abandoned branches/workspaces, or safely remove already-merged or duplicate local work with backups and confirmation.
allowed-tools: Bash, Read, Glob, Grep, Task
argument-hint: "[path] [--exclude-remote]"
---

# Cleanup

Own safe cleanup of no-longer-needed development state: local branches,
remote-tracking branches, git worktrees, and jj workspaces or changes. The
skill discovers candidates, explains evidence and blind spots, asks for user
confirmation, backs up confirmed content to an OS temporary location, then
performs only the approved removals.

## Boundaries

- Use for: `/cleanup`; auditing stale or divergent git/jj state; finding
  branches already merged into the default branch; finding worktrees or jj
  workspaces whose content is duplicated elsewhere; backing up and removing
  user-approved cleanup targets.
- Do not use for: source-code dead-code removal (`coding:find-unused`),
  ordinary lint or formatting (`coding:lint`), PR creation (`coding:write-pr`),
  or force-rewriting active work without an explicit user request and approval.

## Inputs

- **Required**: none — default to the current repository or workspace.
- **Optional**: a path to inspect; `--exclude-remote` to skip remote branch
  deletion candidates and avoid fetching or PR metadata checks for remotes.
- **Prerequisites**: use available tools only. If `jj`, `gh`, network access, or
  credentials are unavailable, continue with git-local evidence and mark the
  affected findings as partial.

## Workflow

1. Establish scope and baseline state.
   - Resolve the target path and identify the repository root with
     `git -C <path> rev-parse --show-toplevel` when possible.
   - Detect jj with `jj root` from the target path. If both git and jj are
     present, record both roots and note mismatches.
   - Identify the default branch from `origin/HEAD`, then from `main`, then
     from `master`; if none exists, ask the user to choose before judging merge
     status.
   - Unless `--exclude-remote` is present, fetch remote metadata only when
     network and credentials are already available. Do not fail the cleanup
     when fetching is impossible; mark remote evidence stale.
2. Build an inventory without deleting anything.
   - Git branches: run `git for-each-ref --format='%(refname:short) %(objectname) %(committerdate:iso8601)' refs/heads refs/remotes`,
     `git branch --merged <default>`, and `git branch --no-merged <default>`.
     When `--exclude-remote` is present, limit remote checks to already-known
     local refs and do not recommend remote branch deletion.
   - Git worktrees: run `git worktree list --porcelain` and map each worktree
     to its path, branch, HEAD, lock/prunable state, and dirty status via
     `git -C <worktree-path> status --short --branch`.
   - jj state when available: run `jj status`, `jj log --no-graph -T 'change_id ++ " " ++ commit_id ++ " " ++ description.first_line() ++ "\n"' -r 'mutable()'`,
     `jj log --no-graph -T 'change_id ++ " " ++ commit_id ++ " " ++ description.first_line() ++ "\n"' -r 'divergent()'`
     to explicitly surface divergent jj changes, and `jj workspace list` if
     supported by the installed jj version.
   - PR metadata when `gh` is authenticated and `--exclude-remote` is absent:
     map branches to PR state with `gh pr list --state all --head <branch> --json number,state,mergedAt,closedAt,headRefName,baseRefName,statusCheckRollup`.
3. Classify candidates with explicit evidence.
   - **Recommend cleanup** when a branch is merged into the default branch, its
     PR is merged or closed and the commits are present in the default branch,
     a worktree is prunable or points at a branch recommended for cleanup, or a
     jj change/workspace is abandoned and its patch-id/content is already
     present on the default branch or another retained branch.
   - **Needs review** when a branch is unmerged but appears duplicated by patch
     equivalence, the PR is closed without merge, the worktree is dirty, the jj
     workspace has mutable divergent changes, or remote information is stale.
   - **Do not cleanup** when commits are unpushed, the worktree has uncommitted
     changes that are not safely backed up, the branch belongs to the default or
     release branch family, the PR is open, or the owner is unclear.
4. Run a blind spot test before asking for deletion approval.
   - Check for untracked files, dirty indexes, stashes, unpushed commits,
     submodules, nested repositories, linked worktrees outside the target root,
     branch names reused across remotes, shallow clones, protected branch name
     patterns, closed-but-unmerged PRs, and disagreement between git and jj
     history.
   - Downgrade any affected candidate to **Needs review** and show the blind
     spot and residual risk before the user decides whether to clean it up.
5. Ask the user to confirm cleanup targets.
   - Present a table grouped by target type with: target name, path or remote,
     recommendation, evidence, blind spots, backup plan, and exact removal
     command.
   - Ask the user to select targets to remove. Never infer approval from the
     original `/cleanup` request.
6. Back up every approved target before removal.
   - Use an OS temporary root: `${TMPDIR:-/tmp}/backups/<project-name>/` on
     Unix-like systems, `$env:TEMP/backups/<project-name>/` on PowerShell, or
     the platform's documented temp directory when different.
   - For git worktrees and non-jj workspace directories, copy the full
     directory tree including dotfiles and untracked files to a unique
     timestamped backup directory. Do not create extra file backups for jj
     divergent changes because jj already preserves abandoned changes in its
     operation history; instead record the jj change IDs and restoration
     command in the metadata file.
   - For branches, create a git bundle or patch backup containing the branch
     tip and range from the default branch, plus a text metadata file with the
     original ref, commit, upstream, PR metadata, and cleanup reason.
   - Verify each backup exists and is non-empty before running any removal
     command.
7. Remove only approved and backed-up targets.
   - Git worktrees: prefer `git worktree remove <path>`. If git refuses
     because the worktree is dirty or locked, stop and ask for a separate
     explicit approval before using any forced removal option.
   - Local branches: use `git branch -d <branch>` for merged branches and
     `git branch -D <branch>` only after explicit approval for an unmerged or
     needs-review candidate.
   - Remote branches: use `git push <remote> --delete <branch>` only when the
     user selected the remote target and credentials are available.
   - jj workspaces/changes: use the installed jj version's supported workspace
     or abandon commands, and avoid abandoning any change not listed in the
     confirmation table. When forgetting a jj workspace, remember that jj only
     removes the workspace record and does not delete the directory; after the
     workspace directory backup has been verified, manually remove the folder
     with the platform-appropriate file removal command.
8. Verify and report.
   - Re-run the relevant git/jj inventory commands to prove approved targets
     are gone and retained targets remain.
   - Report backup paths, removed targets, skipped targets, residual blind
     spots, and restoration hints.

<IMPORTANT>
Cleanup is never fully automatic. The agent must obtain explicit user approval
for each target after showing evidence and backup/removal commands, and must
create and verify a backup before any destructive operation.
</IMPORTANT>

## Verification

- The inventory includes git branches, remote-tracking branches when available,
  git worktrees, and jj workspaces/changes when available.
- Every recommendation has evidence and a blind spot classification.
- Every destructive git command is preceded by explicit user confirmation and a
  verified backup in the OS temporary backup tree; destructive jj commands are
  preceded by explicit user confirmation and recorded jj change IDs because jj
  preserves abandoned changes in operation history.
- Post-cleanup inventory confirms approved targets were removed and unapproved
  targets were not removed.
- Validate this skill with `claude plugin validate --strict <plugin-path>` and
  `python3 <governance-skill-dir>/../verify-skill/scripts/quick_validate.py <skill-or-plugin-path>`.

## Completion

Report the project, default branch, tools available, and fetch/PR metadata
freshness. Summarize counts for recommended, needs-review, protected, removed,
and skipped targets. List each backup path and removal command that ran. If a
blind spot blocked confidence, explain the risk and the command or credential
needed to resolve it.
