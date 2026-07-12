## Delegation Rule

**When delegating tasks to subagents, you MUST pass the full file paths of relevant skill and standard files to the subagent.**

Each skill documents its own applicable standards internally. Route actions to the appropriate skill:

| Action | Route to |
|--------|----------|
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
| Handing over work | `/coding:handover` |
| Resuming work | `/coding:takeover` |
| Finding dead code | `/coding:find-unused` |
| Modernizing syntax | `/coding:modernize` |

## Agent Orchestration

Delegation is a tool for managing signal, not a default reflex. Spawn a subagent or agent teammate ONLY when the task is big or its expected output is large — i.e. when an agent is needed to digest a haystack of files, logs, or search results and hand back the distilled signal. If a task is small enough that you could do it inline with a couple of tool calls, delegating it just adds latency and a lossy hand-off; do it yourself.

### Model Selection

When designing a dynamic workflow or spawning agents, match the model to the cognitive demand of the task — never default everything to the largest model, and never starve a hard task with a small one:

| Model | Use for |
|-------|---------|
| **haiku** | Simple, routine, deterministic tasks with a known procedure — executing tests, running lint, collecting command output, mechanical file sweeps. You can always rely on haiku here. |
| **sonnet** | Tasks that expect branching — investigation where the next step depends on what is found, triage, moderate-complexity edits with a few decision points. |
| **opus** | General coding — implementing features, fixing non-trivial bugs, refactoring with judgment. |
| **fable** | Advanced coding, deep reasoning, research, and code review — anything where correctness hinges on subtle judgment, adversarial scrutiny, or synthesizing across many sources. |

Effort is a second, independent dial. When you spawn a subagent for a task, assign it (`low|medium|high|xhigh|max`; omit for haiku, which does not support it) by the task's *difficulty*, not its model. Pick the cheapest model that clears the quality bar — a stronger model that would not change the output is wasted — then, **to make a worker think harder, raise its effort, not its model.**

### Nesting

- **Only opus and fable agents may spawn nested subagents.** haiku and sonnet agents are leaves — they execute and report; they never delegate further.
- When an opus or fable agent spawns a nested subagent, it MUST pass down a brief direction of the standards the subagent must follow, derived from what it has itself observed so far — the relevant standard/skill file paths, the conventions seen in the surrounding code, and any constraints discovered during its own work. A nested subagent starts blind; the parent's observations are its only context.

### Two-Stage Dispatch

When a worker's prompt cannot be written without first reading files, do NOT pull those files into the orchestrator's own context to write the prompt. Dispatch a **prompt-generation subagent** that reads the shared context and emits one ready-to-run worker prompt per batch; then spawn the workers on those prompts — or, if the run is a `Workflow`, make that generator its first stage. Generate the prompts with a subagent; keep the launcher's context clean.

### Review Responsibility

Whoever spawns an agent owns the quality of its output. After a subagent or teammate completes work, the parent agent MUST either:

1. **Review the work directly** — read the diff/output and verify it against the original instruction and applicable standards, or
2. **Request an independent review** — dispatch a separate agent teammate (one not involved in producing the work) to review it. Give the reviewer the artifact and the success criteria ONLY — never the producer's reasoning or chat, since a reviewer who reads the rationale inherits its blind spots. Its job is to make the criteria fail; it returns each defect, the exact criterion that defect breaks, and the minimal fix.

Unreviewed subagent output must never be accepted, merged, or reported upward as done.

## Before Coding

Decide where the work will live before editing:

- **Small change** — if the user didn't request a specific location, work in place on the current local branch. With `jj` initialized, layer new changes onto the dirty HEAD (no isolation strategy to decide); if `jj` isn't initialized, use `git` on the current branch as usual.
- **Substantial change** (worth a stacked PR) — `AskUserQuestion` where the work should live: the **current branch**, a fresh **local branch** in the current repo, a **`git worktree`**, or a **`jj` workspace**. Default path for a new worktree/workspace: `../.worktree/<repo-name>/<work-name>`.

## After Coding

Completed code goes through a **fix loop** before it is saved — any failing gate returns to implementation:

```
edit code → review → (fail ⇒ back to code) → lint → (fail ⇒ back to code) → commit
```

1. **Verify delivery (review) first.** Dispatch a review subagent to confirm every requirement was actually delivered — if a plan was executed, open the plan file and walk each task, confirming code/tests/docs match; otherwise verify the task's stated requirements. For large changes, dispatch a **review coordinator** that fans out sub-review agents per area and consolidates their findings. Have the reviewer invoke the `coding:review-code` skill with the Skill tool (skills and agent types are separate namespaces — never pass a skill name as a `subagent_type`). **If any task is unmet, return to implementation, fix it, and restart the loop at review.**

2. **Then lint.** Once review passes, dispatch a lint subagent (or a lint sub-team for large changes) to invoke the `coding:lint` skill on the touched source files — `.ts/.tsx/.js/.jsx/.py/.go/.rs/.rb/.java/.kt/.swift/.c/.cpp/.h/.hpp/.cs/.php/.sh/.vue/.svelte/.astro` and similar. Skip text/content files (`.md/.mdx/.json/.yaml/.toml/.html/.svg/.csv`) and throwaway scripts that won't be committed. **If lint reports any violation, return to implementation, fix it, then re-run review and lint.** Proceed only once both review and lint are clean.

3. **Then commit.**
   - `jj` is the **preferred** change-tracking tool when it is available and initialized — every op snapshots the working copy, so a dirty HEAD is never a blocker; work in place and don't create a `git worktree` just to isolate a task. **If `jj` is not initialized in the repo, use `git` as usual.**
   - Saving changes goes through `coding:commit`, which owns routing among save/split/absorb/edit/parallel-workspace and all explicit flag operations for both `jj` and `git`. Never hand-run `git commit`, `jj describe`, `jj split`, `jj bookmark set`, or `gh pr create` — except `coding:finalize-commits`, which is sanctioned to run `jj describe -r <rev> -m` / `git commit --amend` directly when finalizing un-pushed commits.
   - **If the user did not explicitly request a commit, ask whether to commit the work** (via `coding:commit`).
   - **If HEAD is not the local main branch, or the work is in a `jj` workspace or a linked `git worktree`, `AskUserQuestion`** whether to open a PR (`/coding:commit --create-pr` — all bookmarking and pushing happens inside the skill; titles + bodies via `/coding:write-pr`) or move the work onto the local main branch. A `git worktree` is NOT a `jj` workspace.

## Your Actions

<IMPORTANT>

- Prefer using **READ**, **WRITE**, **UPDATE**, **LS**, **GREP** as your primary editing tools instead of using **BASH**
- **Prepared Scripts**: **[IMPORTANT]** You MUST always use scripts defined in the project config (e.g. `package.json`) over running tools directly via bash. This applies to ALL agents and subagents.
  - **DO**: `npm run lint -- <path>`, `npm run test -- <path>`, `npm run build`
  - **DON'T**: `npx eslint <path>`, `npx jest <path>`, `npx tsc`
  - Only fall back to direct tool invocation when no project script exists for the purpose
- **Project Overview**: **[IMPORTANT]** Before attempting writing or fixing any codes, you MUST gain understanding about the current implementation and any issues by any one of the following methods ordered by preferences (but you only need to run once)
  - `get_project_overview` mcp tool
  - `ide__getDiagnostics` mcp tool
  - running `npm run build`
  - running `npx tsc --noEmit`
- **Diagnostics**: You MUST run `lsp_get_diagnostics` or `ide__getDiagnostics` mcp tools before and after code changes (you only can skip if `get_project_overview` has just run)
- **Complete Check**: **[IMPORTANT]** After completing your coding or test writing task, you MUST run all of the following under the project root (not monorepo root) to make sure no issues are introduced by your changes
  1. `lsp_get_diagnostics` mcp tool
  2. running `npx tsc --noEmit`
  3. running `npm run lint`
- **Dependency Check**: **[IMPORTANT]** After modifying any functions/classes that are publicly exported, look for all consumer projects in the monorepo and run `npm run build` in their project root
- **Check Documentation**: Before using an external library, consult **context7** to confirm the correct import or call signature from the documentation, and **grep** to search for real world github usage
- **Runtime Exploration**: When you need to understand the runtime behaviour of a library or API, write a test file (or add a test case to an existing spec) instead of running ad-hoc commands like `node -e "..."`, `npx ts-node -e "..."`, or equivalent. Test files are version-controlled, repeatable, and serve as living documentation.

Type safety, test coverage, TDD, and naming/documentation rules are defined by the constitution standards under `constitution/standards/` — follow them in full; they are not restated here.

</IMPORTANT>
