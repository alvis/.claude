# Finishing a work stream

Read this when a stream's execution finishes, and when a `reviewing` stream is
settled on resume. Everyday planning does not need it — the always-read
contract states only the rule, and the detail lives here.

## One stream at a time

Work **one** stream to completion before starting another. Parallel streams
split attention and leave an overview full of things nobody is finishing. The
next stream starts once the previous one reaches `reviewing` or `completed`; a
stream waiting on someone else is marked `blocked` and released, which is how
capacity is freed rather than by opening a second front.

## Execution finished is not terminal

Finished execution lands in `reviewing`, never straight in a terminal state:

1. Propose the stream's pull request(s) — code delivery routes through
   [coding:write-pr](../../coding/skills/write-pr/SKILL.md).
2. Set lifecycle `reviewing` and record the PR reference(s) in `state.md`, so
   whoever resumes can check them without rediscovering the branch.
3. Reconcile the stream's `overview.md` row.

`reviewing` requires every required executable leaf to be `done` **and** the
pull request(s) recorded. Such a stream is not resumable — there is no next
task to hand anyone — and it is not a mere index marker either: it holds the
one-stream-at-a-time slot until its verdict arrives.

## `completed` requires merge evidence

`completed` is terminal and reachable **only** from `reviewing`, **only** on
merge evidence:

- the recorded pull request(s) observed merged
  (`gh pr view <n> --json state,mergedAt`); or
- with no PR recorded, the stream's branch observed merged into the default
  branch, or its changes observed present there.

An author's assertion that the work is finished is never merge evidence.
Passing tests are not either, while review, sync, publication, or history
anchoring remains required.

[essential:takeover](../skills/takeover/SKILL.md) settles every `reviewing`
stream against this rule before it offers the next task, and asks — never
assumes — whether a settled stream's source tree should be removed, routing
any removal to [coding:cleanup](../../coding/skills/cleanup/SKILL.md).
