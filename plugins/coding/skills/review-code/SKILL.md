---
name: review-code
description: Review alignment, semantic correctness, security, test intent, documentation, quality, and style after code changes. Use for explicit post-implementation or pre-merge review; write canonical work-local review artifacts without editing the reviewed code.
model: opus
context: fork
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion, Write, Edit
argument-hint: "[specifier] [--area=alignment|correctness|security|quality|testing|docs|style|all] [--work-id=<id>] [--explain]"
---

# Review Code

Orchestrate a read-only code review and write seven canonical, lowercase review
areas beneath the active engineering work root. Remediation belongs to
`coding:fix`; mechanical enforcement belongs to `coding:lint`.

## Boundaries

- Review post-implementation changes, PRs, or explicit scopes across alignment,
  correctness, security, quality, testing, docs, and style.
- Do not edit reviewed code, build/deploy infrastructure, review dependencies,
  or write generic root `reviews/` output.
- Reject binary-only scopes. Reject `--out` with a migration message directing
  callers to `--work-id`; review paths are contract-owned.

## Inputs

- Optional specifier: file, directory, glob, package, PR, or git range.
- Optional `--area` canonical area list (default `all`), `--work-id`,
  `--plan=<path>` for an explicitly pinned external plan contract, and
  `--explain` for a work-local change-comprehension child.
- Require a repository checkout and an active or explicit work ID.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Resolve the work root before review.
Read `working.md` first, then `state.md`, its linked plan/spec/design/review
paths, and the selected source. Never write PM-owned `working.md` or the four
work overview files.
A direct PM run resolves or mints the work ID by the contract; a delegated run
requires the explicit work ID/root.

## Output contract

<report>

- Summary: `.engineering/work/<work-id>/review.md`.
- Areas under `.engineering/work/<work-id>/reviews/`:

  | Prefix | File | Ownership |
  |---|---|---|
  | `ALIGN` | `alignment.md` | approved state/spec/design adherence and drift |
  | `CORR` | `correctness.md` | semantic behavior and failure paths |
  | `SEC` | `security.md` | trust boundaries and vulnerabilities |
  | `QUAL` | `quality.md` | structure, consistency, complexity, maintainability |
  | `TEST` | `testing.md` | behavior evidence, coverage, fixtures, reliability |
  | `DOCS` | `docs.md` | code and durable documentation accuracy |
  | `STYL` | `style.md` | repository naming and mechanical-tool results |

- Each area follows [references/review.template.md](references/review.template.md)
  and uses `open|fixed|acknowledged|deferred|skipped` finding status. IDs remain stable
  across reruns. `fixed` is closed only by verified evidence. `acknowledged`
  and `skipped` are closed non-fixed risk dispositions only with rationale,
  accountable owner, and explicit recheck condition; P0/P1 also require
  explicit risk-acceptance authority and durable evidence. `open`, `deferred`,
  and malformed risk dispositions remain outstanding and block review closure.
- `review.md` is rewritten from area files and contains overall status, all five
  disposition counts, derived `closed` and `outstanding` counts, priority
  counts for outstanding findings, one-line area headlines, paths, systemic
  patterns, and PM handback—not duplicated findings.
- With `--explain`, write a lowercase child under `changes/` using
  [references/explainer.md](references/explainer.md); return it for PM
  reconciliation of `changes.md`.

</report>

## Workflow

1. Resolve the specifier and per-area file lists through
   [references/specifier-resolution.md](references/specifier-resolution.md).
   Use state as the default plan contract; an explicit `--plan` wins. Never
   auto-adopt root planning/design files.
2. Run the mandatory mechanical candidate scan described in
   [references/dispatch.md](references/dispatch.md). Candidates are advisory.
3. Dispatch one read-only reviewer per selected area in one parallel batch,
   following [references/dispatch.md](references/dispatch.md) and
   [references/mandates.md](references/mandates.md). Each writes only its
   assigned lowercase area file and returns path, counts, context level, and
   `generated_files`.
4. Validate every expected file, reject malformed disposition metadata, and
   aggregate current dispositions/priorities.
   Rewrite `review.md` entirely. Derive outstanding findings as `open`,
   `deferred`, or malformed `acknowledged`/`skipped`; derive closed findings as
   verified `fixed` plus valid `acknowledged`/`skipped`. Any outstanding P0 is
   `fail`; outstanding P1 is `requires_changes`; only outstanding P2/P3 is
   `pass_with_suggestions`; zero outstanding findings is `pass`. Every
   outstanding finding blocks review closure regardless of displayed verdict.
5. With `--explain`, generate the evidence-backed change child after review.
6. Render the final summary through
   [references/output-formats.md](references/output-formats.md). On malformed
   output, redispatch only the owning area until valid or blocked.
7. Return all area, summary, and optional explainer paths in `generated_files`.
Do not run file sizing; after every artifact writer returns, the PM checks only
eligible work Markdown inside the target `.engineering/` and coordinates a
complete split round if required.

## Verification

- Every selected area file exists, is lowercase, matches the template, and
  contains only its owned findings.
- `review.md` matches all area disposition/priority counts and paths.
- Alignment used the identical pinned state/plan/spec contract expected by any
  follow-up fix; no root fallback was selected.
- Reviewed code was not modified.

## Completion

Report area verdicts, aggregate priorities/dispositions, overall status,
`review.md`, optional explainer child, pinned plan source, and
`generated_files`. Detailed findings remain in area files.
