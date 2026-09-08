# CMT-BODY-02: Keep Issue References Separate From Closure

## Severity

error

## Intent

Commit text records issue identity without controlling issue state. Reference an issue or PR by URL or `Refs: #NNN` at the bottom; `coding:pr create|update` owns verified GitHub Development links for resolving PRs. A `revert` commit carries a `Reverts <sha>` line naming the reverted commit, because the header alone does not identify it.

## Scan

Inspect the whole candidate message for a GitHub closing keyword paired with an issue reference, including case variants, inflections, qualified repository numbers, and URLs. Reject those directives wherever they occur; an ordinary description of a fix without a closing directive remains valid. Confirm every `revert`-typed commit has a `Reverts <sha>` line, and that the sha resolves in this repository.

## Fix

Replace the directive with a plain reference in the candidate message, retaining the issue identity. Pass resolving intent to `coding:pr create|update` for its Development-link workflow. Add the missing `Reverts <sha>`, reading the sha from history rather than memory.

## Edge Cases

- Partial and complete fixes both use plain references; only a PR that resolves the issue receives a closing Development link.
- Do not rewrite historical commits to remove their directives; apply this rule to newly authored messages.
- A revert of a revert still names the commit it reverts, not the original.

## Related

CMT-HEAD-01, CMT-BODY-01
