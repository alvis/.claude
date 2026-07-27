# Promotion, parking, and retirement

Read this when promoting durable knowledge, parking an idle stream, or
retiring a completed one.

## Promotion

Promotion is auditable after retirement deletes the work stream: every
promoted `docs/` file carries front matter naming its `source-work` (the work
ID), promotion date, and any superseded document, and work closure requires a
promotion receipt in the stream's final `changes/` child listing every
promoted path. Only stable knowledge is promoted — never transient task
state. Durable docs that can age may carry the freshness metadata in
[approvals.md](approvals.md).

## Parking idle streams

Live streams are not free: the journal grows, `state.md` accumulates rows,
and every session re-reads them. A stream idle long past its last journal
entry — abandoned rather than paused — may be **parked**: move its entire
`works/<work-id>/` directory to `.state/archive/<work-id>/`, which the
resolver never enumerates, and drop or annotate its `overview.md` row. Both
paths are under the default source tree's `.state/` — the only tree that
carries one — so parking is a move within one directory, never across trees. Park
only with user approval, journal the parking as the final line first, and
never park a stream holding an unresolved critical risk or an unpublished
accepted decision — resolve, promote, or hand over those first. Unparking
is a plain move back. A summary journal line may also compact history: it
may summarize and supersede the journal lines before it, keeping live
streams readable without losing the record (the superseded lines remain,
marked by the summary above them).

## Retirement

Retire completed local work only after acceptance, review closure, durable
promotion, Notion push and verification pull, final receipts, and every accepted
decision's disposition under the completion gate
([decision-causality.md](decision-causality.md)) are recorded — retirement
deletes the operational projection, so nothing consequential may exist only
there. The default retention is 30 days unless repository compliance policy
requires longer. Existing ambiguous artifacts are reported and preserved,
never deleted or migrated by guesswork.

Retirement always records the retired work ID, and the date it was retired,
in `docs/retired-work-ids.md`, one record per line as `<work-id> <date>`. This happens even where the stream had
nothing else worth promoting — code-only work leaves no durable document to
carry its name, and without the ledger entry the ID vanishes from `works/`,
`archive/`, and `docs/` alike, so a later stream can reclaim an identity that
old pull requests and `source-work` references still point at. The entry is
committed before the deletion it stands in for: a record still loose in the
working tree does not outlive the state it replaced.
