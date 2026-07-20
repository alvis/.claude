---
name: handover
description: Persist the complete state and current-focus pointers for an active engineering work item, then emit a portable receipt for another workspace. Use when pausing or transferring coding work; this skill records continuity and does not execute the work.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash, TodoRead, AskUserQuestion
argument-hint: "[work-id]"
---

# Work Handover

Refresh the active work item's ignored local memory and emit a portable receipt
that can rehydrate the work elsewhere. `coding:takeover` owns rehydration;
`coding:write-code` owns continued implementation.

## Boundaries

- Use for pausing or transferring an existing engineering work item.
- Do not perform git history, push, PR, build, test, deployment, review, or
  implementation work.
- Do not create root-level continuation files or assume `.engineering/` is
  committed, copied, or shared between Git worktrees or jj workspaces.
- Only the main agent/PM may run this workflow because it writes `working.md`
  and reconciles work indexes.

## Inputs

- Optional `[work-id]`; otherwise use the active work ID supplied in context.
- Require a repository checkout, a resolvable active work ID, and an external
  continuation anchor: task, issue, PR, or Notion work item. If no anchor is
  writable, emit the receipt in the response for the user to paste there.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Resolve the work root, schemas, naming,
and ownership from that reference before reading or writing state.
A delegated invocation requires an explicit work ID/root; a direct PM run must
resolve an existing active ID. Handover never mints an empty work item.

## Workflow

1. Resolve `.engineering/work/<work-id>/` per the Essential contract. Read
   `working.md` first when present, then `state.md`, its linked detail files,
   the four lazy overview files, `review.md`, relevant review areas, evidence,
   and the materialized working specification. Treat repository and runtime
   evidence as authoritative over stale local memory.
2. Gather todos, current revision/bookmark/branch, working-copy status, staged
   and unstaged changes, untracked files, recent commits, validation results,
   Notion source identity/revision, durable-doc promotion state, and pending
   sync or revalidation obligations. Classify changed and planned files with
   the substates in [references/document-templates.md](references/document-templates.md).
3. Identify every material unresolved decision. Consult the user using
   [references/decision-consultation.md](references/decision-consultation.md);
   route durable decision detail to `decisions/<slug>.md` and let the PM
   reconcile `decisions.md`. Record low-impact reversible assumptions in
   `state.md` with evidence and recheck triggers.
4. Generate one UTC ISO-8601 timestamp. Rewrite `state.md` as the complete
   work context: goal, full plan and lifecycle, success criteria, decisions,
   dependencies, blockers, review dispositions, evidence, durable promotion,
   Notion sync, revalidation, and a prominent link to `working.md`. Split only
   under the shared final batch process; keep the original path as overview.
5. Rewrite `working.md` to approximately 4,096 bytes through editorial
   discipline: current focus, current status, immediate handback point, and
   fast relative paths only. It is not a plan, history, or complete context.
   Do not mechanically size-gate it.
6. Reconcile existing lazy `proposals.md`, `changes.md`, `decisions.md`, and
   `design.md` overview files from child metadata; never copy child details
   into an overview. Produce the external receipt defined in
   [references/output-format.md](references/output-format.md). The receipt
   identifies authoritative sources needed to rehydrate; it never embeds or
   claims to transfer ignored local memory.
7. Return every created or materially rewritten path in `generated_files`.
   Do not run per-file sizing or `wc -c`; the PM runs one final batch after all
   artifact writers finish and coordinates any complete split round.

## Verification

- `state.md` is complete, internally consistent, and links `working.md`; the
  latter contains only current-focus summary and fast paths.
- Every overview matches its children and canonical status vocabulary.
- Decisions, assumptions, deviations, blockers, review dispositions, evidence,
  promotion, and sync/revalidation state are preserved.
- The receipt can rehydrate work without access to this `.engineering/` tree.
- No file outside the resolved work root was modified; external receipt
  publication is reported separately.

## Completion

Use [references/output-format.md](references/output-format.md). Report the
receipt, work ID/root, updated state paths, classification and decision counts,
external anchor status, and `generated_files`. Examples live in
[references/examples.md](references/examples.md).
