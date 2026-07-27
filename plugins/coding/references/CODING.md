# Coding workflow

Read this before you write, modify, review, upload, or publish code — committing, pushing, and opening or updating a pull request are covered too — then follow the phase your task is in — Before, While, or After Coding — top to bottom.

## Before Coding

### Decide who does the work

Settle this first, from where the task came:

- **From the user** — do it yourself when the change is small (low expected token spend); delegate it otherwise.
- **From another agent** — do it yourself, unless you are a lead (an orchestrator). A lead never implements; it only advises and delegates.

To delegate, read `ROUTING.md` in this same `references/` directory and route the work to the specialist whose role fits; and read `orchestration.md` in the essential plugin's `references/` directory before you delegate, orchestrate, or review across a team. Hand the delegate the full file paths of every relevant skill and standard file — a subagent starts blind.

### Decide where the work will live

Settle this before editing:

- **Small change** — if the user didn't request a specific location, work in place on the current local branch. With `jj` initialized, layer new changes onto the dirty HEAD (no isolation strategy to decide); on a git repository, work on the current branch as usual.
- **Substantial change** (worth a stacked PR) — `AskUserQuestion` where the work should live: the **current branch**, a fresh **local branch** in the current repo, a **`git worktree`**, or a **`jj` workspace**. Default path for a new worktree/workspace: `~/.workspaces/<project-root-folder-name>/<work-id>` (reuse the engineering work-id; the built-in `EnterWorktree` harness tool uses `.claude/worktrees/` and is not governed by this convention).
  - The work-id names the state directory, the source tree, and the branch: `.state/works/<work-id>`, `~/.workspaces/<project-root-folder-name>/<work-id>`, and branch `<type>/<work-id>` — the type prefixes the branch only, never the id or the state path. Work that stays a single PR uses `feat/<work-id>` and nothing more, no ordinal and no slice. A stream split into a stack or into sub-tasks becomes two-digit-numbered branches beneath it: `feat/<work-id>/01-resolver`, `feat/<work-id>/02-contract`. Either way the stream is identified from the branch that is checked out; a branch shaped otherwise resolves to nothing and the PM is asked instead.
  - Those two shapes cannot coexist — git stores refs as files, so `feat/<work-id>` blocks `feat/<work-id>/01-resolver` and vice versa. A single-PR stream that grows cannot add a numbered branch beside the bare one, so it **renames** the bare branch into the first slice — through the forge's branch rename, which retargets the open PR rather than closing it — and pushes the later slices only after that lands. Full rules live in `naming.md` in the essential plugin's `references/` directory.

### If you're writing it yourself

**Understand what you're changing first.** Before writing or fixing any code, build an understanding of the current implementation and its issues — run this once, by whichever is available: the `get_project_overview` MCP tool, the `ide__getDiagnostics` MCP tool, `npm run build`, or `npx tsc --noEmit`.

**Carry out each action with the skill that matches it.** A skill is a tool you invoke with the Skill tool — it is not an agent. You never delegate work "to" a skill and never pass a skill name as a `subagent_type`; you *use* a skill to do the work yourself or inside a subagent. Each skill documents its own applicable standards internally.

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
| Writing PR title/body, publishing or updating PRs, and driving CI green | `/coding:write-pr` |
| Pausing work | `/essential:handover` |
| Resuming work | `/essential:takeover` |
| Finding dead code | `/coding:find-unused` |
| Modernizing syntax | `/coding:modernize` |

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

- `jj` is the **preferred** change-tracking tool when it is both installed on PATH and initialized for this repository — every op snapshots the working copy, so a dirty HEAD is never a blocker; work in place and don't create a `git worktree` just to isolate a task. Prove that initialization functionally rather than by directory presence: a `.jj` and a `.git` directory can both exist without sharing a backing repository, so confirm `git rev-parse HEAD` equals `jj log -r @- --no-graph -T 'commit_id'`. Anything else — `jj` missing, either command failing, or the two ids differing — means this is a git repository, and **`git` is then the normal, fully supported path** through every skill below, not a degraded one.
- Saving changes goes through `coding:commit`, which owns routing among save/split/absorb/edit/parallel-workspace and all explicit history operations for both `jj` and `git`. It directly synchronizes only the explicitly authorized correct-merged bookmark and the chosen partial-to-branch target; PR publication and CI convergence go through `coding:write-pr`. Never hand-run `git commit`, `jj describe`, `jj split`, `jj bookmark set`, or `gh pr create` — except `coding:finalize-commits`, which is sanctioned to run `jj describe -r <rev> -m` / `git commit --amend` directly when finalizing un-pushed commits.
- **If the user did not explicitly request a commit, ask whether to commit the work** (via `coding:commit`).
- **If HEAD is not the local main branch, or the work is in a `jj` workspace or a linked `git worktree`, `AskUserQuestion`** whether to open a PR (`/coding:commit --create-pr` remains the compatibility call: it finishes local history work, then delegates title/body authoring, bookmark/PR publication, and CI convergence to `/coding:write-pr`) or move the work onto the local main branch. A `git worktree` is NOT a `jj` workspace.

### Pull requests

Creating or updating a pull request MUST go through the `write-pr` skill, not a hand-rolled `git`/`gh` sequence. `write-pr` composes the conventional-commit title and unified body from the commit, publishes it, and drives CI to green. This applies even when the request looks like a small, one-off PR.

`write-pr` publishes from whichever change-tracking tool the repository already uses, and decides which by running the functional colocation check above — never by asking anyone to initialize `jj`. On a jj-colocated repository it moves the bookmark and pushes with `jj git push`; on a git repository it pushes the same branch with `git push --force-with-lease` and opens or updates the PR with `gh pr create`/`gh pr edit`, using its authored title and body verbatim. Both are equally sanctioned publication paths: each ends with a draft PR on the intended base and CI driven to green (or its documented absence confirmed), and neither is an exception to be recorded, apologized for, or converted into the other.
