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
the receipt identifies whether `specification:implement-code` or
`coding:write-code` owns continued implementation.

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
writes and report the missing contract. Resolve the work root, schemas, naming,
and ownership from that reference before reading or writing state.
A delegated invocation requires an explicit work ID/root; a direct PM run must
resolve an existing active ID. Handover never mints an empty work item.

## Workflow

1. Resolve `.engineering/works/<work-id>/` per the Essential contract. Read
   `state/working.md` first when present, then `state.md`, its linked detail files,
   the four lazy overview files, `review.md`, relevant review areas, evidence,
   and the materialized working specification. Treat repository and runtime
   evidence as authoritative over stale local memory. Run
   `validate-engineering-state validate --state <state.md>`. Refuse
   `migration_required` or invalid state rather than inventing graph identity;
   require `plan_source: state.md` and retain its plan digest/hash kind, parent/subtask graphs,
   task counts, runnable/blocked IDs, and invalidated closure. If root state
   explicitly links implementation detail, require it to be keyed by existing
   IDs and to omit IDs, edges, requiredness, targets, and acceptance mappings
   as definitions; it is procedure, not plan authority.
2. Gather todos, current revision/bookmark/branch, working-copy status, staged
   and unstaged changes, untracked files, recent commits, validation results,
   each specification's declared dual-hash model, paired
   `transport_manifest_hash`/`contract_digest`, Notion source identity/revision
   and logical transport profile, durable-doc promotion state, and pending sync
   or revalidation obligations. Never substitute a generic `hash` field. For a
   Notion source, classify the exact sync relationship and discard the origin
   transport root. The portable receipt retains its stable Notion ref, captured
   revision, paired dual hashes, logical profile, and at most one contained
   repository-relative suggested root; it must never contain an origin absolute
   path, worktree-specific path, or a claim that the suggestion is validated for
   the destination.

   Preserve the sync owner's exact operational `status`, relationship
   `classification`, and `next_action` as three distinct fields; never map or
   invent a classification. A fresh remote ref is sufficient without B/L only
   when status is `success`, classification is exactly `initial`, `unchanged`,
   `metadata_only`, or `converged`, `next_action` is `none`, and evidence proves
   there is no authored or otherwise pending local work. Require portable B/L
   for `local_only`, `remote_only`, `structural_change`, `concurrent`,
   `baseline_required`, or `materialization_conflict`, for operational
   `partial`/`blocked`, and whenever `next_action` is not `none`. Construct it
   only with the dependency-free canonical helper and format in
   [references/blr-transfer-format.md](references/blr-transfer-format.md): exact
   immutable B receipt/bytes and authored L bytes, embedded
   `spec-hash-input-v1` manifests and observed revisions, per-unit exact hashes,
   and independently recomputed paired dual hashes. Record the helper's returned
   outer package checksum in the carrier. Publish the canonical JSON package to
   a retrievable attachment or embed its exact bytes in a response-only receipt.
   If either B/L evidence is unavailable (as it is for `baseline_required`),
   ambiguous, secret-bearing, or cannot be carried portably, return blocked;
   never fabricate B or let a Notion ref erase unsynced authored work or a
   three-way merge base.
   Classify changed and planned files with the substates in
   [references/document-templates.md](references/document-templates.md).
3. Resolve a portable source anchor before claiming a complete handover. When
   every relevant repository change is already captured by an exact
   revision, verify that revision is reachable through the receipt's remote
   repository/ref and record it as `remote_revision`. Otherwise consult the
   user: either pause so `coding:commit` and, when authorized, `coding:push-pr`
   can create a reachable revision, or obtain explicit approval to create a
   patch/bundle payload and attach it to the external anchor. Record the
   carrier type, format, encoding, exactly one of complete content or a
   retrievable locator, checksum, compatible base/result identity, and
   declarative application contract. A local staging path alone is not an
   anchor. A response-only transfer is valid only when it embeds the complete
   approved source payload, task-state snapshot, every required linked
   work-artifact carrier, every inline specification, every required Notion
   B/L transfer, and their checksums. If none of these carriers exists, return a
   blocked, non-rehydratable status and do not emit a complete receipt.
4. Identify every material unresolved decision. Consult the user using
   [references/decision-consultation.md](references/decision-consultation.md);
   route durable decision detail to `decisions/<slug>.md` and let the PM
   reconcile `decisions.md`. Record low-impact reversible assumptions in
   `state.md` with evidence and recheck triggers.
5. Generate one UTC ISO-8601 timestamp. Rewrite `state.md` as the complete
   `engineering-work-state/v1` context: goal, canonical plan pointer/digest/hash
   kind, full parent/subtask DAG, marked task status and evidence, lifecycle,
   success criteria, decisions,
   dependencies, blockers, review dispositions, evidence, durable promotion,
   Notion sync, revalidation, and a prominent link to `state/working.md`. If eligible
   work Markdown requires splitting under the shared batch process, keep the
   original path as overview.
6. Rewrite `state/working.md` to approximately 4,096 bytes through editorial
   discipline: current focus, current status, immediate handback point, and
   fast relative paths only. It is not a plan, history, or complete context.
   Do not mechanically size-gate it.
7. Reconcile existing lazy `proposals.md`, `changes.md`, `decisions.md`, and
   `design.md` overview files from child metadata; never copy child details
   into an overview.
8. Validate the reconciled state again with Essential. Require `status: valid`,
   stored/computed plan-digest equality, and consistent task/lifecycle
   roll-ups. Invoke only
   `validate-engineering-state pack --state <state.md>` and preserve its exact
   canonical stdout bytes as the portable
   `engineering-work-state+json/v1` snapshot defined in
   [references/document-templates.md](references/document-templates.md).
   Validate those exact bytes with
   `validate-engineering-state validate-snapshot --snapshot <file|->`; do not
   synthesize or parse a competing snapshot format. Use only its
   `execution_ledger`, `active_task_ids`, `next_owner`, and `next_action` report
   fields to select receipt continuation. `current_task_id` is an applicable
   executable leaf whose ledger status is `working`, `failed`, or `blocked`; a
   working ID must also appear in working-only `active_task_ids`. Use `none`
   only when the ledger contains no applicable executable leaf in any of those
   three statuses. Copy next owner/action exactly. The snapshot guarantees
   only the complete hierarchical task definitions/graph, task
   status/owner/evidence execution ledger, plan identity, and exact next owner
   and action. The v3 receipt plus explicit checksum-bound linked work-artifact
   carriers separately preserve the full goal/acceptance narrative, decisions
   and assumptions, blockers/risks, review dispositions, validation evidence,
   sync/revalidation, and file status needed without the origin
   `.engineering/`. Reject any missing carrier; never claim the task snapshot
   contains that narrative. Validate ownership/status, redact secrets, and
   SHA-256 the exact canonical JSON bytes. Store the snapshot at a retrievable
   external locator or inline it in the receipt; an ignored local path is never
   a portable snapshot carrier. Produce the external receipt defined in
   [references/output-format.md](references/output-format.md). The receipt
   identifies the workflow owner and authoritative specification/source
   carriers needed to rehydrate and repeats `plan_source: state.md`,
   bare `plan_digest`, plan hash kind, current full `task_id`, exact next owner,
   and exact next action. Any explicitly linked non-authoritative
   implementation detail must be anchored or carried as a checksum-bound work
   artifact keyed by existing IDs; the receipt never claims to transfer ignored local
   memory. Inline source/spec payloads are explicit portable receipt data, not
   a reference to that memory. A Notion transport profile is logical
   configuration only: takeover must map it to an exact destination-local root
   and validate that root before fetching. A required B/L transfer is canonical
   JSON evidence produced by the bundled handover helper, not an origin mirror
   path.
9. Return every created or materially rewritten path in `generated_files`.
Do not run file sizing; after all artifact writers finish, the PM checks only
eligible work Markdown inside the target `.engineering/` and coordinates any
complete split round.

## Verification

- `state.md` is complete, internally consistent, and links `state/working.md`; the
  latter contains only current-focus summary and fast paths.
- Every overview matches its children and canonical status vocabulary.
- Decisions, assumptions, deviations, blockers, review dispositions, evidence,
  promotion, and sync/revalidation state are preserved.
- Essential validates the final state, and its `pack` plus
  `validate-snapshot` operations are the sole state-snapshot producer and
  validator. The snapshot preserves task IDs, DAG edges, statuses, plan
  digest, evidence, owners, and exact next action.
- Goal, decisions, reviews, sync, file-status, and other narrative continuity
  live in explicit v3 receipt fields or separately checksum-bound linked
  work-artifact carriers, not in the Essential snapshot.
- The receipt can rehydrate work without access to this `.engineering/` tree:
  its source anchor, complete task-state snapshot, and all required narrative
  work-artifact carriers are destination-reachable or
  contain the complete approved payloads, and every checksum/revision was
  verified. Every `local` specification path is repository-relative,
   path-contained, and present in the anchored result; ignored work-local
   specifications use an inline carrier or a Notion carrier that satisfies the
   exact no-B/L predicate or includes the complete portable B/L transfer.
- No secret, credential, absolute host path, path traversal, or symlink escape
  is present in a payload or application field.
- A Notion carrier contains its logical profile plus stable ref, captured
  revision, paired remote dual hashes, the exact sync-owner
  `status`/`classification`/`next_action` triplet, and at most a contained
  repository-relative suggested root. B/L absence satisfies the sole clean-state
  predicate above; every other state contains a helper-validated portable B/L
  package or blocks. No carrier contains an origin-workspace transport path.
- No file outside the resolved work root was modified; external receipt
  publication is reported separately.

## Completion

Use [references/output-format.md](references/output-format.md). Report the
receipt, work ID/root, updated state paths, classification and decision counts,
external and source-anchor status, rehydratability, and `generated_files`. Never
label the handover complete when the source anchor is missing. Examples live in
[references/examples.md](references/examples.md).
