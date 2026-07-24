# Checkpoints, approval binding, and freshness

Read this when an emission event below occurs, when recording an approval, or
when authoring durable claims that can age.

## Durable checkpoints

A checkpoint is a compact receipt that makes a consequential event survive the
loss of `.engineering/`. Emit one after each of: an accepted decision, plan
approval, a parallel dispatch batch, an irreversible action, an artifact
approval, a handover, and pre-cleanup/retirement.

Checkpoints publish to the stream's **external anchor** — the owning task, PR,
or Notion work item — using the same publication path as the portable handover
receipt. They are not written under `docs/`. A stream's first checkpoint-worthy
event therefore requires an anchor: if none exists, establish one; if the user
declines, record `Durability: degraded (no anchor)` in `state.md` and continue
— the doctor reports it as a warning.

Format follows `templates/checkpoint.md`: event type, timestamp, actor
`capability_id`, `state_revision`, subject ids with exact revisions or hashes,
and a one-line consequence. Append one `checkpoint` journal line per emission.
Checkpoints are append-only at the anchor; never rewritten.

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
