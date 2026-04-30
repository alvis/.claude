# GIT-PR-SIZE-02: Yellow Zone PR Size

## Severity

warning

## Intent

A yellow-zone PR changes **≤ 30 files** AND nets **≤ 1200 LOC** while exceeding green thresholds. Yellow PRs are mergeable but require the author to surface risk explicitly so a single reviewer can budget about 30 minutes and still catch what matters.

Yellow PRs MUST include a **Risk** section and a **Test plan** section in addition to the green-zone defaults.

## Fix

```markdown
## Summary
Introduces the new pricing engine module with parity tests against the legacy calculator.

## Risk
- Pricing path is on the critical revenue flow
- Behavior gated behind `pricing.engine=v2` flag (default off)
- Legacy code path retained for one release cycle

## Test plan
- Unit tests cover all 14 tax-jurisdiction branches
- Property-based parity test compares 10k samples against legacy
- Manually verified the four highest-volume merchant configs in staging

## Checklist
- [x] Tests added
- [x] Docs updated
- [x] Flag wired with default off
```

### Why this matters

- A yellow PR is large enough that "looks right" is not enough — the reviewer needs the author's mental model.
- Risk plus Test plan converts implicit confidence into explicit, reviewable claims.
- Yellow is a healthy zone: do not artificially shrink to green if the change is genuinely cohesive.

## Edge Cases

- A yellow PR composed mostly of generated files may move down to green-equivalent review effort if marked per `GIT-PR-TYPE-05`. The Risk section is still required because the generator change itself is the risk.
- Yellow PRs that touch a migration must be split (`GIT-PR-TYPE-03`).
- Override numeric thresholds via `[git.pr.thresholds]` in standard-overrides; the section requirements stay attached to the yellow zone regardless of where the band sits.

## Related

GIT-PR-02, GIT-PR-SIZE-01, GIT-PR-SIZE-03, GIT-PR-TYPE-03, GIT-PR-STACK-04
