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

This skill is the single entrypoint for saving work: local snapshots, edits to prior changes, splits, reorders, parallel tasks, stacked PRs. It auto-routes based on working-copy state; flags exist only for explicit operations and behavioural overrides. It is the sole owner of history mutations — `coding:finalize-commits` verifies stacks, `/coding:write-pr` authors PR text.

## Boundaries

- Use for: committing or describing changes, splitting mixed work, editing prior changes, retrospective blame fixups, reordering history, parallel workspaces, and materializing stacked PRs.
- Do not use for: composing PR titles or bodies (always `/coding:write-pr` — never compose inline), per-commit QA of an unpushed stack (`coding:finalize-commits`), or diagnosing code failures (`coding:fix`).
- Tool precedence: `jj` first — every change is a jj change and jj auto-snapshots `@` on every op. `git commit` acts only as the conventional-commit emitter inside the save flow on jj-colocated repos, never hand-run outside this skill. `gh` appears only inside the `--create-pr` flow.

<IMPORTANT>
- Every workflow MUST end with a linear clean chain + working code. No exceptions. If a workflow cannot guarantee this, STOP and surface to the user.
- NEVER `git push` directly. Only `jj git push --bookmark <name>` inside `--create-pr`.
- NEVER rewrite merged-on-origin history without explicit consent. Detected target → `AskUserQuestion`, default = corrective PR per `GIT-PR-STACK-03`. `--allow-rewrite-merged` skips the prompt.
- Every change MUST be self-contained: compile + lint + tests pass for each change in isolation. Shared files (package.json, tsconfig, lockfiles) evolve incrementally — no forward references.
- The Conventional Commits subject regex MUST match BEFORE any mutation (see [references/conventional-commits.md](references/conventional-commits.md)); no emoji prefixes in commit subjects.
- `git worktree` ≠ `jj workspace`. If the user accidentally used a git worktree, `AskUserQuestion` to move work back to HEAD before continuing.
</IMPORTANT>

## Inputs

- **Required**: none — the route is read from working-copy state.
- **Optional** (a flag forces its route):

| Flag | Purpose |
|---|---|
| `--retrospective` | Distribute pending edits on `@` into prior changes (stage 1: `jj absorb`; stage 2: `jj blame` + `jj squash --from @ --into <ancestor>`; stage 3: git fixup fallback). See `references/workflow-retrospective.md`. |
| `--reorder [--up-to <rev>]` | Reorder history into a clean linear chain up to target rev (default `main@origin`). Content-equivalence guard via `verify.sh`. See `references/workflow-reorder.md`. |
| `--create-pr` | After saving, materialise bookmarks + push + invoke `/coding:write-pr` + `gh pr create` as stacked draft PRs. Bookmark naming `<branch-prefix>/NN-<scope>` per `GIT-PR-STACK-01`. See `references/workflow-stacked-pr.md`. |
| `--branch-prefix <name>` | Override the auto-derived branch/bookmark prefix used by `--create-pr`. |
| `--no-verify` | Skip pre-commit + post-commit lint/test/build checks. |
| `--dry-run` | Print the plan, don't mutate. |
| `--allow-rewrite-merged` | Explicit consent to rewrite history already merged on origin (skips the `AskUserQuestion` corrective-PR prompt) per `GIT-PR-STACK-03`. |

- **Prerequisites**: a jj-colocated (or plain git) repository; `gh` authenticated when `--create-pr` is used. Standards `GIT-PR-STACK-01..06` (bookmark naming, fix earliest unmerged, no merged-history rewrites, feature flags, bottom-to-top merge, draft PRs) bind every route; `GIT-PR-SIZE-01..04` are reviewer-enforced and informational here.

## Workflow

The skill self-routes by reading `jj diff --stat`, `jj log -r '@-..@'`, and bookmark state. Open the matching reference file for the full procedure:

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

Before writing any new code, plan the change structure so commits/PRs end up independent — see `references/workflow-plan-structure.md`. End-to-end transcripts of every flag and auto-detected route: `references/examples.md`.

1. **Pre-flight.** Backup only runs for history-rewriting routes; plain saves (default, split, parallel, empty) do not touch prior changes and skip `backup.sh` entirely:

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

   When backup runs, the PreToolUse hook fires it on the first rewriting op and injects `Auto-backup: GIT_TREE_SHA=... CONTENT_HASH=... BACKUP_PATH=...` into context. If the route rewrites history but the hook didn't fire, run manually:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/backup.sh"
   ```

   For every route, capture `jj op log -n1 --no-graph -T 'self.id().short()'` as a rollback handle (`jj op restore <id>` undoes any jj operation).

2. **Detect mode.** Read working-copy state and pick exactly one route:

   ```bash
   jj diff --stat               # file count + LOC
   jj log -r 'visible_heads()'  # bookmarks, divergence, empty changes
   jj bookmark list             # existing stack state
   ```

   Choose by the routing table above. If a flag is present, it forces the route.

3. **Propose the plan** to the user before any mutation. For multi-change routes (`--retrospective`, `--reorder`, `--create-pr`, auto-split), show the ordered list of operations. If `--dry-run`, stop here.

4. **Execute** the procedure in the matching reference file: jj primitives for save/edit/reorder/parallel; LLM-driven per-PR loop for `--create-pr` (`workflow-stacked-pr.md`).

5. **Restack downstream** — mandatory after any rewrite that touched a change with an unmerged bookmark below it on the stack:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/restack.sh" <branch-prefix>
   ```

   Skip when there are no downstream bookmarks.

6. Run the verification below; when a check fails, fix the cause (or take the integrity table's prescribed action) and re-run that check. Repeat until every check passes or a concrete blocker remains — an integrity STOP awaiting the user, or a failure outside this skill's scope — then report the blocker instead of looping.

## Verification

The PostToolUse hook auto-runs `verify.sh` after any successful rewriting op and prints `── Integrity Check ──` to stderr. Read the table:

| `GIT_TREE_MATCH` | `CONTENT_MATCH` | Action |
|---|---|---|
| PASS | PASS | OK → report |
| FAIL | PASS | git tree drift → STOP, show diff, await user |
| PASS | FAIL | filesystem drift → STOP, show diff, await user |
| FAIL | FAIL | corruption → STOP, recover via `jj op restore <id>` |

If the hook didn't fire, run manually:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/verify.sh"
```

Then run project lint/test/build via `npm run lint`, `npm run test`, `npm run build` (skip if `--no-verify`), and confirm the final chain is linear with each change self-contained.

## Completion

Report the route taken (save, split, edit, parallel, retrospective, reorder, create-pr, empty, divergent, or correct-merged), changes touched (change IDs), bookmarks (`name@change-id`), PR URLs when `--create-pr` ran, the last jj op id as the rollback handle, and verification results — lint/test/build as PASS/SKIP/FAIL plus the integrity outcome.
