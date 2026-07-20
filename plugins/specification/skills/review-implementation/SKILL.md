---
name: review-implementation
description: Review implementation against an authoritative work-local or Notion specification, coordinate the seven canonical review areas, and summarize dispositions in the active work item. Use for alignment, ticket validation, omissions, drift, and unsanctioned behavior.
model: opus
context: fork
allowed-tools: Task, Read, Write, Edit, Grep, Glob, Bash, WebSearch, AskUserQuestion, TodoWrite, Skill
argument-hint: "[specifier] --work-id=<id> [--area=alignment|correctness|security|quality|testing|docs|style|all]"
---

# Review Implementation

Coordinate specification alignment and the general Coding review without
duplicating their detection protocols. Write canonical lower-case work-local
review artifacts and one disposition summary.

## Boundaries

- Require a verified work-local specification or invoke `sync-spec` to
  materialize one. Identify sources by receipt/frontmatter ref, not filename.
- `alignment.md` owns contract conformance. `correctness.md` owns semantic bugs
  that are wrong independently of the specification. The other areas are
  `security.md`, `quality.md`, `testing.md`, `docs.md`, and `style.md`.
- Do not create `audit.md`, `deviations.md`, review `readme.md`, root review
  files, or duplicate a finding across areas. Contract/completeness audit gaps
  route to alignment; plan departures stay in work state/changes.
- Review remains read-only with respect to implementation and MDC.

## Inputs and outputs

Require `--work-id=<id>`. Resolve output to
`.engineering/work/<work-id>/reviews/` and summary to sibling `review.md`.
`--area=all` is default; alignment-only still runs mandatory correctness and
security coverage through `coding:review-code`.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve work/review
   roots and read `working.md`, `state.md`, and the spec receipt.
2. For a Notion URL/id or stale/missing receipt, invoke `Skill(sync-spec)` in
   `materialize` mode. Refuse without writing partial reports when no verified
   authoritative specification can be materialized.
3. Resolve implementation scope with `coding:review-code` semantics. Enumerate
   requirements, invariants, schemas, acceptance criteria, and non-functional
   posture. Trace spec-to-code for omission/drift and code-to-spec for
   unsanctioned behavior; search the repository before declaring absence.
4. Adversarially refute each candidate and retain only survivors. Every
   alignment finding cites both spec and implementation locations and uses
   stable `ALIGN-P<n>-<seq>` identity across reruns.
5. Invoke `Skill(coding:review-code)` for requested non-alignment areas,
   including correctness and security on every run. Pass the work-local reviews
   directory and state that spec conformance belongs only in `alignment.md`.
6. Reconcile alignment findings with the user: update spec, update code,
   acknowledge/waive, defer, or skip with required closure metadata. Apply the lifecycle in
   [references/deviation-lifecycle.md](references/deviation-lifecycle.md).
   A decision does not clear a gap until its action lands, except valid
   acknowledgement/skip risk acceptance. P0/P1 risk acceptance requires
   explicit authority and durable evidence.
7. Rewrite `alignment.md` coherently and generate `review.md` with per-area
   verdict/count, finding disposition (`open`, `fixed`, `acknowledged`,
   `deferred`, `skipped`), and next-action pointers. Never copy full findings
   into the summary.
8. Run one read-only structural validator, fix once, and revalidate. Return
   explicit final paths generated or materially rewritten as `generated_files`.
   Do not run `wc -c`; the PM owns the final one-pass batch gate.

## Verification

- All seven canonical areas are present or have an explicit skipped/refused
  reason in `review.md`; correctness and security evidence always exist.
- Findings are single-owned, source-cited, adversarially checked, and their
  dispositions/counts agree between detail and summary.
- Stable IDs and prior reconciliation survive reruns; only closed gaps clear.
- `generated_files` lists `review.md` and every changed area artifact.

## Alignment contract

For each requirement record requirement, spec location, implementation
location, `satisfied|missing|drift|unsanctioned`, severity, evidence,
disposition, and next action. A broken acceptance criterion/weakened invariant
is P0; contract drift is P0/P1 by blast radius; documentation-only divergence
is P2/P3. Keep independently wrong behavior in `correctness.md`.

## Completion

<report>

```yaml
status: success|partial|refused
work_id: '<id>'
specifier: '<target>'
spec_root: '<absolute path>'
areas: {alignment: pass, correctness: pass, security: pass, quality: pass, testing: pass, docs: pass, style: pass}
dispositions: {open: 0, fixed: 0, acknowledged: 0, deferred: 0, skipped: 0}
closure: {closed: 0, outstanding: 0}
generated_files: []
next_action: execute|handover|defer
```

</report>
