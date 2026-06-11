## File Discovery

- At the beginning of each session, greet the user with summary of the project context, including handover and design documents, as well as all relevant skills and standards files that may apply to the project

## Delegation Rule

**When delegating tasks to subagents, you MUST pass the full file paths of relevant skill and standard files to the subagent.**

Each skill documents its own applicable standards internally. Route actions to the appropriate skill:

| Action | Route to |
|--------|----------|
| Writing new code | `/coding:write-code` or `/coding:draft-code` |
| Setting up project | `/coding:setup-project` |
| Completing TODOs | `/coding:complete-code` |
| Fixing issues | `/coding:fix` |
| Reviewing code | `/coding:review` |
| Linting code | `/coding:lint` |
| Refactoring | `/coding:refactor` |
| Committing | `/coding:commit` |
| Finalizing un-pushed commits (per-commit QA) | `/coding:finalize-commits` |
| Creating tests | `/coding:complete-test` |
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

### Nesting

- **Only opus and fable agents may spawn nested subagents.** haiku and sonnet agents are leaves — they execute and report; they never delegate further.
- When an opus or fable agent spawns a nested subagent, it MUST pass down a brief direction of the standards the subagent must follow, derived from what it has itself observed so far — the relevant standard/skill file paths, the conventions seen in the surrounding code, and any constraints discovered during its own work. A nested subagent starts blind; the parent's observations are its only context.

### Review Responsibility

Whoever spawns an agent owns the quality of its output. After a subagent or teammate completes work, the parent agent MUST either:

1. **Review the work directly** — read the diff/output and verify it against the original instruction and applicable standards, or
2. **Request an independent review** — dispatch a separate agent teammate (one not involved in producing the work) to review it.

Unreviewed subagent output must never be accepted, merged, or reported upward as done.

## Change Tracking with `jj`

1. **`jj` is the primary change-tracking tool** — every op snapshots the working copy, so a dirty HEAD is never a blocker. Do NOT create a `git worktree` to "isolate" a task; coding skills work in place.

2. **Work in place on a dirty HEAD** — new changes layer onto existing uncommitted work; no isolation strategy to decide.

3. **Saving changes goes through `coding:commit`** — jj-first. The skill auto-routes among save (`jj describe` + `git commit`), split (`jj split`), absorb (`jj absorb`), edit (`jj edit`), and parallel-workspace (`jj workspace add`) based on working-copy state. Explicit operations via flags: `--retrospective` (blame-trace fixups), `--reorder [--up-to <rev>]` (re-linearise history), `--create-pr` (materialise stacked PRs). Never hand-run `git commit`, `jj describe`, `jj split`, `jj bookmark set`, or `gh pr create` — except `coding:finalize-commits`, which is sanctioned to run `jj describe -r <rev> -m` / `git commit --amend` directly when finalizing un-pushed commits (message conformance + folding QA edits).

4. **Stacked PRs are opt-in** — invoke `/coding:commit --create-pr`. All bookmarking and pushing happens inside the skill per `GIT-PR-STACK-*`. PR titles + bodies are produced by `/coding:write-pr`.

5. **Git-worktree guard** — a `git worktree` is NOT a `jj workspace`. If a coding task was carried out inside a linked `git worktree`, you MUST `AskUserQuestion` whether the work should be moved back onto HEAD.

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
- **Diagnostics**: You MUST run run `lsp_get_diagnostics` or `ide__getDiagnostics` mcp tools before and after code changes (you only can skip if `get_project_overview` has just run)
- **Complete Check**: **[IMPORTANT]**  After completing your coding or test writing task, you MUST run all of the following under the project root (not monorepo root) to make sure no issues are introduced by your changes
    1. `lsp_get_diagnostics` mcp tool
    2. running `npx tsc --noEmit`
    3. running `npm run lint`
- **Dependency Check**: **[IMPORTANT]**  After modifying any functions/classes that are publicly exported, look for all consumer projects in the monorepo and run the following in their project root
    1. running `npm run build`
- **Type Safety**: No `any` types allowed (& preferably no `unknown` unless absolute necessarily)
- **Test Coverage**: Maintain 100% coverage for all code
- **TDD**: Follow Red-Green-Refactor cycle for new features
- **Standards**: All code must follow TypeScript, naming, and documentation standards
- **Check Documentation**: Before using an external library, consult **context7**  to confirm the correct import or call signature from the documentation, and **grep** to search for real world github usage
- **Runtime Exploration**: When you need to understand the runtime behaviour of a library or API, write a test file (or add a test case to an existing spec) instead of running ad-hoc commands like `node -e "..."`, `npx ts-node -e "..."`, or equivalent. Test files are version-controlled, repeatable, and serve as living documentation.

</IMPORTANT>
