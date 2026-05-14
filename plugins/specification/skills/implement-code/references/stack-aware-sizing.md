# Step 9a — Stack-Aware Sizing & Restack Trigger

**When loaded**: After Step 9's post-change re-check completes, when the run is NOT in any of the skip conditions below.

**Skip entirely** (record `stack_dispatch.dispatched=false` with one-line reason) when any of:

- `mode ∈ {VERIFY_ONLY, DRAFT_THEN_ASK, REFUSE, FLAG_MISMATCH}`
- `--dry-run` is set
- `commits_landed` is empty

---

## Step Configuration

- **Purpose**: After `commits_landed` are produced, decide whether to delegate to `coding:stack-code` (split/create mode for oversized changes, restack mode for semantic upstream impact). The orchestrator NEVER runs `jj split` / `jj bookmark set` / `gh pr create` directly — every stack mutation is dispatched through `coding:stack-code` so its standards (`GIT-PR-STACK-01..06`, `GIT-PR-SIZE-01..04`) and detect-mode thresholds remain the single source of truth.
- **Input**: `repo_path`, `commits_landed`, post-commit diff stats, `ticket.slug`
- **Output**: `stack_dispatch` = `{ dispatched: true|false, mode: split|create|restack|null, slug: <slug>|null, prs: [...] }`
- **Sub-skill**: `coding:stack-code` (only when triggered)
- **Parallel Execution**: No

## Phase 1: Planning (You)

1. **Compute aggregate change size** against the base revision (read-only, via `Bash` `jj diff --stat` or `git diff --stat <base>...HEAD`):
   - `changed_files`: total files touched across `commits_landed`
   - `loc_delta`: total added + removed lines
   - `domains_touched`: distinct top-level path prefixes / package roots
2. **Read thresholds from `coding:stack-code`** (do not hardcode here): the detect-mode heuristic table in `plugins/coding/skills/stack-code/SKILL.md` Step 2 is authoritative — currently >5 changed files OR >300 LOC diff OR multiple loosely-coupled domains. If that file's thresholds drift, this skill picks up the new values automatically.
3. **Detect open stack**: presence of `<repo>/.jj/stack-code/<slug>.json` state file OR existing bookmarks matching `<slug>/NN-<scope>` per `GIT-PR-STACK-01`.
4. **Classify the trigger**:
   - **Size-trigger** → dispatch `coding:stack-code` in `split` mode (existing chunky branch) or `create` mode (planned outline) per stack-code's own auto-detect; orchestrator does not pre-pick.
   - **Restack-trigger** → an open stack exists AND the landed code **semantically modifies a symbol/contract that a lower (earlier-in-order) PR in the stack establishes or relies on**. Apply this judgement per symbol, not per file:
     - Trigger: signature change of an exported symbol the lower PR consumes; behavior change in a shared helper a lower PR's tests assume; schema/contract change a lower PR's migration depends on.
     - Do NOT trigger: incidental file overlap (formatting, lint, unrelated co-edit in same file), purely additive code that lower PRs do not reference.
   - **Both triggers fire** → `split` (or `create`) takes precedence; restack is implicit in the new stack layout.
   - **Neither fires** → small, single-domain change; continue with the existing single-commit / single-PR path. Record `stack_dispatch.dispatched=false`.
5. Update TodoWrite: add `stack-aware-sizing` todo set to `in_progress` when a trigger fires.

## Phase 2: Execution (Sub-Skill)

When a trigger fires, dispatch `coding:stack-code` exactly once via the `Skill` tool:

1. Load `/Users/alvis/Repositories/.claude/plugins/coding/skills/stack-code/SKILL.md` via `Read`
2. Invoke with a minimal payload:
   - `--slug <ticket.slug>`
   - For size-trigger: let `coding:stack-code`'s `detect-mode.py` pick `create` vs `split`; do not force `--mode` unless the user has already approved a specific path
   - For restack-trigger: invoke `scripts/restack.py --slug <ticket.slug>` per stack-code Step 8 (Ongoing Operations)
   - Pass `repo_path` so stack-code operates inside the same working copy
3. Capture stack-code's `outputs.mode`, `outputs.slug`, and `outputs.prs[]` from its YAML report into `stack_dispatch`
4. Append the dispatch entry to `child_dispatch_log` so Step 12 surfaces it alongside the `coding:*` chain

## Phase 4: Decision (You)

- `stack-code` reports `status=completed` → record `stack_dispatch` and proceed to Step 10
- `stack-code` reports `status=failed|partial` → mark this skill's final `status=partial`, attach the stack-code report to the running context, still proceed to Step 10 (paper-only review remains valuable)
- Mark `stack-aware-sizing` todo as `completed`
