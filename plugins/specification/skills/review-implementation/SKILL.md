---
name: review-implementation
description: "Review an implementation against an authoritative local or Notion specification, then run the general coding and security review. Use for specification alignment, delivered-ticket validation, or detecting omissions, drift, and unsanctioned behavior before handoff."
model: opus
context: fork
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion, TodoWrite, Skill
argument-hint: "[specifier] [--area=alignment|test|documentation|code-quality|security|style|all] [--out=reviews] [--spec-path=./.code-spec]"
---

# Review Implementation

Review delivered code against a concrete specification and the general review contract. `ALIGNMENT.md` owns specification conformance. `coding:review-code` owns semantic correctness, security, tests, documentation, and sibling consistency. This skill coordinates both and does not edit implementation files.

## Boundaries

- Require an on-disk specification bundle or resolve a Notion source with `Skill(sync-spec)` before alignment.
- Every alignment finding cites both a specification location and an implementation location.
- Do not duplicate the base review protocol or mechanical lint checks.
- Alignment failure changes the report and next-action plan, but never suppresses the general or security review.

## Inputs and outputs

`specifier` accepts the same file, directory, package, PR, or range forms as `coding:review-code`. `--spec-path` defaults to `./.code-spec`; `--out` defaults to `reviews/`. `--area=all` is the default. `--area=alignment` narrows the specification-specific artifact, but it still runs the mandatory general semantic and security areas from `coding:review-code`.

Write:

- `ALIGNMENT.md`: requirements mapped to implementation, with `ALIGN-P<n>-<seq>` findings and a verdict;
- all requested files from `coding:review-code` (`SECURITY.md`, `QUALITY.md`, `TESTING.md`, `DOCS.md`, `STYLE.md`, and `CORRECTNESS.md` as applicable);
- `README.md`: an index with per-area verdicts, counts, and skipped/refused reasons.

If the spec cannot be materialized, return without partial review files:

```yaml
status: refused
reason: spec_not_found
resolved_spec_path: <absolute path>
```

## Workflow

1. Resolve the project root and `--spec-path`. For a Notion URL or ID, invoke `Skill(sync-spec)` once to materialize `.code-spec`, then verify the bundle contains a readable root specification.
2. Resolve the implementation file set with the same semantics as `coding:review-code`.
3. Run the alignment area first. Enumerate every requirement in the bundle (contracts, schemas, invariants, acceptance criteria, non-functional posture), then trace both directions: spec-to-code for omissions and drift, code-to-spec for unsanctioned additions. The specifier bounds only which code gets drift scrutiny — before flagging a requirement as missing, search the whole repository for an implementing site; a requirement implemented anywhere is satisfied. Treat every detection as a candidate: adversarially try to refute it (covered elsewhere, sanctioned by another spec section or an optional/future marker, drift within tolerance) and record only survivors. When scope warrants delegation, dispatch auditors blind — spec path, file set, template, and standards paths only, never the expected conclusion — and keep the verifier independent of the finder. `ALIGNMENT.md` follows `coding:review-code`'s `references/review.template.md` with prefix `ALIGN`, so finding IDs stay stable across re-runs per the base skill's rules.
4. Always invoke `Skill(coding:review-code)` for the requested non-alignment areas, including its general semantic review and security review, even when alignment has P0/P1 findings. Pass the target and output directory; tell the base skill that specification conformance belongs only in `ALIGNMENT.md`.
5. Reconcile each alignment deviation with the user: update the spec, update code, accept with rationale, or defer. Do not silently choose a resolution. Batch the questions, but every deviation must receive a decision.
6. Regenerate `ALIGNMENT.md` and `README.md`, retaining the base review's findings and recording any refusal or skipped area. Follow [references/deviation-lifecycle.md](references/deviation-lifecycle.md) for the severity ladders, the three-state `open`/`decided`/`resolved` verdict model (only `resolved` clears; `decided` still counts as outstanding), how reconciliation decisions are woven into each issue block, re-run ID stability, and the read-only structural validation pass.
7. Return a structured summary and the report's `## Next-Action Plan`, then ask the user which branch to take. Approved implementation changes route to `coding:fix` or `specification:implement-code`; spec changes route to `specification:spec-code` plus a sync; continuation notes route to `coding:handover`. Flip each `decided` deviation to `resolved` as its close-the-gap action completes, and offer a re-detection round to confirm closure.
8. Run the verification below; when a check fails, fix the cause and re-run that check. Repeat until every check passes or a concrete blocker remains, then report the blocker instead of looping.

## Verification

- Every alignment finding cites both a specification location and an implementation location, and survived the adversarial refutation pass.
- `ALIGNMENT.md`, the requested base review files, and the `README.md` index exist with per-area verdicts; the structural validation pass from [references/deviation-lifecycle.md](references/deviation-lifecycle.md) is clean.
- Every deviation carries a recorded reconciliation decision; only `resolved` deviations are counted as cleared.
- General and security review evidence is present even when alignment failed.

## Alignment contract

For each requirement, record `requirement`, `spec_location`, `implementation_location`, `status` (`satisfied`, `missing`, `drift`, or `unsanctioned`), severity, evidence, and next action. Severity follows impact: a broken acceptance criterion or weakened invariant is P0; contract drift is P0 or P1 by blast radius; an unsanctioned addition is P1 minimum unless trivial (logging, internal helpers consistent with siblings); documentation-only divergence is P2 or P3. Keep spec-conformance findings out of the base review files. Semantic bugs that are wrong regardless of the specification remain in the base review's correctness area.

Alignment is a gate for the next action, not a gate for evidence collection: a failed alignment must still have general and security findings so the user can see the complete risk picture.

## Completion report

```yaml
status: success|partial|refused
specifier: <target>
spec_path: <absolute path>
alignment: pass|fail|refused
base_review: completed|partial|refused
general_review: completed|partial|refused
security_review: completed|partial|refused
open_findings: 0
reports: [ALIGNMENT.md, SECURITY.md, ...]
next_action: execute|handover|defer
```

`success` requires alignment plus general and security review to complete with no blocking finding. Use `partial` when any required area fails, is unavailable, or retains findings; use `refused` only when no authoritative specification can be materialized. Never label a run complete when general/security evidence is absent.
