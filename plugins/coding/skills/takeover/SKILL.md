---
name: takeover
description: Resume interrupted implementation from persisted handover documents. Use when CONTEXT.md, NOTES.md, and PLAN.md describe valid continuation state; this adapter validates those inputs and delegates the actual continuation to the standard write-code resume workflow.
model: opus
allowed-tools: Read, Glob, Edit, AskUserQuestion, Skill
argument-hint: "[prefix]"
---

# Takeover

Validate a handover bundle, resolve its pending decisions, and resume the
interrupted work by invoking `coding:write-code --resume` exactly once.
`coding:handover` owns creating and updating handover documents;
`coding:write-code` owns the continuation itself.

## Boundaries

- Use for: resuming interrupted implementation from persisted handover
  documents, or picking up another developer's paused task from CONTEXT.md,
  NOTES.md, and PLAN.md.
- Do not use for: creating or updating handover notes (`coding:handover`),
  starting fresh work without a handover bundle (`coding:write-code`), or
  fixing diagnosed failures directly (`coding:fix`).
- Never repair handover documents or implement code in this skill; recording
  resolved decisions (workflow step 3) is the only permitted handover edit.

## Inputs

- **Required**: none — defaults to `CONTEXT.md`, `NOTES.md`, and `PLAN.md` in
  the working directory.
- **Optional**: `[prefix]` — resolves the bundle as `<prefix>-CONTEXT.md`,
  `<prefix>-NOTES.md`, and `<prefix>-PLAN.md`.
- **Prerequisites**: all three handover documents exist and are readable.

## Workflow

1. Resolve the optional prefix and require all three handover documents.
2. Confirm the documents are internally consistent and identify a concrete
   unfinished implementation scope. Reject missing, malformed, contradictory,
   or already-complete handovers with a concise explanation of what is wrong.
3. Scan PLAN.md for unresolved decision markers (`DECISION REQUIRED`, paused
   or blocked task marks). For each one, present the options recorded in the
   document via `AskUserQuestion`, then persist the answers before execution
   so they survive another interruption: append them to PLAN.md's Decision
   Log, clear the resolved markers, fold the chosen approach into the affected
   task descriptions, and keep still-open questions in NOTES.md.
4. Invoke `coding:write-code --resume` once, passing the resolved handover
   location, the recorded decisions, and the original user context.
5. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains
   (for example an unreadable or contradictory bundle the user must resolve),
   then report the blocker instead of looping.

## Verification

- All three handover documents were located and validated before delegation.
- Every resolved decision is recorded in PLAN.md's Decision Log and its marker
  cleared; still-open questions remain in NOTES.md.
- Exactly one `coding:write-code --resume` invocation ran and returned a
  report.

## Completion

Return the `coding:write-code --resume` report unchanged, prefixed with the
resolved handover location and the decisions recorded. For a rejected
handover, state which document failed validation and why, and suggest
`coding:handover` to regenerate it.
