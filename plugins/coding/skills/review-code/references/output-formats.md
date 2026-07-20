# Review completion formats

Render only a compact summary; detailed findings live under the active work
root. Both interactive and non-interactive modes report:

```markdown
# Code review summary

- Work: `<work-id>`
- Overall: `<pass|pass_with_suggestions|requires_changes|fail>`
- Contract: `<state.md or explicit plan path>`
- Alignment: `<verdict/counts>` — `reviews/alignment.md`
- Correctness: `<verdict/counts>` — `reviews/correctness.md`
- Security: `<verdict/counts>` — `reviews/security.md`
- Quality: `<verdict/counts>` — `reviews/quality.md`
- Testing: `<verdict/counts>` — `reviews/testing.md`
- Docs: `<verdict/counts>` — `reviews/docs.md`
- Style: `<verdict/counts>` — `reviews/style.md`
- Outstanding priorities: `P0:<n> P1:<n> P2:<n> P3:<n>`
- Dispositions: `open:<n> fixed:<n> acknowledged:<n> deferred:<n> skipped:<n>`
- Closure: `closed:<n> outstanding:<n>`
- Summary: `.engineering/work/<work-id>/review.md`
- Generated files: `<explicit paths>`
```

Omit unselected areas. CI/non-interactive mode additionally returns nonzero for
any outstanding finding; it never prompts. Interactive mode may name the next owning skill but
must not inline the findings.
