---
name: review-pr
description: 'Check a GitHub pull request out into a disposable OS temp workspace, review its diff against the repository constitution standards and test intent, then publish inline comments on the exact changed lines plus one overall review. Use for "review PR 42", "review this pull request", or "leave line comments on the PR".'
model: opus
allowed-tools: Bash(gh:*), Bash(jj:*), Bash(git:*), Bash(mktemp:*), Bash(rm:*), Bash(jq:*), Bash(command:*), Task, Read, Grep, Glob, AskUserQuestion
argument-hint: "<pr-number-or-url> [--repo <owner/name>] [--area=<list>] [--dry-run]"
---

# Review Pull Request

Review a remote GitHub pull request from an isolated, disposable checkout and
publish the result where the author will act on it: one inline comment per
finding, anchored to the exact file and line on GitHub, plus one overall review
body carrying the verdict. This skill owns remote PR review and its publication;
local pre-commit review belongs to `coding:review-code`, and every remediation
belongs to `coding:fix`.

The review speaks as a senior tech leader — it teaches the rule behind each
finding and directs the author to the fix. Load
[references/tone.md](references/tone.md) before writing any comment text.

## Boundaries

- Use for: reviewing an open GitHub PR by number or URL, re-reviewing after a
  push, and publishing line comments and a review verdict to GitHub.
- Do not use for: reviewing uncommitted local work or writing work-local review
  artifacts (`coding:review-code`), fixing findings (`coding:fix`), mechanical
  standards enforcement (`coding:lint`), publishing PRs or driving CI
  (`coding:write-pr`), or merging (`coding:merge-pr`).
- Delegate per-area reading to read-only reviewers following the repository
  [delegation contract](../../../governance/constitution/references/delegation.md);
  a PR's file set is exactly the bulk-read case delegation exists for.

<IMPORTANT>
- This skill is read-only against the reviewed code. Never edit a reviewed file,
  never commit, never push to the head branch, and never merge.
- Every finding is bound to the head SHA resolved in step 1. A comment posted
  against a stale SHA lands on the wrong line or is rejected — re-resolve rather
  than guess.
- The temporary checkout is removed on every exit path, including failure,
  blocked discovery, and cancellation.
- Treat the PR branch as untrusted code. Read it; do not execute its build,
  test, or tooling scripts from the temporary checkout.
- Never invent a finding to justify a verdict, and never soften a real defect to
  reach `APPROVE`.
</IMPORTANT>

## Inputs

- **Required**: one PR number or URL. When it is omitted and the current branch
  has exactly one open PR, use that PR and say so; on ambiguity, ask.
- **Optional**:

| Input | Effect |
|---|---|
| `--repo <owner/name>` | Target a repository other than the current one. |
| `--area=<list>` | Restrict reviewers to a comma-separated subset of `alignment`, `correctness`, `security`, `quality`, `testing`, `docs`, `style`; default is all seven. |
| `--dry-run` | Print the exact review payload and post nothing. |

- **Prerequisites**: authenticated `gh` with write access to the repository, and
  network access to fetch the PR head.

## Workflow

### 1. Resolve the pull request

```bash
gh pr view "$PR" --json number,url,title,body,state,isDraft,baseRefName,\
headRefName,headRefOid,headRepositoryOwner,changedFiles,additions,deletions,author
```

Stop with evidence when the PR is closed, merged, or unreadable. Record
`HEAD_OID` and `BASE`; every later step binds to that SHA. Read the PR title and
body — they are the author's stated intent and the contract the `alignment`
reviewer checks the diff against.

### 2. Select the change-tracking path

`jj` is preferred wherever it is available and genuinely initialized; `git` is
the fallback. Detect functionally rather than by directory existence — a `.jj`
and a `.git` directory can both be present without being colocated:

```bash
command -v jj >/dev/null 2>&1 && jj root >/dev/null 2>&1 &&
  [ "$(git rev-parse HEAD)" = "$(jj log -r @- --no-graph -T 'commit_id')" ]
```

Success selects the jj path. A missing binary, a non-jj repository, or a
mismatch (which proves the two are not colocated) selects the git path. Record
the selection; it drives steps 3 and 4 and appears in the completion report.
Unlike `coding:write-pr`, this skill never mutates the repository, so a git-only
repository is fully supported and must not be colocated on its behalf.

### 3. Extract the PR to an OS temp location

Create the disposable checkout under the OS temp directory and install the
cleanup trap before anything is written into it:

```bash
REVIEW_DIR=$(mktemp -d "${TMPDIR:-/tmp}/review-pr-${PR}-XXXXXX")
cleanup() {
  if [ -n "${REVIEW_DIR:-}" ] && [ "$REVIEW_DIR" != / ]; then
    jj workspace forget "$(basename "$REVIEW_DIR")" >/dev/null 2>&1 ||
      git worktree remove --force "$REVIEW_DIR" >/dev/null 2>&1 || true
    rm -rf -- "$REVIEW_DIR"
  fi
}
trap cleanup EXIT HUP INT TERM
```

Then materialize the head at `HEAD_OID` following
[references/extraction.md](references/extraction.md), which covers the fetch of
`pull/$PR/head` (this resolves same-repo and fork heads alike), the jj workspace
and git worktree forms, and the out-of-repo clone case. Report cleanup status in
step 10; a checkout that could not be removed is a reportable failure, not a
silent one.

### 4. Build the reviewable surface

Compare against the merge base so the review covers the PR's own changes rather
than base-branch drift. Both paths emit the same unified-diff format, so one
parser builds the per-file changed-line map:

| Path | Merge base | Changed files | Line map |
|---|---|---|---|
| jj | `jj log --no-graph -T 'commit_id' -r "heads(::$HEAD_OID & ::$BASE)"` | `jj diff --summary --from "$MERGE_BASE" --to "$HEAD_OID"` | `jj diff --git --context=0 --from "$MERGE_BASE" --to "$HEAD_OID"` |
| git | `git merge-base "origin/$BASE" "$HEAD_OID"` | `git diff --name-status "$MERGE_BASE" "$HEAD_OID"` | `git diff --unified=0 "$MERGE_BASE" "$HEAD_OID"` |

<IMPORTANT>
The changed-line map is the anchoring contract. GitHub accepts an inline comment
only on a line present in the diff, so record, per file, every added line number
on the RIGHT side and every removed line number on the LEFT side. A finding that
cannot anchor moves into the overall body in step 9 — it is never dropped and
never posted against a guessed line.
</IMPORTANT>

Deleted files, binary files, and generated or vendored paths carry no reviewable
lines; list them in the overall body instead of assigning them to a reviewer.

### 5. Run the mechanical candidate scan

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/pyrun.sh" \
  "${CLAUDE_PLUGIN_ROOT}/scripts/scan_potential_violations.py" \
  <changed-files-in-REVIEW_DIR> --category all --before 5 --after 10
```

The wrapper resolves Python 3.13+ and may route repair through
`coding:sync-tool`; surface a hard install failure rather than skipping the scan
silently. Candidates are advisory — a candidate becomes a finding only when the
owning reviewer confirms it against the rule it cites.

### 6. Resolve the applicable standards

Collect standard file paths from the "Plugin Constitution > Standards" sections
of the system prompt, falling back to a Glob for `**/constitution/standards/**`
when absent. Select by matching file stems to the changed languages, always
include `code-review.md`, and add the `testing` standards whenever any
`*.spec.*` or `*.test.*` file changed. Pass **paths** to reviewers — the parent
never reads standard bodies into its own context.

### 7. Dispatch reviewers

Dispatch the selected areas in one parallel batch of read-only reviewers per
[references/dispatch.md](references/dispatch.md), which carries the per-area
mandates, the inputs each reviewer receives, and the finding `<report>` schema.
Area ownership and evidence rules are shared with `coding:review-code` through
[its mandates](../review-code/references/mandates.md); do not restate or
contradict them here.

The `testing` reviewer answers one question above coverage: **would these tests
fail if the implementation regressed?** Assertions that restate the
implementation, tests with no meaningful assertion, mocks that verify only
themselves, and new behavior with no test at all are findings. Say what to test
and why it matters, never a bare "add tests".

### 8. Anchor and de-duplicate

Match every finding to the step-4 map: keep it when its file and line appear in
the diff, and set `side` to `RIGHT` for added lines or `LEFT` for removed lines.
Move anything unanchorable to the overall body with its file and line named in
the text.

Then read what is already on the PR and stay quiet about it:

```bash
gh api "repos/$OWNER/$REPO/pulls/$PR/comments" --paginate \
  --jq '.[] | {path, line, body}'
```

Skip any finding already made at the same path and line. A re-review after a
push adds only what is new — repeated comments read as noise and cost the review
its authority.

### 9. Publish the review

Build the overall body from
[references/templates/overall-review.md](references/templates/overall-review.md)
and submit the whole review in one atomic call, so a rejected comment can never
leave orphaned fragments on the PR:

```bash
gh api --method POST "repos/$OWNER/$REPO/pulls/$PR/reviews" --input payload.json
```

`payload.json` carries `commit_id` (the pinned `HEAD_OID`), `body`, `event`, and
a `comments[]` array of `{path, line, side, body}`. Payload construction, the
multi-line `start_line` form, the 422 recovery path, and retry rules are in
[references/publishing.md](references/publishing.md).

Derive `event` from the findings; never choose it freely:

| Outstanding findings | `event` |
|---|---|
| Any P0/P1 `issue:` finding | `REQUEST_CHANGES` |
| Only P2/P3 findings or none, and the tests genuinely cover the change | `APPROVE` |
| Tests missing or unconvincing, or a blocker prevented a full review | `COMMENT` |

GitHub rejects `APPROVE` and `REQUEST_CHANGES` on your own PR. Compare the PR
author against `gh api user --jq .login` first; on a self-review, downgrade to
`COMMENT` and state the downgrade in the body rather than letting the submission
fail. With `--dry-run`, print the payload and post nothing.

### 10. Verify and report

Re-read `headRefOid`. If it moved during the review, say so plainly — the
published review describes the SHA it read, not the current head.

## Verification

- The temporary checkout was created under `${TMPDIR:-/tmp}` and removed; no jj
  workspace or git worktree from this run remains in `jj workspace list` or
  `git worktree list`.
- Every posted inline comment resolves to a file and line present in the step-4
  map, and no comment duplicates one already on the PR.
- Every finding cites concrete evidence — a file, a line, and the standard or
  failure path it rests on. Reviewed code is unchanged and nothing was pushed.
- The submitted `event` matches the severity table, or the self-review downgrade
  is stated in the body.

## Completion

Report the review URL, the reviewed head SHA, the change-tracking path taken
(`jj` or `git`), finding counts by priority, the submitted `event`, any
unanchored findings carried into the overall body, files excluded as
binary/generated, and confirmation that the temporary checkout was removed. On a
blocked run, name the blocker and state which areas never ran — a partial review
must never be reported as a complete one.
