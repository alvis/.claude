---
name: skill-name
description: "Use when a concrete trigger requires this reusable capability and neighboring skills do not own the work."
---

# Skill Name

## Boundaries

- Use for: [specific triggers and owned outcomes].
- Do not use for: [neighboring responsibilities and their owning skills].

## Inputs

- **Required**: [minimum information needed to begin].
- **Optional**: [flags, scope, or defaults that change behavior].

## Workflow

1. Confirm the target and constraints.
2. Perform the smallest complete workflow that produces the owned outcome.
3. Handle explicit failure and ambiguity cases without widening scope.

Put bulky conditional instructions in `references/<topic>.md` and link them at
the decision point. Keep short conditions inline. Delegate only when the work
actually benefits from independent execution.

## Verification

- Run the checks that demonstrate the promised outcome.
- Validate frontmatter with `claude plugin validate --strict <plugin-path>`.
- Run repository policy checks with `quick_validate.py <skill-or-plugin-path>`.

## Completion

Report the outcome, verification performed, changed artifacts, and unresolved
issues. Do not require a fixed report envelope when plain language is clearer.
