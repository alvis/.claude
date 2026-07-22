# Handover examples

```bash
/essential:handover auth-refresh
# Refreshes .engineering/works/auth-refresh/state.md and state/working.md,
# reconciles existing lazy indexes, and emits a portable Markdown receipt.
```

```bash
/essential:handover
# Uses the active work ID from injected/current PM context; rejects ambiguity.
```

```bash
/essential:takeover <task-or-PR-containing-receipt>
# Checks out or applies the source anchor into a fresh workspace, writes each
# ## Work state file back to its work-relative path, stages any specification,
# then hands off to the relevant implementation skill to continue the work.
```

```bash
/essential:handover checkout-refunds
# If relevant changes exist only in the working copy, returns blocked until an
# approved remote revision or externally attached patch/bundle carries them.
```

Invalid work IDs, missing Essential contract paths, non-portable source anchors,
contradictory receipts, or a complete work item are explicit errors. A generic
coding receipt may omit a specification. There is no prefix-based or root-file
compatibility fallback.

The receipt's `Continuation intent` names the capability-level work type — for
example specification-led implementation versus generic coding implementation —
never a fixed skill name; takeover maps it to the relevant implementation skill
and rejects a missing or contradictory intent.

For a response-only handover, the receipt itself embeds the raw contents of every
`## Work state` file, the complete patch or bundle when that is the source
anchor, and any inline specification. For an externally published handover, the
source anchor and specifications may instead be a repository-relative path or a
stable attachment locator. A path such as
`.engineering/works/auth-refresh/state.md` or `/tmp/auth.patch` is never a
portable source anchor on its own.

For a Notion-backed specification, the receipt records the stable page ref and
captured revision so takeover fetches it fresh during rehydration. It never
records an origin-workspace path such as `/Users/alice/project/.engineering/`.
