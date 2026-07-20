---
name: takeover
description: Rehydrate paused coding work from a portable handover receipt, authoritative repository revision, and Notion specification into a workspace-local engineering work root. Use for continuation in a new Git worktree or jj workspace; invoke coding:write-code --resume after validation.
model: opus
allowed-tools: Read, Glob, Edit, Write, Bash, AskUserQuestion, Skill
argument-hint: "<receipt-or-anchor> [--revalidate]"
---

# Takeover

Rehydrate ignored workspace-local work memory from portable authoritative
sources, resolve pending decisions, and invoke `coding:write-code --resume`
exactly once.

## Boundaries

- Use for continuing a handed-over engineering work item in this or another
  Git worktree or jj workspace.
- Do not assume `.engineering/` is versioned, copied, or synchronized between
  workspaces. Existing local state is evidence to validate, not the transfer
  mechanism.
- Do not implement code here. Apart from rehydrated work artifacts and resolved
  decisions, implementation belongs to `coding:write-code`.

## Inputs

- Required: a portable receipt or an external task, issue, PR, or Notion anchor
  containing it.
- Optional: `--revalidate` forces revalidation even when receipt sources match.
- Require repository access and the authoritative Notion specification named
  by the receipt.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Resolve the current workspace and work
root from that reference before rehydrating anything.
The receipt supplies the work ID; never mint a replacement identity.

## Workflow

1. Parse and validate the receipt schema from `coding:handover`: repository
   identity, revision, work ID, external anchor, goal/status, authoritative spec
   IDs and revisions, durable-doc refs, unresolved decisions, validation/sync
   state, and recheck triggers. Reject missing, contradictory, or completed
   receipts with a precise reason.
2. Confirm this checkout matches the repository identity and resolve
   `.engineering/work/<work-id>/`. Never copy `.engineering/notion/` or another
   workspace's work directory. Use the specification sync owner to materialize
   only the required spec into this work root; preserve notion-sync-owned names.
3. Compare repository revision, spec revision/hash, external anchor, durable
   docs, dependencies, configuration/schema, and explicit recheck triggers.
   `--revalidate`, any mismatch, or missing evidence yields `revalidated`;
   exact matching authoritative sources yields `receipt_verified`. Record every
   contradiction before execution.
4. Reconstruct or refresh `state.md` from the receipt and authoritative sources,
   including the full goal, plan/lifecycle, criteria, decisions, dependencies,
   blockers, reviews, evidence, promotion, sync, and revalidation state. Link
   `working.md`. Refresh `working.md` with only current focus, handback point,
   and fast paths; only the main agent/PM may perform this step.
5. Resolve decisions that block the next action using `AskUserQuestion`. Store
   detail in `decisions/<slug>.md`, reconcile `decisions.md`, and update the
   affected state tasks. Leave deferred questions explicit with owner/deadline.
6. Invoke `coding:write-code --resume` once with the resolved work ID/root,
   receipt verdict, contradictions, decisions, and original user context.
7. Return every created or materially rewritten path in `generated_files`.
Do not run file sizing; the PM checks only eligible work Markdown inside the
target `.engineering/`.

## Verification

- Rehydration used authoritative sources, not copied ignored state.
- `state.md` is complete and links the PM-owned, current-focus-only
  `working.md`; subagents read them in that order.
- Every resolved decision is durable in the work decision artifacts.
- Exactly one `coding:write-code --resume` invocation returned a report.

## Completion

Prefix the unchanged `coding:write-code --resume` report with the work root,
receipt source, `receipt_verified|revalidated` verdict, contradictions,
decisions, materialized spec paths, and `generated_files`. On rejection, name
the invalid receipt field or source and recommend `coding:handover` only when a
fresh receipt can repair it.
