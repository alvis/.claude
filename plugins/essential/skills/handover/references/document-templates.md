# Work-memory templates

Use the Essential engineering-work contract as authoritative. These shapes add
handover-specific content; all timestamps are one real UTC ISO-8601 value.

## `goal.md`

```markdown
# <Work headline> charter

- Work ID: `<work-id>`
- Charter revision: `<n>`
- Updated: `<timestamp>`
- State: [state.md](state.md)

## Goal
## Scope and non-goals

## Success criteria

| ID | Criterion | Acceptance evidence |
|---|---|---|
| `SC-1` | `<criterion>` | `<expected evidence>` |

## Specification provenance
```

The charter owns goal, scope, success criteria, and specification provenance;
`state.md` links to it and never restates them. For a Notion-backed contract,
record the source kind, page id, and the base-id/revision the charter was
authored against — the canonical specification stays the sole authority.
`Charter revision` bumps only on explicit user approval, journaled in
`state/journal.md` and `state/revisions.md`.

## `state.md`

```markdown
# <Work headline>

- Work ID: `<work-id>`
- Lifecycle status: `<initialized|active|blocked|complete|retiring>`
- Updated: `<timestamp>`
- Charter: [goal.md](goal.md)
- Current focus: [working.md](state/working.md)
- Journal: [journal.md](state/journal.md)
- Plan source: `state.md`
- Plan revision: `<n>`
- State revision: `<n>`
- External anchor: `<task|issue|PR|Notion URL>`

## Status

<Current lifecycle/task roll-up, owner, and exact next action.>

## Tasks

| ID | Mark | Status | Task | Depends on | Required | Acceptance | Owner | Evidence / next action |
|---|---|---|---|---|---|---|---|---|
| `LFE` | `⧗` | `working` | `<summary> [targets: none]` | `-` | `yes` | `<criterion>` | `<owner>` | `<evidence or action>` |
| `LFE01` | `✓` | `done` | `<summary> [targets: src/example.ts]` | `-` | `yes` | `<criterion>` | `<owner>` | `<evidence>` |

## Plan graph
## Current state and file status
## Approved decisions and accepted assumptions
## Outstanding proposals
## Dependencies, blockers, risks, and pivot signals
## Reviews and dispositions
## Evidence and validation
## Durable promotion
## Specification sync and revalidation
## Continuation
```

The root table contains the complete registry: every three-letter parent and
every `AAA01`-style child exactly once. A resumable `state/*.md` child may mirror
only its parent's existing subset and cannot introduce an ID. Store full IDs in
`Depends on`; parent edges target parents and child edges target siblings.
Every Task cell is exactly `<summary> [targets: <comma-separated paths>|none]`.
Marks and status words use `- planned`, `⧗ working`, `✓ done`, `X failed`,
`! blocked`, or `⊘ cancelled`. Graph notation and diagrams are derived display,
not authority.

`## Outstanding proposals` preserves the proposal inventory across the state
rewrite: every `proposals/` child still awaiting user approval and every approved
proposal not yet implemented, each with its status and child path, so a
same-machine resume reads the outstanding approval/implementation work from
`state.md` without scanning the folder. Omit the section only when no such
proposal exists.

File substates: completed; `need-draft`; `need-completion`; `need-fixing`;
`need-testing`; `need-linting`; `need-refactoring`; blocked. Record path,
substate, remaining action, evidence, and blocker. Use semantic `state/*.md`
children for genuinely resumable execution detail. Numeric split children are
reserved for a shared file that exceeded its size limit.

The `## Continuation` section persists, on disk, everything a resume needs to
route the next step: `Current task` (full executable task ID or
none), `Next owner` (exact continuation owner), `Next action` (one sentence), and
`Continuation intent` (a capability-level work-type descriptor — for example
`specification-led implementation` or `generic coding implementation` — never a
fixed skill name). A takeover reads these fields straight from `state.md`.

## `overview.md`

The default source tree's global cross-tree index: one table of every work stream
across every source tree (Git worktree or jj workspace) on the machine, so a
single read shows all outstanding work and where it lives. Handover upserts only
the rows whose `Location` is the current source tree and preserves every other row
byte-for-byte. Follow this template:

```markdown
# Engineering overview

- Updated: `<timestamp>`

| Work ID | Lifecycle | Headline | Next action | Location | Spec | Documentations |
|---|---|---|---|---|---|---|
| `<work-id>` | `<initialized\|active\|blocked\|complete\|retiring>` | `<one line>` | `<one line or ->` | `<source-tree path> (<git-worktree\|jj-workspace> @ <revision>)` | `<capability>` or `<capability> (pending-publication)` or `-` | `[<title>](docs/<slug>.md)` or `-` |
| `<work-id>` | `complete` | `<one line>` | `-` | `-` | `-` | `-` |
```

- `Location` is the source tree that currently holds the stream's
  `.engineering/works/<work-id>/`: its repository-relative or absolute path plus
  the tree kind and current revision. Use `-` when that source tree has been
  removed, so the stream is orphaned and no longer resumable.
- `Spec` names the capability or specification source the stream works against,
  suffixed `(pending-publication)` while the stream holds accepted spec
  deviations not yet pushed to the canonical source, or `-` for generic work.
  Before planning a new stream against a capability, resolve any sibling
  stream's pending publication on it first.
- `Documentations` links any durable `docs/` material for the stream — an
  architecture document, ADR index, or capability specification — or `-` when
  none exists.
- Every stream in a tree's own `.engineering/works/` appears as exactly one row,
  continuable and index-only alike. The overview is a status index only; each
  stream's authoritative resumable context stays in that stream's own
  `state.md`/`state/` files. A retired stream may be dropped once its row adds no
  signal.

## `state/working.md`

```markdown
# Current focus

- Updated: `<timestamp>`
- Status: `<one sentence>`
- Working now: `<one narrow outcome>`
- Handback point: `<exact next action or blocker>`

## Fast paths
- State: [state.md](../state.md)
- Spec: [<relative path>](<relative path>)
- Source/test: [<relative path>](<relative path>)
- Active decision/design/review/evidence: [<relative path>](<relative path>)
```

Aim at approximately 4,096 bytes by editing, not a gate. Never include the full
plan, history, completed inventory, copied spec, or review findings.

## Lazy work overviews

`proposals.md`, `changes.md`, `decisions.md`, and `design.md` are created with
their first child and then retained until work closes. Each contains purpose,
one headline, canonical status counts, last PM reconciliation timestamp, and a
table of child headline/status/relative path. Never copy child detail.
