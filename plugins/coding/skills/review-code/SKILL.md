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

- **If present**: Use **Team Mode** — see `references/team-mode.md` for the full Phase 1–4 workflow (planning, team setup, review cycle, index & cleanup).
- **If absent**: Use **Subagent Mode** — see `references/subagent-mode.md` for the full Phase 1–3 workflow (planning, parallel Task dispatch per scope, index & report).

For specifier resolution (file/dir/glob/package/PR/git-range/cmd-output), default scope determination, file discovery, and per-scope file filtering — see `references/specifier-resolution.md`. Both modes use this logic in their Phase 1.

### Step 2: Reporting

Both modes converge here. Render the final summary using the format matching the runtime mode:

- **CI / Non-Interactive** vs **Interactive** output templates and shared fields → see `references/output-formats.md`.

The orchestrator reports the **per-area file listing** (one line per area, with verdict), aggregate counts per priority, and the path to `<out>/README.md`. Detailed findings live in the area files — not in the console summary.

## 📝 Examples

For invocation examples covering Team Mode, Subagent Mode, single/multi-scope review, glob/PR/git/package specifiers, CI vs Interactive, clean-pass output, Pending Decisions output, Team Mode output, and error handling — see `references/examples.md`.
