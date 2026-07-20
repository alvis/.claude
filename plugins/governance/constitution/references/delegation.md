# Delegated Execution

Operational guidance for skills whose workflow dispatches subagents.
Delegation is a context-economics decision: delegate a step when performing
it directly would consume more session context than the tokens needed to
describe the task and read the report back — bulk file reads, noisy command
output, transformations over many independent resources. Keep small work
inline; delegation that saves no context only adds latency and failure modes.
Skills that adopt these rules link this file at the dispatch step and may
tighten any bound with a skill-specific value.

## Batching and dispatch

- Batch at most ~10 resources per subagent, one subagent per batch; the bound
  keeps each report reviewable and a failed batch cheap to retry.
- Dispatch independent batches in parallel in a single message.
- Stop dispatching further batches while reported issues remain unresolved.
- Give each subagent one bounded mission capsule with exact paths, constraints,
  and the standards it must read. Every `Agent`, `Task`, and `SendMessage` body
  must stay at or below 4,096 characters. Put longer assignments in a durable,
  secret-free task artifact and send its absolute path plus at most two summary
  lines. Instruct the recipient to read referenced standards recursively.

## Reports

- Request only fields the orchestrator will act on. Routine execution reports
  are terse deltas; reviews return `ok` or `blocked` plus at most two lines.
  Detailed evidence belongs in a bounded artifact sent directly to the worker
  that needs it; the orchestrator receives the verdict and path, not a relay.
- When a structured report is required, keep it below 1000 tokens and wrap it
  in `<report>...</report>`. Put each hard guardrail in
  `<IMPORTANT>...</IMPORTANT>`, following the Content Boundary Convention in
  `authoring-invariants.md`, without exceeding the message ceiling.

## Review and decision

- Reviews are read-only; a review subagent must not modify resources.
- Decide per batch from the combined reports:
  - **Proceed**: success or acceptable partial success — continue.
  - **Fix**: minor failures — re-dispatch only the failed items.
  - **Rollback**: critical failure — revert the batch, then re-dispatch.
- Bound retries (typically 2 per batch), then report the remaining issues
  instead of looping.
