# Review checklist and finding schema

Load this at step 7 of `coding:review-pr`. Evidence rules come from
[the shared review mandates](../../review-code/references/mandates.md); this file
adds what is specific to reviewing a PR diff.

## Depth

Scale depth to the size zone from step 4: green reviews line by line, yellow leads
with the key areas then goes line by line, red leads with architecture and goes
line-level only where it matters, black says split it before reviewing further. A
2,000-line review that comments on everything teaches nothing.

One finding per problem, at the highest priority that applies. The same mistake in
eight places is one finding on the clearest instance, noting that it applies
throughout.

## Checks worth reading outside the diff for

These are the findings a diff-only reader cannot make, and they are usually the
most valuable ones in the review:

- **Is this the best solution?** Walk the lean ladder in
  [CODING.md](../../../references/CODING.md). Search the repository before
  accepting a new helper, type, or constant: a hand-rolled thing that
  `@theriety/core` or the codebase already provides is a finding, and so is an
  abstraction with one caller.
- **Callers of what changed.** Follow a changed signature, return shape, or thrown
  error into its actual call sites. A caller that now receives `undefined`, ignores
  a new error, or breaks on a renamed field is a verified finding — anchor it to the
  changed line that breaks it, and name the call site in the body.
- **Siblings the new file should resemble.** Open the files with the same role in
  the same directory and compare naming, parameter and return shape, error, log,
  retry, and cache behavior. Unexplained divergence from an established local
  pattern is the most common real finding in a PR review.
- **Scope against the stated goal.** The PR title, body, and any resolvable
  goal/spec are the contract. Report what the PR claims but does not do, and what it
  does without claiming — scope creep is a finding, not a bonus.
- **Secrets and trust boundaries the diff introduces.** Any token, credential,
  internal hostname, or widened trust boundary entering the repository in this diff.
- **Docs the change makes wrong.** Read the README, API doc, or example the changed
  surface belongs to, and flag it when the diff contradicts it.

`style` reports only what the candidate scan surfaced plus naming-policy gaps, each
with its rule id. Never run project lint — `coding:lint` owns that.

## Finding schema

Record each finding as:

<report>

```yaml
findings:
  - path: <repo-relative path as it appears in the diff>
    line: <line number in the head revision>
    side: RIGHT | LEFT
    start_line: <first line of a multi-line range, or null>
    concern: alignment | correctness | security | quality | testing | docs | style
    priority: P0 | P1 | P2 | P3
    prefix: issue | suggestion | nit | question | praise
    body: <the comment text, written per tone.md>
    evidence: <the rule, failure path, or repository precedent it rests on>
goal_spec_alignment: matches | diverges | skipped_unknown
not_reviewed:
  - path: <path>
    reason: <binary, generated, vendored, deleted, or too large>
```

</report>

- `path` and `line` must come from the step-4 changed-line map. A finding rooted in
  unchanged code anchors to the changed line that causes it.
- `side` is `RIGHT` for added lines and `LEFT` for removed ones; most findings are
  `RIGHT`. `start_line` opens a multi-line range and must be below `line` on the
  same side — use it when the problem is a block, not a line.
- `priority` is about consequence, not effort: **P0** breaks correctness, security,
  or data integrity; **P1** violates a standard or will cause a real defect; **P2**
  is maintainability or design; **P3** is optional polish. It drives the verdict.
- `prefix` follows `constitution/standards/code-review.md`: `issue` for P0/P1,
  `suggestion` for P2, `nit` for P3, `question` where intent is genuinely unclear,
  `praise` where the work is genuinely good.
- `evidence` is mandatory. A finding that cannot name the rule it applies or the
  failure it predicts is an opinion, and opinions are not posted.
- `goal_spec_alignment` is `skipped_unknown` when no goal or spec can be resolved.
  Never infer a goal from the diff and then grade the diff against it.

## When a concern cannot be finished

Name it in the completion report and cap the verdict at `COMMENT` per
[publishing.md](publishing.md). Never present a partial review as complete, and
never fill the gap by dispatching another reviewer.
