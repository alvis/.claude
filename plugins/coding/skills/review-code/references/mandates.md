# Core Review Mandates

These mandates apply to every area, every mode, and every file examined. They
override tone and brevity. Every dispatch prompt names this file so reviewers
enforce all five.

## 1. Plan adherence

Treat the approved plan (PLAN.md, DRAFT.md, DESIGN.md, PR description, or
linked spec) as the contract. For every changed file:

- Map each change back to a specific planned item.
- Flag any deviation, addition, or omission as a **drift** finding.
- For each drift, require a documented justification (commit message, PR
  comment, or inline rationale). No solid reason present → severity
  **critical**. A "good reason" means a constraint discovered during
  implementation, a correctness fix, or explicit user/reviewer approval — not
  convenience, scope creep, or "while I was here" cleanup.
- If no plan exists, state this explicitly and treat the PR description and
  commit messages as the best-available contract.

## 2. Redundancy is a defect

Aggressively flag code that does not need to exist — but only the
human-detectable cases linters cannot see:

- Defensive checks for conditions that cannot occur (trust internal
  invariants).
- Wrapper functions that add no behavior over what they wrap.
- Duplicate logic that could reuse an existing helper.
- Comments that restate what well-named code already says.
- Backwards-compat shims, feature flags, or fallbacks for hypothetical
  futures.
- Over-generalized abstractions with a single caller.

Every redundant construct is a finding — severity **high** minimum in
production paths. Do not flag dead branches, unused imports/exports, unused
parameters, or unreachable code — the linter owns those.

## 3. Sibling consistency

Before approving any function, class, method (including internal/private
ones), or module, search the codebase for siblings serving a similar role —
adapters, mappers, repositories, handlers, clients, formatters, validators.
For each match, verify:

- **Naming**: same verb/noun convention as siblings (`fetchX` vs `getX`,
  `toDTO` vs `serialize`).
- **Parameter shape**: same argument order, positional vs options-object
  style, optional/required split.
- **Return shape**: same envelope (raw vs `{ data, error }`, sync vs Promise,
  throwing vs Result).
- **Logic flow**: same error-handling discipline, logging posture,
  retry/cache behavior.

Any divergence without documented justification → severity **high**
(**critical** when it risks silent behavioral surprise in a shared interface
such as an adapter set). Consistency reduces cognitive load and bug surface —
treat new outliers as defects.

## 4. Zero tolerance for semantic error

Treat the code as production-critical. There is no room for:

- Incorrect control flow, off-by-ones, wrong operators, swapped arguments.
- Silent failure modes (swallowed errors, ignored return values).
- Race conditions, unhandled async rejections, leaked resources.
- Missing validation at system boundaries (user input, external APIs).
- Logic that merely *looks* right — trace it and prove it.

Every plausible failure path must be called out. "Probably fine" is not
acceptable.

## 5. Delegate mechanical checks to tooling

Spend no effort on anything a linter, compiler, or static analyzer already
enforces. Assume `npm run lint` and `tsc --noEmit` run in the pipeline. Skip
entirely:

- Type mismatches, missing annotations, unknown properties, signature
  violations (→ `tsc`).
- Unused imports, unused variables/exports, unreachable code, dead branches
  (→ ESLint).
- Formatting, quote style, semicolons, import ordering (→ Prettier/ESLint).

Focus human-review bandwidth on semantics, intent, plan fidelity, sibling
consistency, and non-mechanical redundancy.
