# Deviation lifecycle — reconciliation, three-state verdicts, and finalization

Referenced from SKILL.md Workflow steps 5–7. Defines how reconciled decisions
are recorded so the review gate cannot go green before gaps actually close.

## Severity ladders for detection

- **Drift** (implementation deviates from the spec — wrong shape or contract,
  weakened invariant, different error semantics, ordering, or side-effect set):
  P0 if it breaks a documented acceptance criterion or shared interface; P1 for
  an observable public-surface change; P2 for internal-helper or naming
  divergence; P3 if purely cosmetic relative to spec wording.
- **Omission** (a spec requirement with no implementing site anywhere in the
  repository): P0 if gated by an acceptance criterion or labeled "MUST"; P1
  otherwise; P2 only if the spec itself marks it optional or future.
- **Unsanctioned addition**: P1 minimum unless trivial (logging, internal
  helpers consistent with siblings).

## Three-state model

Each deviation is `open`, `decided`, or `resolved`:

- **open** — no resolution chosen yet.
- **decided** — the user chose "update spec to match code", "update code to
  match spec", or "defer". A resolution exists but the gap is still real; the
  deviation stays outstanding until the close-the-gap action executes.
- **resolved** — the gap is gone: either the close-the-gap action completed,
  or the user chose "accept as-is / waive" (which resolves immediately — the
  gap is explicitly tolerated).

Only `resolved` deviations drop out of the verdict counts. Both `open` and
`decided` count as outstanding, so a verdict that counts `decided` deviations
as outstanding is correct, not a mismatch. When aggregating into the
`README.md` index, map any `decided` deviation to `REQUIRES_CHANGES` exactly
like an `open` one.

Overall status follows the base-skill logic with this counting rule: any P0
outstanding → FAIL; P1 outstanding with no P0 → REQUIRES_CHANGES; only P2/P3
outstanding → PASS_WITH_SUGGESTIONS; all deviations `resolved` and all areas
passing → PASS.

## Weaving reconciliation into ALIGNMENT.md

Rewrite each issue block in place with: the chosen resolution, a rationale
describing the final gap (what remains different and why that is acceptable or
must change), the concrete close-the-gap action (the exact edit or delegation
that would resolve it), and the inline state (`open`/`decided`/`resolved`).
Dissolve these into the existing issue blocks — never append a parallel
"Resolutions" appendix.

Then append a single `## Next-Action Plan` section with two ready branches:

- **Branch A — hand off**: spec/implementation paths, the report location, and
  exactly which delegations (`specification:spec-code`, `coding:fix`,
  `specification:implement-code`) remain to close each gap. Executed via
  `coding:handover`, after which the skill stops.
- **Branch B — execute now**: the same delegations sequenced for immediate
  execution. Spec changes route to `specification:spec-code` then persist via
  the sync skill; code changes route to `coding:fix` (targeted) or
  `specification:implement-code` (ticket-scale). As each `decided` deviation's
  action completes, flip it to `resolved` and recompute the verdict and index.
  Offer an optional re-detection round afterward to confirm the gaps closed.

## Re-run stability

When `ALIGNMENT.md` already exists, read it first: match new findings to prior
unchecked entries by source location plus issue text and reuse their original
`ALIGN-P<n>-<seq>` IDs; preserve `## Pending Decisions`, any prior
`## Next-Action Plan`, and reconciliation annotations already woven in; for a
prior unchecked item with no current match, confirm it no longer applies
before dropping it; new findings take the next available sequence per
priority. Rewrite the file in full.

## Structural validation

After writing or finalizing `ALIGNMENT.md`, dispatch one read-only validator
subagent to confirm:

1. frontmatter carries `area: alignment`, `prefix: ALIGN`, `reviewed_at`, and
   `files_reviewed_count`;
2. the verdict line is well-formed and matches the outstanding count under the
   three-state rule (do not flag `decided`-counted verdicts as mismatches);
3. issue blocks follow the canonical template format with stable
   `ALIGN-P<n>-<seq>` IDs across re-runs;
4. `## Pending Decisions` is present iff any issue has `**Solution**: TBD`;
5. the alignment-specific additions (`## Next-Action Plan`, per-issue
   reconciliation annotations) are accepted, not flagged as template
   violations.

On a validation failure with fixable fatals, re-write the report once with the
fatals attached as fix instructions, then re-validate (max 1 retry).
