# Core review mandates

These rules apply to all seven areas; area ownership prevents duplicate
findings.

## Contract alignment belongs to alignment

`state.md` and its linked approved specification/design/decision artifacts are
the default implementation contract. An explicitly pinned plan may override
the plan portion. `alignment.md` alone reports additions, omissions,
unjustified drift, stale spec derivations, and missing promotion/sync work.
Other reviewers route pure drift there rather than duplicating it.

## Semantic errors belong to correctness

Trace behavior rather than trusting code shape. Wrong control flow/operators,
swapped arguments, silent errors, races, unhandled async work, leaks, and
boundary validation defects belong in `correctness.md` unless security-specific.
No “probably fine” findings: provide evidence and a plausible failure path.

## Redundancy and sibling consistency belong to quality

Search siblings with the same role and compare naming, parameter and return
shape, error/log/retry/cache behavior, and logic flow. Flag unexplained
divergence and human-detectable redundancy such as behavior-free wrappers,
duplicate logic, impossible defensive checks, parallel compatibility paths, or
single-caller over-generalization. Tool-detectable dead/unused code stays with
lint.

## Mechanical checks stay mechanical

Do not spend semantic-review effort on type errors, unused imports/variables,
formatting, import ordering, or other compiler/linter facts. `style.md` may
report actual command results; remediation belongs to `coding:lint` or
`coding:fix` as appropriate.

## Evidence and dispositions

Every finding cites a source/contract/runtime fact and has one status:
`open`, `fixed`, `acknowledged`, `deferred`, or `skipped`. Verified `fixed` and
valid `acknowledged`/`skipped` findings are closed. Closed risk dispositions
require rationale, owner, and recheck condition; P0/P1 also require explicit
risk-acceptance authority/evidence. `open`, `deferred`, and malformed risk
dispositions remain outstanding and block closure. Never change status merely
to produce a passing verdict.
