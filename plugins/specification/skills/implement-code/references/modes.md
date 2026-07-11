# Mode Bodies

**When loaded**: After Step 3 mode selection picks one of the seven modes. Read only the section for the resolved mode — sections are mutually exclusive (exactly one runs per invocation).

This file holds the per-mode execution bodies. The mode-selection table itself stays inline in `SKILL.md` (Step 3) so every invocation can decide which mode it's in without loading this file. Only the per-mode bulk lives here.

---

## Mode Semantics (one-line summaries)

- **COMMIT_PLAN**: Execute PLAN.md phases via `coding:write-code` → `coding:review-code` → `coding:commit`, one commit per PLAN phase
- **PI_ITERATE**: Partial implementation exists; dispatch `coding:complete-code` then `coding:fix` then `coding:review-code` then `coding:commit`
- **DRAFT_THEN_ASK**: No plan yet; refuse to code, print pointer to run `specification:plan-code` first, ask user whether to proceed with a lightweight draft
- **AUDIT_AND_COMPLETE**: Dispatch `coding:review-code` first, then `coding:complete-code` + `coding:fix` for gaps, then `coding:commit`
- **VERIFY_ONLY**: Ticket marked done; dispatch `coding:review-code` only, report any drift, no commits
- **FLAG_MISMATCH**: Emit a structured report to the user describing the mismatch and ask for resolution via `AskUserQuestion`; do not code
- **REFUSE**: Decline with a clear message citing stage + matched rule; no dispatch

---

## Step 8 — Per-Mode Child Chains

Select the child chain from the mode:

### COMMIT_PLAN

Per PLAN phase:

1. `coding:write-code` — TDD-complete the phase
2. `coding:review-code` — MUST pass before commit
3. `coding:commit` — atomic commit for the phase

### PI_ITERATE

1. `coding:complete-code` — finish TODOs
2. `coding:fix` — fix broken tests/lint
3. `coding:review-code`
4. `coding:commit`

### DRAFT_THEN_ASK

1. Print pointer to `specification:plan-code`
2. If user opts into lightweight draft: `coding:draft-code` only, then `coding:handover`

### AUDIT_AND_COMPLETE

1. `coding:review-code` (baseline)
2. `coding:complete-code` for gaps
3. `coding:fix`
4. `coding:review-code` (final)
5. `coding:commit`

### VERIFY_ONLY

1. `coding:review-code` — no commits

### FLAG_MISMATCH / REFUSE

No children dispatched; skip to Step 13.

Update TodoWrite with one todo per dispatched child.

---

## Deviation Policy Block (verbatim, embedded in every `coding:*` dispatch)

```markdown
## Deviation Policy

The Working Draft / AI Coder Prompt / PLAN phase you are implementing is a DRAFT and may contain errors. If you encounter any of the following while implementing, DEVIATE and proceed, appending an entry to `<repo>/DEVIATIONS.md`:

- Missing or wrong dependency (package not installed, wrong version, replaced)
- Wrong integration assumption (API signature, event name, schema field, import path, module layout differs from what the draft assumes)
- Standard violation (draft conflicts with `plugins/<plugin>/constitution/standards/`)
- Architectural conflict (draft's structure doesn't fit the repo's existing pattern)
- Symbol the draft references no longer exists

SKIP logging for trivial differences:

- Auto-added JSDoc the draft omitted
- Inferred type annotations the draft left implicit
- Lint / formatter-driven whitespace or import ordering
- Casing adjustments to match local conventions
- Obvious prose typos in the draft

**DEVIATIONS.md entry format** (append, never rewrite existing entries):

    ### D-<N>: <short title>
    - **When**: <step name / commit label>
    - **Draft said**: <one-line summary>
    - **What I did instead**: <one-line summary>
    - **Reason**: missing-dep | wrong-integration | standard-violation | arch-conflict | stale-symbol
    - **Impact on spec**: none | surface-change | behavior-change
    - **Severity**: minor | major | blocking

DO NOT refuse the task over a deviation. DO NOT ask the user mid-implementation for trivial choices. Record and proceed.
```

---

## Trailing DEVIATIONS Commit (Step 8)

After the last code commit, dispatch one extra `coding:commit` scoped to `DEVIATIONS.md` with message `chore(deviations): log draft departures for <ticket.slug>`.

**Skip** this trailing commit when any of the following hold:

- The file ended header-only (no `D-N` entries appended)
- Mode is `VERIFY_ONLY` or `DRAFT_THEN_ASK` (no commits land)
- `--dry-run` is set
