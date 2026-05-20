# Step 9a — Stack-Aware Sizing & Restack Trigger

**When loaded**: After Step 9's post-change re-check completes, when the run is NOT in any of the skip conditions below.

**Skip entirely** (record `stack_dispatch.dispatched=false` with one-line reason) when any of:

- `mode ∈ {VERIFY_ONLY, DRAFT_THEN_ASK, REFUSE, FLAG_MISMATCH}`
- `--dry-run` is set
- `commits_landed` is empty

---

## Step Configuration

- **Purpose**: After `commits_landed` are produced, decide whether to delegate to `coding:commit --create-pr` (oversized changes → stacked PRs; existing-stack semantic upstream impact → mandatory restack). The orchestrator NEVER runs `jj split` / `jj bookmark set` / `gh pr create` directly — every stack mutation is dispatched through `coding:commit` so its standards (`GIT-PR-STACK-01..06`, `GIT-PR-SIZE-01..04`) remain the single source of truth.
- **Input**: `repo_path`, `commits_landed`, post-commit diff stats, `ticket.slug`
- **Output**: `stack_dispatch` = `{ dispatched: true|false, mode: stacked-pr|restack|null, branch_prefix: <slug>|null, prs: [...] }`
- **Sub-skill**: `coding:commit` (only when triggered)
- **Parallel Execution**: No

## Phase 1: Planning (You)

1. **Compute aggregate change size** against the base revision (read-only, via `Bash` `jj diff --stat` or `git diff --stat <base>...HEAD`):
   - `changed_files`: total files touched across `commits_landed`
   - `loc_delta`: total added + removed lines
   - `domains_touched`: distinct top-level path prefixes / package roots
2. **Threshold for stacked PRs**: `>5 changed files OR >300 LOC diff OR multiple loosely-coupled domains`. (Mirrored from `coding:commit`'s scenario router; bump in lockstep if upstream thresholds change.)
3. **Detect open stack**: existing bookmarks matching `<branch-prefix>/NN-<scope>` per `GIT-PR-STACK-01` (via `jj bookmark list` or `git branch --list '*/[0-9][0-9]-*'`).
4. **Classify the trigger**:
   - **Size-trigger** → dispatch `coding:commit --create-pr --branch-prefix <ticket.slug>`. The commit skill auto-detects multi-concern `@` and splits before opening the PR stack.
   - **Restack-trigger** → an open stack exists AND the landed code **semantically modifies a symbol/contract that a lower (earlier-in-order) PR in the stack establishes or relies on**. Apply this judgement per symbol, not per file:
     - Trigger: signature change of an exported symbol the lower PR consumes; behavior change in a shared helper a lower PR's tests assume; schema/contract change a lower PR's migration depends on.
     - Do NOT trigger: incidental file overlap (formatting, lint, unrelated co-edit in same file), purely additive code that lower PRs do not reference.
   - **Both triggers fire** → `--create-pr` takes precedence; restack is implicit in the new stack layout (the commit skill's post-rewrite Step 4 invokes `restack.sh` automatically).
   - **Neither fires** → small, single-domain change; continue with the existing single-commit / single-PR path. Record `stack_dispatch.dispatched=false`.
5. Update TodoWrite: add `stack-aware-sizing` todo set to `in_progress` when a trigger fires.

## Phase 2: Execution (Sub-Skill)

When a trigger fires, dispatch `coding:commit` exactly once via the `Skill` tool:

1. Load `/Users/alvis/Repositories/.claude/plugins/coding/skills/commit/SKILL.md` via `Read`
2. Invoke with a minimal payload:
   - `--branch-prefix <ticket.slug>`
   - For size-trigger: `--create-pr` (the skill auto-routes split + stacked-PR materialisation)
   - For restack-trigger: no extra flag — the skill's mandatory Step 4 (`restack.sh`) runs after any rewrite touching a change with downstream bookmarks
   - Pass `repo_path` so the commit skill operates inside the same working copy
3. Capture the commit skill's report `outputs.route`, `outputs.branch_prefix`, and `outputs.prs[]` into `stack_dispatch`
4. Append the dispatch entry to `child_dispatch_log` so Step 12 surfaces it alongside the `coding:*` chain

## Phase 4: Decision (You)

- `coding:commit` reports `status=completed` → record `stack_dispatch` and proceed to Step 10
- `coding:commit` reports `status=failed|partial` → mark this skill's final `status=partial`, attach the commit report to the running context, still proceed to Step 10 (paper-only review remains valuable)
- Mark `stack-aware-sizing` todo as `completed`
