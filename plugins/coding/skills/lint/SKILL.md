---
name: lint
description: Apply coding standards and linting to specified code areas. Use when enforcing style guidelines, fixing lint errors, or standardizing code formatting across files.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep, Skill, AskUserQuestion, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [specifier] [--scope=SCOPE] [--skip-unused]
---

# Linting

Apply applicable coding standards to ensure consistent code quality across the specified files, with standards discovered at runtime from all active plugins and system context. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. Lint corrections must therefore reshape the offending line into something that belongs, not wrap it in a disable comment or shadow it with a "compliant" twin — when the file is done, the only visible record of the violation is its absence.

## Arguments

- **specifier** (positional, optional): File path, directory, or glob pattern selecting which files to lint.
- **--scope** (optional, default: `uncommitted`): The area within each file to focus linting on. The linter agent interprets this value at runtime. Common values:
  - `uncommitted` — Focus on line ranges with uncommitted changes (staged + unstaged). The linter uses `git diff` to identify changed hunks and lints those areas plus their immediate surrounding context (enclosing functions/blocks).
  - `all` — Lint each file in its entirety.
  - Any other value (e.g., `mocks`, `handlers`, a function name) — The linter interprets the value as a hint for which sections of the code to focus on.
- **--skip-unused** (optional flag): Bypass Step 1 (the pre-flight unused-code scan) entirely and go straight to the lint workflow.

Iteration is handled at the session level via [`/goal`](https://code.claude.com/docs/en/goal) — not by this skill. To run lint until clean, set a goal first, then invoke `/coding:lint`. Example: `/goal violations_found_total reaches 0 from a fresh /coding:lint pass on src/, or stop after 5 turns`. The Step-6 report below is shaped so the goal evaluator (default Haiku) can read convergence state directly.

**Lead pre-filter for `uncommitted` scope**: Before batching, the lead runs `git diff --name-only` to identify files with uncommitted changes. Files with no changes are excluded from batching to save linter tokens. If no specifier is given, all changed files are included. If a specifier is given, only changed files matching the specifier are batched.

## Purpose & Scope

When framework-specific lint skills are available (e.g. `react:lint`), this skill auto-dispatches the relevant subset of files to them and aggregates results.

**What this command does NOT do**:

- does not modify configuration files (tsconfig.json, eslintrc, etc.)
- does not install or update linting packages
- does not create new linting rules or configurations
- does not process binary files or non-code assets
- does not modify gitignored or vendor files

**When to REJECT**:

- target is a configuration file that shouldn't be linted
- no valid source files found in the specified area
- target is outside the project directory
- no files match the specifier after scope pre-filtering (e.g., `--scope=uncommitted` but no uncommitted changes in the specified files)

## Workflow

ultracode: you'd perform the following steps.

You are the **Lead Orchestrator**. Your role is strictly **orchestration** — you coordinate, delegate, and aggregate. You MUST NOT perform any scanning, linting, reviewing, or standards-reading work yourself.

**Lead Rules**:

- **DO**: Discover files, create batches, spawn teammates, manage lifecycle, aggregate results
- **DO NOT**: Read standard files, run the mechanical scanner, apply standards, lint code, review compliance, or fix issues — teammates do all of it
- **NEVER**: Use the `Read` tool on any standard file (paths containing `constitution/standards/`). These are for teammates to read, not you.
- **DO NOT**: Assign new tasks to any agent that reported `context_level` >= 60% — retire them instead
- **ALWAYS**: Pass the full file paths of standard files to teammates (string values only) — they read and interpret the standards, not you
- **LIFECYCLE**: Manage reviewer lifecycle based on pass/fail + `context_level` reports only (detailed findings go directly to linters, not through you)

### Step 1: Scan for unused code (pre-flight)

If `--skip-unused` is in $ARGUMENTS, skip this step entirely.

1. Invoke `Skill: coding:find-unused` with the specifier (or repo root if none given). It runs its own parallel-agent LSP scan and returns a categorized report: commented-out code, unused exports, unused test helpers. `--scope` does NOT apply here — dead-code detection is project-wide by nature.
2. If the report has zero findings: log "No unused code found" and proceed to Step 2 silently — do NOT prompt the user.
3. If findings exist: present them per-item via `AskUserQuestion`. One question per finding (file:line + symbol/snippet), options Remove / Keep. Batch ≤4 questions per call; paginate across calls for larger sets.
4. Collect all "Remove" decisions. If none, proceed to Step 2.
5. Spawn ONE dedicated cleanup agent (`Task`, subagent_type general-purpose, haiku model) with the confirmed-unused list (paths, line ranges, symbols). Instruct it to delete precisely via Edit, preserve surrounding code, and report removed items. Await completion.
6. Record scan/removed/kept counts for the Step 6 report. Proceed to Step 2.

### Step 2: Plan

1. **Parse arguments**: Extract specifier and `--scope` from `$ARGUMENTS` (default scope: `uncommitted`).
2. **Discover target files**:
   - **If scope is `uncommitted`**: Run `git diff --name-only HEAD`, `git diff --name-only --cached`, and `git ls-files --others --exclude-standard` to get the list of changed/new files. If a specifier is given, filter this list to files matching the specifier. If no files remain after filtering, report "No uncommitted changes found in specified area" and exit early.
   - **Otherwise** (scope is `all` or any custom value): Discover via Glob/Bash based on specifier.
   - Filter out gitignored files, node_modules, dist, build, out.
3. **Create dynamic batches** (max 2 files per batch). Group related files together when possible (same directory/module).
4. **Discover applicable standard file paths** (string values only — do NOT read these files):
   a. **Collect all available standards**: Extract every standard file path listed under **all** "Plugin Constitution > Standards" sections in your system prompt. These paths span all active plugins (coding, react, backend, etc.) and system-level configurations. If the system prompt does not contain standard paths, fall back to `Glob` searching for `**/constitution/standards/*.md` across plugin directories.
   b. **Select the base set**: Refer to the **Delegation Rule** section in your system prompt. Under "When Linting Code", a list of applicable standard names is provided. Match each name against the collected paths by filename stem (e.g., `documentation` matches `documentation.md`).
   c. **Extend by file context**:
      - If any target files are test files (`*.spec.*` or `*.test.*`), also include any standard whose filename contains `testing`.
      - **React dispatch branch**: If any target files are React files (`*.tsx` or `*.jsx`) AND a `react:lint` skill is available in the system prompt's available-skills list, **partition the file set**: route `.tsx` / `.jsx` files to a `Skill: react:lint` dispatch (as a sibling Task — see Step 3 mechanics), and continue the coding:lint workflow only on the remaining files. If `react:lint` is **NOT** available (older install), fall back to the legacy inline behavior: include standards from the react plugin (paths containing `/react/`) in this run's standard set and keep the React files in the coding batches.
      - If any target files are backend service files, also include standards from the backend plugin (paths containing `/backend/`).
   d. **Rename resilience**: If a delegation-rule name does not exactly match any collected path, include any file whose stem partially matches (e.g., if `typescript` was split into `typescript-types.md` and `typescript-style.md`, both would match).
   e. Pass all matched full absolute paths as strings to teammates. You never need to know their contents.
   f. **Framework auto-discovery (file dispatch)**: After standard selection, inspect the target file set for framework signals:
      - `.tsx` / `.jsx` → `react`
      - `.vue` → `vue` (future)
      - `.svelte` → `svelte` (future)

      For each detected framework, check whether `<framework>:lint` exists in the system prompt's available-skills list:

      - **If available**: Compute the file subset belonging to that framework (e.g., `react_files = [f for f in files if f.endswith(('.tsx', '.jsx'))]` and `other_files = files - react_files`). Spawn a `Task` with `subagent_type: general-purpose` whose prompt is: *"Run `Skill: <framework>:lint` on these files with `--scope=<inherited>`: <file list>. Report `violations_found_total` and `status` on completion."* The dispatched Task runs in **parallel** with the remaining coding:lint workflow. **Remove those framework files from this run's batches** so the coding linters do not double-process them.
      - **If not available**: Leave the files in this run's batches (the legacy inline behavior from step c handles them).

      Track each dispatched framework subtask in a dispatch registry so Step 5 can aggregate its results.

### Step 3: Set up the team & run linters

1. **Create team**: `TeamCreate` with name `lint-team`.
2. **Concurrency limits**:
   - Max **4 linters** active (working) at any time — if all 4 slots are occupied, queue remaining batches until a linter becomes idle or is retired.
   - Max **2 reviewers** active (working) at any time — if both slots are occupied, queue review assignments until a reviewer becomes idle or is retired.
3. **Initialize agent pool**: Lead maintains a registry tracking each agent's name, role, model, last-reported `context_level`, and status (`working` / `idle` / `retired`).
4. **Spawn or reuse linter teammates**: For each batch:
   - **Check pool** for an idle linter with `context_level` < 60%.
   - **If found**: Reuse via `SendMessage` with new batch instructions.
   - **If not found**: Spawn a fresh `linter-N` using **haiku** model, type `general-purpose`.
5. **Create lint tasks**: `TaskCreate` per batch with full instructions including:
   - The full absolute paths to the standard files collected in Step 2 (as string values — teammates read these files themselves).
   - Complete file list for the batch.
   - **The `--scope` value** — the linter uses this to determine which area of each file to lint:
     - `uncommitted`: Run `git diff` on each assigned file to identify changed hunks; lint those line ranges and their enclosing functions/blocks; skip untouched sections. Still apply all standards, but scoped to the changed areas.
     - `all`: Lint each file in its entirety against all standards.
     - Any other value: Interpret as a hint for which sections to focus on (e.g., `mocks` → focus on mock/stub code; a function name → focus on that function and its callers).
   - **Linting process** — each linter MUST:
     1. **Run the mechanical scanner on its own batch files** via the shared wrapper (which resolves a correct interpreter — never bare `python3`):

        ```
        plugins/coding/scripts/pyrun.sh plugins/coding/scripts/scan_potential_violations.py <this batch's files> --category all --before 5 --after 10
        ```

        The wrapper **auto-heals a missing interpreter**: if no Python ≥3.13 is found, it installs one via `coding:sync-tool` and retries, so the scan is **expected to always run**. There is **no skip marker** — a genuine hard install failure surfaces as a loud non-zero exit. On a non-zero exit, **STOP and report scan failure** in the YAML report — do NOT silently proceed as if the scan were merely "unavailable". Capture stdout as the advisory candidate-violations list (it covers all categories via `--category all`). The candidates are **advisory**: re-check every one against the relevant rule before flagging.
     2. Scan each file against the loaded standards' Quick Scan checklists.
     3. For each potential violation — including every advisory candidate from step 1 — read the matching rule file (`./rules/<rule-id>.md`) to confirm the violation and follow its Fix section.
     4. Run the project lint/type/test tools (eslint, tsc, pytest, …) — **NOT the scanner again** — and fix any remaining tool-reported issues.
   - Expected YAML report format (see below) — **must include `violations_found` count** (integer, `0` if already compliant and no modifications were made) and **use `status: compliant`** when `violations_found` is `0` (distinct from `success`, which means violations were found and fixed).
   - Instruction that linters CANNOT further delegate work.
   - **Instruction to report `context_level`** (calculated as `input_tokens / context_window_size × 100`, default context window: 200K tokens) in their completion message.
   - **Instruction to WAIT for reviewer feedback** after completing the lint task (if violations were found) — linters must NOT self-claim new tasks from the task list until the lead confirms the batch is complete.
   - **Instruction: if `context_level` >= 60%, the linter MUST NOT self-claim any further tasks** — it must report to the lead and await instructions.
   - **Instruction: if reviewers flag issues AND the linter's `context_level` >= 60%**, the linter must request retirement from the lead (send a message requesting the lead to retire it and reassign the fix to a fresh agent).
6. **Assign tasks**: `TaskUpdate` to set owner per linter.

### Step 4: Lint–review cycle (per batch, all batches in parallel)

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
   - Subject: "Review lint batch N (reviewer A/B)".
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
| `linter-N` | **haiku** | Run the scanner on its batch, apply standards (scoped by `--scope`), fix reviewer feedback | **4** | Spawned on demand; reports `violations_found`; if compliant → batch completes without review; if violations found → must **wait for reviewer approval**; **reused if `context_level` < 60%**; requests retirement if >= 60% and more fix work needed |
| `reviewer-N` | **sonnet** | Independent compliance review (only when violations found) | **2** | Spawned on demand; messages **detailed findings directly to linter**; reports **pass/fail + `context_level`** to lead; reused if < 60%, retired if >= 60% |

### Step 5: Aggregate & clean up

1. **Wait** for all batch lint-review cycles to complete (including batches that completed immediately due to compliance) **and** for every framework dispatch subtask (from Step 2 step f) to return its `violations_found_total` + `status`.
2. **Collect results** via `TaskGet` for each completed batch, and read each framework dispatch's reported `violations_found_total` + `status`.
3. **Aggregate** all batch reports into a final summary:
   - **Sum** `violations_found` across all coding batches **and** every dispatched framework subtask into `violations_found_total`.
   - **Take the worst status** across all coding batches and every framework dispatch, using the precedence `failure > partial > success > compliant`.
   - Track batches that were **compliant (review skipped)** vs. **reviewed**, and list framework dispatches separately under "Framework dispatches" with their individual `violations_found_total` + `status`.
4. **Shutdown** all remaining teammates via `SendMessage` shutdown requests.
5. **Delete team** via `TeamDelete`.
6. Proceed to Step 6.

### Step 6: Report

The report MUST begin with the following top-level keys so `/goal`'s evaluator (default Haiku) can read convergence state without parsing prose:

```
violations_found_total: <int>   # sum across all batches in this pass
status: compliant | success | partial | failure
```

Use `status: compliant` and `violations_found_total: 0` together to signal the goal is met. Use `status: success` when violations were found and fixed in this pass (the goal evaluator will request another pass to verify clean state). Use `partial` or `failure` when issues remain.

Unused-code removals from Step 1 are reported separately (in the "Unused Code (Step 1)" block below) and do **not** count toward `violations_found_total` — a one-time prune must not skew `/goal` convergence.

The remainder of the summary follows below:

```
[✅/❌] Command: $ARGUMENTS

## Unused Code (Step 1)
- Scan: [ran/skipped]
- Findings: [count]   Removed: [count]   Kept: [count]

## Summary
- Scope: [uncommitted|all|custom]
- Files scanned: [count]
- Files modified: [count]
- Files already compliant: [count]
- Standards compliance: [PASS/FAIL]
- Linting status: [all_pass/some_fail]

## Actions Taken
1. Added/updated JSDoc comments in [X] files
2. Reordered functions in [Y] files
3. Standardized error messages in [Z] files
4. Fixed logging formats in [W] files

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

### Default Usage (Uncommitted Changes)

```bash
/lint
# Lints only files with uncommitted changes (default --scope=uncommitted)
# Linter focuses on changed line ranges and their surrounding context
```

### Uncommitted Scope with Specifier

```bash
/lint "src/utils/"
# Lints only uncommitted files within src/utils/
# If no uncommitted changes in src/utils/, reports "No uncommitted changes found"
```

### Lint Entire Files

```bash
/lint "src/utils/helper.ts" --scope=all
# Lints the entire file regardless of git status
```

### Focus on Specific Area

```bash
/lint "src/services/" --scope=mocks
# Linter interprets "mocks" and focuses on mock/stub sections within each file
```

### Complex Usage with Directory

```bash
/lint "src/components/" --scope=all
# Processes all TypeScript and JavaScript files in the components directory
```

### Pattern-Based Linting

```bash
/lint "**/*.test.ts" --scope=all
# Lints all test files across the entire project
```

### Pre-flight Unused-Code Scan (Step 1)

```bash
/lint "src/"
#   Step 1: invokes coding:find-unused on src/.
#   Scan reports 2 dead exports:
#     - src/utils/format.ts:42  export `legacyFormat` (no references)
#     - src/api/client.ts:88    export `oldFetch` (no references)
#   Per-item AskUserQuestion prompts (Remove/Keep):
#     - legacyFormat → user picks Remove
#     - oldFetch     → user picks Keep
#   Cleanup agent (Task, general-purpose, haiku) deletes only `legacyFormat`.
#   Step 1 records: Findings 2, Removed 1, Kept 1.
#   Then the lint workflow runs on the (now pruned) file set.
```

### Skipping the Unused-Code Scan

```bash
/lint "src/" --skip-unused
# Step 1 is bypassed entirely — no find-unused scan, no removal prompts.
# Goes straight to the lint workflow.
```

### Error Case Handling

```bash
/lint "node_modules/"
# Error: Cannot lint vendor/dependency files
# Suggestion: Target source code directories instead
# Alternative: Use '/lint "src/"' for source files
```

### Large-Scale Processing

```bash
/lint "src/" --scope=uncommitted
#   Discovers uncommitted files under src/, creates lint-team:
#   - linter-1 (haiku): Handles src/components/Button.tsx, src/components/Modal.tsx
#   - linter-2 (haiku): Handles src/utils/format.ts (parallel)
#   Each linter runs the scanner on its own batch, then uses git diff to focus on
#   changed hunks within assigned files.
#   Linter-1 finds violations → 2 reviewers assigned for that batch.
#   Linter-2 reports compliant → review skipped for that batch.
#   Agents report context_level after each task:
#     - context < 60%: agent reused for next task
#     - context >= 60%: agent retired, fresh replacement spawned
#   Team is cleaned up after all batches complete.
```

### Iterating Until Clean With /goal

```bash
/goal violations_found_total reaches 0 from a fresh /coding:lint pass on src/, or stop after 5 turns
/lint "src/" --scope=uncommitted
# Pass 1: 7 violations fixed across 4 files; report shows status: success
# Goal evaluator (Haiku) returns no → Claude re-invokes /coding:lint
# Pass 2: 1 violation fixed; status: success
# Pass 3: violations_found_total: 0, status: compliant → goal met, session pauses
```

### Single Pass (No Goal)

```bash
/lint "src/"
# Runs the workflow once. With no active /goal, the session pauses after the pass.
```

### Headless / Non-Interactive

```bash
claude -p "/goal violations_found_total reaches 0 from a fresh /coding:lint pass on src/, or stop after 5 turns" \
       -p "/lint src/ --scope=uncommitted"
# Single invocation runs the goal loop to completion; exit when condition met or cap hit.
```
