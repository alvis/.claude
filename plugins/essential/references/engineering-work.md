# Engineering work lifecycle

Read this contract before creating or materially rewriting project engineering
artifacts. It defines their paths, ownership, promotion, and final size check.
Domain skills own artifact content; Essential owns this cross-plugin lifecycle.
All lead-role agents must read [truth.md](truth.md) once before working on
any project: it defines the kinds of truth these artifacts carry, the
constitutional rules, validity, and `capability_id`.
Per-moment detail lives in the references named below; read each when its
moment arrives, not before.

## Resolve the workspace first

The injected instruction gives the absolute path to this file. Derive the
Essential plugin root from that path, then run the resolver from inside the
target repository:

```bash
ENGINEERING_WORK_REFERENCE='<absolute engineering-work.md path injected by Essential>'
ESSENTIAL_ROOT="$(cd "$(dirname "$ENGINEERING_WORK_REFERENCE")/.." && pwd)"
"$ESSENTIAL_ROOT/bin/resolve-engineering-workspace"
```

A normal invocation is read-only; `--bootstrap` is the explicit PM-only
creation mode below. The resolver chooses identity in this order: explicit
`--work-id`, `ENGINEERING_WORK_ID`, a work directory matching the Git
branch/jj workspace label, then a sole existing workspace-local work
directory only when the workspace label is generic or unavailable. Branch and
workspace names may identify existing work but never create a new identity;
`work_id_source` records the choice. On `work_id_required`, no work path is
selected — the PM asks the user, a worker reports the ambiguity, and nobody
guesses through candidates, a detached checkout, or a generic `main`,
`master`, `trunk`, or `default` label. The resolver's `--help` enumerates
every output field; the essentials:

- `durable_root` is the active workspace root for versioned project documents
  and `.gitignore` (`repo_root` is its alias); it follows the tree the caller
  is working in, and is where `docs/` promotion lands.
- `state_root` is the **default source tree** — Git's main worktree or the jj
  workspace registered as `default` — the one tree carrying the ignored
  `.state/`, falling back to `active_workspace` when none is
  discoverable. `work_dir` is always
  `state_root/.state/works/<work-id>/`, whichever tree the caller is in.
- Work state is centralized, never per-tree, and never committed: every tree
  reads and writes the same `.state/`. Two trees must not run the same
  stream concurrently — that is what the coordinator lease enforces.

`resolved` with `engineering_ignored: true` is a hard bootstrap gate before
any work artifact or probe is written. On `requires_ignore`, every worker
stops and reports the returned `ignore_file` — the **default source tree's**
`.gitignore`, the tree that carries `.state/`. The PM alone adds the
exact `.state/` rule there, includes that path in `generated_files`, and
reruns the resolver. A sync-only or ad hoc `git check-ignore` probe does not
replace this bootstrap contract.

### First-use work-memory bootstrap

Once the user has confirmed a new work identity and the resolver returns
`resolved` with `engineering_ignored: true`, the PM alone — while holding
the coordinator lease — reruns the resolver with that confirmed ID and
`--bootstrap`, before delegating or creating any other work artifact.
`--bootstrap` never derives or mints an ID and cannot bypass
`work_id_required` or `requires_ignore`. [lease.md](lease.md) carries the
invocation, the no-clobber creation semantics, what the initial files hold,
and the `bootstrap_created` and `bootstrap_existing` paths the PM adds to
`generated_files`.

## Canonical topology

Versioned `docs/` follows the active working tree; ignored `.state/`
lives only in the default source tree (`state_root`).

```text
docs/                               # versioned; active working tree
├── index.md
├── architecture/
│   ├── overview.md
│   ├── <architecture-slug>.md
│   ├── <architecture-slug>/*.md
│   └── decisions/<nnnn>-<decision-slug>.md
├── design/
│   ├── system.md
│   ├── system/*.md
│   ├── <design-slug>.md
│   └── <design-slug>/*.md
├── specs/<capability>/
│   ├── index.md
│   ├── provenance.json
│   └── *.md
└── <domain>/<slug>/…                # plugin-owned durable documents

.state/                       # ignored; default source tree only
├── overview.md                      # global status index across every source tree
├── notion/                          # default source tree only: Notion mirror
├── archive/<work-id>/               # parked idle streams; resolver never enumerates
└── works/<work-id>/                 # every stream, whichever tree works it
    ├── goal.md
    ├── state.md
    ├── lease.json
    ├── state/{working,journal,revisions,unresolved,plan,discovery}.md
    ├── spec/
    ├── proposals.md + proposals/*.md
    ├── changes.md + changes/*.md
    ├── decisions.md + decisions/*.md
    ├── design.md + design/*.md
    ├── review.md + reviews/*.md
    └── artifacts/
```

All generated project Markdown filenames are lowercase; plugin control files
with fixed runtime names (`SKILL.md`, `CLAUDE.md`, …) keep them.

### Durable documentation

- `docs/index.md` is the small entrypoint to architecture, design, and
  capability specifications.
- `docs/architecture/` owns structural rules, boundaries, topology,
  protocols, and flows; a choice with alternatives and consequences is an ADR
  under `decisions/`, never a second architecture truth.
- `docs/design/` owns durable system-wide and feature design.
- `docs/specs/<capability>/` is reviewed, versioned specification content.
  For an inline source, `index.md` is the durable authoritative carrier; for
  an explicit local source it is a content-equivalent durable carrier; for
  Notion it is a verified derivation. `provenance.json` records source kind,
  source and approval hashes, template identity, and output hashes.
- Beyond those trees, **durable user-facing documents live under
  `docs/<domain>/<slug>/`**, owned by the plugin that mints them and
  referenced from the owning stream's state — for example
  `docs/initiatives/<slug>/index.md` and
  `docs/production/<slug>/assets.md`. The minting plugin defines the
  document's shape; this contract defines only its home and provenance
  obligations.
- Task implementation state does not become durable merely because a skill
  wrote it. Promote only stable knowledge, with provenance and supersession
  links, during completion ([retirement.md](retirement.md)).

## Deterministic names

`"$ESSENTIAL_ROOT/bin/derive-engineering-name"` is the only path-name
derivation implementation (`slug`, `tracker-work-id`, `minted-work-id`,
`workspace-work-id`; see `--help`). Never reimplement its rules; pass every
occupied sibling to `--collision-with` (for a work ID: every ID under `works/`
and `archive/`). A work ID is an identity, never renamed; derive or mint only
when the resolver cannot select safely and the PM resolved the ambiguity. A
minted `<kind>-<scope-slug>` names the stream, its branch
`<kind>/<scope-slug>`, and its source tree; stack and sub-work branches keep
the ID as their prefix (`<work-id>/NN-<type>`, `<work-id>-<sub-work>-NN`), so
any of them resolves it. Naming rules: use the
owning capability (not the task title) for `docs/specs/<capability>/`; ADRs
alone use a zero-padded monotonic numeric prefix and are never renumbered;
ordinary work-local children use unnumbered semantic `<slug>.md` names, with
numbered `<nn>-<topic-slug>.md` (increments of 10) reserved for mechanical
splits of an oversized file; never use `part-1`, `misc`, or a task title as a
child name.

## Work memory

### Global overview (`.state/overview.md`)

The default source tree carries `.state/`, and with it the single global
`overview.md`: one table of every work stream (work ID, lifecycle, headline,
next action, `Location`, `Spec`, `Documentations`). Every stream's state
already sits under the same `works/`, so this is an index over local state,
not a cross-tree aggregator; its `Location` column records **which checkout
each stream is worked in**. Every cell derives from each stream's own files,
so a lost or stale overview is rebuilt by re-reading them. The PM/coordinator
updates it whenever a stream's status changes — in particular at handover. A
stream is worked in exactly one source tree at a time. Before planning against
a capability, resolve any sibling row marked `pending-publication` first.

### One stream at a time

Work **one** stream to completion before starting another. Finished execution
sets lifecycle `reviewing`, not a terminal state; `completed` needs merge
evidence, never the author's say-so. Read
[stream-completion.md](stream-completion.md) when a stream finishes or is
settled.

### `goal.md`

`goal.md` is the work stream's charter: the goal, scope and non-goals,
numbered success criteria (`SC-1`, `SC-2`, …) each with expected acceptance
evidence, specification provenance, and the stream's `## Workspace anchors`
(the resolved git/jj workspace by default; other kinds per
[anchors.md](anchors.md)). It carries `Charter revision: N`, bumped only on
explicit user approval and journaled — the charter separates what "done"
means from where the work stands, so status churn can never drift the
definition of success. For a Notion-backed contract the canonical
specification wins every conflict, and charter drift after a new base is a
user decision, never a silent edit. Task `Acceptance` cells, `changes/`
children, and `reviews/alignment.md` findings cite `SC-n` IDs so closure is
checkable.

### `state/working.md` and `state.md`

`state/working.md` is a temporary, narrow lens on what is being worked on
now — current focus, handback point, and fast paths only; the PM/coordinator
is its only writer; aim for ~4,096 bytes editorially, with no mechanical
gate. A subagent reads it only for current-work navigation and reads
`state.md` for resume, planning, alignment, or when explicitly assigned; it
reports paths, evidence, and state deltas to the PM and never edits PM-owned
work memory.

`state.md` is the complete resumable execution context: full plan, lifecycle
status, decisions, dependencies, blockers, open questions, review state,
evidence references, repository revision, and sync state. It links to the
charter rather than restating it, carries `Plan revision: N` (each bump
appends what/why/approver/spec base-id to `state/revisions.md`), the
monotonic `State revision: N`, and the inventory of `proposals/` children
awaiting approval or approved-but-unimplemented, kept current the moment a
proposal changes. Detail lives in semantic `state/*.md` children;
`state.md` references rather than copies. Every new or explicitly rewritten
state file follows [the work-state contract](engineering-work-state.md);
state is free-form, LLM-readable Markdown with no separate validation step —
read it directly and judge. Preserve any existing state file byte-for-byte
until an explicit rewrite; older shapes migrate lazily at the next explicit
coordinator rewrite, journaled, never on read.

### Persistence and the coordinator lease

Persist state immediately, never lazily — append first, reconcile second.
The moment a task changes status, a decision is made, a revision is
approved, or a sync event lands, the lease holder appends one journal line
(grammar in the work-state contract and the journal's own header) and then
reconciles the affected tables. The journal is append-only; the tables in
`state.md`, the lazy overviews, and `overview.md` are views over it, so
suspected drift is settled by re-reading the journal. State in
`.state/` is the operational projection of the work, not the record of
record: deleting it may cost convenience and execution detail, but must
never erase an accepted decision, approved contract, published artifact
identity, or unresolved critical risk — those live in versioned docs and
durable promotion records; every state change, discovery, and decision
lands immediately in the journal and its owning file. This
discipline bounds crash loss to one journal line. A worker without the lease
returns its status change and evidence in its output manifest immediately;
the lease holder reconciles it at once.

One actor holds the work item's coordinator lease and is the sole writer of
`goal.md`, `state/working.md`, `state.md`, `state/journal.md`,
`state/revisions.md`, the four lazy overview files, and `review.md`. The PM
holds it by default and may explicitly grant it to one orchestration skill,
naming the files covered. Every other subagent is a worker: it writes only
assigned children and returns paths plus reconciliation deltas. The lease is
on disk, not just convention — never write under a live foreign lease, and
claim an expired lease only through the explicit takeover verb, journaled as
a `lease` event. Verbs, the write protocol, and the `State revision` bump
live in [lease.md](lease.md); read it before any coordinator write.

### Overviews, decisions, and reviews

Create `proposals.md`, `changes.md`, `decisions.md`, or `design.md` with the
first child in its folder and reconcile them per
[overviews.md](overviews.md) — including the proposals-vs-changes
distinction, canonical child statuses, and deviation provenance. Decisions
follow [decision-causality.md](decision-causality.md); accepting one
triggers the blast-radius sweep. Reviews follow
[reviews.md](reviews.md): `review.md` rolls up the seven canonical
engineering areas plus any plugin-namespaced areas, and work closes only
when the roll-up agrees with every detail.

## Specification lifecycle

An explicit local path, approved inline candidate, or selected Notion
identity may supply a specification; inline prompt text is evidence only
until it becomes an approved candidate with a durable carrier. Neither path
claims a Notion round trip. Spec freshness is checked
at named moments — materialize before planning, before each dispatch
batch, before review, and at completion — and a changed base triggers the
revalidation sweep (non-done dependents `! blocked`; done rows keep `✓ done`
and gain stale validity plus remediation tasks). Mirrors, materialization,
the sweep procedure, the authored-docs sweep, and completion verification
live in [spec-lifecycle.md](spec-lifecycle.md); mid-execution change routing
lives in [change-control.md](change-control.md).

## Evidence, continuity, and retirement

Keep logs, screenshots, captures, binaries, and large raw evidence outside
Markdown; work artifacts store concise results plus source-bound paths,
revisions, hashes, and dispositions. Resumable findings belong in
`state/discovery.md`; source material belongs in `artifacts/`; only durable
conclusions are promoted to `docs/`.

Continuity has one mechanism: the on-disk work directory. A handover
completes the stream's state and updates `overview.md`, both under the default
source tree's `.state/`; a resume reads those files and continues from
whichever tree the reader is in, since every tree resolves to the same state.
Nothing else is needed — the directory holds state,
decisions, specification, and `artifacts/` together, and each stream records
the source anchor that names the revision its work assumes. Handover scopes to
the stream being paused and releases the coordinator lease.

Remember that `.state/` is ignored: one reflexive `git clean -fdx`
deletes every stream on the machine, silently. A copy of `.state/`
kept outside the repository is the designed recovery — take one before a
stream carries non-recoverable decisions, and promote durable knowledge
early. [essential:doctor](../skills/doctor/SKILL.md) checks a recovered
tree's structural integrity before it is resumed. Idle streams are parked and completed streams retired per
[retirement.md](retirement.md); retirement deletes the operational
projection, so it is gated on promotion and decision dispositions.

## Write boundary

Work state has exactly two homes: the **default source tree's**
`.state/` (the resolver's `state_root`) and the **active** tree's
versioned `docs/`. Every write a lifecycle skill makes lands in
`state_root/.state/works/<work-id>/**`,
`state_root/.state/overview.md`, or — at promotion only — the active
tree's `docs/`. Any other destination is a contract violation. A skill that
believes it needs one has misread this contract; stop and report instead.

**Output volume is never a reason to create a file.** A report that would be
long is shortened editorially or degraded to pointers into
`.state/` — the state is already on disk, so a pointer loses nothing.
Spilling a response to an ad hoc file is never the answer, whatever its
size. Where a generated carrier genuinely must exist as a file — a
`git format-patch` patch, a bundle, a captured log — its only legal home is
`.state/works/<work-id>/artifacts/`, so it travels with the work
directory. This is also the destination for the general instruction to
externalize long detail to a task-owned artifact. A worker that has not
cleared the `requires_ignore` gate writes nothing at all and reports.

## Structural doctor

`"$ESSENTIAL_ROOT/bin/engineering-doctor" --work-dir <work_dir>` is a
read-only structural checker (broken IDs, cycles, contradictory statuses,
missing evidence annotations, dead links, unsuperseded decisions, lease
conflicts, overview drift). It never judges prose or blocks by default —
findings inform the coordinator's own reading. Run it before large dispatch
batches, handover, and retirement; pass `--strict` (nonzero exit on errors)
when work is irreversible or release-critical and treat failure as
stop-and-report.

## Output manifest and final size loop

Every artifact-writing skill returns the explicit final paths it generated or
materially rewrote, and the coordinator runs exactly one batch size pass over
them at the end of a run. Read
[output-manifest.md](output-manifest.md) for the manifest shape, the checker
invocation, and the split round it can demand.
