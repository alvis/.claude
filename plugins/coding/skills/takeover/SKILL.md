---
name: takeover
description: Resume interrupted implementation from persisted handover documents. Use when CONTEXT.md, NOTES.md, and PLAN.md describe valid continuation state; this adapter validates those inputs and delegates the actual continuation to the standard write-code resume workflow.
model: opus
allowed-tools: Read, Glob, Skill
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

After validation succeeds, pass the resolved handover location and original user
context to the resume invocation. Return its report unchanged.
