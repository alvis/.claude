---
name: takeover
description: Resume interrupted implementation from persisted handover documents. Use when CONTEXT.md, NOTES.md, and PLAN.md describe valid continuation state; this adapter validates those inputs and delegates the actual continuation to the standard write-code resume workflow.
model: opus
allowed-tools: Read, Glob, Edit, AskUserQuestion, Skill
argument-hint: "[prefix]"
---

# Takeover

Validate the handover bundle, then invoke `coding:write-code --resume` exactly once.

## Validation

1. Resolve the optional prefix and require `CONTEXT.md`, `NOTES.md`, and `PLAN.md`.
2. Confirm the documents are readable, internally consistent, and identify a
   concrete unfinished implementation scope.
3. Reject missing, malformed, contradictory, or already-complete handovers with a
   concise explanation. Do not repair the documents or implement work directly.

## Pending decisions

After validation, scan PLAN.md for unresolved decision markers (`DECISION
REQUIRED`, paused or blocked task marks). If any exist:

1. Present each decision to the user via `AskUserQuestion`, offering the options
   recorded in the document.
2. Persist the answers before execution begins, so the decisions survive another
   interruption: append them to PLAN.md's Decision Log, clear the resolved
   markers, fold the chosen approach into the affected task descriptions, and
   keep still-open questions in NOTES.md. Recording decisions this way is the
   only permitted handover edit.
3. Include the recorded decisions in the context passed to the resume
   invocation.

## Delegation

Pass the resolved handover location, recorded decisions, and original user
context to a single `coding:write-code --resume` invocation. Return its report
unchanged.
