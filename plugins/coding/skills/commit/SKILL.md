---
name: commit
description: 'Save code changes cleanly with jj-first, git-compatible routing. Use for commits, split/absorb/edit operations, stacked changes, restacks, history reordering, retrospective blame fixes, or PR materialization; preserve the repository history policy and keep coding:commit as the sole history-mutation owner.'
model: opus
allowed-tools: Bash(jj:*), Bash(git:*), Bash(gh:*), Bash(npm:*), Bash(pnpm:*), Bash(bash ${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/*), Read, Grep, Glob, Agent
argument-hint: "[--retrospective] [--reorder [--up-to <rev>]] [--create-pr] [--branch-prefix <name>] [--no-verify] [--dry-run] [--allow-rewrite-merged]"
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/pre-commit-hook.sh"
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/post-rewrite-hook.sh"
---

# Save Any Code Change — jj-first, git-compatible

This skill is the single entrypoint for saving work: local snapshots, edits to prior changes, splits, reorders, parallel tasks, stacked PRs. It auto-routes based on working-copy state; flags exist only for explicit operations and behavioural overrides.

## Prime Directive

**Every workflow MUST end with a linear clean chain + working code.** No exceptions. If a workflow cannot guarantee this, STOP and surface to the user.

## Tool Priority

1. **`jj` first** — every change is a jj change. jj auto-snapshots `@` on every op.
2. **`git commit` is the conventional-commit emitter** — used inside save flow on jj-colocated repos. Never hand-run outside this skill.
3. **`gh` for PRs** — only inside `--create-pr` flow. Never `git push` directly.
4. **PR titles + bodies are produced by `/coding:write-pr`** — never compose inline.

## Scenario Router

The skill self-routes by reading `jj diff --stat`, `jj log -r '@-..@'`, and bookmark state. Open the matching reference file for full procedure.

| Trigger | How invoked | Reference |
|---|---|---|
| Default save | (no flag) | `references/workflow-save-local.md` |
| Multiple concerns on `@` | auto-detected | `references/workflow-split.md` |
| User asks "edit commit X" | auto-detected | `references/workflow-edit.md` |
| Proposed work unrelated to current `@` | auto-detected | `references/workflow-parallel.md` |
| `@` is empty | auto-detected | `references/scenario-empty-changes.md` |
| Divergent change ID in `jj log` | auto-detected | `references/scenario-divergent.md` |
| Target already merged on origin | auto-detected | `references/workflow-correct-merged.md` |
| Blame-trace fixups into prior changes | `--retrospective` | `references/workflow-retrospective.md` |
| Reorder existing history | `--reorder [--up-to <rev>]` | `references/workflow-reorder.md` |
| Partial hunks → existing branch | user names a target branch + asks to save part of `@` | `references/workflow-partial-to-branch.md` |
| Open stacked PRs | `--create-pr` | `references/workflow-stacked-pr.md` |

Before writing any new code, plan the change structure so commits/PRs end up independent — see `references/workflow-plan-structure.md`.

## Default Pipeline (6 steps)

ultrathink: walk these steps for every invocation.

### Step 0 — Pre-flight

**Backup only runs for history-rewriting routes.** Plain saves (default, split, parallel, empty) do not touch prior changes and therefore skip `backup.sh` entirely.

| Route | Rewrites history? | Backup |
|---|---|---|
| Default save (`jj describe` + `git commit`) | No | skip |
| Split current change (`jj split`) | No | skip |
| Parallel workspace (`jj new` / `jj workspace add`) | No | skip |
| Empty / divergent | No | skip |
| Edit prior change (`jj edit`) | Yes | run |
| `--retrospective` (`jj absorb` / `jj squash`) | Yes | run |
| `--reorder` (`jj rebase`) | Yes | run |
| Partial hunks → existing branch (`git add -p` + `git commit` + `jj git import` + `jj bookmark move --allow-backwards`) | Yes (bookmark move, possibly backward) | run |
| Correct merged target (`git rebase` fallback) | Yes | run |

When backup runs, the PreToolUse hook fires it on the first rewriting op and injects `Auto-backup: GIT_TREE_SHA=... CONTENT_HASH=... BACKUP_PATH=...` into context. **If the route rewrites history but the hook didn't fire**, run manually:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/backup.sh"
```

For every route, capture `jj op log -n1 --no-graph -T 'self.id().short()'` as a rollback handle (`jj op restore <id>` undoes any jj operation).

### Step 1 — Detect mode

Read working-copy state and pick exactly one route:

```bash
jj diff --stat               # file count + LOC
jj log -r 'visible_heads()'  # bookmarks, divergence, empty changes
jj bookmark list             # existing stack state
```

Choose by the Scenario Router table above. If a flag is present, it forces the route.

### Step 2 — Propose plan

Present the plan to the user before any mutation. For multi-change routes (`--retrospective`, `--reorder`, `--create-pr`, auto-split), show the ordered list of operations.

If `--dry-run`, stop here.

### Step 3 — Execute

Follow the procedure in the matching reference file. jj primitives for save/edit/reorder/parallel; LLM-driven per-PR loop for `--create-pr` (`workflow-stacked-pr.md`).

### Step 4 — Restack downstream (mandatory after any rewrite)

If the execution touched a change with an unmerged bookmark below it on the stack:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/restack.sh" <branch-prefix>
```

Skip when there are no downstream bookmarks.

### Step 5 — Verify integrity

The PostToolUse hook auto-runs `verify.sh` after any successful rewriting op and prints `── Integrity Check ──` to stderr. Read the table:

| `GIT_TREE_MATCH` | `CONTENT_MATCH` | Action |
|---|---|---|
| PASS | PASS | OK → Step 6 |
| FAIL | PASS | git tree drift → STOP, show diff, await user |
| PASS | FAIL | filesystem drift → STOP, show diff, await user |
| FAIL | FAIL | corruption → STOP, recover via `jj op restore <id>` |

If hook didn't fire, run manually:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/verify.sh"
```

Then run project lint/test/build via `npm run lint`, `npm run test`, `npm run build` (skip if `--no-verify`).

### Step 6 — Report

```text
[OK/FAIL] Command: commit

## Summary
- Route taken: <save | split | edit | parallel | retrospective | reorder | create-pr | empty | divergent | correct-merged>
- Changes touched: <change-ids>
- Bookmarks: <name@change-id>
- PRs: <urls if --create-pr>
- Last op id: <jj op id for rollback>

## Verification
- Lint / Test / Build: <PASS/SKIP/FAIL>
- Integrity (Step 5): <PASS/FAIL>
```

## Hard Rules

- **NEVER `git push` directly.** Only `jj git push --bookmark <name>` inside `--create-pr`.
- **NEVER rewrite merged-on-origin history without explicit consent.** Detected target → `AskUserQuestion`, default = corrective PR per `GIT-PR-STACK-03`. `--allow-rewrite-merged` skips the prompt.
- **Every change MUST be self-contained.** Compile + lint + tests pass for each change in isolation. Shared files (package.json, tsconfig, lockfiles) evolve incrementally — no forward references.
- **Conventional Commits subject regex MUST match BEFORE any mutation.** See `references/conventional-commits.md`.
- **No emoji prefixes** in commit subjects.
- **PR titles + bodies always produced by `/coding:write-pr`** — never compose inline.
- **`git worktree` ≠ `jj workspace`.** If user accidentally used a git worktree, `AskUserQuestion` to move work back to HEAD before continuing.

## Flags

| Flag | Purpose |
|---|---|
| `--retrospective` | Distribute pending edits on `@` into prior changes (stage 1: `jj absorb`; stage 2: `jj blame` + `jj squash --from @ --into <ancestor>`; stage 3: git fixup fallback). See `references/workflow-retrospective.md`. |
| `--reorder [--up-to <rev>]` | Reorder history into a clean linear chain up to target rev (default `main@origin`). Content-equivalence guard via `verify.sh`. See `references/workflow-reorder.md`. |
| `--create-pr` | After saving, materialise bookmarks + push + invoke `/coding:write-pr` + `gh pr create` as stacked draft PRs. Bookmark naming `<branch-prefix>/NN-<scope>` per `GIT-PR-STACK-01`. See `references/workflow-stacked-pr.md`. |
| `--branch-prefix <name>` | Override the auto-derived branch/bookmark prefix used by `--create-pr`. |
| `--no-verify` | Skip pre-commit + post-commit lint/test/build checks. |
| `--dry-run` | Print the plan, don't mutate. |
| `--allow-rewrite-merged` | Explicit consent to rewrite history already merged on origin (skips the `AskUserQuestion` corrective-PR prompt) per `GIT-PR-STACK-03`. |

## Standards Referenced

- `GIT-PR-STACK-01..06` — bookmark naming, fix earliest unmerged, no merged-history rewrites, feature flags, bottom-to-top merge, draft PRs
- `GIT-PR-SIZE-01..04` — reviewer-enforced zone thresholds (informational here)
- Conventional Commits allowlist — see `references/conventional-commits.md`

## Examples

See `references/examples.md` for end-to-end transcripts of every flag and auto-detected route.
