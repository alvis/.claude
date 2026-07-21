# Engineering work-state contract

Use this contract for every new or coordinator-migrated `state.md` and every
resumable `state/*.md` child. Essential owns the schema and validator; domain
skills own task definitions and evidence.

## Schemas and authority

- On-disk Markdown uses `engineering-work-state/v1`.
- Portable snapshots use `engineering-work-state+json/v1`.
- Plan approval uses `engineering-plan-definition-digest-v1`.
- Root `state.md` is the complete execution registry. Its `## Tasks` table
  contains every parent and numbered subtask in the work item, even when a
  `state/*.md` child mirrors a subset for detailed resumption.
- A child state declares `State role: child` and `Parent task: ABC`. It cannot
  introduce an ID absent from the root registry. The coordinator reconciles
  its mutable fields with the root before validation, dispatch, or handover.
- New v1 root state uses `Plan source: state.md`: the complete root task
  registry is the approved definition source and consumers never guess among
  planning files. `state/plan.md` may hold ID-keyed semantic
  detail, but it is non-authoritative and cannot introduce or redefine tasks.
- Legacy state without `Schema` is `migration_required`. Preserve it
  byte-for-byte until the coordinator performs an explicit migration; neither
  the resolver nor validator rewrites it.

Root state metadata contains at least:

```markdown
- Schema: `engineering-work-state/v1`
- State role: `root`
- Work ID: `eng-421-example`
- Lifecycle status: `active`
- Plan source: `state.md`
- Plan digest: `<64 lowercase hexadecimal characters>`
- Hash kind: `engineering-plan-definition-digest-v1`
```

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

## DAG and roll-up semantics

`Depends on` is the authoritative graph. A chain is a linear DAG; use a
branching DAG only when dependencies justify it. Display the overall graph as
`LFE → {API,DOC} → VAL` and a local child graph as
`LFE01 → {LFE02,LFE03} → LFE04` when that compact notation is exact.
Inside the parent section, `01 → {02,03} → 04` is an optional derived
shorthand. Generated graph text or Mermaid never enters the approval digest.

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
that carries `task_id`, `plan_digest`, attempt outcome, and evidence.
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

## Plan definition digest

Compute the plan digest over canonical JSON containing sorted tasks with:

- full task ID;
- summary and targets parsed from the canonical `Task` cell;
- sorted `depends_on` IDs;
- requiredness; and
- acceptance mapping.

Exclude mark, runtime status, owner, evidence/next action, timestamps, layout,
and derived diagrams. Therefore progress updates preserve approval, while a
change to identity, definition, target, dependency, requiredness, or acceptance
changes the digest and requires reapproval. A validator run with
`--previous-state` against the last accepted state reports the affected
downstream closure and enforces permanent ID history: retain removed work as an
optional cancelled tombstone rather than deleting its row.

## Validation and portable snapshots

Resolve the Essential root, then validate before dispatch, review, handover,
takeover completion, cleanup, or retirement:

```bash
"$ESSENTIAL_ROOT/bin/validate-engineering-state" validate \
  --state "$work_dir/state.md"
```

The dependency-free validator emits one JSON report with `status`, schema,
work/lifecycle identity, plan source, stored and computed digests, hash kind,
parent and child graphs, topology, status counts, runnable leaf IDs, blocked
leaf IDs, active/failed IDs, the complete execution ledger, exact next owner
and next action, invalidated downstream closure, and errors. Root validation
automatically reconciles every file directly under `state/` that explicitly
declares `engineering-work-state/v1` or `State role: child`. It leaves unmarked
semantic narrative such as `state/plan.md` alone. Directly
validating an unversioned file still returns `migration_required`. Declared
mirrors validate against the complete root registry. Exit codes are 0 for
`valid`, 2 for `invalid`, and 3 for `migration_required`.

Portable transport uses the same parser:

```bash
"$ESSENTIAL_ROOT/bin/validate-engineering-state" pack \
  --state "$work_dir/state.md" >state.json
"$ESSENTIAL_ROOT/bin/validate-engineering-state" validate-snapshot \
  --snapshot state.json
"$ESSENTIAL_ROOT/bin/validate-engineering-state" render \
  --snapshot state.json >state.md
```

`pack` refuses invalid state and serializes the complete root registry as
canonical `engineering-work-state+json/v1`. Accepted snapshot bytes are exactly
sorted compact canonical JSON followed by one LF. Snapshot parsing rejects
duplicate JSON keys, control characters, noncanonical task/dependency/target
ordering, unknown/missing keys, malformed task values, digest, graph, topology,
or execution-ledger drift, and contradictory roll-ups. `render` emits canonical Markdown only after the
snapshot validates. It preserves IDs, definitions, edges, mutable statuses,
owners, evidence/next actions, plan identity, and continuation owner/action;
domain narrative remains in separately transported specification/evidence
artifacts rather than being inferred by the renderer.
