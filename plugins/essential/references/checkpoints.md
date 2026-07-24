# Checkpoints, approval binding, and freshness

Read this when a checkpoint-worthy event occurs, when recording an approval,
or when authoring durable claims that can age.

## Durable checkpoints

A checkpoint is a compact receipt that makes a consequential event survive
the loss of `.engineering/` — which is ignored working memory, one reflexive
`git clean -fdx` away from silent deletion. Checkpoint-worthy events: an
accepted decision, plan approval, a parallel dispatch batch, an irreversible
action, an artifact approval, a handover, and pre-cleanup/retirement.

Checkpoints publish to the stream's **external anchor** — the owning task,
PR, or Notion work item — using the same publication path as the portable
handover receipt; they are not written under `docs/`. A stream must
establish its anchor and first checkpoint **before it carries any
non-recoverable decision**; if the user declines an anchor, record
`Durability: degraded (no anchor)` in `state.md` and continue — the doctor
reports it as a warning.

**Coalesce to stay legible.** A steady drip of receipt comments trains
humans to mute the anchor, which erodes the durability value. Emit at most
one checkpoint per anchor per session unless ownership changes hands —
handover, takeover, and retirement always emit immediately. Between those,
accumulate checkpoint-worthy events and publish them as one batched
session-end checkpoint (one block listing each event since the last
checkpoint). Durability is preserved; anchor noise is not.

Format follows `templates/checkpoint.md`: event type, timestamp, actor
`capability_id`, `state_revision`, subject ids with exact revisions or
hashes, and a one-line consequence — one block per event, batched blocks
under one anchor comment. Append one `checkpoint` journal line per emission.
Checkpoints are append-only at the anchor and never rewritten. In the
journal, a `checkpoint` line may also **compact history**: it may summarize
and supersede the journal lines before it, keeping a long-running stream's
journal readable without losing the record.

## Approval binding

An approval is real only when it names all of: the artifact id; its content
hash or immutable revision (commit SHA, spec base-id, render revision and
timecode range); the reviewer (`capability_id` or user) and their authority;
the scope approved; and any unresolved exceptions. Anything less is an
opinion, not an approval. An approval of one revision never carries to a
successor revision merely because the successor was derived from it.

## Freshness

A file comparison answers "did the file change?"; freshness answers "did the
claim go stale while the file stayed identical?" Durable docs and externally
sourced claims (research, market facts, platform rules, third-party APIs,
licensing) may carry front matter:

```yaml
last_verified: <ISO-8601 date>
revalidate_on:
  - <named trigger, e.g. delivery-date-changed>
```

When a named trigger fires or `last_verified` is older than the claim's risk
tolerates, re-verify before relying on it — the same discipline agent memory
already applies (`templates/memory.md`).
