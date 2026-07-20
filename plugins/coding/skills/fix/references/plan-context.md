# Contract pinning for post-review fixes

When fixing a `coding:review-code` finding, pin the identical contract used by
the alignment review so the rerun produces comparable drift verdicts.

Resolve in this order:

1. Explicit `--plan=<absolute-path>` supplied to both review and fix.
2. `plan_source` returned by the preceding review.
3. The plan/lifecycle section of the active work root's `state.md`.
4. If none exists, record `plan_source: none_found`; the named review finding
   and linked authoritative spec are the best available contract.

Never discover or confirm a root-level fallback. Read the resolved source in
full. Send its absolute path plus one-line digest, work ID/root, finding ID, and
relevant spec/design paths to every fix subtask. Carry `plan_source` unchanged
into completion and the rerun invocation.
