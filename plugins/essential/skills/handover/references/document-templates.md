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
route the next step without a receipt: `Current task` (full executable task ID or
none), `Next owner` (exact continuation owner), `Next action` (one sentence), and
`Continuation intent` (a capability-level work-type descriptor — for example
`specification-led implementation` or `generic coding implementation` — never a
fixed skill name). A same-machine takeover reads these fields straight from
`state.md`; the receipt's per-stream `### Continuation` carries the same four
fields.

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
  removed, so the stream is orphaned and resumable only from a receipt (or no
  longer resumable at all).
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

## Handover receipt

The receipt is plain Markdown a human can paste. It is an **index over the
persisted work directories, not a carrier of their contents** — no work-file
bodies, no specification bodies, no artifact bytes, no patches, no JSON
snapshot, no base64, no checksums, no schema version line. Its size tracks the
number of streams, never the size of the work, so it always fits a task
comment, a PR description, or a chat response. It is never written to a file.

It describes the **current source tree's** `.engineering/works/` streams (this
Git worktree or jj workspace only — never another tree's works): a
`## Work index` row for **every** work stream in this tree, then a
`## Transfer` section covering each **selected continuable** stream (lifecycle
`initialized`, `active`, or `blocked`). `complete` and `retiring` streams appear
as index rows only; they are not an error. The receipt contains, in order:

````markdown
## Handover receipt

- Repository: <stable remote/name identity>
- Source tree: <kind (Git worktree or jj workspace) and label of the current tree>
- Generated: <one UTC ISO-8601 timestamp>
- Streams: <N> indexed / <M> selected
- External anchor: <URL or response-only>

## Work index

| Work ID | Lifecycle | Headline | Next owner | Next action | Intent | Anchor | Rev |
|---|---|---|---|---|---|---|---|
| `<work-id>` | `active` | `<one line>` | `<owner>` | `<one line>` | `<intent>` | `<anchor label>` | `<n>` |
| `<work-id>` | `blocked` | `<one line>` | `<owner>` | `<one line>` | `<intent>` | `<anchor label>` | `<n>` |
| `<work-id>` | `complete` | `<one line>` | `-` | `-` | `-` | `-` | `<n>` |

## Transfer

To resume any stream below on this machine, run `essential:takeover` in the
source tree named above — the state is already on disk. To resume elsewhere,
copy that stream's work directory to the destination tree's `.engineering/works/`,
bring the destination checkout to the stream's anchor, then run
`essential:takeover` there.

### <work-id>

- Work directory: `<absolute path to .engineering/works/<work-id>>`
- Source anchor: `<remote/ref @ revision>` | patch at `artifacts/<name>.patch`
  (base `<base commit>`) | bundle at `artifacts/<name>.bundle`, ref `<ref>`,
  base `<base commit>` | none — local-only changes: `<summary>`
- Specification: `<repository-relative path>` | Notion `<stable ref>` @
  `<captured revision>`, merge base `<revision>` | none
- Lease at handover: `<released | expired (owner <capability_id>)>`
- Continuation: task `<id or none>` — `<next owner>` to `<next action>`

### <next selected work-id>

<... repeated entry per selected stream ...>
````

The `## Work index` is the synthesized view of the current source tree's streams;
the cross-tree index lives separately in the default tree's
`.engineering/overview.md`, not in this receipt. List every `works/<work-id>/`
stream in this source tree once, ordered by lifecycle then work ID, with its
current lifecycle, one-line headline, next owner, next action, capability-level
continuation intent, a short anchor label that lets a resume group streams
sharing one revision, and its `State revision`.

`## Transfer` names, per selected stream, the absolute work directory that holds
its state. That directory is the carrier: copying it moves `goal.md`, `state.md`,
`state/` children, decisions, changes, design, proposals, the materialized
specification, and `artifacts/` together, with no reassembly step and nothing to
write back. Never inline a file's contents here — a pathname is exactly the
right answer, because the recipient copies the directory rather than
reconstructing it. Redact secrets from the headline, path, and anchor label; the
carried files themselves are handled by the destination's own ignore rules.

Each stream's source anchor tells the destination how to reach that stream's
*code*, which the work directory does not carry. Use a destination-reachable
remote revision when one exists; otherwise a user-approved `git format-patch`
patch or `git bundle` written under that stream's `artifacts/`, so it travels
with the directory. A dirty workspace path, a local-only revision, or a command
string is not an anchor — record `none` with a summary of the local-only changes
instead. Normalize and contain every repository and destination path; reject
absolute paths, `..`, and symlink escapes.

Specifications are optional and per stream, and appear as **provenance only**:
the materialized copy already travels inside the work directory. Record a
repository-relative path present in the anchored tree, or a Notion stable ref
with its captured revision so a resume can fetch it fresh. For a Notion-backed
spec, also record the immutable merge base (last synced revision) so a resumed
publication can three-way merge against concurrent remote edits rather than
overwrite them. If a stream's live specification source is unreachable at
handover time, mark the provenance stale and note it. Generic coding work omits
the line.

`Continuation intent` is a required per-stream capability-level descriptor of the
work type to continue — for example `specification-led implementation` when a
spec governs the next action, or `generic coding implementation` when none does.
It names the kind of work, never a fixed skill name; takeover maps it to the
relevant implementation skill. Emit it consistently with `Next action` so the
two agree.
