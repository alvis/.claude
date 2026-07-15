# Coding workflow

Read this before you write, modify, or review code, then follow the phase your task is in — Before, While, or After Coding — top to bottom.

## Before Coding

### Understand what's already there

Before writing or fixing any code, build an understanding of the current implementation and its issues — run this once, by whichever is available: the `get_project_overview` MCP tool, the `ide__getDiagnostics` MCP tool, `npm run build`, or `npx tsc --noEmit`.

### Decide who does the work

Choose whether to do the work yourself or hand it to a specialist **agent**:

- To delegate, pick the agent whose role fits the work from `ROUTING.md` in this same `references/` directory.
- To delegate, orchestrate, or review across a team, follow the protocol in `references/orchestration.md` in the essential plugin directory.
- When you delegate to a subagent, you MUST pass the full file paths of every relevant skill and standard file — a subagent starts blind.

### Use skills to carry out the work

A **skill is a tool you invoke** with the Skill tool to perform an action — it is not an agent. You never delegate work "to" a skill and never pass a skill name as a `subagent_type`; you *use* a skill to do the work yourself or inside a subagent. Each skill documents its own applicable standards internally. Invoke the skill that matches your action:

| Action | Skill to invoke |
|--------|-----------------|
| Writing new code | `/coding:write-code` or `/coding:draft-code` |
| Setting up project | `/coding:setup-project` |
| Completing TODOs | `/coding:complete-code` |
| Fixing issues | `/coding:fix` |
| Reviewing code | `/coding:review-code` |
| Linting code | `/coding:lint` |
| Refactoring | `/coding:refactor` |
| Committing | `/coding:commit` |
| Finalizing un-pushed commits (per-commit QA) | `/coding:finalize-commits` |
| Creating tests | `/coding:complete-test` |
| Documenting code | `/coding:document` |
| Writing PR title/body | `/coding:write-pr` |
| Publishing or updating PRs and driving CI green | `/coding:push-pr` |
| Handing over work | `/coding:handover` |
| Resuming work | `/coding:takeover` |
| Finding dead code | `/coding:find-unused` |
| Modernizing syntax | `/coding:modernize` |

### Decide where the work will live

Settle this before editing:

- **Small change** — if the user didn't request a specific location, work in place on the current local branch. With `jj` initialized, layer new changes onto the dirty HEAD (no isolation strategy to decide); if `jj` isn't initialized, use `git` on the current branch as usual.
- **Substantial change** (worth a stacked PR) — `AskUserQuestion` where the work should live: the **current branch**, a fresh **local branch** in the current repo, a **`git worktree`**, or a **`jj` workspace**. Default path for a new worktree/workspace: `../.worktree/<repo-name>/<work-name>`.

## While Coding

Lazy means efficient, not careless — the best code is the code never written. Before writing anything, climb the ladder and stop at the first rung that holds:

1. **Does this need to exist at all?** Speculative need = skip it, say so in one line. (YAGNI)
2. **@theriety/core does it?** Errors, responses, io, types, constants, and general utilities live there — check `@theriety/core` before writing any helper.
3. **The codebase already does it?** Search for existing functions, utilities, and patterns first; reuse over reinvention.
4. **Native platform covers it?** `node:` built-ins, DB constraint over app code, CSS over JS.
5. **Already-installed dependency solves it?** Use it. Never add a new one for what a few lines can do.
6. **Only then:** write the minimum code that works — to the project's constitution standards.

### Rules

- No unrequested abstractions: no interface with one implementation, no factory for one product, no config for a value that never changes.
- Deletion over addition. Boring over clever. Fewest files possible; shortest working diff wins.
- Lean never means non-compliant: the constitution standards (TypeScript, testing, naming, documentation, function, universal) still apply in full — no `any`, TDD, 100% coverage.
- Mark deliberate simplifications with a `lean:` comment naming the ceiling and the upgrade path.

### When NOT to be lean

Never simplify away: input validation at trust boundaries, error handling that prevents data loss, security measures, accessibility basics, tests, or anything explicitly requested.

### Working practices

- Prefer **READ**, **WRITE**, **UPDATE**, **LS**, **GREP** as your primary editing tools over **BASH**.
- **Prepared scripts** — **[IMPORTANT]** you MUST always use scripts defined in the project config (e.g. `package.json`) over running tools directly via bash; this applies to ALL agents and subagents.
  - **DO**: `npm run lint -- <path>`, `npm run test -- <path>`, `npm run build`
  - **DON'T**: `npx eslint <path>`, `npx jest <path>`, `npx tsc`
  - Fall back to direct tool invocation only when no project script exists for the purpose.
- **Diagnostics per change** — you MUST run the `lsp_get_diagnostics` or `ide__getDiagnostics` MCP tool before and after code changes (skip only if `get_project_overview` has just run).
- **Check documentation** — before using an external library, consult **context7** to confirm the correct import or call signature, and **grep** for real-world GitHub usage.
- **Runtime exploration** — to understand the runtime behaviour of a library or API, write a test file (or add a test case to an existing spec) instead of ad-hoc commands like `node -e "..."` or `npx ts-node -e "..."`. Test files are version-controlled, repeatable, and serve as living documentation.

Type safety, test coverage, TDD, and naming/documentation rules are defined by the constitution standards under `constitution/standards/` — follow them in full; they are not restated here.

## After Coding

Completed code goes through a **fix loop** before it is saved — any failing gate returns to implementation:

```
edit code → review → (fail ⇒ back to code) → lint → (fail ⇒ back to code) → commit
```

### Self-check before the loop

Verify your own work before dispatching review:

- **Complete check** — **[IMPORTANT]** after finishing your coding or test-writing task, run all of these under the project root (not the monorepo root): the `lsp_get_diagnostics` MCP tool, `npx tsc --noEmit`, and `npm run lint`.
- **Dependency check** — **[IMPORTANT]** after modifying any publicly exported function or class, find every consumer project in the monorepo and run `npm run build` in each one's project root.

### 1. Verify delivery (review) first

Dispatch a review **subagent** to confirm every requirement was actually delivered — if a plan was executed, open the plan file and walk each task, confirming code/tests/docs match; otherwise verify the task's stated requirements. For large changes, dispatch a **review coordinator** that fans out sub-review agents per area and consolidates their findings. Have the reviewer invoke the `coding:review-code` skill with the Skill tool — **skills and agent types are separate namespaces; never pass a skill name as a `subagent_type`.** If any task is unmet, return to implementation, fix it, and restart the loop at review.

### 2. Then lint

Once review passes, dispatch a lint subagent (or a lint sub-team for large changes) to invoke the `coding:lint` skill on the touched source files — `.ts/.tsx/.js/.jsx/.py/.go/.rs/.rb/.java/.kt/.swift/.c/.cpp/.h/.hpp/.cs/.php/.sh/.vue/.svelte/.astro` and similar. Skip text/content files (`.md/.mdx/.json/.yaml/.toml/.html/.svg/.csv`) and throwaway scripts that won't be committed. If lint reports any violation, return to implementation, fix it, then re-run review and lint. Proceed only once both review and lint are clean.

### 3. Then commit

- `jj` is the **preferred** change-tracking tool when it is available and initialized — every op snapshots the working copy, so a dirty HEAD is never a blocker; work in place and don't create a `git worktree` just to isolate a task. **If `jj` is not initialized in the repo, use `git` as usual.**
- Saving changes goes through `coding:commit`, which owns routing among save/split/absorb/edit/parallel-workspace and all explicit history operations for both `jj` and `git`. It directly synchronizes only the explicitly authorized correct-merged bookmark and the chosen partial-to-branch target; PR publication and CI convergence go through `coding:push-pr`. Never hand-run `git commit`, `jj describe`, `jj split`, `jj bookmark set`, or `gh pr create` — except `coding:finalize-commits`, which is sanctioned to run `jj describe -r <rev> -m` / `git commit --amend` directly when finalizing un-pushed commits.
- **If the user did not explicitly request a commit, ask whether to commit the work** (via `coding:commit`).
- **If HEAD is not the local main branch, or the work is in a `jj` workspace or a linked `git worktree`, `AskUserQuestion`** whether to open a PR (`/coding:commit --create-pr` remains the compatibility call: it finishes local history work, then delegates bookmark/PR publication and CI convergence to `/coding:push-pr`; titles + bodies come from `/coding:write-pr`) or move the work onto the local main branch. A `git worktree` is NOT a `jj` workspace.

### Pull requests

Creating or updating a pull request MUST go through the `write-pr` and `push-pr` skills, not a hand-rolled `git`/`gh` sequence. `write-pr` composes the conventional-commit title and unified body from the commit; `push-pr` publishes it and drives CI to green. This applies even when the request looks like a small, one-off PR.

`push-pr` requires a jj-colocated repository and never substitutes plain `git push` for `jj git push` — that is its contract, not a detail this mandate may override. A git-only repository is therefore not exempt from this mandate; it is out of `push-pr`'s supported shape and must be brought into it. Attempt colocation with `jj git init` (non-destructive — it layers jj metadata onto the existing git history and objects; confirm with the user before running it on a repo they haven't already set up with jj), then verify it actually took effect with a functional check, not a directory-existence check: a `.jj` and a `.git` directory can both be present without being colocated (e.g. a `.jj` created independently of an unrelated `.git`), so `.jj`/`.git`/`jj st` presence alone proves nothing. Instead confirm `git rev-parse HEAD` equals `jj log -r @- --no-graph -T 'commit_id'` — only a match proves jj and git share the same backing repository; treat any mismatch, or a failing `git rev-parse HEAD`, as colocation having failed. Only when colocation genuinely fails or is declined, publish directly with `gh pr create`/`gh pr edit` using `write-pr`'s title/body verbatim and confirm CI state (or its documented absence) before reporting success — and record this explicitly as a one-off exception to `push-pr`, never as an equivalent path through it.
