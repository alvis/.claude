# Core review mandates

These rules apply to all seven areas; area ownership prevents duplicate findings. Apply `coding:standards/code-review/` before recording or prioritizing a candidate: `CRV-FDBK-01` owns evidence eligibility, `CRV-FDBK-02` owns settled dispositions, and `CRV-PRIO-02` owns the stopping condition. Unsupported speculation is omitted, not recorded as an open or deferred finding or a confirmation question.

## Contract alignment belongs to alignment

Root `state.md` (`plan_source: state.md`) plus linked approved specification/design/decision artifacts is the implementation contract. Its explicit ID-keyed implementation detail may be consulted but cannot duplicate or override IDs, edges, requiredness, targets, or acceptance mappings. A caller-supplied plan may assert but never override root state. Bind every result to the exact `plan_source: state.md` and relevant full task IDs. `alignment.md` alone reports additions, omissions, unjustified drift, stale spec derivations, and missing promotion/sync work. Other reviewers route pure drift there rather than duplicating it.

## Semantic errors belong to correctness

Trace supported behavior rather than trusting code shape. Wrong control flow/operators, swapped arguments, silent errors, races, unhandled async work, leaks, and boundary validation defects belong in `correctness.md` unless security-specific. Apply the standard's evidence threshold even without a feature-specific requirement; a merely plausible failure path is insufficient.

## Redundancy and sibling consistency belong to quality

Search siblings with the same role and compare naming, parameter and return shape, error/log/retry/cache behavior, and logic flow. Flag unexplained divergence and human-detectable redundancy such as behavior-free wrappers, duplicate logic, impossible defensive checks, parallel compatibility paths, or single-caller over-generalization. For a defensive-check finding, trace value provenance and show that no public, external, dynamic, unsafe, persistence, or deserialization boundary exists and that supported execution cannot invalidate the condition independently, applying `GEN-SAFE-03`. A first-party producer postcondition does not justify the check merely because the type cannot fully express it. Cite the exact producer test that proves the checked postcondition; broad coverage and the helper's name are not evidence. Tool-detectable dead/unused code stays with lint.

## Mechanical checks stay mechanical

Do not spend semantic-review effort on type errors, unused imports/variables, formatting, import ordering, or other compiler/linter facts. `style.md` may report actual command results; remediation belongs to `coding:lint` or `coding:fix` as appropriate.

## Evidence and dispositions

Every finding's existing evidence field supplies the governing requirement or rule, applicability proof, and concrete impact required by `CRV-FDBK-01`. It has one status: `open`, `fixed`, `acknowledged`, `deferred`, or `skipped`. Verified `fixed` and valid `acknowledged`/`skipped` findings are closed. Closed risk dispositions require rationale, owner, and recheck condition; P0/P1 also require explicit risk-acceptance authority/evidence. `open`, `deferred`, and malformed risk dispositions remain outstanding and block closure. Never change status merely to produce a passing verdict. On rerun, retain settled dispositions under `CRV-FDBK-02`; cite new invalidating evidence before reopening one. Stop under `CRV-PRIO-02` once required checks pass and evidenced defects are resolved.
