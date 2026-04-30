# GIT-PR-SIZE-03: Red Zone PR Size

## Severity

warning

## Intent

A red-zone PR changes **≤ 60 files** AND nets **≤ 2000 LOC** while exceeding yellow thresholds. Red PRs are allowed only when splitting would harm review (mechanical refactors, generated files, atomic migrations). They MUST include an isolation justification and a reviewer-time estimate so reviewers can plan.

A red PR carries everything yellow requires (Summary, Checklist, Risk, Test plan) **plus** a `## Why this size` section.

## Fix

```markdown
## Summary
Codemod-driven rename of `User` -> `Account` across the persistence layer.

## Why this size
- Mechanical refactor (`GIT-PR-TYPE-04`); 47 files touched, all by automated codemod
- Splitting would leave the codebase non-compiling between PRs
- No behavior change; type-checker is the safety net
- Reviewer-time estimate: ~20 min — diff is uniform; spot-check 5 representative files

## Risk
- Snapshot tests will need re-recording (tracked in follow-up)
- No public API renamed; downstream consumers unaffected

## Test plan
- `npm run typecheck` clean across all workspaces
- Existing test suite passes without modification

## Checklist
- [x] Codemod script committed under `scripts/codemods/`
- [x] No behavior change verified
```

### Why this matters

- Without justification, a red PR signals an unsplit feature, not a cohesive change.
- The reviewer-time estimate is a forcing function: if the author cannot estimate, the PR is not ready.
- Acceptable red-zone categories are narrow: `mechanical-refactor`, `migration` (atomic), `cleanup` (sweeping deprecations), and PRs dominated by `GIT-PR-TYPE-05` generated files.

## Edge Cases

- Red PRs that interleave behaviour changes with mechanical edits violate `GIT-PR-TYPE-04`; split before submitting.
- A red PR whose justification is "feature too large to split" is a yellow-PR-shaped feature in disguise — re-plan as a stack (`GIT-PR-STACK-*`).
- Override numeric thresholds via `[git.pr.thresholds]` in standard-overrides.

## Related

GIT-PR-SIZE-02, GIT-PR-SIZE-04, GIT-PR-TYPE-03, GIT-PR-TYPE-04, GIT-PR-TYPE-05, GIT-PR-STACK-05
