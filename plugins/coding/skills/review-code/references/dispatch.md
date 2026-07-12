# Area Dispatch Contracts

How the orchestrator dispatches one read-only review subagent per selected
area via the Task tool.

## Contents

- [Prompt hygiene (all areas)](#prompt-hygiene-all-areas)
- [Standards per area](#standards-per-area)
- [Scan candidate routing](#scan-candidate-routing)
- [Re-run logic (all areas)](#re-run-logic-all-areas)
- [Completion message (all areas)](#completion-message-all-areas)
- [Area contracts](#area-contracts)

## Prompt hygiene (all areas)

Begin every dispatch prompt with this neutral preamble verbatim:

> You are an independent reviewer. Treat the artifact as unfamiliar code.
> Apply the rubric without assuming the author's intent was correct.

Pass only: the area/file-set name, the file paths to analyze, the rubric
paths (`plugins/coding/constitution/standards/code-review.md` plus the
area-specific scan standards below), the mandates file
(`references/mandates.md`), the output target path, the template path
(`references/review.template.md`), and the area's scan-candidate slice. For
code-quality only, also pass the path to the approved plan document — the
file path only, never a summary or paraphrase of its contents.

<IMPORTANT>Do not include parent-conversation framing, the implementer's
reasoning, "what we built and why" prose, sibling reviewers' findings, or
"the user wants X" / "we decided Y" sentences. All agents operate read-only —
no code modifications — and must report issues with exact `file:line`
references and function names.</IMPORTANT>

## Standards per area

All standards use the format `standard:<name>`; every area also receives the
baseline `code-review` and `universal/scan`.

| Area | Standards |
|------|-----------|
| test | `testing/scan`, `universal/scan`, `code-review` |
| documentation | `documentation/scan`, `code-review` |
| code-quality | `code-review`, `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan` |
| security | `universal/scan`, `code-review` |
| style | `typescript/scan`, `naming/scan`, `code-review` |

## Scan candidate routing

Slice the pre-pass scanner output by category and pass each area its slice as
"Candidate violations (advisory; verify against scan.md before flagging)":

- **documentation**: `jsdoc-uppercase`, `jsdoc-fullstop`, `comment-rule-id`,
  `author-stamp`, `section-name` (DOC-* rules).
- **test**: `test-hooks`, `test-mock-stub`, `test-conditional-skip`,
  `aaa-comment`, `test-title-convention`, `test-file-naming`,
  `test-dynamic-import`, `undefined-override` (TST-* rules).
- **code-quality**: `let`, `conditional-spread`, `dynamic-import-static`,
  `catch-error-defensive`, `escape-cast`, `star-import-export`,
  `silent-catch`, `unit-suffix`, `abbreviation-denylist`,
  `canonical-param-name`, `py-type-ignore-format`, `py-future-annotations`,
  `py-missing-all` (TYP-*, FUNC-*, NAM-*, ERR-*, PYT-* rules).
- **style**: all categories.
- **security**: none.

Subagents must re-check every candidate against the loaded rule files before
adding a finding — the scanner is advisory, not authoritative.

## Re-run logic (all areas)

When the target area file already exists, the subagent reads it first, then:

- matches new findings to prior unchecked entries by `Source` location plus
  `Issue` text, reusing original IDs and any Pending Decisions context;
- confirms prior unchecked items with no current match no longer apply before
  dropping them;
- assigns new findings the next available sequence within their priority;
- rewrites the file in full.

## Completion message (all areas)

Each subagent returns a short completion message — not the findings — with
the area file path(s) written, open-issue counts per priority, and
`context_level`. Findings live in the area files.

## Area contracts

### test

- `subagent_type: "coding:ava-thompson-testing-evangelist"`, prompted as a
  Testing Quality Analyst.
- Performs: coverage analysis (run coverage tools, identify uncovered
  lines/branches with exact `file:line`, recommend specific test cases); test
  quality analysis (structure, complex setups, arrange-act-assert, redundant
  tests); fixtures and mocks analysis (duplicate fixtures, centralizable
  mocks, consolidation strategy).
- Output: `<out>/TESTING.md`, prefix `TEST`.

### documentation

- `subagent_type: "general-purpose"`, prompted as a Documentation Quality
  Analyst.
- Checks: JSDoc/TSDoc completeness for all exports, inline comments for
  complex logic, README accuracy, API documentation, example usage, type
  definition documentation.
- Output: `<out>/DOCS.md`, prefix `DOCS`.

### code-quality

- `subagent_type: "coding:marcus-williams-code-quality"`, prompted as a Code
  Quality Analyst. Must apply every mandate in `references/mandates.md`.
- Performs, in order: plan adherence check (mandatory first step — locate the
  plan, map every change, flag drifts with severities per mandate 1); sibling
  consistency check (Grep for same-role siblings, compare naming, parameter
  shape, return shape, logic flow); non-mechanical redundancy; semantic
  correctness with zero tolerance; then structure, naming, complexity, DRY,
  error handling, performance, accessibility, and architecture. Never
  re-check what tooling enforces (mandate 5).
- Output — findings split across two files:
  - correctness/semantics findings (off-by-ones, swapped arguments, wrong
    operators, swallowed errors, race conditions, plan drift, semantic bugs)
    → `<out>/CORRECTNESS.md`, prefix `CORR`;
  - all other quality findings (sibling consistency, redundancy, structure,
    naming, complexity, DRY, error-handling posture, performance,
    accessibility, architecture) → `<out>/QUALITY.md`, prefix `QUAL`.

### security

- `subagent_type: "coding:nina-petrov-security-champion"`, prompted as a
  Security Analyst.
- Checks: injection (SQL/XSS/command), authentication and authorization,
  input validation, sensitive data exposure (secrets, logging), dependency
  vulnerabilities, CORS and security headers, crypto usage.
- Output: `<out>/SECURITY.md`, prefix `SEC`.

### style

- `subagent_type: "general-purpose"`, prompted as a Style & Linting Analyst.
- Performs: identify package.json files (project and monorepo levels),
  extract lint scripts (lint, lint:fix, eslint, prettier), execute them and
  capture output, parse `file:line` references, report all linting issues,
  check naming convention compliance.
- Output: `<out>/STYLE.md`, prefix `STYL`.
