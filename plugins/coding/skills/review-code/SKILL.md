---
name: review-code
description: 'MUST RUN after implementing any code. Spawns review subagents (test, security, code-quality, docs, style) to audit against the plan, siblings, redundancy, and correctness. Triggers when: "review this code", "review my PR", "audit this file", "check the code quality", "review for security". Also use when: finishing an implementation, validating test coverage, pre-merge checks. Examples: "review src/auth", "review the pull request", "audit this module for security issues".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion
argument-hint: [specifier] [--area=test|documentation|code-quality|security|style|all] [--out=reviews]
enforcement: mandatory-post-implementation
orchestration: subagent-spawning
---

# Code Review

Performs comprehensive code review of specified files, directories, PRs, or patterns against established coding standards and best practices. Intelligently adapts review scope based on context and delegates to specialized agents for thorough coverage.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Does not modify or fix any code (use /fix for remediation)
- Does not run tests or builds (focuses on static analysis)
- Does not handle deployment or infrastructure reviews

**When to REJECT**:

- When asked to fix issues (redirect to /fix command)
- When specifier points to binary or non-code files exclusively
- When requesting review of external dependencies or node_modules

## 🛑 Core Review Mandates (apply to EVERY scope, EVERY mode)

These mandates override tone and brevity. Reviewers MUST enforce them on every file examined.

1. **Plan Adherence (MANDATORY)**: Treat the approved plan (PLAN.md, DRAFT.md, DESIGN.md, PR description, or linked spec) as the contract. For every changed file:
   - Map each change back to a specific planned item.
   - Flag any deviation, addition, or omission as a **drift** finding.
   - For each drift, require a documented justification (commit message, PR comment, or inline rationale). If no solid reason is present → severity **critical**. A "good reason" means: a constraint discovered during implementation, a correctness fix, or explicit user/reviewer approval — NOT convenience, scope creep, or "while I was here" cleanup.
   - If no plan exists, the reviewer MUST state this explicitly and treat the PR description / commit messages as the best-available contract.

2. **Redundancy is a Defect** (human-detectable only — linters handle the mechanical cases): Aggressively flag code that does not need to exist. Focus on what ESLint / knip / `tsc` CANNOT see:
   - Defensive checks for conditions that cannot occur (trust internal invariants).
   - Wrapper functions that add no behaviour over what they wrap.
   - Duplicate logic that could reuse an existing helper.
   - Comments that restate what well-named code already says.
   - Backwards-compat shims, feature flags, or fallbacks for hypothetical futures.
   - Over-generalised abstractions with a single caller.
   Every redundant construct is a finding — severity **high** minimum when in production paths. **DO NOT** flag dead branches, unused imports, unused exports, unused parameters, or unreachable code — the linter/knip step owns those.

3. **Sibling Consistency (MANDATORY)**: Before approving any function, class, method (including internal/private ones), or module, search the codebase for siblings serving a similar role — e.g. adapters, mappers, repositories, handlers, clients, formatters, validators. For each match, verify:
   - **Naming**: follows the same verb/noun convention as its siblings (`fetchX` vs `getX`, `toDTO` vs `serialize`).
   - **Parameter shape**: same argument order, same positional vs options-object style, same optional/required split.
   - **Return shape**: same envelope (raw vs `{ data, error }`, sync vs Promise, throwing vs Result).
   - **Logic flow**: same error-handling discipline, same logging posture, same retry/cache behaviour.
   Any divergence without documented justification → severity **high** (critical if it risks silent behavioural surprise in a shared interface like an adapter set). Consistency reduces cognitive load and bug surface — treat new outliers as defects.

4. **Zero Tolerance for Semantic Error**: Treat the code as production-critical. There is NO room for:
   - Incorrect control flow, off-by-ones, wrong operators, swapped arguments.
   - Silent failure modes (swallowed errors, ignored return values).
   - Race conditions, unhandled async rejections, leaked resources.
   - Missing validation at system boundaries (user input, external APIs).
   - Logic that merely *looks* right — reviewers must trace it and prove it.
   Every plausible failure path must be called out. "Probably fine" is not acceptable.

5. **Delegate Mechanical Checks to Tooling**: Reviewers MUST NOT spend effort on anything a linter, compiler, or static analyzer already enforces. Assume `npm run lint`, `tsc --noEmit`, and `knip` run in the pipeline. SKIP these entirely:
   - Type mismatches, missing annotations, unknown properties, signature violations (→ `tsc`).
   - Unused imports, unused variables/exports, unreachable code, dead branches (→ ESLint / knip).
   - Formatting, quote style, semicolons, import ordering (→ Prettier / ESLint).
   Focus human-review bandwidth on semantics, intent, plan fidelity, sibling consistency, and non-mechanical redundancy.

## 📤 Output Format & Priority Levels

Reviews emit **one Markdown file per area** under `<out>/` (default: `reviews/`, relative to project root). The canonical structure for each file is defined by `references/review.template.md` — every subagent and every re-run MUST conform to it exactly.

### Priority taxonomy

| Priority | Meaning |
|----------|---------|
| **P0** | Blocker — security hole, data loss, broken build / startup, must-fix before merge |
| **P1** | High — correctness bug, major standard violation, plan drift without justification |
| **P2** | Medium — maintainability issue, minor bug, unclear contract |
| **P3** | Low — polish, nits, cosmetic concerns |

### Area files & prefixes

| Prefix | File | Area |
|--------|------|------|
| `SEC`  | `<out>/SECURITY.md`    | Security |
| `QUAL` | `<out>/QUALITY.md`     | Code quality |
| `TEST` | `<out>/TESTING.md`     | Tests / coverage |
| `DOCS` | `<out>/DOCS.md`        | Documentation |
| `STYL` | `<out>/STYLE.md`       | Style / lint / naming |
| `CORR` | `<out>/CORRECTNESS.md` | Correctness / semantics |

A top-level `<out>/README.md` index lists every area file with its current verdict.

### Issue ID format

`<PREFIX>-P<n>-<seq>` — sequential per priority within the area file. Examples: `SEC-P0-1`, `SEC-P0-2`, `QUAL-P1-1`, `TEST-P3-4`. IDs are **stable across re-runs** for the same finding; new findings get the next available sequence within their priority.

### Per-file structure (canonical: `references/review.template.md`)

Every area file follows this order:

1. **Frontmatter**: `area`, `prefix`, `reviewed_at`, `files_reviewed_count`.
2. **Title**: `# <AREA> Review`.
3. **Verdict line** (one of):
   - `**Verdict**: ✅ PASS` (single line, exactly this string) — when the file has zero open issues.
   - `**Verdict**: ❌ FAIL — N issues (P0:a, P1:b, P2:c, P3:d)` — counts open (unchecked) issues only.
4. **`## General Status`** — `Files Reviewed` bullet list + 2–4 sentence prose summary. If verdict is ✅ PASS, replace the body with the single line `_No issues found._`.
5. **`## Issues`** — grouped strictly by priority: `### P0 — Blockers`, `### P1 — High`, `### P2 — Medium`, `### P3 — Low`. Empty priority groups may be omitted.
6. **`## Pending Decisions`** — duplicates every issue whose `**Solution**` is `TBD`, with options and a recommendation.

### Issue block format

Each issue is a todo-checkbox list item with three labelled fields:

```markdown
- [ ] ### SEC-P0-1: <one-line summary>

  **Source**: `path/to/file.ts:42-58`
  ```ts
  // representative source lines that triggered the finding
  ```

  **Issue**: <what is wrong, which standard/principle is violated, why it doesn't work>

  **Solution**: <directional fix — enough for an agent to act, NOT a full diff>
```

`Solution` is **direction**, not a full patch. Capture the intent ("validate token at boundary, reject empty input, route through existing `verifyToken` helper") so a downstream `/coding:fix` agent can implement.

### Fixed-issue convention

When an issue is resolved, **both** signals are required:

1. Flip the checkbox from `- [ ]` to `- [x]`.
2. Wrap the heading text in `~~...~~`.

Example:

```markdown
- [x] ### ~~SEC-P0-1: hard-coded credentials in auth handler~~
```

Fixed issues remain in the file as historical record. They are **not** counted in the verdict line.

### Pending Decisions format

When the right fix is unclear or there are multiple credible directions, set `**Solution**: TBD` on the main issue and **duplicate** the issue under `## Pending Decisions` with an `**Options**` block:

```markdown
- [ ] ### QUAL-P1-3: <same summary as main issue>

  **Source**: `path/to/file.ts:88-104`
  ```ts
  // same snippet as main issue
  ```

  **Issue**: <same description as main issue>

  **Options**:
  1. <approach A> — Pros: <…>. Cons: <…>.
  2. <approach B> — Pros: <…>. Cons: <…>.

  **Recommended**: Option <N> — <one-line reason>
```

### Resolution rule

When a Pending Decision is resolved (an option is chosen):

1. Fill in `**Solution**` on the main issue under `## Issues` with the chosen direction.
2. **Delete** the corresponding entry from `## Pending Decisions`.

Never leave both a concrete `**Solution**` on the main issue and a duplicate `Pending Decisions` entry — they are mutually exclusive states.

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Subagent Orchestration

You are a **Review Orchestrator**. Drive the review end-to-end via fire-and-forget `Task` subagents — coordinate analysis, never modify code directly, and consolidate learning. Approach:

- **Strategic Delegation**: assign each scope with clear mission, constraints, success metrics.
- **Parallel Coordination**: run specialized agents autonomously and simultaneously.
- **Learning Orientation**: each subagent writes its own area file under `<out>/` (per `references/review.template.md`); the orchestrator generates `<out>/README.md` plus systemic improvements.
- **Visible Reasoning**: reviewers explain why issues matter, not just what's wrong.
- **Truth Over Ego**: findings are data for system upgrades, not criticism.
- **Scope Management**: adapt depth based on user-selected areas of focus.

#### Standards Applied

The review skill applies the following standards (all references use format `standard:<name>`):

| Scope | Standards |
|-------|-----------|
| All scopes (baseline) | `code-review`, `universal/scan` |
| test | `testing/scan` |
| documentation | `documentation/scan` |
| code-quality | `code-review`, `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan` |
| security | `universal/scan`, `code-review` |
| style | `typescript/scan`, `naming/scan` |

#### Phase 1: Planning (You)

**Context Detection & Scope Selection**: detect execution environment, resolve specifier, determine default scope, discover files, and categorize them by type. See `references/specifier-resolution.md`.

**File filtering by scope**: see `references/specifier-resolution.md` (File Filtering by Scope). Prepare a separate file list per selected scope.

**Pre-pass mechanical scan**: Run `python3 plugins/coding/scripts/scan_potential_violations.py <discovered-files> --category all --before 5 --after 10` and capture the stdout. Slice the report by category and pass the slice into each subagent's dispatch prompt as a "Candidate violations (advisory; verify against scan.md before flagging)" section, using this routing: docs gets `jsdoc-*`; test gets `test-hooks`; code-quality gets `let`; style gets all four; security gets none. Subagents MUST re-check every candidate against the loaded rule files before adding a finding. If `python3` is unavailable, log a warning and proceed without the pre-pass.

#### Phase 2: Execution (Subagents via Task Tool)

Dispatch up to **8 parallel scope review tasks** at any time using the Task tool, one for each selected scope.

- All agents must operate in READ-ONLY mode — no code modifications.
- Agents must report issues with exact `file:line` references and function names.
- Each agent receives its scope-specific standards and file list.

##### TEST Scope (if selected)

Task tool with `subagent_type: "coding:ava-thompson-testing-evangelist"`.

Prompt the agent as a **Testing Quality Analyst** performing comprehensive read-only test analysis. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the rubric paths (`plugins/coding/constitution/standards/code-review.md` and the area-specific scan standards `testing/scan`, `universal/scan`), the output target path, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning, "what we built and why" prose, sibling reviewers' findings, or "the user wants X" / "we decided Y" sentences. Include standards: `testing/scan`, `universal/scan`, `code-review`. The agent performs:

1. **Coverage Analysis**: run coverage tools, identify uncovered lines/branches/statements, specify exact `file:line` locations, recommend specific test cases.
2. **Test Quality Analysis**: analyze structure and organization, identify complex setups, check arrange-act-assert patterns, find unnecessary or redundant tests.
3. **Fixtures & Mocks Analysis**: find duplicate fixture patterns, identify centralizable mocks, recommend consolidation strategies.

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/TESTING.md` (resolved against project root from the `--out` arg, default `reviews/`). Prefix `TEST`. Issue IDs follow `TEST-P<n>-<seq>`. Verdict computed from open (unchecked) issues only. If `<out>/TESTING.md` already exists, read it first and apply the re-run logic: match new findings to prior unchecked entries by `Source` location + `Issue` text; reuse original IDs and any Pending Decisions context; for prior unchecked items with no current match, confirm they no longer apply before dropping; new findings get the next available sequence per priority. Rewrite the file in full. Return a short completion message to the orchestrator with the file path, open-issue counts per priority, and `context_level`.

##### DOCUMENTATION Scope (if selected)

Task tool with `subagent_type: "general-purpose"`.

Prompt the agent as a **Documentation Quality Analyst** performing read-only documentation review. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the rubric paths (`plugins/coding/constitution/standards/code-review.md` and `documentation/scan`), the output target path, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning, "what we built and why" prose, sibling reviewers' findings, or "the user wants X" / "we decided Y" sentences. Include standard: `documentation/scan`. The agent checks:

1. JSDoc/TSDoc completeness for all exported functions, classes, interfaces.
2. Inline comments for complex logic.
3. README accuracy and completeness.
4. API documentation if applicable.
5. Example usage and code samples.
6. Type definitions documentation.

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/DOCS.md`. Prefix `DOCS`. Issue IDs follow `DOCS-P<n>-<seq>`. Apply the same re-run logic as above (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

##### CODE-QUALITY Scope (if selected)

Task tool with `subagent_type: "coding:marcus-williams-code-quality"`.

Prompt the agent as a **Code Quality Analyst** performing read-only code quality review. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the path to the approved plan document (file path only — do NOT summarize or paraphrase its contents), the rubric paths (`plugins/coding/constitution/standards/code-review.md` plus `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan`), the output target paths, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning narrative, "what we built and why" prose, sibling reviewers' findings during this initial pass, or "the user wants X" / "we decided Y" sentences. The agent MUST apply the Core Review Mandates (Plan Adherence, Redundancy, Sibling Consistency, Zero Tolerance, Delegate Mechanical Checks) defined at the top of this skill. Include standards: `code-review`, `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan`. The agent performs:

0. **Plan Adherence Check (MANDATORY FIRST STEP)**: locate the approved plan (PLAN.md, DRAFT.md, DESIGN.md, linked spec, or PR description). For each changed file, map every change to a planned item. Flag drifts (additions, deviations, omissions). For each drift, evaluate whether a solid documented justification exists (commit message, PR comment, inline rationale). Drift without justification → severity **critical**. Drift with weak justification (convenience, scope creep) → severity **high**. If no plan is available, state this and use PR description as best-available contract.
1. **Sibling Consistency Check (MANDATORY)**: for every function, class, method (INCLUDING internal/private members), and module, Grep the codebase for siblings of similar role (adapters, mappers, repositories, handlers, clients, formatters, validators, etc.). Compare naming conventions, parameter shape (order, options-object vs positional, optional/required split), return shape (envelope style, sync vs async, throw vs Result), and internal logic pattern (error handling, logging, retry/cache). Any unjustified divergence → severity **high** (**critical** for adapter-sets or other shared-interface families where inconsistency causes silent behavioural surprise).
2. **Non-Mechanical Redundancy**: scan for redundancy that linters CANNOT detect — defensive checks for impossible conditions, wrapper functions with no added behaviour, duplicate logic ignoring an existing helper, comments restating code, backwards-compat shims, speculative fallbacks, over-generalised abstractions with a single caller. Every genuine redundancy is a finding (high+ in production paths). DO NOT flag dead branches, unused imports/exports, unreachable code — those belong to the `style` scope / linter.
3. **Semantic Correctness (Zero Tolerance)**: trace every non-trivial control flow. Flag off-by-ones, swapped arguments, wrong operators, silent failures, swallowed errors, unhandled rejections, race conditions, leaked resources, missing boundary validation. "Probably fine" is not acceptable — prove correctness or flag it.
4. **Code Structure**: organization, modularity, separation of concerns.
5. **Naming Conventions**: compliance with naming standards (beyond lint rules — domain-appropriate, sibling-aligned names).
6. **Complexity**: functions/methods needing refactoring.
7. **DRY Violations**: code duplication (where linters miss the semantic overlap).
8. **Error Handling**: error handling patterns and logging.
9. **Performance**: performance concerns.
10. **Accessibility**: accessibility issues (if applicable).
11. **Architecture**: architectural patterns and design decisions.

**DO NOT** re-check what tooling already enforces — skip type errors (→ `tsc`), unused imports/vars/exports, unreachable code, dead branches (→ ESLint / knip), and formatting (→ Prettier). The `style` scope and CI lint step own these. Spend bandwidth on semantics, intent, sibling fit, and plan fidelity.

**Output**: write the area file using `references/review.template.md`. Code-quality findings are split between two area files based on category:

- **Correctness/semantics findings** (off-by-ones, swapped arguments, wrong operators, swallowed errors, race conditions, plan-drift, semantic bugs) → `<out>/CORRECTNESS.md`, prefix `CORR`, IDs `CORR-P<n>-<seq>`.
- **All other quality findings** (sibling-consistency, non-mechanical redundancy, structure, naming, complexity, DRY, error-handling posture, performance, accessibility, architecture) → `<out>/QUALITY.md`, prefix `QUAL`, IDs `QUAL-P<n>-<seq>`.

For each target file, apply the re-run logic (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions, drop only after confirming no longer applicable, new findings get next available sequence). Rewrite each file in full. Return a short completion message listing both file paths with open-issue counts per priority and `context_level`.

##### SECURITY Scope (if selected)

Task tool with `subagent_type: "coding:nina-petrov-security-champion"`.

Prompt the agent as a **Security Analyst** performing read-only security review. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the rubric paths (`plugins/coding/constitution/standards/code-review.md` and `universal/scan`), the output target path, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning, "what we built and why" prose, sibling reviewers' findings, or "the user wants X" / "we decided Y" sentences. Include standards: `universal/scan`, `code-review`. The agent checks:

1. **Injection Vulnerabilities**: SQL injection, XSS, command injection.
2. **Authentication/Authorization**: auth implementation review.
3. **Input Validation**: input sanitization and validation.
4. **Sensitive Data**: exposed secrets, logging sensitive data.
5. **Dependencies**: known vulnerabilities.
6. **CORS & Headers**: security headers configuration.
7. **Crypto**: proper encryption usage.

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/SECURITY.md`. Prefix `SEC`. Issue IDs follow `SEC-P<n>-<seq>`. Apply the re-run logic (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

##### STYLE Scope (if selected)

Task tool with `subagent_type: "general-purpose"`.

Prompt the agent as a **Style & Linting Analyst** performing read-only style review. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the rubric paths (`plugins/coding/constitution/standards/code-review.md` plus `typescript/scan`, `naming/scan`), the output target path, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning, "what we built and why" prose, sibling reviewers' findings, or "the user wants X" / "we decided Y" sentences. Include standards: `typescript/scan`, `naming/scan`. The agent performs:

1. Identify project package.json files (project and monorepo levels).
2. Extract linting scripts (lint, lint:fix, eslint, prettier).
3. Execute linting scripts and capture output.
4. Parse linter output for `file:line` references.
5. Report all linting issues found.
6. Check naming convention compliance.

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/STYLE.md`. Prefix `STYL`. Issue IDs follow `STYL-P<n>-<seq>`. Apply the re-run logic (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

#### Phase 3: Index & Report Generation (You)

1. **Collect completion messages** from each Task tool execution (file path written, open-issue counts per priority, `context_level`). If any agent reports failure, log it and note the corresponding area file is incomplete or missing.
2. **Verify each expected area file** exists at its target path under `<out>/` and starts with the canonical verdict line per `references/review.template.md`. Surface any structural problems rather than silently aggregating.
3. **Compute aggregate counts** from each file's verdict line: totals per priority across `<out>/SECURITY.md`, `<out>/QUALITY.md`, `<out>/TESTING.md`, `<out>/DOCS.md`, `<out>/STYLE.md`, `<out>/CORRECTNESS.md`. List which areas are FAIL vs PASS.
4. **Systemic Pattern Analysis** (across area files): recurring issues, root causes, process gaps, system improvements, learning assets. Capture this as a short addendum at the end of `<out>/README.md`.
5. **Determine overall status** from open-issue counts:
   - Any P0 open: **FAIL**
   - P1 open, no P0: **REQUIRES_CHANGES**
   - Only P2/P3 open: **PASS_WITH_SUGGESTIONS**
   - All areas verdict ✅ PASS: **PASS**
6. **Generate or refresh `<out>/README.md` index** with one row per area file (verdict pulled verbatim from each file's first verdict line, link to the file), reviewed timestamp, aggregate priority counts, the systemic improvements section, and overall status. On re-runs, **rewrite** the index entirely from current area files.

### Step 2: Reporting

Render the final summary using the format matching the runtime mode:

- **CI / Non-Interactive** vs **Interactive** output templates and shared fields → see `references/output-formats.md`.

The orchestrator reports the **per-area file listing** (one line per area, with verdict), aggregate counts per priority, and the path to `<out>/README.md`. Detailed findings live in the area files — not in the console summary.

## 📝 Examples

For invocation examples covering single/multi-scope review, glob/PR/git/package specifiers, CI vs Interactive, clean-pass output, Pending Decisions output, and error handling — see `references/examples.md`.
