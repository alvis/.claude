# Reviewer dispatch and finding schema

Load this at step 7 of `coding:review-pr`. Area ownership, evidence rules, and
de-duplication come from [the shared review mandates](../../review-code/references/mandates.md);
this file adds only what is specific to reviewing a remote PR.

## Dispatch

One parallel batch, at most seven reviewers, one per selected area. Reviewers are
read-only and may not delegate further. Each receives:

- the absolute `$REVIEW_DIR` and the changed file paths for its area (paths, not
  contents);
- the changed-line map, so it knows which lines a comment can anchor to;
- the resolved standard file paths from step 6;
- the PR title and body as the author's stated intent;
- its slice of the mechanical candidate scan, marked advisory;
- [tone.md](tone.md) and the finding schema below;
- an instruction to modify nothing, execute nothing from the checkout, and
  return the `<report>` unchanged in shape.

Per-area file selection mirrors `coding:review-code`: alignment gets the changed
files plus the PR description; correctness and quality get source plus tests;
security gets source, with `auth/`, `api/`, and `services/` paths prioritized;
testing gets tests plus the source they cover; docs gets source, docs, and
examples; style gets everything textual.

Scale depth to the diff, per `code-review.md`: under 100 changed lines, review
line by line; 100-500, key areas first, then line by line; over 500,
architecture first and line-level detail only where it matters. A 2,000-line
review that comments on everything teaches nothing.

## Finding schema

Each reviewer returns exactly this, and nothing else:

<report>

```yaml
area: alignment | correctness | security | quality | testing | docs | style
findings:
  - path: <repo-relative path as it appears in the diff>
    line: <line number in the head revision>
    side: RIGHT | LEFT
    start_line: <first line of a multi-line range, or null>
    priority: P0 | P1 | P2 | P3
    prefix: issue | suggestion | nit | question | praise
    body: <the comment text, written per tone.md>
    evidence: <the standard rule, failure path, or sibling precedent it rests on>
files_reviewed: [<path>]
not_reviewed:
  - path: <path>
    reason: <binary, generated, vendored, deleted, or too large>
```

</report>

Field rules:

- `path` and `line` must come from the changed-line map. A reviewer that wants
  to flag unchanged code names it inside `body` and anchors the comment to the
  nearest changed line that makes the point land.
- `side` is `RIGHT` for added or context lines in the head revision and `LEFT`
  for removed lines. Removed-line comments are for deletions that break
  something; most findings are `RIGHT`.
- `priority` drives the review verdict, so it is a judgement about consequence,
  not about effort: **P0** breaks correctness, security, or data integrity;
  **P1** violates a constitution standard or will cause a real defect;
  **P2** is a maintainability or design improvement; **P3** is optional polish.
- `prefix` maps to priority and sets the reader's expectation, per the table in
  `constitution/standards/code-review.md`: `issue` for P0/P1, `suggestion` for
  P2, `nit` for P3, `question` where intent is genuinely unclear, `praise` where
  the work is genuinely good.
- `evidence` is mandatory. A finding that cannot name the rule it applies or the
  failure it predicts is an opinion, and opinions do not get posted.

## Per-area emphasis for a PR

Only the deltas from the shared mandates are listed; everything else is
unchanged.

- **alignment** — the contract is the PR title and body, plus any linked issue
  or spec. Report what the PR claims but does not do, and what it does without
  claiming. Scope creep in a PR is a finding, not a bonus.
- **correctness** — trace the changed control flow against its callers in the
  checkout, not just the hunk. The diff hides the caller that now receives
  `undefined`.
- **security** — new trust boundaries introduced by the diff, and existing ones
  the diff widens. Check whether any secret, token, or internal hostname entered
  the repository in this PR.
- **quality** — compare each new file against its siblings in the same
  directory. Unexplained divergence from an established local pattern is the
  most common real finding in a PR review.
- **testing** — see the mandate in `SKILL.md` step 7. Additionally: does the PR
  change behavior without changing a single test, and does any test in the diff
  assert only that a mock was called?
- **docs** — exported API surface changed by the diff, and any README or example
  the diff makes wrong.
- **style** — report only what a mechanical rule can name, with the rule id.
  Cap `nit` findings at five per PR; beyond that, say once in the overall body
  that the formatter should run and stop commenting.

## Reruns

If a reviewer returns malformed output or fails, redispatch that area alone with
the validation error and the same inputs. Never ask another area to repair it,
and never post a partial area silently — an area that could not be reviewed is
named in the completion report.
