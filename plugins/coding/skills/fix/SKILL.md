---
name: fix
description: Fix diagnosed incorrect behavior, failed tests, type errors, lint failures, or broken CI. Use when a concrete failure can be reproduced or review findings identify a defect; route new functionality to write-code and green structural cleanup to refactor.
model: opus
context: fork
allowed-tools: Edit, MultiEdit, Read, Write, Grep, Glob, Bash, Task, TodoWrite
argument-hint: "[specifier] [--area=AREA] [--note=...] [--plan=PATH]"
---

# Fix Code Issues

Diagnose and repair concrete failures — failing tests, type errors, lint
failures, broken CI, review findings — restoring green without adding
behavior. `coding:write-code` owns new functionality; `coding:refactor` owns
structural cleanup of working code.

<IMPORTANT>
Coherence Mandate: every edit must produce one continuous, deliberate work —
rewrite over restructure, restructure over integrate, never append. A fix is
not a patch laid on top of the broken region; it is the smallest rewrite that
lets the corrected logic sit in place as if the bug had never been there — no
visible patch seams, no `// fixed:` markers, no parallel "v2" helpers, no
defensive wrapper retained "just in case" the original path comes back.
</IMPORTANT>

## Boundaries

- Use for: reproducible failures (tests, types, lint, CI) and defects
  identified by review findings, including incorrect test behavior, fixtures,
  and mocks.
- Do not use for: new features (`coding:write-code`), refactoring working
  code (`coding:refactor`), architecture changes, or fixes requiring external
  service changes. Reject when all checks pass and no defect is identified,
  or when the requested change would break existing functionality.

## Inputs

- **Required**: a failure to fix — an error message, failing check, review
  finding, or a specifier (file, directory, or pattern) to diagnose.
- **Optional**: `--area=test|lint|type|review|impl|fixtures|refactor` to skip
  auto-detection; `--note=...` for focus guidance; `--plan=PATH` to pin the
  plan contract for post-review fixes; `--from-composite` when invoked from a
  composite workflow.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Resolve the active work root first.
When delegated, read `working.md`, then `state.md` and only relevant linked
review/spec/design paths; never write PM-owned `working.md` or reconcile work
overview files.
A direct PM run resolves or mints the work ID by the contract; a delegated run
requires the explicit work ID/root.

## Standards

For test correction (step 3) apply `testing/scan`, `typescript/scan`, and
`documentation/scan`; when a specific rule violation is detected, load its
fix guidance from `testing/rules/<rule-id>.md`. For fixture optimization
(step 4) apply the `universal`, `typescript`, `function`, `documentation`,
and `testing` write standards.

## Workflow

1. **Diagnose.** Parse the specifier and flags. Without `--area`, auto-detect
   by running tests, the type checker, and the linter, prioritizing tests >
   types > lint. Map the area to its entry step — `test` → step 3, `fixtures`
   → step 4, `impl` → step 2, `refactor` → step 5 — and with multiple areas
   start from the earliest and run all relevant steps. Collect error
   messages and map each to its code location; for broader project context
   (handover docs, review findings, planning notes) see
   [references/context-discovery.md](references/context-discovery.md). When
   this run follows a `/coding:review-code`, pin the plan contract per
   [references/plan-context.md](references/plan-context.md) so the follow-up
   review validates against the identical plan.
2. **Plan.** Read the affected files and their test descriptions; determine
   expected behavior from tests and state-linked work/durable design and
   specification files; decide
   whether each issue is source-code logic or test implementation, asking the
   user when expected behavior is ambiguous. List the changes needed, ordered
   by dependency.
3. **Fix tests.** Fix incorrect test behavior and logic — never modify a test
   just to make it pass — plus standards violations, imports, and references.
   For unused-code errors, check state-linked design and work docs first: if the code
   is planned but unimplemented, use the `throw new Error('IMPLEMENTATION:
   ...')` pattern; remove only genuinely unnecessary code. When more than 25
   files are affected, batch at most 10 test files per subagent and dispatch
   batches in parallel (per the constitution's delegation guidance); the
   bound keeps each report reviewable and a failed batch cheap to retry.
   Re-run checks after each fix and address newly surfaced errors.
4. **Optimize fixtures** (skip when no fixtures or mocks exist). Fix
   incorrect fixture definitions and mock behavior, type-safety issues, and
   organization problems; keep fixture data realistic and valid; run tests to
   confirm they still pass.

   <IMPORTANT>
   In steps 3-4, modify only test files, mock files, fixtures, and test
   support files — never the source code under test.
   </IMPORTANT>

5. **Validate.** Run the full test suite, linter, and type checker across the
   affected scope. When a check fails, fix the cause and re-run that check;
   repeat until every check passes or a concrete blocker remains, then report
   the blocker instead of looping. For each failure that occurred, record its
   root cause, the systemic cause that allowed it, the assumption that proved
   wrong, and how to prevent that class of error.

## Verification

- The originally reported failure no longer reproduces.
- Tests, type check, and lint pass across the affected scope with no
  regressions.
- Edits are confined to the diagnosed defect: no new features, no unrelated
  restructuring, and for test-area fixes no source-under-test modifications.

## Completion

Report the area (detected or specified), issues found and fixed, files
modified, the root-cause classification
(`source_code_logic` / `test_implementation` / `requirements_unclear`) with
the reasoning behind it, per-issue file:line entries with what changed,
fixture optimizations when step 4 ran, and validation results
(tests/types/lint). Suggest next steps (refactor, commit) only when relevant.
When the run followed a review, include the keys the follow-up review
consumes:

<report>

```yaml
plan_source: <absolute path or none_found>
review_rerun: /coding:review-code <scope> --plan=<plan_source> # omit when plan_source is none_found
```

</report>

Return every created or materially rewritten path as `generated_files` to the
PM. Do not run per-file sizing; the PM performs the single final Markdown batch
after all artifact writers finish.
