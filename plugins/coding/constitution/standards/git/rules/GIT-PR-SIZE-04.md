# GIT-PR-SIZE-04: Black Zone PR Size

## Severity

warning

## Intent

A black-zone PR changes **> 60 files** OR **> 2000 LOC**. The lint flags black-zone PRs and surfaces the rejection template (`write.md` -> Black-Zone Rejection Template). The flag is **advisory**, not auto-blocking — escape hatches matter for genuine atomic changes — but the default expectation is that the PR is split before review.

## Fix

When a PR enters the black zone, the author either splits it or paste-replies to the flag with explicit justification:

```markdown
## ⛔ PR Size — Black Zone

This PR exceeds **60 files** or **2000 LOC** (zone threshold).

Black-zone PRs are flagged because reviewer attention degrades sharply past this size.
Please split before requesting review:

- [ ] Extract mechanical refactors into their own PR (`GIT-PR-TYPE-04`)
- [ ] Extract migrations into their own PR with rollback (`GIT-PR-TYPE-03`)
- [ ] Extract generated files into their own PR or mark them clearly (`GIT-PR-TYPE-05`)
- [ ] Land code spec / scaffolding first (`GIT-PR-TYPE-02`)
- [ ] Stack remaining behaviour changes per `GIT-PR-STACK-*`
```

If splitting is genuinely impossible (e.g. a single atomic migration), the author writes `## Why this size` justifying the override and applies the project-local threshold escape:

```toml
# standard-overrides.toml
[git.pr.thresholds]
files_red   = 80
loc_red     = 2800
files_black = 80
loc_black   = 2800
```

### Why this matters

- Reviewer recall drops sharply past ~60 files; bugs hide in the long tail of the diff.
- A flag-only approach respects engineering judgment for legitimate atomic changes while making oversize the conscious exception, not the default.
- Project-local overrides keep the rule honest for repos where larger PRs are normal (monorepo-wide upgrades, vendor drops).

## Edge Cases

- A black PR that is 95 % `GIT-PR-TYPE-05` generated files (e.g. SDK regeneration) is the canonical justified override; the human-authored diff still must fit in red or below.
- A black PR opened for "speed of review" contradicts the rule — speed is exactly what the zone threshold protects.
- Override only the smallest necessary band; do not raise green thresholds to mask habitual oversize work.

## Related

GIT-PR-SIZE-02, GIT-PR-SIZE-03, GIT-PR-TYPE-02, GIT-PR-TYPE-03, GIT-PR-TYPE-04, GIT-PR-TYPE-05, GIT-PR-STACK-05
