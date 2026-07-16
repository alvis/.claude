---
name: review-code
description: Review semantic correctness, security, test intent, documentation, sibling consistency, and alignment with the implementation plan. Use after code changes or for explicit review requests; report findings without editing code and leave mechanical standards enforcement to lint.
model: opus
context: fork
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion
argument-hint: "[specifier] [--area=test|documentation|code-quality|security|style|all] [--out=reviews]"
---

# Review Code

Orchestrates a comprehensive read-only review of the specified code, writing
one Markdown report per area under `<out>/` plus an index. It never modifies
code: remediation belongs to `coding:fix`, and mechanical standards
enforcement belongs to `coding:lint` (see
[references/routing.md](references/routing.md)). Every reviewer applies the
five mandates in [references/mandates.md](references/mandates.md) — plan
adherence, non-mechanical redundancy, sibling consistency, zero tolerance for
semantic error, and delegating mechanical checks to tooling.

## Boundaries

- Use for: post-implementation review, explicit review requests, PR audits,
  and pre-merge checks across the areas test, documentation, code-quality,
  security, and style.
- Do not use for: fixing issues (`coding:fix`), running builds or
  deployments, deployment/infrastructure reviews, or reviewing external
  dependencies and node_modules.
- Reject when: asked to modify code, or the specifier resolves exclusively to
  binary or non-code files.

## Inputs

- **Required**: none — an omitted specifier auto-detects scope per
  [references/specifier-resolution.md](references/specifier-resolution.md).
- **Optional**: `[specifier]` — file, directory, glob, package name, PR
  number, or git range;
  `--area=test|documentation|code-quality|security|style|all` (default all);
  `--out=<dir>` — report directory relative to the project root (default
  `reviews/`); `--explain` — additionally generate a change-comprehension
  artifact and quiz from actual code paths after the independent review.
- **Prerequisites**: a repository checkout; lint and `tsc` are assumed to run
  in the pipeline, so reviewers skip everything tooling already enforces.

## Output contract

<report>

- One Markdown file per area under `<out>/`, conforming exactly to
  [references/review.template.md](references/review.template.md) (frontmatter,
  canonical verdict line, issue blocks, fixed-issue convention, Pending
  Decisions lifecycle), plus a `<out>/README.md` index listing every area file
  with its verdict.
- Area files and ID prefixes:

  | Prefix | File | Area |
  |--------|------|------|
  | `SEC`  | `<out>/SECURITY.md`    | security |
  | `QUAL` | `<out>/QUALITY.md`     | code quality |
  | `TEST` | `<out>/TESTING.md`     | tests / coverage |
  | `DOCS` | `<out>/DOCS.md`        | documentation |
  | `STYL` | `<out>/STYLE.md`       | style / lint / naming |
  | `CORR` | `<out>/CORRECTNESS.md` | correctness / semantics |

- Priorities: P0 blocker (must fix before merge), P1 high (correctness bug,
  unjustified plan drift), P2 medium (maintainability), P3 low (polish).
- Issue IDs are `<PREFIX>-P<n>-<seq>`, sequential per priority within the
  area file and stable across re-runs for the same finding.
- Each issue's `Solution` is direction, not a full patch — enough for a
  downstream `coding:fix` agent to act.
- With `--explain`, `<out>/CHANGE_EXPLAINER.md` follows
  [references/explainer.md](references/explainer.md); it teaches the integrated
  behavior and does not change the review verdict.

</report>

## Workflow

1. Resolve the specifier into discovered files and per-area file lists, and
   select the areas to review, per
   [references/specifier-resolution.md](references/specifier-resolution.md).
2. Pre-pass mechanical scan: run
   `plugins/coding/scripts/pyrun.sh plugins/coding/scripts/scan_potential_violations.py <discovered-files> --category all --before 5 --after 10`
   and capture stdout. The `pyrun.sh` wrapper resolves Python 3.13+ and
   auto-heals via `coding:sync-tool` when none is found, so the pre-pass
   effectively always runs — never skip it, and surface a hard install
   failure loudly instead of swallowing it. Slice the output per the category
   routing in [references/dispatch.md](references/dispatch.md); candidates
   are advisory only.
3. Dispatch one read-only subagent per selected area via the Task tool,
   following the per-area contracts, prompt hygiene, and re-run logic in
   [references/dispatch.md](references/dispatch.md). Delegation follows
   [delegation.md](../../../governance/constitution/references/delegation.md)
   with these skill-specific bounds: dispatch all selected areas in parallel
   in a single message (at most 6 area files, so one agent per area keeps
   each report reviewable), and each agent returns a short completion message
   — path, open-issue counts per priority, `context_level` — instead of the
   findings themselves.
4. Collect completion messages and verify each expected area file exists at
   its target path and starts with the canonical verdict line per
   [references/review.template.md](references/review.template.md); surface
   structural problems rather than silently aggregating. Compute aggregate
   counts per priority from the verdict lines, add a short systemic-pattern
   addendum (recurring issues, root causes, process gaps), determine overall
   status — any open P0: FAIL; P1 but no P0: REQUIRES_CHANGES; only P2/P3:
   PASS_WITH_SUGGESTIONS; all areas PASS: PASS — and rewrite `<out>/README.md`
   entirely from the current area files (per-area verdict rows, timestamp,
   aggregate counts, systemic addendum, overall status).
5. When `--explain` is present, load
   [references/explainer.md](references/explainer.md) and generate
   `<out>/CHANGE_EXPLAINER.md` from the final diff, relevant pre-existing code
   paths, plans/specifications, implementation notes, deviations, and review
   reports. Keep the explainer evidence-backed and the quiz about behavior,
   invariants, failure modes, and integration—not file-name trivia.
6. Render the final summary in the mode-appropriate format (CI vs
   interactive) per [references/output-formats.md](references/output-formats.md).
7. When a check in the verification below fails — a missing or malformed area
   file, a failed agent — fix the cause (typically re-dispatching only that
   area) and re-run that check. Repeat until every check passes or a concrete
   blocker remains, then report the blocker instead of looping.

## Verification

- Every selected area file exists under `<out>/`, conforms to
  [references/review.template.md](references/review.template.md), and opens
  with a canonical verdict line.
- `<out>/README.md` was rewritten with per-area verdicts, aggregate priority
  counts, and the overall status.
- No code file was modified by the review.
- With `--explain`, `CHANGE_EXPLAINER.md` cites actual code and context paths,
  distinguishes pre-existing behavior from the change, and contains a separate
  answer key for its comprehension quiz.

## Completion

Report the per-area file listing (one line per area with its verdict),
aggregate counts per priority, the overall status, and the path to
`<out>/README.md`; include the explainer path when requested. Detailed findings
live in the area files, not the console summary. For invocation examples —
single/multi-area, glob/PR/git/package
specifiers, CI vs interactive, clean pass, Pending Decisions, error handling
— see [references/examples.md](references/examples.md).
