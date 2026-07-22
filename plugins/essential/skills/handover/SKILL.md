---
name: handover
description: Persist the current source tree's engineering work stream state and update the default source tree's global cross-tree overview, then emit a portable receipt that indexes the current tree's streams and embeds each continuable one. Use when pausing or transferring coding work; this skill records continuity and does not execute the work.
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
  streams to embed; it never invents a stream and never reaches another tree.
- Require a repository checkout, a resolvable current-tree workspace, and, for
  each continuable stream, an external continuation anchor: task, issue, PR, or
  Notion work item. If no anchor is writable, emit the receipt in the response
  for the user to paste there.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Run the resolver: its `active_workspace`
is the current source tree that owns the work streams to refresh, and its
`default_workspace` locates the global `.engineering/overview.md` to update
(which may be a different tree on the same machine). Resolve the work root,
conventions, naming, and ownership from that reference before reading or writing
state. Handover never mints an empty work item.

## Workflow

1. List every `.engineering/works/<work-id>/` stream in the **current source
   tree** (the resolver's `active_workspace`) per the Essential contract. Apply
   the optional `[work-id-filter]`; default to all of this tree's streams. For
   each stream, read `state.md` to record its lifecycle status and one-line
   headline. Partition the streams: `initialized`, `active`, and `blocked` are
   **continuable** and receive full treatment below; `complete` and `retiring`
   become **index-only** rows and are never an error.
2. For each continuable stream, read `state/working.md` first when present, then
   `state.md`, its linked detail files, the four lazy overview files, `review.md`,
   relevant review areas, evidence, and the materialized working specification.
   From the `state.md` task table, determine which tasks are runnable, which are
   blocked, the current owner, and the next action; proceed on that reading, with
   no separate validation step. Treat repository and runtime evidence as
   authoritative over stale local memory. Any implementation detail that root
   state links is procedure keyed by existing task IDs, not plan authority.
3. For each continuable stream, gather todos, current revision/bookmark/branch,
   working-copy status, staged and unstaged changes, untracked files, recent
   commits, and each specification's location: inline raw text, a
   repository-relative path, or a Notion reference with its captured revision.
   Classify changed and planned files with the substates in
   [references/document-templates.md](references/document-templates.md).
4. Resolve a portable source anchor per continuable stream before claiming that
   stream is rehydratable. When every relevant repository change is already
   captured by a revision reachable through the receipt's remote repository/ref,
   record it as the remote revision to check out. Otherwise consult the user:
   either pause so `coding:commit` and, when authorized, `coding:push-pr` can
   create a reachable revision, or obtain explicit approval to attach a
   `git format-patch` patch or a `git bundle` ref to that stream's external
   anchor. Record the carrier and its compatible base/result revision with plain
   git; there is no checksum verification. A local staging path alone is not an
   anchor. If a continuable stream has no destination-reachable carrier, return a
   blocked, non-rehydratable status for that stream: degrade it to an index-only
   row marked `Embedded? no`, record its exact local-only changes, and continue
   with the other streams. If the filtered selection is a single stream and it is
   blocked, return `handover: blocked` for the whole run.
5. For each continuable stream, identify every material unresolved decision.
   Consult the user using
   [references/decision-consultation.md](references/decision-consultation.md);
   route durable decision detail to `decisions/<slug>.md` and let the PM
   reconcile `decisions.md`. Record low-impact reversible assumptions in
   `state.md` with evidence and recheck triggers.
6. Generate one UTC ISO-8601 timestamp for the whole run. For each continuable
   stream, rewrite `state.md` as the complete work context: goal, full
   parent/subtask task table with marked status and evidence, lifecycle, success
   criteria, decisions, dependencies, blockers, review dispositions, evidence,
   durable promotion, specification location, and a prominent link to
   `state/working.md`. If eligible work Markdown requires splitting under the
   shared batch process, keep the original path as overview.
7. For each continuable stream, rewrite `state/working.md` to approximately 4,096
   bytes through editorial discipline: current focus, current status, immediate
   handback point, and fast relative paths only. It is not a plan, history, or
   complete context. Do not mechanically size-gate it. Reconcile that stream's
   existing lazy `proposals.md`, `changes.md`, `decisions.md`, and `design.md`
   overview files from child metadata; never copy child details into an overview.
8. Update the global `.engineering/overview.md` in the default source tree (the
   resolver's `default_workspace`). Upsert exactly one entry for the current
   source tree — its kind (Git worktree or jj workspace), label/path, current
   revision, and a table of this tree's work streams (work ID, lifecycle,
   headline, next action) across every stream from step 1 — and preserve every
   other source tree's entry byte-for-byte. If the default tree carries no
   `overview.md` yet, create it. Never write another tree's `works/`.
9. Build the receipt's `## Work index` across the current tree's streams from
   step 1, then emit a `## Work stream: <work-id>` section per continuable
   stream: gather the raw contents of `state.md`, `state/working.md`, and every
   continuity-relevant detail file (decisions, changes, design, `state/*.md`
   children, needed evidence) and embed them verbatim, each in its own fenced
   block whose fence is at least one backtick longer than the longest backtick
   run inside that file and whose preceding line names the work-relative path as
   `path: <work-id>/…`. When a stream depends on specific ignored evidence to
   continue, embed that evidence's bytes inline or attach it by external
   locator — a bare `evidence/…` path is not portable — but never embed the whole
   `evidence/` tree. Include any specification needed to continue as inline
   captured content plus its provenance (repository-relative path in the anchored
   tree, or a Notion stable ref with its captured revision, plus the immutable
   merge base a Notion-backed resume needs). Determine that stream's current
   task, next owner, and next action by reading its task table directly. Redact
   secrets from every embedded payload; if redaction would make one stream's
   required section incomplete, degrade that stream to an index-only row rather
   than blocking the whole receipt. Produce the external receipt defined in
   [references/output-format.md](references/output-format.md). Each stream's
   receipt section routes continuation to the relevant implementation skill and
   records the current task, exact next owner, exact next action, and a
   capability-level continuation intent describing the work type (never a fixed
   skill name). Inline source/spec/evidence payloads are explicit portable
   receipt data, not a reference to ignored local memory.
10. Return every created or materially rewritten path — including the updated
   `overview.md` — in `generated_files`. Do not run file sizing; after all
   artifact writers finish, the PM checks only eligible work Markdown inside the
   target `.engineering/` and coordinates any complete split round.

## Verification

- Handover touched only the current source tree's `works/` and the default
  tree's `overview.md`; no other source tree's work streams were indexed or
  rewritten.
- `overview.md` now carries one up-to-date entry for the current source tree with
  every stream's lifecycle, and every other tree's entry is unchanged.
- Every current-tree stream appears exactly once in the receipt's `## Work index`
  with its canonical lifecycle; continuable streams are embedded and
  `complete`/`retiring` streams are index-only.
- Each embedded stream's `state.md` is complete, internally consistent, and links
  `state/working.md`; the latter contains only current-focus summary and fast
  paths.
- Every overview matches its children and canonical status vocabulary.
- Decisions, assumptions, deviations, blockers, review dispositions, evidence,
  promotion, and specification state are preserved per embedded stream.
- Each `## Work stream:` section embeds the raw contents of that stream's
  `state.md`, `state/working.md`, and every continuity-relevant detail file (with
  any required evidence carried as bytes, not a bare path), each labelled with its
  `path: <work-id>/…` line and fenced with a collision-safe backtick run.
- Each embedded stream can rehydrate without access to this `.engineering/` tree:
  its source anchor is destination-reachable, and every embedded work-state file,
  specification, and required evidence is contained in the anchored tree, carried
  inline, or named by a durable external locator.
- No secret, credential, absolute host path, path traversal, or symlink escape
  is present in an embedded payload.

## Completion

Use [references/output-format.md](references/output-format.md). Report the
receipt, the current source tree, the default tree's `overview.md` path, the
embedded and index-only stream counts, per-stream updated state paths,
classification and decision counts, external and source-anchor status, per-stream
rehydratability, and `generated_files`. Never label a stream's handover complete
when its source anchor is missing. Examples live in
[references/examples.md](references/examples.md).
