---
name: stack-code
description: 'Orchestrate jj-based stacked GitHub PRs end-to-end: auto-detects create vs split mode, drives `jj split`/`jj describe`/`jj bookmark set`/`jj git push`, and opens each draft PR with a Conventional Commits title and the unified PR body from `coding:write-pr`. Triggers when: "/stack-code", "stack these PRs", "split this branch into a stack", "open a PR stack". Also use when: a working copy has multiple loosely-coupled changes that should land as ordered draft PRs, or main has moved and an open stack needs restacking. Examples: "stack-code this feature outline", "split my chunky branch into PRs", "restack my open stack against latest main".'
model: opus
allowed-tools: Bash(jj:*), Bash(gh:*), Bash(python3:*), Read
argument-hint: [--slug <slug>] [--mode create|split] [--fix-up] [--dry-run]
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
- Sibling skill `coding:write-pr` available — the unified template lives at `../write-pr/references/templates/pr.md` and is read directly by `execute-stack.py`. No shell-out to `write-pr` Python scripts (they no longer exist). Each stacked PR opens as a self-contained PR: `context_body` and `implementation_body` MUST be substantive narrative per slice — `execute-stack.py` HARD-FAILS when they are empty or carry stack-metadata padding.
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
- **`--fix-up`** (default: OFF): on a re-run for an existing bookmark, squash/absorb the working-copy edits into the bookmark's existing owning change (per `GIT-PR-STACK-02`) and re-push the bookmark via `jj git push --bookmark <name>` (force-with-lease for unmerged bookmarks). The public git history then reflects the change as if it had been implemented correctly the first time. When OFF, subsequent edits become ordinary follow-up commits stacked on top of the existing bookmark via `jj new <change_id>` + `jj describe` + `jj bookmark set <name> -r @-`; a single PR may carry multiple commits. In BOTH modes, after any successful re-run that touches an unmerged bookmark, the orchestrator unconditionally re-runs the restack flow so downstream stack PRs are re-parented onto the new tip and never depend on stale git commits. `--fix-up` MUST refuse to rewrite already-merged commits per `GIT-PR-STACK-03`; merged state is detected via `gh pr view --json state` and the run aborts with a clear, actionable error pointing to the corrective-PR sub-flow in `references/workflow-correct.md`.
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

### Proposal Schema (required per-slice fields)

Each entry in `proposal["prs"]` MUST carry the fields below. `execute-stack.py` hard-fails before any mutation when a required field is missing or boilerplate-only.

| Field                     | Required | Source / Description                                                                |
| ------------------------- | -------- | ----------------------------------------------------------------------------------- |
| `n`                       | yes      | PR ordinal (integer); drives `<slug>/NN-<scope>` bookmark naming.                   |
| `scope`                   | yes      | Kebab-case scope; validated by `lib.bookmark_name`.                                 |
| `bookmark`                | yes      | Full bookmark `<slug>/NN-<scope>`.                                                  |
| `files`                   | yes      | Paths owned by this slice (used by `jj split`, diff inspection, idempotence guard).|
| `title`                   | yes      | Conventional Commits title; validated by `lib.validate_conventional_subject`.       |
| `summary`                 | yes      | Plain-language one-sentence purpose; fills `{{summary_paragraph}}`.                 |
| `context_body`            | yes      | Substantive narrative — WHY this slice exists. MUST NOT reference other PRs in the stack. Hard-fails when empty or contains stack-metadata markers. |
| `implementation_body`     | yes      | Substantive narrative — WHAT changed and WHY this approach. MUST NOT be a flat file list. Hard-fails when empty or contains stack-metadata markers. |
| `breaking_changes_body`   | no       | Migration notes. Auto-filled with `None.` only when `title` carries `!` but body is blank. |
| `related_issues_body`     | no       | `Closes:` / `Refs:` lines. Drop section when absent.                                |
| `manual_testing_body`     | no       | Reviewer repro steps. Drop section when absent.                                     |
| `additional_notes_body`   | no       | Limitations, follow-ups. Drop section when absent.                                  |
| `delivered_trailer`       | no       | Extra `- [x]` items beyond the diff-derived defaults.                               |
| `reviewer_trailer`        | no       | Extra `- [ ]` items beyond the change-shape-derived defaults.                       |

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
  6. Read `../write-pr/references/templates/pr.md`, substitute placeholders from the proposal entry, and write the body to a tempfile. Each slice's proposal MUST include a self-contained `context_body` and `implementation_body`; do not reference other PRs in the stack from the body. `execute-stack.py` HARD-FAILS (exits non-zero, names the offending slice) when either field is empty or contains stack-metadata boilerplate (e.g. `Part of stack ...`, `Files in this slice`). Fix the proposal at source — there is no auto-padding fallback.
  7. `gh pr create --draft --title "<conventional-title>" --body-file <tmp> --base <prev_or_main>` per `GIT-PR-STACK-06`.

### Step 7: Verify

- **Script**: `scripts/verify.py --slug <slug>`
- Typecheck: auto-detect `tsc --noEmit` or `mypy`. State integrity: every PR has a resolvable `change_id`. Full tests prompt-only.

### Step 8: Ongoing Operations

- **Re-run for an existing bookmark (`--fix-up` ON, default OFF)**: `execute-stack.py --slug <slug> --fix-up` squashes/absorbs working-copy edits into the bookmark's existing owning change (`jj edit <change_id>` + `jj squash` / `jj absorb`) per `GIT-PR-STACK-02`, then re-pushes via `jj git push --bookmark <name>` (force-with-lease for unmerged bookmarks). Public git history reads as if the change had been implemented correctly the first time. Sub-flows A and B in `references/workflow-correct.md` describe the underlying jj operations.
- **Re-run for an existing bookmark (`--fix-up` OFF, default)**: subsequent edits land as ordinary follow-up commits stacked on top of the existing bookmark via `jj new <change_id>` + `jj describe` + `jj bookmark set <name> -r @-`. A single PR may then carry multiple commits. See sub-flow E in `references/workflow-correct.md`.
- **Mandatory restack after any rewrite or follow-up**: in BOTH `--fix-up` modes, after any successful re-run that touched an unmerged bookmark, the orchestrator unconditionally invokes `scripts/restack.py --slug <slug>` so downstream stack PRs are re-parented onto the new tip and never depend on stale git commits.
- **Merged-history guard for `--fix-up`**: `--fix-up` MUST refuse to rewrite already-merged commits (`GIT-PR-STACK-03`). `execute-stack.py` checks each affected bookmark's PR state via `gh pr view --json state` and aborts with a clear, actionable error pointing the user to the corrective-PR sub-flow C in `references/workflow-correct.md` if any target is `MERGED`.
- **Review-comment correction**: `references/workflow-correct.md` — `jj edit <change>` + `jj absorb` for in-place fixes (sub-flows A/B, default `--fix-up` path); corrective PR on top (sub-flow C) when public history would be rewritten (`GIT-PR-STACK-03`).
- **Main moved**: `scripts/restack.py --slug <slug>` rebases the next unmerged bookmark onto `main@origin` and re-parents open PRs.
- **Lower PR merged**: `restack.py` auto-detects merged PRs and rewrites the base of the next PR.
- **Merged-upstream-flaw**: open a corrective PR per `references/workflow-correct.md` (compat-migration sub-flow D).

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
- A slice with an empty or boilerplate-only `context_body` / `implementation_body` aborts `execute-stack.py` BEFORE any `jj`/`gh` mutation, with a clear error naming the offending slice (`#NN <bookmark>`). There is no auto-padding fallback; the proposal must be fixed at source.
- `gh pr create` failures leave the bookmark pushed but the PR un-opened — re-run `execute-stack.py --dry-run` to see the residual plan, then re-execute for the failing entry only (state file dedupes by bookmark).
- `--fix-up` against an already-merged bookmark aborts BEFORE any rewrite or push: `gh pr view --json state` returns `MERGED`, `execute-stack.py` exits with a non-zero status and prints the failing bookmark + a pointer to sub-flow C (corrective PR) in `references/workflow-correct.md`. No `jj` mutation is performed.
- The mandatory post-rewrite/post-follow-up restack (`scripts/restack.py --slug <slug>`) runs even if the originating `--fix-up` (or follow-up) succeeded but pushed only a single bookmark — failure to restack downstream PRs is treated as a hard error and surfaced in the summary.
- Hard rule: no `jj git push --force` on already-merged history (`GIT-PR-STACK-03`); `--fix-up` honours this via the merged-state check above.

### Idempotence

- `bootstrap.py`, `detect-mode.py`, `propose-splits.py` are pure (no state mutation).
- `execute-stack.py` and `restack.py` are idempotent per-bookmark: re-running over an existing bookmark with no working-copy edits is a no-op when the `change_id` matches state, regardless of `--fix-up`.
- `--fix-up` ON: re-runs with new working-copy edits squash/absorb into the existing owning change and re-push the bookmark; repeat invocations with no further edits are no-ops.
- `--fix-up` OFF (default): re-runs with new working-copy edits append a follow-up commit on the existing bookmark and re-push; repeat invocations with no further edits are no-ops.
- In both `--fix-up` modes, the mandatory post-rewrite/post-follow-up `restack.py` invocation is itself idempotent — running it when downstream PRs are already re-parented is a no-op.
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

# Re-run for an existing bookmark, FIX-UP mode (squash/absorb into existing change, force-with-lease push)
python3 scripts/execute-stack.py --proposal /tmp/plan.json --fix-up --dry-run
python3 scripts/execute-stack.py --proposal /tmp/plan.json --fix-up
# -> orchestrator unconditionally re-runs restack.py for downstream PRs after the rewrite

# Re-run for an existing bookmark, FOLLOW-UP mode (default, --fix-up OFF)
python3 scripts/execute-stack.py --proposal /tmp/plan.json
# -> appends a new commit to the existing bookmark; PR carries multiple commits
# -> orchestrator unconditionally re-runs restack.py for downstream PRs after the follow-up

# --fix-up against an already-merged bookmark aborts before any mutation
python3 scripts/execute-stack.py --proposal /tmp/plan.json --fix-up
# error: bookmark <slug>/01-<scope> is MERGED — refusing to rewrite per GIT-PR-STACK-03;
#        see references/workflow-correct.md sub-flow C (corrective PR) instead.

# Restack after main moves (also invoked unconditionally after any --fix-up or follow-up re-run)
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
  fix_up: false  # true when invoked with --fix-up; false (default) for follow-up-commit mode
  prs:
    - number: NN
      bookmark: '<slug>/NN-<scope>'
      title: '<conventional-commit title>'
      url: '<gh pr url>'
      base: '<prev_bookmark_or_main>'
  restacked_downstream_bookmarks:
    - '<slug>/NN+1-<scope>'  # bookmarks re-parented by the mandatory post-rewrite/post-follow-up restack
    - '<slug>/NN+2-<scope>'  # empty list when no downstream bookmarks existed or none required re-parenting
  state_file: '.jj/stack-code/<slug>.json'
  last_op_id: '<jj op id>'
issues: [...]
summary: |
  Stack [<slug>] landed as N draft PRs per GIT-PR-STACK-01..06.
  [Mode detected, PRs opened, fix_up flag, restacked downstream bookmarks, restack/verify status.]
```
