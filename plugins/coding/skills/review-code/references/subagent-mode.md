# Subagent Mode Workflow

Use this workflow when the session context does **not** contain `**Agent Teams**: enabled`. This is the Subagent Mode (fallback) branch of Step 2.

You are a **Review Orchestrator**. You coordinate code review to improve both the code and the system. You never modify code directly, only delegate analysis and consolidate learning. Your approach emphasizes:

- **Strategic Delegation**: Assign review with clear mission, constraints, success metrics
- **Parallel Coordination**: Run specialized agents autonomously and simultaneously
- **Learning Orientation**: Each subagent writes its own area file under `<out>/` (per `references/review.template.md`); orchestrator generates the `<out>/README.md` index plus systemic improvements
- **Visible Reasoning**: Reviewers explain why issues matter, not just what's wrong
- **Truth Over Ego**: Findings are data for system upgrades, not criticism
- **Scope Management**: Adapt depth based on user-selected areas of focus

## Standards Applied

The review skill applies the following standards (all references use format `standard:<name>`):

| Scope | Standards |
|-------|-----------|
| All scopes (baseline) | `code-review`, `universal/scan` |
| test | `testing/scan` |
| documentation | `documentation/scan` |
| code-quality | `code-review`, `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan` |
| security | `universal/scan`, `code-review` |
| style | `typescript/scan`, `naming/scan` |

## Phase 1: Planning (You)

**Context Detection & Scope Selection**: Use the same scope selection logic as Team Mode -- detect execution environment, resolve specifier, determine default scope, discover files, and categorize them by type. See `references/specifier-resolution.md`.

**File filtering by scope**: see `references/specifier-resolution.md` (Subagent-Mode File Filtering by Scope).

Prepare file lists for each selected scope.

**Pre-pass mechanical scan**: Run `python3 plugins/coding/scripts/scan_potential_violations.py <discovered-files> --category all --before 5 --after 10` and capture the stdout. Slice the report by category and pass the slice into each subagent's dispatch prompt as a "Candidate violations (advisory; verify against scan.md before flagging)" section, using the same routing as Team Mode (docs gets `jsdoc-*`; test gets `test-hooks`; code-quality gets `let`; style gets all four; security gets none). Subagents MUST re-check every candidate against the loaded rule files before adding a finding. If `python3` is unavailable, log a warning and proceed without the pre-pass.

## Phase 2: Execution (Subagents via Task Tool)

Dispatch up to 5 scope review tasks in parallel using the Task tool, one for each selected scope.

- **All agents must operate in READ-ONLY mode** -- no code modifications
- **Agents must report issues with exact file:line references**, function names
- Each agent receives its scope-specific standards and file list

### For TEST Scope (if selected)

Task tool with `subagent_type: "coding:ava-thompson-testing-evangelist"`

Prompt the agent as a **Testing Quality Analyst** performing comprehensive read-only test analysis. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the rubric paths (`plugins/coding/constitution/standards/code-review.md` and the area-specific scan standards `testing/scan`, `universal/scan`), the output target path, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning, "what we built and why" prose, sibling reviewers' findings, or "the user wants X" / "we decided Y" sentences. Include standards: `testing/scan`, `universal/scan`, `code-review`. The agent performs:

1. **Coverage Analysis**: Run coverage tools, identify uncovered lines/branches/statements, specify exact file:line locations, recommend specific test cases
2. **Test Quality Analysis**: Analyze structure and organization, identify complex setups, check arrange-act-assert patterns, find unnecessary or redundant tests
3. **Fixtures & Mocks Analysis**: Find duplicate fixture patterns, identify centralizable mocks, recommend consolidation strategies

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/TESTING.md` (resolved against project root from the `--out` arg, default `reviews/`). Prefix `TEST`. Issue IDs follow `TEST-P<n>-<seq>`. Verdict is computed from open (unchecked) issues only. If `<out>/TESTING.md` already exists, read it first and apply the re-run logic: match new findings to prior unchecked entries by `Source` location + `Issue` text; reuse original IDs and any Pending Decisions context; for prior unchecked items with no current match, confirm they no longer apply before dropping; new findings get the next available sequence per priority. Rewrite the file in full. Return a short completion message to the orchestrator with the file path, open-issue counts per priority, and `context_level`.

### For DOCUMENTATION Scope (if selected)

Task tool with `subagent_type: "general-purpose"`

Prompt the agent as a **Documentation Quality Analyst** performing read-only documentation review. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the rubric paths (`plugins/coding/constitution/standards/code-review.md` and `documentation/scan`), the output target path, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning, "what we built and why" prose, sibling reviewers' findings, or "the user wants X" / "we decided Y" sentences. Include standard: `documentation/scan`. The agent checks:

1. JSDoc/TSDoc completeness for all exported functions, classes, interfaces
2. Inline comments for complex logic
3. README accuracy and completeness
4. API documentation if applicable
5. Example usage and code samples
6. Type definitions documentation

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/DOCS.md`. Prefix `DOCS`. Issue IDs follow `DOCS-P<n>-<seq>`. Apply the same re-run logic as above (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

### For CODE-QUALITY Scope (if selected)

Task tool with `subagent_type: "coding:marcus-williams-code-quality"`

Prompt the agent as a **Code Quality Analyst** performing read-only code quality review. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the path to the approved plan document (file path only — do NOT summarize or paraphrase its contents), the rubric paths (`plugins/coding/constitution/standards/code-review.md` plus `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan`), the output target paths, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning narrative, "what we built and why" prose, sibling reviewers' findings during this initial pass, or "the user wants X" / "we decided Y" sentences. The agent MUST apply the Core Review Mandates (Plan Adherence, Redundancy, Sibling Consistency, Zero Tolerance, Delegate Mechanical Checks) defined at the top of this skill. Include standards: `code-review`, `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan`. The agent performs:

0. **Plan Adherence Check (MANDATORY FIRST STEP)**: Locate the approved plan (PLAN.md, DRAFT.md, DESIGN.md, linked spec, or PR description). For each changed file, map every change to a planned item. Flag drifts (additions, deviations, omissions). For each drift, evaluate whether a solid documented justification exists (commit message, PR comment, inline rationale). Drift without justification → severity **critical**. Drift with weak justification (convenience, scope creep) → severity **high**. If no plan is available, state this and use PR description as best-available contract.
1. **Sibling Consistency Check (MANDATORY)**: For every function, class, method (INCLUDING internal/private members), and module, Grep the codebase for siblings of similar role (adapters, mappers, repositories, handlers, clients, formatters, validators, etc.). Compare naming conventions, parameter shape (order, options-object vs positional, optional/required split), return shape (envelope style, sync vs async, throw vs Result), and internal logic pattern (error handling, logging, retry/cache). Any unjustified divergence → severity **high** (**critical** for adapter-sets or other shared-interface families where inconsistency causes silent behavioural surprise).
2. **Non-Mechanical Redundancy**: Scan for redundancy that linters CANNOT detect — defensive checks for impossible conditions, wrapper functions with no added behaviour, duplicate logic ignoring an existing helper, comments restating code, backwards-compat shims, speculative fallbacks, over-generalised abstractions with a single caller. Every genuine redundancy is a finding (high+ in production paths). DO NOT flag dead branches, unused imports/exports, unreachable code — those belong to the `style` scope / linter.
3. **Semantic Correctness (Zero Tolerance)**: Trace every non-trivial control flow. Flag off-by-ones, swapped arguments, wrong operators, silent failures, swallowed errors, unhandled rejections, race conditions, leaked resources, missing boundary validation. "Probably fine" is not acceptable — prove correctness or flag it.
4. **Code Structure**: Organization, modularity, separation of concerns
5. **Naming Conventions**: Compliance with naming standards (beyond lint rules — domain-appropriate, sibling-aligned names)
6. **Complexity**: Functions/methods needing refactoring
7. **DRY Violations**: Code duplication (where linters miss the semantic overlap)
8. **Error Handling**: Error handling patterns and logging
9. **Performance**: Performance concerns
10. **Accessibility**: Accessibility issues (if applicable)
11. **Architecture**: Architectural patterns and design decisions

**DO NOT** re-check what tooling already enforces — skip type errors (→ `tsc`), unused imports/vars/exports, unreachable code, dead branches (→ ESLint / knip), and formatting (→ Prettier). The `style` scope and CI lint step own these. Spend bandwidth on semantics, intent, sibling fit, and plan fidelity.

**Output**: write the area file using `references/review.template.md`. Code-quality findings are split between two area files based on category:

- **Correctness/semantics findings** (off-by-ones, swapped arguments, wrong operators, swallowed errors, race conditions, plan-drift, semantic bugs) → `<out>/CORRECTNESS.md`, prefix `CORR`, IDs `CORR-P<n>-<seq>`.
- **All other quality findings** (sibling-consistency, non-mechanical redundancy, structure, naming, complexity, DRY, error-handling posture, performance, accessibility, architecture) → `<out>/QUALITY.md`, prefix `QUAL`, IDs `QUAL-P<n>-<seq>`.

For each target file, apply the re-run logic (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions, drop only after confirming no longer applicable, new findings get next available sequence). Rewrite each file in full. Return a short completion message listing both file paths with open-issue counts per priority and `context_level`.

### For SECURITY Scope (if selected)

Task tool with `subagent_type: "coding:nina-petrov-security-champion"`

Prompt the agent as a **Security Analyst** performing read-only security review. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the rubric paths (`plugins/coding/constitution/standards/code-review.md` and `universal/scan`), the output target path, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning, "what we built and why" prose, sibling reviewers' findings, or "the user wants X" / "we decided Y" sentences. Include standards: `universal/scan`, `code-review`. The agent checks:

1. **Injection Vulnerabilities**: SQL injection, XSS, command injection
2. **Authentication/Authorization**: Auth implementation review
3. **Input Validation**: Input sanitization and validation
4. **Sensitive Data**: Exposed secrets, logging sensitive data
5. **Dependencies**: Known vulnerabilities
6. **CORS & Headers**: Security headers configuration
7. **Crypto**: Proper encryption usage

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/SECURITY.md`. Prefix `SEC`. Issue IDs follow `SEC-P<n>-<seq>`. Apply the re-run logic (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

### For STYLE Scope (if selected)

Task tool with `subagent_type: "general-purpose"`

Prompt the agent as a **Style & Linting Analyst** performing read-only style review. Begin the dispatch prompt with the neutral preamble verbatim: "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct." Pass only: the scope/file-set name, the file paths to analyze, the rubric paths (`plugins/coding/constitution/standards/code-review.md` plus `typescript/scan`, `naming/scan`), the output target path, and the template path `references/review.template.md`. Do NOT include parent-conversation framing, the implementer's reasoning, "what we built and why" prose, sibling reviewers' findings, or "the user wants X" / "we decided Y" sentences. Include standards: `typescript/scan`, `naming/scan`. The agent performs:

1. Identify project package.json files (project and monorepo levels)
2. Extract linting scripts (lint, lint:fix, eslint, prettier)
3. Execute linting scripts and capture output
4. Parse linter output for file:line references
5. Report all linting issues found
6. Check naming convention compliance

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/STYLE.md`. Prefix `STYL`. Issue IDs follow `STYL-P<n>-<seq>`. Apply the re-run logic (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

## Phase 3: Index & Report Generation (You)

1. **Collect completion messages** from each Task tool execution (file path written, open-issue counts per priority, `context_level`). If any agent reports failure, log it and note that the corresponding area file is incomplete or missing.
2. **Verify each expected area file** exists at its target path under `<out>/` and starts with the canonical verdict line per `references/review.template.md`. Surface any structural problems rather than silently aggregating.
3. **Compute aggregate counts** from each file's verdict line: totals per priority across `<out>/SECURITY.md`, `<out>/QUALITY.md`, `<out>/TESTING.md`, `<out>/DOCS.md`, `<out>/STYLE.md`, `<out>/CORRECTNESS.md`. List which areas are FAIL vs PASS.
4. **Systemic Pattern Analysis** (across area files): recurring issues, root causes, process gaps, system improvements, learning assets. Capture this as a short addendum at the end of `<out>/README.md`.
5. **Determine overall status** from open-issue counts:
   - Any P0 open: **FAIL**
   - P1 open, no P0: **REQUIRES_CHANGES**
   - Only P2/P3 open: **PASS_WITH_SUGGESTIONS**
   - All areas verdict ✅ PASS: **PASS**
6. **Generate or refresh `<out>/README.md` index** with one row per area file (verdict pulled verbatim from each file's first verdict line, link to the file), reviewed timestamp, aggregate priority counts, the systemic improvements section, and overall status. On re-runs, **rewrite** the index entirely from current area files.
