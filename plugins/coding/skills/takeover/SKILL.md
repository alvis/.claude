---
name: takeover
description: Resume paused coding work from CONTEXT.md, NOTES.md, and PLAN.md. Use for takeover, continuing yesterday's coding work, resuming a continuation bundle, or --refresh; trust recorded assumptions for 24 hours, revalidate older state, and invoke coding:write-code --resume. For saving current state, use the session-persistence workflow.
model: opus
allowed-tools: Read, Glob, Edit, Bash, AskUserQuestion, Skill
argument-hint: "[prefix] [--refresh]"
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
  `<prefix>-NOTES.md`, and `<prefix>-PLAN.md`; `--refresh` forces assumption
  revalidation regardless of bundle age.
- **Prerequisites**: all three handover documents exist and are readable.

## Workflow

1. Resolve the optional prefix and require all three handover documents.
2. Confirm the documents are structurally valid and internally consistent, and
   identify a concrete unfinished implementation scope. This check always runs;
   reject missing, malformed, contradictory, or already-complete handovers with
   a concise explanation.
3. Apply the freshness gate to the common ISO 8601 timestamp written as
   CONTEXT.md and NOTES.md `Last Updated` plus PLAN.md `Updated`:
   Parse those document fields and compare them with the current UTC time; do
   not substitute filesystem modification time.
   - When those three timestamps match and are no more than 24 hours old, and
     `--refresh` is absent, treat every recorded assumption as still valid and
     skip repository assumption revalidation.
   - When the bundle is older than 24 hours, timestamps are missing or
     inconsistent, or `--refresh` is present, revalidate only assumptions that
     may drift: branch or baseline identity, dependency/API versions,
     configuration and schema state, external references, and explicit recheck
     triggers. Record contradictions before execution.
   - A contradiction discovered naturally during resumed work overrides the
     trust window and follows the normal deviation or pending-decision path.
4. Scan PLAN.md for unresolved decision markers (`DECISION REQUIRED`, paused
   or blocked task marks). For each one, present the options recorded in the
   document via `AskUserQuestion`, then persist the answers before execution
   so they survive another interruption: append them to PLAN.md's Decision
   Log, clear the resolved markers, fold the chosen approach into the affected
   task descriptions, and keep still-open questions in NOTES.md.
5. Invoke `coding:write-code --resume` once, passing the resolved handover
   location, freshness verdict, revalidated contradictions if any, recorded
   decisions, and the original user context.
6. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains
   (for example an unreadable or contradictory bundle the user must resolve),
   then report the blocker instead of looping.

## Verification

- All three handover documents were located and validated before delegation.
- The freshness gate reports `trusted_24h`, `revalidated`, or `forced_refresh`;
  `trusted_24h` performed no repository assumption revalidation.
- Every resolved decision is recorded in PLAN.md's Decision Log and its marker
  cleared; still-open questions remain in NOTES.md.
- Exactly one `coding:write-code --resume` invocation ran and returned a
  report.

## Completion

Return the `coding:write-code --resume` report unchanged, prefixed with the
resolved handover location, freshness verdict, revalidated contradictions, and
the decisions recorded. For a rejected
handover, state which document failed validation and why, and suggest
`coding:handover` to regenerate it.
