---
name: review-code
description: 'MUST RUN after implementing any code. Spawns review subagents (test, security, code-quality, docs, style) to audit against the plan, siblings, redundancy, and correctness. Triggers when: "review this code", "review my PR", "audit this file", "check the code quality", "review for security". Also use when: finishing an implementation, validating test coverage, pre-merge checks. Examples: "review src/auth", "review the pull request", "audit this module for security issues".'
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch, AskUserQuestion, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
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

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.

- **If present**: Use **Team Mode** (Step 2A)
- **If absent**: Use **Subagent Mode** (Step 2B)

### Step 2A: Team Mode (Agent Teams enabled)

#### Phase 1: Planning & Scope Selection (Lead)

**Context Detection & Scope Selection**:

**Detect execution environment**:

- Check if CI/non-interactive mode (no user interaction available)
- Check if interactive mode (user can respond to prompts)

**Resolve specifier** (if provided):

The `<specifier>` argument identifies which files to review through multiple methods:

1. **File paths**: Direct path to specific file(s) - `src/auth/auth.service.ts`
2. **Directory paths**: Review all code files in directory - `src/api/`
3. **Glob patterns**: Pattern matching - `**/*.spec.ts`, `src/**/*.{ts,tsx}`
4. **Package names**: Find all imports/usage - `@myapp/auth`, `lodash`
5. **PR numbers**: Review PR changes - `PR#123`
6. **Git ranges**: Review commits - `HEAD~3..HEAD`
7. **Command output**: Dynamic file lists - `$(git diff --cached --name-only)`
8. **Omitted**: Review entire codebase or auto-detect from current context

**Determine default scope based on context**:

1. If `--area` parameter provided → Use specified scope(s)
2. If specifier includes test files (`**/*.spec.ts`, `**/*.test.ts`) → Default to `test` scope
3. If specifier includes documentation files (`**/*.md`, `**/README*`) → Default to `documentation` scope
4. If working in interactive mode and no clear context → Ask user via AskUserQuestion (multiSelect):
   - Options: test, documentation, code-quality, security, style, all
   - Default: all
5. If in CI mode and no scope specified → Default to `all`

**File Discovery**:

Use Glob/Grep to discover files matching the specifier. Categorize by type:

- Source: *.ts,*.tsx
- Tests: *.spec.ts,*.spec.tsx
- Docs: *.md, README
- Config: *.json,*.yaml

Filter files by selected scopes (pass file paths to teammates, not file contents).

#### Phase 2: Team Setup & Execution

1. **Create team**: `TeamCreate` with name `review-team`

2. **Initialize agent pool registry** tracking:
   - Name (agent identifier)
   - Role (reviewer type: test, security, code-quality, documentation, style)
   - Model (opus for specialized, haiku for general)
   - Context Level (%)
   - Status (working, idle, retired)

3. **Spawn specialized reviewer teammates** (one per selected scope):

   For each selected scope, spawn appropriate agent:

   - **test scope**: `Task` with `team_name="review-team"`, `name="test-reviewer"`, `subagent_type="coding:ava-thompson-testing-evangelist"`, `model="opus"`
   - **security scope**: `Task` with `team_name="review-team"`, `name="security-reviewer"`, `subagent_type="coding:nina-petrov-security-champion"`, `model="opus"`
   - **code-quality scope**: `Task` with `team_name="review-team"`, `name="quality-reviewer"`, `subagent_type="coding:marcus-williams-code-quality"`, `model="opus"`
   - **documentation scope**: `Task` with `team_name="review-team"`, `name="docs-reviewer"`, `subagent_type="general-purpose"`, `model="opus"`
   - **style scope**: `Task` with `team_name="review-team"`, `name="style-reviewer"`, `subagent_type="general-purpose"`, `model="opus"`

4. **Create review tasks**: `TaskCreate` for each scope with:
   - Subject: "Review [scope] (e.g., test, security)"
   - Description: Full instructions including:
     - **Core Review Mandates** (plan adherence, non-mechanical redundancy, sibling consistency across adapters/mappers/etc., zero-tolerance semantics, delegate mechanical checks to lint/tsc/knip) — see top of skill
     - Path to the approved plan document (PLAN.md/DRAFT.md/DESIGN.md/PR description) for drift checking
     - File paths to analyze (NOT file contents)
     - Standard file paths to consult (e.g., `/absolute/path/to/standards/testing.md`)
     - **Output target**: the absolute path to the area file under `<out>/` (e.g., `<project-root>/reviews/SECURITY.md`) — the subagent writes this file directly
     - **Template**: `references/review.template.md` — the canonical structure to follow (frontmatter, verdict, General Status, Issues grouped P0→P3, Pending Decisions)
     - **Re-run instruction**: if the target file already exists, read it first; cross-reference new findings against any unchecked (`- [ ]`) issues by `Source` location + `Issue` text; reuse the original `<PREFIX>-P<n>-<seq>` ID for matched issues; preserve any Pending Decisions context on matched issues; for prior unchecked issues with no current match, confirm the issue no longer applies before dropping it; new unmatched findings get the next available sequence per priority
     - Instruction to calculate and report `context_level` from token usage in the completion message back to the lead

5. **Assign ownership**: `TaskUpdate` to set owner for each task to corresponding reviewer

#### Phase 3: Review Cycle

1. **Wait for completion messages** from all reviewers via `SendMessage`

2. **Track context levels**: Each reviewer reports their `context_level` calculated as:
   - `context_level = (input_tokens / context_window_size) × 100`
   - Based on real token usage from conversation metadata

3. **Update agent pool registry** with reported context levels

4. **Collect review reports** via `TaskGet` for each completed task

5. **Optional: Cross-scope review round** (if multiple critical issues found):
   - Check agent pool for idle reviewers with `context_level < 50%`
   - If eligible reviewers exist → Reuse via `SendMessage` with cross-scope review task
   - If not → Spawn fresh reviewers with appropriate specialization
   - Task: Check for conflicts or interactions between scope findings
   - Wait for cross-review completion messages

#### Phase 4: Index & Cleanup

1. **Verify per-area files**:
   - For every scope spawned, confirm the corresponding `<out>/<AREA>.md` file exists and conforms to `references/review.template.md` (frontmatter + verdict line + General Status + Issues + Pending Decisions).
   - If a file is missing, surface the failure rather than silently aggregating.

2. **Generate or refresh `<out>/README.md` index**:
   - One row per area file, with the verdict pulled verbatim from the file's first verdict line (`✅ PASS` or `❌ FAIL — N issues (P0:a, P1:b, P2:c, P3:d)`).
   - Link each area name to its file (e.g., `[Security](./SECURITY.md)`).
   - Include reviewed timestamp and aggregate counts (P0/P1/P2/P3 totals across files).
   - On re-runs, **rewrite** this index entirely from the current area files.

3. **Print console summary**:
   - Counts per priority across all areas.
   - List of FAIL areas with their open-issue counts.
   - Path to `<out>/README.md`.
   - Agent lifecycle statistics (agents spawned, reused, retired).

4. **Shutdown teammates**:
   - Send `SendMessage` with type `shutdown_request` to all active teammates
   - Wait for shutdown confirmations

5. **Cleanup**: `TeamDelete` to remove team

6. **Report**:
   - Display per-area file listing with each verdict.
   - Path to `<out>/README.md` index.
   - Note execution mode: team.
   - Include agent lifecycle stats (spawned, reused, retired by context level).

#### Agent Summary

| Role | Agent Type | Model | Lifecycle |
|------|------------|-------|-----------|
| Test Reviewer | `coding:ava-thompson-testing-evangelist` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Security Reviewer | `coding:nina-petrov-security-champion` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Quality Reviewer | `coding:marcus-williams-code-quality` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Docs Reviewer | `general-purpose` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Style Reviewer | `general-purpose` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |

**Context-aware reuse policy**: Reviewers with reported `context_level < 50%` are eligible for reuse in optional cross-scope review rounds. Reviewers with `context_level >= 50%` are retired and replaced with fresh agents if additional review rounds are needed.

### Step 2B: Subagent Mode (fallback)

You are a **Review Orchestrator**. You coordinate code review to improve both the code and the system. You never modify code directly, only delegate analysis and consolidate learning. Your approach emphasizes:

- **Strategic Delegation**: Assign review with clear mission, constraints, success metrics
- **Parallel Coordination**: Run specialized agents autonomously and simultaneously
- **Learning Orientation**: Each subagent writes its own area file under `<out>/` (per `references/review.template.md`); orchestrator generates the `<out>/README.md` index plus systemic improvements
- **Visible Reasoning**: Reviewers explain why issues matter, not just what's wrong
- **Truth Over Ego**: Findings are data for system upgrades, not criticism
- **Scope Management**: Adapt depth based on user-selected areas of focus

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

**Context Detection & Scope Selection**: Use the same scope selection logic as Team Mode (Step 2A Phase 1) -- detect execution environment, resolve specifier, determine default scope, discover files, and categorize them by type.

**File filtering by scope**:

- test: test files + source files
- documentation: source + doc files + test files
- code-quality: source files + test files
- security: source files (especially auth/, api/, services/)
- style: source + test files

Prepare file lists for each selected scope.

#### Phase 2: Execution (Subagents via Task Tool)

Dispatch up to 5 scope review tasks in parallel using the Task tool, one for each selected scope.

- **All agents must operate in READ-ONLY mode** -- no code modifications
- **Agents must report issues with exact file:line references**, function names
- Each agent receives its scope-specific standards and file list

**For TEST Scope** (if selected):

Task tool with `subagent_type: "coding:ava-thompson-testing-evangelist"`

Prompt the agent as a **Testing Quality Analyst** performing comprehensive read-only test analysis. Include standards: `testing/scan`, `universal/scan`, `code-review`. The agent performs:

1. **Coverage Analysis**: Run coverage tools, identify uncovered lines/branches/statements, specify exact file:line locations, recommend specific test cases
2. **Test Quality Analysis**: Analyze structure and organization, identify complex setups, check arrange-act-assert patterns, find unnecessary or redundant tests
3. **Fixtures & Mocks Analysis**: Find duplicate fixture patterns, identify centralizable mocks, recommend consolidation strategies

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/TESTING.md` (resolved against project root from the `--out` arg, default `reviews/`). Prefix `TEST`. Issue IDs follow `TEST-P<n>-<seq>`. Verdict is computed from open (unchecked) issues only. If `<out>/TESTING.md` already exists, read it first and apply the re-run logic: match new findings to prior unchecked entries by `Source` location + `Issue` text; reuse original IDs and any Pending Decisions context; for prior unchecked items with no current match, confirm they no longer apply before dropping; new findings get the next available sequence per priority. Rewrite the file in full. Return a short completion message to the orchestrator with the file path, open-issue counts per priority, and `context_level`.

**For DOCUMENTATION Scope** (if selected):

Task tool with `subagent_type: "general-purpose"`

Prompt the agent as a **Documentation Quality Analyst** performing read-only documentation review. Include standard: `documentation/scan`. The agent checks:

1. JSDoc/TSDoc completeness for all exported functions, classes, interfaces
2. Inline comments for complex logic
3. README accuracy and completeness
4. API documentation if applicable
5. Example usage and code samples
6. Type definitions documentation

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/DOCS.md`. Prefix `DOCS`. Issue IDs follow `DOCS-P<n>-<seq>`. Apply the same re-run logic as above (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

**For CODE-QUALITY Scope** (if selected):

Task tool with `subagent_type: "coding:marcus-williams-code-quality"`

Prompt the agent as a **Code Quality Analyst** performing read-only code quality review. The agent MUST apply the Core Review Mandates (Plan Adherence, Redundancy, Sibling Consistency, Zero Tolerance, Delegate Mechanical Checks) defined at the top of this skill. Include standards: `code-review`, `universal/scan`, `function/scan`, `observability/scan`, `typescript/scan`, `naming/scan`. The agent performs:

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

**For SECURITY Scope** (if selected):

Task tool with `subagent_type: "coding:nina-petrov-security-champion"`

Prompt the agent as a **Security Analyst** performing read-only security review. Include standards: `universal/scan`, `code-review`. The agent checks:

1. **Injection Vulnerabilities**: SQL injection, XSS, command injection
2. **Authentication/Authorization**: Auth implementation review
3. **Input Validation**: Input sanitization and validation
4. **Sensitive Data**: Exposed secrets, logging sensitive data
5. **Dependencies**: Known vulnerabilities
6. **CORS & Headers**: Security headers configuration
7. **Crypto**: Proper encryption usage

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/SECURITY.md`. Prefix `SEC`. Issue IDs follow `SEC-P<n>-<seq>`. Apply the re-run logic (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

**For STYLE Scope** (if selected):

Task tool with `subagent_type: "general-purpose"`

Prompt the agent as a **Style & Linting Analyst** performing read-only style review. Include standards: `typescript/scan`, `naming/scan`. The agent performs:

1. Identify project package.json files (project and monorepo levels)
2. Extract linting scripts (lint, lint:fix, eslint, prettier)
3. Execute linting scripts and capture output
4. Parse linter output for file:line references
5. Report all linting issues found
6. Check naming convention compliance

**Output**: write the area file using `references/review.template.md`. Target path: `<out>/STYLE.md`. Prefix `STYL`. Issue IDs follow `STYL-P<n>-<seq>`. Apply the re-run logic (match prior unchecked issues by `Source` + `Issue`, preserve IDs and Pending Decisions). Rewrite the file in full. Return a short completion message with file path, open-issue counts per priority, and `context_level`.

#### Phase 3: Index & Report Generation (You)

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

### Step 3: Reporting

**Output Format** (both modes):

The orchestrator reports the **per-area file listing** (one line per area, with verdict), aggregate counts per priority, and the path to `<out>/README.md`. Detailed findings live in the area files — not in the console summary.

**Common fields**:

- Execution mode: [team|subagent]
- Review scopes: [list of scopes reviewed]
- Overall status: [PASS|PASS_WITH_SUGGESTIONS|REQUIRES_CHANGES|FAIL]
- Per-area file listing with each file's verdict
- Aggregate open-issue counts: P0, P1, P2, P3
- Path to `<out>/README.md` index

**Team mode additional fields**:

- Agent lifecycle stats:
  - Total agents spawned: [N]
  - Agents reused: [N]
  - Agents retired: [N]
  - Average context level at completion: [X%]

**Output format**:

**If CI/Non-Interactive Mode**:

```markdown
# Code Review Summary

**Generated**: [timestamp]
**Review Scopes**: [scopes reviewed]
**Overall Status**: [PASS|PASS_WITH_SUGGESTIONS|REQUIRES_CHANGES|FAIL]

## Area Files

- [Security](./reviews/SECURITY.md) — ❌ FAIL — 3 issues (P0:1, P1:2, P2:0, P3:0)
- [Quality](./reviews/QUALITY.md) — ✅ PASS
- [Testing](./reviews/TESTING.md) — ❌ FAIL — 2 issues (P0:0, P1:0, P2:1, P3:1)
- [Docs](./reviews/DOCS.md) — ✅ PASS
- [Style](./reviews/STYLE.md) — ✅ PASS
- [Correctness](./reviews/CORRECTNESS.md) — ❌ FAIL — 1 issue (P0:0, P1:1, P2:0, P3:0)

## Aggregate

- P0: [N], P1: [N], P2: [N], P3: [N]

Index: `./reviews/README.md`
```

**If Interactive Mode**:

```
Code Review Complete

Area files written under reviews/:
  SECURITY.md    ❌ FAIL — 3 issues (P0:1, P1:2, P2:0, P3:0)
  QUALITY.md     ✅ PASS
  TESTING.md     ❌ FAIL — 2 issues (P0:0, P1:0, P2:1, P3:1)
  DOCS.md        ✅ PASS
  STYLE.md       ✅ PASS
  CORRECTNESS.md ❌ FAIL — 1 issue (P0:0, P1:1, P2:0, P3:0)

Aggregate open issues: P0:1, P1:3, P2:1, P3:1

FAIL areas: SECURITY, TESTING, CORRECTNESS

Index: reviews/README.md
```

## 📝 Examples

### Team Mode Examples (Agent Teams enabled)

#### Context-Aware Review with Team Coordination

```bash
/review
# Team mode behavior:
#   - Creates review-team
#   - Spawns specialized reviewers for all scopes in parallel
#   - Each reviewer writes its own area file under reviews/
#   - Orchestrator generates reviews/README.md index
#   - Reports agent lifecycle stats
```

#### Single Scope Review (Team Mode)

```bash
/review-code --area=security
# Team mode:
#   - Creates review-team
#   - Spawns security-reviewer (nina-petrov-security-champion, opus)
#   - Writes reviews/SECURITY.md
#   - Updates reviews/README.md index
```

#### Custom Output Directory (Team Mode)

```bash
/review-code "src/api/" --area=security,code-quality --out=audits/q4
# Team mode:
#   - Writes audits/q4/SECURITY.md, audits/q4/QUALITY.md, audits/q4/CORRECTNESS.md
#   - Generates audits/q4/README.md index with verdicts
#   - On re-run, preserves issue IDs and Pending Decisions context
```

### Subagent Mode Examples (Fallback)

#### Context-Aware Review (Auto-Detect)

```bash
/review
# Detects current context:
#   - If in test files → Reviews test scope
#   - If in docs → Reviews documentation scope
#   - Otherwise → Asks user or defaults to all
```

### Single Scope Review

```bash
/review-code --area=test
# Reviews only test quality, coverage, and complexity
# Delegates to Testing Quality Analyst
```

### Multiple Scope Review

```bash
/review-code "src/api/" --area=security,code-quality
# Reviews API directory for security vulnerabilities and code quality
# Runs security and code-quality analysts in parallel
```

### Pattern-Based Review

```bash
/review-code "src/api/**/*.spec.ts" --area=test
# Reviews only API test files using glob pattern
# Limits file discovery to specified pattern
```

### Pull Request Review

```bash
/review-code "PR#123" --area=all
# Reviews all files changed in pull request 123
# Comprehensive review across all quality dimensions
```

### Directory Review with Custom Output

```bash
/review-code "src/auth/" --out=reviews/auth
# Reviews authentication directory
# Writes reviews/auth/SECURITY.md, QUALITY.md, etc.
# Index at reviews/auth/README.md
```

### Package-Based Review

```bash
/review-code "@myapp/auth" --area=security,code-quality
# Reviews all files that import/use the auth package
# Focuses on security and code quality in auth-related code
```

### CI Mode Example

```bash
/review-code --area=all
# In CI environment:
#   - Writes per-area files under reviews/
#   - Prints area-file listing + aggregate counts to console
#   - No interactive prompts
#   - Exits with non-zero code if any P0 issues found
```

### Interactive Mode Example

```bash
/review-code "src/"
# In interactive environment:
#   - May prompt for scope selection if unclear
#   - Writes per-area files under reviews/
#   - Prints area-file listing with verdicts to console
#   - User-friendly formatting
```

### Glob Pattern Review

```bash
/review-code "src/services/**/auth*.ts" --area=security
# Reviews only auth-related files within services directory
# Focuses on security vulnerabilities using glob pattern
```

### Documentation Review

```bash
/review-code "src/**/*.ts" --area=documentation
# Reviews JSDoc/TSDoc coverage in all TypeScript source files
# Identifies missing or incomplete documentation
```

### Git-Based Review

```bash
/review-code "HEAD~3..HEAD" --area=all
# Reviews changes in last 3 commits
# Comprehensive analysis of recent changes
```

### Pre-Commit Review

```bash
/review-code "$(git diff --cached --name-only)" --area=test,code-quality
# Reviews only staged files
# Perfect for pre-commit hook integration
# Focuses on test and code quality
```

### Multiple File Types Review

```bash
/review-code "**/*.{ts,tsx,js,jsx}" --area=code-quality,style
# Reviews all TypeScript and JavaScript files
# Focuses on code quality and style compliance
```

### Clean Pass Example (single area, zero issues)

```bash
/review-code "src/auth/" --area=style
# Subagent writes reviews/STYLE.md:
#
#   # STYLE Review
#   **Verdict**: ✅ PASS
#   ## General Status
#   _No issues found._
#
# Console output:
#   STYLE.md  ✅ PASS
#   Index: reviews/README.md
```

### Issues with Pending Decisions Example

```bash
/review-code "src/api/" --area=security,code-quality --out=reviews
# Subagents write reviews/SECURITY.md, reviews/QUALITY.md, reviews/CORRECTNESS.md.
# reviews/SECURITY.md contains issues like:
#
#   ## Issues
#   ### P0 — Blockers
#   - [ ] ### SEC-P0-1: missing input validation on /payments
#         **Source**: `src/api/payments.controller.ts:203-218`
#         **Issue**: ...
#         **Solution**: TBD
#   ### P1 — High
#   - [ ] ### SEC-P1-1: token compared with == instead of constant-time
#         **Solution**: replace with `timingSafeEqual` from existing `crypto-utils`
#
#   ## Pending Decisions
#   - [ ] ### SEC-P0-1: missing input validation on /payments
#         **Options**:
#         1. Inline zod schema — Pros: local. Cons: duplicates auth boundary contract.
#         2. Reuse existing `validateRequest` middleware — Pros: consistent. Cons: requires routing tweak.
#         **Recommended**: Option 2 — matches sibling controllers in `users.controller.ts`.
#
# Console output:
#   SECURITY.md     ❌ FAIL — 2 issues (P0:1, P1:1, P2:0, P3:0)
#   QUALITY.md      ✅ PASS
#   CORRECTNESS.md  ✅ PASS
#   Index: reviews/README.md
```

### Team Mode Output Example

```bash
/review-code "src/api/" --area=all
# Output (Team Mode):
#
# Code Review Complete (Team Mode)
#
# Area files written under reviews/:
#   SECURITY.md     ❌ FAIL — 5 issues (P0:1, P1:2, P2:1, P3:1)
#   QUALITY.md      ❌ FAIL — 8 issues (P0:0, P1:3, P2:4, P3:1)
#   TESTING.md      ❌ FAIL — 6 issues (P0:0, P1:1, P2:3, P3:2)
#   DOCS.md         ✅ PASS
#   STYLE.md        ✅ PASS
#   CORRECTNESS.md  ❌ FAIL — 4 issues (P0:0, P1:2, P2:1, P3:1)
#
# Aggregate open issues: P0:1, P1:8, P2:9, P3:5
#
# FAIL areas: SECURITY, QUALITY, TESTING, CORRECTNESS
#
# Agent Lifecycle:
#   - Total agents spawned: 5
#   - Agents reused: 2 (for cross-scope review)
#   - Agents retired: 3 (context >= 50%)
#   - Average context level: 38%
#
# Index: reviews/README.md
```

### Error Handling

```bash
/review-code "nonexistent/path"
# Error: Path not found
# Suggestion: Check path exists with 'ls nonexistent/'
# Alternative: Use glob patterns like '/review-code "**/*"' or '/review' for full codebase

/review-code --area=invalid
# Error: Invalid scope 'invalid'
# Valid scopes: test, documentation, code-quality, security, style, all
# Example: /review-code --area=test,code-quality

/review-code "unknown-package"
# Warning: Package 'unknown-package' not found in imports
# Suggestion: Check package name or use file path instead
# Alternative: Use '/review-code "src/**/*"' to review source directory
```
