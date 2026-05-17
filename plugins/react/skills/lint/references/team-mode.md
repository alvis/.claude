# React Lint Team Workflow

Loaded by `SKILL.md` Step 1. Full team orchestration with lint-review cycles, scoped to React files.

You are the **Lead Orchestrator**. Your role is strictly **orchestration** — you coordinate, delegate, and aggregate. You MUST NOT perform any linting, reviewing, or standards-reading work yourself.

**Lead Rules**:

- **DO**: Discover React files, create batches, spawn teammates, manage lifecycle, aggregate results
- **DO NOT**: Read standard files, apply standards, lint code, review compliance, or fix issues
- **NEVER**: Use the `Read` tool on any standard file (paths containing `constitution/standards/`). These are for teammates to read, not you.
- **DO NOT**: Assign new tasks to any agent that reported `context_level` >= 60% — retire them instead
- **ALWAYS**: Pass the full file paths of standard files to teammates — they read and interpret the standards, not you
- **LIFECYCLE**: Manage reviewer lifecycle based on pass/fail + `context_level` reports only (detailed findings go directly to linters, not through you)

## Phase 1: Planning (Lead)

1. **Parse arguments**: Extract specifier and `--scope` from `$ARGUMENTS` (default scope: `uncommitted`)
2. **Discover target React files**:
   - **If scope is `uncommitted`**: Run `git diff --name-only HEAD`, `git diff --name-only --cached`, and `git ls-files --others --exclude-standard` to get the list of changed/new files. Filter the union to **React files only**: any path ending in `.tsx` or `.jsx`. Sibling `*.stories.tsx` are included automatically since they end in `.tsx`. If a specifier is given, further filter to files matching the specifier. If no React files remain after filtering, report "No uncommitted React changes found in specified area" and exit early.
   - **Otherwise** (scope is `all` or any custom value): Discover via Glob/Bash based on specifier, then filter the result to `.tsx` / `.jsx` only.
   - Filter out gitignored files, `node_modules`, `dist`, `build`, `out`, `.next`.
3. **Create dynamic batches** (max 2 files per batch)
   - Group related files together when possible (same component folder, page route, or story + component pair).
4. **Pre-pass mechanical scan**: Run BOTH scanners and concatenate their stdout into a single advisory section for linters:
   - `python3 plugins/react/scripts/scan_potential_violations.py <target-files> --category all --before 5 --after 10` — catches React-specific patterns (hook order, a11y attrs, story exports, etc.). Note: this script is delivered separately; if the file does not yet exist, log a warning and skip this scanner.
   - `python3 plugins/coding/scripts/scan_potential_violations.py <target-files> --category all --before 5 --after 10` — catches cross-cutting categories that still apply to `.tsx`/`.jsx` (e.g., `jsdoc-uppercase`, `let`, `dynamic-import-static`, `DOC-FORM-03`, `DOC-FORM-04`, `TYP-CORE-05`).
   Pass the combined report to each linter teammate as a "Candidate violations (advisory; verify against scan.md before flagging)" section. Linters MUST re-check every candidate against the relevant rule file (`./rules/<rule-id>.md`) before flagging. If `python3` is not available, log a warning and proceed without the pre-pass.
5. **Discover applicable standard file paths** (string values only — do NOT read these files):
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

## Phase 2: Team Setup & Execution (Lead orchestrates)

1. **Create team**: `TeamCreate` with name `react-lint-team`
2. **Concurrency limits**:
   - Max **4 linters** active (working) at any time — if all 4 slots are occupied, queue remaining batches until a linter becomes idle or is retired
   - Max **2 reviewers** active (working) at any time — if both slots are occupied, queue review assignments until a reviewer becomes idle or is retired
3. **Initialize agent pool**: Lead maintains a registry tracking each agent's name, role, model, last-reported `context_level`, and status (`working` / `idle` / `retired`)
4. **Spawn or reuse linter teammates**: For each batch:
   - **Check pool** for an idle linter with `context_level` < 60%
   - **If found**: Reuse via `SendMessage` with new batch instructions
   - **If not found**: Spawn a fresh `linter-N` using **haiku** model, type `general-purpose`
5. **Create lint tasks**: `TaskCreate` per batch with full instructions including:
   - The full absolute paths to the standard files collected in Phase 1 Step 5 (as string values — teammates will read these files themselves)
   - Complete file list for the batch (React files only)
   - **The `--scope` value** — the linter uses this to determine which area of each file to lint:
     - `uncommitted`: Run `git diff` on each assigned file to identify changed hunks; lint those line ranges and their enclosing components/hooks/blocks; skip untouched sections. Still apply all standards, but scoped to the changed areas.
     - `all`: Lint each file in its entirety against all standards.
     - Any other value: Interpret as a hint for which sections to focus on (e.g., `hooks` → focus on `use*` calls and custom hooks; a component name → focus on that component and its callers).
   - **Linting process**: Linters must (1) scan each file against the loaded standards' Quick Scan checklists, (2) for each potential violation, read the matching rule file (`./rules/<rule-id>.md`) to confirm the violation and follow its Fix section, (3) run the lint script, (4) fix any remaining tool-reported issues
   - Expected YAML report format — **must include `violations_found` count** (integer, `0` if already compliant and no modifications were made) and **use `status: compliant`** when `violations_found` is `0` (distinct from `success` which means violations were found and fixed)
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
   - Subject: "Review react lint batch N (reviewer A/B)"
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
| `linter-N` | **haiku** | Apply react + universal standards (scoped by `--scope`), fix reviewer feedback | **4** | Spawned on demand; reports `violations_found`; if compliant → batch completes without review; if violations found → must **wait for reviewer approval**; **reused if `context_level` < 60%**; requests retirement if >= 60% and more fix work needed |
| `reviewer-N` | **sonnet** | Independent compliance review (only when violations found) | **2** | Spawned on demand; messages **detailed findings directly to linter**; reports **pass/fail + `context_level`** to lead; reused if < 60%, retired if >= 60% |

## Phase 4: Aggregation & Cleanup (Lead)

1. **Wait** for all batch lint-review cycles to complete (including batches that completed immediately due to compliance)
2. **Collect results** via `TaskGet` for each completed batch
3. **Aggregate** all batch reports into final summary — sum `violations_found` across all batches into `violations_found_total`; take the worst status across batches (`failure` > `partial` > `success` > `compliant`); track batches that were **compliant (review skipped)** vs. **reviewed**
4. **Shutdown** all remaining teammates via `SendMessage` shutdown requests
5. **Delete team** via `TeamDelete`
6. Proceed to Step 3: Reporting
