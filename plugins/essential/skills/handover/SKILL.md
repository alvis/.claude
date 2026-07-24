---
name: handover
description: Persist the current source tree's engineering work stream state and update the default source tree's global cross-tree overview, then emit a portable receipt that indexes the current tree's streams and carries each continuable one in full. Use when pausing or transferring coding work; this skill records continuity and does not execute the work.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion
argument-hint: "[work-id-filter]"
---

# Work Handover

Refresh the ignored local memory of the work streams in the **current source
tree** (this Git worktree or jj workspace), update the default source tree's
global `.engineering/overview.md`, and emit one portable receipt that can
rehydrate the current tree's work elsewhere. `essential:takeover` owns
resumption; the receipt routes each stream's continuation to the relevant
implementation skill.

## Boundaries

- Use for pausing or transferring the engineering work streams in the current
  source tree.
- Handover is scoped to the current source tree only. Never index, refresh, or
  rewrite another source tree's `.engineering/works/`; the default tree's
  `overview.md` is the only cross-tree surface, and this skill only upserts the
  current tree's row in it.
- Do not perform git history, push, PR, build, test, deployment, review, or
  implementation work.
- Do not create root-level continuation files or assume `.engineering/` is
  committed, copied, or shared between Git worktrees or jj workspaces.
- Do not claim a stream is rehydratable when its relevant repository changes
  exist only in this working copy. A local path or change ID with no
  destination-reachable carrier is not a portable source anchor.
- Only the main agent/PM may run this workflow because it writes `state/working.md`
  and reconciles work indexes and the overview.

## Inputs

- Optional `[work-id-filter]`; otherwise handle every work stream under
  `.engineering/works/` in the **current source tree**. A filter narrows the
  streams to carry in full; it never invents a stream and never reaches another tree.
- Persistence requires only a repository checkout and a resolvable current-tree
  workspace; a same-machine pause needs no external anchor and no writable
  receipt destination. The portable receipt additionally uses, per continuable
  stream, an external continuation anchor (task, issue, PR, or Notion work item);
  if no anchor is writable, emit the receipt in the response for the user to
  paste there. A stream that has no destination-reachable anchor is still
  persisted and resumable locally; only its cross-machine carrying degrades.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Run the resolver: its `active_workspace`
is the current source tree that owns the work streams to refresh, and its
`default_workspace` locates the global `.engineering/overview.md` to update
(which may be a different tree on the same machine). Resolve the work root,
conventions, naming, and ownership from that reference before reading or writing
state. Handover never mints an empty work item. Hold each selected stream's
on-disk coordinator lease before rewriting its state in steps 5–7 with the
idempotent `engineering-lease ensure` verb — it renews a lease this session
already holds and acquires a free one; a live foreign lease (`contended`)
stops that stream with a report. Perform the rewrites through the
lease-verified write path in Essential's `lease.md`, bump `State revision`
on each coordinator rewrite, and release every lease at completion.

Handover has two outcomes. **Persistence** (steps 1–7) always runs and always
completes: it refreshes the current source tree's on-disk work state and the
default tree's global `overview.md` so a same-machine session can pause, close,
and later resume from state files with no receipt. The **portable receipt**
(steps 8–9) is an additional best-effort artifact for cross-machine transfer;
per-stream it degrades to an index-only row when a source anchor is not
destination-reachable, but such degradation never blocks persistence, the
overview upsert, or the run. Never terminate the run before the overview upsert.

### Persistence (always completes)

1. List every `.engineering/works/<work-id>/` stream in the **current source
   tree** (the resolver's `active_workspace`) per the Essential contract — always
   the complete set, never narrowed by `[work-id-filter]`, because the overview
   upsert (step 7) and the receipt's `## Work index` (step 9) must show every
   stream in this tree. For each stream, read `state.md` to record its lifecycle
   status and one-line headline. Partition the streams: `initialized`, `active`,
   and `blocked` are **continuable**; `complete` and `retiring` become
   **index-only** rows and are never an error. Then apply the optional
   `[work-id-filter]` to the continuable streams to derive the **selected**
   streams (all continuable streams when no filter is given); only the selected
   streams get a full refresh (steps 2–6) and a carried receipt section
   (steps 8–9). The filter never removes a stream from step 1, the overview, or
   the index.
2. For each selected stream, read `state/working.md` first when present, then
   `state.md`, its linked detail files, the four lazy overview files, `review.md`,
   relevant review areas, evidence, and the materialized working specification.
   From the `state.md` task table, determine which tasks are runnable, which are
   blocked, the current owner, and the next action; proceed on that reading, with
   no separate validation step. Treat repository and runtime evidence as
   authoritative over stale local memory. Any implementation detail that root
   state links is procedure keyed by existing task IDs, not plan authority.
3. For each selected stream, gather todos, current revision/bookmark/branch,
   working-copy status, staged and unstaged changes, untracked files, recent
   commits, and each specification's location: inline raw text, a
   repository-relative path, or a Notion reference with its captured revision.
   Classify changed and planned files with the substates in
   [references/document-templates.md](references/document-templates.md).
4. For each selected stream, identify every material unresolved decision.
   Consult the user using
   [references/decision-consultation.md](references/decision-consultation.md);
   route durable decision detail to `decisions/<slug>.md` and let the PM
   reconcile `decisions.md`. Record low-impact reversible assumptions in
   `state.md` with evidence and recheck triggers.
5. Generate one UTC ISO-8601 timestamp for the whole run. For each continuable
   stream, rewrite `state.md` as the complete work context: goal, full
   parent/subtask task table with marked status and evidence, lifecycle, success
   criteria, decisions, dependencies, blockers, review dispositions, evidence,
   durable promotion, specification location, and a prominent link to
   `state/working.md`. Include a `## Continuation` section persisting the current
   task ID, exact next owner, exact next action, and a capability-level
   continuation intent describing the work type (never a fixed skill name), so a
   same-machine takeover can route the resume from on-disk state alone. If
   eligible work Markdown requires splitting under the shared batch process, keep
   the original path as overview.
6. For each selected stream, rewrite `state/working.md` to approximately 4,096
   bytes through editorial discipline: current focus, current status, immediate
   handback point, and fast relative paths only. It is not a plan, history, or
   complete context. Do not mechanically size-gate it. Reconcile that stream's
   existing lazy `proposals.md`, `changes.md`, `decisions.md`, and `design.md`
   overview files from child metadata; never copy child details into an overview.
7. Update the global `.engineering/overview.md` in the default source tree (the
   resolver's `default_workspace`), following the canonical shape in
   [references/document-templates.md](references/document-templates.md).
   Immediately before writing, re-read the current `overview.md` so a concurrent
   update in another tree is not lost. Upsert one row per stream from step 1 whose
   `Location` is the current source tree — work ID, lifecycle, headline, next
   action, the current tree's `Location` (path plus kind and revision), and any
   `docs/` link in `Documentations` — and preserve every other row (streams that
   live in other source trees) byte-for-byte. If the default tree carries no
   `overview.md` yet, create it. Never write another tree's `works/`. After this
   write the same-machine pause is complete and resumable from state files.

### Portable receipt (best-effort; degrades per stream, never blocks)

8. For each selected stream, resolve a portable source anchor before carrying its
   full `## Work stream:` section. When every relevant repository change is
   already captured by a revision reachable through the receipt's remote
   repository/ref, record it as the remote revision to check out. Otherwise
   consult the user: either pause to commit and, when authorized, create a pull
   request so a reachable revision exists, or obtain explicit approval to attach a
   `git format-patch` patch or a `git bundle` ref to that stream's external
   anchor. Record the carrier and its compatible base/result revision with plain
   git; there is no checksum verification. A local staging path alone is not an
   anchor. If a selected stream has no destination-reachable carrier, drop it to
   an index-only row, record its exact local-only changes, and continue — the
   stream still resumes locally from the state written in steps 5–7; only its
   cross-machine carrying is deferred. This never returns `handover: blocked` for
   the run; the local pause already succeeded at step 7.
9. Build the receipt's `## Work index` across the current tree's streams from
   step 1 (every stream, each with its `Location`), then emit a
   `## Work stream: <work-id>` section per selected stream anchored in step 8:
   gather the raw contents of `goal.md`, `state.md`, `state/working.md`, and every
   continuity-relevant detail file (decisions, changes, design, `state/*.md`
   children including `state/journal.md` and `state/revisions.md` when they
   exist, needed artifacts, and every outstanding `proposals/` child still
   awaiting approval or approved but not yet implemented) and carry them verbatim, each in its own fenced
   block whose fence is at least one backtick longer than the longest backtick run
   inside that file and whose preceding line names the stream-root-relative path
   as `path: <relative path>` with no `<work-id>/` prefix. When a stream depends
   on specific ignored artifacts to continue, carry those bytes inline or attach
   them by external locator — a bare `artifacts/…` path is not portable — but
   never carry the whole `artifacts/` tree. Include any specification needed to
   continue as inline captured content plus its provenance (repository-relative
   path in the anchored tree, or a Notion stable ref with its captured revision,
   plus the immutable merge base a Notion-backed resume needs). Carry the
   `## Continuation` fields from step 5 into each section. Redact secrets from
   every carried payload; if redaction would make one stream's required section
   incomplete, degrade that stream to an index-only row rather than blocking the
   whole receipt. Produce the external receipt defined in
   [references/output-format.md](references/output-format.md). Each stream's
   receipt section routes continuation to the relevant implementation skill and
   records the current task, exact next owner, exact next action, and a
   capability-level continuation intent describing the work type (never a fixed
   skill name). State each carried stream's `State revision`, its coordinator
   lease status at handover (released, or expired with owner), and pointers to
   checkpoints already published at its external anchor; emit the handover
   checkpoint to that anchor per Essential's `checkpoints.md`. Inline
   source/spec/artifact payloads are explicit portable receipt data, not a
   reference to ignored local memory.
10. Return every created or materially rewritten path — including the updated
   `overview.md` — in `generated_files`. Do not run file sizing; after all
   artifact writers finish, the PM checks only eligible work Markdown inside the
   target `.engineering/` and coordinates any complete split round.

## Verification

- Persistence completed before any receipt work: every selected stream's
  `state.md` (with its `## Continuation` fields) and `state/working.md` were
  refreshed and the default tree's `overview.md` was upserted; the run was never
  terminated by a missing source anchor.
- Handover touched only the current source tree's `works/` and the default
  tree's `overview.md`; no other source tree's work streams were indexed or
  rewritten.
- `overview.md` now carries one up-to-date row per current-tree stream — each with
  its lifecycle, `Location`, `Spec`, and `Documentations` — and every other
  tree's rows are unchanged.
- A same-machine takeover could resume every continuable stream from the on-disk
  state alone — `## Continuation` names the current task, next owner, next action,
  and continuation intent — with no receipt.
- Every current-tree stream appears exactly once in the receipt's `## Work index`
  with its canonical lifecycle; a selected stream with a destination-reachable
  anchor is carried in full, and `complete`/`retiring` streams, unselected
  streams, and anchor-degraded streams are index-only.
- Each carried stream's `state.md` is complete, internally consistent, and links
  `state/working.md`; the latter contains only current-focus summary and fast
  paths.
- Every overview matches its children and canonical status vocabulary.
- Decisions, assumptions, deviations, blockers, review dispositions, evidence,
  promotion, and specification state are preserved per carried stream.
- Each `## Work stream:` section carries the raw contents of that stream's
  `goal.md`, `state.md`, `state/working.md`, and every continuity-relevant detail file (with
  any required artifacts carried as bytes, not a bare path), each labelled with
  its stream-root-relative `path:` line (no `<work-id>/` prefix) and fenced with a
  collision-safe backtick run.
- Each carried stream can rehydrate without access to this `.engineering/` tree:
  its source anchor is destination-reachable, and every carried work-state file,
  specification, and required artifact is contained in the anchored tree, carried
  inline, or named by a durable external locator.
- No secret, credential, absolute host path, path traversal, or symlink escape
  is present in a carried payload.
- Every held coordinator lease was released, each carried stream states its
  `State revision`, and the handover checkpoint was emitted to each carried
  stream's external anchor (or its absence is recorded as degraded
  durability).

## Completion

Use [references/output-format.md](references/output-format.md). Report the
receipt, the current source tree, the default tree's `overview.md` path, the
carried and index-only stream counts, per-stream updated state paths,
classification and decision counts, external and source-anchor status, per-stream
rehydratability, and `generated_files`. `handover: complete` reports the
successful local pause once persistence and the `overview.md` upsert land, even
when a stream is `carried: false`; mark a stream's cross-machine rehydratability
`false` when its source anchor is missing, and reserve `handover: blocked` for a
failure that prevents persistence itself. Examples live in
[references/examples.md](references/examples.md).
