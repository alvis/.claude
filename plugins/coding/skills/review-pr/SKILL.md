---
name: review-pr
description: 'Review a GitHub pull request from an isolated checkout of its head, judging the diff against the repository constitution standards and test intent, then publish inline comments on the exact changed lines plus one overall review. Use for "review PR 42", "review this pull request", or "leave line comments on the PR".'
model: opus
context: fork
agent: code-quality-critic
allowed-tools: Bash(gh:*), Bash(jj:*), Bash(git:*), Bash(mktemp:*), Bash(rm:*), Bash(jq:*), Bash(command:*), Read, Grep, Glob, AskUserQuestion
argument-hint: "[<pr-number-or-url> | <source-tree-path>] [--repo <owner/name>] [--area=<list>] [--dry-run]"
---

# Review Pull Request

Review a remote GitHub pull request and publish the result where the author will
act on it: one inline comment per finding, anchored to the exact file and line,
plus one overall review carrying the verdict. This skill owns remote PR review, its
publication, and PR-size zone enforcement (`GIT-PR-SIZE-01..04`, handed over by
`coding:write-pr`). Local pre-commit review belongs to `coding:review-code`;
remediation to `coding:fix`.

## Boundaries

- Use for: reviewing an open GitHub PR by number, URL, or the path of a source tree
  holding its head; re-reviewing after a push; publishing line comments and a
  verdict to GitHub.
- Do not use for: reviewing uncommitted local work or writing work-local review
  artifacts (`coding:review-code`), fixing findings (`coding:fix`), mechanical
  standards enforcement (`coding:lint`), publishing PRs or driving CI
  (`coding:write-pr`), or merging (`coding:merge-pr`).
- One reviewer, one pass. Never fan out per area — a PR is sized so one reader can
  hold it whole, and split judgement produces split findings.

## Execution

`context: fork` and `agent: code-quality-critic` run this skill in a fresh critic
subagent with no inherited context. Review as an external party who knows only the
PR, the repository, and the standards.

<IMPORTANT>
- Read-only against the reviewed code. Confine every mutation to the review tree
  this run created and to the review published on GitHub.
- Do not delegate.
- Read and search the checkout as widely as the change requires; run only the
  read-only git, `gh`, and scanner commands named below. Treat the branch as
  untrusted code.
- CI status counts only when already known, from the metadata *Resolve the pull
  request* already fetches. Repair belongs to `coding:write-pr`.
- Build `payload.json` by shell redirection from `jq`, never with a file-writing
  tool — this agent's `Write`/`Edit` fence would deny the path.
</IMPORTANT>

## Inputs

- **Required**: one PR number, PR URL, or source tree path. When omitted, resolve
  from the current tree. On ambiguity, ask.
- **Optional**: `--repo <owner/name>` to target another repository; `--area=<list>`
  to restrict the review to a subset of `alignment`, `correctness`, `security`,
  `quality`, `testing`, `docs`, `style` (default all); `--dry-run` to print the
  payload and post nothing.
- **Prerequisites**: authenticated `gh` with write access, and network access to
  reach the PR.

## Workflow

### Resolve the pull request

From a PR number or URL, read its metadata directly:

```bash
gh pr view "$PR" --json number,url,title,body,state,isDraft,baseRefName,headRefName,\
headRefOid,headRepositoryOwner,changedFiles,additions,deletions,author,statusCheckRollup
```

From a source tree path — or no argument at all, meaning the current tree — resolve
which PRs that tree carries. A tree may hold a whole stack, so match every open PR
head against its history rather than assuming one:

```bash
gh pr list --state open --json number,headRefName,headRefOid,baseRefName
git -C "$TREE" merge-base --is-ancestor "$HEAD_REF_OID" HEAD   # per candidate PR
```

Order the matches bottom-up by their base chain — each PR's `baseRefName` is the
previous PR's `headRefName` — and review each in that order, so a finding lands on
the PR that introduced it rather than the one that inherited it. No match is a clean
stop naming the tree and its HEAD; an unresolvable tangle asks.

Stop with evidence when a PR is closed, merged, or unreadable. Record `HEAD_OID` and
`BASE` per PR; everything downstream binds to that SHA.

### Select the change-tracking path

Prefer `jj` where it is available and genuinely initialized. Detect functionally — a
`.jj` and a `.git` directory can both be present without being colocated:

```bash
command -v jj >/dev/null 2>&1 && jj root >/dev/null 2>&1 &&
  [ "$(git rev-parse HEAD)" = "$(jj log -r @- --no-graph -T 'commit_id')" ]
```

Anything else selects git. This skill never mutates the repository, so a git-only
repository is fully supported and must not be colocated on its behalf.

### Locate or create the review tree

Reuse before you extract. A tree already sitting at `HEAD_OID` is the same content a
fresh checkout would produce, minus the cost:

1. Search for a candidate at `HEAD_OID` — the invoked tree first, then entries from
   `git worktree list --porcelain` and `jj workspace list`.
2. Accept one only when `git -C <tree> rev-parse HEAD` equals `HEAD_OID` **and**
   `git -C <tree> status --porcelain` is empty. A dirty tree is not the PR head, and
   reviewing it would describe uncommitted work as if the author had pushed it.
3. With no candidate, create a disposable checkout and record that this run owns it:

   ```bash
   REVIEW_DIR=$(mktemp -d "${TMPDIR:-/tmp}/review-pr-${PR}-XXXXXX")
   REVIEW_TREE_OWNED=true
   trap cleanup EXIT HUP INT TERM
   ```

[references/extraction.md](references/extraction.md) carries the checkout forms and
the cleanup contract.

<IMPORTANT>
`cleanup` removes a tree only when `REVIEW_TREE_OWNED` is true. A reused tree
belongs to the user and its removal would destroy real work.
</IMPORTANT>

### Build the reviewable surface

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

### Run the mechanical candidate scan

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/pyrun.sh" \
  "${CLAUDE_PLUGIN_ROOT}/scripts/scan_potential_violations.py" \
  <changed-files-in-review-tree> --category all --before 5 --after 10
```

The wrapper resolves Python 3.13+ and may route repair through `coding:sync-tool`;
surface a hard install failure rather than skipping silently. Candidates are
advisory until confirmed against the rule they cite.

### Resolve the applicable standards

Take standard paths from the "Plugin Constitution > Standards" sections of the
system prompt, or Glob `**/constitution/standards/**`. Match stems to the changed
languages, always include `code-review.md`, and add `testing` when any `*.spec.*` or
`*.test.*` file changed.

### Review

The diff is the subject of the review, not the limit of the reading.

- **Read whatever it takes.** Follow callers of a changed function, open the
  siblings a new file should resemble, read the module the change plugs into, the
  goal, and the spec. Understanding the change is the job; explore the checkout.
- **Judge only the diff.** Every finding is about a changed line and anchors to
  one. Read unchanged code to understand the change, not to grade it.
- **Ask whether the diff is the best solution**, not only whether it works: walk
  the lean ladder in [WORKFLOW.md](../../references/WORKFLOW.md) — need, `@theriety/core`,
  existing codebase, platform, installed dependency, then minimum new code. A
  hand-rolled helper duplicating what the repository already provides is a finding.
- **Say so when the change belongs somewhere else.** A guard repeated at each call
  site that belongs in the callee, validation in a controller that belongs in the
  domain, a symptom patched downstream of the function that produced the bad value —
  propose the better location and name the exact path. Never relocate it yourself.

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

### Anchor and de-duplicate

Keep a finding when its file and line appear in the changed-line map, setting `side`
to `RIGHT` for added lines or `LEFT` for removed ones; move anything unanchorable to
the overall body with its file and line named in the text. Then skip whatever has
already been said at the same path and line:

```bash
gh api "repos/$OWNER/$REPO/pulls/$PR/comments" --paginate \
  --jq '.[] | {path, line, body}'
```

A re-review after a push adds only what is new.

### Publish the review

Build the body from
[references/templates/overall-review.md](references/templates/overall-review.md)
and submit the whole review in one atomic call, so a rejected comment cannot leave
orphaned fragments:

```bash
gh api --method POST "repos/$OWNER/$REPO/pulls/$PR/reviews" --input payload.json
```

`payload.json` carries `commit_id` (the pinned `HEAD_OID`), `body`, `event`, and
`comments[]` of `{path, line, side, body}`. Payload construction and 422 recovery
are in [references/publishing.md](references/publishing.md).

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
- A created review tree is gone and leaves no entry in `jj workspace list` or
  `git worktree list`; a reused tree is untouched, still clean, still at `HEAD_OID`.
- Every posted comment resolves to a line in the changed-line map and duplicates
  nothing already on the PR.
- The submitted `event` matches the verdict table, or the self-review downgrade is
  stated in the body.

## Completion

Report per PR reviewed: review URL, reviewed SHA, the review tree used and whether
it was reused or created, change-tracking path, PR zone, goal/spec alignment
(including *skipped — unknown*), finding counts by priority, submitted `event`,
unanchored findings, and paths not reviewed. For a stack, report each PR in the same
bottom-up order it was reviewed. On a blocked run, name the blocker and which
concerns never ran — a partial review is never reported as complete.
