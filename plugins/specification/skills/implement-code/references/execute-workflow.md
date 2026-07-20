# Execution mechanisms

The parent selects Workflow fan-out for independent code-producing slices and a
sequential Coding chain otherwise. The orchestrator does not edit source or
history.

## Shared dispatch contract

Each child receives absolute repository/work paths, exact specification refs
and headings, one plan slice, acceptance criteria, deviation policy, and the
Essential output-manifest rule. Coding agents treat work-spec MDC as read-only.
Architectural uncertainty returns `pending_decision`; only the orchestrator may
ask and route the answer through `specification:mdc`.

## Workflow mechanism

1. Slice planned execution by linked implementation-plan slice, iteration by
   pending-work/test cluster, and audit completion by independently fixable gap.
2. Fan out independent slices. Each runs its mode-appropriate Coding writer,
   review/fix loop (maximum three), then `coding:commit` on success.
3. Give each landed slice to an independent adversarial verifier. Accept only
   when no verifier can refute its cited requirement/criterion.
4. Requeue refuted slices with evidence. Stop on a decision or iteration/token
   guard; never silently downgrade or continue stale work.

```yaml
verified_slices: []
pending_decisions:
  - {slice_id: '', spec_loc: '', question: '', options: [], rationale: ''}
commits_landed: [{sha: '', message: ''}]
child_dispatch_log: [{skill: '', status: pass|fail|partial, summary: ''}]
generated_files: []
departures: []
unresolved: []
```

On a pending decision, record the answer through `mdc`, update the work receipt
hash, and resume the same run so completed slices remain cached.

## Sequential mechanism

Run the selected chain from `modes.md` in the live session. Apply the same
decision stop, deviation reporting, three-pass review bound, and manifest
collection. Do not create root plan/deviation artifacts or write PM-owned
overview/state files.
