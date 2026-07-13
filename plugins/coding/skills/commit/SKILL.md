---
name: commit
description: 'Save code changes cleanly with jj-first, git-compatible routing. Use for commits, split/absorb/edit operations, stacked changes, history reordering, retrospective blame fixes, or the --create-pr compatibility handoff; preserve the repository history policy and keep coding:commit as the sole history-mutation owner.'
model: opus
allowed-tools: Bash(jj:*), Bash(git:*), Bash(gh:*), Bash(npm:*), Bash(pnpm:*), Bash(bash ${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/*), Read, Grep, Glob, Agent, Skill
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

This skill is the single entrypoint for saving work: local snapshots, edits to prior changes, splits, reorders, parallel tasks, and the compatibility route from `--create-pr` to `coding:push-pr`. It auto-routes based on working-copy state; flags exist only for explicit operations and behavioural overrides. It is the sole owner of history mutations — `coding:finalize-commits` verifies stacks, `coding:push-pr` publishes them, and `coding:write-pr` authors PR text.

**Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike.

## Boundaries

- Use for: committing or describing changes, splitting mixed work, editing prior changes, retrospective blame fixups, reordering history, parallel workspaces, and preserving the `--create-pr` compatibility entrypoint.
- Do not use for: pushing, opening, updating, or polling PRs (`coding:push-pr`), composing PR titles or bodies (`coding:write-pr`), per-commit QA of an unpushed stack (`coding:finalize-commits`), or diagnosing code failures (`coding:fix`).
- Tool precedence: `jj` first — every change is a jj change and jj auto-snapshots `@` on every op. `git commit` acts only as the conventional-commit emitter inside the save flow on jj-colocated repos, never hand-run outside this skill. `gh` is retained for history routes that inspect remote PR state; publication belongs to `coding:push-pr`.

<IMPORTANT>
- Every workflow MUST end with a linear clean chain + working code. No exceptions. If a workflow cannot guarantee this, STOP and surface to the user.
- This skill never pushes, opens, updates, or polls PRs. `coding:push-pr` owns every remote publication and CI-convergence action.
- NEVER rewrite merged-on-origin history without explicit consent. Detected target → `AskUserQuestion`, default = corrective PR per `GIT-PR-STACK-03`. `--allow-rewrite-merged` skips the prompt.
- Every change MUST be self-contained: compile + lint + tests pass for each change in isolation. Shared files (package.json, tsconfig, lockfiles) evolve incrementally — no forward references.
- The Conventional Commits subject regex MUST match BEFORE any mutation (see [references/conventional-commits.md](references/conventional-commits.md)); no emoji prefixes in commit subjects.
- `git worktree` ≠ `jj workspace`. If the user accidentally used a git worktree, `AskUserQuestion` to move work back to HEAD before continuing.
</IMPORTANT>

## Inputs

- **Required**: none — the route is read from working-copy state.
- **Optional** (history flags force a route; publication and behavior flags modify it):

| Flag | Purpose |
|---|---|
| `--retrospective` | Distribute pending edits on `@` into prior changes (stage 1: `jj absorb`; stage 2: `jj blame` + `jj squash --from @ --into <ancestor>`; stage 3: git fixup fallback). See `references/workflow-retrospective.md`. |
| `--reorder [--up-to <rev>]` | Reorder history into a clean linear chain up to target rev (default `main@origin`). Content-equivalence guard via `verify.sh`. See `references/workflow-reorder.md`. |
| `--create-pr` | Compatibility entrypoint: finish the selected save/history route, then invoke `coding:push-pr` with the resolved change or stack. |
| `--branch-prefix <name>` | Forward the branch/bookmark prefix to `coding:push-pr` when `--create-pr` is present. |
| `--no-verify` | Skip pre-commit + post-commit lint/test/build checks. With `--create-pr`, also map this to `coding:push-pr --skip-local-test`; no new commit flag is introduced. |
| `--dry-run` | Print the plan, don't mutate. |
| `--allow-rewrite-merged` | Explicit consent to rewrite history already merged on origin (skips the `AskUserQuestion` corrective-PR prompt) per `GIT-PR-STACK-03`. |

- **Prerequisites**: a jj-colocated (or plain git) repository. Publication prerequisites are checked by `coding:push-pr`. Standards `GIT-PR-STACK-01..06` (bookmark naming, fix earliest unmerged, no merged-history rewrites, feature flags, bottom-to-top merge, draft PRs) bind every route; `GIT-PR-SIZE-01..04` are reviewer-enforced and informational here.

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
| Publish saved change or stack | `--create-pr` | Required handoff to `coding:push-pr` after local history work |

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

   Choose by the routing table above. A history-operation flag forces its
   route; `--create-pr` adds the post-save publication handoff.

3. **Propose the plan** to the user before any mutation. For multi-change routes (`--retrospective`, `--reorder`, `--create-pr`, auto-split), show the ordered list of operations. With `--dry-run`, skip local mutation but still perform the `coding:push-pr --dry-run` handoff when `--create-pr` is present.

4. **Execute local history.** Complete the matching save/edit/reorder/parallel procedure and resolve the exact change or bottom-to-top stack. Do not reproduce any bookmark, push, PR, restack, or CI workflow here.

5. Run the verification below; when a check fails, fix the cause (or take the integrity table's prescribed action) and re-run that check. Repeat until every check passes or a concrete blocker remains — an integrity STOP awaiting the user, or a failure outside this skill's scope — then report the blocker instead of looping.

6. **Hand off publication after local work is complete.** With `--create-pr`, invoke `coding:push-pr <resolved-change-or-stack>` and forward `--branch-prefix <name>` and `--dry-run` when present. If `--no-verify` is also present, pass `--skip-local-test`. After any other local rewrite, identify affected unmerged bookmarks. When invoked by `coding:push-pr`, return the changed stack metadata to that caller so it can resume publication; otherwise invoke `coding:push-pr` once with the resolved stack when remote restacking is required. Its [publication workflow](../push-pr/references/publish-stack.md) owns restack, push, and PR-base repair. Skip the handoff only when no remote publication was requested and no existing remote stack is affected.

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

Report the route taken (save, split, edit, parallel, retrospective, reorder, create-pr compatibility handoff, empty, divergent, or correct-merged), changes touched (change IDs), the last jj op id as the rollback handle, and verification results — lint/test/build as PASS/SKIP/FAIL plus the integrity outcome. When `--create-pr` ran, preserve the PR URLs and final green state returned by `coding:push-pr`; this skill itself never pushes, opens, updates, or polls.
