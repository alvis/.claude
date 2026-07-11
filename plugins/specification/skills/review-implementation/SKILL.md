---
name: review-implementation
description: "Review an implementation against an authoritative local or Notion specification, then run the general coding and security review. Use for specification alignment, delivered-ticket validation, or detecting omissions, drift, and unsanctioned behavior before handoff."
model: opus
context: fork
agent: general-purpose
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

`specifier` accepts the same file, directory, package, PR, or range forms as `coding:review-code`. `--spec-path` defaults to `./.code-spec`; `--out` defaults to `reviews/`. `--area=all` is the default. `--area=alignment` produces only alignment findings; any other selection still runs alignment when a spec is available.

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
3. Run the alignment area first. Enumerate requirements, map each to code evidence, and record omissions, drift, or unsanctioned additions. Use independent find/verify checks when the scope warrants them.
4. Always invoke `Skill(coding:review-code)` for the requested non-alignment areas, including its general semantic review and security review, even when alignment has P0/P1 findings. Pass the target and output directory; tell the base skill that specification conformance belongs only in `ALIGNMENT.md`.
5. Reconcile each alignment deviation with the user: update the spec, update code, accept with rationale, or defer. Do not silently choose a resolution.
6. Regenerate `ALIGNMENT.md` and `README.md`, retaining the base review's findings and recording any refusal or skipped area.
7. Return a structured summary and a next-action plan. Approved implementation changes route to `coding:fix` or `specification:implement-code`; continuation notes route to `coding:handover`.

## Alignment contract

For each requirement, record `requirement`, `spec_location`, `implementation_location`, `status` (`satisfied`, `missing`, `drift`, or `unsanctioned`), severity, evidence, and next action. Keep spec-conformance findings out of the base review files. Semantic bugs that are wrong regardless of the specification remain in the base review's correctness area.

Alignment is a gate for the next action, not a gate for evidence collection: a failed alignment must still have general and security findings so the user can see the complete risk picture.

## Completion report

```yaml
status: success|partial|refused
specifier: <target>
spec_path: <absolute path>
alignment: pass|fail|refused
base_review: completed|partial|skipped
general_review: completed
security_review: completed
open_findings: 0
reports: [ALIGNMENT.md, SECURITY.md, ...]
next_action: execute|handover|defer
```
