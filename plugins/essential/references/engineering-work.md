# Engineering work lifecycle

Read this contract before creating or materially rewriting project engineering
artifacts. It defines their paths, ownership, promotion, and final size check.
Domain skills own artifact content; Essential owns this cross-plugin lifecycle.
Read [truth.md](truth.md) once per work stream: it defines the kinds of truth
these artifacts carry, the constitutional rules, validity, and `capability_id`.
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
  and `.gitignore` (`repo_root` is its alias); `active_workspace` owns its
  own ignored `.engineering/works/<work-id>/`, and `work_dir` is the only
  temporary root for the selected work.
- Each Git worktree or jj workspace has isolated work state. Never copy
  `.engineering/` between them or commit it.

`resolved` with `engineering_ignored: true` is a hard bootstrap gate before
any work artifact or probe is written. On `requires_ignore`, every worker
stops and reports the returned `ignore_file`. The PM alone adds the exact
`.engineering/` rule to the active workspace `.gitignore`, includes that
`.gitignore` path in `generated_files`, and reruns the resolver. A sync-only
or ad hoc `git check-ignore` probe does not replace this bootstrap contract.

### First-use work-memory bootstrap

After the user has confirmed any new work identity and the resolver returns
`resolved` with `engineering_ignored: true`, the PM invokes the resolver once
more with that confirmed ID and `--bootstrap`, before delegating or creating
any other work artifact:

```bash
"$ESSENTIAL_ROOT/bin/resolve-engineering-workspace" \
  --work-id=<confirmed-work-id> --bootstrap
```

Identity selection remains separate and interactive: `--bootstrap` never
derives or mints an ID, and it cannot bypass `work_id_required` or
`requires_ignore`. The resolver owns the mechanical bootstrap; the PM alone
may request it while holding the coordinator lease. It creates the work
directory, `state/`, and whichever of `goal.md`, `state/working.md`,
`state.md`, and `state/journal.md` is missing; each file is created with
no-clobber semantics, an existing regular file is preserved byte-for-byte,
and symlinked or non-regular components are refused on every invocation —
safe to rerun after an interrupted first use. The initial files carry
identity, revision counters at `1`, explicit placeholders, and the journal's
append-only header; downstream owners replace placeholders with observed
truth. The resolver returns exact paths in `bootstrap_created` and preserved
paths in `bootstrap_existing`; the PM adds created paths to the combined
`generated_files` manifest.

## Canonical topology

```text
docs/
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

.engineering/                       # ignored, isolated per source tree
├── overview.md                      # default source tree only: global cross-tree status index
├── notion/                          # conventional default-workspace mirror
├── archive/<work-id>/               # parked idle streams; resolver never enumerates
└── works/<work-id>/                 # in the source tree that owns the stream
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
derivation implementation (`slug`, `tracker-work-id`, `minted-work-id`; see
`--help`). Never reimplement its rules or add a random suffix; pass every
occupied sibling slug through `--collision-with`. A minted work ID is an
identity and is never renamed; derive or mint only when the resolver cannot
select safely and the PM has resolved the ambiguity. Naming rules: use the
owning capability (not the task title) for `docs/specs/<capability>/`; ADRs
alone use a zero-padded monotonic numeric prefix and are never renumbered;
ordinary work-local children use unnumbered semantic `<slug>.md` names, with
numbered `<nn>-<topic-slug>.md` (increments of 10) reserved for mechanical
splits of an oversized file; never use `part-1`, `misc`, or a task title as a
child name.

## Work memory

### Cross-tree overview (`.engineering/overview.md`)

The default source tree — Git's main worktree or the jj workspace registered
as `default` — carries the single global `overview.md`: one table of every
work stream across all source trees (work ID, lifecycle, headline, next
action, `Location`, `Spec`, `Documentations`). It is an index, not a state
store: every cell derives from each stream's own files, so a lost or stale
overview is rebuilt by re-reading them. The PM/coordinator updates it
whenever a stream's status changes — in particular at handover. A stream is
worked in exactly one source tree at a time. Before planning against a
capability, resolve any sibling row marked `pending-publication` first.

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
`.engineering/` is the operational projection of the work, not the record of
record: deleting it may cost convenience and execution detail, but must
never erase an accepted decision, approved contract, published artifact
identity, or unresolved critical risk — those live in versioned docs,
external anchors, and checkpoints ([checkpoints.md](checkpoints.md)). This
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
triggers the blast-radius sweep and a checkpoint. Reviews follow
[reviews.md](reviews.md): `review.md` rolls up the seven canonical
engineering areas plus any plugin-namespaced areas, and work closes only
when the roll-up agrees with every detail.

## Specification lifecycle

An explicit local path, approved inline candidate, or selected Notion
identity may supply a specification; inline prompt text is evidence only
until it becomes an approved candidate with a durable carrier. Neither path
claims a Notion round trip. Spec freshness is checked
at named checkpoints — materialize before planning, before each dispatch
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

Continuity has two paths. On the **same machine**, pausing and resuming
works from the on-disk state files: a handover completes the current tree's
stream state and updates the default tree's `overview.md`; a new session
reads the overview, picks a tree and stream, and resumes from that tree's
own files — no receipt required. Ignored work memory is not a
**cross-machine** transport: for that, a handover additionally emits a
plain-Markdown portable receipt into the owning task, PR, or Notion work
item (or the response), carrying a destination-reachable source anchor, the
raw work-state contents, and authoritative specification carriers. A
recipient reads those carriers in an isolated post-anchor tree before
reconstructing fresh local work state; it never copies `.engineering/` or
trusts a local-only path. Handover scopes to the current source tree only,
emits its checkpoint, and releases the coordinator lease.

Remember that `.engineering/` is ignored: one reflexive `git clean -fdx`
deletes every stream on the machine, silently. Checkpoints at the external
anchor are the designed recovery — establish the anchor and first checkpoint
before a stream carries non-recoverable decisions
([checkpoints.md](checkpoints.md)). Idle streams are parked and completed
streams retired per [retirement.md](retirement.md); retirement deletes the
operational projection, so it is gated on promotion, decision dispositions,
and the retirement checkpoint.

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

Every artifact-writing skill returns explicit final paths it generated or
materially rewrote:

<report>

```yaml
generated_files:
  - /absolute/path/to/file.md
```

</report>

Writers finish all files and links before returning the manifest and never
measure or split independently. The coordinator combines and deduplicates
manifests, selects only absolute `.md` paths inside the resolved target
workspace's `.engineering/` (excluding any `working.md`), and runs exactly
one pass when eligible paths remain:

```bash
"$ESSENTIAL_ROOT/bin/check-markdown-size" \
  --engineering-root "$active_workspace/.engineering" \
  "${generated_md_files[@]}"
```

The checker canonicalizes the declared root and every path, excludes
traversal, symlink, and other-workspace escapes, and returns every eligible
file greater than 16,384 bytes together (12,288 bytes is authoring guidance
only). The gate does not apply outside `.engineering/`; the only separate
limit is the 2,000-byte injection limit for Essential's `CLAUDE.md`,
`MAINAGENT.md`, and `SUBAGENT.md`.

On `split_required`, send all oversized files through one complete split
round — each original path remains a concise overview linking its lowercase
children — then rebuild the final manifest and run one subsequent batch
pass. The checker reports only `pass`, `split_required`, or `invalid`; it
never edits or splits files itself.
