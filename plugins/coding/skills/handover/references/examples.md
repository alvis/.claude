# Handover examples

```bash
/coding:handover auth-refresh
# Refreshes .engineering/work/auth-refresh/state.md and working.md,
# reconciles existing lazy indexes, and emits a portable receipt.
```

```bash
/coding:handover
# Uses the active work ID from injected/current PM context; rejects ambiguity.
```

```bash
/coding:takeover <task-or-PR-containing-receipt> --revalidate
# Rehydrates a new workspace from repository and Notion truth, then resumes.
```

Invalid work IDs, missing Essential contract paths, absent authoritative spec
identity, contradictory receipts, or a complete work item are explicit errors.
There is no prefix-based or root-file compatibility fallback.
