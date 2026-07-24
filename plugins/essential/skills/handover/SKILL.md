---
name: handover
description: Persist the current source tree's engineering work stream state and update the default source tree's global cross-tree overview, then emit a bounded receipt indexing the current tree's streams and naming the work directory that carries each one. Use when pausing or transferring coding work; this skill records continuity and does not execute the work.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion
argument-hint: "[work-id-filter]"
---

# Work Handover

Refresh the local memory of the work streams in the **current source tree**
(this Git worktree or jj workspace), update the default source tree's global
`.engineering/overview.md`, and emit one bounded receipt that indexes those
streams and names the work directory carrying each. `.engineering/` is the
portable carrier: work moves to another tree or machine by copying the work
directory, and the receipt says which directory to copy and where the code
lives. `essential:takeover` owns resumption; it always resumes from the state
files on disk.

## Boundaries

- Use for pausing or transferring the engineering work streams in the current
  source tree.
- Handover is scoped to the current source tree only. Never index, refresh, or
  rewrite another source tree's `.engineering/works/`; the default tree's
  `overview.md` is the only cross-tree surface, and this skill only upserts the
  current tree's row in it.
- Do not perform git history, push, PR, build, test, deployment, review, or
  implementation work.
- Write only to the current tree's `.engineering/works/<work-id>/**` and the
  default tree's `.engineering/overview.md`. No other destination is ever
  correct — not `/tmp`, not a dotted sibling such as `.local/`, not the
  repository root, not `$HOME`, not `docs/`. Handover creates no continuation
  file of its own: the state files *are* the continuation.
- Never write a file because the receipt or report would be large. A long
  receipt is shortened to pointers into `.engineering/`, never spilled to
  disk. If a receipt cannot be produced within that bound, report why; the
  persisted state on disk is already the durable outcome.
- Do not assume `.engineering/` is committed. Do assume it is portable: a
  deliberate copy of a work directory is how a stream reaches another tree or
  machine.
- Do not claim a stream's *code* is reachable elsewhere when its relevant
  repository changes exist only in this working copy. Copying the work
  directory carries the state, not the commits; a local-only change ID is not
  a destination-reachable source anchor.
- Only the main agent/PM may run this workflow because it writes `state/working.md`
  and reconciles work indexes and the overview.

## Inputs

- Optional `[work-id-filter]`; otherwise handle every work stream under
  `.engineering/works/` in the **current source tree**. A filter narrows the
  streams to carry in full; it never invents a stream and never reaches another tree.
- Persistence requires only a repository checkout and a resolvable current-tree
  workspace; a pause needs no external anchor and no writable receipt
  destination. The receipt is additionally published to an external
  continuation anchor (task, issue, PR, or Notion work item) when one is
  writable; otherwise it is simply returned in the response. Because the
  receipt indexes rather than carries, it always fits either destination.
- A stream whose repository changes are not reachable from another machine is
  still persisted, still indexed, and still resumable — here immediately, and
  elsewhere once its code is reachable. Only its *code* portability is
  deferred, and the receipt says so.

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
default tree's global `overview.md`. This is the durable result — a session can
pause, close, and later resume from those files with no receipt, and another
machine can resume from a copy of them. The **receipt** (steps 8–9) is a
bounded index over that state: it names each stream, its work directory, and
how to reach its code. It carries no file contents, so it neither grows with the
work nor can fail for size. Never terminate the run before the overview upsert.

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
   streams get a full refresh (steps 2–6) and a per-stream receipt entry
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
   task ID, exact next owner, exact next action, a capability-level continuation
   intent describing the work type (never a fixed skill name), and the stream's
   **source anchor** — the destination-reachable revision the work assumes,
   resolved by the rule in step 8, which runs before this write when an anchor
   is not already recorded. State alone must be enough to route a resume and to tell
   any tree, here or elsewhere, which revision to be at. If eligible work
   Markdown requires splitting under the shared batch process, keep the original
   path as overview.
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

### Receipt (bounded index over the persisted state)

8. For each selected stream, resolve its source anchor — how a destination
   checkout reaches the code this work assumes. When every relevant repository
   change is already captured by a revision reachable through the remote
   repository/ref, record that revision. Otherwise consult the user: either
   pause to commit and, when authorized, create a pull request so a reachable
   revision exists, or obtain explicit approval to generate a `git format-patch`
   patch or a `git bundle`. **Write any such carrier to
   `.engineering/works/<work-id>/artifacts/`** — never to `/tmp`, the repository
   root, or any path outside the work directory — so it travels with the state
   when the directory is copied. Record the carrier and its compatible
   base/result revision with plain git; there is no checksum verification. If a
   stream has no destination-reachable anchor and no approved carrier, record its
   exact local-only changes and continue: the stream is still persisted, still
   indexed, and still resumable in this tree; only its code portability is
   deferred. This never returns `handover: blocked`; the pause already succeeded
   at step 7.
9. Build the receipt defined in
   [references/output-format.md](references/output-format.md). It has three
   parts and no others: a `## Handover receipt` header (repository identity,
   source tree, timestamp), a `## Work index` table with one row for **every**
   stream from step 1, and a `## Transfer` section naming each selected stream's
   absolute work directory, its source anchor from step 8, and the instruction to
   copy that directory to the destination tree and run `essential:takeover`
   there. Each index row carries the work ID, lifecycle, one-line headline, next
   owner, next action, the capability-level continuation intent (never a fixed
   skill name), source anchor label, `State revision`, and coordinator lease
   status at handover (released, or expired with owner).

   Never inline a work file's contents, a specification's body, artifact bytes,
   or a patch into the receipt — the work directory already holds them, and
   naming it is the whole mechanism. A specification appears only as provenance
   (repository-relative path, or a Notion stable ref with its captured revision
   and the immutable merge base a Notion-backed resume needs), because its
   materialized copy travels inside the directory. Redact any secret that would
   otherwise appear in a headline, path, or anchor label. The receipt is bounded
   by construction: its size tracks the number of streams, never the size of the
   work, so it always fits its destination and is never written to a file.
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
- No path outside the closed write set was created or rewritten: every entry in
  `generated_files` is under the current tree's
  `.engineering/works/<work-id>/`, or is the default tree's
  `.engineering/overview.md`. No continuation file, receipt file, patch, or
  bundle was written anywhere else, and nothing was written because output was
  large.
- Every current-tree stream appears exactly once in the receipt's `## Work index`
  with its canonical lifecycle, and every selected stream appears in
  `## Transfer` with its absolute work directory and source anchor.
- The receipt inlines no work-file contents, specification body, artifact bytes,
  or patch, and fits its destination without elision.
- Each selected stream's `state.md` is complete, internally consistent, and links
  `state/working.md`; the latter contains only current-focus summary and fast
  paths.
- Every overview matches its children and canonical status vocabulary.
- Decisions, assumptions, deviations, blockers, review dispositions, evidence,
  promotion, and specification state are preserved per selected stream.
- Each selected stream is transferable by copying its work directory: the
  directory holds its state, its materialized specification, and any approved
  patch or bundle under `artifacts/`, and its recorded source anchor brings a
  destination checkout to the right revision.
- No secret, credential, absolute host path, path traversal, or symlink escape
  is present in the receipt.
- Every held coordinator lease was released and each indexed stream states
  its `State revision`.

## Completion

Use [references/output-format.md](references/output-format.md). Report the
receipt, the current source tree, the default tree's `overview.md` path, the
indexed stream count, per-stream updated state paths and work directory,
classification and decision counts, external and source-anchor status, per-stream
transferability, and `generated_files`. `handover: complete` reports the
successful pause once persistence and the `overview.md` upsert land; mark a
stream `transferable: false` only when its source anchor is missing — its state
is transferable regardless — and reserve `handover: blocked` for a failure that
prevents persistence itself. Examples live in
[references/examples.md](references/examples.md).
