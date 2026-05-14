# Lint Team Workflow

Loaded by `SKILL.md` Step 2. Full team orchestration with lint-review cycles.

You are the **Lead Orchestrator**. Your role is strictly **orchestration** — you coordinate, delegate, and aggregate. You MUST NOT perform any linting, reviewing, or standards-reading work yourself.

**Lead Rules**:

- **DO**: Discover files, create batches, spawn teammates, manage lifecycle, aggregate results
- **DO NOT**: Read standard files, apply standards, lint code, review compliance, or fix issues
- **NEVER**: Use the `Read` tool on any standard file (paths containing `constitution/standards/`). These are for teammates to read, not you.
- **DO NOT**: Assign new tasks to any agent that reported `context_level` >= 60% — retire them instead
- **ALWAYS**: Pass the full file paths of standard files to teammates — they read and interpret the standards, not you
- **LIFECYCLE**: Manage reviewer lifecycle based on pass/fail + `context_level` reports only (detailed findings go directly to linters, not through you)

## Phase 1: Planning (Lead)

1. **Parse arguments**: Extract specifier and `--scope` from `$ARGUMENTS` (default scope: `uncommitted`)
2. **Discover target files**:
   - **If scope is `uncommitted`**: Run `git diff --name-only HEAD` and `git diff --name-only --cached` and `git ls-files --others --exclude-standard` to get the list of changed/new files. If a specifier is given, filter this list to files matching the specifier. If no files remain after filtering, report "No uncommitted changes found in specified area" and exit early.
   - **Otherwise** (scope is `all` or any custom value): Discover via Glob/Bash based on specifier (current behavior).
   - Filter out gitignored files, node_modules, dist, build, out
3. **Create dynamic batches** (max 2 files per batch)
   - Group related files together when possible (same directory/module)
4. **Pre-pass mechanical scan**: Run `python3 plugins/coding/scripts/scan_potential_violations.py <target-files> --category all --before 5 --after 10` and capture the stdout. Pass the report to each linter teammate as a "Candidate violations (advisory; verify against scan.md before flagging)" section. Linters MUST re-check every candidate against the relevant rule (`DOC-FORM-03`, `DOC-FORM-04`, `TST-MOCK-04`, `TST-MOCK-10`, `TST-DATA-01`, `TST-DATA-05`, `TST-STRU-04`, `TYP-CORE-05`) before flagging. If `python3` is not available, log a warning and proceed without the pre-pass.
5. **Discover applicable standard file paths** (string values only — do NOT read these files):
   a. **Collect all available standards**: Extract every standard file path listed under **all** "Plugin Constitution > Standards" sections in your system prompt. These paths span all active plugins (coding, react, backend, etc.) and system-level configurations. If the system prompt does not contain standard paths, fall back to `Glob` searching for `**/constitution/standards/*.md` across plugin directories.
   b. **Select the base set**: Refer to the **Delegation Rule** section in your system prompt. Under "When Linting Code", a list of applicable standard names is provided. Match each name against the collected paths by filename stem (e.g., `documentation` matches `documentation.md`).
   c. **Extend by file context**:
      - If any target files are test files (`*.spec.*` or `*.test.*`), also include any standard whose filename contains `testing`
      - **React dispatch branch**: If any target files are React files (`*.tsx` or `*.jsx`) AND a `react:lint` skill is available in the system prompt's available-skills list, **partition the file set**: route `.tsx` / `.jsx` files to a `Skill: react:lint` dispatch (as a sibling Task — see Step 4f for the dispatch mechanics), and continue the coding:lint workflow only on the remaining files. If `react:lint` is **NOT** available (older install), fall back to the legacy inline behavior: include standards from the react plugin (paths containing `/react/`) in this run's standard set and keep the React files in the coding batches.
      - If any target files are backend service files, also include standards from the backend plugin (paths containing `/backend/`)
   d. **Rename resilience**: If a delegation-rule name does not exactly match any collected path, include any file whose stem partially matches (e.g., if `typescript` was split into `typescript-types.md` and `typescript-style.md`, both would match).
   e. Pass all matched full absolute paths as strings to teammates. You never need to know their contents.
   f. **Framework auto-discovery (file dispatch)**: After standard selection, inspect the target file set for framework signals:
      - `.tsx` / `.jsx` → `react`
      - `.vue` → `vue` (future)
      - `.svelte` → `svelte` (future)

      For each detected framework, check whether `<framework>:lint` exists in the system prompt's available-skills list:

      - **If available**: Compute the file subset belonging to that framework (e.g., `react_files = [f for f in files if f.endswith(('.tsx', '.jsx'))]` and `other_files = files - react_files`). Spawn a `Task` with `subagent_type: general-purpose` whose prompt is: *"Run `Skill: <framework>:lint` on these files with `--scope=<inherited>`: <file list>. Report `violations_found_total` and `status` on completion."* The dispatched Task runs in **parallel** with the remaining coding:lint workflow. **Remove those framework files from this run's batches** so the coding linters do not double-process them.
      - **If not available**: Leave the files in this run's batches (the legacy inline behavior from Step 4c handles them).

      Track each dispatched framework subtask in a dispatch registry so Phase 4 can aggregate its results.

## Phase 2: Team Setup & Execution (Lead orchestrates)

1. **Create team**: `TeamCreate` with name `lint-team`
2. **Concurrency limits**:
   - Max **4 linters** active (working) at any time — if all 4 slots are occupied, queue remaining batches until a linter becomes idle or is retired
   - Max **2 reviewers** active (working) at any time — if both slots are occupied, queue review assignments until a reviewer becomes idle or is retired
3. **Initialize agent pool**: Lead maintains a registry tracking each agent's name, role, model, last-reported `context_level`, and status (`working` / `idle` / `retired`)
4. **Spawn or reuse linter teammates**: For each batch:
   - **Check pool** for an idle linter with `context_level` < 60%
   - **If found**: Reuse via `SendMessage` with new batch instructions
   - **If not found**: Spawn a fresh `linter-N` using **haiku** model, type `general-purpose`
5. **Create lint tasks**: `TaskCreate` per batch with full instructions including:
   - The full absolute paths to the standard files collected in Phase 1 Step 4 (as string values — teammates will read these files themselves)
   - Complete file list for the batch
   - **The `--scope` value** — the linter uses this to determine which area of each file to lint:
     - `uncommitted`: Run `git diff` on each assigned file to identify changed hunks; lint those line ranges and their enclosing functions/blocks; skip untouched sections. Still apply all standards, but scoped to the changed areas.
     - `all`: Lint each file in its entirety against all standards.
     - Any other value: Interpret as a hint for which sections to focus on (e.g., `mocks` → focus on mock/stub code; a function name → focus on that function and its callers).
   - **Linting process**: Linters must (1) scan each file against the loaded standards' Quick Scan checklists, (2) for each potential violation, read the matching rule file (`./rules/<rule-id>.md`) to confirm the violation and follow its Fix section, (3) run the lint script, (4) fix any remaining tool-reported issues
   - Expected YAML report format (see below) — **must include `violations_found` count** (integer, `0` if already compliant and no modifications were made) and **use `status: compliant`** when `violations_found` is `0` (distinct from `success` which means violations were found and fixed)
   - Instruction that linters CANNOT further delegate work
   - **Instruction to report `context_level`** (calculated as `input_tokens / context_window_size × 100`, default context window: 200K tokens) in their completion message
   - **Instruction to WAIT for reviewer feedback** after completing the lint task (if violations were found) — linters must NOT self-claim new tasks from the task list until the lead confirms the batch is complete
   - **Instruction: if `context_level` >= 60%, the linter MUST NOT self-claim any further tasks** — it must report to the lead and await instructions
   - **Instruction: if reviewers flag issues AND the linter's `context_level` >= 60%**, the linter must request retirement from the lead (send a message requesting the lead to retire it and reassign the fix to a fresh agent)
6. **Assign tasks**: `TaskUpdate` to set owner per linter

## Phase 3: Lint-Review Cycle (per batch, all batches in parallel)

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
   - All reviewers use **sonnet** model, type `general-purpose`
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

**Important**: All batches run this cycle in parallel. The lead orchestrates multiple lint-review cycles concurrently.

**Concurrency**: Max 4 linters and 2 reviewers active at any time. Lead queues excess work until slots free up.

## Agent Summary

| Agent | Model | Role | Max Concurrent | Lifecycle |
|-------|-------|------|----------------|-----------|
| Lead (skill agent) | opus | Orchestration only | 1 | Entire workflow |
| `linter-N` | **haiku** | Apply standards (scoped by `--scope`), fix reviewer feedback | **4** | Spawned on demand; reports `violations_found`; if compliant → batch completes without review; if violations found → must **wait for reviewer approval**; **reused if `context_level` < 60%**; requests retirement if >= 60% and more fix work needed |
| `reviewer-N` | **sonnet** | Independent compliance review (only when violations found) | **2** | Spawned on demand; messages **detailed findings directly to linter**; reports **pass/fail + `context_level`** to lead; reused if < 60%, retired if >= 60% |

## Phase 4: Aggregation & Cleanup (Lead)

1. **Wait** for all batch lint-review cycles to complete (including batches that completed immediately due to compliance) **and** for every framework dispatch subtask (from Phase 1 Step 4f) to return its `violations_found_total` + `status`
2. **Collect results** via `TaskGet` for each completed batch, and read each framework dispatch's reported `violations_found_total` + `status`
3. **Aggregate** all batch reports into a final summary:
   - **Sum** `violations_found` across all coding batches **and** every dispatched framework subtask into `violations_found_total`
   - **Take the worst status** across all coding batches and every framework dispatch, using the precedence `failure > partial > success > compliant`
   - Track batches that were **compliant (review skipped)** vs. **reviewed**, and list framework dispatches separately under "Framework dispatches" with their individual `violations_found_total` + `status`
4. **Shutdown** all remaining teammates via `SendMessage` shutdown requests
5. **Delete team** via `TeamDelete`
6. Proceed to Step 3: Reporting
