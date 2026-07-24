# Engineering work-state contract

Use this convention for every new or coordinator-migrated `state.md` and every
resumable `state/*.md` child. A work item is free-form, LLM-readable Markdown:
nothing is machine-validated and any layout a reader can follow works. This
document describes the shared shape that keeps state files easy to resume from;
Essential owns the convention, domain skills own task definitions and evidence.

## Roles and authority

- Root `state.md` is the complete execution registry. Its `## Tasks` table
  contains every parent and numbered subtask in the work item, even when a
  `state/*.md` child mirrors a subset for detailed resumption.
- A child state declares `State role: child` and `Parent task: ABC`. It cannot
  introduce an ID absent from the root registry. The coordinator reconciles
  its mutable fields with the root before dispatch or handover.
- Root state uses `Plan source: state.md`: the complete root task registry is
  the approved definition source and consumers never guess among planning
  files. `state/plan.md` may hold ID-keyed semantic detail, but it is
  non-authoritative and cannot introduce or redefine tasks.
- There is no required header token. Preserve any existing state file
  byte-for-byte until the coordinator performs an explicit rewrite; the resolver
  never rewrites it.

Root state metadata contains at least:

```markdown
- State role: `root`
- Work ID: `eng-421-example`
- Lifecycle status: `active`
- Charter: [goal.md](goal.md)
- Plan source: `state.md`
- Plan revision: `3`
- State revision: `41`
- Written under: `a1b2c3d4`
```

The charter pointer names the work's `goal.md`, which owns the goal, scope,
numbered success criteria, and specification provenance; the root state never
restates them. `Plan revision` counts approved definition changes, starting at
`1`. `State revision` is a monotonic counter bumped on every coordinator write
of `state.md` (progress and definition alike), starting at `1`; it orders
journal lines and lets the lease and doctor detect a stale writer.
`Written under` records the short hash of the engineering-work contract this
file was bootstrapped or last coordinator-rewritten against — provenance
only, stamped by the resolver and rewrites; it confers no authority (the
current contracts always judge) but lets the doctor report drift as "written
under X, current is Y" and order migrations by staleness. All three fields
apply to new and coordinator-rewritten files only — an older file gains them
at its next explicit rewrite under the lazy-migration rule, never on read.

Keep lifecycle status (`initialized|active|blocked|complete|retiring`), task
status, attempt outcome (`pass|fail|partial`), file state, review state, and
sync state in separately named fields. Never reuse one vocabulary for another.

## Task identity and tables

Every state file has `## Status` and `## Tasks`. The root table uses exactly
these first nine columns:

```markdown
| ID | Mark | Status | Task | Depends on | Required | Acceptance | Owner | Evidence / next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

The `Task` cell is an immutable definition with the exact grammar
`<summary> [targets: <comma-separated targets>|none]`. Targets may be source
paths, artifact paths, or named external surfaces. Escape a literal Markdown
pipe as `\|`. Use `—` for no dependency and `yes|no` for `Required`.

- Give every top-level task one mnemonic ID matching `^[A-Z]{3}$`.
- Give every subtask its parent ID plus `01` through `99`, for example `LFE01`.
- Permit only that one child level. Promote deeper work to another parent.
- Assign IDs before approval. Never rename, recycle, or reuse an ID.
- Retain every assigned ID as history. Removed scope becomes an optional
  `cancelled` tombstone; never delete its row from a later plan revision.
- Treat a parent with children as a derived roll-up, not executable work. A
  parent with no children is an executable leaf.
- Store full IDs in `Depends on`. Parent dependencies reference parents;
  subtask dependencies reference siblings under the same parent. Prohibit
  cross-parent partial dependencies; promote that boundary to a parent.
- Treat row order and diagrams as presentation only.

Use these exact mark/status pairs:

| Mark | Status | Meaning |
| --- | --- | --- |
| `-` | `planned` | Definition is approved but execution has not started. |
| `⧗` | `working` | An owner is actively executing it. |
| `✓` | `done` | Acceptance is met and evidence is recorded. |
| `X` | `failed` | An attempt failed and has a retry or disposition. |
| `!` | `blocked` | Work cannot advance and has an owner/unblock action. |
| `⊘` | `cancelled` | An approved plan revision removed optional scope. |

Record `attempt:` plus either `retry:` or `disposition:` for failed work.
Record `unblock:` for blocked work. Required work cannot remain cancelled;
revise and reapprove the definition so it is optional or absent.

Validity is orthogonal to status (see Essential's `truth.md`). Mark/status
pairs are history and are never falsified; `✓ done` is terminal. When later
truth invalidates a done row's result, append
`validity: stale (<reason or superseding id>)` — or `validity: unknown (…)`
when unverified — to its Evidence cell and add remediation tasks with new IDs.
An unmarked row is `current`.

## DAG and roll-up semantics

`Depends on` is the authoritative graph. A chain is a linear DAG; use a
branching DAG only when dependencies justify it. Display the overall graph as
`LFE → {API,DOC} → VAL` and a local child graph as
`LFE01 → {LFE02,LFE03} → LFE04` when that compact notation is exact.
Inside the parent section, `01 → {02,03} → 04` is an optional derived
shorthand. Generated graph text or Mermaid is presentation only and never
redefines the task registry.

Derive a parent with children as follows:

- `planned`: all considered children are planned.
- `working`: a child is working, or completed child work leaves runnable work.
- `done`: every required child is done; when a parent has only optional
  children, every child is terminal and at least one is done.
- `failed`: an unresolved required child failed.
- `blocked`: required work remains but no child is running or runnable.
- `cancelled`: all considered optional children were removed by an approved
  plan revision.

A failed leaf blocks only its downstream closure. Independent siblings remain
runnable. The coordinator alone changes task status after reconciling a result
that carries `task_id`, attempt outcome, and evidence.
Any dependency edge that still names a cancelled predecessor is also blocked;
an approved plan revision must remove that obsolete edge before execution.
Reconcile a planned leaf downstream of any failed, blocked, or cancelled
predecessor to explicit `! blocked` with `unblock:` evidence. Leave ordinary
future work `planned` while it waits only on planned or working predecessors.
An executable task may become `working`, `done`, or `failed` only after every
own dependency and every predecessor of its parent is `done`; a task that
cannot be attempted is `blocked`, never `failed`. Lifecycle `blocked` is
invalid while any required executable leaf is still `working`.

Lifecycle `complete` requires every required executable leaf to be `done`.
Lifecycle `blocked` requires unfinished required work and no runnable required
leaf. Passing tests alone does not make a lifecycle complete while review,
sync, publication, or history anchoring remains required.

## Reading state and definition changes

There is no separate validation step: before dispatch, review, handover,
takeover, cleanup, or retirement, read `state.md` (and `state/*.md` children)
directly and proceed on that reading. The plan definition is the root task
registry itself — IDs, `Task` summaries and targets, `Depends on` edges,
requiredness, acceptance. A "definition changed" check is simply re-reading
the file: a definition change takes effect the moment it is written and
downstream reconciliation follows the DAG rules above, while progress updates
(mark, runtime status, owner, evidence) never change the definition.

## Change control during execution

Plans change during execution; that is the normal path, not an exception.
When a mid-execution finding may change how, what, or why work is executed,
follow the journal → classify (task-local / plan-level / spec-level) →
resume procedure in Essential's [change-control.md](change-control.md).

`state/journal.md` is append-only: one line per status transition, decision,
plan or charter revision, sync event, sweep, checkpoint, or lease event —
`- <ISO-8601> <actor>@<capability_id> rev:<N> <event-type> <subject>: <transition or summary> [evidence: <ref>] [invalidates: <ids>]` —
newest last, never rewritten or deleted. `<event-type>` is one of
`status|decision|revision|sync|sweep|checkpoint|lease`; `rev:<N>` is the
`State revision` the writer was at; `invalidates:` names outputs or evidence
the event made stale. Older lines in the pre-grammar form
(`- <ISO-8601> <actor> <task-id or event>: <summary>`) remain valid history.
`state/revisions.md` is the same discipline at plan granularity: one entry per
approved revision. Neither file is ever the plan authority; both make the
authoritative tables auditable and reconstructible.

## Portable handover

Ignored work memory is not a cross-machine transport. To move a work item,
a handover emits a plain-Markdown receipt — a destination-reachable source
anchor plus the raw contents of every continuity-relevant work file — and a
takeover writes each file back to its work-relative path verbatim. There
are no snapshot bytes, checksums, or machine render step; the reader
judges completeness directly. The receipt shape (including per-stream
`State revision`, lease status, and checkpoint pointers) is defined in the
handover skill's document templates.
