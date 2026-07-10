---
name: lint
description: Apply React, JSX, hooks, accessibility, and Storybook standards to .tsx/.jsx files; auto-invoked by /coding:lint when React files are detected.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep, Skill, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: "[specifier] [--scope=SCOPE]"
---

# React Linting

Apply React-specific coding standards (components, hooks, accessibility, Storybook, project structure) plus the universal coding standards (documentation, function, naming, typescript, universal) to `.tsx` / `.jsx` files. Standards are discovered at runtime from all active plugins and system context. This skill is normally dispatched by `/coding:lint` when React files are detected in a batch, but can also be invoked directly. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. Lint corrections must therefore reshape the offending line into something that belongs, not wrap it in a disable comment or shadow it with a "compliant" twin — when the file is done, the only visible record of the violation is its absence.

## Arguments

- **specifier** (positional, optional): File path, directory, or glob pattern selecting which React files to lint. Non-React files in the resolved set are ignored.
- **--scope** (optional, default: `uncommitted`): The area within each file to focus linting on. The linter agent interprets this value at runtime. Common values:
  - `uncommitted` — Focus on line ranges with uncommitted changes (staged + unstaged). The linter uses `git diff` to identify changed hunks and lints those areas plus their immediate surrounding context (enclosing components/hooks/blocks).
  - `all` — Lint each file in its entirety.
  - Any other value (e.g., `hooks`, `stories`, a component name) — The linter interprets the value as a hint for which sections of the code to focus on.

Iteration is handled at the session level via [`/goal`](https://code.claude.com/docs/en/goal) — not by this skill. To run lint until clean, set a goal first, then invoke `/react:lint` (or run `/coding:lint`, which dispatches here automatically). The Step-5 report below is shaped so the goal evaluator (default Haiku) can read convergence state directly.

**Lead pre-filter for `uncommitted` scope**: Before batching, the lead runs `git diff --name-only` to identify React files with uncommitted changes. Files with no changes are excluded from batching to save linter tokens. If no specifier is given, all changed `.tsx/.jsx` files are included. If a specifier is given, only changed React files matching the specifier are batched.

## Purpose & Scope

This skill mirrors `/coding:lint` but narrows the target file set to React files (`*.tsx`, `*.jsx`, including sibling `*.stories.tsx`) and loads React-specific standards in addition to the universal coding standards that all TypeScript/JavaScript files obey.

**What this command does NOT do**:

- does not modify configuration files (tsconfig.json, eslintrc, next.config.js, etc.)
- does not install or update linting packages
- does not create new linting rules or configurations
- does not process binary files or non-code assets
- does not modify gitignored or vendor files
- does not lint non-React `.ts` / `.js` files — those stay with `/coding:lint`

**When to REJECT**:

- target is a configuration file that shouldn't be linted
- no React source files (`*.tsx` or `*.jsx`) found in the specified area
- target is outside the project directory
- no files match the specifier after scope pre-filtering (e.g., `--scope=uncommitted` but no uncommitted React changes in the specified files)

## Workflow

ultracode: you'd perform the following steps.

You are the **Lead Orchestrator**. Your role is strictly **orchestration** — you coordinate, delegate, and aggregate. You MUST NOT perform any scanning, linting, reviewing, or standards-reading work yourself.

**Lead Rules**:

- **DO**: Discover React files, create batches, spawn teammates, manage lifecycle, aggregate results
- **DO NOT**: Read standard files, run the mechanical scanners, apply standards, lint code, review compliance, or fix issues — teammates do all of it
- **NEVER**: Use the `Read` tool on any standard file (paths containing `constitution/standards/`). These are for teammates to read, not you.
- **DO NOT**: Assign new tasks to any agent that reported `context_level` >= 60% — retire them instead
- **ALWAYS**: Pass the full file paths of standard files to teammates (string values only) — they read and interpret the standards, not you
- **LIFECYCLE**: Manage reviewer lifecycle based on pass/fail + `context_level` reports only (detailed findings go directly to linters, not through you)

### Step 1: Plan

1. **Parse arguments**: Extract specifier and `--scope` from `$ARGUMENTS` (default scope: `uncommitted`).
2. **Discover target React files**:
   - **If scope is `uncommitted`**: Run `git diff --name-only HEAD`, `git diff --name-only --cached`, and `git ls-files --others --exclude-standard` to get the list of changed/new files. Filter the union to **React files only**: any path ending in `.tsx` or `.jsx`. Sibling `*.stories.tsx` are included automatically since they end in `.tsx`. If a specifier is given, further filter to files matching the specifier. If no React files remain after filtering, report "No uncommitted React changes found in specified area" and exit early.
   - **Otherwise** (scope is `all` or any custom value): Discover via Glob/Bash based on specifier, then filter the result to `.tsx` / `.jsx` only.
   - Filter out gitignored files, `node_modules`, `dist`, `build`, `out`, `.next`.
3. **Create dynamic batches** (max 2 files per batch). Group related files together when possible (same component folder, page route, or story + component pair).
4. **Discover applicable standard file paths** (string values only — do NOT read these files):
   a. **Collect all available standards**: Extract every standard file path listed under **all** "Plugin Constitution > Standards" sections in your system prompt. These paths span all active plugins (coding, react, backend, etc.) and system-level configurations. If the system prompt does not contain standard paths, fall back to `Glob` searching for `**/constitution/standards/*.md` across plugin directories.
   b. **Select the react base set**: From the collected paths, include every standard rooted under the react plugin (path contains `/plugins/react/constitution/standards/`). Match by filename stem against the following expected set:
      - `accessibility`
      - `components`
      - `hooks`
      - `project-structure`
      - `storybook`
   c. **Append the universal coding subset**: `.tsx` / `.jsx` files are still TypeScript/JavaScript, so they obey the cross-cutting coding standards. From the collected paths, also include the standards from the coding plugin whose filename stem matches:
      - `documentation`
      - `function`
      - `naming`
      - `typescript`
      - `universal`
   d. **Extend by file context**:
      - If any target files are test files (`*.spec.tsx` or `*.test.tsx`), also include any standard whose filename contains `testing`.
      - If any target files are story files (`*.stories.tsx`), ensure the `storybook` standard is included (it should be from step b, but double-check).
   e. **Rename resilience**: If an expected stem does not exactly match any collected path, include any file whose stem partially matches (e.g., if `typescript` was split into `typescript-types.md` and `typescript-style.md`, both would match).
   f. Pass all matched full absolute paths as strings to teammates. You never need to know their contents.

### Step 2: Set up the team & run linters

1. **Create team**: `TeamCreate` with name `react-lint-team`.
2. **Concurrency limits**:
   - Max **4 linters** active (working) at any time — if all 4 slots are occupied, queue remaining batches until a linter becomes idle or is retired.
   - Max **2 reviewers** active (working) at any time — if both slots are occupied, queue review assignments until a reviewer becomes idle or is retired.
3. **Initialize agent pool**: Lead maintains a registry tracking each agent's name, role, model, last-reported `context_level`, and status (`working` / `idle` / `retired`).
4. **Spawn or reuse linter teammates**: For each batch:
   - **Check pool** for an idle linter with `context_level` < 60%.
   - **If found**: Reuse via `SendMessage` with new batch instructions.
   - **If not found**: Spawn a fresh `linter-N` using **haiku** model, type `general-purpose`.
5. **Create lint tasks**: `TaskCreate` per batch with full instructions including:
   - The full absolute paths to the standard files collected in Step 1 (as string values — teammates read these files themselves).
   - Complete file list for the batch (React files only).
   - **The `--scope` value** — the linter uses this to determine which area of each file to lint:
     - `uncommitted`: Run `git diff` on each assigned file to identify changed hunks; lint those line ranges and their enclosing components/hooks/blocks; skip untouched sections. Still apply all standards, but scoped to the changed areas.
     - `all`: Lint each file in its entirety against all standards.
     - Any other value: Interpret as a hint for which sections to focus on (e.g., `hooks` → focus on `use*` calls and custom hooks; a component name → focus on that component and its callers).
   - **Linting process** — each linter MUST:
     1. **Run BOTH mechanical scanners on its own batch files** via the shared wrapper (which resolves a correct interpreter — never bare `python3`), react scanner first, then coding scanner, concatenating their stdout:

        ```bash
        plugins/coding/scripts/pyrun.sh plugins/react/scripts/scan_potential_violations.py <this batch's files> --category all --before 5 --after 10
        plugins/coding/scripts/pyrun.sh plugins/coding/scripts/scan_potential_violations.py <this batch's files> --category all --before 5 --after 10
        ```

        The **react scanner** catches React-specific patterns (hook order, a11y attrs, story exports, etc.); the **coding scanner** catches cross-cutting categories that still apply to `.tsx`/`.jsx`. Both cover all categories via `--category all`. The wrapper **auto-heals a missing interpreter**: if no Python ≥3.13 is found, it installs one via `coding:sync-tool` and retries, so the scan is **expected to always run**. There is **no skip marker** — a genuine hard install failure surfaces as a loud non-zero exit. On a non-zero exit, **STOP and report scan failure** in the YAML report — do NOT silently proceed. Capture the concatenated stdout as the advisory candidate-violations list. The candidates are **advisory**: re-check every one against the relevant rule before flagging.
     2. Scan each file against the loaded standards' Quick Scan checklists.
     3. For each potential violation — including every advisory candidate from step 1 — read the matching rule file (`./rules/<rule-id>.md`) to confirm the violation and follow its Fix section.
     4. Run the project lint/type/test tools (eslint, tsc, pytest, …) — **NOT the scanners again** — and fix any remaining tool-reported issues.
   - Expected YAML report format — **must include `violations_found` count** (integer, `0` if already compliant and no modifications were made) and **use `status: compliant`** when `violations_found` is `0` (distinct from `success`, which means violations were found and fixed).
   - Instruction that linters CANNOT further delegate work.
   - **Instruction to report `context_level`** (calculated as `input_tokens / context_window_size × 100`, default context window: 200K tokens) in their completion message.
   - **Instruction to WAIT for reviewer feedback** after completing the lint task (if violations were found) — linters must NOT self-claim new tasks from the task list until the lead confirms the batch is complete.
   - **Instruction: if `context_level` >= 60%, the linter MUST NOT self-claim any further tasks** — it must report to the lead and await instructions.
   - **Instruction: if reviewers flag issues AND the linter's `context_level` >= 60%**, the linter must request retirement from the lead (send a message requesting the lead to retire it and reassign the fix to a fresh agent).
6. **Assign tasks**: `TaskUpdate` to set owner per linter.

### Step 3: Lint–review cycle (per batch, all batches in parallel)

After each linter completes their lint task:

1. **Linter sends completion message** to lead with YAML report (including `violations_found` count) and `context_level` (calculated as `input_tokens / context_window_size × 100`). Linter then **waits** — it must NOT self-claim new tasks until the lead confirms the batch outcome.
2. **Lead records linter's `context_level`** but does NOT yet retire or reassign the linter — the linter may be needed for fixes.
3. **Lead checks linter's report for violations**:
   - **If `violations_found` is `0` AND `status` is `compliant`** (no modifications were made):
     - **SKIP review entirely** for this batch — do NOT assign reviewers.
     - Mark batch as complete immediately.
     - The linter is eligible for new batches if `context_level` < 60%; otherwise the lead retires it.
     - Log the batch as "compliant — review skipped" in the aggregation.
   - **If `violations_found` > 0** (modifications were made):
     - **Proceed to reviewer assignment** (steps 4+ below).
4. **Lead assigns 2 reviewers** per completed batch (only when violations were found):
   - **Check pool** for idle reviewers with `context_level` < 60% — reuse via `SendMessage`.
   - **If not enough idle reviewers**: Spawn fresh `reviewer-N`.
   - All reviewers use **sonnet** model, type `general-purpose`.
5. **Lead creates review tasks** for each reviewer with these instructions:
   - Subject: "Review react lint batch N (reviewer A/B)".
   - Description includes: the file list that was linted, the full file paths to standards (reviewers read these themselves), instruction to independently review for compliance, **instruction to report `context_level`** in their response.
   - **The linter's name** (e.g., `linter-1`) so the reviewer knows where to send detailed findings.
   - Reviewers work independently — they do NOT coordinate with each other.
   - **Communication rules**:
     - Send **detailed findings directly to the linter** via `SendMessage` (full issue descriptions, file paths, line numbers, expected fixes).
     - Send only **pass/fail + `context_level`** to the lead (e.g., `status: approved, context_level: 30%` or `status: issues_found, context_level: 45%`).
6. **Reviewers review the linted files** and communicate:
   - **To the linter** (via `SendMessage`): Full issue details if issues found, or "approved, no issues" if compliant.
   - **To the lead** (via `SendMessage`): Only `status: approved` or `status: issues_found`, plus `context_level: XX%`.
7. **Lead updates reviewer pool** based on each reviewer's reported `context_level`:
   - If `context_level` < 60%: Mark reviewer as `idle` — available for reuse in future review rounds.
   - If `context_level` >= 60%: Retire reviewer via shutdown request.
8. **If either reviewer flags issues**:
   - **If linter `context_level` < 60%**: The linter already received detailed findings directly from reviewers — it fixes the issues, then reports back to lead with updated `context_level`. Lead assigns 2 reviewers again (reuse idle pool or spawn fresh). Repeat until both approve.
   - **If linter `context_level` >= 60%**: The linter sends a **self-retirement request** to the lead. Lead retires the linter, spawns a fresh replacement, and forwards the linter's partial work context + reviewer findings to the new linter. The new linter fixes issues and the cycle continues.
9. **When both reviewers approve**: Lead marks the batch as fully completed. The linter is now eligible for new batches if `context_level` < 60%; otherwise the lead retires it.

```
Per-batch flow:

  linter-N ──[scan + lint]──> lead (YAML report + context_level + violations_found)
                         │
                         │  linter WAITS (no self-claiming)
                         │
                    violations_found > 0?
                    ┌────┴────┐
                    no        yes
                    │         │
              batch complete  ├──[spawn/reuse]──> reviewer-N (sonnet)
              (review skipped)└──[spawn/reuse]──> reviewer-N (sonnet)
              linter: pool               │
              or retire        reviewers review independently
                                         │
                               ┌─────────┴─────────┐
                               │                   │
                         To linter (DM):     To lead:
                         detailed findings   pass/fail + context_level
                               │                   │
                               └─────────┬─────────┘
                                         │
                          lead updates reviewer pool
                            < 60% → mark idle for reuse
                            >= 60% → retire via shutdown
                                         │
                               Both approve? ──yes──> batch complete
                                    │                  └── linter: pool or retire
                                    │                      based on context_level
                                    no (either flags issues)
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                    linter < 60%        linter >= 60%
                          │                   │
                    linter fixes        linter sends self-
                    (already has        retirement request
                    details from          to lead
                    reviewers)              │
                          │            lead retires linter,
                          │            spawns fresh replacement,
                          │            forwards context + findings
                          │                   │
                          └─────────┬─────────┘
                                    │
                          lead assigns 2 reviewers
                                    │
                                    └──> repeat until both approve
```

**Important**: All batches run this cycle in parallel. The lead orchestrates multiple lint-review cycles concurrently. Max 4 linters and 2 reviewers active at any time; lead queues excess work until slots free up.

#### Agent Summary

| Agent | Model | Role | Max Concurrent | Lifecycle |
|-------|-------|------|----------------|-----------|
| Lead (skill agent) | opus | Orchestration only | 1 | Entire workflow |
| `linter-N` | **haiku** | Run both scanners on its batch, apply react + universal standards (scoped by `--scope`), fix reviewer feedback | **4** | Spawned on demand; reports `violations_found`; if compliant → batch completes without review; if violations found → must **wait for reviewer approval**; **reused if `context_level` < 60%**; requests retirement if >= 60% and more fix work needed |
| `reviewer-N` | **sonnet** | Independent compliance review (only when violations found) | **2** | Spawned on demand; messages **detailed findings directly to linter**; reports **pass/fail + `context_level`** to lead; reused if < 60%, retired if >= 60% |

### Step 4: Aggregate & clean up

1. **Wait** for all batch lint-review cycles to complete (including batches that completed immediately due to compliance).
2. **Collect results** via `TaskGet` for each completed batch.
3. **Aggregate** all batch reports into the final summary — sum `violations_found` across all batches into `violations_found_total`; take the worst status across batches (`failure` > `partial` > `success` > `compliant`); track batches that were **compliant (review skipped)** vs. **reviewed**.
4. **Shutdown** all remaining teammates via `SendMessage` shutdown requests.
5. **Delete team** via `TeamDelete`.
6. Proceed to Step 5.

### Step 5: Report

The report shares the same shape as `/coding:lint` so the parent dispatcher can aggregate. It MUST begin with the following top-level keys so `/goal`'s evaluator (default Haiku) — and the dispatching `/coding:lint` orchestrator — can read convergence state without parsing prose:

```
violations_found_total: <int>   # sum across all batches in this pass
status: compliant | success | partial | failure
```

Use `status: compliant` and `violations_found_total: 0` together to signal the goal is met. Use `status: success` when violations were found and fixed in this pass. Use `partial` or `failure` when issues remain.

The remainder of the summary follows below:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Scope: [uncommitted|all|custom]
- Files scanned: [count]
- Files modified: [count]
- Files already compliant: [count]
- Standards compliance: [PASS/FAIL]
- Linting status: [all_pass/some_fail]

## Actions Taken
1. Fixed hook violations in [X] files
2. Added/updated JSDoc on components in [Y] files
3. Repaired a11y attributes in [Z] files
4. Standardized story exports in [W] files

## Workflows Applied
- Linting workflow: [Status]

## Review Cycles
- Batch 1: [N] review rounds until both reviewers approved
- Batch 2: compliant — review skipped
- ...

## Review Coverage
- Batches reviewed: [count] (violations found, sent to reviewers)
- Batches skipped: [count] (already compliant, review not needed)

## Agent Lifecycle
- Agents spawned: [count]
- Agents reused: [count]
- Agents retired (context >= 60%): [count]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## Examples

### Default Usage (Uncommitted React Changes)

```bash
/react:lint
# Lints only .tsx/.jsx files with uncommitted changes (default --scope=uncommitted)
# Linter focuses on changed line ranges and their surrounding component/hook bodies
```

### Uncommitted Scope with Specifier

```bash
/react:lint "src/components/"
# Lints only uncommitted React files within src/components/
# If no uncommitted .tsx/.jsx changes in src/components/, reports "No uncommitted React changes found"
```

### Lint Entire Files

```bash
/react:lint "src/components/Modal.tsx" --scope=all
# Lints the entire file regardless of git status
```

### Focus on Specific Area

```bash
/react:lint "src/hooks/" --scope=hooks
# Linter interprets "hooks" and focuses on use* calls and custom hook bodies
```

### Pattern-Based Linting

```bash
/react:lint "**/*.stories.tsx" --scope=all
# Lints all Storybook story files across the entire project
```

### Auto-Dispatch from /coding:lint

```bash
/coding:lint "src/" --scope=uncommitted
#   /coding:lint discovers a mixed set: src/utils/format.ts, src/components/Button.tsx
#   It partitions:
#     - .ts files → handled by /coding:lint's own batches
#     - .tsx files → dispatched as a sibling Task running Skill: react:lint
#   Both run in parallel. Final report sums violations_found_total from both
#   and reports the worst status.
```

### Error Case Handling

```bash
/react:lint "src/utils/"
# Error: No React source files (*.tsx or *.jsx) found in the specified area
# Suggestion: Use /coding:lint for plain .ts / .js files
```

### Iterating Until Clean With /goal

```bash
/goal violations_found_total reaches 0 from a fresh /react:lint pass on src/, or stop after 5 turns
/react:lint "src/" --scope=uncommitted
# Pass 1: 4 violations fixed across 3 components; report shows status: success
# Goal evaluator (Haiku) returns no → Claude re-invokes /react:lint
# Pass 2: violations_found_total: 0, status: compliant → goal met, session pauses
```

### Single Pass (No Goal)

```bash
/react:lint "src/components/"
# Runs the workflow once. With no active /goal, the session pauses after the pass.
```
