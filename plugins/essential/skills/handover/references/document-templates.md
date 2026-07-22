# Work-memory templates

Use the Essential engineering-work contract as authoritative. These shapes add
handover-specific content; all timestamps are one real UTC ISO-8601 value.

## `state.md`

```markdown
# <Work headline>

- Work ID: `<work-id>`
- Lifecycle status: `<initialized|active|blocked|complete|retiring>`
- Updated: `<timestamp>`
- Current focus: [working.md](state/working.md)
- External anchor: `<task|issue|PR|Notion URL>`

## Status

<Current lifecycle/task roll-up, owner, and exact next action.>

## Tasks

| ID | Mark | Status | Task | Depends on | Required | Acceptance | Owner | Evidence / next action |
|---|---|---|---|---|---|---|---|---|
| `LFE` | `⧗` | `working` | `<summary> [targets: none]` | `-` | `yes` | `<criterion>` | `<owner>` | `<evidence or action>` |
| `LFE01` | `✓` | `done` | `<summary> [targets: src/example.ts]` | `-` | `yes` | `<criterion>` | `<owner>` | `<evidence>` |

## Goal and success criteria
## Plan graph
## Current state and file status
## Approved decisions and accepted assumptions
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

The default source tree's global cross-tree index. One `## <source-tree label>`
section per source tree, each with an identity block and a work-stream table.
Upsert only the current tree's section at handover and preserve the others
byte-for-byte:

```markdown
# Engineering overview

- Updated: `<timestamp>`

## <source-tree label or path>

- Kind: `<git-worktree|jj-workspace>`
- Path: `<repository-relative or absolute source-tree path>`
- Revision: `<current branch/bookmark @ short revision>`

| Work ID | Lifecycle | Headline | Next action |
|---|---|---|---|
| `<work-id>` | `<initialized|active|blocked|complete|retiring>` | `<one line>` | `<one line or ->` |

## <another source tree>

<... one section per source tree; secondary trees are never edited here ...>
```

Every stream in a tree's own `.engineering/works/` appears in that tree's table,
continuable and index-only alike. The overview is a status index only; each
stream's authoritative resumable context stays in that stream's own
`state.md`/`state/` files. A tree with no active streams may keep an empty table
or be omitted once retired.

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

## Portable receipt

The receipt is plain Markdown a human can paste. It carries no JSON snapshot, no
base64 bundle, no checksums, and no schema version line. It describes the
**current source tree's** `.engineering/works/` streams (this Git worktree or jj
workspace only — never another tree's works): a `## Work index` row for **every**
work stream in this tree, then an embedded `## Work stream: <work-id>` section
only for each **continuable** stream (lifecycle `initialized`, `active`, or
`blocked`). `complete` and `retiring` streams appear as index rows only; they are
not an error. The receipt contains, in order:

`````markdown
## Handover receipt

- Repository: <stable remote/name identity>
- Source tree: <kind (Git worktree or jj workspace) and label of the current tree>
- Generated: <one UTC ISO-8601 timestamp>
- Streams: <N> embedded / <M> index-only
- External anchor: <URL or response-only>

## Work index

| Work ID | Lifecycle | Headline | Next owner | Next action | Source anchor | Embedded? |
|---|---|---|---|---|---|---|
| `<work-id>` | `active` | `<one line>` | `<owner>` | `<one line>` | `<anchor label>` | `yes` |
| `<work-id>` | `blocked` | `<one line>` | `<owner>` | `<one line>` | `<anchor label>` | `yes` |
| `<work-id>` | `complete` | `<one line>` | `-` | `-` | `<anchor label or none>` | `no` |

## Work stream: <work-id>

### Source anchor

<How to obtain this stream's code at the right revision, with plain git and no
checksum verification — exactly one of:>
- Remote revision to check out: `<remote/ref @ revision>`
- Attached patch: `git format-patch` output, inline below or at <attachment locator>
- Bundle ref: `git bundle` at <attachment locator>, ref `<ref>`, base `<base commit>`

### Work state

<The raw contents of this stream's state.md, state/working.md, and every
continuity-relevant detail file — decisions, changes, design, state/*.md
children, needed evidence — each in its own fenced block. On the line
immediately before each opening fence, name the work-relative path as
`path: <work-id>/<relative path>`. Fence each file with a backtick run at least
one longer than the longest backtick run inside that file (minimum three); the
closing fence uses the same length. This lets a state file that itself contains
a fenced block travel without closing early:>

path: <work-id>/state.md

````markdown
<verbatim contents, may itself contain ``` fences>
````

path: <work-id>/state/working.md

```markdown
<verbatim contents>
```

path: <work-id>/decisions/<slug>.md

```markdown
<verbatim contents>
```

### Specifications

<Any spec contract needed to continue this stream. Embed the captured
specification content inline as the authority of record, then record its
provenance — a repository-relative path in the anchored tree, or a Notion stable
ref with its captured revision — so takeover can confirm a resumed spec matches
by direct comparison and refresh a live source. For a Notion-backed spec that a
resume must be able to re-publish, also record the immutable merge base (the last
synced revision the local content diverged from) so takeover can three-way merge
instead of clobbering concurrent remote edits. Omit this section for generic
coding work with no specification.>

### Continuation

- Current task: <full executable task ID or none>
- Next owner: <exact continuation owner>
- Next action: <one sentence>
- Continuation intent: <capability-level work type — e.g. specification-led implementation or generic coding implementation — never a fixed skill name>
- Route: hand off to the relevant implementation skill to continue the work.

## Work stream: <next continuable work-id>

<... repeated section per continuable stream ...>
`````

The `## Work index` is the synthesized view of the current source tree's streams;
the cross-tree index lives separately in the default tree's
`.engineering/overview.md`, not in this receipt. List every `works/<work-id>/`
stream in this source tree once, ordered by lifecycle then work ID, with its
current lifecycle, one-line headline, next owner, next action, a short
`Source anchor` label that lets takeover group streams sharing one revision, and
`Embedded?` (`yes` for continuable streams carried in full below, `no` for
`complete`/`retiring` index-only rows).

Emit one `## Work stream: <work-id>` section per continuable stream. Each
`### Work state` block is the verbatim content of one work file, labelled with
its `path: <work-id>/…` line so takeover can write it straight back. Include
every file needed to continue that stream without the origin `.engineering/`
tree; do not summarize, elide, or replace a file's content with a pathname. Do
not embed the whole `evidence/` tree, but when a stream needs specific evidence
to continue, carry those exact bytes — inline in a labelled fenced block or by a
durable external attachment locator — because a bare `evidence/…` path is not
reachable from the destination. Redact secrets, credentials, private keys, and
environment values from every embedded block; if redaction would leave one
stream's required section incomplete, degrade that stream to an index-only row
and note it, rather than blocking the whole receipt.

Each stream's source anchor must carry that stream's relevant repository changes
as one of the three plain-git shapes above. A dirty workspace path, a local-only
revision, or a command string is not an anchor. Normalize and contain every
repository and destination path; reject absolute paths, `..`, and symlink
escapes.

Specifications are optional and per stream. Embed the captured specification
content inline as the authority of record, and record where it came from: a
repository-relative path present in the anchored tree, or a Notion stable ref
with its captured revision so takeover can fetch it fresh. For a Notion-backed
spec, also carry the immutable merge base (last synced revision) so a resumed
publication can three-way merge against concurrent remote edits rather than
overwrite them; the local Notion mirror bases are ignored state and never travel,
so the base revision must be named explicitly in the receipt. If a stream's live
specification source is unreachable at handover time, keep the captured content
inline, mark the provenance as stale, and degrade only that stream. Generic
coding work omits the section.

`Continuation intent` is a required per-stream capability-level descriptor of the
work type to continue — for example `specification-led implementation` when a
spec governs the next action, or `generic coding implementation` when none does.
It names the kind of work, never a fixed skill name; takeover maps it to the
relevant implementation skill. Emit it consistently with `Next action` so the
two agree.
