---
name: stack-code
description: 'Orchestrate jj-based stacked GitHub PRs end-to-end: auto-detects create vs split mode, drives `jj split`/`jj describe`/`jj bookmark set`/`jj git push`, and opens each draft PR with a Conventional Commits title and the unified PR body from `coding:write-pr`. Triggers when: "/stack-code", "stack these PRs", "split this branch into a stack", "open a PR stack". Also use when: a working copy has multiple loosely-coupled changes that should land as ordered draft PRs, or main has moved and an open stack needs restacking. Examples: "stack-code this feature outline", "split my chunky branch into PRs", "restack my open stack against latest main".'
model: opus
argument-hint: [--slug <slug>] [--mode create|split] [--dry-run]
---

# Stack Code: Orchestrate jj-based Stacked PRs

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Drive the full lifecycle of stacked GitHub PRs on top of Jujutsu, so a multi-domain change lands as ordered, reviewable, draft PRs that obey `GIT-PR-STACK-01..06` and `GIT-PR-SIZE-01..04`. Every PR opens with a Conventional Commits title and the unified PR body from the sibling `coding:write-pr` template.

**When to use**:
- Explicit `/stack-code` invocation.
- A feature outline (create-mode) that should land as a planned stack.
- A chunky existing branch (split-mode) that should be sliced before review.
- An open stack that needs restacking after main moves or a lower PR merges.

**Prerequisites**:
- `jj` and `gh` on PATH (auto-installed via `coding:sync-tool` from `bootstrap.py` on first run; on macOS, Homebrew is also installed if missing). `gh` must be authenticated — `sync-tool` will block with instructions if not.
- Sibling skill `coding:write-pr` available — the unified template lives at `../write-pr/references/templates/pr.md` and is read directly by `execute-stack.py`. No shell-out to `write-pr` Python scripts (they no longer exist).
- Standards index resolves: `GIT-PR-STACK-01..06`, `GIT-PR-SIZE-01..04`.

### Your Role

You are the orchestration layer. You drive child scripts and read the unified PR template from sibling `coding:write-pr` — never replicate their logic. You always confirm with the user before destructive ops (`jj split`, `jj git push`, `gh pr create`, `jj rebase`), and you always print a dry-run plan before mutating anything.

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Working copy**: a jj-colocated repo (auto-init via `bootstrap.py` if not yet colocated).
- **Mode signal**: feature outline (create-mode) OR chunky uncommitted change (split-mode). Auto-detected by `detect-mode.py`; user confirms.

#### Optional Inputs

- **`--slug`**: override the derived feature slug (kebab-case).
- **`--mode`**: force `create` or `split`, bypassing detection.
- **`--dry-run`**: print the plan only.
- **`STACK_CODE_AUTO_APPROVE=1`**: skip confirmation prompts in evals only.

#### Expected Outputs

- **Stacked draft PRs** named `<slug>/NN-<scope>` per `GIT-PR-STACK-01`, each with a Conventional Commits title and the unified PR body composed inline from `../write-pr/references/templates/pr.md`.
- **State file** `.jj/stack-code/<slug>.json` (see `references/state-schema.md`).
- **Operation summary** on stderr; machine-readable JSON on stdout.

#### Data Flow Summary

The skill bootstraps `jj`/`gh`, detects mode (noop/create/split) from working-copy state, then either drives `coding:write-code` per planned PR (create-mode) or clusters paths via `propose-splits.py` (split-mode) with LLM domain review. After user approval, `execute-stack.py` runs `jj split`/`describe`/`bookmark set`/`git push` per PR, fills the unified PR body from the sibling `coding:write-pr` template, and opens each draft PR via `gh pr create` against the previous bookmark or `main`. `verify.py` confirms typecheck and state integrity.

### Conventional Commits Title Requirement

Every commit subject AND every PR title MUST match the Conventional Commits regex (allowlist enforced by `lib.validate_conventional_subject`):

```
^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([\w./-]+\))?!?: .+
```

A non-conformant subject aborts `execute-stack.py` BEFORE any mutation.

### Visual Overview

```plaintext
[/stack-code]
   |
   v
[Step 1: bootstrap.py]                   # idempotent jj install + colocate + state dir
   |
   v
[Step 2: detect-mode.py]                 # emits {mode, slug, rationale}
   |
   v
[Step 3: confirm mode + slug with user]
   |
   +--(noop)---->[Step 3z: print rationale, exit cleanly — nothing to stack]
   |
   +--(create)-->[Step 4a: per planned PR, invoke coding:write-code]
   |                                  |
   |                                  v
   |                          [Step 5a: execute-stack.py --dry-run]
   |
   +--(split)--->[Step 4b: propose-splits.py]   # cluster by path prefix
                                       |
                                       v
                          [LLM Review: domain meaningfulness check]
                                       |
                                       v
                          [Step 4c: user reviews/edits revised proposal JSON]
                                       |
                                       v
                          [Step 5b: execute-stack.py --dry-run]
                                       |
                                       v
                          [Step 5c: user approval -> execute-stack.py (real)]
   |
   v
[Step 6: per PR -> read ../write-pr/references/templates/pr.md, fill, write tmpfile]
[Step 7: gh pr create --draft --title "<conv-title>" --body-file <tmp> --base <prev_or_main>]
   |
   v
[Step 8: verify.py]                      # typecheck + state integrity
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Bootstrap environment
2. Detect mode and confirm slug
3. Branch on mode (noop, create, or split)
4. Review the split proposal for domain meaningfulness (split-mode only)
5. Propose plan and obtain user approval
6. Execute stack (dry-run -> real)
7. Compose each PR body inline from the unified template
8. Open draft PRs via `gh pr create`
9. Verify and report
10. Handle ongoing ops (correction, restack, corrective-PR)

### Step 1: Bootstrap

- **Purpose**: Delegates to `coding:sync-tool` to install/update `jj` and `gh` (and `brew` on macOS if missing). Ensures repo is colocated and state dir exists.
- **Script**: `scripts/bootstrap.py`
- **Sub-skill**: `coding:sync-tool`.

### Step 2: Detect Mode

- **Purpose**: Decide noop vs create vs split with a one-line rationale.
- **Script**: `scripts/detect-mode.py` -> JSON `{mode, slug, rationale, files, loc}`.
- Heuristic table:

  | Working copy state                                       | Mode     |
  |----------------------------------------------------------|----------|
  | clean AND no commits diverged from `main@origin`         | `noop`   |
  | >5 changed files OR >300 LOC diff                        | `split`  |
  | diverged commits exist on top of `main@origin`           | `split`  |
  | small uncommitted change (<= thresholds, no divergence)  | `create` |

- **Override**: if the user has an outline to build from a clean working copy, they invoke with `--mode create` to bypass the `noop` short-circuit.
- **Confirmation**: present mode + slug to user before proceeding.

### Step 3: Branch on Mode

- **Noop-mode**: print the rationale (e.g. "nothing to stack — working copy is clean and at main@origin") to the user and exit cleanly. Do NOT proceed to `propose-splits.py` or `execute-stack.py`. The user can re-invoke with `--mode create` if they intend to build from an outline.
- **Create-mode**: drive `coding:write-code` per planned PR from the outline. Each yields a discrete change with a conventional-commit subject. Then call Step 6.
- **Split-mode**: call `propose-splits.py --slug <slug>` to cluster `jj diff` paths by path prefix. User reviews/edits the proposal JSON, then proceeds to Step 4.

### Step 4: Review for Meaningfulness

- **Purpose**: `propose-splits.py` clusters by shallow path heuristics only. Before showing the plan to the user, you (the orchestrating LLM) must apply domain judgement that the script cannot.
- **What to do**: examine the proposal JSON. Read the user's `plugins/backend/constitution/standards/data-entity.md` and `data-operation.md` if the changes touch data/service layers. Look for:
  - **(a) Same domain split across PRs** — e.g. `prisma/customer.prisma`, `src/services/customer/operations.ts`, `src/data/customer/repository.ts`, `src/lib/customer/util.ts` should land as ONE PR for the `customer` scope, not four PRs split by directory.
  - **(b) Unrelated domains in one PR** — a single cluster mixing `customer/` and `order/` files should be split further.
  - **(c) Layering violations** — data + service + UI for the same feature/domain landing in separate PRs when they should be one cohesive change.
- **Action**: if you find issues, present a revised plan to the user with rationale and a side-by-side diff against `propose-splits.py`'s original output. Otherwise, proceed unchanged to Step 5.
- **Non-goal**: do NOT add a script for this — the LLM does all domain reasoning here. The script side stays deterministic and minimal.

### Step 5: Plan Approval

- Always print the plan table on stderr (PR#, scope, files, LOC, bookmark).
- Always run `execute-stack.py --proposal <json> --dry-run` first.
- Require user confirmation (or `STACK_CODE_AUTO_APPROVE=1`) before dropping `--dry-run`.
- Reviewer assigns the size zone (`GIT-PR-SIZE-01..04`) at review time; the orchestrator no longer pre-classifies it.

### Step 6: Execute Stack

- **Script**: `scripts/execute-stack.py`
- For each PR in proposal:
  1. Validate the PR's conventional-commit title (`lib.validate_conventional_subject`); abort the entire run on the first violation.
  2. `jj split` selecting the cluster's files.
  3. `jj describe -m <conventional-msg>` (msg composed by `lib.commit_message`, mirroring `coding:commit` format — do not shell out).
  4. `jj bookmark set <slug>/NN-<scope>` per `GIT-PR-STACK-01`.
  5. `jj git push --bookmark <name>`.
  6. Read `../write-pr/references/templates/pr.md`, substitute placeholders from the proposal entry, and write the body to a tempfile.
  7. `gh pr create --draft --title "<conventional-title>" --body-file <tmp> --base <prev_or_main>` per `GIT-PR-STACK-06`.

### Step 7: Verify

- **Script**: `scripts/verify.py --slug <slug>`
- Typecheck: auto-detect `tsc --noEmit` or `mypy`. State integrity: every PR has a resolvable `change_id`. Full tests prompt-only.

### Step 8: Ongoing Operations

- **Review-comment correction**: `references/workflow-correct.md` — `jj edit <change>` + `jj absorb` for in-place fixes; corrective PR on top when public history would be rewritten (`GIT-PR-STACK-03`).
- **Main moved**: `scripts/restack.py --slug <slug>` rebases the next unmerged bookmark onto `main@origin` and re-parents open PRs.
- **Lower PR merged**: `restack.py` auto-detects merged PRs and rewrites the base of the next PR.
- **Merged-upstream-flaw**: open a corrective PR per `references/workflow-correct.md` (compat-migration sub-flow).

### State File Location

`.jj/stack-code/<slug>.json` — see `references/state-schema.md`.

### Standards Referenced

- `GIT-PR-STACK-01` (bookmark naming `<slug>/NN-<scope>`), `GIT-PR-STACK-02..06` (lifecycle, drafts, merge order)
- `GIT-PR-SIZE-01..04` (zone thresholds — enforced by reviewers, not this skill)
- Conventional Commits allowlist (`lib.CONVENTIONAL_TYPES`), mirrored in `coding:write-pr`

### Error Handling & Rollback

- Each mutating script writes `state.last_op_id = jj op log -n1 --no-graph -T 'self.id().short()'`.
- Rollback any step with `jj op restore <last_op_id>`.
- A non-conventional commit subject aborts `execute-stack.py` BEFORE any `jj`/`gh` mutation, with a clear error message naming the failing token.
- `gh pr create` failures leave the bookmark pushed but the PR un-opened — re-run `execute-stack.py --dry-run` to see the residual plan, then re-execute for the failing entry only (state file dedupes by bookmark).
- Hard rule: no `jj git push --force` on already-merged history (`GIT-PR-STACK-03`).

### Idempotence

- `bootstrap.py`, `detect-mode.py`, `propose-splits.py` are pure (no state mutation).
- `execute-stack.py` and `restack.py` are idempotent per-bookmark: re-running over an existing bookmark is a no-op when the change_id matches state.
- `verify.py` is read-only.

## Examples

```bash
# Auto-detect, dry-run only
python3 scripts/bootstrap.py
python3 scripts/detect-mode.py --slug auth-rewrite

# Split-mode end-to-end
python3 scripts/propose-splits.py --slug auth-rewrite > /tmp/plan.json
python3 scripts/execute-stack.py --proposal /tmp/plan.json --dry-run
python3 scripts/execute-stack.py --proposal /tmp/plan.json   # prompts for confirmation

# Restack after main moves
python3 scripts/restack.py --slug auth-rewrite --dry-run

# Verify
python3 scripts/verify.py --slug auth-rewrite
```

### Skill Completion

**Report the skill output as specified**:

```yaml
skill: stack-code
status: completed|failed|partial
outputs:
  mode: noop|create|split
  slug: '<feature-slug>'
  prs:
    - number: NN
      bookmark: '<slug>/NN-<scope>'
      title: '<conventional-commit title>'
      url: '<gh pr url>'
      base: '<prev_bookmark_or_main>'
  state_file: '.jj/stack-code/<slug>.json'
  last_op_id: '<jj op id>'
issues: [...]
summary: |
  Stack [<slug>] landed as N draft PRs per GIT-PR-STACK-01..06.
  [Mode detected, PRs opened, restack/verify status.]
```
