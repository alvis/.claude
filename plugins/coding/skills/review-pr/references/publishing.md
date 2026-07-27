# Publishing the review to GitHub

Load this from the *Publish the review* step of `coding:review-pr`.

Submit body, verdict, and every inline comment in one `POST`. The create-pending /
add-comments / submit sequence leaves a half-populated pending review on the PR when
any step fails, and a pending review is invisible to the author but blocks the next
run.

```bash
gh api --method POST "repos/$OWNER/$REPO/pulls/$PR/reviews" --input payload.json
```

## Payload

```json
{
  "commit_id": "<the pinned HEAD_OID>",
  "body": "<overall review, from templates/overall-review.md>",
  "event": "REQUEST_CHANGES | APPROVE | COMMENT",
  "comments": [
    { "path": "src/auth/session.ts", "line": 42, "side": "RIGHT", "body": "issue: …" },
    { "path": "src/auth/session.ts", "start_line": 51, "line": 58, "side": "RIGHT", "body": "suggestion: …" }
  ]
}
```

- `commit_id` is mandatory here even though the API treats it as optional. Without
  it GitHub anchors against the current head, so a push mid-review silently
  relocates every comment.
- `line` is the line number in the file at `commit_id`, not a diff offset.
- `start_line` must be below `line` on the same `side`.

Assemble the file with `jq` and shell redirection into the review tree. Comment
bodies carry newlines, backticks, and code fences, so string-concatenated JSON breaks
on the first one — and a file-writing tool is denied by this agent's `Write`/`Edit`
fence.

## Failure recovery

| Response | Cause | Action |
|---|---|---|
| 422 naming a comment path or line | The line is not in the diff | Drop that comment, move its text into the overall body as an unanchored finding, resubmit once. |
| 422 on `APPROVE`/`REQUEST_CHANGES` | Self-review | Resubmit with `COMMENT`; state the downgrade in the body. |

Never answer a 422 by re-anchoring the comment to a nearby line that happens to be
in the diff. A comment on the wrong line costs more author time than no comment.

## Re-review hygiene

- Skip a finding whose path, line, and substance already appear in
  `gh api repos/$OWNER/$REPO/pulls/$PR/comments`. The author has seen it.
- A previously reported finding that is now fixed gets one line in the overall body,
  not a new inline comment. Acknowledging the fix is what makes the next round land.
- Never resolve or reply to another reviewer's threads. This skill adds its own
  review; it does not moderate the conversation.
