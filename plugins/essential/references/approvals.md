# Approval binding and freshness

Read this when recording an approval or authoring durable claims that can
age.

## Approval binding

An approval is real only when it names all of: the artifact id; its content
hash or immutable revision (commit SHA, spec base-id, render revision and
timecode range); the reviewer (`capability_id` or user) and their authority;
the scope approved; and any unresolved exceptions. Anything less is an
opinion, not an approval. An approval of one revision never carries to a
successor revision merely because the successor was derived from it.

Record approvals where they belong and at once: the decision, review, or
change child that carries the approved thing, with one journal line per the
work-state contract — approvals are state changes and follow the same
append-first discipline as every other state change.

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
