---
name: handover
description: Persist the current source tree's engineering work stream state and update the default source tree's global cross-tree overview, so the session can pause and any later session resume from the files on disk. Use when pausing coding work; this skill records continuity and does not execute the work.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion
argument-hint: "[work-id-filter]"
---

# Work Handover

Refresh the local memory of the work streams in the **current source tree**
(this Git worktree or jj workspace) and update the default source tree's global
`.engineering/overview.md`, so the session can stop here and a later one pick
the work up exactly where it stands. `essential:takeover` owns resumption; it
always resumes from the state files on disk.

## Boundaries

- Use for pausing the engineering work streams in the current source tree.
- Handover is scoped to the current source tree only. Never index, refresh, or
  rewrite another source tree's `.engineering/works/`; the default tree's
  `overview.md` is the only cross-tree surface, and this skill only upserts the
  current tree's row in it.
- Do not perform git history, push, PR, build, test, deployment, review, or
  implementation work.
- Write to exactly two destinations: the current tree's
  `.engineering/works/<work-id>/**` and the default tree's
  `.engineering/overview.md`. Handover does not promote to `docs/` — promotion
  belongs to completion, not to a pause — and it creates no continuation file
  of its own: the state files *are* the continuation.
- Never write a file because the report would be large. A long report is
  shortened to pointers into `.engineering/`, never spilled to disk; the
  persisted state on disk is already the durable outcome.
- Do not assume `.engineering/` is committed.
- Only the main agent/PM may run this workflow because it writes `state/working.md`
  and reconciles work indexes and the overview.

## Inputs

- Optional `[work-id-filter]`; otherwise handle every work stream under
  `.engineering/works/` in the **current source tree**. A filter narrows the
  streams to refresh in full; it never invents a stream and never reaches
  another tree.
- Persistence requires only a repository checkout and a resolvable current-tree
  workspace. A pause needs nothing external.

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

Persistence always runs and always completes: it refreshes the current source
tree's on-disk work state and the default tree's global `overview.md`. That is
the whole outcome — a session can pause, close, and later resume from those
files. Never terminate the run before the overview upsert.

## Workflow

1. List every `.engineering/works/<work-id>/` stream in the **current source
   tree** (the resolver's `active_workspace`) per the Essential contract — always
   the complete set, never narrowed by `[work-id-filter]`, because the overview
   upsert (step 7) must show every stream in this tree. For each stream, read
   `state.md` to record its lifecycle status and one-line headline. Partition the
   streams: `initialized`, `active`, and `blocked` are **continuable**;
   `complete` and `retiring` become **index-only** rows and are never an error.
   Then apply the optional `[work-id-filter]` to the continuable streams to
   derive the **selected** streams (all continuable streams when no filter is
   given); only the selected streams get a full refresh (steps 2–6). The filter
   never removes a stream from step 1 or the overview.
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
   **source anchor** — the revision the work assumes. State alone must be enough
   to route a resume and to tell a checkout which revision to be at. If eligible
   work Markdown requires splitting under the shared batch process, keep the
   original path as overview.
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
   write the pause is complete and resumable from state files.
8. Return every created or materially rewritten path — including the updated
   `overview.md` — in `generated_files`. Do not run file sizing; after all
   artifact writers finish, the PM checks only eligible work Markdown inside the
   target `.engineering/` and coordinates any complete split round.

## Verification

- Every selected stream's `state.md` (with its `## Continuation` fields) and
  `state/working.md` were refreshed and the default tree's `overview.md` was
  upserted.
- Handover touched only the current source tree's `works/` and the default
  tree's `overview.md`; no other source tree's work streams were indexed or
  rewritten.
- `overview.md` now carries one up-to-date row per current-tree stream — each with
  its lifecycle, `Location`, `Spec`, and `Documentations` — and every other
  tree's rows are unchanged.
- A takeover could resume every continuable stream from the on-disk state alone —
  `## Continuation` names the current task, next owner, next action, and
  continuation intent.
- No path outside the closed write set was created or rewritten: every entry in
  `generated_files` is under the current tree's
  `.engineering/works/<work-id>/`, or is the default tree's
  `.engineering/overview.md`. No continuation file was written anywhere else,
  and nothing was written because output was large.
- Each selected stream's `state.md` is complete, internally consistent, and links
  `state/working.md`; the latter contains only current-focus summary and fast
  paths.
- Every overview matches its children and canonical status vocabulary.
- Decisions, assumptions, deviations, blockers, review dispositions, evidence,
  promotion, and specification state are preserved per selected stream.
- No secret, credential, absolute host path, path traversal, or symlink escape
  is present in the report.
- Every held coordinator lease was released and each refreshed stream states
  its `State revision`.

## Completion

Use [references/output-format.md](references/output-format.md). Report the
current source tree, the default tree's `overview.md` path, the stream count,
per-stream updated state paths and work directory, classification and decision
counts, and `generated_files`. `handover: complete` reports the successful pause
once persistence and the `overview.md` upsert land; reserve `handover: blocked`
for a failure that prevents persistence itself. Examples live in
[references/examples.md](references/examples.md).
