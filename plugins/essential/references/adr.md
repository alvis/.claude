# Architecture decision records

Read this when creating, accepting, superseding, indexing, or reviewing an
architecture decision record (ADR). It is the contract for durable ADRs; work-
local `decisions/` children keep their separate lifecycle.

## Paths and authority

- Effective ADRs live directly under `docs/architecture/decisions/`.
- Archived ADRs live directly under `docs/architecture/decisions/superseded/`.
- ADR filenames use the zero-padded numeric prefix from `naming.md`; moving an
  ADR never renumbers it.
- `docs/architecture/README.md` is the index. It lists every effective ADR and
  no archived ADR.

The ADR explains why a choice was accepted. The architecture document explains
the current structure. Neither copies the other.

## Superseding an ADR

When a later ADR changes an accepted choice, whether partially or completely:

1. Create the new ADR as an effective record. It must stand on its own and must
   not mention the old ADR or explain what changed from it.
2. Move the old file to `decisions/superseded/` without changing its body.
3. Prepend this header to the moved file, filling every field and keeping the
   original body below it:

   ```markdown
   > **Status:** Superseded
   >
   > **Superseded by:** [ADR-<nnnn> — <title>](../<nnnn>-<slug>.md)
   >
   > **What changed:** <State whether the change is partial or complete and summarize the changed choice.>
   ```

4. Update `docs/architecture/README.md` so its ADR table contains only the
   effective ADRs directly under `decisions/`; remove the moved path.

Do not edit the old ADR into the new decision. The archive header is the only
permitted addition to its historical body.

## Reading history

Scan `decisions/superseded/` when the history is needed. If a current ADR is
known, inspect only archived files whose `Superseded by` header links to that
ADR. This keeps unrelated historical choices out of the current decision
context.

## Integrity contract

Every ADR filename uses a zero-padded numeric prefix that matches its first
visible canonical `# ADR-<nnnn>: <title>` heading. An effective ADR must not
contain supersession or explicit replacement/predecessor language, links into
`superseded/`, contradictory status declarations, or unresolved template
placeholders; ordinary Markdown autolinks and inline HTML are not placeholders.
An archived ADR must retain its original heading and substantive decision body
below the prepended header, not just status metadata. The header fields appear
in order with exactly one `Status: Superseded`, one successor, and one
change-summary field. Its successor link must target an existing effective ADR
with a later numeric identity, and its non-empty change summary must explicitly
state whether the change is partial or complete. The ADR index table must be a
valid Markdown table whose delimiter row has the same number of columns as its
header, include a `Status` column, and mark every effective ADR `Accepted`. The
doctor reports each violation with a proposed repair; the doctor skill always
offers the user an explicit, approved fix during investigation.
