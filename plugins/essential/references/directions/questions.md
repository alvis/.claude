# Asking user questions

Write every question for a reader with little context, whether a newcomer or a
senior decision-maker. Give them enough information to choose without opening
another file.

## Establish the decision

- State what needs direction and why it matters now.
- Describe each referenced item in one line. Do not write only `ADR 1` or
  `Proposal A`; write, for example, `Architecture Decision Record (ADR) 1 —
  Consolidate vendors: moves purchases to one supplier, lowering unit cost but
  increasing dependency`.
- Define any term an outsider may not know, then state its implication for this
  decision. For example, `cannibalization means a new offering takes sales from
  an existing one, which can reduce total growth even when the new offering
  performs well`.
- Ask one focused question. Separate unrelated decisions.

## Present choices

Put the solution in one line in each choice title and prefer every applicable
tag there, such as `Consolidate purchasing [Pragmatic] [Recommended]`. If the
provider limits title or label length, keep the solution title within that
limit and put the tags on the first line of the choice detail instead. For
example, use title `Consolidate vendors` and begin its detail with
`[Pragmatic] [Recommended]`.

For a material decision, identify the recommendation and explain why.

| Tag | Use when |
| --- | --- |
| `Architectural` | This is the long-term north star, aligned with the system architecture and expected to remain correct as the codebase evolves. |
| `Ideal` | This is the highest-quality implementation: the best balance of correctness, maintainability, readability, and engineering principles. |
| `Recommended` | This is the default for most situations unless a compelling reason favors another choice. |
| `Pragmatic` | This deliberately trades some elegance or generality for practicality, delivery speed, or simplicity. |
| `Hotfix` | This urgently restores functionality and should usually be revisited after the immediate issue is resolved. |
| `Workaround` | This temporarily bypasses the root cause to keep progress moving and needs a planned permanent replacement. |

In each choice body, explain how the solution works and what choosing it commits
the decision-maker to. Include meaningful benefits, drawbacks, implications,
upfront or ongoing cost, reversibility, and follow-up work. Use explicit
`Pros` and `Cons` when they make a real trade-off easier to compare.
