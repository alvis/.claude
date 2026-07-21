# Alignment finding lifecycle

This reference defines alignment severity, disposition, rerun stability, and
summary reconciliation.

## Detection severity

- Drift is P0 when it breaks an acceptance criterion/shared invariant, P1 for
  observable contract change, P2 for internal naming/helper divergence, and P3
  for wording-only mismatch.
- Omission is P0 for a required acceptance/MUST item, P1 otherwise, and P2 only
  when the source marks it optional/future.
- Unsanctioned additions are P1 minimum unless they are trivial internal
  behavior consistent with repository standards.

## Dispositions

- `open`: no decision.
- `fixed`: the gap no longer exists and verification confirmed it.
- `acknowledged`: closed non-fixed risk acceptance with durable rationale,
  accountable owner, and explicit recheck condition.
- `deferred`: owner and decision/recheck deadline recorded; gap remains.
- `skipped`: closed non-fixed scope/non-applicability acceptance with durable
  rationale, accountable owner, and explicit recheck condition.

`fixed` closes only with verification evidence. `acknowledged` and `skipped`
close only with the metadata above; P0/P1 additionally require explicit
risk-acceptance authority and durable acceptance evidence. Malformed closed
risk dispositions remain outstanding. `open` and `deferred` remain outstanding
and block review closure. Outstanding P0 yields FAIL; P1 yields
REQUIRES_CHANGES; only outstanding P2/P3 yields PASS_WITH_SUGGESTIONS.

## Writing `alignment.md`

Rewrite each issue block in place with resolution rationale, concrete action,
owner/deadline where applicable, and disposition. Maintain one next-action
section linking exact work-local spec, change, or handoff paths. Never append a
parallel resolutions/deviations ledger.

On rerun, match prior findings by spec location, implementation location, and
issue meaning; reuse IDs and reconciliation. Confirm closure before dropping an
unmatched prior finding. New findings take the next sequence.

## Summary reconciliation

`review.md` contains only per-area verdict/counts, all five dispositions,
derived closed/outstanding counts, and relative paths. Map verified `fixed` and
valid `acknowledged`/`skipped` to closed; map `open`, `deferred`, and malformed
risk dispositions to outstanding. Do not copy issue bodies.

Validate frontmatter area/prefix/review timestamp/file count, verdict/count
consistency, stable IDs, required decision metadata, and link resolution. Retry
one fixable structural failure once.
