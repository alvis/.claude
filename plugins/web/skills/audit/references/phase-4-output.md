# Canonical review rendering

Render actionable Markdown from `<audit-dir>/report-final.json`, or from
`report.json` with explicit partial coverage when manual adjudication is not
complete. Raw data remains evidence; canonical work review files are the human
engineering interface.

## Source validation

Before rendering:

1. Require contract version `3.0` and retain the source path plus SHA-256.
2. Preserve audited URLs, exact viewport dimensions, CLI exit status, warnings,
   capped/unvisited pages, cross-origin exclusions, orphan routes, recurring
   elements, crop/context paths, and manual-review coverage.
3. Verify every final AI verdict cites a focused crop or records
   `missing_section_crop` with null verdict.
4. Build one stable finding identity from CLI finding ID when present,
   otherwise `<rule-id>--<route-hash8>--<selector-hash8>`.

## Classification and writing

Apply `review-template.md` and classify each finding exactly once. Group by
canonical review area, then severity and stable identity. Write only applicable
`reviews/<area>.md` files; merge by finding identity so a rerun updates evidence
without erasing existing dispositions.

Coverage defects are findings in `testing.md`, including:

- zero audited pages or capped/unvisited required pages;
- missing required viewport/state data;
- missing focused crop for AI adjudication;
- driver warnings that invalidate claimed coverage; and
- incomplete manual review.

Site-level navigation or interaction failures belong to `correctness.md`.
Recurring visual issues are one `quality.md` finding with all affected routes,
not duplicate per-page prose. Cross-origin candidates declined by the user are
recorded as scope evidence, not defects.

## PM roll-up handoff

Return the reconciliation payload from `review-template.md`, including zeroes
for absent areas, plus:

```yaml
audit_summary:
  overall_score: <exact CLI value>
  risk: critical|high|medium|low
  pages_audited: <n>
  viewports: [<label + dimensions>]
  worst_pages: [<URL + score + primary finding IDs>]
  warnings: [<exact warnings>]
  raw_evidence: [<absolute final paths>]
```

This payload is for PM reconciliation into `review.md`; a worker does not write
the roll-up. Conversation output is a concise status, top open findings, exact
review/evidence paths, and coverage limitations rather than a competing report.

## Multi-page audits

Keep per-page and per-viewport data in JSON. Canonical findings cite every
affected page. Sort the concise handoff's worst pages from lowest score upward,
but retain all details in source evidence and review findings.
