---
name: handover
description: Persist the complete state and current-focus pointers for an active engineering work item, then emit a portable receipt for another workspace. Use when pausing or transferring coding work; this skill records continuity and does not execute the work.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion
argument-hint: "[work-id]"
---

# Work Handover

Refresh the active work item's ignored local memory and emit a portable receipt
that can rehydrate the work elsewhere. `essential:takeover` owns rehydration;
the receipt routes continuation to the relevant implementation skill.

## Boundaries

- Use for pausing or transferring an existing engineering work item.
- Do not perform git history, push, PR, build, test, deployment, review, or
  implementation work.
- Do not create root-level continuation files or assume `.engineering/` is
  committed, copied, or shared between Git worktrees or jj workspaces.
- Do not claim that a receipt is rehydratable when relevant repository changes
  exist only in this working copy. A local path or change ID with no
  destination-reachable carrier is not a portable source anchor.
- Only the main agent/PM may run this workflow because it writes `state/working.md`
  and reconciles work indexes.

## Inputs

- Optional `[work-id]`; otherwise use the active work ID supplied in context.
- Require a repository checkout, a resolvable active work ID, and an external
  continuation anchor: task, issue, PR, or Notion work item. If no anchor is
  writable, emit the receipt in the response for the user to paste there.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Resolve the work root, conventions, naming,
and ownership from that reference before reading or writing state.
A delegated invocation requires an explicit work ID/root; a direct PM run must
resolve an existing active ID. Handover never mints an empty work item.

## Workflow

1. Resolve `.engineering/works/<work-id>/` per the Essential contract. Read
   `state/working.md` first when present, then `state.md`, its linked detail files,
   the four lazy overview files, `review.md`, relevant review areas, evidence,
   and the materialized working specification. From the `state.md` task table,
   determine which tasks are runnable, which are blocked, the current owner, and
   the next action; proceed on that reading, with no separate validation step.
   Treat repository and runtime evidence as authoritative over stale local memory.
   Any implementation detail that root state links is procedure keyed by existing
   task IDs, not plan authority.
2. Gather todos, current revision/bookmark/branch, working-copy status, staged
   and unstaged changes, untracked files, recent commits, and each
   specification's location: inline raw text, a repository-relative path, or a
   Notion reference with its captured revision. Classify changed and planned
   files with the substates in
   [references/document-templates.md](references/document-templates.md).
3. Resolve a portable source anchor before claiming a complete handover. When
   every relevant repository change is already captured by a revision reachable
   through the receipt's remote repository/ref, record it as the remote revision
   to check out. Otherwise consult the user: either pause so `coding:commit` and,
   when authorized, `coding:push-pr` can create a reachable revision, or obtain
   explicit approval to attach a `git format-patch` patch or a `git bundle` ref
   to the external anchor. Record the carrier and its compatible base/result
   revision with plain git; there is no checksum verification. A local staging
   path alone is not an anchor. If no destination-reachable carrier exists,
   return a blocked, non-rehydratable status and do not emit a complete receipt.
4. Identify every material unresolved decision. Consult the user using
   [references/decision-consultation.md](references/decision-consultation.md);
   route durable decision detail to `decisions/<slug>.md` and let the PM
   reconcile `decisions.md`. Record low-impact reversible assumptions in
   `state.md` with evidence and recheck triggers.
5. Generate one UTC ISO-8601 timestamp. Rewrite `state.md` as the complete work
   context: goal, full parent/subtask task table with marked status and evidence,
   lifecycle, success criteria, decisions, dependencies, blockers, review
   dispositions, evidence, durable promotion, specification location, and a
   prominent link to `state/working.md`. If eligible work Markdown requires
   splitting under the shared batch process, keep the original path as overview.
6. Rewrite `state/working.md` to approximately 4,096 bytes through editorial
   discipline: current focus, current status, immediate handback point, and
   fast relative paths only. It is not a plan, history, or complete context.
   Do not mechanically size-gate it.
7. Reconcile existing lazy `proposals.md`, `changes.md`, `decisions.md`, and
   `design.md` overview files from child metadata; never copy child details
   into an overview.
8. Gather the raw contents of `state.md`, `state/working.md`, and every
   continuity-relevant detail file (decisions, changes, design, `state/*.md`
   children, needed evidence) and embed them verbatim in the receipt, each in
   its own fenced block labelled with its work-relative path. Include any
   specification needed to continue as inline raw text, a repository-relative
   path in the anchored tree, or a Notion stable ref with its captured revision.
   Determine the current task, next owner, and next
   action by reading the task table directly. Redact secrets from every embedded
   payload; if redaction would make a required section incomplete, block and ask
   for a safe carrier. Produce the external receipt defined in
   [references/output-format.md](references/output-format.md). The receipt routes
   continuation to the relevant implementation skill and records the current
   task, exact next owner, exact next action, and a capability-level continuation
   intent describing the work type (never a fixed skill name). Inline source/spec
   payloads are explicit portable receipt data, not a reference to ignored local
   memory.
9. Return every created or materially rewritten path in `generated_files`.
Do not run file sizing; after all artifact writers finish, the PM checks only
eligible work Markdown inside the target `.engineering/` and coordinates any
complete split round.

## Verification

- `state.md` is complete, internally consistent, and links `state/working.md`; the
  latter contains only current-focus summary and fast paths.
- Every overview matches its children and canonical status vocabulary.
- Decisions, assumptions, deviations, blockers, review dispositions, evidence,
  promotion, and specification state are preserved.
- The receipt embeds the raw contents of `state.md`, `state/working.md`, and
  every continuity-relevant detail file, each labelled with its work-relative
  path, so goal, task table, decisions, reviews, and file status travel with it.
- The receipt can rehydrate work without access to this `.engineering/` tree:
  its source anchor is destination-reachable, and every embedded work-state file
  and specification is contained in the anchored tree, carried inline, or named
  by a Notion stable ref with its captured revision.
- No secret, credential, absolute host path, path traversal, or symlink escape
  is present in an embedded payload.
- No file outside the resolved work root was modified; external receipt
  publication is reported separately.

## Completion

Use [references/output-format.md](references/output-format.md). Report the
receipt, work ID/root, updated state paths, classification and decision counts,
external and source-anchor status, rehydratability, and `generated_files`. Never
label the handover complete when the source anchor is missing. Examples live in
[references/examples.md](references/examples.md).
