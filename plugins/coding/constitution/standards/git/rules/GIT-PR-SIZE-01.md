# GIT-PR-SIZE-01: Green Zone PR Size

## Severity

warning

## Intent

A green-zone PR changes **≤ 15 files** AND nets **≤ 500 LOC**. Green PRs are the default-mergeable unit of work — small enough that a reviewer can hold the entire diff in their head, fast enough that turnaround does not stall a stack.

A PR's zone is the stricter of the two metrics: 12 files / 600 LOC is yellow, not green.

## Fix

```markdown
## Summary
Adds the `archiveOrder()` operation to the order service.

## Checklist
- [x] Tests added
- [x] Docs updated
```

PR metadata:

```text
files changed: 7
net LOC: 184
zone: green
```

### Why this matters

- Reviewer working memory is the binding constraint, not LOC alone.
- Green PRs need only the Summary and Checklist sections (`GIT-PR-02`); ceremony scales with size.
- Stacks are healthier when each layer fits in green — splits become natural, not forced.

## Edge Cases

- Generated files (lockfiles, snapshots) inflate LOC without inflating cognitive load. Mark them per `GIT-PR-TYPE-05` and a reviewer may still treat the PR as green in spirit.
- Tests count toward LOC. A green-LOC PR with a 400-line test file is still green; do not split tests away from the code they cover.
- Project overrides may relax thresholds via `[git.pr.thresholds]` in standard-overrides. The zone definitions remain ordinal even when numeric bands shift.

## Related

GIT-PR-02, GIT-PR-SIZE-02, GIT-PR-SIZE-03, GIT-PR-SIZE-04, GIT-PR-TYPE-05
