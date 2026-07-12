# Plan Context Capture (Post-Review Fixes)

When this skill runs after a `/coding:review-code` in the same session, the
plan that the review validated against must be pinned into the fix context so
a follow-up `/coding:review-code` can be re-run against the identical
contract and produce comparable drift verdicts.

## Detect the trigger

No dedicated flag is needed. Treat the run as post-review when the input
references a review report or YAML findings from `/coding:review-code`, when
`--note` mentions a review, or when the prior turn ran `/coding:review-code`.

## Resolve the plan source (first match wins)

1. Explicit path passed via `--plan=<path>` — always wins when provided.
2. The active plan-mode plan file surfaced by the Claude Code harness for the
   current session. This is the authoritative source when the session is in —
   or has just exited — plan mode. Do NOT hardcode this path; read it from
   the harness-provided session context.
3. The `plan_source` echoed by the preceding review report, if present.
4. Repo-level fallback (requires confirmation): if a repo-level plan doc is
   discoverable (`PLAN.md`, `DRAFT.md`, or `DESIGN.md` at the repo root or
   scope directory), use AskUserQuestion to ask whether to adopt one of them
   or none. Never silently adopt a repo plan when there is no plan-mode plan —
   a stale repo doc may not match what the review actually validated against.
5. Otherwise record `plan_source: none_found` and treat the review report
   itself as the best-available contract.

## Inject and preserve

- Read the resolved plan document in full and treat it as a first-class input
  alongside the error context.
- Echo its absolute path and a one-line digest into every fix subtask prompt
  so downstream agents stay aligned with the same contract.
- Carry the path into the completion report as `plan_source` so the follow-up
  review can be invoked with the same `--plan` argument.
