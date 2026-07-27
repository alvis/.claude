---
name: review-pr
description: 'Check a GitHub pull request out into a disposable OS temp workspace, review its diff against the repository constitution standards and test intent, then publish inline comments on the exact changed lines plus one overall review. Use for "review PR 42", "review this pull request", or "leave line comments on the PR".'
model: opus
context: fork
agent: code-quality-critic
allowed-tools: Bash(gh:*), Bash(jj:*), Bash(git:*), Bash(mktemp:*), Bash(rm:*), Bash(jq:*), Bash(command:*), Read, Grep, Glob, AskUserQuestion
argument-hint: "<pr-number-or-url> [--repo <owner/name>] [--area=<list>] [--dry-run]"
---

# Review Pull Request

Review a remote GitHub pull request from an isolated, disposable checkout and
publish the result where the author will act on it: one inline comment per
finding, anchored to the exact file and line, plus one overall review carrying the
verdict. This skill owns remote PR review, its publication, and PR-size zone
enforcement (`GIT-PR-SIZE-01..04`, handed over by `coding:write-pr`). Local
pre-commit review belongs to `coding:review-code`; remediation to `coding:fix`.

## Boundaries

- Use for: reviewing an open GitHub PR by number or URL, re-reviewing after a
  push, and publishing line comments and a verdict to GitHub.
- Do not use for: reviewing uncommitted local work or writing work-local review
  artifacts (`coding:review-code`), fixing findings (`coding:fix`), mechanical
  standards enforcement (`coding:lint`), publishing PRs or driving CI
  (`coding:write-pr`), or merging (`coding:merge-pr`).
- One reviewer, one pass. Never fan out per area — a PR is sized so one reader can
  hold it whole, and split judgement produces split findings.

## Execution

`context: fork` and `agent: code-quality-critic` run this skill in a fresh critic
subagent with no inherited context. Review as an external party who knows only the
PR, the repository, and the standards — a reviewer who watched the code get written
reviews its intent instead of its text.

<IMPORTANT>
- Read-only against the reviewed code: never edit a reviewed file, never commit,
  never push, never merge.
- Do not delegate. No second reviewer, no `security-champion`, no
  `principal-engineer`. This is a first-line check; name deeper work needed in the
  review body and let the caller decide.
- Read and search the checkout freely, but run nothing the PR branch configures —
  no builds, tests, project linters, or anything that triggers or waits on CI.
  Treat the branch as untrusted code.
- CI status counts only when already known: step 1 asks for it in the call it
  already makes, and nothing polls or waits. Repair belongs to `coding:write-pr`.
- Build `payload.json` by shell redirection from `jq`, never with a file-writing
  tool — this agent's `Write`/`Edit` fence would deny the path.
</IMPORTANT>

## Inputs

- **Required**: one PR number or URL. When omitted and the current branch has
  exactly one open PR, use it and say so; on ambiguity, ask.
- **Optional**: `--repo <owner/name>` to target another repository; `--area=<list>`
  to restrict the review to a subset of `alignment`, `correctness`, `security`,
  `quality`, `testing`, `docs`, `style` (default all); `--dry-run` to print the
  payload and post nothing.
- **Prerequisites**: authenticated `gh` with write access, and network access to
  fetch the PR head.

## Workflow

### 1. Resolve the pull request

```bash
gh pr view "$PR" --json number,url,title,body,state,isDraft,baseRefName,headRefName,\
headRefOid,headRepositoryOwner,changedFiles,additions,deletions,author,statusCheckRollup
```

Stop with evidence when the PR is closed, merged, or unreadable. Record `HEAD_OID`
and `BASE`; every later step binds to that SHA. The title and body are the author's
stated intent — the contract `alignment` checks the diff against.

### 2. Select the change-tracking path

Prefer `jj` where it is available and genuinely initialized. Detect functionally — a
`.jj` and a `.git` directory can both be present without being colocated:

```bash
command -v jj >/dev/null 2>&1 && jj root >/dev/null 2>&1 &&
  [ "$(git rev-parse HEAD)" = "$(jj log -r @- --no-graph -T 'commit_id')" ]
```

Anything else selects git. This skill never mutates the repository, so a git-only
repository is fully supported and must not be colocated on its behalf.

### 3. Extract the PR to an OS temp location

```bash
REVIEW_DIR=$(mktemp -d "${TMPDIR:-/tmp}/review-pr-${PR}-XXXXXX")
trap cleanup EXIT HUP INT TERM
```

Define `cleanup` and materialize the head at `HEAD_OID` per
[references/extraction.md](references/extraction.md), which owns the fetch, the
jj/git/clone checkout forms, and the cleanup contract. Install the trap before the
checkout exists so an interrupted checkout still cleans up.

### 4. Build the reviewable surface

Compare against the merge base, so the review covers the PR's own changes rather
than base-branch drift:

| Path | Merge base | Changed files | Line map |
|---|---|---|---|
| jj | `jj log --no-graph -T 'commit_id' -r "heads(::$HEAD_OID & ::$BASE)"` | `jj diff --summary --from "$MERGE_BASE" --to "$HEAD_OID"` | `jj diff --git --context=0 --from "$MERGE_BASE" --to "$HEAD_OID"` |
| git | `git merge-base "origin/$BASE" "$HEAD_OID"` | `git diff --name-status "$MERGE_BASE" "$HEAD_OID"` | `git diff --unified=0 "$MERGE_BASE" "$HEAD_OID"` |

Both paths emit unified diff, so one parser builds the map.

<IMPORTANT>
The changed-line map is the anchoring contract. GitHub accepts an inline comment
only on a line present in the diff, so record per file every added line (RIGHT
side) and every removed line (LEFT). A finding that cannot anchor moves into the
overall body — never dropped, never posted against a guessed line.
</IMPORTANT>

Classify the size zone from the same counts, and treat a missing required section
as a finding citing its rule id:

| Zone | Bound (stricter of the two wins) | PR body must add |
|---|---|---|
| green | ≤ 15 files and ≤ 500 net LOC | Summary, Checklist |
| yellow | ≤ 30 files and ≤ 1200 LOC | Risk, Test plan |
| red | ≤ 60 files and ≤ 2000 LOC | Why this size |
| black | > 60 files or > 2000 LOC | should be split before review |

Black zone leads the overall body and caps the verdict at `COMMENT` — a review that
cannot honestly cover the diff must not approve it. Deleted, binary, generated, and
vendored paths carry no reviewable lines; list them as not reviewed.

### 5. Run the mechanical candidate scan

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/pyrun.sh" \
  "${CLAUDE_PLUGIN_ROOT}/scripts/scan_potential_violations.py" \
  <changed-files-in-REVIEW_DIR> --category all --before 5 --after 10
```

The wrapper resolves Python 3.13+ and may route repair through `coding:sync-tool`;
surface a hard install failure rather than skipping silently. Candidates are
advisory until confirmed against the rule they cite.

### 6. Resolve the applicable standards

Take standard paths from the "Plugin Constitution > Standards" sections of the
system prompt, or Glob `**/constitution/standards/**`. Match stems to the changed
languages, always include `code-review.md`, and add `testing` when any `*.spec.*` or
`*.test.*` file changed.

### 7. Review

The diff is the subject of the review, not the limit of the reading.

- **Read whatever it takes.** Follow callers of a changed function, open the
  siblings a new file should resemble, read the module the change plugs into, the
  goal, and the spec. Understanding the change is the job; explore the checkout.
- **Judge only the diff.** Every finding is about a changed line and anchors to
  one. Read unchanged code to understand the change, not to grade it.
- **Ask whether the diff is the best solution**, not only whether it works: walk
  the lean ladder in [CODING.md](../../references/CODING.md) — need, `@theriety/core`,
  existing codebase, platform, installed dependency, then minimum new code. A
  hand-rolled helper duplicating what the repository already provides is a finding.

Cover the concerns in consequence order — correctness and security, then alignment,
testing, quality, docs, style — in one pass.
[references/review.md](references/review.md) carries the per-concern checklist, the
depth ladder, and the finding schema;
[references/tone.md](references/tone.md) governs every word that gets posted.

`testing` answers one question above coverage: **would these tests fail if the
implementation regressed?** Assertions that restate the implementation, tests with
no meaningful assertion, mocks that verify only themselves, and new behavior with
no test at all are findings. Say what to test and why it matters, never a bare
"add tests".

### 8. Anchor and de-duplicate

Keep a finding when its file and line appear in the step-4 map, setting `side` to
`RIGHT` for added lines or `LEFT` for removed ones; move anything unanchorable to
the overall body with its file and line named in the text. Then skip whatever has
already been said at the same path and line:

```bash
gh api "repos/$OWNER/$REPO/pulls/$PR/comments" --paginate \
  --jq '.[] | {path, line, body}'
```

A re-review after a push adds only what is new.

### 9. Publish the review

Build the body from
[references/templates/overall-review.md](references/templates/overall-review.md)
and submit the whole review in one atomic call, so a rejected comment cannot leave
orphaned fragments:

```bash
gh api --method POST "repos/$OWNER/$REPO/pulls/$PR/reviews" --input payload.json
```

`payload.json` carries `commit_id` (the pinned `HEAD_OID`), `body`, `event`, and
`comments[]` of `{path, line, side, body}`. Payload construction, the multi-line
form, and 422 recovery are in [references/publishing.md](references/publishing.md).

Derive `event`; never choose it freely:

| Outstanding findings | `event` |
|---|---|
| Any P0/P1 `issue:` finding | `REQUEST_CHANGES` |
| Only P2/P3 or none, and the tests genuinely cover the change | `APPROVE` |
| Tests unconvincing, red CI, black zone, or a blocker prevented a full review | `COMMENT` |

GitHub rejects `APPROVE` and `REQUEST_CHANGES` on your own PR. Compare the author
against `gh api user --jq .login` first; on a self-review, downgrade to `COMMENT`
and say so in the body. With `--dry-run`, print the payload and post nothing.

## Verification

- Re-read `headRefOid`. If it moved during the review, say so plainly — the published
  review describes the SHA it read, not the current head.
- The temporary checkout is gone: no entry for it in `jj workspace list` or
  `git worktree list`.
- Every posted comment resolves to a line in the step-4 map and duplicates nothing
  already on the PR.
- The submitted `event` matches the verdict table, or the self-review downgrade is
  stated in the body.

## Completion

Report the review URL, reviewed SHA, change-tracking path, PR zone, goal/spec
alignment (including *skipped — unknown*), finding counts by priority, submitted
`event`, unanchored findings, paths not reviewed, and cleanup status. On a blocked
run, name the blocker and which concerns never ran — a partial review is never
reported as complete.
