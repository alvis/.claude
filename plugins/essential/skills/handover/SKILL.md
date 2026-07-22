---
name: handover
description: Persist the complete state of every engineering work stream in the default-worktree workspace and emit one portable receipt that indexes all streams and embeds each continuable one for another workspace. Use when pausing or transferring coding work; this skill records continuity and does not execute the work.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion
argument-hint: "[work-id-filter]"
---

# Work Handover

Refresh the ignored local memory of every engineering work stream and emit one
portable receipt that can rehydrate the workspace elsewhere. The receipt indexes
every stream and embeds each continuable one. `essential:takeover` owns
rehydration; the receipt routes each stream's continuation to the relevant
implementation skill.

## Boundaries

- Use for pausing or transferring the engineering work streams in this workspace.
- Do not perform git history, push, PR, build, test, deployment, review, or
  implementation work.
- Do not create root-level continuation files or assume `.engineering/` is
  committed, copied, or shared between Git worktrees or jj workspaces.
- Do not claim a stream is rehydratable when its relevant repository changes
  exist only in this working copy. A local path or change ID with no
  destination-reachable carrier is not a portable source anchor.
- Only the main agent/PM may run this workflow because it writes `state/working.md`
  and reconciles work indexes.

## Inputs

- Optional `[work-id-filter]`; otherwise handle every work stream under
  `.engineering/works/` in the default worktree. A filter narrows the streams to
  index and embed; it never invents a stream.
- Require a repository checkout, a resolvable engineering workspace, and, for
  each continuable stream, an external continuation anchor: task, issue, PR, or
  Notion work item. If no anchor is writable, emit the receipt in the response
  for the user to paste there.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Resolve the work root, conventions, naming,
and ownership from that reference before reading or writing state. The
`.engineering/works/` tree lives in the default worktree; resolve it there.
Handover never mints an empty work item.

## Workflow

1. List every `.engineering/works/<work-id>/` stream in the default worktree per
   the Essential contract. Apply the optional `[work-id-filter]`; default to all
   streams. For each stream, read `state.md` to record its lifecycle status and
   one-line headline. Partition the streams: `initialized`, `active`, and
   `blocked` are **continuable** and receive full treatment below; `complete` and
   `retiring` become **index-only** rows and are never an error.
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
6. Generate one UTC ISO-8601 timestamp for the whole receipt. For each
   continuable stream, rewrite `state.md` as the complete work context: goal,
   full parent/subtask task table with marked status and evidence, lifecycle,
   success criteria, decisions, dependencies, blockers, review dispositions,
   evidence, durable promotion, specification location, and a prominent link to
   `state/working.md`. If eligible work Markdown requires splitting under the
   shared batch process, keep the original path as overview.
7. For each continuable stream, rewrite `state/working.md` to approximately 4,096
   bytes through editorial discipline: current focus, current status, immediate
   handback point, and fast relative paths only. It is not a plan, history, or
   complete context. Do not mechanically size-gate it. Reconcile that stream's
   existing lazy `proposals.md`, `changes.md`, `decisions.md`, and `design.md`
   overview files from child metadata; never copy child details into an overview.
8. Build the `## Work index` across **every** stream from step 1: one row per
   stream with its lifecycle, headline, next owner, next action, a short source
   anchor label, and `Embedded?`. Then, for each continuable stream, emit a
   `## Work stream: <work-id>` section: gather the raw contents of `state.md`,
   `state/working.md`, and every continuity-relevant detail file (decisions,
   changes, design, `state/*.md` children, needed evidence) and embed them
   verbatim, each in its own fenced block whose fence is at least one backtick
   longer than the longest backtick run inside that file and whose preceding
   line names the work-relative path as `path: <work-id>/…`. Include any
   specification needed to continue as inline captured content plus its
   provenance (repository-relative path in the anchored tree, or a Notion stable
   ref with its captured revision). Determine that stream's current task, next
   owner, and next action by reading its task table directly. Redact secrets from
   every embedded payload; if redaction would make one stream's required section
   incomplete, degrade that stream to an index-only row rather than blocking the
   whole receipt. Produce the external receipt defined in
   [references/output-format.md](references/output-format.md). Each stream's
   receipt section routes continuation to the relevant implementation skill and
   records the current task, exact next owner, exact next action, and a
   capability-level continuation intent describing the work type (never a fixed
   skill name). Inline source/spec payloads are explicit portable receipt data,
   not a reference to ignored local memory.
9. Return every created or materially rewritten path in `generated_files`.
Do not run file sizing; after all artifact writers finish, the PM checks only
eligible work Markdown inside the target `.engineering/` and coordinates any
complete split round.

## Verification

- Every stream under `works/` appears exactly once in the `## Work index` with
  its canonical lifecycle; continuable streams are embedded and `complete`/
  `retiring` streams are index-only.
- Each embedded stream's `state.md` is complete, internally consistent, and links
  `state/working.md`; the latter contains only current-focus summary and fast
  paths.
- Every overview matches its children and canonical status vocabulary.
- Decisions, assumptions, deviations, blockers, review dispositions, evidence,
  promotion, and specification state are preserved per embedded stream.
- Each `## Work stream:` section embeds the raw contents of that stream's
  `state.md`, `state/working.md`, and every continuity-relevant detail file, each
  labelled with its `path: <work-id>/…` line and fenced with a collision-safe
  backtick run, so goal, task table, decisions, reviews, and file status travel
  with it.
- Each embedded stream can rehydrate without access to this `.engineering/` tree:
  its source anchor is destination-reachable, and every embedded work-state file
  and specification is contained in the anchored tree, carried inline, or named
  by a Notion stable ref with its captured revision.
- No secret, credential, absolute host path, path traversal, or symlink escape
  is present in an embedded payload.
- No file outside the resolved work roots was modified; external receipt
  publication is reported separately.

## Completion

Use [references/output-format.md](references/output-format.md). Report the
receipt, the workspace root, the embedded and index-only stream counts, per-stream
updated state paths, classification and decision counts, external and
source-anchor status, per-stream rehydratability, and `generated_files`. Never
label a stream's handover complete when its source anchor is missing. Examples
live in [references/examples.md](references/examples.md).
