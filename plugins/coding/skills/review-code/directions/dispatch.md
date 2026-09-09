# Review dispatch contracts

Before dispatch, allocate one collision-safe OS temporary directory with a distinct `<area>.md` path per reviewer. Keep these files until the main agent has validated and persisted them under `reviews/`; then remove the temporary directory. A failed write or import blocks presentation.

Dispatch selected areas in one parallel batch, at most seven reviewers. Each reviewer receives file paths and these common inputs:

- resolved work ID/root, assigned temporary report path, and previous area report when present;
- exact relevant spec/design/review paths from the mission capsule;
- canonical `plan_source: state.md` and applicable full `task_id` values read directly from `state.md`;
- discovered source/test/doc paths for the area;
- advisory mechanical-scan slice;
- [review.md](templates/review.md) and [mandates.md](references/mandates.md);
- instruction to write only its assigned report, leave reviewed code and `.state` untouched, delegate no further, and preserve stable finding IDs/statuses. Keep evidence, plan binding, and reviewed task IDs in the report; return only its path, verdict, counts, and a short summary for the main agent.

The capsule is sufficient by default. Give `state.md` to alignment reviewers, or when resume/cross-slice evidence requires it; give `state/working.md` only when navigation is otherwise missing. Do not make every area reread both broad entrypoints.

Before dispatch, group discovered files by owning project, resolve every configured compiler-test discovery glob that applies to each group, then run the scanner once per group with that project's root and one repeated pattern argument per resolved compiler glob. Never combine files owned by different test roots in one invocation:

```bash
bun run plugins/coding/scripts/scanlib/core.ts \
  <files-owned-by-project> --category all --before 5 --after 10 \
  --test-root <project-root> [--test-pattern <compiler-test-glob> ...]
```

Surface a hard Bun runtime failure. Candidate output is not a finding until the assigned reviewer validates it against `coding:standards/code-review/`'s evidence threshold. Pass prior dispositions and their evidence; a fresh dispatch does not reset them.

## Areas

### alignment

- General-purpose contract analyst.
- Compare every changed behavior/file with root state's canonical task definition and criteria, materialized specs, approved work decisions/design, and relevant durable docs. Identify omissions, additions, unjustified drift, stale derivations, and missing promotion/sync work.
- If no approved work contract exists or its current task definitions differ from the review capsule, state that blocker; do not adopt root planning files.
- Follow an explicit implementation-detail link only for procedure keyed by existing IDs; reject it if it restates/changes IDs, edges, requiredness, targets, or acceptance mappings.
- Write the assigned report for `reviews/alignment.md`, prefix `ALIGN`.

### correctness

- Code-quality critic focused only on semantics.
- Trace control flow, boundaries, async/resource behavior, errors, operators, arguments, invariants, and plausible failure paths. Do not duplicate alignment, quality, or mechanical findings.
- Write the assigned report for `reviews/correctness.md`, prefix `CORR`.

### security

- Security champion.
- Check injection, authentication/authorization, validation, data/secrets, dependency exposure, CORS/headers, cryptography, and trust boundaries.
- Write the assigned report for `reviews/security.md`, prefix `SEC`.

### quality

- Code-quality critic focused on sibling consistency, non-mechanical redundancy, structure, naming posture, complexity, DRY, error-handling posture, performance, accessibility, and architecture. Route semantic bugs to correctness and plan drift to alignment.
- Write the assigned report for `reviews/quality.md`, prefix `QUAL`.

### testing

- General-purpose test-quality analyst.
- Check meaningful behavior/edge/failure/integration coverage, assertion strength, per-source coverage, isolation, determinism, fixture/mock ownership, complexity, and redundancy.
- Write the assigned report for `reviews/testing.md`, prefix `TEST`.

### docs

- General-purpose documentation analyst.
- Check exported API docs, complex-logic explanation, README/API/example/type accuracy, and whether durable architecture/design/spec promotion is required.
- Write the assigned report for `reviews/docs.md`, prefix `DOCS`.

### style

- General-purpose style analyst.
- Discover and run repository lint/format/naming checks, capture exact diagnostics, and report naming-policy gaps not already owned by tooling.
- Write the assigned report for `reviews/style.md`, prefix `STYL`.

## Reruns

If a reviewer fails or writes malformed output, retain the previous canonical report and redispatch that area only with the validation error and same inputs. Never ask another area to repair it.
