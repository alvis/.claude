# Lazy work overviews

Read this when creating or reconciling `proposals.md`, `changes.md`,
`decisions.md`, or `design.md`. Create each overview with the first child in
its corresponding folder; once created, retain it until work closes. The
PM/coordinator alone reconciles these overviews; subagents may create or
update assigned children and return them in their output manifest.

## Proposals vs changes

`proposals/` and `changes/` both document a work stream's tasks and
implementation against the active canonical specification — the canonical
Notion spec for a Notion-backed contract, the source at its exact path for a
reachable `repo:` local contract (the derived carrier is only
content-equivalent, never the authority), or the durable carrier for a
`local-approved:` or `inline-approved:` contract. They differ by
**implementation state**, not by approval and not by being deviations. A
`proposals/` child is anything proposed but **not yet implemented**: most
often a task to implement the work stream (derived from the canonical spec —
for a Notion-backed contract, from the canonical Notion spec), but also a
bounded research finding, a decision proposal, or a specification-change
proposal awaiting reconciliation. When the work is done, its final
implementation documentation shifts to a `changes/` child, together with any
last-mile changes made during implementation. A `changes/` child therefore
also holds general implementation and explainer records, not only deviations.

Approval is a **status on the proposal, not a folder move**. A proposal is
`open` until the user approves it and `accepted` once approved, so downstream
planning can tell an approved proposal from an undecided one — but an
approved proposal that is not yet implemented stays in `proposals/`; only
implementation shifts it to `changes/`. A proposal never approved ends in
`proposals/` (`rejected` or `withdrawn`). Separately, the coordinator creates
or links the corresponding `changes/` child as implementation proceeds — that
child may be `pending` before it becomes `applied`. A `changes/` child links
back to its originating proposal **when one exists**; a direct change record
with no proposal (a review explainer, an implementation-time material
departure) is complete without that back-link. `state.md` carries the list of
proposals still awaiting user approval and those approved but pending
implementation, so a resume sees the outstanding work at a glance.

Each `proposals/` and `changes/` child SHOULD carry a section recording any
deviations from the canonical specification, if any — deviations are an
optional subsection, not what defines the folder.

## Overview shape and statuses

Each overview contains only:

1. Purpose and one headline summary.
2. Counts by canonical status.
3. A table with `status`, one-line `headline`, and relative child `path`.
4. `last_pm_reconciliation` as an ISO-8601 timestamp.

Do not copy child detail into an overview. `state.md` links to the overview,
not directly to the folder. `state/working.md` links only to the overview or
child needed for the current focus.

| Overview | Child statuses |
| --- | --- |
| `proposals.md` | `open`, `accepted`, `rejected`, `withdrawn` |
| `changes.md` | `pending`, `applied`, `reverted`, `superseded` |
| `decisions.md` | `proposed`, `accepted`, `rejected`, `superseded` |
| `design.md` | `draft`, `approved`, `implemented`, `promoted`, `superseded` |

Each child starts with structured metadata containing at least its canonical
status, one-line headline, owner, created timestamp, and source/provenance
references. A `decisions/` child additionally follows
[decision-causality.md](decision-causality.md): causal metadata
(`supersedes`/`affects`/`invalidates`/`preserves`), the blast-radius sweep on
acceptance, and the completion gate that dispositions every accepted decision
before retirement.

When a `proposals/` or `changes/` child's deviation section records a
deviation from a Notion-backed specification, that deviation's provenance
MUST link to the related `.mdc` file under the default source tree's
`.engineering/notion/` — that folder lives only on the default source tree
and is never copied into a secondary tree, so the link resolves there; a
Notion-backed spec deviation recorded without that link is incomplete. A
non-Notion contract has no such folder and cites its authoritative source
instead of inventing Notion provenance: a reachable `repo:` local source
keeps its exact source path authoritative and cites that path (the derived
carrier is only content-equivalent), while a `local-approved:` or
`inline-approved:` source cites its durable carrier as the sole authority.

If an overview itself ever requires splitting, reserve `00-index-<group>.md`
names inside its folder for index shards.
