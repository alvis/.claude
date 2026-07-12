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
- Give each subagent exact paths, constraints, and the standards it must read.
  Instruct it to read assigned standards recursively: if standard A references
  standard B, read B too.

## Reports

- Bound execution reports to under 1000 tokens and review reports to under
  500 tokens; request only the fields the orchestrator will act on.
- Wrap each returned report in `<report>...</report>` and each hard guardrail
  in the prompt in `<IMPORTANT>...</IMPORTANT>`, following the Content
  Boundary Convention in `authoring-invariants.md`.

## Review and decision

- Reviews are read-only; a review subagent must not modify resources.
- Decide per batch from the combined reports:
  - **Proceed**: success or acceptable partial success — continue.
  - **Fix**: minor failures — re-dispatch only the failed items.
  - **Rollback**: critical failure — revert the batch, then re-dispatch.
- Bound retries (typically 2 per batch), then report the remaining issues
  instead of looping.
