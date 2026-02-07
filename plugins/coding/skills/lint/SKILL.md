---
name: lint
description: Apply coding standards and linting to specified code areas. Use when enforcing style guidelines, fixing lint errors, or standardizing code formatting across files.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
argument-hint: [specifier] [--scope=SCOPE]
---

# Linting

Apply applicable coding standards to ensure consistent code quality across the specified files. Standards are discovered at runtime from all active plugins and system context.

## Arguments

- **specifier** (positional, optional): File path, directory, or glob pattern selecting which files to lint.
- **--scope** (optional, default: `uncommitted`): The area within each file to focus linting on. The linter agent interprets this value at runtime. Common values:
  - `uncommitted` — Focus on line ranges with uncommitted changes (staged + unstaged). The linter uses `git diff` to identify changed hunks and lints those areas plus their immediate surrounding context (enclosing functions/blocks).
  - `all` — Lint each file in its entirety (legacy behavior).
  - Any other value (e.g., `mocks`, `handlers`, a function name) — The linter interprets the value as a hint for which sections of the code to focus on.

**Lead pre-filter for `uncommitted` scope**: Before batching, the lead runs `git diff --name-only` to identify files with uncommitted changes. Files with no changes are excluded from batching to save linter tokens. If no specifier is given, all changed files are included. If a specifier is given, only changed files matching the specifier are batched.

## 🎯 Purpose & Scope

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

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Determine Execution Mode

Check the session context for `**Agent Teams**: enabled` under the "Agent Capabilities" section.
c

- **If present**: Use **Team Mode** (Step 2A) — full team orchestration with lint-review cycles
- **If absent**: Use **Subagent Mode** (Step 2B) — existing workflow via subagents

### Step 2A: Team Mode (Agent Teams enabled)

You are the **Lead Orchestrator**. Your role is strictly **orchestration** — you coordinate, delegate, and aggregate. You MUST NOT perform any linting, reviewing, or standards-reading work yourself.

**Lead Rules**:

- **DO**: Discover files, create batches, spawn teammates, manage lifecycle, aggregate results
- **DO NOT**: Read standard files, apply standards, lint code, review compliance, or fix issues
- **NEVER**: Use the `Read` tool on any standard or workflow file (paths containing `constitution/standards/` or `constitution/workflows/`). These are for teammates to read, not you.
- **DO NOT**: Assign new tasks to any agent that reported `context_level` >= 60% — retire them instead
- **ALWAYS**: Pass the full file paths of standard files to teammates — they read and interpret the standards, not you
- **LIFECYCLE**: Manage reviewer lifecycle based on pass/fail + `context_level` reports only (detailed findings go directly to linters, not through you)

#### Phase 1: Planning (Lead)

1. **Parse arguments**: Extract specifier and `--scope` from `$ARGUMENTS` (default scope: `uncommitted`)
2. **Discover target files**:
   - **If scope is `uncommitted`**: Run `git diff --name-only HEAD` and `git diff --name-only --cached` and `git ls-files --others --exclude-standard` to get the list of changed/new files. If a specifier is given, filter this list to files matching the specifier. If no files remain after filtering, report "No uncommitted changes found in specified area" and exit early.
   - **Otherwise** (scope is `all` or any custom value): Discover via Glob/Bash based on specifier (current behavior).
   - Filter out gitignored files, node_modules, dist, build, out
3. **Create dynamic batches** (max 2 files per batch)
   - Group related files together when possible (same directory/module)
4. **Discover applicable standard file paths** (string values only — do NOT read these files):
   a. **Collect all available standards**: Extract every standard file path listed under **all** "Plugin Constitution > Standards" sections in your system prompt. These paths span all active plugins (coding, react, backend, etc.) and system-level configurations. If the system prompt does not contain standard paths, fall back to `Glob` searching for `**/constitution/standards/*.md` across plugin directories.
   b. **Select the base set**: Refer to the **Delegation Rule** section in your system prompt. Under "When Linting Code", a list of applicable standard names is provided. Match each name against the collected paths by filename stem (e.g., `documentation` matches `documentation.md`).
   c. **Extend by file context**:
      - If any target files are test files (`*.spec.*` or `*.test.*`), also include any standard whose filename contains `testing`
      - If any target files are React files (`*.tsx` or `*.jsx`), also include standards from the react plugin (paths containing `/react/`)
      - If any target files are backend service files, also include standards from the backend plugin (paths containing `/backend/`)
   d. **Rename resilience**: If a delegation-rule name does not exactly match any collected path, include any file whose stem partially matches (e.g., if `typescript` was split into `typescript-types.md` and `typescript-style.md`, both would match).
   e. Pass all matched full absolute paths as strings to teammates. You never need to know their contents.

#### Phase 2: Team Setup & Execution (Lead orchestrates)

1. **Create team**: `TeamCreate` with name `lint-team`
2. **Concurrency limits**:
   - Max **4 linters** active (working) at any time — if all 4 slots are occupied, queue remaining batches until a linter becomes idle or is retired
   - Max **2 reviewers** active (working) at any time — if both slots are occupied, queue review assignments until a reviewer becomes idle or is retired
3. **Initialize agent pool**: Lead maintains a registry tracking each agent's name, role, model, last-reported `context_level`, and status (`working` / `idle` / `retired`)
4. **Spawn or reuse linter teammates**: For each batch:
   - **Check pool** for an idle linter with `context_level` < 60%
   - **If found**: Reuse via `SendMessage` with new batch instructions
   - **If not found**: Spawn a fresh `linter-N` using **opus** model, type `general-purpose`
5. **Create lint tasks**: `TaskCreate` per batch with full instructions including:
   - The full absolute paths to the standard files collected in Phase 1 Step 4 (as string values — teammates will read these files themselves)
   - Complete file list for the batch
   - **The `--scope` value** — the linter uses this to determine which area of each file to lint:
     - `uncommitted`: Run `git diff` on each assigned file to identify changed hunks; lint those line ranges and their enclosing functions/blocks; skip untouched sections. Still apply all standards, but scoped to the changed areas.
     - `all`: Lint each file in its entirety against all standards.
     - Any other value: Interpret as a hint for which sections to focus on (e.g., `mocks` → focus on mock/stub code; a function name → focus on that function and its callers).
   - Expected YAML report format (see below) — **must include `violations_found` count** (integer, `0` if already compliant and no modifications were made) and **use `status: compliant`** when `violations_found` is `0` (distinct from `success` which means violations were found and fixed)
   - Instruction that linters CANNOT further delegate work
   - **Instruction to report `context_level`** (calculated as `input_tokens / context_window_size × 100`, default context window: 200K tokens) in their completion message
   - **Instruction to WAIT for reviewer feedback** after completing the lint task (if violations were found) — linters must NOT self-claim new tasks from the task list until the lead confirms the batch is complete
   - **Instruction: if `context_level` >= 60%, the linter MUST NOT self-claim any further tasks** — it must report to the lead and await instructions
   - **Instruction: if reviewers flag issues AND the linter's `context_level` >= 60%**, the linter must request retirement from the lead (send a message requesting the lead to retire it and reassign the fix to a fresh agent)
6. **Assign tasks**: `TaskUpdate` to set owner per linter

#### Phase 3: Lint-Review Cycle (per batch, all batches in parallel)

After each linter completes their lint task:

1. **Linter sends completion message** to lead with YAML report (including `violations_found` count) and `context_level` (calculated as `input_tokens / context_window_size × 100`). Linter then **waits** — it must NOT self-claim new tasks until the lead confirms the batch outcome.
2. **Lead records linter's `context_level`** but does NOT yet retire or reassign the linter — the linter may be needed for fixes.
3. **Lead checks linter's report for violations**:
   - **If `violations_found` is `0` AND `status` is `compliant`** (no modifications were made):
     - **SKIP review entirely** for this batch — do NOT assign reviewers
     - Mark batch as complete immediately
     - The linter is eligible for new batches if `context_level` < 60%; otherwise the lead retires it
     - Log the batch as "compliant — review skipped" in the aggregation
   - **If `violations_found` > 0** (modifications were made):
     - **Proceed to reviewer assignment** (steps 4+ below)
4. **Lead assigns 2 reviewers** per completed batch (only when violations were found):
   - **Check pool** for idle reviewers with `context_level` < 60% — reuse via `SendMessage`
   - **If not enough idle reviewers**: Spawn fresh `reviewer-N`
   - All reviewers use **opus** model, type `general-purpose`
5. **Lead creates review tasks** for each reviewer with these instructions:
   - Subject: "Review lint batch N (reviewer A/B)"
   - Description includes: the file list that was linted, the full file paths to standards (reviewers read these themselves), instruction to independently review for compliance, **instruction to report `context_level`** in their response
   - **The linter's name** (e.g., `linter-1`) so the reviewer knows where to send detailed findings
   - Reviewers work independently — they do NOT coordinate with each other
   - **Communication rules**:
     - Send **detailed findings directly to the linter** via `SendMessage` (full issue descriptions, file paths, line numbers, expected fixes)
     - Send only **pass/fail + `context_level`** to the lead (e.g., `status: approved, context_level: 30%` or `status: issues_found, context_level: 45%`)
6. **Reviewers review the linted files** and communicate:
   - **To the linter** (via `SendMessage`): Full issue details if issues found, or "approved, no issues" if compliant
   - **To the lead** (via `SendMessage`): Only `status: approved` or `status: issues_found`, plus `context_level: XX%`
7. **Lead updates reviewer pool** based on each reviewer's reported `context_level`:
   - If `context_level` < 60%: Mark reviewer as `idle` — available for reuse in future review rounds
   - If `context_level` >= 60%: Retire reviewer via shutdown request
8. **If either reviewer flags issues**:
   - **If linter `context_level` < 60%**: The linter already received detailed findings directly from reviewers — it fixes the issues, then reports back to lead with updated `context_level`. Lead assigns 2 reviewers again (reuse idle pool or spawn fresh). Repeat until both approve.
   - **If linter `context_level` >= 60%**: The linter sends a **self-retirement request** to the lead (requesting the lead to retire it and reassign the fix to a fresh agent). Lead retires the linter, spawns a fresh replacement, and forwards the linter's partial work context + reviewer findings to the new linter. The new linter fixes issues and the cycle continues.
9. **When both reviewers approve**: Lead marks the batch as fully completed. The linter is now eligible for new batches if `context_level` < 60%; otherwise the lead retires it.

```
Per-batch flow:

  linter-N ──[lint]──> lead (YAML report + context_level + violations_found)
                         │
                         │  linter WAITS (no self-claiming)
                         │
                    violations_found > 0?
                    ┌────┴────┐
                    no        yes
                    │         │
              batch complete  ├──[spawn/reuse]──> reviewer-N-a (opus)
              (review skipped)└──[spawn/reuse]──> reviewer-N-b (opus)
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

**Important**: All batches run this cycle in parallel. The lead orchestrates multiple lint-review cycles concurrently.

**Concurrency**: Max 4 linters and 2 reviewers active at any time. Lead queues excess work until slots free up.

#### Agent Summary

| Agent | Model | Role | Max Concurrent | Lifecycle |
|-------|-------|------|----------------|-----------|
| Lead (skill agent) | opus | Orchestration only | 1 | Entire workflow |
| `linter-N` | **opus** | Apply standards (scoped by `--scope`), fix reviewer feedback | **4** | Spawned on demand; reports `violations_found`; if compliant → batch completes without review; if violations found → must **wait for reviewer approval**; **reused if `context_level` < 60%**; requests retirement if >= 60% and more fix work needed |
| `reviewer-N-a/b` | **opus** | Independent compliance review (only when violations found) | **2** | Spawned on demand; messages **detailed findings directly to linter**; reports **pass/fail + `context_level`** to lead; reused if < 60%, retired if >= 60% |

#### Phase 4: Aggregation & Cleanup (Lead)

1. **Wait** for all batch lint-review cycles to complete (including batches that completed immediately due to compliance)
2. **Collect results** via `TaskGet` for each completed batch
3. **Aggregate** all batch reports into final summary — track batches that were **compliant (review skipped)** vs. **reviewed**
4. **Shutdown** all remaining teammates via `SendMessage` shutdown requests
5. **Delete team** via `TeamDelete`
6. Proceed to Step 3: Reporting

### Step 2B: Subagent Mode (fallback)

1. Parse `--scope` from `$ARGUMENTS` (default: `uncommitted`)
2. **If scope is `uncommitted`**: Pre-filter files via `git diff --name-only HEAD`, `git diff --name-only --cached`, and `git ls-files --others --exclude-standard`. Pass the filtered file list and scope value to the workflow. If no files match, report "No uncommitted changes found" and exit.
3. **Otherwise**: Pass the specifier and scope value directly to the workflow.
4. Execute `workflows:lint` with the scope value as additional context — workflow subagents use the scope to determine which areas within each file to lint.

### Step 3: Reporting

**Output Format** (same for both modes):

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Scope: [uncommitted|all|custom]
- Files scanned: [count]
- Files modified: [count]
- Files already compliant: [count]
- Standards compliance: [PASS/FAIL]
- Linting status: [all_pass/some_fail]
- Execution mode: [team/subagent]

## Actions Taken
1. Added/updated JSDoc comments in [X] files
2. Reordered functions in [Y] files
3. Standardized error messages in [Z] files
4. Fixed logging formats in [W] files

## Workflows Applied
- Linting workflow: [Status]

## Review Cycles (team mode only)
- Batch 1: [N] review rounds until both reviewers approved
- Batch 2: compliant — review skipped
- ...

## Review Coverage (team mode only)
- Batches reviewed: [count] (violations found, sent to reviewers)
- Batches skipped: [count] (already compliant, review not needed)

## Agent Lifecycle (team mode only)
- Agents spawned: [count]
- Agents reused: [count]
- Agents retired (context >= 60%): [count]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## 📝 Examples

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
# Lints the entire file regardless of git status (legacy behavior)
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

### Error Case Handling

```bash
/lint "node_modules/"
# Error: Cannot lint vendor/dependency files
# Suggestion: Target source code directories instead
# Alternative: Use '/lint "src/"' for source files
```

### Large-Scale Processing (Team Mode)

```bash
/lint "src/" --scope=uncommitted
# With CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1:
#   Discovers uncommitted files under src/, creates lint-team:
#   - linter-1 (opus): Handles src/components/Button.tsx, src/components/Modal.tsx
#   - linter-2 (opus): Handles src/utils/format.ts (parallel)
#   Each linter uses git diff to focus on changed hunks within assigned files.
#   Linter-1 finds violations → 2 reviewers assigned for that batch.
#   Linter-2 reports compliant → review skipped for that batch.
#   Agents report context_level after each task:
#     - context < 60%: agent reused for next task
#     - context >= 60%: agent retired, fresh replacement spawned
#   Team is cleaned up after all batches complete.
```

### Large-Scale Processing (Subagent Fallback)

```bash
/lint "src/" --scope=uncommitted
# Without agent teams enabled:
#   Discovers uncommitted files under src/, delegates to subagents:
#   - Agent A: Handles src/components (2 files, focuses on changed hunks)
#   - Agent B: Handles src/utils (1 file, already compliant — no review needed)
#   - Summary Agent: Compiles results after all complete
```
