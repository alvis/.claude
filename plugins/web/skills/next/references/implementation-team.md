# Implementation Team Dispatch

Bounds for delegating multi-file code fixes discovered during a `next` debugging session. Delegate only when doing the edits directly would consume more session context than briefing teammates and reading their reports; small fixes stay inline. General batching, report, and decision rules live in `plugins/governance/constitution/references/delegation.md`; the values below tighten them for this skill.

## Sizing

Estimate scope by counting the components, hooks, and files implied by the task, then create a persistent team via `TeamCreate`:

- implementer teammates (haiku) — `ceil(files / 10)`, minimum 1; the 10-file bound keeps each slice reviewable and a failed slice cheap to retry
- 1 reviewer teammate (sonnet)

## Partitioning and briefing

Partition the file set so each implementer owns a coherent slice — by feature, route, or component cluster, never random shards. Brief each implementer with its slice plus standards as paths only:

- `plugins/react/constitution/standards/`
- `plugins/web/constitution/standards/`

## Cycle

Implementers stream completed files; the reviewer audits each batch; the lead orchestrates and aggregates only (never reads file bodies); `TeamDelete` on completion.

## Context rotation

Every `SendMessage` reply must include `context_used: <token-count>`. When `context_used > 150_000` for any teammate, delete that teammate via `TeamDelete`, spawn a replacement via `TeamCreate`, and re-issue the in-flight slice with a brief handover: files completed, files remaining, decisions made.
