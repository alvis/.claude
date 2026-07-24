# Publishing the review to GitHub

Load this at step 9 of `coding:review-pr`. It pins the payload shape, the
failure recovery path, and the rules that keep a re-review from becoming noise.

## Why one atomic call

The GitHub reviews API accepts the body, the verdict, and every inline comment
in a single `POST`. Use it. The alternative — create a pending review, add
comments one at a time, submit — leaves a half-populated pending review on the
PR whenever any step fails, and a pending review is invisible to the author but
blocks the next run from starting cleanly.

```bash
gh api --method POST "repos/$OWNER/$REPO/pulls/$PR/reviews" --input payload.json
```

## Payload

```json
{
  "commit_id": "<HEAD_OID resolved in step 1>",
  "body": "<overall review, from templates/overall-review.md>",
  "event": "REQUEST_CHANGES | APPROVE | COMMENT",
  "comments": [
    {
      "path": "src/auth/session.ts",
      "line": 42,
      "side": "RIGHT",
      "body": "issue: …"
    },
    {
      "path": "src/auth/session.ts",
      "start_line": 51,
      "line": 58,
      "side": "RIGHT",
      "body": "suggestion: …"
    }
  ]
}
```

- `commit_id` is mandatory here even though the API treats it as optional.
  Without it GitHub anchors against the current head, so a push mid-review
  silently relocates every comment.
- `line` is the line number in the file at `commit_id`, not a diff offset.
- `start_line` opens a multi-line comment and must be less than `line`, on the
  same `side`. Use it when the finding is about a block, not a line — pointing at
  one arbitrary line of a five-line problem reads as imprecision.
- Build the JSON with `jq` from the reviewer reports rather than by hand. Comment
  bodies contain newlines, backticks, and code fences; hand-assembled JSON breaks
  on the first one.

```bash
jq -n --arg commit "$HEAD_OID" --arg body "$OVERALL" --arg event "$EVENT" \
  --slurpfile comments comments.json \
  '{commit_id: $commit, body: $body, event: $event, comments: $comments[0]}' \
  > payload.json
```

## Failure recovery

| Response | Cause | Action |
|---|---|---|
| 422 naming a comment path or line | The line is not in the diff | Drop that one comment, move its text into the overall body as an unanchored finding, resubmit once. |
| 422 on `APPROVE`/`REQUEST_CHANGES` | Self-review | Resubmit with `COMMENT`; state the downgrade in the body. |
| 403 | Missing write access, or a rate limit | Report the blocker with `gh auth status`; do not retry blindly. |
| 404 | Wrong `$OWNER/$REPO`, or no access | Re-resolve from step 1; do not create anything. |
| 5xx or network failure | Transient | Retry up to three times with 2s, 4s, 8s backoff. Verify with `gh api repos/$OWNER/$REPO/pulls/$PR/reviews --jq 'last'` before retrying, so a review that landed is never posted twice. |

Never respond to a 422 by re-anchoring the comment to a nearby line that happens
to be in the diff. A comment on the wrong line costs more author time than no
comment at all.

## Re-review hygiene

Before building the payload, read what is already there:

```bash
gh api "repos/$OWNER/$REPO/pulls/$PR/comments" --paginate \
  --jq '.[] | {path, line, body}'
```

- Skip a finding whose path, line, and substance already appear. The author has
  seen it.
- When a previous finding is now fixed, do not post about it inline. Note it once
  in the overall body — acknowledging the fix is what makes the next round of
  feedback land.
- Never resolve or reply to another reviewer's threads. This skill adds its own
  review; it does not moderate the conversation.

## Verdict

The table in `SKILL.md` step 9 is the whole rule, and it is derived, not chosen.
Two clarifications:

- "The tests genuinely cover the change" means the `testing` reviewer confirmed
  the tests would fail on regression. Coverage percentage is not that
  confirmation.
- A blocker — an area that could not run, a file too large to read, a missing
  standard — caps the verdict at `COMMENT`. Approving what you did not read is
  the one failure this skill must never commit.
